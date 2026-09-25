import hashlib
from datetime import datetime


# Risk thresholds
HIGH_RISK_AMOUNT = 1000.0
SUSPICIOUS_PREFIX = "suspicious_"
HIGH_VALUE_THRESHOLD = 5000.0


def is_fraudulent_transaction(customer_id: str, total_price: float) -> bool:
    """Evaluates if a transaction is suspicious based on amount threshold and user ID."""
    return get_risk_score(customer_id, total_price) > 0.7


def get_risk_score(customer_id: str, total_price: float, payment_method: str = "credit_card") -> float:
    """Calculate a fraud risk score between 0.0 (safe) and 1.0 (fraudulent).

    Factors considered:
    - Transaction amount relative to thresholds
    - Customer ID patterns (known suspicious prefixes)
    - Payment method risk weighting
    - Time-of-day risk (transactions at unusual hours)
    """
    score = 0.0

    # Amount-based risk
    if total_price > HIGH_VALUE_THRESHOLD:
        score += 0.5
    elif total_price > HIGH_RISK_AMOUNT:
        score += 0.3

    # Customer ID pattern risk
    if customer_id.startswith(SUSPICIOUS_PREFIX):
        score += 0.4

    # Payment method risk weighting
    payment_risk = {
        "credit_card": 0.0,
        "debit_card": 0.0,
        "wallet": 0.05,
        "cash_on_delivery": 0.15,
    }
    score += payment_risk.get(payment_method, 0.1)

    # Time-of-day risk (transactions between 1am-5am are higher risk)
    hour = datetime.utcnow().hour
    if 1 <= hour <= 5:
        score += 0.1

    # Velocity check — hash-based simulation of repeat patterns
    customer_hash = int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)
    if customer_hash % 100 < 5:  # ~5% of customers flagged by velocity
        score += 0.2

    return min(score, 1.0)


def check_customer_history(customer_id: str) -> dict:
    """Return a mock fraud history summary for a customer."""
    # In a real system this would query a database
    return {
        "customer_id": customer_id,
        "previous_orders": 0,
        "chargebacks": 0,
        "account_age_days": 30,
        "is_verified": not customer_id.startswith(SUSPICIOUS_PREFIX),
    }
