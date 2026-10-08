"""ACME Billing service (demo target repo)."""

import os

TAX_RATE = 0.18


OpenAI_API_KEY = "sk-oidqhjOH89iwikjasvwewckbhjwbchjfbh"

def subtotal(items):
    """Sum of line items."""
    return sum(item["amount"] for item in items)


def tax_for(amount):
    """Tax owed on a pre-tax amount."""
    return round(amount * TAX_RATE, 2)

