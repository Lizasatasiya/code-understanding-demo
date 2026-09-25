from app.stock_checker import check_stock
from app.pricing_calculator import calculate_total
from app.models import CartItem

class WishlistService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._items: list[CartItem] = []

    def add_item(self, item_id: str, name: str, price: float, quantity: int = 1, is_digital: bool = False) -> bool:
        """Add an item to the wishlist. Ignores duplicates."""
        if any(i.id == item_id for i in self._items):
            return False
        self._items.append(CartItem(
            id=item_id, 
            name=name,
            price=price, 
            quantity=quantity,
            is_digital=is_digital
        ))
        return True

    def remove_item(self, item_id: str) -> bool:
        """Remove an item from the wishlist by ID."""
        before = len(self._items)
        self._items = [i for i in self._items if i.id != item_id]
        return len(self._items) < before

    def get_available_items(self) -> list[CartItem]:
        """Return only the wishlisted items that are currently in stock."""
        return [item for item in self._items if check_stock(item.id, item.quantity)]

    def move_to_cart(self, item_id: str) -> CartItem | None:
        """Move a wishlisted item to the cart payload if it is in stock.

        Returns the item CartItem ready to be added to CartService, or None if
        the item is not found or out of stock.
        """
        item = next((i for i in self._items if i.id == item_id), None)
        if item is None:
            return None
        if not check_stock(item.id, item.quantity):
            return None
        self.remove_item(item_id)
        return item

    def estimated_total(self, discount_code: str = None) -> float:
        """Estimate the total cost of all wishlisted items using the pricing engine."""
        if not self._items:
            return 0.0
        return calculate_total(self._items, discount_code)

    def summary(self) -> dict:
        """Return a summary of the current wishlist state."""
        available = self.get_available_items()
        return {
            "user_id": self.user_id,
            "total_items": len(self._items),
            "available_items": len(available),
            "estimated_total": self.estimated_total(),
        }
