# Livre des concepts PyMart (lab par lab)

**But :** demain, tu dois pouvoir *expliquer* le projet.  
Ce fichier est ton **cours condensé**. Lis-le une fois. Chaque lab = **1 idée clé**.

> Astuce oralediag : pour chaque lab, retiens la phrase **« En une phrase »**.  
> Si on te demande un détail, regarde **« Où c’est dans le code »**.

---

## Carte mentale (vue d’ensemble)

```
Lab 1–2   → organiser le code + environnement
Lab 3–5   → nettoyer des données texte + gérer les erreurs
Lab 6–9   → objets métier (classes, héritage, exceptions)
Lab 10–12 → streamer, fichiers, dates
Finale    → tout brancher dans une CLI
```

**Produit final à citer :**  
`python -m pymart.cli` importe des fichiers, crée/liste des commandes, écrit des rapports datés.

---

## Lab 1 — Packages et imports

### En une phrase
On découpe le code en **package** (`pymart/`) pour importer proprement au lieu d’un seul gros fichier.

### Concept
- Un dossier avec `__init__.py` = **package** importable.
- Sous-packages : `inventory/`, `billing/`.
- Script d’entrée qui consomme le package : `from pymart... import ...`

### Pourquoi ça compte
Sans packages, le projet final serait illisible. La CLI importe `pymart.services`, `pymart.models`, etc.

### Où c’est dans le code
- Package : `pymart/`
- Démo : `python demos/lab01_main.py`

### Phrase orale type
> « On a un package `pymart` avec des sous-modules. Le script importe les fonctions au lieu de tout coller dans un seul fichier. »

---

## Lab 2 — Environnement virtuel + dépendances

### En une phrase
Un **venv** isole les libs du projet ; `requirements.txt` fige les versions pour reproduire l’install.

### Concept
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
- `pip freeze > requirements.txt` capture l’état.
- Sans venv : conflits entre projets / machines.

### Pourquoi ça compte
Tout le monde (toi, correcteur, CI) installe les mêmes versions (`tabulate`, `requests`…).

### Où c’est dans le code
- `requirements.txt`
- `.venv/` (local, pas commit)

### Phrase orale type
> « Le venv isole les dépendances. Le requirements.txt permet de réinstaller exactement ce qu’il faut. »

---

## Lab 3 — Nettoyage de chaînes (string processing)

### En une phrase
On transforme des lignes **sales** (espaces, casse, téléphone) en champs **standards** avec `split` / `strip` / title / digits.

### Concept
Pipeline typique :
1. `split("|")` → champs
2. `strip()` + collapse espaces
3. name → Title Case
4. email → lower, validation simple (`@`, domaine avec `.`)
5. phone → garder les chiffres → format `(555) 010-2000`

### Pourquoi ça compte
Les exports POS sont sales. Sans nettoyage, impossible de comparer / stocker proprement.

### Où c’est dans le code
- `pymart/customers/cleaning.py`
- `python demos/lab03_customer_report.py`

### Phrase orale type
> « On normalise name, email et phone avec des méthodes string, puis on imprime un rapport aligné. »

---

## Lab 4 — Listes, types, tri

### En une phrase
On convertit du texte en **types Python** (`int`, `float`), on stocke des **listes de listes**, on **trie** par prix.

### Concept
- `split("|")` + strip labels (`qty:`, `price:`)
- Enlever `$` et `,` avant `float`
- `records.sort(key=lambda r: r[3])`
- Affichage avec f-strings alignées

### Pourquoi ça compte
Trier / totaliser demande des nombres, pas des strings `"$12.00"`.

### Où c’est dans le code
- `pymart/sales/cleaning.py`
- `python demos/lab04_sales_report.py`

### Phrase orale type
> « Après nettoyage, chaque ligne est `[sku, name, qty, price]` typée, puis on trie par prix pour le rapport. »

---

## Lab 5 — try / except / else / finally

### En une phrase
Une **mauvaise ligne** ne doit pas planter tout l’import : on catch, on log, on continue.

### Concept
```python
try:
    parse(...)
except ValidationError:
    rejected += 1   # attendu : mauvaise donnée
except Exception:
    failed += 1     # inattendu
else:
    imported += 1   # succès seulement ici
finally:
    log_processed() # toujours
```
- Distinguer **PARSE** (illisible) vs **VALIDATION** (lisible mais invalide).
- Résumé : imported / rejected / failed.

### Pourquoi ça compte
En prod, un fichier a toujours des lignes pourries. Fail-fast total = inutilisable.

### Où c’est dans le code
- `pymart/orders/importer.py`
- `python demos/lab05_import_orders.py`
- Même esprit dans `pymart.cli import`

