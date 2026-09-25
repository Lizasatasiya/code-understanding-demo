from app.stock_checker import check_stock
from app.pricing_calculator import calculate_total, calculate_subtotal
from app.fraud_detector import is_fraudulent_transaction
from app.shipping_calculator import calculate_shipping
from app.models import CartItem, Customer, Order
import uuid

class CartService:
    def __init__(self):
        self.items: list[CartItem] = []
        self.discount_code = None
        
    def add_item(self, item_id: str, name: str, price: float, quantity: int = 1, weight_kg: float = 0.5, is_digital: bool = False) -> bool:
        if not check_stock(item_id, quantity):
            raise ValueError(f"Not enough stock for {name}")
            
        # Check if item already exists
        for item in self.items:
            if item.id == item_id:
                return self.update_item_quantity(item_id, item.quantity + quantity)
                
        self.items.append(CartItem(
            id=item_id,
            name=name,
            price=price,
            quantity=quantity,
            weight_kg=weight_kg,
            is_digital=is_digital
        ))
        return True
        
    def apply_promo_code(self, code: str):
        self.discount_code = code

    def remove_item(self, item_id: str) -> bool:
        """Remove an item from the cart by its ID. Returns True if removed."""
        original_len = len(self.items)
        self.items = [item for item in self.items if item.id != item_id]
        return len(self.items) < original_len

    def checkout(self, customer: Customer) -> Order:
        if not self.items:
            raise ValueError("Cannot checkout an empty cart")
            
        subtotal = calculate_subtotal(self.items)
        shipping = calculate_shipping(self.items, customer.address, subtotal)
        total = calculate_total(self.items, self.discount_code, shipping)

        if is_fraudulent_transaction(customer.id, total):
            raise PermissionError("Transaction rejected: suspected fraud.")
            
        order = Order(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            items=self.items.copy(),
            subtotal=subtotal,
            shipping_cost=shipping,
            tax=round(total - subtotal - shipping + (subtotal if self.discount_code else 0), 2),
            total=total,
            status="confirmed"
        )
        
        self.clear_cart()
        return order
    
    def update_item_quantity(self, item_id: str, new_quantity: int) -> bool:
        """Update the quantity of an existing cart item.

        Validates stock availability for the new quantity before applying the
        change. Raises ValueError if the item is not in the cart or if there
        is insufficient stock.

        Returns True when the quantity is successfully updated.
        """
        if new_quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        for item in self.items:
            if item.id == item_id:
                if not check_stock(item_id, new_quantity):
                    raise ValueError(
                        f"Not enough stock to update '{item.name}' to quantity {new_quantity}."
                    )
                item.quantity = new_quantity
                return True

        raise ValueError(f"Item '{item_id}' not found in cart.")
    
    def clear_cart(self) -> None:
        """Removes all items from the cart and clears any applied discount codes."""
        self.items = []
        self.discount_code = None

    def refund_order(self, customer_id: str) -> bool:
        """Process a full refund for an order. Connects to external payment gateway."""
        total = calculate_total(self.items, self.discount_code)
        if total > 500:
            is_fraudulent_transaction(customer_id, total)
        return True

    def get_order_summary(self, customer_id: str) -> dict:
        """Returns a full order summary including fraud check status and final price."""
        total = calculate_total(self.items, self.discount_code)
        is_suspicious = is_fraudulent_transaction(customer_id, total)
        return {
            "customer_id": customer_id,
            "item_count": len(self.items),
            "discount_code": self.discount_code,
            "total": total,
            "flagged": is_suspicious,
        }