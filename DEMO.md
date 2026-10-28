# PyMart final demo checklist

## 1. Help

```bash
python -m pymart.cli --help
```

## 2. Successful import (with rejected bad rows)

```bash
rm -f .pymart_store.json
python -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt
```

Expected:

- products imported=5 rejected=2
- customers imported=3 rejected=2
- order lines imported=5 rejected=3
- validation messages include file + line context

## 3. Orders

```bash
python -m pymart.cli order list
python -m pymart.cli order create --id 2001 --customer C1001 --sku NB-001 --qty 1 --date 2026-06-30
```

## 4. Reports on disk

```bash
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

Creates at least:

- `reports/daily/2026-06-30/daily_sales_2026-06-30.txt`
- `reports/monthly/2026-06/monthly_summary_2026-06.txt`
- `reports/monthly/2026-06/stock_levels_2026-06.txt`

## 5. Graceful error example

```bash
python -m pymart.cli order create --id 2002 --customer C1001 --sku NOPE --qty 1
```

Prints an actionable `Order error: ... Unknown product SKU ...` and exits non-zero without a traceback crash.