### Phrase orale type
> « try/except par ligne : on rejette la mauvaise donnée, on continue, et on affiche un résumé. »

---

## Lab 6 — Classes OOP de base

### En une phrase
`Product` et `Customer` encapsulent l’état + des **méthodes métier** (`apply_discount`, `add_loyalty_points`).

### Concept
- `__init__` = création + premières validations
- Méthodes = comportement (pas juste des données)
- `__str__` = affichage lisible

### Pourquoi ça compte
Le métier n’est plus des dicts éparpillés : c’est des objets cohérents.

### Où c’est dans le code
- `pymart/models/product.py`, `pymart/models/customer.py`
- `python demos/lab06_store_demo.py`

### Phrase orale type
> « Product et Customer sont des classes : validation à la création, méthodes pour changer le prix ou les points. »

---

## Lab 7 — Properties, classmethod, staticmethod, encapsulation

### En une phrase
On contrôle les écritures avec des **`@property`**, on compte les instances avec un **classmethod**, on valide l’email avec un **staticmethod**, on cache l’interne avec `__`.

### Concept (à ne pas mélanger)

| Outil | Rôle |
|-------|------|
| `@property` / setter | `p.price = -1` → refus via validation |
| `@classmethod` | agit sur la **classe** (`Product.total_products()`) |
| `@staticmethod` | utilitaire sans `self` (`Customer.is_valid_email`) |
| `__sku` / `__email` | name mangling → pas d’accès direct `obj.__sku` |

### Pourquoi ça compte
L’API publique reste simple (`product.price`) mais **protège** l’intégrité des données.

### Où c’est dans le code
- `pymart/models/product.py`, `customer.py`
- `python demos/lab07_properties_demo.py`

### Phrase orale type
> « Le prix passe par un setter validé. total_products est un classmethod. is_valid_email est static. Les attributs `__` renforcent l’encapsulation. »

---

## Lab 8 — Héritage + polymorphisme

### En une phrase
`PerishableProduct` / `ElectronicProduct` **héritent** de `Product` et **surchargent** `describe()` ; une boucle unique appelle `describe()` sans `isinstance`.

### Concept
```python
class PerishableProduct(Product):
    def __init__(...):
        super().__init__(...)   # réutilise la base
        self.expiry_date = ...

    def describe(self):
        return super().describe() + " | expires: ..."
```
- **Héritage** = réutiliser la base.
- **Polymorphisme** = même appel, comportement selon le type réel.

### Pourquoi ça compte
Catalogue mixte (lait, casque, carte) sans `if kind == ...` partout.

### Où c’est dans le code
- `pymart/models/perishable.py`, `electronic.py`
- `python demos/lab08_catalog_demo.py`
- Rapports finaux utilisent `product.describe()`

### Phrase orale type
> « Les sous-classes appellent super() puis ajoutent leurs champs. print_catalog appelle describe() : polymorphisme. »

---

## Lab 9 — Exceptions métier custom

### En une phrase
On crée une hiérarchie `PyMartError` → erreurs riches (`InsufficientStockError`, …) avec **contexte** (sku, qty…).

### Concept
```python
class InsufficientStockError(PyMartError):
    def __init__(self, sku, requested_qty, available_stock):
        self.sku = sku
        ...
        super().__init__(f"Insufficient stock for SKU '{sku}': ...")
```
- Catch **spécifique** d’abord, puis `PyMartError`.
- Message + attributs = diagnostic / UX.

### Pourquoi ça compte
`ValueError` générique ne dit pas *quoi* faire. Une erreur métier guide la correction.

### Où c’est dans le code
- `pymart/exceptions.py`
- `Product.sell()` / `apply_discount()`
- `python demos/lab09_run_demo.py`

### Phrase orale type
> « On a une base PyMartError et des sous-classes avec contexte. sell() lève InsufficientStockError au lieu de planter obscurément. »

---

## Lab 10 — Generators (streaming)

### En une phrase
Un **generator** (`yield`) traite **1 enregistrement à la fois** : mémoire stable même sur gros fichiers.

### Concept
```python
def read_sales_records(lines):
    for line in lines:
        yield clean(line)   # pas de liste géante

high = (r for r in read_sales_records(data) if r["total"] >= 200)
```
- **Lazy** : calcul à la demande.
- **Closure** `make_threshold_filter(min)` = fabrique de filtres.
- `list(stream)` = eager (charge tout) ; à éviter sur gros volumes.

### Pourquoi ça compte
Les exports POS peuvent être énormes. Stream = scalable.

### Où c’est dans le code
- `pymart/streaming/sales.py`
- `pymart/io/parsers.py` (`iter_text_rows`)
- `python demos/lab10_stream_sales.py`

