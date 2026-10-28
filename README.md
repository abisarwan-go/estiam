# PyMart — back-office toolkit

Toolkit Python en ligne de commande pour les opérations quotidiennes de **PyMart** : import d’extraits POS (produits, clients, commandes), validation/nettoyage des données, traitement des commandes, et génération de rapports datés (journalier / mensuel) archivés sur disque.

Ce README est la doc **technique** (setup, CLI, formats, architecture).  
Pour **apprendre / réviser les concepts lab par lab** (oral, veille d’examen) : lire **[LIVRE_CONCEPTS.md](./LIVRE_CONCEPTS.md)** d’abord.

---

## Prérequis

- Python **3.10+** (testé avec 3.14)
- Terminal à la **racine du projet** (`mini-projet/`)
- macOS / Linux / Windows

---

## Installation

```bash
cd mini-projet

python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Dépendances tierces (`requirements.txt`) :

| Package | Usage |
|---------|--------|
| `tabulate` | affichage tableau (démo lab 1) |
| `requests` | installée pour le lab 2 (venv / deps) |

Le CLI final (`python -m pymart.cli`) fonctionne surtout avec la **stdlib**. Les packages ci-dessus restent pour les labs / compatibilité.

Vérifier :

```bash
python -m pymart.cli --help
```

---

## Démarrage rapide (parcours complet)

Depuis la racine du projet :

```bash
# 1) repartir d’un store vide
rm -f .pymart_store.json

# 2) importer les fichiers d’exemple
python -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt

# 3) lister les commandes importées
python -m pymart.cli order list

# 4) générer les rapports
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

Résultat attendu à l’import (fichiers d’exemple) :

- products **imported=5 rejected=2**
- customers **imported=3 rejected=2**
- order lines **imported=5 rejected=3**
- messages de validation avec contexte `file=` + `line=`

Fichiers générés :

```
reports/daily/2026-06-30/daily_sales_2026-06-30.txt
reports/monthly/2026-06/monthly_summary_2026-06.txt
reports/monthly/2026-06/stock_levels_2026-06.txt
```

État persisté dans `.pymart_store.json` (ignoré par git).

---

## CLI de référence

Point d’entrée :

```bash
python -m pymart.cli [--store PATH] <commande> ...
```

| Option globale | Défaut | Description |
|----------------|--------|-------------|
| `--store` | `.pymart_store.json` | fichier JSON d’état (produits, clients, commandes, erreurs d’import) |

### `import`

Importe un ou plusieurs fichiers texte pipe-delimited (`|`).

```bash
python -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt
```

| Flag | Description |
|------|-------------|
| `--products` | catalogue produits |
| `--customers` | clients |
| `--orders` | lignes de commandes |

- Les lignes invalides sont **rejetées** (pas de crash).
- Les messages d’erreur sont **actionnables** (fichier + numéro de ligne quand possible).
- L’import met à jour le stock lors des commandes valides.

### `order`

```bash
# lister
python -m pymart.cli order list

# créer une commande (1 ligne)
python -m pymart.cli order create \
  --id 2001 \
  --customer C1001 \
  --sku NB-001 \
  --qty 1 \
  --date 2026-06-30
```

| Flag (`create`) | Requis | Description |
|-----------------|--------|-------------|
| `--id` | oui | identifiant commande |
| `--customer` | oui | id client existant |
| `--sku` | oui | SKU produit existant |
| `--qty` | oui | quantité (> 0) |
| `--date` | non | `YYYY-MM-DD` (défaut : aujourd’hui) |

Exemple d’erreur sans traceback :

```bash
python -m pymart.cli order create --id 2002 --customer C1001 --sku NOPE --qty 1
# Order error: Unknown product SKU 'NOPE'.
```

### `report`

```bash
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

| Flag | Description |
|------|-------------|
| `--type` | `daily` ou `monthly` |
| `--date` | obligatoire pour `daily` (`YYYY-MM-DD`) |
| `--month` | obligatoire pour `monthly` (`YYYY-MM`) |
| `--out` | dossier de sortie (défaut `reports/`) |

Le dossier de sortie est créé automatiquement s’il n’existe pas.

---

## Formats des fichiers d’entrée

Séparateur : `|`  
Lignes vides / commentaires `#` : ignorés  
Header optionnel (première colonne `sku` / `customer_id` / `order_id`) : sauté

