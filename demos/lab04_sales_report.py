"""Print a cleaned, price-sorted PyMart sales report (lab 4)."""

import _bootstrap  # noqa: F401

from pymart.sales import clean_sales

RAW_SALES = [
    "  sku-001 |  WIDGET  | qty: 2 | price:  3.50 ",
    "SKU-002|gadget|QTY:10|PRICE:$12.00",
    " sku-003 | Thingamajig | qty:  1 | price: 0.99",
    "SKU-004 |  widget pro| qty:5| price: 1,299.00 ",
    " sku-005|GADGET mini | qty: 03 | price: $7.5 ",
    "SKU-006 | Doohickey| qty: 0 | price:  4 ",
    " SKU-007|  thingamajig XL  | QTY:2 | PRICE: $0.990 ",
    "sku-008 | Widget| qty: -1 | price: $3.50",
]


def format_report(records: list[list]) -> str:
    """Build an aligned multi-line report string sorted by price."""
    rows = sorted(records, key=lambda r: (r[3], r[1], r[0]))

    lines = [
        "PYMART SALES REPORT (cleaned, sorted by price)",
        "-" * 72,
        f"{'SKU':<10} {'Item':<18} {'Qty':>5} {'Price':>10} {'Line Total':>12}",
        "-" * 72,
    ]

    grand_total = 0.0
    for sku, name, qty, price in rows:
        line_total = qty * price
        grand_total += line_total
        lines.append(
            f"{sku:<10} {name:<18} {qty:>5d} {price:>10.2f} {line_total:>12.2f}"
        )

    lines.append("-" * 72)
    lines.append(f"{'Grand Total':>47} {grand_total:>12.2f}")
    return "\n".join(lines)


def main() -> None:
    cleaned = clean_sales(RAW_SALES)
    print(format_report(cleaned))


if __name__ == "__main__":
    main()
