"""Order and order-line models."""

from datetime import date, datetime


class OrderLine:
    def __init__(self, sku, quantity, unit_price):
        self.sku = sku
        self.quantity = quantity
        self.unit_price = unit_price

    @property
    def line_total(self):
        return round(self.quantity * self.unit_price, 2)

    def describe(self):
        return (
            f"{self.sku} x{self.quantity} @ ${self.unit_price:.2f} "
            f"= ${self.line_total:.2f}"
        )


class Order:
    def __init__(self, order_id, customer_id, order_date, status="created"):
        self.order_id = order_id
        self.customer_id = customer_id
        self.order_date = order_date
        self.lines = []
        self.status = status

    @property
    def total(self):
        total = 0.0
        for line in self.lines:
            total = total + line.line_total
        return round(total, 2)

    def add_line(self, line):
        self.lines.append(line)

    def describe(self):
        return (
            f"Order {self.order_id} | customer={self.customer_id} | "
            f"date={self.order_date.isoformat()} | "
            f"lines={len(self.lines)} | total=${self.total:.2f} | "
            f"status={self.status}"
        )

    def to_dict(self):
        lines_data = []
        for line in self.lines:
            lines_data.append(
                {
                    "sku": line.sku,
                    "quantity": line.quantity,
                    "unit_price": line.unit_price,
                    "line_total": line.line_total,
                }
            )
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "order_date": self.order_date.isoformat(),
            "status": self.status,
            "lines": lines_data,
            "total": self.total,
        }

    @classmethod
    def from_dict(cls, data):
        order_date = data["order_date"]
        if isinstance(order_date, str):
            order_date = date.fromisoformat(order_date)

        order = cls(
            order_id=str(data["order_id"]),
            customer_id=str(data["customer_id"]),
            order_date=order_date,
            status=str(data.get("status", "created")),
        )
        for raw_line in data.get("lines", []):
            order.add_line(
                OrderLine(
                    sku=str(raw_line["sku"]),
                    quantity=int(raw_line["quantity"]),
                    unit_price=float(raw_line["unit_price"]),
                )
            )
        return order


def parse_order_date(value):
    """Try a few common date formats."""
    text = value.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognized date format: {value!r}")
