import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.models import (
    Customer,
    CartItem,
    OrderItem,
    Order,
    OrderStatus,
    PaymentMethod,
    Address,
    Discount,
)
from app.stock_checker import check_stock
from app.fraud_detector import is_fraudulent_transaction, get_risk_score
from app.shipping_calculator import calculate_shipping


class OrderServiceException(Exception):
    """Base exception for order processing errors."""
    pass


class InventoryUnavailableException(OrderServiceException):
    """Raised when an item in the cart cannot be fulfilled due to stock shortages."""
    pass


class FraudDetectedException(OrderServiceException):
    """Raised when the transaction fails automated risk assessment."""
    pass


class OrderService:
    """Orchestrates order lifecycle: validation, risk evaluation, checkout, and fulfillment."""

    STANDARD_TAX_RATE = 0.08  # 8% baseline sales tax

    def __init__(self):
        # In-memory storage simulating a persistent repository
        self._orders: Dict[str, Order] = {}

    def create_order(
        self,
        customer: Customer,
        items: List[CartItem],
        discount: Optional[Discount] = None,
        shipping_address: Optional[Address] = None,
        payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD,
    ) -> Order:
        """Processes and finalizes an order from a collection of cart items.

        Coordinates:
        1. Input validation & empty check
        2. Inventory availability verification via StockChecker
        3. Automated fraud & velocity scoring
        4. Subtotal, discount deduction, shipping, and tax calculation
        5. Loyalty points accrual
        """
        if not items:
            raise OrderServiceException("Cannot create an order with an empty item list.")

        destination = shipping_address or customer.address
        if not destination:
            raise OrderServiceException("A valid shipping destination is required to place an order.")

        # Step 1: Inventory stock verification
        for item in items:
            available_qty = check_stock(item.id)
            if available_qty < item.quantity:
                raise InventoryUnavailableException(
                    f"Insufficient inventory for item '{item.name}' (ID: {item.id}). "
                    f"Requested: {item.quantity}, Available: {available_qty}"
                )

        # Step 2: Financial calculations
        subtotal = round(sum(item.subtotal for item in items), 2)

        # Step 3: Fraud risk assessment
        if is_fraudulent_transaction(customer.id, subtotal):
            risk_score = get_risk_score(customer.id, subtotal, payment_method.value)
            raise FraudDetectedException(
                f"Transaction flagged by automated fraud engine. Risk score: {risk_score:.2f}"
            )

        # Step 4: Apply optional discount
        discount_amount = 0.0
        if discount and discount.is_applicable(subtotal, [i.category for i in items]):
            discount_amount = round(discount.calculate_discount(subtotal), 2)

        discounted_subtotal = max(0.0, subtotal - discount_amount)

        # Step 5: Shipping cost calculation
        shipping_cost = calculate_shipping(items, destination, discounted_subtotal)

        # Step 6: Tax computation
        tax = round(discounted_subtotal * self.STANDARD_TAX_RATE, 2)

        # Final total
        final_total = round(discounted_subtotal + shipping_cost + tax, 2)

        # Step 7: Create immutable order item records
        order_items = [
            OrderItem(
                item_id=item.id,
                name=item.name,
                unit_price=item.price,
                quantity=item.quantity,
                line_total=item.subtotal,
                category=item.category,
            )
            for item in items
        ]

        # Step 8: Build the Order entity
        order_id = f"ord_{uuid.uuid4().hex[:10]}"
        points_earned = customer.earn_points(final_total)

        order = Order(
            id=order_id,
            customer_id=customer.id,
            items=order_items,
            subtotal=subtotal,
            discount_amount=discount_amount,
            shipping_cost=shipping_cost,
            tax=tax,
            total=final_total,
            status=OrderStatus.CONFIRMED,
            payment_method=payment_method,
            shipping_address=destination,
            loyalty_points_earned=points_earned,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self._orders[order_id] = order
        return order

    def cancel_order(self, order_id: str, reason: str = "customer_request") -> Order:
        """Cancels an existing order if it has not yet reached the shipped status."""
        order = self._orders.get(order_id)
        if not order:
            raise OrderServiceException(f"Order '{order_id}' does not exist.")

        if not order.can_cancel():
            raise OrderServiceException(
                f"Order '{order_id}' cannot be cancelled because current status is '{order.status.value}'."
            )

        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.utcnow()
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """Retrieves an order by its unique identifier."""
        return self._orders.get(order_id)

    def list_customer_orders(self, customer_id: str) -> List[Order]:
        """Lists all historical orders associated with a specific customer."""
        return [order for order in self._orders.values() if order.customer_id == customer_id]
