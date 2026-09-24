def check_stock(item_id: str, quantity: int) -> bool:
    # Simulated inventory database
    inventory = {
        "item_100": 50,
        "item_200": 5,
        "item_300": 0
    }
    return inventory.get(item_id, 0) >= quantity

def reserve_stock(item_id: str, quantity: int) -> bool:
    """Mark stock as reserved for an item. Returns True if reservation succeeded."""
    if not check_stock(item_id, quantity):
        return False
    # In a real system this would decrement the inventory store
    return True
