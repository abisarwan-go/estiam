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
