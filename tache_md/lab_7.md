Set up the lab starting point with existing Product and Customer classes
Assume you already have two simple Python classes in place and working: Product and Customer. At this starting point, they are straightforward “data holders” with instance attributes set directly in __init__. A typical Product has fields like name and price, and a typical Customer has fields like name and email. There are no validations yet. For example, nothing prevents a negative product price or a malformed email address, and debugging output is still the default object representation.
Create a small lab workspace with one script you will edit throughout the lab:

pymart_lab/

main.py (edit this file)

Keep everything in main.py for now so you can focus on refactoring behavior into properties and methods without chasing imports across files.

Before changing anything, run a baseline check to confirm your starting point works end-to-end. Execute the script and verify it runs without errors and prints whatever minimal output it currently has (even if it is just a couple of print() calls). If it fails now, fix the starting point first. Otherwise you will not know whether later failures come from your refactor or from a broken baseline.
Add a validated price property on Product using a setter
A property lets you keep a simple attribute-style API (product.price) while routing all writes through validation logic. The key pattern is to store the real value in an internal attribute (for example, _price) and expose price as the controlled interface.
Implement price with a getter and a setter. The getter returns the internal value. The setter checks incoming values and rejects negative numbers by raising ValueError with a clear message, then stores the value only when it passes validation.

Store the value in an internal attribute such as self._price

@property def price(self): return self._price

@price.setter def price(self, value): raise ValueError("Price cannot be negative") when value < 0, else set self._price = value

Verify the behavior with quick instantiation tests.

Valid price: p = Product("Notebook", 2.50) then p.price should be 2.5

Invalid price: Product("Notebook", -1) should raise ValueError with your message (and Product should not end up with a negative stored _price)

Track total Product instances using a class attribute and class method
Add a class attribute to Product so the count is shared by every instance. Because it lives on the class, not on self, it represents a single source of truth for how many Product objects have been created.

A clean pattern is to (1) define a counter on the class, (2) define a class method that increments it, and (3) call that method from __init__ so every successful construction is counted in the same way.

Add the class attribute and class method:

class Product:
    total_created = 0  # class attribute shared by all Products

    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.__class__._register_new_product()

    @classmethod
    def _register_new_product(cls):
        cls.total_created += 1
Confirm it increments correctly:

p1 = Product("Notebook", 2.50)
print(Product.total_created)  # 1

p2 = Product("Pen", 1.25)
print(Product.total_created)  # 2

print(p1.total_created, p2.total_created)  # 2 2
Validate emails on Customer with a static method
A static method is a good fit for an email validator because it does not depend on any particular Customer instance. It simply answers: does this string look like an acceptable email? Keep the rule intentionally basic for the lab, using a lightweight pattern check that rejects obvious mistakes (missing @, missing a dot in the domain, spaces, empty parts).
Implement Customer.is_valid_email(email: str) -> bool as a @staticmethod, then decide where it should run. Common choices are (1) validate in __init__ to prevent creating invalid customers, and (2) validate again in whatever code path updates the email. If you have an email property setter, that is usually the cleanest single place to enforce the rule on both creation and updates. Do you want invalid emails to raise a ValueError, or should they be quietly ignored? For business objects, raising is typically clearer because invalid data should not enter the system.

__init__: call the validator before assigning self.email

Email updates: enforce via an email setter (or a dedicated update_email(...) method)

Error handling: raise ValueError with a short message when invalid

A minimal implementation can be done with a simple regular expression such as ^[^\s@]+@[^\s@]+\.[^\s@]+$ (not perfect, but good enough for practice). Then add a few small tests that cover both accepted and rejected samples.

import re

class Customer:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email  # validate through the setter

    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not isinstance(email, str):
            return False
        pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        return re.match(pattern, email) is not None

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not Customer.is_valid_email(value):
            raise ValueError(f"Invalid email: {value}")
        self._email = value
import pytest

@pytest.mark.parametrize("email", [
    "a@b.com",
    "student.name@school.edu",
    "first_last@company.org",
])
def test_valid_emails_accepted(email):
    c = Customer("Test", email)
    assert c.email == email

@pytest.mark.parametrize("email", [
    "",
    "no-at-symbol.com",
    "missing-domain@",
    "missing-dot@domain",
    "has space@domain.com",
])
def test_invalid_emails_rejected(email):
    with pytest.raises(ValueError):
        Customer("Test", email)
Improve debugging with clean repr methods for both classes
Python’s default object display (something like <__main__.Product object at 0x...>) tells you almost nothing when you are scanning logs or stepping through a debugger. A good __repr__ gives an unambiguous, constructor-like snapshot so you can immediately see what instance you are dealing with, and with what key values.
For Product, aim for a concise representation that could plausibly recreate the object, such as Product(name='Markers', price=4.99). For Customer, include identifiers that matter in logs, such as Customer(name='Ava Chen', email='ava@school.edu'). Keep __repr__ brief, stable, and focused on fields you would use to distinguish instances when something goes wrong.
class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def __repr__(self) -> str:
        return f"Product(name={self.name!r}, price={self.price!r})"


class Customer:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def __repr__(self) -> str:
        return f"Customer(name={self.name!r}, email={self.email!r})"
A quick run shows the difference between the default display and the improved output. Which one would you rather see in a stack trace or log line when a checkout fails?

# Default (no __repr__ defined):
# <__main__.Product object at 0x105b6f550>
# <__main__.Customer object at 0x105b6f610>

