Implement PyMartError and context-rich subclasses
A clear exception hierarchy makes failures predictable and actionable. Start with a single module-wide base exception so callers can catch “any PyMart domain error” in one place while still distinguishing specific cases when needed.
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

    def __init__(self, sku: str, percentage: float):
        self.sku = sku
        self.percentage = percentage
        super().__init__(
            f"Invalid discount for SKU '{sku}': attempted {percentage}%."
        )
Integrate custom exceptions into Product domain methods
Domain methods should protect the integrity of a Product by validating inputs at the point where state changes. When a rule is violated, raise a custom exception that clearly identifies what was attempted and what the product’s current state was, so the caller can present a useful message or make a recovery decision.
Selling should validate the requested quantity and fail fast when stock cannot cover the sale. If qty is not positive, treat it as invalid input. If qty exceeds current stock, raise InsufficientStockError and include context such as sku (or product id), requested_qty, and available_stock so an error message can be as specific as “SKU A123: requested 5, available 2.”
Discounting should validate the percentage range before applying it. If percent is outside the allowed bounds, raise InvalidDiscountError with context like sku, percent, and the accepted min_percent and max_percent. This makes it straightforward to report what was wrong, and it avoids partially applying business logic when inputs are invalid.

[An image about a Product object flow showing sell and apply_discount raising different exceptions based on validation]

Validate behavior with a runner script and targeted exception handling
Create a small runner script that exercises three scenarios: one happy path and two failures that hit different custom exceptions. Keep it intentionally narrow so you can see the exception type, message, and stored context without noise. For example, run a purchase that succeeds, then run a purchase that fails due to insufficient stock, and finally apply a discount that fails validation (such as a negative discount or one above the allowed maximum).
Handle failures by catching your custom hierarchy explicitly, from most specific to most general, and print messages that include both what happened and what to do next. Catching subclasses (for example, a stock-related error separately from a discount-related error) allows you to tailor output, while still keeping a final except PyMartError as e as a safety net for any other domain error you introduced.

Catch each PyMartError subclass you expect and print a short, contextual message.

In the message, include key context fields (such as product_id, sku, requested_qty, available_qty, or discount_percent).

Avoid catching broad Exception unless you are also re-raising or logging it, so domain failures do not get swallowed.

Confirm that your exceptions surface stored context by printing it directly in the handler and verifying it matches the triggering inputs. If your exception stores context in an attribute like context (or similar), print it alongside str(e) and the exception class name. If your __str__ already formats context, verify that the formatted output includes the fields you care about for diagnostics and user-facing feedback, and that the same context can be reused for logging without rebuilding it at the call site.

[An image about console output examples showing caught exception messages for stock and discount errors]

Concrete outcome: a PyMart product module with a custom exception hierarchy
A clean end state is a small, reusable PyMart module that keeps domain rules close to the domain model, and reports all violations through a consistent exception hierarchy. The result is easy to import in other projects, straightforward to test, and predictable to run because errors are never hidden behind silent returns.

A package-ready layout that stays coherent as PyMart grows:

pymart/exceptions.py: PyMartError plus domain-specific subclasses

pymart/product.py: Product and its rule-enforcing methods

pymart/__init__.py: optional re-exports for a friendly public API

run_demo.py: a small script that exercises success and failure paths