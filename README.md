# PyMart back-office toolkit

Production-oriented CLI for importing POS extracts, processing orders, and writing dated operational reports.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

## CLI

```bash
python -m pymart.cli --help

# Import sample extracts (pipe-delimited text)
python -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt

# List / create orders
python -m pymart.cli order list
python -m pymart.cli order create --id 2001 --customer C1001 --sku NB-001 --qty 1 --date 2026-06-30

# Reports (written under reports/ with day/month archive folders)
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

State is persisted in `.pymart_store.json` (override with `--store`).

## Package layout

- `pymart/models` — Product hierarchy, Customer, Order
- `pymart/io` — streaming parsers (generators)
- `pymart/services` — import/order store
- `pymart/reports` — daily/monthly writers
- `pymart/cli.py` — argparse entry point (`python -m pymart.cli`)
- `data/` — sample messy extracts for demos

## Notes

- Invalid rows are rejected with actionable messages (file + line) and do not crash the import.
- Product subclasses override `describe()` for polymorphic catalog/report output.
- Monthly run also writes a stock-level report next to the summary.