# With __repr__ above:
p = Product("Markers", 4.99)
c = Customer("Ava Chen", "ava@school.edu")

print(p)
print(c)
# Product(name='Markers', price=4.99)
# Customer(name='Ava Chen', email='ava@school.edu')
Demonstrate encapsulation with a name-mangled internal attribute
Pick one internal attribute per class that should not be touched from the outside, then make it name-mangled by prefixing it with a double underscore. For example, store the actual price on Product as __price, and store the email on Customer as __email. This does not make the attribute truly private, but it makes accidental access and subclass collisions far less likely, nudging everyone to use the public interface (properties).
Refactor your property getters and setters so they consistently read and write the mangled attribute, not a public-looking name like self.price or self._price.

class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price  # uses the public property setter

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, value: float) -> None:
        if value <= 0:
            raise ValueError("price must be > 0")
        self.__price = float(value)


class Customer:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email  # uses the public property setter

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, value: str) -> None:
        value = value.strip()
        if "@" not in value:
            raise ValueError("invalid email")
        self.__email = value
Now compare direct access with the public interface. The property works as expected, but direct access to the double-underscore name fails because Python rewrites it internally.

p = Product("Mouse", 25)

print(p.price)      # 25.0 (public interface)
p.price = 30        # validated update

print(p.__price)    # AttributeError: 'Product' object has no attribute '__price'
print(p._Product__price)  # 30.0 (possible, but bypasses the intended interface)
If you find yourself reaching for p._Product__price, that is usually a sign you are defeating your own validation and creating hard-to-debug state. The safer rule is simple: outside the class, use the public properties. Inside the class, use the mangled internal attributes.

Concrete outcome: enhanced, encapsulated PyMart classes with validated properties
At this point, PyMart’s Product and Customer objects behave like real business entities. Product.price is protected by validation through a property setter, Product tracks how many instances exist, Customer validates emails via a static method, and both classes print cleanly thanks to an informative __repr__. Internal state is encapsulated so you interact through the public API, not by poking at raw attributes.

You can confirm the lab is complete if all of the following are true:

Setting product.price to an invalid value is blocked, and valid values persist.

Creating products increments the total count, and the class method reports the correct total.

Invalid customer emails are rejected (either at creation time or when assigning), and valid emails are accepted.

Printing an object or inspecting it in a REPL shows a clean, readable Product(...) and Customer(...) representation.

An internal, name-mangled attribute cannot be accessed directly via its original name, reinforcing encapsulation.

Final run checklist (end-to-end):

Create two Product objects with valid prices, then verify the reported total product count matches.

Try p.price = -1 (or a non-numeric value). Confirm it fails, then set p.price = 19.99 and confirm it succeeds.

Create a Customer with a valid email, then attempt to set an invalid email and confirm it is rejected.

print(p) and print(customer) (or just evaluate them in the interpreter). Confirm the output is concise and informative.

Attempt to read the encapsulated internal attribute using its non-mangled name and confirm it is not directly accessible.

Full solution code blocks to reproduce exactly
class Product:
    # class attribute to track total instances
    _total_products = 0

    def __init__(self, name: str, price: float):
        self.name = name
        self.__sku = None  # name-mangled internal attribute (encapsulation demo)
        self.price = price  # validated via property setter
        Product._total_products += 1

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("price must be a number")
        if value < 0:
            raise ValueError("price must be >= 0")
        self._price = float(value)

    def apply_discount(self, percent: float) -> None:
        if not isinstance(percent, (int, float)):
            raise TypeError("percent must be a number")
        if percent < 0 or percent > 100:
            raise ValueError("percent must be between 0 and 100")
        self.price = self.price * (1 - percent / 100)

    def set_sku(self, sku: str) -> None:
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError("sku must be a non-empty string")
        self.__sku = sku.strip()

    def get_sku(self):
        return self.__sku

    @classmethod
    def total_products(cls) -> int:
        return cls._total_products

    def __repr__(self) -> str:
        return f"Product(name={self.name!r}, price={self.price:.2f})"
class Customer:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email  # validated via property setter

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not Customer.is_valid_email(value):
            raise ValueError("Invalid email address")
        self._email = value

    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not isinstance(email, str):
            return False
        email = email.strip()
        if "@" not in email:
            return False
        local, _, domain = email.partition("@")
        if not local or not domain:
            return False
        if domain.startswith(".") or domain.endswith("."):
            return False
        if "." not in domain:
            return False
        return True

    def __repr__(self) -> str:
        return f"Customer(name={self.name!r}, email={self.email!r})"
# Minimal test script demonstrating all features

def main():
    # Create products (validated price + instance tracking)
    p1 = Product("Notebook", 3.50)
    p2 = Product("Backpack", 29.99)

    print(p1)
    print(p2)
    print("Total products:", Product.total_products())

    # Methods and validated discount flow
    p2.apply_discount(10)
    print("After discount:", p2)

    # Encapsulation via name-mangled attribute
    p1.set_sku("NB-001")
    print("SKU via method:", p1.get_sku())
    print("Direct access attempt uses mangled name:", p1._Product__sku)

    # Customer with email validation via static method
    c1 = Customer("Ava", "ava@example.com")
    print(c1)

    print("Is valid email?", Customer.is_valid_email("bad-email"))

    # Uncomment to see validation errors:
    # Product("Pen", -1)
    # Customer("Noah", "not-an-email")


if __name__ == "__main__":
    main()