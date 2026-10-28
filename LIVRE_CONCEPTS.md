# Livre des concepts PyMart (lab par lab)

**But :** demain, tu dois pouvoir *expliquer* le projet **sans déjà connaître le jargon**.  
Ce fichier est ton **cours autodocumenté**. Chaque lab = 1 idée. Chaque bout de code est **décortiqué**.

### Comment lire
1. Lis **« En une phrase »**
2. Lis **« Décodage »** (le code est traduit en français)
3. Garde la **« Phrase orale »** pour demain

### Règle du livre
Si tu vois du code, il y a toujours un bloc **Décodage ligne par ligne**.  
Rien n’est “évident” : `lambda`, `yield`, `self`, `super()`, etc. sont expliqués.

---

## Carte mentale

```
Lab 1–2   → organiser le code + environnement
Lab 3–5   → nettoyer du texte + gérer les erreurs
Lab 6–9   → objets (classes), héritage, exceptions
Lab 10–12 → flux (generators), fichiers, dates
Finale    → tout brancher dans une CLI
```

**Produit final :**  
`python -m pymart.cli` = programme lancé dans le terminal qui importe des fichiers, gère des commandes, écrit des rapports.

**Décodage de cette commande :**
- `python` = lance l’interpréteur Python
- `-m` = “exécute un **module** / package comme un programme”
- `pymart.cli` = le fichier `pymart/cli.py` (ou le package cli) à l’intérieur du dossier `pymart`

---

## Lab 1 — Packages et imports

### En une phrase
On range le code dans un **package** `pymart/` pour pouvoir écrire `from pymart... import ...` au lieu de tout coller dans un seul fichier.

### Vocabulaire
| Mot | Sens |
|-----|------|
| **Module** | un fichier `.py` |
| **Package** | un **dossier** de modules, reconnu par Python grâce à `__init__.py` |
| **Import** | “va chercher ce code ailleurs et donne-moi accès” |

### Structure
```text
pymart/                 ← package principal
  __init__.py           ← dit à Python : “ce dossier est un package”
  inventory/            ← sous-package
    __init__.py
    stock.py            ← module avec des fonctions stock
  billing/
    __init__.py
    invoice.py
demos/lab01_main.py     ← script qui UTILISE le package
```

### Code typique
```python
from pymart.inventory.stock import add_stock, get_stock
```

### Décodage ligne par ligne
- `from pymart.inventory.stock`
  - entre dans le package `pymart`
  - puis le sous-package `inventory`
  - puis le module `stock.py`
- `import add_stock, get_stock`
  - récupère **deux fonctions** définies dans ce fichier
- Après ça, tu peux appeler `add_stock(...)` dans ton script

### Pourquoi ça compte
Le projet final a beaucoup de fichiers. Sans packages, tu te perds et les imports cassent.

### Où c’est
- Code : `pymart/`
- Démo : `python demos/lab01_main.py`

### Phrase orale
> « On a un package `pymart` avec des sous-modules. Le script importe les fonctions au lieu de tout mettre dans un seul fichier. »

---

## Lab 2 — venv + requirements

### En une phrase
Un **environnement virtuel** isole les bibliothèques du projet ; `requirements.txt` liste les versions à réinstaller.

### Vocabulaire
| Mot | Sens |
|-----|------|
| **venv** | “mini Python privé” pour ce projet seulement |
| **pip** | outil qui **installe** des bibliothèques |
| **dépendance** | bibliothèque dont ton projet a besoin (`tabulate`, `requests`…) |
| **requirements.txt** | liste figée : `nom==version` |

### Commandes
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Décodage
- `python -m venv .venv`  
  crée un dossier `.venv` = environnement isolé
- `source .venv/bin/activate`  
  “à partir de maintenant, ce terminal utilise CE Python-là”
- `pip install -r requirements.txt`  
  `-r` = “lis le fichier et installe tout ce qui est dedans”

### Pourquoi ça compte
Sans venv : “ça marche sur mon PC” / “pas sur le tien”.

### Où c’est
- `requirements.txt`
- `.venv/` (local, pas dans git)

### Phrase orale
> « Le venv isole les libs. Le requirements.txt permet de réinstaller les mêmes versions. »

