from datetime import datetime
from typing import Dict, List, Optional

VALID_CODES: Dict[str, dict] = {
    "SUMMER20": {
        "percentage": 0.20,
        "max_amount": 50.0,
        "min_order": 25.0,
        "categories": None,
        "expires": None,
        "single_use": False,
    },
    "WELCOME10": {
        "percentage": 0.10,
        "max_amount": None,
        "min_order": 0.0,
        "categories": None,
        "expires": None,
        "single_use": True,
    },
    "ELECTRONICS15": {
        "percentage": 0.15,
        "max_amount": 100.0,
        "min_order": 50.0,
        "categories": ["electronics"],
        "expires": None,
        "single_use": False,
    },
    "FLASH30": {
        "percentage": 0.30,
        "max_amount": 30.0,
        "min_order": 100.0,
        "categories": None,
        "expires": datetime(2026, 12, 31),
        "single_use": False,
    },
}

# Track which single-use codes have been redeemed
_redeemed_codes: Dict[str, List[str]] = {}  # code -> [customer_ids]


def validate_promo_code(code: str, customer_id: str = None, subtotal: float = 0.0,
                         categories: List[str] = None) -> dict:
    """Validate a promo code against order context. Returns validation result dict.
    
    Checks: existence, expiry, minimum order value, category restrictions,
    and single-use redemption status.
    """
    if code not in VALID_CODES:
        return {"valid": False, "reason": "Unknown promo code"}

    config = VALID_CODES[code]

    # Expiry check
    if config["expires"] and datetime.utcnow() > config["expires"]:
        return {"valid": False, "reason": "Promo code has expired"}

    # Min order check
    if subtotal < config["min_order"]:
        return {"valid": False, "reason": f"Minimum order of ${config['min_order']:.2f} required"}

    # Category restriction check
    if config["categories"] and categories:
        if not any(c in config["categories"] for c in categories):
            return {"valid": False, "reason": f"Code only valid for: {', '.join(config['categories'])}"}

    # Single-use check
    if config["single_use"] and customer_id:
        redeemed_by = _redeemed_codes.get(code, [])
        if customer_id in redeemed_by:
            return {"valid": False, "reason": "This code has already been used"}

    return {
        "valid": True,
        "percentage": config["percentage"],
        "max_amount": config["max_amount"],
    }


def apply_discount(base_price: float, code: str, customer_id: str = None,
                    categories: List[str] = None) -> float:
    """Apply a promo code discount to the base price with full validation.
    
    Returns the discounted price. If the code is invalid, returns the
    original price unchanged.
    """
    if not code:
        return base_price

    validation = validate_promo_code(code, customer_id, base_price, categories)
    if not validation["valid"]:
        return base_price

    percentage = validation["percentage"]
    max_amount = validation.get("max_amount")

    raw_discount = base_price * percentage
    if max_amount is not None:
        raw_discount = min(raw_discount, max_amount)

    # Mark single-use codes as redeemed
    config = VALID_CODES.get(code, {})
    if config.get("single_use") and customer_id:
        _redeemed_codes.setdefault(code, []).append(customer_id)

    return round(base_price - raw_discount, 2)


def get_available_discounts(subtotal: float = 0.0, categories: List[str] = None) -> List[dict]:
    """Return all currently valid discount codes for the given order context."""
    available = []
    for code, config in VALID_CODES.items():
        if config["expires"] and datetime.utcnow() > config["expires"]:
            continue
        if subtotal < config["min_order"]:
            continue
        if config["categories"] and categories:
            if not any(c in config["categories"] for c in categories):
                continue
        available.append({
            "code": code,
            "percentage": config["percentage"],
            "max_amount": config["max_amount"],
            "min_order": config["min_order"],
        })
    return available
