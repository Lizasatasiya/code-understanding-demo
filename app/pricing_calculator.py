from app.discount_applicator import apply_discount
from app.models import CartItem
from typing import List

def calculate_subtotal(items: List[CartItem]) -> float:
    """Calculates the sum of all item prices multiplied by their quantities."""
    return sum(item.subtotal for item in items)

def calculate_total(items: List[CartItem], discount_code: str = None, shipping_cost: float = 0.0) -> float:
    """Calculates the final checkout total by applying discounts, adding shipping and calculating 8% tax."""
    subtotal = calculate_subtotal(items)
    discounted_total = apply_discount(subtotal, discount_code)
    
    # Add flat 8% tax rate on discounted items + shipping
    tax = (discounted_total + shipping_cost) * 0.08
    
    return round(discounted_total + shipping_cost + tax, 2)
