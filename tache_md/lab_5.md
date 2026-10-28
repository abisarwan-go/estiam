Lab – Adding error handling to PyMart's data import routine
Start from a naive PyMart import routine that breaks on bad rows
PyMart receives each purchase as a raw text record with pipe-separated fields:

order_id|sku|quantity|unit_price

Here is a small batch with both valid and malformed rows (the kind that show up in real imports):

1001|SKU-RED-CHAIR|2|39.99

1002|SKU-BLUE-DESK|1|129.50

1003|SKU-GREEN-LAMP|3 (missing unit_price)

1004|SKU-WHITE-RUG|two|89.00 (quantity is not an integer)

1005|SKU-BLACK-SHELF|1|9.9x (unit_price is not a float)

oops-not-even-delimited (not enough fields)

`` (empty row)

A baseline import routine often assumes every row is well-formed. This version is intentionally naive. It can throw IndexError when fields are missing, and ValueError when numeric conversions fail:

def import_orders_naive(raw_lines):
    imported = []

    for line in raw_lines:
        parts = line.split("|")

        order_id = int(parts[0])
        sku = parts[1]
        quantity = int(parts[2])
        unit_price = float(parts[3])

        imported.append({
            "order_id": order_id,
            "sku": sku,
            "quantity": quantity,
            "unit_price": unit_price,
            "line_total": quantity * unit_price,
        })

    return imported


raw_lines = [
    "1001|SKU-RED-CHAIR|2|39.99",
    "1002|SKU-BLUE-DESK|1|129.50",
    "1003|SKU-GREEN-LAMP|3",           # missing unit_price
    "1004|SKU-WHITE-RUG|two|89.00",    # bad int
    "1005|SKU-BLACK-SHELF|1|9.9x",     # bad float
    "oops-not-even-delimited",         # not enough fields
    "",                                # empty
]

print(import_orders_naive(raw_lines))
Run this once and note where it fails first. With the sample batch above, the import typically crashes on the first malformed row:

1003|SKU-GREEN-LAMP|3 often triggers IndexError: list index out of range when the code hits parts[3].

If you move that row later (or test rows one at a time), you will also see:

ValueError: invalid literal for int() on quantity = int(parts[2]) when quantity is two.

ValueError: could not convert string to float when unit_price is 9.9x.

The key observation is that a single bad row stops the entire import, even when most records are perfectly usable.

Identify concrete failure points before writing any exception handling
Exception handling works best when it is anchored to specific, proven breakpoints. Before adding any try and except, walk the import code line by line and mark exactly where bad input can trigger runtime failures. The goal is not to anticipate every edge case. It is to identify the handful of predictable failure points you can validate or guard without hiding real defects.
Index-related failures usually come from assuming a row has “enough” columns. Any code that does positional access, such as row[3] for email or row[5] for total, can raise IndexError when a line is short, has trailing delimiters removed, or is otherwise malformed. The simplest way to pinpoint these is to list every positional access in your parsing step, then match each access to the minimum required column count for that record type.
Value-related failures usually come from converting strings into typed values before you have confirmed they are valid. Calls like int(row[0]), float(row[5]), date parsing, or mapping a string into an expected set can raise ValueError when fields are empty, contain non-numeric characters, include currency symbols, or use unexpected formats. Anywhere you do conversion or strict validation is a likely ValueError hotspot, especially when you are stripping whitespace, splitting composite fields, or normalizing casing.
Minimum validation rules for PyMart imports should be small, explicit, and tied to business-critical correctness:

Sales records: required fields present (enough columns), sale_id present and unique, customer_id present, product_id present, quantity is an integer greater than 0, unit_price (or total) parses as a number and is not negative, sale_date parses and is a real calendar date.

Customer records: required fields present (enough columns), customer_id present and unique, name not blank, email present and contains @ (basic check), optional numeric fields (such as loyalty points) parse if provided and are not negative.

If a rule cannot be justified as necessary to prevent a crash or protect downstream integrity, leave it out for now and add it later based on observed bad data.

