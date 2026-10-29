"""Electronic product: has a warranty in months."""

from .product import Product


class ElectronicProduct(Product):
    def __init__(
        self,
        sku,
        name,
        price,
        warranty_months,
        power_watts=None,
        quantity=0,
    ):
        super().__init__(sku=sku, name=name, price=price, quantity=quantity)

        if not isinstance(warranty_months, int):
            raise TypeError("warranty_months must be an integer")
        if warranty_months < 0:
            raise ValueError("warranty_months cannot be negative")
        self.warranty_months = warranty_months

        if power_watts is not None:
            if not isinstance(power_watts, (int, float)):
                raise TypeError("power_watts must be a number")
            if power_watts < 0:
                raise ValueError("power_watts cannot be negative")
            self.power_watts = float(power_watts)
        else:
            self.power_watts = None

    def describe(self):
        text = super().describe()
        text = f"{text} | warranty: {self.warranty_months} months"
        if self.power_watts is not None:
            text = f"{text} | power: {self.power_watts}W"
        return text
