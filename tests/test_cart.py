import pytest
from app.cart_service import CartService

def test_cart_checkout():
    cart = CartService()
    cart.add_item("item_100", "Wireless Mouse", 25.00, 2)
    cart.apply_promo_code("WELCOME10")
    
    receipt = cart.checkout("user_123")
    
    # (25 * 2) = 50. -10% = 45. +8% tax = 48.60
    assert receipt["total_price"] == 48.60
    assert len(receipt["items"]) == 1

def test_out_of_stock():
    cart = CartService()
    with pytest.raises(ValueError):
        cart.add_item("item_300", "Sold Out Keyboard", 100.0, 1)

def test_fraudulent_checkout():
    cart = CartService()
    # Adding items that push total over $1000
    cart.add_item("item_100", "Expensive Laptop", 1200.0, 1)
    
    with pytest.raises(PermissionError, match="Transaction rejected: suspected fraud."):
        cart.checkout("user_123")
        
def test_suspicious_user_checkout():
    cart = CartService()
    cart.add_item("item_100", "Wireless Mouse", 25.00, 1)
    
    with pytest.raises(PermissionError, match="Transaction rejected: suspected fraud."):
        cart.checkout("suspicious_bot_001")
