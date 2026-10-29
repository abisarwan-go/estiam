"""Perishable product: has an expiry date."""

from datetime import date, datetime

from .product import Product


class PerishableProduct(Product):
    def __init__(
        self,
        sku,
        name,
        price,
        expiry_date,
        storage_temp_c=None,
        quantity=0,
    ):
        super().__init__(sku=sku, name=name, price=price, quantity=quantity)
        self.expiry_date = self._parse_expiry(expiry_date)

        if storage_temp_c is not None:
            if not isinstance(storage_temp_c, (int, float)):
                raise TypeError("storage_temp_c must be a number")
            self.storage_temp_c = float(storage_temp_c)
        else:
            self.storage_temp_c = None

    @staticmethod
    def _parse_expiry(value):
        """Accept a date object or a 'YYYY-MM-DD' string."""
        if isinstance(value, datetime):
            parsed = value.date()
        elif isinstance(value, date):
            parsed = value
        elif isinstance(value, str):
            try:
                parsed = date.fromisoformat(value.strip())
            except ValueError:
                raise ValueError(
                    f"expiry_date must be ISO format YYYY-MM-DD, got {value!r}"
                )
        else:
            raise TypeError("expiry_date must be a date or ISO string")

        if parsed < date.today():
            raise ValueError(f"expiry_date cannot be in the past: {parsed}")
        return parsed

    def describe(self):
        text = super().describe()
        text = f"{text} | expires: {self.expiry_date.isoformat()}"
        if self.storage_temp_c is not None:
            text = f"{text} | store at {self.storage_temp_c}°C"
        return text
