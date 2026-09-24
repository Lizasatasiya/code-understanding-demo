def check_stock(item_id: str, quantity: int) -> bool:
    # Simulated inventory database
    inventory = {
        "item_100": 50,
        "item_200": 5,
        "item_300": 0
    }
    return inventory.get(item_id, 0) >= quantity
