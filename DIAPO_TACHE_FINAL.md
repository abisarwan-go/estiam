---
marp: true
paginate: true
title: PyMart — Tâche finale
description: Diaporama de présentation du back-office CLI
---

<!--
COMMENT UTILISER CE FICHIER
1) Google Slides / PowerPoint : copie chaque slide (titre + puces) une par une
2) Marp (VS Code extension "Marp for VS Code") : Preview → Export PDF/PPTX
3) À l’oral : lis les “Notes orateur” sous chaque slide (en commentaire HTML)
-->

# PyMart
## Back-office CLI — Tâche finale

Présentation du livrable  
`python -m pymart.cli`

<!-- Notes orateur :
Présente-toi en 10s. Dis : “J’ai construit un outil en ligne de commande pour importer des exports POS, traiter les commandes et générer des rapports datés.”
-->

---

# Contexte métier

- PyMart = magasin multi-catégories
- Les exports POS sont **sales** (espaces, casse, valeurs invalides)
- Les managers veulent des rapports **reproductibles** (daily / monthly)

<!-- Notes orateur :
Insiste sur le problème : données sales + besoin de rapports archivables.
-->

---

# Objectif de la solution

Un toolkit CLI qui sait :

1. **Importer** products / customers / orders
2. **Créer / lister** des commandes
3. **Générer** des rapports sur disque
4. **Afficher** des erreurs claires **sans crash**

<!-- Notes orateur :
Ces 4 points reprennent exactement le sujet tache_final.
-->

---

# Démo — commandes clés

```bash
python -m pymart.cli --help

python -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt

python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

<!-- Notes orateur :
Si démo live : lance import puis les 2 reports. Sinon montre screenshots.
-->

---

# Architecture package

```text
pymart/
  cli.py          → interface utilisateur
  models/         → Product, Customer, Order...
  io/             → parsers streaming
  services/       → Store (état + JSON)
  reports/        → writers daily/monthly
  exceptions.py   → erreurs métier
```

Séparation des responsabilités = maintenable

<!-- Notes orateur :
Dis : “Pas un seul script monolithique : package clair.”
-->

---

# OOP — modèle métier

- Classes : **Product**, **Customer**, **Order** (+ OrderLine)
- Héritage : `Product` → `PerishableProduct` / `ElectronicProduct`
- Polymorphisme : méthode **`describe()`** surchargée
- Encapsulation : validations / properties

<!-- Notes orateur :
Exemple oral : “print(p.describe()) marche pour lait et casque sans if type.”
-->

---

# Robustesse — erreurs

- Exceptions custom :  
  `DataValidationError`, `RecordFormatError`,  
  `UnknownProductError`, `DuplicateIdError`, …
- Import **ligne par ligne** : reject + continue
- Messages avec **fichier + numéro de ligne**
- CLI : message clair, **pas de traceback** pour les erreurs métier

<!-- Notes orateur :
Montre un reject à l’import ou `SKU NOPE`.
-->

---

# Generators + fichiers + dates

- **Generator** : `iter_text_rows` / `yield` (streaming)
- **Filesystem** : crée `reports/` si absent, archive par date
- **datetime / calendar** :
  - rapport daily daté
  - résumé monthly + calendrier du mois

<!-- Notes orateur :
Coche mentalement les exigences stdlib du sujet.
-->

---

# Sorties (preuves)

Au moins **2 types** de rapports sur disque :

1. `reports/daily/2026-06-30/daily_sales_2026-06-30.txt`
2. `reports/monthly/2026-06/monthly_summary_2026-06.txt`  
   (+ `stock_levels_2026-06.txt`)

Mêmes entrées → sorties **reproductibles**

<!-- Notes orateur :
Ouvre les fichiers dans l’IDE pendant la slide.
-->

---

# Checklist consignes

- [x] Package + structure claire
- [x] `requirements.txt`
- [x] CLI import / order / report
- [x] ≥ 2 exceptions custom
- [x] ≥ 1 generator utilisé
- [x] ≥ 2 rapports datés écrits
- [x] Docs : `README.md` + preuves (screenshots / vidéo)

<!-- Notes orateur :
Slide de clôture : “Le livrable couvre la grille.” Puis questions.
-->

---

# Merci — Questions ?

Repo / lancement :

```bash
python -m pip install -r requirements.txt
python -m pymart.cli --help
```

Docs : `README.md` · `PREUVE_SOUMISSION.md`
