import _bootstrap  # noqa: F401

from tabulate import tabulate

from pymart.inventory.stock import add_stock, get_stock
from pymart.billing.invoice import compute_total


def main() -> None:
    add_stock("pencils", 10)
    add_stock("notebooks", 3)

    qty = get_stock("pencils")
    total = compute_total(unit_price=1.25, quantity=qty)

    stock_rows = [
        ["pencils", get_stock("pencils")],
        ["notebooks", get_stock("notebooks")],
    ]
    print(tabulate(stock_rows, headers=["Item", "Qty"], tablefmt="grid"))
    print(f"Invoice total for pencils: ${total:.2f}")


if __name__ == "__main__":
    main()