---

## Lab 3 — Nettoyage de chaînes (strings)

### En une phrase
On prend une ligne sale, on la découpe, on nettoie chaque morceau (espaces, casse, téléphone).

### Exemple de donnée brute
```text
"grACE hopper| grace.hopper@NAVY.mil|555.010.2001"
```

### Pipeline (étapes)
1. **Séparer** les champs
2. **Enlever** les espaces inutiles
3. **Normaliser** name / email / phone

### Code typique
```python
parts = raw.split("|")
name = parts[0].strip().title()
email = "".join(parts[1].split()).lower()
digits = "".join(ch for ch in parts[2] if ch.isdigit())
phone = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
```

### Décodage
- `raw.split("|")`  
  coupe la string dès qu’il y a `|` → liste `["grACE hopper", " grace...", "555..."]`
- `parts[0]`  
  1er élément de la liste (index commence à **0**)
- `.strip()`  
  enlève espaces au début/à la fin
- `.title()`  
  `grace hopper` → `Grace Hopper`
- `"".join(parts[1].split())`  
  - `.split()` sans argument coupe sur tous les espaces  
  - `"".join(...)` recolle **sans** espace → email sans trous
- `.lower()`  
  majuscules → minuscules
- `ch.isdigit()`  
  `True` si le caractère est un chiffre `0-9`
- `"".join(ch for ch in ... if ...)`  
  “fabrique une nouvelle string avec seulement les chiffres”  
  (c’est une **compréhension** : boucle courte en une ligne)
- `digits[:3]`  
  “tranche” : les 3 premiers caractères (indices 0,1,2)
- `f"(...)"`  
  **f-string** : colle du texte + des variables dans une string

### Pourquoi ça compte
Les exports magasin sont sales. Sans normaliser, impossible de comparer deux emails / téléphones.

### Où c’est
- `pymart/customers/cleaning.py`
- `python demos/lab03_customer_report.py`

### Phrase orale
> « On split, strip, title/lower, et on reconstruit le téléphone à partir des chiffres seulement. »

---

## Lab 4 — Types, listes, tri

### En une phrase
On transforme du texte en vrais nombres (`int`/`float`), on range chaque vente dans une liste, puis on **trie par prix**.

### Forme d’une ligne nettoyée
```python
# index:  0        1         2     3
row = ["SKU-001", "Widget",  2,  3.50]
#        sku       name     qty  price
```

### Pourquoi `r[3]` ?
Parce que le **prix** est le **4e** élément, donc index **3** (0,1,2,3).

### Code qui fait peur (expliqué)
```python
records.sort(key=lambda r: r[3])
```

### Décodage COMPLET de cette ligne
1. `records`  
   une **liste** de lignes, chaque ligne est elle-même une liste `[sku, name, qty, price]`
2. `.sort(...)`  
   trie **la liste sur place** (modifie `records` directement)
3. `key=...`  
   “pour décider l’ordre, utilise CETTE valeur de chaque élément”
4. `lambda r: r[3]`  
   - `lambda` = **mini-fonction anonyme** (sans `def`, sans nom)  
   - `r` = “une ligne” (un élément de `records`)  
   - `r[3]` = le prix de cette ligne  
   - donc : “trie selon le prix”

### Version équivalente PLUS LISIBLE (même idée)
```python
def prix_de_la_ligne(r):
    return r[3]   # le prix

records.sort(key=prix_de_la_ligne)
```
`lambda` = juste la version courte de cette fonction.

### Autre code utile du lab
```python
price = float(text.replace("$", "").replace(",", ""))
```
- `.replace("$", "")` enlève le symbole dollar
- `.replace(",", "")` enlève les séparateurs de milliers (`1,299.00` → `1299.00`)
- `float(...)` convertit la string en nombre à virgule

### Pourquoi ça compte
Tu ne peux pas trier correctement des prix s’ils restent des strings `"$12.00"`.

### Où c’est
- `pymart/sales/cleaning.py`
- `python demos/lab04_sales_report.py`

### Phrase orale
> « Chaque vente devient une liste typée. On trie avec sort(key=...) sur le prix (index 3). lambda est juste une petite fonction anonyme. »

