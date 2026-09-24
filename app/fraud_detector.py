def is_fraudulent_transaction(customer_id: str, total_price: float) -> bool:
    # Simulated fraud detection rules
    if total_price > 1000.0:
        return True
    if customer_id.startswith("suspicious_"):
        return True
    return False