Add targeted try and except blocks without masking real bugs
Target exception handling is about precision. Put the try block around the few lines that can realistically fail during a record’s parsing and conversion, not around the entire loop or entire import function. When try covers too much, you end up “handling” programming mistakes (like a misspelled variable name) as if they were bad input, which hides real bugs and makes them harder to fix.
Focus the risky section on operations like splitting fields, parsing dates, converting numbers, and mapping values. Then catch only the exceptions you expect from those operations (for example, conversion and parsing errors), and enrich the error with useful context such as the record number and the raw input line. That context is what turns a vague failure into an actionable one.
Finally, make sure the loop continues. One invalid record should be rejected and logged, then processing should move on to the next line. That way a batch import produces partial success with clear visibility, rather than failing fast and leaving you with no imported data and no reliable accounting of what went wrong.
Use else and finally to control successful execution and always log processing
When parsing each row, treat “success” as a specific state, not an assumption. Put record appends and success counters inside the else block so they only run when the try block completes without exceptions. If you append the record before parsing is fully validated, or increment “imported” in a shared path, you quietly count failures as wins and make reconciliation painful later.
Use finally for the one action that must happen every time: logging that the record was processed, regardless of outcome. This keeps your audit trail consistent even when a row fails validation, raises a parse error, or triggers an unexpected exception. Keep these logs short and structured enough to be useful: include a record identifier (row number, SKU, email), a status (IMPORTED, REJECTED, ERROR), and one compact reason when relevant. Too much detail becomes noise. Too little detail forces re-runs just to learn what happened.
Raise custom flagged validation errors while continuing the import
Validation should reject bad records without crashing the run. A clean pattern is to raise a <code>ValueError</code> for validation problems, but with a consistent tagged message that your import loop can recognize and record. For example: <code>raise ValueError("[VALIDATION] missing required field: sku")</code>. This makes validation failures explicit and machine-sortable, while still using a standard exception type.
Keep parse failures and validation failures distinct in both wording and handling. Parsing is about not being able to read a record (bad JSON, wrong delimiter, invalid date format). Validation is about a record that can be read but violates business rules (negative price, missing SKU, quantity not an integer). Use different tags such as <code>[PARSE]</code> vs <code>[VALIDATION]</code>, so your logs and rejection list can answer: did we fail to interpret the input, or did we interpret it and decide it was unacceptable?
Inside the import loop, catch and continue. On exception, append a rejection entry that includes the original record identifier (or row number) plus the reason from the exception message, then move on to the next record. The success path should add to the imported list, while the failure path adds to a <code>rejected</code> collection. If you can continue processing after a record is rejected, you should. It keeps the import productive and ensures you finish with a complete set of rejected records and their reasons.
Produce a summary report of imported versus rejected records
A reliable import is not finished until it can tell you, clearly and consistently, what happened. Track two primary totals. How many records produced valid imported objects, and how many were rejected. Then capture why rejections happened in a way that can be reviewed, filtered, and reprocessed without rereading logs.
Return two outputs from the routine: (1) the list of imported objects ready for persistence or downstream steps, and (2) a structured rejection list. Each rejection should include at minimum a stable record identifier (row number, source id, or filename plus line), a short error code or category, and a human-readable message. When operators ask “what should I fix first?”, you can compute top rejection reasons by counting these error codes, rather than scraping freeform text.
End the run by emitting a final summary that is stable and readable. Keep the same ordering and labels every time so it is easy to scan and compare across runs. A compact format works well: totals first, then the top reasons with counts, followed by where to find the full rejection list if it is written to a file or passed onward.

[An image about a concise report card showing imported count, rejected count, and example rejection reasons]

Concrete outcome: a robust import routine that never crashes and reports clearly
A hardened import routine does three things reliably on mixed-quality input: it processes every record without a full-run crash, it distinguishes between validation problems and unexpected bugs, and it returns a summary that makes the next action obvious. The function below assumes you already have a flagged validation error (for reject-and-continue) and a per-row validator from earlier sections.
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Tuple, Any, Optional

class ValidationError(Exception):
    """A flagged, expected data problem. Safe to reject a record and continue."""

@dataclass
class ImportSummary:
    total: int = 0
    imported: int = 0
    rejected: int = 0
    failed: int = 0  # unexpected errors
    warnings: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)


def import_products(
    rows: Iterable[Dict[str, Any]],
    validate_row: Callable[[Dict[str, Any]], Dict[str, Any]],
    save_product: Callable[[Dict[str, Any]], str],
    logger,
) -> ImportSummary:
    """Import products from dict rows.

    Expected behavior:
    - Never crashes the whole run because of bad data.
    - Rejects rows with ValidationError and continues.
    - Surfaces unexpected exceptions as actionable 'failed' entries and continues.
    - Always logs completion and returns totals.
    """

    summary = ImportSummary()

    logger.info("import.start")
    try:
        for index, raw in enumerate(rows, start=1):
            summary.total += 1

            try:
                product = validate_row(raw)  # may raise ValidationError
                product_id = save_product(product)  # may raise unexpected exceptions

            except ValidationError as e:
                summary.rejected += 1
                summary.errors.append({
                    "row": index,
                    "kind": "rejected",
                    "message": str(e),
                    "hint": "Fix the row values and re-run import.",
                    "row_data": raw,
                })
                logger.warning("import.row.rejected", extra={"row": index, "error": str(e)})

            except Exception as e:
                # Unexpected bug or infrastructure issue. Capture, report, and continue.
                summary.failed += 1
                summary.errors.append({
                    "row": index,
                    "kind": "failed",
                    "message": f"Unexpected error: {type(e).__name__}: {e}",
                    "hint": "Check logs/traceback and fix code or dependency. Row was skipped.",
                    "row_data": raw,
                })
                logger.exception("import.row.failed", extra={"row": index})

            else:
                summary.imported += 1
                logger.info("import.row.imported", extra={"row": index, "product_id": product_id})

    finally:
        logger.info(
            "import.complete",
            extra={
                "total": summary.total,
                "imported": summary.imported,
                "rejected": summary.rejected,
                "failed": summary.failed,
                "warnings": summary.warnings,
            },
        )

    return summary
On a mixed-quality file, the routine completes the loop every time and returns an ImportSummary where total = imported + rejected + failed. Rejections produce targeted messages you can hand back to a data owner (what field is wrong and what to do next). Failures capture truly unexpected exceptions, log a traceback for engineers, and still allow the remaining rows to be processed so one bad record does not erase the whole run.
A quick verification checklist for the expected outcome:

The function returns even when some rows are malformed or incomplete.

The summary reports totals and outcome counts that add up.

Error entries are actionable: they include a row number, a clear category (rejected vs failed), and a hint that matches the category.

Logs show a single import.complete event even when exceptions occur mid-stream.

The error-handling patterns worth reusing across other PyMart routines are consistent layering and consistent reporting: catch ValidationError closest to where it occurs to reject-and-continue, let else mark the success path cleanly, use a broad except Exception only to prevent a full-run crash while preserving diagnostics via logger.exception, and use finally to guarantee end-of-run logging and totals.