---

## Lab 5 — try / except / else / finally

### En une phrase
Si une ligne est mauvaise, on **attrape l’erreur**, on la compte, et on **continue** les autres lignes.

### Vocabulaire
| Mot | Sens |
|-----|------|
| **Exception** | “erreur Python” qui interrompt le flux normal |
| **raise** | “lève / déclenche” une erreur |
| **try** | “essaie ce code risqué” |
| **except** | “si cette erreur arrive, fais ça” |
| **else** | “si try a réussi (pas d’erreur)” |
| **finally** | “fais ça dans tous les cas (succès ou échec)” |

### Code
```python
try:
    order = parse_order_line(line)
except ValidationError:
    rejected += 1
except Exception:
    failed += 1
else:
    imported += 1
    orders.append(order)
finally:
    log("ligne traitée")
```

### Décodage du flux
1. Entre dans `try` → tente de parser
2. Si `ValidationError` (donnée invalide attendue) → `rejected += 1`
3. Sinon si autre `Exception` (bug inattendu) → `failed += 1`
4. Si **aucune** erreur → `else` s’exécute → on compte un import réussi
5. Dans tous les cas → `finally` logue

### PARSE vs VALIDATION (idée métier)
- **PARSE** : “je n’arrive même pas à lire” (pas assez de colonnes, `two` au lieu de `2`)
- **VALIDATION** : “j’ai lu, mais la règle métier refuse” (quantité ≤ 0, etc.)

### Pourquoi ça compte
Un seul mauvais enregistrement ne doit pas tuer tout l’import.

### Où c’est
- `pymart/orders/importer.py`
- `python demos/lab05_import_orders.py`
- Même logique dans `python -m pymart.cli import`

### Phrase orale
> « try/except par ligne : on rejette la mauvaise donnée, on continue, puis on affiche imported/rejected. »

---

## Lab 6 — Classes (OOP de base)

### En une phrase
Une **classe** décrit un type d’objet (ex: Product). Une **instance** est un objet concret créé à partir de la classe.

### Vocabulaire
| Mot | Sens |
|-----|------|
| **Classe** | le “moule” |
| **Instance** | un objet fabriqué avec le moule |
| **Attribut** | donnée collée à l’objet (`self.price`) |
| **Méthode** | fonction collée à l’objet (`apply_discount`) |
| **`self`** | “cet objet-ci” (l’instance courante) |
| **`__init__`** | constructeur : appelé à la création `Product(...)` |
| **`__str__`** | texte affiché quand on fait `print(objet)` |

### Code
```python
class Product:
    def __init__(self, sku, name, price, quantity):
        self.sku = sku
        self.name = name
        self.price = price
        self.quantity = quantity

    def apply_discount(self, percentage):
        self.price = self.price * (1 - percentage / 100)
        return self.price

p = Product("NB-001", "Notebook", 3.49, 120)
p.apply_discount(10)
```

### Décodage
- `class Product:`  
  définit le moule Product
- `def __init__(self, ...):`  
  s’exécute quand tu écris `Product(...)`
- `self.price = price`  
  range la valeur **dans l’objet**
- `p = Product(...)`  
  crée **une instance**
- `p.apply_discount(10)`  
  appelle la méthode sur **cette** instance `p`  
  (Python passe `p` automatiquement dans `self`)

### Pourquoi ça compte
Au lieu de dicts partout, on a des objets métier avec comportement.

### Où c’est
- `pymart/models/product.py`, `customer.py`
- `python demos/lab06_store_demo.py`

### Phrase orale
> « Product/Customer sont des classes : __init__ initialise, les méthodes changent l’état, print utilise __str__. »

---

## Lab 7 — property / classmethod / staticmethod / encapsulation

### En une phrase
On contrôle comment on lit/écrit les données (`property`), on a des outils de classe (`classmethod`), des utilitaires sans objet (`staticmethod`), et on cache l’interne (`__nom`).

### 1) `@property` + setter
```python
@property
def price(self):
    return self._price

@price.setter
def price(self, value):
    if value < 0:
        raise ValueError("price must be >= 0")
    self._price = value
```

