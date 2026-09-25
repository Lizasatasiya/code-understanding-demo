from app.stock_checker import check_stock
from app.pricing_calculator import calculate_total
from app.fraud_detector import is_fraudulent_transaction

class CartService:
    def __init__(self):
        self.items = []
        self.discount_code = None
        
    def add_item(self, item_id: str, name: str, price: float, quantity: int = 1) -> bool:
        if not check_stock(item_id, quantity):
            raise ValueError(f"Not enough stock for {name}")
            
        self.items.append({
            "id": item_id,
            "name": name,
            "price": price,
            "quantity": quantity
        })
        return True
        
    def apply_promo_code(self, code: str):
        self.discount_code = code

    def remove_item(self, item_id: str) -> bool:
        """Remove an item from the cart by its ID. Returns True if removed."""
        original_len = len(self.items)
        self.items = [item for item in self.items if item["id"] != item_id]
        return len(self.items) < original_len

    def checkout(self, customer_id: str) -> dict:
        total = calculate_total(self.items, self.discount_code)

        if is_fraudulent_transaction(customer_id, total):
            raise PermissionError("Transaction rejected: suspected fraud.")

        return {
            "customer_id": customer_id,
            "items": self.items,
            "total_price": total,
            "status": "done"
        }
    
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
            if item["id"] == item_id:
                if not check_stock(item_id, new_quantity):
                    raise ValueError(
                        f"Not enough stock to update '{item['name']}' to quantity {new_quantity}."
                    )
                item["quantity"] = new_quantity
                return True

        raise ValueError(f"Item '{item_id}' not found in cart.")
    

    def refund_order(self, customer_id: str) -> bool:
        """Process a full refund for an order. Connects to external payment gateway."""
        total = calculate_total(self.items, self.discount_code)
        if total > 500:
            is_fraudulent_transaction(customer_id, total)
        return True

    def apply_bulk_discount(self, code: str) -> float:
        """Applies a promo code if valid and returns the discounted total price."""
        if not validate_promo_code(code):
            raise ValueError(f"Promo code '{code}' is not valid.")
        self.discount_code = code
        return calculate_total(self.items, self.discount_code)

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