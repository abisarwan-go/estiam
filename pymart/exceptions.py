"""PyMart domain exception hierarchy."""


class PyMartError(Exception):
    """Base class for all PyMart domain exceptions."""


class InsufficientStockError(PyMartError):
    """Raised when requested quantity exceeds available stock."""

    def __init__(self, sku: str, requested_qty: int, available_stock: int):
        self.sku = sku
        self.requested_qty = requested_qty
        self.available_stock = available_stock
        super().__init__(
            f"Insufficient stock for SKU '{sku}': requested {requested_qty}, "
            f"available {available_stock}."
        )


class InvalidDiscountError(PyMartError):
    """Raised when an attempted discount percentage is invalid."""

    def __init__(
        self,
        sku: str,
        percentage: float,
        min_percent: float = 0,
        max_percent: float = 100,
    ):
        self.sku = sku
        self.percentage = percentage
        self.min_percent = min_percent
        self.max_percent = max_percent
        super().__init__(
            f"Invalid discount for SKU '{sku}': attempted {percentage}% "
            f"(allowed {min_percent}–{max_percent})."
        )