### Décodage property
- `@property`  
  permet d’écrire `p.price` (comme un attribut) alors que c’est une méthode
- `@price.setter`  
  le code exécuté quand on fait `p.price = ...`
- Intérêt : `p.price = -1` peut être **refusé**

`_price` (un underscore) = convention “interne”.  
`__price` / `__sku` (deux underscores) = **name mangling** : Python renomme en coulisse pour éviter l’accès direct accidentel.

### 2) `@classmethod`
```python
@classmethod
def total_products(cls):
    return cls._total_products
```
- Reçoit `cls` (la **classe**), pas une instance
- Sert pour un compteur partagé par tous les Product

### 3) `@staticmethod`
```python
@staticmethod
def is_valid_email(email):
    return "@" in email and "." in email.split("@")[-1]
```
- Pas de `self`, pas de `cls`
- Juste une fonction rangée dans la classe (organisation)

### Tableau anti-confusion
| Décorateur | Reçoit | Sert à |
|------------|--------|--------|
| méthode normale | `self` | agir sur **un** objet |
| `@classmethod` | `cls` | agir sur / pour la **classe** |
| `@staticmethod` | rien | utilitaire lié thématiquement |
| `@property` | `self` | lecture contrôlée style attribut |

### Où c’est
- `pymart/models/product.py`, `customer.py`
- `python demos/lab07_properties_demo.py`

### Phrase orale
> « price est une property validée. total_products est classmethod. is_valid_email est staticmethod. __sku cache l’interne. »

---

## Lab 8 — Héritage + polymorphisme

### En une phrase
Une sous-classe **réutilise** la classe mère (`super()`) et peut **redéfinir** une méthode (`describe`) ; une boucle appelle la même méthode sur des objets différents.

### Vocabulaire
| Mot | Sens |
|-----|------|
| **Héritage** | `class Enfant(Parent)` : Enfant reçoit le comportement du Parent |
| **`super()`** | “appelle la version du parent” |
| **Override** | redéfinir une méthode du parent |
| **Polymorphisme** | même appel (`p.describe()`), comportement selon le vrai type |

### Code
```python
class PerishableProduct(Product):
    def __init__(self, sku, name, price, expiry_date, quantity=0):
        super().__init__(sku, name, price, quantity)
        self.expiry_date = expiry_date

    def describe(self):
        return super().describe() + f" | expires: {self.expiry_date}"

products = [Product(...), PerishableProduct(...), ElectronicProduct(...)]
for p in products:
    print(p.describe())   # pas de if type == ...
```

### Décodage
- `class PerishableProduct(Product)`  
  “PerishableProduct **est un** Product” (+ options en plus)
- `super().__init__(...)`  
  laisse Product initialiser sku/name/price/quantity
- `def describe(self):` dans l’enfant  
  remplace/étend la version parent
- Boucle `for p in products: p.describe()`  
  Python choisit la bonne version selon l’objet réel = **polymorphisme**

### Pourquoi ça compte
Catalogue mixte sans une forêt de `if`.

### Où c’est
- `pymart/models/perishable.py`, `electronic.py`
- `python demos/lab08_catalog_demo.py`

### Phrase orale
> « Les sous-classes appellent super(), surchargent describe(), et une seule boucle affiche chaque type correctement. »

---

## Lab 9 — Exceptions custom

### En une phrase
On crée nos propres types d’erreurs (`PyMartError`, `InsufficientStockError`) avec un message clair + des attributs utiles.

### Code
```python
class PyMartError(Exception):
    """Base de toutes les erreurs métier PyMart."""

class InsufficientStockError(PyMartError):
    def __init__(self, sku, requested_qty, available_stock):
        self.sku = sku
        self.requested_qty = requested_qty
        self.available_stock = available_stock
        super().__init__(
            f"Insufficient stock for SKU '{sku}': "
            f"requested {requested_qty}, available {available_stock}."
        )
```

### Décodage
- `class ... (Exception)` / `(PyMartError)`  
  “cette classe **est une** exception”
- On stocke `self.sku`, etc. pour que le `except` puisse lire le contexte
- `super().__init__("message")`  
  définit le texte vu dans `print(erreur)` / `str(erreur)`

