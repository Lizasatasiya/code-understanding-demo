def apply_discount(base_price: float, code: str) -> float:
    if not code:
        return base_price
        
    discounts = {
        "SUMMER20": 0.20,
        "WELCOME10": 0.10
    }
    
    discount_pct = discounts.get(code, 0.0)
    return base_price * (1.0 - discount_pct)
