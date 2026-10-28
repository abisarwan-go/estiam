Lab – Extending PyMart's class hierarchy with inheritance and polymorphism
Set up the baseline Product contract for extension
Before adding subclasses, lock down what the existing Product guarantees. You will rely on a small, stable set of fields that every product must have (for example: name, price, and a unique identifier such as sku). Keep validation and formatting decisions here consistent, because subclasses will inherit them rather than re-implement them.
Confirm a single polymorphic interface that every product can answer: describe(). Code that works with products should call describe() without caring which specific subclass it is dealing with. If your current Product uses a different method name (like __str__ or details), either add describe() as the canonical method or make describe() delegate to the existing one so there is one obvious contract to extend.
Define the exact string format describe() returns, since subclasses will extend it rather than replace it blindly. A simple baseline that is easy to append to is:

"{sku} | {name} | ${price:.2f}"

When you build subclasses later, they should start from the parent description and add their extra information at the end, preserving this shared prefix so mixed lists stay readable and consistent.

Create PerishableProduct with super init and new attributes
Add an expiry_date attribute to represent when a product becomes unsafe or unsellable. Enforce a consistent format early so the rest of the code stays simple. A practical rule is: accept either a datetime.date or an ISO string like "2026-07-30", normalize to date, and reject anything that cannot be parsed or that is already in the past (if your business rules treat expired items as invalid to create).
Implement __init__ by delegating shared setup to Product via super().__init__(...), then set the new attribute. This keeps the base class responsible for base fields (like name, price, sku) and avoids duplication:

Call super().__init__(name, price, sku, ...) first

Normalize and validate expiry_date

Store self.expiry_date as a date (not a string) for reliable comparisons and sorting

Override describe() or __str__() so the perishable-specific info appears wherever products are printed. A clean approach is to reuse the base string and append the new field, for example: f"{super().__str__()} | expires: {self.expiry_date.isoformat()}". This preserves the parent formatting while making PerishableProduct immediately recognizable in logs and user-facing lists.
Create ElectronicProduct with super init and new attributes
Electronic products typically carry a warranty, so add a warranty_months attribute and enforce a simple domain rule: it must be an integer and cannot be negative. If your catalog treats “no warranty” as a valid case, allow 0, but still reject missing values or strings like "12 months".
In __init__, reuse the base Product setup with super().__init__(...) so you do not duplicate validation or assignments for shared fields like name, price, and sku. Then set the new attribute and validate it close to where it is introduced:

Call super().__init__(name, price, sku) first (or whatever the base signature is)

Validate warranty_months (type and range)

Assign self.warranty_months = warranty_months

To surface the new attribute everywhere the object is printed or logged, override describe() or __str__() and extend the base output rather than replacing it. A common pattern is to build on the parent’s text and append warranty details, for example: return the parent description plus ", warranty: {self.warranty_months} months". That keeps formatting consistent across product types while still exposing what makes ElectronicProduct unique.
Demonstrate polymorphism with a mixed product list
Polymorphism means you can treat different concrete product types as plain Product objects and still get type-specific behavior. The key is to rely on a shared method name, describe(), and let each subclass provide its own implementation.
def print_catalog(products: list[Product]) -> None:
    # No isinstance checks. No branching by type.
    for p in products:
        print(p.describe())

# Mixed concrete types, stored as Product references
products: list[Product] = [
    PerishableProduct(name="Milk", price=3.49, expiration_date="2026-08-01", storage_temp_c=4),
    ElectronicProduct(name="Headphones", price=79.99, warranty_years=2, power_watts=5),
    PerishableProduct(name="Strawberries", price=5.99, expiration_date="2026-07-31", storage_temp_c=2),
]

print_catalog(products)
Expected output will differ by subclass because each one dispatches its own describe() implementation:

Perishable: Milk ($3.49). Expires: 2026-08-01. Store at 4°C.
Electronic: Headphones ($79.99). Warranty: 2 years. Power: 5W.
Perishable: Strawberries ($5.99). Expires: 2026-07-31. Store at 2°C.
Concrete outcome: a working product hierarchy you can run
You should now have a small but complete hierarchy with three classes. A base Product, plus PerishableProduct and ElectronicProduct that call super().__init__(...) to reuse shared setup, then add their own fields. The final piece is a single loop function that accepts a mixed list of products and prints readable, subtype-specific output by relying on method overrides rather than type checks.
A minimal run scenario can be as small as creating one instance of each class, putting them into a single list, and iterating:

Create p1 = Product(...), p2 = PerishableProduct(...), p3 = ElectronicProduct(...)

Put them into products = [p1, p2, p3]

Call one function like print_catalog(products) that loops and prints each item (for example, by calling a shared method such as describe() or by using each object’s __str__) so each subtype can present its extra details

To sanity-check that inheritance and overriding are actually working, do three quick checks. First, confirm the relationships: isinstance(p2, Product) and isinstance(p3, Product) should be True. Second, confirm override behavior by calling the same method on each object inside the loop and verifying the perishable output includes its perishable-only data and the electronic output includes its electronic-only data. Third, confirm super() usage indirectly by checking that shared base fields (like name and price) are still present and correct on the subclasses, since those should be initialized by the base constructor that the subclass called via super().