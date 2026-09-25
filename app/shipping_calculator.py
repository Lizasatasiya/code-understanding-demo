from app.models import CartItem, Address, ShippingRate
from typing import List

# Mock DB for shipping rates
SHIPPING_RATES = {
    "US": ShippingRate("US", 5.0, 1.5, 100.0),
    "CA": ShippingRate("CA", 10.0, 2.5, 150.0),
    "UK": ShippingRate("UK", 15.0, 3.0, 200.0),
    "EU": ShippingRate("EU", 12.0, 2.5, 180.0),
}

def calculate_shipping(items: List[CartItem], address: Address, subtotal: float) -> float:
    """Calculates shipping cost based on weight, region, and subtotal."""
    if not address:
        return 0.0 # Default/unknown address gets free shipping for now
        
    rate = SHIPPING_RATES.get(address.country)
    
    if not rate:
        # Fallback to international rate
        rate = ShippingRate("INT", 25.0, 5.0, 500.0)
        
    # Check for free shipping
    if subtotal >= rate.free_shipping_threshold:
        return 0.0
        
    # Calculate total physical weight
    total_weight = sum(item.weight_kg * item.quantity for item in items if not item.is_digital)
    
    # If all items are digital, shipping is free
    if total_weight == 0 and all(item.is_digital for item in items):
        return 0.0
        
    shipping_cost = rate.base_rate + (total_weight * rate.per_kg_rate)
    return round(shipping_cost, 2)
