# CodeUnderstandingDemo — E-Commerce Cart Engine

A proof-of-concept **IDE-independent code understanding system** that intercepts `git commit`, analyzes your staged changes using AST + LLM, and asks you smart questions before the commit goes through.

---

## The Application

A simple **E-Commerce Cart Engine** with real dependencies between modules:

```
cart_service.py
    ├── add_item()     → check_stock()        [stock_checker.py]
    └── checkout()     → calculate_total()    [pricing_calculator.py]
                       → is_fraudulent_transaction() [fraud_detector.py]

pricing_calculator.py
    └── calculate_total() → apply_discount()  [discount_applicator.py]
```

| File | Responsibility |
|---|---|
| `app/cart_service.py` | Add items, apply promo codes, checkout |
| `app/stock_checker.py` | Checks item availability against simulated inventory |
| `app/pricing_calculator.py` | Calculates subtotal, applies discounts, adds 8% tax |
| `app/discount_applicator.py` | Applies promo code discounts (SUMMER20, WELCOME10) |
| `app/fraud_detector.py` | Rejects transactions over $1000 or from suspicious users |

---

## Setup

```bash
# 1. Create venv and install deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Add your Groq API key (one level above the project)
echo "GROQ_API_KEY=your_key_here" > ../.env

# 3. Init git and install the pre-commit hook
git init
python -m scripts.install_hook
git add .
git commit -m "Initial commit" --no-verify

# 4. Start the FastAPI server (in a separate terminal)
python3 -m server.main
```

---

## Demo Change

Open `app/cart_service.py` and add fraud detection to `checkout()`:

```python
from app.fraud_detector import is_fraudulent_transaction  # uncomment

def checkout(self, customer_id: str) -> dict:
    total = calculate_total(self.items, self.discount_code)

    if is_fraudulent_transaction(customer_id, total):          # add this
        raise PermissionError("Transaction rejected: suspected fraud.")

    return {"customer_id": customer_id, "items": self.items,
            "total_price": total, "status": "completed"}
```

Then commit it:

```bash
git add app/cart_service.py
git commit -m "add fraud detection on checkout"
```

---

## What Happens on Commit

```
git commit
    ↓ pre-commit hook fires
    ↓ ChangeDetector   — git diff + AST (only changed functions)
    ↓ CodeGraph        — maps file/function relationships
    ↓ ContextBuilder   — collects relevant dependencies
    ↓ ChangeSummary    — what changed, why, impact
    ↓ QuestionGenerator — Groq LLM generates 3 focused questions
    ↓ Developer answers in terminal
    ↓ POST /understanding-session → FastAPI server
    ↓ commit succeeds
```

---

## Running Tests

```bash
pytest tests/test_cart.py -v
```
