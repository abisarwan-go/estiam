Set up the messy PyMart dataset you will clean
You are going to turn a messy list of sales record strings into a clean, sorted sales report that a human can read and a program can reliably process. The final output you are working toward is a normalized table where each row has: sku, name, qty, and price, with consistent types and formatting.
Start with this intentionally inconsistent dataset. It includes extra whitespace, mixed casing, and numbers written in different formats (commas, currency symbols, and inconsistent decimals):

sales_records = [
    "  sku-001 |  WIDGET  | qty: 2 | price:  3.50 ",
    "SKU-002|gadget|QTY:10|PRICE:$12.00",
    " sku-003 | Thingamajig | qty:  1 | price: 0.99",
    "SKU-004 |  widget pro| qty:5| price: 1,299.00 ",
    " sku-005|GADGET mini | qty: 03 | price: $7.5 ",
    "SKU-006 | Doohickey| qty: 0 | price:  4 ",
    " SKU-007|  thingamajig XL  | QTY:2 | PRICE: $0.990 ",
    "sku-008 | Widget| qty: -1 | price: $3.50",
]
Split raw record strings into fields with split
When each sale is stored as a single comma-separated string, the first job is turning it into separate fields. In Python, split(',') converts one record into a list, which makes each piece easy to clean and convert later.

record = "A104, Notebook, 3, 4.99"
raw_fields = record.split(',')
print(raw_fields)
# ['A104', ' Notebook', ' 3', ' 4.99']
A few pitfalls show up immediately. Extra spaces leave leading or trailing whitespace in each element, which is why the split result often looks “messy” at first. Missing fields can happen when a record has too few commas, which shifts meaning and breaks conversions. Embedded commas are trickier. A product name like "Binder, Large" will be split into two fields unless the dataset uses quoting rules, which basic split(',') does not understand.

A minimal guardrail is to validate the expected field count before proceeding:

EXPECTED_FIELDS = 4  # SKU, Name, Quantity, Price

raw_fields = record.split(',')
if len(raw_fields) != EXPECTED_FIELDS:
    raise ValueError(f"Bad record (expected {EXPECTED_FIELDS} fields): {record}")
Clean whitespace and normalize fields with strip
When you split a raw record into fields, the values often keep invisible baggage: leading spaces, trailing spaces, or both. Those characters matter because string comparisons are literal. 'SKU-001' != 'SKU-001 ' and 'Widget' != ' Widget'. That can break lookups, grouping, sorting, deduping, and even numeric conversion if you later try to parse quantity or price.
Apply strip() to every field to remove whitespace on both ends, then normalize the fields you will rely on downstream in a consistent way. For a PyMart-style record, a practical pattern is: strip everything, standardize SKU casing, and standardize product names for reporting or matching.

# After split(), you might have something like:
sku, name, qty, price = fields  # e.g., [' sku-001 ', '  Deluxe Widget  ', ' 2 ', ' 19.99  ']

# 1) Strip all fields (leading and trailing whitespace)
sku   = sku.strip()
name  = name.strip()
qty   = qty.strip()
price = price.strip()

# 2) Normalize consistently for downstream processing
sku_norm  = sku.upper()          # stable keys for matching
name_norm = name.title()         # cleaner, consistent display

# Spot-check prints (use repr to reveal spaces)
print('sku raw/clean:', repr(fields[0]), '->', repr(sku_norm))
print('name raw/clean:', repr(fields[1]), '->', repr(name_norm))
print('qty raw/clean:', repr(fields[2]), '->', repr(qty))
print('price raw/clean:', repr(fields[3]), '->', repr(price))
Convert quantity and price to numeric types safely
After trimming and normalizing your text fields, convert the numeric ones into real numbers so you can sort, total, and format reliably. A safe pattern is: clean first, convert second. For quantity, aim for an int. For price, aim for a float (or keep it as a string until you can handle decimals consistently).
Common issues to clean before conversion include stray spaces, currency symbols (like $), and separators. A practical approach is to remove what you do not need, then convert:

Quantity: qty_text.strip() then int(qty_text)

Price: price_text.strip().replace("$", "") then float(price_text)

If prices might contain commas (e.g., "1,299.00"), remove them before converting: replace(",", ""). If you might see empty strings or non-numeric junk (e.g., "N/A"), decide how you want to treat those records before calling int() or float().

When conversion fails, you have three reasonable policies. Which one fits your goal: a report that is always produced, or data integrity that never hides problems?

Skip: ignore the record and keep going. Best for one-off reports where a few bad rows are acceptable.

Default: set a fallback like qty = 0 or price = 0.0. Best when you need output no matter what, but it can distort totals.

Raise: stop with an error (or re-raise after logging). Best during development or when correctness matters most.

