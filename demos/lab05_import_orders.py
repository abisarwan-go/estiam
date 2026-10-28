"""Demonstrate robust PyMart order import error handling (lab 5)."""

from __future__ import annotations

import _bootstrap  # noqa: F401

import logging
from collections import Counter

from pymart.orders import ImportSummary, import_orders

RAW_LINES = [
    "1001|SKU-RED-CHAIR|2|39.99",
    "1002|SKU-BLUE-DESK|1|129.50",
    "1003|SKU-GREEN-LAMP|3",  # missing unit_price
    "1004|SKU-WHITE-RUG|two|89.00",  # bad int
    "1005|SKU-BLACK-SHELF|1|9.9x",  # bad float
    "oops-not-even-delimited",  # not enough fields
    "",  # empty
]


def print_summary(summary: ImportSummary) -> None:
    print("PYMART ORDER IMPORT SUMMARY")
    print("-" * 72)
    print(f"Total rows : {summary.total}")
    print(f"Imported   : {summary.imported}")
    print(f"Rejected   : {summary.rejected}")
    print(f"Failed     : {summary.failed}")
    print(
        f"Check      : "
        f"{summary.imported + summary.rejected + summary.failed} "
        f"== {summary.total}"
    )
    print("-" * 72)

    if summary.orders:
        print("Imported orders:")
        for order in summary.orders:
            print(
                f"  #{order['order_id']}  {order['sku']:<18} "
                f"qty={order['quantity']}  "
                f"unit={order['unit_price']:.2f}  "
                f"total={order['line_total']:.2f}"
            )
        print("-" * 72)

    if summary.errors:
        print("Rejections / failures:")
        for err in summary.errors:
            print(
                f"  row {err['row']:>2}  [{err['category']}]  {err['message']}"
            )
            print(f"         hint: {err['hint']}")
            print(f"         data: {err['row_data']!r}")
        print("-" * 72)

        reason_counts = Counter(err["message"] for err in summary.errors)
        print("Top rejection reasons:")
        for reason, count in reason_counts.most_common():
            print(f"  {count}x  {reason}")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    summary = import_orders(RAW_LINES)
    print()
    print_summary(summary)


if __name__ == "__main__":
    main()
