from app.discount_applicator import apply_discount

def calculate_subtotal(items: list) -> float:
    return sum(item["price"] * item["quantity"] for item in items)

def calculate_total(items: list, discount_code: str = None) -> float:
    subtotal = calculate_subtotal(items)
    discounted_total = apply_discount(subtotal, discount_code)
    
    # Add flat 8% tax rate
    tax = discounted_total * 0.08
    return round(discounted_total + tax, 2)
