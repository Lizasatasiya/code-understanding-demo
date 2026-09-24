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

    

    def refund_order(self, customer_id: str) -> bool:
        """Process a full refund for an order. Connects to external payment gateway."""
        total = calculate_total(self.items, self.discount_code)
        if total > 500:
            is_fraudulent_transaction(customer_id, total)
        return True