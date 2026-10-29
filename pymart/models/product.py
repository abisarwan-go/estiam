"""Product entity with validated properties."""

from pymart.exceptions import InsufficientStockError, InvalidDiscountError


class Product:
    # Shared counter: how many Product objects were created.
    _total_products = 0

    def __init__(self, sku, name, price, quantity=0):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(quantity, int):
            raise TypeError("quantity must be an integer")
        if quantity < 0:
            raise ValueError("quantity must be zero or more")

        self.name = name.strip()
        self.quantity = quantity
        self._sku = None
        self.sku = sku  # goes through the property setter
        self.price = price  # goes through the property setter
        Product._total_products += 1

    @classmethod
    def total_products(cls):
        return cls._total_products

    @classmethod
    def reset_counter(cls):
        """Reset instance counter (useful in tests)."""
        cls._total_products = 0

    @property
    def sku(self):
        return self._sku

    @sku.setter
    def sku(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("sku must be a non-empty string")
        self._sku = value.strip()

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("price must be a number")
        if value < 0:
            raise ValueError("price must be >= 0")
        self._price = round(float(value), 2)

    def sell(self, qty):
        """Reduce stock. Returns remaining quantity."""
        if not isinstance(qty, int):
            raise TypeError("qty must be an integer")
        if qty <= 0:
            raise ValueError("qty must be positive")
        if qty > self.quantity:
            raise InsufficientStockError(
                sku=str(self.sku),
                requested_qty=qty,
                available_stock=self.quantity,
            )

        self.quantity = self.quantity - qty
        return self.quantity

    def apply_discount(self, percentage):
        """Reduce price by a percentage from 0 to 100."""
        if not isinstance(percentage, (int, float)):
            raise TypeError("percentage must be a number")
        if percentage < 0 or percentage > 100:
            raise InvalidDiscountError(
                sku=str(self.sku),
                percentage=percentage,
                min_percent=0,
                max_percent=100,
            )

        self.price = self.price * (1 - percentage / 100)
        return self.price

    def describe(self):
        """Text used by reports (subclasses can override this)."""
        return f"{self.sku} | {self.name} | ${self.price:.2f}"

    def __str__(self):
        return (
            f"SKU={self.sku} | Name={self.name} | "
            f"Price=${self.price:.2f} | Qty={self.quantity}"
        )

    def __repr__(self):
        return f"Product(name={self.name!r}, price={self.price:.2f})"
