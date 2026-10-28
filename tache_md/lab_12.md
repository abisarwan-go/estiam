Timestamp report filenames with datetime.now and write via os path utilities
A reliable report filename is predictable for humans and sortable for machines. Start by capturing the current local time and formatting it to match report_YYYY-MM-DD_HHMMSS.txt, then build the destination path with os.path.join so your script stays portable across operating systems.
from datetime import datetime
import os

# 1) Build a timestamped filename.
#    report_YYYY-MM-DD_HHMMSS.txt (example: report_2026-07-30_091522.txt)
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H%M%S")
filename = f"report_{timestamp}.txt"

# 2) Assemble a safe output path.
#    Keep the base name simple (letters, numbers, underscore, dash, dot).
output_dir = os.path.join(os.getcwd(), "reports")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, filename)

# 3) Write a minimal report body and confirm where it was saved.
report_body = (
    f"PyMart Report\n"
    f"Generated at: {now.isoformat(timespec='seconds')}\n"
)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(report_body)

print("Created:", filename)
print("Saved to:", output_path)
If you rerun the script, do you want a new file every time (timestamps) or should the latest report overwrite a stable name like report_latest.txt?

Compute the next review date using timedelta for a 30-day schedule
A reliable review schedule starts with a single reference point. Capture today as a date when you only care about the calendar day, or as a datetime when the time of day matters. Pick one and stay consistent so the schedule does not drift between runs.
Compute the next date by adding a fixed offset with timedelta(days=30). This keeps the logic explicit and repeatable: next_review = today + timedelta(days=30). If you captured a datetime, the result preserves the time-of-day. If you captured a date, the result stays a calendar date.
For traceability, persist the computed next_review next to the report output. A simple approach is to write a small metadata text or JSON file in the same output folder (or append a footer line to the report) that records both generated_on and next_review. When someone audits the report later, they can see exactly when it was produced and when it is due for review again.

[An image about a small timeline showing today and the next review date 30 days later]

Simulate and measure report generation time with time.time and time.sleep
A simple way to measure how long a report takes to generate is to record a start timestamp, run the work, then record an end timestamp. With time.time(), both timestamps are floating-point seconds since the epoch. Subtracting them gives an elapsed duration in seconds that you can print and also store as part of your report’s metadata.
When you are still building the report logic, time.sleep() can stand in for a slow step such as database fetches, complex calculations, or writing large files. Measure the simulated step the same way you would the real work so your logging and metadata structure are ready when you swap in the real implementation.

Record start = time.time() before generation and end = time.time() after to compute elapsed = end - start

Use time.sleep(...) to simulate a long-running generation step

Print the measured duration and include it in the report metadata output (for example, metadata["generation_seconds"] = elapsed)

Use calendar to confirm leap year status and print the current month schedule
The calendar module gives you reliable, built-in utilities for date rules that often show up in planning conversations. Start by checking whether the current year is a leap year: get the year from datetime.now().year, then call calendar.isleap(year). A common misconception is that “every year divisible by 4 is a leap year.” Century years break that rule unless they are divisible by 400, and calendar.isleap handles that correctly for you.
To print a simple month schedule for the current month, pull year and month from datetime.now(), then use calendar.month(year, month) to produce a ready-to-print text calendar. This console-style output is useful when a team needs to quickly talk through deadlines, review meetings, and the spacing of report runs without opening another tool or building a UI.
Connect both outputs back to operations: leap-year status can affect late-February reporting and end-of-month cutoffs, and the printed month calendar helps anchor recurring report planning and review cycles in a shared visual reference. If a review cycle lands near February, does an extra day shift any promised delivery or meeting cadence for PyMart’s stakeholders?
Concrete outcome: an automated, timestamped, and scheduled PyMart reporting script
The goal is a single runnable script that ties everything together: timestamped filenames, a 30-day next review date, timing metrics, and calendar checks. One run should both save a report file to disk and print clear scheduling output to the screen, so you can verify behavior without extra steps.
import os
from datetime import datetime, timedelta
import time
import calendar

def generate_pymart_report(output_dir="reports"):
    # Ensure output folder exists
    os.makedirs(output_dir, exist_ok=True)

    # Timestamped filename
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"pymart_report_{timestamp}.txt"
    path = os.path.join(output_dir, filename)

    # Timing metrics
    start = time.time()
    # Simulate report generation work
    time.sleep(2)

    # Next review date (30-day schedule)
    next_review = now + timedelta(days=30)

    # Calendar checks and monthly schedule
    year = now.year
    month = now.month
    is_leap = calendar.isleap(year)
    month_calendar = calendar.month(year, month)

    # Write report
    lines = [
        "PyMart Report",
        "============",
        f"Generated at: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Next review date: {next_review.strftime('%Y-%m-%d')}",
        f"Leap year: {is_leap}",
        "",
        "Current month schedule:",
        month_calendar,
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    end = time.time()
    duration = end - start

    # On-screen scheduling output
    print("Report run complete.")
    print(f"Saved report file: {path}")
    print(f"Duration (seconds): {duration:.3f}")
    print(f"Next review date: {next_review.strftime('%Y-%m-%d')}")
    print(f"Leap year ({year}): {is_leap}")
    print("Current month schedule:")
    print(month_calendar)

    return path, duration, next_review

if __name__ == "__main__":
    generate_pymart_report()
When this executes end-to-end, you should see: (1) a new reports/ file whose name includes a timestamp, (2) printed duration in seconds based on the simulated work, (3) a next review date exactly 30 days after the run, and (4) leap-year status plus the formatted current month calendar. If any one of those outputs is missing, the lab requirements are not yet fully met.