"""In-memory store + save/load as JSON."""

import json
from datetime import date
from pathlib import Path

from pymart.exceptions import (
    DataValidationError,
    DuplicateIdError,
    InsufficientStockError,
    PyMartError,
    UnknownProductError,
)
from pymart.io.parsers import (
    iter_text_rows,
    parse_customer_row,
    parse_order_row,
    parse_product_row,
)
from pymart.models import Customer, ElectronicProduct, PerishableProduct, Product
from pymart.models.order import Order, OrderLine


class Store:
    def __init__(self, state_path=".pymart_store.json"):
        self.state_path = Path(state_path)
        self.products = {}
        self.customers = {}
        self.orders = {}
        self.import_errors = []

    def save(self):
        products_data = []
        for product in self.products.values():
            products_data.append(self._product_to_dict(product))

        customers_data = []
        for customer in self.customers.values():
            customers_data.append(
                {
                    "customer_id": customer.customer_id,
                    "name": customer.name,
                    "email": customer.email,
                    "loyalty_points": customer.loyalty_points,
                }
            )

        orders_data = []
        for order in self.orders.values():
            orders_data.append(order.to_dict())

        payload = {
            "products": products_data,
            "customers": customers_data,
            "orders": orders_data,
            "import_errors": self.import_errors,
        }
        self.state_path.write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    def load(self):
        if not self.state_path.exists():
            return
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        self.products.clear()
        self.customers.clear()
        self.orders.clear()
        self.import_errors = list(payload.get("import_errors", []))

        for raw in payload.get("products", []):
            product = self._product_from_dict(raw)
            self.products[str(product.sku)] = product

        for raw in payload.get("customers", []):
            customer = Customer(
                customer_id=raw["customer_id"],
                name=raw["name"],
                email=raw["email"],
                loyalty_points=int(raw.get("loyalty_points", 0)),
            )
            self.customers[customer.customer_id] = customer

        for raw in payload.get("orders", []):
            order = Order.from_dict(raw)
            self.orders[order.order_id] = order

    @staticmethod
    def _product_to_dict(product):
        data = {
            "sku": product.sku,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity,
            "kind": "standard",
        }
        if isinstance(product, PerishableProduct):
            data["kind"] = "perishable"
            data["extra"] = product.expiry_date.isoformat()
            data["storage_temp_c"] = product.storage_temp_c
        elif isinstance(product, ElectronicProduct):
            data["kind"] = "electronic"
            data["extra"] = str(product.warranty_months)
            data["power_watts"] = product.power_watts
        return data

    @staticmethod
    def _product_from_dict(raw):
        kind = raw.get("kind", "standard")
        sku = raw["sku"]
        name = raw["name"]
        price = float(raw["price"])
        quantity = int(raw["quantity"])
        extra = raw.get("extra", "")

        if kind == "perishable":
            return PerishableProduct(
                sku=sku,
                name=name,
                price=price,
                quantity=quantity,
                expiry_date=extra or "2099-12-31",
                storage_temp_c=raw.get("storage_temp_c"),
            )
        if kind == "electronic":
            if str(extra).isdigit():
                months = int(extra)
            else:
                months = 12
            return ElectronicProduct(
                sku=sku,
                name=name,
                price=price,
                quantity=quantity,
                warranty_months=months,
                power_watts=raw.get("power_watts"),
            )
        return Product(sku=sku, name=name, price=price, quantity=quantity)

    def _build_product(self, raw):
        kind = raw["kind"]
        if kind == "perishable":
            return PerishableProduct(
                sku=raw["sku"],
                name=raw["name"],
                price=raw["price"],
                quantity=raw["quantity"],
                expiry_date=raw["extra"] or "2099-12-31",
            )
        if kind == "electronic":
            if str(raw["extra"]).isdigit():
                months = int(raw["extra"])
            else:
                months = 12
            return ElectronicProduct(
                sku=raw["sku"],
                name=raw["name"],
                price=raw["price"],
                quantity=raw["quantity"],
                warranty_months=months,
            )
        return Product(
            sku=raw["sku"],
            name=raw["name"],
            price=raw["price"],
            quantity=raw["quantity"],
        )

    def import_products(self, path):
        imported = 0
        rejected = 0
        source = str(path)

        for line_no, fields in iter_text_rows(path):
            try:
                raw = parse_product_row(fields, source=source, line=line_no)
                if raw["sku"] in self.products:
                    raise DuplicateIdError("product", raw["sku"])
                product = self._build_product(raw)
            except PyMartError as exc:
                rejected = rejected + 1
                self.import_errors.append(str(exc))
            else:
                self.products[str(product.sku)] = product
                imported = imported + 1

        return imported, rejected

    def import_customers(self, path):
        imported = 0
        rejected = 0
        source = str(path)

        for line_no, fields in iter_text_rows(path):
            try:
                raw = parse_customer_row(fields, source=source, line=line_no)
                if raw["customer_id"] in self.customers:
                    raise DuplicateIdError("customer", raw["customer_id"])
                customer = Customer(
                    customer_id=raw["customer_id"],
                    name=raw["name"],
                    email=raw["email"],
                    loyalty_points=raw["loyalty_points"],
                )
            except PyMartError as exc:
                rejected = rejected + 1
                self.import_errors.append(str(exc))
            else:
                self.customers[customer.customer_id] = customer
                imported = imported + 1

        return imported, rejected

    def import_orders(self, path):
        """Import order lines and group them by order_id."""
        imported_lines = 0
        rejected = 0
        source = str(path)
        grouped = {}

        for line_no, fields in iter_text_rows(path):
            try:
                raw = parse_order_row(fields, source=source, line=line_no)
                if raw["sku"] not in self.products:
                    raise UnknownProductError(
                        raw["sku"], source=source, line=line_no
                    )
                if raw["customer_id"] not in self.customers:
                    raise DataValidationError(
                        f"unknown customer_id '{raw['customer_id']}'",
                        source=source,
                        line=line_no,
                    )
                product = self.products[raw["sku"]]
                if raw["quantity"] > product.quantity:
                    raise InsufficientStockError(
                        raw["sku"], raw["quantity"], product.quantity
                    )
            except PyMartError as exc:
                rejected = rejected + 1
                self.import_errors.append(str(exc))
            else:
                order_id = raw["order_id"]
                if order_id not in grouped:
                    grouped[order_id] = []
                grouped[order_id].append(raw)
                imported_lines = imported_lines + 1

        for order_id, rows in grouped.items():
            if order_id in self.orders:
                self.import_errors.append(
                    str(DuplicateIdError("order", order_id))
                )
                continue

            first = rows[0]
            order = Order(
                order_id=order_id,
                customer_id=first["customer_id"],
                order_date=date.fromisoformat(first["order_date"]),
                status="imported",
            )
            for raw in rows:
                product = self.products[raw["sku"]]
                product.sell(raw["quantity"])
                order.add_line(
                    OrderLine(
                        sku=raw["sku"],
                        quantity=raw["quantity"],
                        unit_price=raw["unit_price"],
                    )
                )
            self.orders[order_id] = order

        return imported_lines, rejected

    def create_order(
        self,
        order_id,
        customer_id,
        sku,
        quantity,
        order_date=None,
    ):
        if order_id in self.orders:
            raise DuplicateIdError("order", order_id)
        if customer_id not in self.customers:
            raise DataValidationError(f"unknown customer_id '{customer_id}'")
        if sku not in self.products:
            raise UnknownProductError(sku)

        product = self.products[sku]
        product.sell(quantity)
        order = Order(
            order_id=order_id,
            customer_id=customer_id,
            order_date=order_date or date.today(),
            status="created",
        )
        order.add_line(
            OrderLine(sku=sku, quantity=quantity, unit_price=product.price)
        )
        self.orders[order_id] = order
        return order

    def list_orders(self):
        orders = list(self.orders.values())

        def sort_key(order):
            return (order.order_date, order.order_id)

        orders.sort(key=sort_key)
        return orders

    def iter_orders_for_date(self, day):
        """Generator: yield orders for one calendar day."""
        for order in self.list_orders():
            if order.order_date == day:
                yield order

    def iter_orders_for_month(self, year, month):
        """Generator: yield orders for one calendar month."""
        for order in self.list_orders():
            if order.order_date.year == year and order.order_date.month == month:
                yield order
