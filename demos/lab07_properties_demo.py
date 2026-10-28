"""Demonstrate validated properties, class/static methods, and encapsulation (lab 7)."""

import _bootstrap  # noqa: F401

from pymart.models import Customer, Product


def main() -> None:
    p1 = Product(sku="NB-001", name="Notebook", price=3.50, quantity=120)
    p2 = Product(sku="BK-550", name="Backpack", price=29.99, quantity=8)

    print(p1)
    print(repr(p1))
    print(p2)
    print(repr(p2))
    print("Total products:", Product.total_products())

    p2.apply_discount(10)
    print("After discount:", p2)

    print("SKU via method:", p1.get_sku())
    print("Mangled internal access:", p1._Product__sku)
    try:
        print(p1.__sku)
    except AttributeError as exc:
        print("Direct __sku access blocked:", type(exc).__name__)

    try:
        p1.price = -1
    except ValueError as exc:
        print("Invalid price blocked:", exc)
    p1.price = 19.99
    print("Updated price:", p1)

    c1 = Customer(
        customer_id="C1001",
        name="Ava",
        email="ava@example.com",
        loyalty_points=0,
    )
    print(c1)
    print(repr(c1))
    print("Is valid email?", Customer.is_valid_email("bad-email"))

    try:
        c1.email = "not-an-email"
    except ValueError as exc:
        print("Invalid email blocked:", exc)

    try:
        print(c1.__email)
    except AttributeError as exc:
        print("Direct __email access blocked:", type(exc).__name__)


if __name__ == "__main__":
    main()
