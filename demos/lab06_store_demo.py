"""Mini-store demo for Product and Customer classes (lab 6)."""

import _bootstrap  # noqa: F401

from pymart.models import Customer, Product


def main() -> None:
    products = [
        Product(sku="NB-001", name="Notebook", price=3.49, quantity=120),
        Product(sku="PN-101", name="Pen Pack", price=5.99, quantity=45),
        Product(sku="BK-550", name="Backpack", price=39.95, quantity=8),
    ]

    customers = [
        Customer(
            customer_id="C1001",
            name="Aisha Khan",
            email="aisha@example.com",
            loyalty_points=20,
        ),
        Customer(
            customer_id="C1002",
            name="Miguel Rivera",
            email="miguel@example.com",
            loyalty_points=0,
        ),
    ]

    print("BEFORE")
    for product in products:
        print(product)
    for customer in customers:
        print(customer)

    products[2].apply_discount(15)  # 15% off backpack
    products[1].apply_discount(10)  # 10% off pen pack
    customers[0].add_loyalty_points(50)
    customers[1].add_loyalty_points(10)

    print("\nAFTER")
    for product in products:
        print(product)
    for customer in customers:
        print(customer)


if __name__ == "__main__":
    main()
