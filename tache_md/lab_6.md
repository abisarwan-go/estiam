Build the Product class with core inventory attributes
A Product represents one sellable inventory item. Give it a stable identifier (sku), a human-friendly name, a price, and an on-hand quantity. Type expectations keep the class predictable: sku and name as str, price as a numeric money value, and quantity as an int count of units.
Implement __init__ so object creation is the gatekeeper for valid data. Assign fields, then validate immediately: require non-empty sku and name (trim whitespace), ensure price is non-negative, and ensure quantity is an integer that is zero or more. If a value is invalid, raise a clear exception (commonly ValueError) so bad inventory data cannot silently enter your system.
Choose representations that match how the business will use the data. quantity should stay an integer because inventory is counted in whole units for this lab. price can be stored as a float for simplicity, but constrain it to two decimal places if you plan to display currency, or store cents as an integer (for example, price_cents: int) to avoid rounding surprises. Whichever you choose, keep the constraint consistent: no negative prices, no negative quantities, and no empty identifiers.
Build the Customer class with identity and loyalty tracking
A Customer object should capture stable identity information and a small, reliable piece of business state. Start with three attributes:

name (required): a non-empty string used for display and basic identification.

email (required): a non-empty string that looks like a real email (at minimum, contains @).

loyalty_points (optional): an integer counter representing the customer’s current balance in your loyalty program.

Implement an __init__ constructor that sets sensible defaults and rejects obviously bad inputs early. A practical baseline is to default loyalty_points to 0, and ensure it stays within an allowed range such as 0 to 1_000_000.

class Customer:
    def __init__(self, name, email, loyalty_points=0):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(email, str) or not email.strip() or "@" not in email:
            raise ValueError("email must be a non-empty address containing '@'")
        if not isinstance(loyalty_points, int):
            raise TypeError("loyalty_points must be an integer")
        if loyalty_points < 0 or loyalty_points > 1_000_000:
            raise ValueError("loyalty_points must be between 0 and 1,000,000")

        self.name = name.strip()
        self.email = email.strip()
        self.loyalty_points = loyalty_points
Loyalty points represent earned value the customer can later redeem. They are not currency, but they behave like a balance, so negative values usually indicate a bug or an invalid operation. If you later introduce expiration rules, tiers, or redemption, those can build on the same invariant: loyalty_points is always an integer within the allowed range.
Add one practical method to each class for business behavior
Business behavior belongs on the objects that own the data. A Product should be able to adjust its own price, and a Customer should be able to manage their own loyalty points. Keep these methods small, validate inputs, and make the side effects explicit.

class Product:
    def __init__(self, sku, name, price, quantity):
        self.sku = sku
        self.name = name
        self.price = float(price)
        self.quantity = int(quantity)

    def apply_discount(self, percentage):
        """Reduce price by a percentage.

        Args:
            percentage (float|int): Discount percent from 0 to 100.

        Returns:
            float: The updated price.

        Side effects:
            Updates self.price.
        """
        if not isinstance(percentage, (int, float)):
            raise TypeError("percentage must be a number")
        if percentage < 0 or percentage > 100:
            raise ValueError("percentage must be between 0 and 100")

        new_price = self.price * (1 - percentage / 100)
        # Safety: never allow a negative price due to rounding or bad data.
        self.price = max(0.0, round(new_price, 2))
        return self.price


class Customer:
    def __init__(self, customer_id, full_name, loyalty_points=0):
        self.customer_id = customer_id
        self.full_name = full_name
        self.loyalty_points = int(loyalty_points)

    def add_loyalty_points(self, amount):
        """Add points to the customer's loyalty balance.

        Args:
            amount (int): Non-negative number of points to add.

        Returns:
            int: The updated loyalty point balance.

        Side effects:
            Updates self.loyalty_points.
        """
        if not isinstance(amount, int):
            raise TypeError("amount must be an integer")
        if amount < 0:
            raise ValueError("amount must be non-negative")

        self.loyalty_points += amount
        return self.loyalty_points
A common mistake is making these methods accept “anything” and silently doing nothing on bad input. If a discount is 250 or points are negative, that is a data-quality problem. Failing fast with clear errors makes bugs easier to find and keeps your objects in a valid state.

Make objects readable with str and print clear details
Good objects are easy to inspect. When you implement __str__, you decide what someone sees when they print() an instance, which makes debugging and quick validation much faster.

Implement __str__ for Product so it consistently displays the SKU, name, price, and quantity. Keep the format compact and predictable, for example: SKU=PM-1001 | Name=Notebook | Price=$4.99 | Qty=32. This way, a single print(product) tells you whether inventory-related method calls actually changed the quantity you expected.

Implement __str__ for Customer to display name, email, and loyalty points in the same spirit, for example: Customer=Alex Kim | Email=alex@school.edu | Points=120. Then validate your formatting by printing objects before and after calling your class methods.

Print a Product, call your product behavior method, print it again to confirm updated values.

Print a Customer, call your loyalty-related method, print it again to confirm points changed.

If the output is hard to scan or missing a key field, revise the __str__ format until it reads clearly in one line.

Instantiate multiple products and customers and test the workflow
Create a small “mini store” in code by instantiating several Product and Customer objects with realistic values. Use a mix of prices and stock levels so changes are easy to spot when you print them (for example, a low-stock item and a higher-priced item). Do the same for customers, including different starting loyalty point balances if your class supports it.

Next, simulate activity by applying a discount to a couple of products and adding loyalty points to one or more customers. The goal is to make state changes visible. If the discount reduces a product’s price, and adding points increases a customer’s loyalty total, printing objects before and after should clearly show what changed.

# Assumes Product and Customer are already defined from earlier sections.

products = [
    Product(sku="NB-001", name="Notebook", price=3.49, stock=120),
    Product(sku="PN-101", name="Pen Pack", price=5.99, stock=45),
    Product(sku="BK-550", name="Backpack", price=39.95, stock=8),
]

customers = [
    Customer(customer_id="C1001", full_name="Aisha Khan", email="aisha@example.com", loyalty_points=20),
    Customer(customer_id="C1002", full_name="Miguel Rivera", email="miguel@example.com", loyalty_points=0),
]

print("BEFORE")
for p in products:
    print(p)
for c in customers:
    print(c)

# Demonstrate state changes
products[2].apply_discount(0.15)      # 15% off backpack
products[1].apply_discount(0.10)      # 10% off pen pack
customers[0].add_loyalty_points(50)   # Aisha earns points
customers[1].add_loyalty_points(10)   # Miguel earns points

print("\nAFTER")
for p in products:
    print(p)
for c in customers:
    print(c)
Concrete outcome
You now have two working Python classes that represent PyMart’s core business entities: Product for inventory-aware items, and Customer for identity plus loyalty tracking. Each class supports meaningful state changes through its methods, so the objects behave like real parts of a store rather than passive data containers.

A runnable test script ties everything together by creating multiple products and customers, mutating state (such as stock levels and loyalty points), and printing results to confirm behavior end-to-end. Because __str__ is implemented cleanly, your output is readable and consistent, setting you up for the next layer of features where clear object displays become essential for carts, orders, and receipts.