### Catch spécifique → général
```python
try:
    product.sell(10)
except InsufficientStockError as e:
    print(e.sku, e.requested_qty, e.available_stock)
except PyMartError as e:
    print("autre erreur métier:", e)
```
- `as e` = “range l’objet erreur dans la variable `e`”
- On attrape d’abord le cas précis, puis le filet plus large

### Où c’est
- `pymart/exceptions.py`
- `python demos/lab09_run_demo.py`

### Phrase orale
> « Hiérarchie PyMartError. InsufficientStockError porte sku/quantités. On catch du plus précis au plus général. »

---

## Lab 10 — Generators (`yield`) et streaming

### En une phrase
Un generator **rend les résultats un par un** (`yield`) au lieu de construire une énorme liste en mémoire.

### Vocabulaire
| Mot | Sens |
|-----|------|
| **`yield`** | “renvoie une valeur… et met la fonction en pause jusqu’au prochain tour” |
| **Generator** | fonction qui utilise `yield` |
| **Lazy** | calcule seulement quand on demande |
| **Eager** | calcule/charge tout d’un coup (`list(...)`) |
| **Closure** | fonction interne qui “se souvient” d’une variable extérieure |

### Code generator
```python
def read_sales_records(lines):
    for line in lines:
        yield clean(line)
```

### Décodage
- Boucle sur chaque `line`
- `yield clean(line)` envoie **un** enregistrement nettoyé
- La fonction ne crée pas `big_list.append(...)` de tout le fichier

### Filtre en generator expression
```python
high = (r for r in read_sales_records(data) if r["total"] >= 200)
```
- `( ... )` avec `for` = generator (paresseux)
- `[ ... ]` serait une list comprehension (charge tout)

### Closure (filtre configurable)
```python
def make_threshold_filter(min_total):
    def keep(record):
        return record["total"] >= min_total
    return keep

keep_high = make_threshold_filter(200)
keep_high(une_vente)  # True/False
```

### Décodage closure
- `make_threshold_filter(200)` crée et **retourne** la fonction `keep`
- `keep` “se rappelle” que `min_total` vaut `200`
- Ça évite les variables globales

### Où c’est
- `pymart/streaming/sales.py`
- `pymart/io/parsers.py` (`iter_text_rows`)
- `python demos/lab10_stream_sales.py`

### Phrase orale
> « yield stream les lignes une par une. Les generator expressions filtrent sans tout charger. Une closure fabrique un filtre avec seuil mémorisé. »

---

## Lab 11 — Fichiers et dossiers

### En une phrase
On crée des dossiers, on écrit des fichiers, on les déplace/copie selon des règles, on parcourt l’arborescence.

### Vocabulaire
| Mot | Sens |
|-----|------|
| **`pathlib.Path`** | objet “chemin de fichier/dossier” |
| **`mkdir`** | créer un dossier |
| **`exist_ok=True`** | “si ça existe déjà, ne plante pas” |
| **`shutil.move`** | déplacer (l’original part) |
| **`shutil.copy2`** | copier (l’original reste) |
| **idempotent** | re-exécuter ne casse pas / converge vers le même état |
| **dry-run** | afficher ce qu’on *ferait*, sans le faire |

### Code
```python
from pathlib import Path
import shutil

folder = Path("reports") / "2024"
folder.mkdir(parents=True, exist_ok=True)

path = folder / "sales_2024-01.txt"
path.write_text("contenu\n", encoding="utf-8")

shutil.move(str(path), "reports/archive/sales/2024/sales_2024-01.txt")
```

### Décodage
- `Path("reports") / "2024"`  
  construit un chemin portable (`reports/2024`)
- `parents=True`  
  crée aussi les dossiers parents manquants
- `write_text(...)`  
  écrit le fichier
- `move` vs `copy2`  
  archive “en déplaçant” vs “en gardant l’original”

### Où c’est
- `python demos/lab11_organize_reports.py`
- CLI finale : `reports/daily/...`, `reports/monthly/...`

### Phrase orale
> « pathlib crée l’arborescence, on écrit des .txt, puis move/copy selon des règles de nommage. »

