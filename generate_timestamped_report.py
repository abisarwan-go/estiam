"""Generate a timestamped PyMart report with scheduling metadata (lab 12)."""

from __future__ import annotations

import calendar
import json
import os
import time
from datetime import datetime, timedelta


def generate_pymart_report(output_dir: str = "reports") -> tuple[str, float, datetime]:
    # Ensure output folder exists
    os.makedirs(output_dir, exist_ok=True)

    # Timestamped filename
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H%M%S")
    filename = f"report_{timestamp}.txt"
    path = os.path.join(output_dir, filename)

    # Timing metrics (sleep simulates slow report work)
    start = time.time()
    time.sleep(0.5)

    # Next review date (30-day schedule)
    next_review = now + timedelta(days=30)

    # Calendar checks and monthly schedule
    year = now.year
    month = now.month
    is_leap = calendar.isleap(year)
    month_calendar = calendar.month(year, month)

    end = time.time()
    duration = end - start

    # Write report body + scheduling metadata
    lines = [
        "PyMart Report",
        "============",
        f"Generated at: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Generated at (ISO): {now.isoformat(timespec='seconds')}",
        f"Next review date: {next_review.strftime('%Y-%m-%d')}",
        f"Leap year: {is_leap}",
        f"Generation seconds: {duration:.3f}",
        "",
        "Current month schedule:",
        month_calendar.rstrip("\n"),
        "",
    ]

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    # Persist metadata beside the report for audits
    metadata = {
        "generated_on": now.isoformat(timespec="seconds"),
        "next_review": next_review.strftime("%Y-%m-%d"),
        "generation_seconds": round(duration, 3),
        "leap_year": is_leap,
        "report_file": filename,
    }
    meta_path = os.path.join(output_dir, f"report_{timestamp}.meta.json")
    with open(meta_path, "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    # Also refresh a stable latest pointer
    latest_path = os.path.join(output_dir, "report_latest.txt")
    with open(latest_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    # On-screen scheduling output
    print("Report run complete.")
    print(f"Saved report file: {path}")
    print(f"Saved metadata: {meta_path}")
    print(f"Updated latest: {latest_path}")
    print(f"Duration (seconds): {duration:.3f}")
    print(f"Next review date: {next_review.strftime('%Y-%m-%d')}")
    print(f"Leap year ({year}): {is_leap}")
    print("Current month schedule:")
    print(month_calendar)

    return path, duration, next_review


if __name__ == "__main__":
    generate_pymart_report()
