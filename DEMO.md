# Demo checklist (short)

La documentation complète est dans **[README.md](./README.md)**.

Parcours minimal :

```bash
rm -f .pymart_store.json

python -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt

python -m pymart.cli order list
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

Attendu à l’import : `5/2`, `3/2`, `5/3` (imported/rejected).  
Attendu sur disque : daily + monthly + stock sous `reports/`.