### Phrase orale type
> « yield renvoie un flux. On filtre avec une generator expression. On ne matérialise pas toute la liste en RAM. »

---

## Lab 11 — Fichiers & dossiers (os / pathlib / shutil)

### En une phrase
On crée une arborescence de rapports, on **parcourt** avec `os.walk` / `rglob`, on **move/copy** selon des règles, on nettoie les dossiers vides.

### Concept
- `Path.mkdir(exist_ok=True)` → setup idempotent
- Règles : ex. `inventory_*` → move archive ; `sales_*` → copy archive
- `shutil.move` / `shutil.copy2`
- Dry-run avant d’écrire pour de vrai

### Pourquoi ça compte
Sans organisation, les rapports s’empilent et deviennent introuvables.

### Où c’est dans le code
- `python demos/lab11_organize_reports.py`
- Idée reprise : `reports/daily/...`, `reports/monthly/...` dans la CLI

### Phrase orale type
> « On crée reports/année, on écrit des .txt, on archive avec move/copy selon le nom de fichier. »

---

## Lab 12 — datetime / time / calendar

### En une phrase
On horodate les fichiers (`datetime.now`), on calcule une **revue +30 jours** (`timedelta`), on mesure la durée (`time`), on affiche calendrier / année bissextile (`calendar`).

### Concept
```python
now = datetime.now()
filename = f"report_{now:%Y-%m-%d_%H%M%S}.txt"
next_review = now + timedelta(days=30)
calendar.isleap(now.year)
calendar.month(now.year, now.month)
```

### Pourquoi ça compte
Les managers ont besoin de rapports **datés**, planifiables, reproductibles.

### Où c’est dans le code
- `python demos/lab12_timestamped_report.py`
- Rapports CLI : dates dans noms + chemins `daily/YYYY-MM-DD`, `monthly/YYYY-MM`

### Phrase orale type
> « Les noms de fichiers portent un timestamp. On ajoute 30 jours pour la prochaine revue, et on utilise calendar pour le mois / leap year. »

---

## Tâche finale — Assemblage CLI

### En une phrase
On branche tout dans **`python -m pymart.cli`** : import → store → orders → reports sur disque.

### Ce que tu dois pouvoir démontrer

```bash
python -m pymart.cli import --products data/products.txt --customers data/customers.txt --orders data/orders.txt
python -m pymart.cli order list
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

### Comment les labs se reconnectent

| Besoin final | Lab(s) |
|--------------|--------|
| Package propre | 1 |
| Install reproductible | 2 |
| Nettoyage texte | 3, 4 |
| Import robuste | 5, 9 |
| Modèle Product/Customer/Order | 6–8 |
| Stream parsing | 10 |
| Écrire/archiver rapports | 11, 12 |
| CLI | finale (`pymart/cli.py`) |

### Structure à citer à l’oral
> « `models` pour le domaine, `io` pour parser en streaming, `services.store` pour l’état, `reports` pour écrire, `cli` pour l’utilisateur. »

---

## Fiche de révision 10 minutes (veille d’oral)

1. **Package** = dossier + imports (`pymart`)
2. **venv + requirements** = isolation deps
3. **Strings** = split/strip/normalize
4. **Types + sort** = int/float puis `sort(key=...)`
5. **try/except/else/finally** = 1 ligne mauvaise ≠ crash total
6. **Classe** = état + méthodes
7. **property / class / static / __** = contrôle d’accès
8. **héritage + describe()** = polymorphisme
9. **PyMartError** = erreurs métier contextualisées
10. **yield** = streaming mémoire-friendly
11. **pathlib/shutil** = organiser fichiers
12. **datetime/calendar** = rapports datés
13. **CLI finale** = assemble le tout

---

## Mini glossaire

| Mot | Sens simple |
|-----|-------------|
| Package | Dossier Python importable |
| OOP | Programmer avec des objets/classes |
| Encapsulation | Cacher l’interne, exposer une API sûre |
| Héritage | Sous-classe réutilise/étend la base |
| Polymorphisme | Même méthode, comportements différents |
| Generator | Fonction qui `yield`, paresseuse |
| CLI | Programme piloté en ligne de commande |
| Idempotent | Re-exécuter sans casser l’état |

---

## Suite (demain / plus tard)

1. Relire **ce livre** (30–40 min).
2. Lancer le **démarrage rapide** du `README.md` une fois.
3. Ensuite seulement : ajouter de l’**autodoc** (docstrings) dans le code pour lire fichier par fichier.

Tu n’as pas besoin de tout mémoriser ligne à ligne : retiens la **phrase orale** de chaque lab + la carte mentale du haut.
