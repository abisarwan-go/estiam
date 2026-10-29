"""Write dated reports to disk (daily + monthly + stock)."""

import calendar
from datetime import datetime, timedelta
from pathlib import Path


def _ensure_archive_dirs(out_dir, day):
    day_dir = out_dir / "daily" / day.strftime("%Y-%m-%d")
    month_dir = out_dir / "monthly" / day.strftime("%Y-%m")
    day_dir.mkdir(parents=True, exist_ok=True)
    month_dir.mkdir(parents=True, exist_ok=True)
    return day_dir


def write_daily_report(store, report_date, out_dir="reports"):
    out = Path(out_dir)
    day_dir = _ensure_archive_dirs(out, report_date)
    filename = f"daily_sales_{report_date.isoformat()}.txt"
    path = day_dir / filename

    orders = list(store.iter_orders_for_date(report_date))
    revenue = 0.0
    for order in orders:
        revenue = revenue + order.total
    revenue = round(revenue, 2)
    next_review = report_date + timedelta(days=30)

    lines = [
        "PyMart Daily Sales Summary",
        "==========================",
        f"Report date: {report_date.isoformat()}",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"Next review date: {next_review.isoformat()}",
        f"Orders: {len(orders)}",
        f"Revenue: ${revenue:.2f}",
        "",
        "Order details:",
    ]
    if not orders:
        lines.append("  (no orders)")
    else:
        for order in orders:
            lines.append(f"  - {order.describe()}")
            for line in order.lines:
                lines.append(f"      • {line.describe()}")

    lines.append("")
    lines.append("Catalog snapshot (polymorphic describe):")
    for product in store.products.values():
        lines.append(f"  - {product.describe()}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _top_items(counter, limit=5):
    """Return the top N items from a {key: number} dict."""
    items = list(counter.items())

    def by_value(item):
        return item[1]

    items.sort(key=by_value, reverse=True)
    return items[:limit]


def write_monthly_report(store, year, month, out_dir="reports"):
    out = Path(out_dir)
    month_key = f"{year:04d}-{month:02d}"
    month_dir = out / "monthly" / month_key
    month_dir.mkdir(parents=True, exist_ok=True)
    path = month_dir / f"monthly_summary_{month_key}.txt"

    orders = list(store.iter_orders_for_month(year, month))
    revenue = 0.0
    for order in orders:
        revenue = revenue + order.total
    revenue = round(revenue, 2)

    by_sku = {}
    by_customer = {}
    for order in orders:
        if order.customer_id not in by_customer:
            by_customer[order.customer_id] = 0.0
        by_customer[order.customer_id] = (
            by_customer[order.customer_id] + order.total
        )
        for line in order.lines:
            if line.sku not in by_sku:
                by_sku[line.sku] = 0
            by_sku[line.sku] = by_sku[line.sku] + line.quantity

    top_skus = _top_items(by_sku, limit=5)
    top_customers = _top_items(by_customer, limit=5)

    _weekday, last_day = calendar.monthrange(year, month)
    month_calendar = calendar.month(year, month)
    is_leap = calendar.isleap(year)

    lines = [
        "PyMart Monthly Summary",
        "======================",
        f"Period: {month_key} (days 1–{last_day})",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"Leap year: {is_leap}",
        f"Orders: {len(orders)}",
        f"Revenue: ${revenue:.2f}",
        "",
        "Top-selling products:",
    ]
    if not top_skus:
        lines.append("  (none)")
    else:
        for sku, qty in top_skus:
            lines.append(f"  - {sku}: {qty} units")

    lines.append("")
    lines.append("Top customers by spend:")
    if not top_customers:
        lines.append("  (none)")
    else:
        for customer_id, spend in top_customers:
            customer = store.customers.get(customer_id)
            if customer:
                label = customer.name
            else:
                label = customer_id
            lines.append(f"  - {label} ({customer_id}): ${spend:.2f}")

    lines.append("")
    lines.append("Failed/rejected import messages:")
    if not store.import_errors:
        lines.append("  (none)")
    else:
        for err in store.import_errors[-20:]:
            lines.append(f"  - {err}")

    lines.append("")
    lines.append("Month calendar:")
    lines.append(month_calendar.rstrip("\n"))
    lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Second report file: stock levels for the same month folder.
    stock_path = month_dir / f"stock_levels_{month_key}.txt"
    stock_lines = [
        "PyMart Stock Level Report",
        "=========================",
        f"As of period: {month_key}",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    products = list(store.products.values())

    def by_sku_name(product):
        return str(product.sku)

    products.sort(key=by_sku_name)
    for product in products:
        stock_lines.append(
            f"{product.sku:<12} qty={product.quantity:<5} "
            f"price=${product.price:<8.2f} {product.describe()}"
        )
    stock_path.write_text("\n".join(stock_lines) + "\n", encoding="utf-8")

    return path
