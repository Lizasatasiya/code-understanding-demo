# Code Understanding Demo

This is a proof-of-concept IDE-independent code understanding system that runs on `git commit`.

## How the Code Graph works
The system uses the Python `ast` module to detect function definitions and calls in staged files. A simple in-memory graph is constructed using nodes (files and functions) and edges (contains, defined_in, calls). The `ContextBuilder` uses this graph to find relevant dependencies for the modified code.

## How it remains IDE-independent
The system integrates via a Git `pre-commit` hook. Since Git works exactly the same whether you use VS Code, PyCharm, Neovim, or the terminal, the hook runs reliably regardless of your editor, prompting for understanding before allowing the commit.

## Setup Instructions

1. **Initialize the repository:**
   ```bash
   cd code-understanding-demo
   git init
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start the FastAPI Server:**
   Open a new terminal and run:
   ```bash
   cd code-understanding-demo
   source venv/bin/activate
   python -m server.main
   ```

4. **Install the Git Hook:**
   In your main terminal, run:
   ```bash
   python -m scripts.install_hook
   ```
   Add initial files:
   ```bash
   git add .
   git commit -m "Initial commit" --no-verify
   ```

## Make a Demo Change

Modify `app/cart_service.py` to add `is_fraudulent_transaction`:

```python
from app.stock_checker import check_stock
from app.pricing_calculator import calculate_total
from app.fraud_detector import is_fraudulent_transaction  # <--- UNCOMMENT THIS

class CartService:
    # ... (init and add_item)
        
    def checkout(self, customer_id: str) -> dict:
        total = calculate_total(self.items, self.discount_code)
        
        # <--- ADD THESE LINES
        if is_fraudulent_transaction(customer_id, total):
            raise PermissionError("Transaction rejected: suspected fraud.")
        
        return {
            "customer_id": customer_id,
            "items": self.items,
            "total_price": total,
            "status": "completed"
        }
```

Run the commit flow:
```bash
git add app/cart_service.py
git commit -m "add fraud detection on checkout"
```

## Example Terminal Output
```
$ git commit -m "add fraud detection on checkout"

[HOOK] Code Understanding Check
[ENV] Python project detected
[CHANGE] Reading staged diff...
[CHANGE] Found 1 modified python files
[AST] Analyzing changed functions...
[GRAPH] Building code relationship graph...
[GRAPH] Found 3 code relationships
[DEPENDENCY] Finding relevant dependencies...
[CONTEXT] Building code understanding context...
[CONTEXT] Selected 2 relevant code entities
[SUMMARY] Generating change summary...
[QUESTIONS] Generating questions...
[QUESTIONS] Generated 3 questions

[INTERACTION] Asking developer...

========================================
Code Understanding Check

Changed:
app/cart_service.py

Function:
checkout()

Question 1/3

What behavior did your change introduce?

Your answer:
> Added fraud detection to block suspicious checkouts.


...

[SERVER] Sending understanding session...
[SERVER] Session received successfully.
[HOOK] Understanding session completed.
```