Store cleaned records as a list of lists
After converting each field to the right type, store every cleaned row in a single, consistent structure: a list of lists. The goal is a cleaned_records variable shaped like [[sku, name, qty, price], ...], where each inner list is one record and every position always means the same thing.
As you process records, append cleaned rows in the same order every time. Keep types consistent across all rows so later steps like sorting and formatting behave predictably: sku and name as strings, qty as an integer, and price as a float.

cleaned_records = []

For each raw record, build row = [sku, name, qty, price]

cleaned_records.append(row)

Before moving on, do a quick inspection to confirm both structure and types are what you expect. Print a couple of rows and check types in each position.

print(cleaned_records[:2])

print([type(x) for x in cleaned_records[0]])

Sort records by price with sort and a key function
Once each record stores price as a number, you can sort the records in place by that field using a key function. If your records look like [sku, name, qty, price], sort ascending by price like this:

# records: list[list] -> [sku, name, qty, price]
records.sort(key=lambda r: r[3])
Python’s sort is stable, meaning if two records have the same price, their relative order stays the same as it was before sorting. If you want a deterministic tie-breaker when prices match, extend the key to include another field such as name (or SKU):

# tie-break by name, then by sku
records.sort(key=lambda r: (r[3], r[1], r[0]))
To sort by price from high to low, keep the same key and add reverse=True:

records.sort(key=lambda r: r[3], reverse=True)
If you combine descending price with tie-breakers, keep the tuple key and still use reverse=True (it reverses the overall ordering of the key values):

records.sort(key=lambda r: (r[3], r[1], r[0]), reverse=True)
Rebuild formatted output with join and f-strings
Once each record is cleaned and sorted, turn it back into report-ready text. The goal is consistency: same field order, predictable spacing, and readable alignment across every line. That is easiest when you format one line per record with an f-string, using width and alignment specifiers so columns line up even when values have different lengths.
Build each report line with numeric formatting baked in: quantity should be an integer (no decimals), and price should always show two decimals. For example:

qty as an integer: f"{qty:>4d}"

price with two decimals: f"${price:>8.2f}"

left-align text fields to fixed widths: f"{item:<16}" and f"{category:<12}"

Assemble the line by combining the pieces into a single f-string, such as:

line = f"{item:<16} {category:<12} {qty:>4d} ${price:>8.2f}"

When you have a list of formatted lines, avoid repeated string concatenation in a loop. Instead, collect all lines into a list and use "\n".join(lines) to produce one multi-line report string efficiently. That final string is what you print (or write to a file), and every row will remain aligned because the formatting rules were applied uniformly at the point of line creation.
Concrete outcome: a script that prints a cleaned, sorted sales report
Here is a complete, end-to-end script that takes a raw list of record strings, cleans each field, converts types, sorts by price, and prints a neatly formatted report.

# PyMart sales report: clean, sort, and print

raw_sales = [
    "  T-shirt  |  2  |  19.99  ",
    "Mug|1| 9.50",
    "  Notebook | 5 |3.25 ",
    "Sticker Pack| 10 | 1.99",
    "Hoodie | 1 |  39.99",
]

cleaned = []

for record in raw_sales:
    parts = record.split("|")
    if len(parts) != 3:
        continue  # skip malformed rows

    name = parts[0].strip()
    qty_str = parts[1].strip()
    price_str = parts[2].strip()

    try:
        qty = int(qty_str)
        price = float(price_str)
    except ValueError:
        continue  # skip rows with non-numeric qty/price

    cleaned.append([name, qty, price])

# Sort by price (ascending)
cleaned.sort(key=lambda row: row[2])

# Print report
print("PYMART SALES REPORT (cleaned, sorted by price)")
print("-" * 60)
print(f"{'Item':20} {'Qty':>5} {'Price':>10} {'Line Total':>12}")
print("-" * 60)

grand_total = 0.0
for name, qty, price in cleaned:
    line_total = qty * price
    grand_total += line_total
    print(f"{name:20} {qty:>5d} {price:>10.2f} {line_total:>12.2f}")

print("-" * 60)
print(f"{'Grand Total':>47} {grand_total:>12.2f}")
Expected output format (your numbers should match the data you used, but the alignment and ordering should look like this):

PYMART SALES REPORT (cleaned, sorted by price)
------------------------------------------------------------
Item                   Qty      Price   Line Total
------------------------------------------------------------
Sticker Pack            10       1.99       19.90
Notebook                 5       3.25       16.25
Mug                      1       9.50        9.50
T-shirt                  2      19.99       39.98
Hoodie                   1      39.99       39.99
------------------------------------------------------------
                                     Grand Total      125.62
Checklist for a quick self-check:

Data cleaned (split on |, strip() each field)

Types converted (int for quantity, float for price)

Sorted by price (sort(key=...))

Output formatted (aligned columns, 2-decimal prices and totals)