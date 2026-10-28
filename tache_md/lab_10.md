Create a large simulated PyMart sales dataset you will stream through
To practice streaming, you need data big enough to matter, but simple enough to understand at a glance. Use an in-memory dataset represented as CSV-like text lines (a header plus many rows). Each row should intentionally include issues you would normally see in real exports so your generator can clean as it yields.

Assume the raw columns arrive in this order: order_id, timestamp, store_id, cashier_id, sku, qty, unit_price, discount, total, payment_method, customer_id, notes

Build your simulated lines so they include these common messy data problems you will clean during streaming:

Leading or trailing whitespace around fields and separators

Currency symbols and thousands separators in money fields (e.g., $1,299.00, USD 9.99)

Missing fields (empty strings), including optional fields like notes and sometimes customer_id

Inconsistent numeric types (qty as "2", "2.0", or even "two")

Discount represented inconsistently (10%, 0.10, $1.00, or blank)

Payment method casing and spelling variations ("credit", "Credit Card", "CARD")

A small sample of raw lines might look like:

1000042, 2026-06-14 09:03:12 , S-007 , C-19, SKU-00421 , 2 , $19.99 , 10% , $35.98 , Credit Card , , " first-time buyer "

1000043,2026-06-14T09:04:01Z,S-007,C-19,SKU-00017,1,USD 1,299.00,,1299.00,CARD,CUST-8812,

1000044, 2026/06/14 09:04:41, S-012, C-03, SKU-01000, two, $3.50, $0.00, $3.50, cash , CUST-1044, ""

Before writing any generators, confirm the exact cleaned schema you want to produce. A practical target is a normalized dictionary (or named tuple) with consistent types:

order_id (int)

timestamp (ISO 8601 string, normalized)

store_id (string, trimmed)

cashier_id (string, trimmed)

sku (string, trimmed)

qty (int, default 0 if missing or invalid)

unit_price (float)

discount_rate (float from 0.0 to 1.0)

total (float)

payment_method (string, normalized to a small set like card, cash, mobile, other)

customer_id (string or None)

notes (string or None)

A single cleaned record should look like:

{"order_id": 1000042, "timestamp": "2026-06-14T09:03:12", "store_id": "S-007", "cashier_id": "C-19", "sku": "SKU-00421", "qty": 2, "unit_price": 19.99, "discount_rate": 0.10, "total": 35.98, "payment_method": "card", "customer_id": null, "notes": "first-time buyer"}

Write read_sales_records to yield one cleaned record at a time
Implement read_sales_records(data) as a generator so it parses, cleans, and yields one record at a time. Expect each input line to be messy, so treat parsing and cleaning as part of the streaming step. The goal is to return a consistent Python shape (often a dict) per record, without ever building an in-memory list of all records.
A practical pattern is: iterate lines, split into fields, normalize strings, convert types, then yield a cleaned record. Apply the same rules every time so downstream code can rely on the schema.

Type conversions: convert numeric text to int/float where appropriate. When conversion fails, fall back to a safe default (for example, 0 for quantity, 0.0 for amount).

Normalization: trim whitespace, standardize casing (for example, "Online" and "online" both become "online"), and normalize empty markers (for example, "", "N/A", "null") to None.

Safe defaults: if a field is missing, too short, or unparseable, set a predictable value rather than throwing, unless the field is truly required for your pipeline.

A minimal implementation might yield records like {"order_id": 12345, "customer_id": "C0192", "sku": "SKU-1007", "quantity": 2, "amount": 19.98, "channel": "online"}.

Validate the generator behavior by pulling only the first few records, which is the key advantage of streaming. If records = read_sales_records(data), then next(records) should immediately return the first cleaned record without processing the entire dataset. You can also sanity-check a small sample:

Call next(records) a couple of times to inspect individual cleaned outputs

Run a short loop such as for i, rec in enumerate(records): ... and break after 3 to 5 records to confirm conversions and defaults are applied consistently

Filter high-value sales with a generator expression
Start by choosing a numeric threshold that represents “high-value” for PyMart, then layer a generator expression on top of the stream returned by read_sales_records(). Because read_sales_records() yields one already-cleaned record at a time, your filter should check the cleaned numeric field (for example, total) and keep only records at or above the threshold.
A generator expression keeps the pipeline streaming: it produces matching records on demand, rather than building a full list in memory. Consume it with a bounded approach so you do not accidentally iterate and print an unending stream. For example:

