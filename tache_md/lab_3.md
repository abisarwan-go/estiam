Inspect the raw PyMart customer dataset and define the target output
Here is a small sample of raw PyMart customer records as messy strings. They include inconsistent casing, extra spaces, and inconsistent separators:

" ada lovelace | ADA@Example.COM | (555) 010-2000 "

"grACE hopper| grace.hopper@NAVY.mil|555.010.2001"

"ALAN turing | alan.turing @computing.org | 5550102002"

" katherine JOHNSON|k.johnson@nasa.gov| +1 555 010 2003 "

From each record, produce a standardized set of fields:

Full name: single spaces between words, trimmed, and Title Case (e.g., "Grace Hopper")

Email: trimmed, no internal spaces, and lowercase (e.g., "grace.hopper@navy.mil")

Phone: digits normalized into (555) 010-2001 format (assume US 10-digit numbers, optionally starting with country code 1)

Before coding, decide exactly what the final report should print so you can test against a clear target. For the four sample rows above, your intended output lines might look like:

Ada Lovelace | ada@example.com | (555) 010-2000

Grace Hopper | grace.hopper@navy.mil | (555) 010-2001

Alan Turing | alan.turing@computing.org | (555) 010-2002

Katherine Johnson | k.johnson@nasa.gov | (555) 010-2003

Normalize customer names by trimming whitespace and applying title case
Start by splitting each raw record into its three parts so you can target the name without disturbing the email or phone. If your records are delimited (for example, by commas or pipes), split once into name, email, and phone, then strip each piece to remove leading and trailing whitespace introduced by inconsistent entry or formatting.
Clean the name field in two passes: first normalize whitespace, then normalize casing. Use strip() to trim the ends, and consider collapsing multiple internal spaces so " aNNa mArIE " becomes "aNNa mArIE". Then apply title case so each word is capitalized in a readable way, producing "Anna Marie". Rebuild the record from the cleaned components and print an interim line after each transformation so you can verify the cleanup before moving on.

Split record into name, email, phone, then strip() each component

Clean name: trim, normalize internal spaces, then apply title case

Rebuild and print an interim formatted record for quick verification

Validate email format using string methods with an optional regex bonus
A practical email check does not need to be perfect. It needs to be strict enough to catch obvious problems while staying readable. With string methods only, start by trimming whitespace, then require exactly one @, non-empty local and domain parts, at least one dot in the domain, and no spaces. You can also reject domains that start or end with a dot, or any address that begins or ends with @.
When an email fails validation, decide how it should appear in your final report. Two common patterns are: keep the original and add an INVALID_EMAIL flag, or replace the value with a placeholder like "(invalid)" while preserving the customer row so the report stays complete. Whichever you choose, make it consistent. A report that silently drops rows or blanks fields without explanation makes debugging harder later.
As a bonus, you can offer an enhanced validation path using regex for a slightly tighter rule set. For example, a simple pattern can enforce allowed characters and basic domain structure, while still avoiding an overly complex “perfect” email regex. If you add this bonus, keep the string-method version as the default and treat regex as an optional upgrade so the core lab remains approachable.
Format phone numbers into a standard pattern using string methods and f-strings
Phone numbers often arrive with mixed spacing and punctuation. The most reliable approach is to normalize first, validate second, then format into one consistent output you can store and reuse.
Strip spaces and punctuation by extracting digits only (for example, build a new string from ch where ch.isdigit() is true).

Validate digit length before formatting. Decide what “valid” means for your dataset (commonly 10 digits for US numbers). If the digit count is wrong, store a safe placeholder (like an empty string or None) and optionally record the original value for review.

Format into a consistent pattern and store it. For 10 digits, slice and format with an f-string like f"({d[:3]}) {d[3:6]}-{d[6:]}", then save that formatted value back onto the customer record (or into a new output field).

Print a clean PyMart customer report using f-strings
Use f-strings to turn your cleaned fields (name, email, phone) into report lines that scan easily in a terminal. Set fixed column widths so entries align even when names or emails vary in length, and decide on a consistent placeholder (like "INVALID") for any field that failed validation so the output stays predictable.
Print a header first, then print one standardized line per customer. A simple pattern is: (1) print the title and column headings, (2) print a divider line, (3) loop through customers and format each line with width and alignment specifiers such as <, >, and a column width (for example, name:<22). Keep a running total of customers processed, and increment invalid counters whenever a standardized field equals your invalid placeholder.
Assemble each line with consistent column widths (for example: name, email, phone) so all rows align.

Print a header block once, then each customer entry on its own line.

Track totals plus invalid-field counts (invalid name, invalid email, invalid phone) as you print, and show the counts at the end.

Concrete outcome: a script that outputs a cleaned, standardized customer list
Run your final script from start to finish on the provided PyMart dataset with no manual edits in between. The goal is one clean pass: read each raw record, transform it, and print the standardized results in a consistent report format. If anything breaks, fix the root cause in the transformation steps rather than patching individual records.
Before you consider it done, verify every output line includes the same core fields and that each field is standardized the same way each time: the customer name is trimmed and in title case, the email passes your validation rule, and the phone number prints in your chosen standard pattern. Your lab deliverable is the final printed report. It should show every record in the dataset, in order, with clean formatting and no leftover raw artifacts like extra spaces, mixed casing, or unformatted phone strings.