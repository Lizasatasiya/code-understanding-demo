from app.stock_checker import check_stock
from app.pricing_calculator import calculate_total
# We will add fraud_detector import during the demo change
# from app.fraud_detector import is_fraudulent_transaction

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
        
        return {
            "customer_id": customer_id,
            "items": self.items,
            "total_price": total,
            "status": "completed"
        }