threshold = 200.0

high_value_sales = (r for r in read_sales_records(path) if r["total"] >= threshold)

Inspect only a few: for i, r in enumerate(high_value_sales): ...; if i == 4: break

When you inspect a handful of filtered records, verify two things at once: the totals are truly above the threshold, and the values look cleaned (correct types, trimmed strings, normalized currencies) before filtering happened. If you see surprises like string totals ("250") or unstripped currency symbols, fix the cleaning in read_sales_records() first. Filtering should rely on cleaned data, not perform cleanup itself.
Use a closure to build a configurable threshold filter
A clean way to make your streaming pipeline configurable is to build a filter factory: a function that returns another function. Implement make_threshold_filter(min_amount) so it returns a keep(record) function that checks whether a record meets your minimum sale threshold. The inner function “remembers” min_amount even after make_threshold_filter has finished, so your configuration travels with the filter instead of living in global variables.
from typing import Callable, Dict, Any

Record = Dict[str, Any]

def make_threshold_filter(min_amount: float) -> Callable[[Record], bool]:
    def keep(record: Record) -> bool:
        return record["amount"] >= min_amount
    return keep
Use the returned function in your generator pipeline so different thresholds are just different filters. Because the threshold is captured by the closure, you can build multiple independent filters with no shared state.

high_value = make_threshold_filter(500.0)
mid_value  = make_threshold_filter(200.0)

# read_sales_records(...) yields cleaned records one at a time
high_stream = (r for r in read_sales_records("sales.csv") if high_value(r))
mid_stream  = (r for r in read_sales_records("sales.csv") if mid_value(r))

# consume lazily
first_three = [next(high_stream) for _ in range(3)]
[An image about a control knob setting a threshold that changes what the pipeline outputs]

Compare memory and runtime behavior against building full lists
Lazy iteration streams one record at a time, while eager list creation builds the entire result up front. The biggest practical difference is peak memory. A streaming pipeline tends to keep memory roughly proportional to the size of a single record plus small iterator overhead, whereas materializing into a list grows memory proportional to the number of records times record size. If PyMart data is large, that peak memory is usually the first bottleneck, long before CPU becomes the limiting factor.
What changes when you wrap a stream depends on the consumer:

list(stream) forces full realization. You pay the full memory bill and you often delay getting the first result until everything has been produced.

sum(stream) typically stays streaming. It pulls items one by one, keeping only a running total, but it does consume the entire stream.

any(stream) can short-circuit. It stops at the first truthy item, which can make it dramatically faster than materializing if an early match is likely.

for x in stream: is streaming by default. Work happens incrementally inside the loop, and you can break early to avoid reading the rest.

Practical guidelines:

Stream when the dataset can be large or unbounded, when you want early results, or when you may exit early (for example, finding the first suspicious transaction).

Materialize when you truly need random access, multiple passes over the same data, sorting/grouping that requires holding everything, or you must share a stable snapshot across steps.

When in doubt, keep it lazy until a step proves it must be eager. The moment you call list(...), you have chosen peak memory equal to the full output size, not just the next record.

Concrete outcome: a memory-efficient streaming pipeline for PyMart sales data
You now have a composable streaming pipeline: dataset → read_sales_records → threshold filter function → filtered generator. Each stage processes one record at a time, so you can scan large sales data without building intermediate lists in memory.
A compact end-to-end version looks like this:

# dataset: an iterable of raw rows (simulated or from a file)
clean_records = read_sales_records(dataset)

# closure-built predicate. for example, keep sales >= $500
is_high_value = make_threshold_filter(min_total=500)

# filtered generator. no extra list allocated
high_value_sales = (r for r in clean_records if is_high_value(r))

# consume incrementally
for sale in high_value_sales:
    print(sale["sale_id"], sale["total"], sale["timestamp"])
Notice what is missing: there is no “collect-all” step. Each sale is produced, filtered, and consumed immediately, which is what keeps memory flat as data grows.

To extend this to real files, swap dataset for a file iterator (for example, lines from a CSV) and keep the same downstream stages. To grow the transformation chain, add more generator-based steps (cleaning, enrichment, grouping into batches) that each accept an iterable and yield records onward. The key design question to keep asking is: “Does this step yield results as it goes, or does it accumulate everything first?”

[An image about the final end-to-end pipeline with labeled stages producing a small output stream]