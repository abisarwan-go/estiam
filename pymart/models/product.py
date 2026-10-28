"""Product entity for PyMart inventory."""

from __future__ import annotations


class Product:
    def __init__(
        self,
        sku: str,
        name: str,
        price: float,
        quantity: int,
    ) -> None:
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError("sku must be a non-empty string")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(price, (int, float)):
            raise TypeError("price must be a number")
        if price < 0:
            raise ValueError("price must be non-negative")
        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise TypeError("quantity must be an integer")
        if quantity < 0:
            raise ValueError("quantity must be zero or more")

        self.sku = sku.strip()
        self.name = name.strip()
        self.price = round(float(price), 2)
        self.quantity = quantity

    def apply_discount(self, percentage: float) -> float:
        """Reduce price by a percentage from 0 to 100.

        Returns:
            The updated price.
        """
        if not isinstance(percentage, (int, float)) or isinstance(
            percentage, bool
        ):
            raise TypeError("percentage must be a number")
        if percentage < 0 or percentage > 100:
            raise ValueError("percentage must be between 0 and 100")

        new_price = self.price * (1 - percentage / 100)
        self.price = max(0.0, round(new_price, 2))
        return self.price

    def __str__(self) -> str:
        return (
            f"SKU={self.sku} | Name={self.name} | "
            f"Price=${self.price:.2f} | Qty={self.quantity}"
        )
