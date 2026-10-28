"""Exercise Product domain exceptions: success, stock error, discount error."""

import _bootstrap  # noqa: F401

from pymart import (
    InsufficientStockError,
    InvalidDiscountError,
    Product,
    PyMartError,
)


def main() -> None:
    product = Product(sku="A123", name="Notebook", price=3.49, quantity=5)
    print("START:", product)

    # Happy path: successful sale
    try:
        remaining = product.sell(2)
        print(f"OK sale: sold 2, remaining={remaining}")
        print("  after:", product)
    except PyMartError as exc:
        print(f"Unexpected domain error: {type(exc).__name__}: {exc}")

    # Failure: insufficient stock
    try:
        product.sell(10)
    except InsufficientStockError as exc:
        print(
            f"STOCK ERROR ({type(exc).__name__}): {exc}\n"
            f"  context: sku={exc.sku}, requested={exc.requested_qty}, "
            f"available={exc.available_stock}\n"
            f"  next: reduce quantity or restock SKU {exc.sku}."
        )
    except PyMartError as exc:
        print(f"Other domain error: {type(exc).__name__}: {exc}")

    # Failure: invalid discount
    try:
        product.apply_discount(-5)
    except InvalidDiscountError as exc:
        print(
            f"DISCOUNT ERROR ({type(exc).__name__}): {exc}\n"
            f"  context: sku={exc.sku}, percent={exc.percentage}, "
            f"allowed={exc.min_percent}–{exc.max_percent}\n"
            f"  next: choose a discount between "
            f"{exc.min_percent} and {exc.max_percent}."
        )
    except PyMartError as exc:
        print(f"Other domain error: {type(exc).__name__}: {exc}")

    print("END:", product)


if __name__ == "__main__":
    main()
