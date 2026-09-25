from typing import Dict


# Simulated inventory database
_inventory: Dict[str, int] = {
    "item_100": 50,
    "item_200": 5,
    "item_300": 0,
    "item_400": 100,
    "item_500": 25,
}

# Track reserved quantities (separate from available stock)
_reservations: Dict[str, int] = {}


def check_stock(item_id: str, quantity: int) -> bool:
    """Check if sufficient unreserved stock is available for an item."""
    total_stock = _inventory.get(item_id, 0)
    reserved = _reservations.get(item_id, 0)
    available = total_stock - reserved
    return available >= quantity


def reserve_stock(item_id: str, quantity: int) -> bool:
    """Reserve stock for an item. Returns True if reservation succeeded.
    
    Reservations are held until checkout completes or the cart is cleared.
    This prevents overselling when multiple users are shopping concurrently.
    """
    if not check_stock(item_id, quantity):
        return False
    _reservations[item_id] = _reservations.get(item_id, 0) + quantity
    return True


def release_stock(item_id: str, quantity: int) -> None:
    """Release previously reserved stock back into the available pool.
    
    Called when items are removed from cart or when a cart session expires.
    """
    current = _reservations.get(item_id, 0)
    new_reserved = max(0, current - quantity)
    if new_reserved == 0:
        _reservations.pop(item_id, None)
    else:
        _reservations[item_id] = new_reserved


def get_available_stock(item_id: str) -> int:
    """Return the number of unreserved units available for an item."""
    total = _inventory.get(item_id, 0)
    reserved = _reservations.get(item_id, 0)
    return max(0, total - reserved)


def restock_item(item_id: str, quantity: int) -> int:
    """Add stock for an item. Returns the new total quantity."""
    if quantity <= 0:
        raise ValueError("Restock quantity must be positive")
    _inventory[item_id] = _inventory.get(item_id, 0) + quantity
    return _inventory[item_id]
