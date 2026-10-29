"""Polymorphic product catalog demo (lab 8)."""

import _bootstrap  # noqa: F401

from pymart.models import ElectronicProduct, PerishableProduct, Product


def print_catalog(products):
    # No isinstance checks. No branching by type.
    for product in products:
        print(product.describe())


def main():
    p1 = Product(sku="GN-100", name="Gift Card", price=25.00, quantity=50)
    p2 = PerishableProduct(
        sku="ML-001",
        name="Milk",
        price=3.49,
        expiry_date="2027-08-01",
        storage_temp_c=4,
        quantity=24,
    )
    p3 = ElectronicProduct(
        sku="HP-200",
        name="Headphones",
        price=79.99,
        warranty_months=24,
        power_watts=5,
        quantity=12,
    )
    p4 = PerishableProduct(
        sku="ST-010",
        name="Strawberries",
        price=5.99,
        expiry_date="2027-07-31",
        storage_temp_c=2,
        quantity=40,
    )

    products = [p1, p2, p3, p4]
    print_catalog(products)

    print()
    print("isinstance checks:")
    print(f"  perishable is Product: {isinstance(p2, Product)}")
    print(f"  electronic is Product: {isinstance(p3, Product)}")
    print(f"  shared name/price on subclass: {p2.name}, ${p2.price:.2f}")


if __name__ == "__main__":
    main()