### Produits — `data/products.txt`

```text
sku|name|price|quantity|kind|extra
NB-001| notebook |3.49|120|standard|
ML-001|Fresh Milk|3.49|24|perishable|2027-08-01
HP-200|Headphones|79.99|12|electronic|24
```

| Colonne | Règles |
|---------|--------|
| `sku` | non vide, normalisé en majuscules |
| `name` | non vide, title-case |
| `price` | float ≥ 0 (accepte `$`, virgules) |
| `quantity` | int ≥ 0 |
| `kind` | `standard` \| `perishable` \| `electronic` |
| `extra` | date ISO d’expiry (`perishable`) ou mois de garantie (`electronic`) |

### Clients — `data/customers.txt`

```text
customer_id|name|email|loyalty_points
C1001| aisha khan |aisha@example.com|20
```

| Colonne | Règles |
|---------|--------|
| `customer_id` | requis |
| `name` | requis |
| `email` | requis, doit contenir `@` |
| `loyalty_points` | int ≥ 0 (défaut 0) |

### Commandes — `data/orders.txt`

```text
order_id|customer_id|order_date|sku|quantity|unit_price
1001|C1001|2026-06-30|NB-001|2|3.49
```

| Colonne | Règles |
|---------|--------|
| `order_id` | requis (plusieurs lignes = même commande) |
| `customer_id` | doit exister après import clients |
| `order_date` | `YYYY-MM-DD` (aussi `YYYY/MM/DD`, `DD-MM-YYYY`) |
| `sku` | doit exister après import produits |
| `quantity` | int > 0, stock suffisant |
| `unit_price` | float ≥ 0 |

Les fichiers `data/*.txt` contiennent volontairement des lignes invalides pour démontrer le rejet contrôlé.

---

## Architecture

```
mini-projet/
├── README.md                 # cette doc
├── DEMO.md                   # checklist courte (renvoie ici)
├── requirements.txt
├── data/                     # extraits POS d’exemple
├── pymart/                   # package applicatif
│   ├── cli.py                # argparse — python -m pymart.cli
│   ├── exceptions.py         # hiérarchie d’erreurs métier
│   ├── models/               # Product, Customer, Order + sous-classes
│   ├── io/                   # parsers streaming (generators)
│   ├── services/             # Store (import, commandes, persistence JSON)
│   ├── reports/              # writers daily / monthly / stock
│   ├── inventory/            # helpers stock (labs)
│   ├── billing/              # helpers facture / taxe (labs)
│   ├── customers/            # nettoyage clients string (labs)
│   ├── sales/                # nettoyage ventes (labs)
│   ├── orders/               # import orders robuste (labs)
│   └── streaming/            # pipeline générateurs ventes (labs)
├── demos/                    # scripts de lab (lab01 … lab12)
└── tache_md/                 # énoncés des labs / tâche finale
```

### Couches principales (tâche finale)

| Module | Rôle |
|--------|------|
| `pymart.cli` | interface utilisateur CLI |
| `pymart.io.parsers` | lecture ligne à ligne + nettoyage/validation |
| `pymart.services.store` | état mémoire + `.pymart_store.json` |
| `pymart.models` | objets métier |
| `pymart.reports.writers` | écriture rapports datés |
| `pymart.exceptions` | erreurs métier typées |

### Modèle objet

- `Product` (base) → `PerishableProduct`, `ElectronicProduct`
- Polymorphisme via `describe()` (utilisé dans les rapports catalogue)
- `Customer` (identité + loyalty + validation email)
- `Order` / `OrderLine`

### Exceptions custom (exemples)

- `DataValidationError`, `RecordFormatError`
- `UnknownProductError`, `DuplicateIdError`
- `InsufficientStockError`, `InvalidDiscountError`
- base commune : `PyMartError`

### Générateurs

Utilisés notamment pour :

- streamer les lignes de fichiers (`iter_text_rows`)
- itérer les commandes d’un jour / d’un mois (`iter_orders_for_date`, `iter_orders_for_month`)
- labs streaming (`pymart.streaming`)

