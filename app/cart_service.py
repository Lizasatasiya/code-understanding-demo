from app.stock_checker import check_stock, reserve_stock, release_stock
from app.pricing_calculator import calculate_total, calculate_subtotal
from app.fraud_detector import is_fraudulent_transaction, get_risk_score
from app.shipping_calculator import calculate_shipping
from app.models import CartItem, Customer, Order, OrderItem, OrderStatus, PaymentMethod
import uuid


class CartService:
    MAX_ITEMS_PER_CART = 50
    MAX_QUANTITY_PER_ITEM = 20

    def __init__(self):
        self.items: list[CartItem] = []
        self.discount_code = None
        self._reserved_items: dict[str, int] = {}  # item_id -> reserved qty
        
    def add_item(self, item_id: str, name: str, price: float, quantity: int = 1,
                 weight_kg: float = 0.5, is_digital: bool = False, category: str = "general") -> bool:
        """Add an item to the cart with stock reservation."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValueError(f"Cannot add more than {self.MAX_QUANTITY_PER_ITEM} of a single item")
        if len(self.items) >= self.MAX_ITEMS_PER_CART:
            raise ValueError(f"Cart cannot exceed {self.MAX_ITEMS_PER_CART} items")

        if not check_stock(item_id, quantity):
            raise ValueError(f"Not enough stock for {name}")
            
        # Check if item already exists — merge quantities
        for item in self.items:
            if item.id == item_id:
                new_qty = item.quantity + quantity
                if new_qty > self.MAX_QUANTITY_PER_ITEM:
                    raise ValueError(f"Total quantity would exceed limit of {self.MAX_QUANTITY_PER_ITEM}")
                return self.update_item_quantity(item_id, new_qty)
                
        # Reserve stock before adding to cart
        if not reserve_stock(item_id, quantity):
            raise ValueError(f"Failed to reserve stock for {name}")

        self.items.append(CartItem(
            id=item_id,
            name=name,
            price=price,
            quantity=quantity,
            weight_kg=weight_kg,
            is_digital=is_digital,
            category=category
        ))
        self._reserved_items[item_id] = quantity
        return True
        
    def apply_promo_code(self, code: str):
        self.discount_code = code

    def remove_item(self, item_id: str) -> bool:
        """Remove an item from the cart and release its stock reservation."""
        original_len = len(self.items)
        removed_items = [item for item in self.items if item.id == item_id]
        self.items = [item for item in self.items if item.id != item_id]

        # Release reserved stock
        for item in removed_items:
            release_stock(item.id, item.quantity)
            self._reserved_items.pop(item.id, None)

        return len(self.items) < original_len

    def checkout(self, customer: Customer) -> Order:
        """Process checkout: validate, calculate costs, create order, clear cart."""
        if not self.items:
            raise ValueError("Cannot checkout an empty cart")
        
        # Validate payment method for COD restrictions
        if customer.payment_method == PaymentMethod.COD:
            subtotal_check = calculate_subtotal(self.items)
            if subtotal_check > 500:
                raise ValueError("Cash on Delivery is not available for orders above $500")
            
        subtotal = calculate_subtotal(self.items)
        shipping = calculate_shipping(self.items, customer.address, subtotal)
        total = calculate_total(self.items, self.discount_code, shipping)

        # Fraud check with risk scoring
        risk_score = get_risk_score(customer.id, total, customer.payment_method.value)
        if risk_score > 0.7:
            self._release_all_reservations()
            raise PermissionError(f"Transaction rejected: risk score {risk_score:.2f} exceeds threshold")

        # Build order items (snapshot prices at time of purchase)
        order_items = [
            OrderItem(
                item_id=item.id,
                name=item.name,
                unit_price=item.price,
                quantity=item.quantity,
                line_total=item.subtotal,
                category=item.category
            )
            for item in self.items
        ]

        # Calculate loyalty points
        points_earned = customer.earn_points(total)

        order = Order(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            items=order_items,
            subtotal=subtotal,
            discount_amount=subtotal - (total - shipping - (total * 0.08 / 1.08)),
            shipping_cost=shipping,
            tax=round(total - subtotal - shipping, 2),
            total=total,
            status=OrderStatus.CONFIRMED,
            payment_method=customer.payment_method,
            shipping_address=customer.address,
            loyalty_points_earned=points_earned
        )
        
        self.clear_cart()
        return order
    
    def update_item_quantity(self, item_id: str, new_quantity: int) -> bool:
        """Update the quantity of an existing cart item with stock re-reservation."""
        if new_quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        if new_quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValueError(f"Quantity cannot exceed {self.MAX_QUANTITY_PER_ITEM}")

        for item in self.items:
            if item.id == item_id:
                if not check_stock(item_id, new_quantity):
                    raise ValueError(
                        f"Not enough stock to update '{item.name}' to quantity {new_quantity}."
                    )
                # Release old reservation, make new one
                release_stock(item_id, item.quantity)
                reserve_stock(item_id, new_quantity)
                item.quantity = new_quantity
                self._reserved_items[item_id] = new_quantity
                return True

        raise ValueError(f"Item '{item_id}' not found in cart.")
    
    def clear_cart(self) -> None:
        """Removes all items from the cart, releases reservations, and clears discount codes."""
        self._release_all_reservations()
        self.items = []
        self.discount_code = None

    def _release_all_reservations(self) -> None:
        """Release all stock reservations held by this cart."""
        for item_id, qty in self._reserved_items.items():
            release_stock(item_id, qty)
        self._reserved_items.clear()

    def get_cart_summary(self) -> dict:
        """Returns a summary of the current cart state."""
        subtotal = calculate_subtotal(self.items) if self.items else 0.0
        categories = list(set(item.category for item in self.items))
        heavy_items = [item for item in self.items if item.is_heavy()]
        return {
            "item_count": len(self.items),
            "total_quantity": sum(item.quantity for item in self.items),
            "subtotal": subtotal,
            "discount_code": self.discount_code,
            "categories": categories,
            "has_heavy_items": len(heavy_items) > 0,
            "has_digital_only": all(item.is_digital for item in self.items) if self.items else False,
        }

    def get_fraud_adjusted_subtotal(self, customer_id: str) -> float:
        """Returns the subtotal adjusted by the customer's risk score."""
        subtotal = calculate_subtotal(self.items)
        risk = get_risk_score(customer_id, subtotal, "credit_card")
        return subtotal * (1 + risk)

    def get_total_weight(self) -> float:
        """Calculate the total weight of all physical items in the cart."""
        return sum(item.weight_kg * item.quantity for item in self.items if not item.is_digital)

    def get_total_items_count(self) -> int:
        """Return the total number of items in the cart."""
        return sum(item.quantity for item in self.items)

    def get_most_expensive_item(self):
        """Return the most expensive item in the cart, or None if cart is empty."""
        if not self.items:
            return None
        return max(self.items, key=lambda item: item.price)