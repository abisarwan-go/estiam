"""Custom errors used by PyMart."""


class PyMartError(Exception):
    """Base class for all PyMart domain exceptions."""


def _with_file_line(message, source=None, line=None):
    """Add [file=..., line=...] in front of a message when available."""
    parts = []
    if source:
        parts.append(f"file={source}")
    if line is not None:
        parts.append(f"line={line}")
    if parts:
        return f"[{', '.join(parts)}] {message}"
    return message


class DataValidationError(PyMartError):
    """A record was read, but values break a business rule."""

    def __init__(self, message, source=None, line=None):
        self.source = source
        self.line = line
        super().__init__(_with_file_line(message, source, line))


class RecordFormatError(PyMartError):
    """A raw line cannot be split into the expected fields."""

    def __init__(self, message, source=None, line=None):
        self.source = source
        self.line = line
        super().__init__(_with_file_line(message, source, line))


class UnknownProductError(PyMartError):
    """An order mentions a SKU that is not in the catalog."""

    def __init__(self, sku, source=None, line=None):
        self.sku = sku
        self.source = source
        self.line = line
        super().__init__(
            _with_file_line(f"Unknown product SKU '{sku}'.", source, line)
        )


class DuplicateIdError(PyMartError):
    """An id (product / customer / order) already exists."""

    def __init__(self, entity, identifier):
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"Duplicate {entity} id '{identifier}'.")


class InsufficientStockError(PyMartError):
    """Not enough stock for a sale."""

    def __init__(self, sku, requested_qty, available_stock):
        self.sku = sku
        self.requested_qty = requested_qty
        self.available_stock = available_stock
        super().__init__(
            f"Insufficient stock for SKU '{sku}': requested {requested_qty}, "
            f"available {available_stock}."
        )


class InvalidDiscountError(PyMartError):
    """Discount percentage is outside the allowed range."""

    def __init__(self, sku, percentage, min_percent=0, max_percent=100):
        self.sku = sku
        self.percentage = percentage
        self.min_percent = min_percent
        self.max_percent = max_percent
        super().__init__(
            f"Invalid discount for SKU '{sku}': attempted {percentage}% "
            f"(allowed {min_percent}–{max_percent})."
        )