---

## Lab 12 — datetime / time / calendar

### En une phrase
On prend “maintenant”, on fabrique un nom de fichier horodaté, on calcule une date +30 jours, on mesure une durée, on affiche un calendrier.

### Code
```python
from datetime import datetime, timedelta
import time
import calendar

now = datetime.now()
filename = f"report_{now.strftime('%Y-%m-%d_%H%M%S')}.txt"
next_review = now + timedelta(days=30)

start = time.time()
# ... travail ...
duration = time.time() - start

calendar.isleap(now.year)          # True/False année bissextile
print(calendar.month(now.year, now.month))
```

### Décodage
- `datetime.now()`  
  date + heure actuelles
- `strftime('...')`  
  formate en texte selon un motif :
  - `%Y` année 4 chiffres
  - `%m` mois
  - `%d` jour
  - `%H%M%S` heure/minute/seconde
- `timedelta(days=30)`  
  “une durée de 30 jours”
- `now + timedelta(...)`  
  date de revue
- `time.time()`  
  horodatage machine (secondes) ; différence = durée
- `calendar.isleap`  
  bissextile ?
- `calendar.month`  
  petit calendrier texte du mois

### Où c’est
- `python demos/lab12_timestamped_report.py`
- Rapports CLI datés

### Phrase orale
> « Timestamp dans le nom de fichier, next review = now + 30 jours, durée avec time.time, calendrier avec calendar. »

---

## Tâche finale — CLI qui assemble tout

### En une phrase
`pymart.cli` est le “tableau de bord” : import → commandes → rapports, en réutilisant les concepts des labs.

### Commandes à savoir lancer
```bash
python -m pymart.cli import --products data/products.txt --customers data/customers.txt --orders data/orders.txt
python -m pymart.cli order list
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

### Décodage architecture (ce que tu dis à l’oral)
| Dossier | Rôle simple |
|---------|-------------|
| `pymart/models` | objets métier (Product, Customer, Order…) |
| `pymart/io` | lire/nettoyer les fichiers (souvent en streaming) |
| `pymart/services` | logique + mémoire/persistance (`.pymart_store.json`) |
| `pymart/reports` | écrire les rapports sur disque |
| `pymart/cli.py` | arguments terminal (`argparse`) |
| `pymart/exceptions.py` | erreurs métier |

### Lien labs → finale
| Besoin | Vient du lab |
|--------|--------------|
| Package | 1 |
| Install deps | 2 |
| Nettoyage texte | 3–4 |
| Import robuste | 5, 9 |
| Classes / héritage | 6–8 |
| Streaming | 10 |
| Fichiers + dates | 11–12 |
| CLI | finale |

---

## Fiche 10 minutes (veille)

1. Package = dossier importable (`__init__.py`)
2. venv + requirements = isolation des libs
3. split/strip/lower/title = nettoyer du texte
4. `sort(key=lambda r: r[3])` = trier selon le prix (index 3) ; `lambda` = mini-fonction
5. try/except/else/finally = une ligne pourrie ≠ crash total
6. class / self / __init__ = objets métier
7. property / classmethod / staticmethod / `__` = contrôle d’accès
8. héritage + `super()` + `describe()` = polymorphisme
9. exceptions custom = erreurs métier avec contexte
10. `yield` = stream 1 par 1
11. pathlib/shutil = dossiers/fichiers
12. datetime/calendar = rapports datés
13. CLI = assemblage

---

## Mini glossaire global

| Mot | Sens ultra simple |
|-----|-------------------|
| Index | Position dans une liste (`0` = premier) |
| f-string | `f"prix={x}"` colle variables dans du texte |
| lambda | petite fonction sans nom |
| key= | “trie/groupe selon cette valeur” |
| self | l’objet courant |
| super() | appelle le parent |
| yield | renvoie et met en pause |
| Exception | erreur gérable avec try/except |
| CLI | programme en ligne de commande |
| Idempotent | re-run sans casser |

---

## Suite

1. Lis **ce livre** (c’est la priorité).
2. Lance une fois le quick start du `README.md`.
3. Plus tard : docstrings autodoc dans le code source.