---

## Rapports générés

| Type | Chemin typique | Contenu |
|------|----------------|---------|
| Daily sales | `reports/daily/<YYYY-MM-DD>/daily_sales_<date>.txt` | commandes du jour, revenue, snapshot catalogue |
| Monthly summary | `reports/monthly/<YYYY-MM>/monthly_summary_<YYYY-MM>.txt` | CA mois, top produits/clients, erreurs d’import, calendrier |
| Stock levels | `reports/monthly/<YYYY-MM>/stock_levels_<YYYY-MM>.txt` | stock courant + `describe()` |

Nommage daté + arborescence jour/mois pour archivage reproductible.

---

## Labs (démos)

Les scripts de labs sont dans `demos/`. **Toujours lancer depuis la racine** :

```bash
python demos/lab01_main.py
python demos/lab03_customer_report.py
python demos/lab04_sales_report.py
python demos/lab05_import_orders.py
python demos/lab06_store_demo.py
python demos/lab07_properties_demo.py
python demos/lab08_catalog_demo.py
python demos/lab09_run_demo.py
python demos/lab10_stream_sales.py
python demos/lab11_organize_reports.py
python demos/lab12_timestamped_report.py
```

| Script | Lab | Sujet |
|--------|-----|--------|
| `lab01_main.py` | 1 | package `pymart` + inventory/billing |
| _(pas de script)_ | 2 | venv + `requirements.txt` |
| `lab03_customer_report.py` | 3 | nettoyage clients (name/email/phone) |
| `lab04_sales_report.py` | 4 | ventes nettoyées / tri prix |
| `lab05_import_orders.py` | 5 | import robuste + exceptions |
| `lab06_store_demo.py` | 6 | classes Product / Customer |
| `lab07_properties_demo.py` | 7 | properties, class/static methods |
| `lab08_catalog_demo.py` | 8 | héritage + polymorphisme |
| `lab09_run_demo.py` | 9 | exceptions stock / discount |
| `lab10_stream_sales.py` | 10 | generators + filtres |
| `lab11_organize_reports.py` | 11 | organisation fichiers rapports |
| `lab12_timestamped_report.py` | 12 | datetime / calendar / timing |

Énoncés : `tache_md/lab_*.md` et `tache_md/tache_final.md`.

Détail des commandes démos : `demos/README.md`.

---

## Checklist de validation (tâche finale)

1. `python -m pymart.cli --help` affiche les sous-commandes.
2. Import des 3 fichiers `data/` : compteurs imported/rejected + messages contextuels.
3. `order list` affiche les commandes importées.
4. `report --type daily` et `report --type monthly` écrivent au moins **2** fichiers sur disque.
5. Une commande invalide (SKU inconnu) sort en erreur claire, **sans traceback**.
6. Re-run des mêmes imports/rapports : comportement stable / reproductible.

---

## Dépannage

| Problème | Cause probable | Fix |
|----------|----------------|-----|
| `ModuleNotFoundError: pymart` | mauvais dossier courant | `cd` à la racine `mini-projet/` |
| `ModuleNotFoundError: tabulate` | venv non activé / deps manquantes | `source .venv/bin/activate` puis `pip install -r requirements.txt` |
| Import 0 / beaucoup de rejects | mauvais format / séparateur | vérifier `|` et les colonnes documentées plus haut |
| `Unknown product` à l’import orders | produits non importés avant | importer `--products` puis `--orders` |
| Rapports vides pour une date | aucune commande ce jour-là | utiliser `2026-06-30` / `2026-06` avec les samples |
| Store “bizarre” après tests | ancien `.pymart_store.json` | `rm -f .pymart_store.json` puis re-importer |

---

## Fichiers générés / ignorés

Ignorés par git (voir `.gitignore`) :

- `.venv/`
- `.pymart_store.json`
- `/reports/` (sorties CLI / lab 12)
- `pymart_workspace/` (lab 11)
- `__pycache__/`

---

## Licence / contexte

Projet pédagogique ESTIAM — mini-projet Python (labs 1–12 + tâche finale PyMart).
