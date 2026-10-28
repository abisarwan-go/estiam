Create a new folder on your computer named pymart (or PyMart) and open it in Visual Studio Code using <kbd>File</kbd> → <kbd>Open Folder...</kbd>. You should see the folder name at the top of the Explorer panel, with no files yet. Starting from an empty workspace helps you keep package code, scripts, and configuration in one predictable place.
Confirm you are working with the right Python interpreter. Open the Command Palette (<kbd>Ctrl</kbd>/<kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd>), choose Python: Select Interpreter, and pick the environment you intend to use for this lab. Then verify terminal access by opening <kbd>Terminal</kbd> → <kbd>New Terminal</kbd> and running python --version (or python3 --version) to confirm VS Code is pointing at the same Python you selected.
Decide where the runnable entry point will live. For this lab, place a main.py at the project root (next to the package folder you will create later), so you can run the project from the workspace folder without complex paths. If you prefer a scripts/ folder for runnable files, choose that now and stick to it. Changing the entry point location later often leads to confusing import errors and inconsistent run commands.
Build the PyMart package and subpackage folder structure
Create a top-level folder named pymart/ inside your project. This folder is your main Python package. Inside pymart/, create two subfolders: inventory/ and billing/. These are subpackages that will hold code related to stock management and purchases.
Add an __init__.py file in each of these three folders (pymart/, pymart/inventory/, pymart/billing/). The files can be empty for now. Their presence tells Python to treat each folder as an importable package, so later you can use imports like from pymart.inventory import ... without surprises.
Your folder tree should match this structure exactly:

pymart/

__init__.py

inventory/

__init__.py

billing/

__init__.py

Add modules with simple functions for inventory and billing
Create two small modules that do one job each and return values that are easy to verify in the console. Avoid reading files, reaching out to databases, or adding complex class hierarchies. The goal is quick feedback: call a function, see a clear return value, and know it worked.

Create pymart/inventory/stock.py with one or two stock-related functions:

# pymart/inventory/stock.py

def add_stock(current_qty: int, added_qty: int) -> int:
    """Return the new stock level after receiving inventory."""
    return current_qty + added_qty


def is_in_stock(current_qty: int, requested_qty: int) -> bool:
    """Return True when you can fulfill the requested quantity."""
    return current_qty >= requested_qty
These are intentionally small. If add_stock(10, 5) returns 15, you know the module is being imported and executed correctly. If is_in_stock(3, 4) returns False, you know the boolean logic is behaving as expected.

Create pymart/billing/invoice.py with one or two invoice-related functions:
# pymart/billing/invoice.py

def line_total(unit_price: float, quantity: int) -> float:
    """Return the total for a single invoice line."""
    return round(unit_price * quantity, 2)


def invoice_total(subtotal: float, tax_rate: float) -> float:
    """Return the invoice total including tax (tax_rate like 0.07 for 7%)."""
    return round(subtotal * (1 + tax_rate), 2)
Keep return values simple and “print-friendly”. If line_total(2.5, 4) returns 10.0 and invoice_total(10.0, 0.07) returns 10.7, you can confirm the billing module does what it should without any extra setup.

Import and use the package from a top-level main script
Create a main.py at the project root (next to the pymart/ folder) and treat it as the single runnable entry point for the project. Keeping the “run from here” script at the top level helps you use clean, package-based imports rather than import paths that depend on which folder you happened to run from.

Use absolute imports in main.py so it reads like a consumer of your package:

# main.py

from pymart.inventory.stock import add_stock, get_stock
from pymart.billing.invoice import compute_total

def main() -> None:
    add_stock("pencils", 10)
    add_stock("notebooks", 3)

    qty = get_stock("pencils")
    total = compute_total(unit_price=1.25, quantity=qty)

    print(f"Stock for pencils: {qty}")
    print(f"Invoice total for pencils: ${total:.2f}")

if __name__ == "__main__":
    main()
Inside a subpackage module, a relative import can be useful when one module depends on a neighbor module in the same subpackage. For example, if pymart/billing/invoice.py needs a helper in pymart/billing/tax.py, import it relatively:
# pymart/billing/invoice.py

from .tax import add_tax  # relative import within the billing subpackage

def compute_total(unit_price: float, quantity: int) -> float:
    subtotal = unit_price * quantity
    return add_tax(subtotal)
Run main.py and validate expected console output
Run main.py from the integrated terminal using the interpreter you selected in VS Code. From the project root (the folder that contains main.py), run:

python main.py (Windows)

python3 main.py (macOS/Linux)

A successful run should print your expected messages and exit cleanly with no traceback.

Validate that imports resolve and your functions execute in the intended order by reading the console top to bottom. Do the first lines correspond to the first calls in main.py? If the output looks out of sequence, check for code that runs on import (top-level statements inside your modules) and make sure any “demo” calls are under an if __name__ == "__main__": guard in the file you intend to execute.
If you hit errors, fix the environment details before changing logic:

ModuleNotFoundError for your package: confirm you are running from the correct working directory (project root) and that your package folder sits next to main.py.

Imports work sometimes: ensure every package and subpackage directory includes an __init__.py (unless you intentionally created a namespace package).

Wrong file runs: verify the terminal is opened in the expected folder and that you are invoking the correct main.py (watch for duplicates in nested folders).

Interpreter mismatch: make sure the terminal is using the same interpreter selected in VS Code (the one with your dependencies, if any).

Concrete outcome you should have at the end
By the end of this lab, you should have a complete, working Python project you can run immediately and reuse as a template for future internal packages. The key test is simple: you can import your package cleanly and demonstrate both the inventory and billing functionality from one top-level script.
You should be able to point to all of the following, without workarounds:

A working, importable pymart package with at least two subpackages

A main.py that exercises both inventory and billing code paths

A successful run producing clear console output proving the package works