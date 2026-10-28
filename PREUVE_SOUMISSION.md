# Preuve de soumission — quoi faire concrètement

Tu as **déjà** le code + `requirements.txt` + docs.  
Il te reste surtout la **preuve** demandée : **procédure + captures** *ou* **vidéo courte**.

Choisis **une** option (la plus rapide pour toi = **captures**).

---

## Ce qui est déjà OK (ne stresse pas)

| Deliverable | Chez toi |
|-------------|----------|
| Package Python | `pymart/` |
| Structure claire | `models/`, `io/`, `services/`, `reports/`, `cli.py` |
| `requirements.txt` | présent |
| CLI | `python -m pymart.cli` |
| Générateur | `pymart/io/parsers.py` (`iter_text_rows` / yield) |
| ≥ 2 exceptions custom | `pymart/exceptions.py` |
| ≥ 2 rapports datés | `reports/daily/...`, `reports/monthly/...` |
| Docs run | `README.md`, `DEMO.md` |

---

## Option A (recommandée) — Document + screenshots

### ✅ Déjà prêt dans le repo
Le pack complet est dans **`preuves/`** :

| Fichier | Usage |
|---------|--------|
| [`preuves/PROCEDURE_PREUVES.html`](./preuves/PROCEDURE_PREUVES.html) | **À ouvrir dans le navigateur → Imprimer → Enregistrer en PDF** (rendu type screenshots) |
| [`preuves/PROCEDURE_PREUVES.md`](./preuves/PROCEDURE_PREUVES.md) | Même contenu en Markdown |
| `preuves/captures/*.txt` | Sorties terminal réelles |
| `preuves/rapports/*.txt` | Copies des 3 fichiers de rapports générés |
| `bash preuves/regenerate_captures.sh` | Relancer le parcours et régénérer les preuves |

**À rendre demain :** le **PDF** exporté depuis le HTML (ou le dossier `preuves/` zippé).

### Fichier à rendre (si tu refais à la main)
Crée un dossier `preuves/` (ou un PDF / Google Doc) avec **5 captures** + 2–3 phrases chacune.

### Avant de capturer
```bash
cd mini-projet
source .venv/bin/activate   # si besoin
rm -f .pymart_store.json
```

### Capture 1 — Lancer la CLI (help)
Commande :
```bash
python -m pymart.cli --help
```
Screenshot : le terminal qui montre `import`, `order`, `report`.

### Capture 2 — Import réussi (+ erreurs gérées)
```bash
python -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt
```
Screenshot :  
- `imported=... rejected=...`  
- messages `file=... line=...`  
→ ça prouve **validation errors handled** + import OK.

### Capture 3 — Rapport daily sur disque
```bash
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
```
Puis ouvre le fichier dans l’éditeur / Finder :
```text
reports/daily/2026-06-30/daily_sales_2026-06-30.txt
```
Screenshot du **chemin** + début du contenu.

### Capture 4 — Rapport monthly (2e rapport)
```bash
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```
Screenshot d’au moins un de :
```text
reports/monthly/2026-06/monthly_summary_2026-06.txt
reports/monthly/2026-06/stock_levels_2026-06.txt
```

### Capture 5 — Erreur gracieuse (pas de traceback)
```bash
python -m pymart.cli order create --id 2002 --customer C1001 --sku NOPE --qty 1
```
Screenshot : `Order error: Unknown product SKU 'NOPE'.`  
(pas de long stack trace)

### Bonus utile (1 capture)
Arborescence projet dans VS Code / Finder :
`pymart/`, `data/`, `demos/`, `requirements.txt`, `README.md`.

### Texte minimal à coller sous les images
> 1) Help CLI  
> 2) Import sample data with rejected invalid rows  
> 3) Daily report written under reports/daily/...  
> 4) Monthly + stock reports under reports/monthly/...  
> 5) Unknown SKU handled via custom exception message

---

## Option B — Vidéo / démo live (2–4 min)

Enregistre ton écran (QuickTime sur Mac) et montre dans l’ordre :

1. Structure dossiers (`pymart/`, `data/`)
2. `python -m pymart.cli import ...`
3. `report daily` + ouvrir le fichier
4. `report monthly` + ouvrir le fichier
5. `order create ... SKU NOPE` (erreur propre)

Pas besoin de parler longtemps : montre + 1 phrase par étape.

---

## Checklist finale avant envoi

- [ ] Projet zip / repo contient `pymart/`, `data/`, `requirements.txt`, `README.md`
- [ ] Sur machine propre : `python -m venv .venv && pip install -r requirements.txt`
- [ ] `python -m pymart.cli import ...` marche
- [ ] Dossier `reports/` créé tout seul
- [ ] Au moins 2 fichiers rapports datés visibles
- [ ] Preuve jointe : screenshots **ou** vidéo
- [ ] (Oral) tu peux citer : package, OOP héritage `describe()`, exceptions, generator, datetime/path

---

## Comment “soumettre” en pratique

Selon ce que demande ESTIAM / le prof :

1. **Repo GitHub** (ton `estiam`) + lien PR/main  
2. **+** PDF/Doc `preuves` avec les 5 screenshots  
   **ou** lien Drive/YouTube unlisted de la vidéo  
3. Éventuellement un **zip** du projet sans `.venv/` ni `__pycache__/`

Tu n’as **pas** besoin de tout relire : demain = lancer les 5 commandes + capturer.
