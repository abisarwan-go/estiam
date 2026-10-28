Lab – Automating PyMart's report file organization
PyMart generates lots of plain-text reports. As the months roll on, those files tend to pile up in the same place, get named inconsistently, and become hard to find when someone needs “the 2024 returns summary” or “last year’s inventory snapshot.” This lab builds a practical, file-system focused Python workflow that puts order back into that chaos.
You will work toward a single script that creates a predictable folder structure, generates report files into the right year, scans what already exists, and then applies simple rules to move, copy, and clean up reports. If you can point the script at a directory on disk, you should be able to re-run it safely and end up with organized reports every time.
Before you start, ask yourself: what does “organized” mean for your team. Is it by year only, by year and department, or by year and month. What should happen when a report is duplicated, incorrectly placed, or missing. Those choices will guide the rules you implement as you move through the lab.
Set up the PyMart reports workspace and folder structure
Create a stable workspace under reports/ so every report has a predictable destination. A simple pattern is to keep one folder per year (for example, reports/2024/, reports/2025/). When your automation always writes into one of these year folders, you avoid scattered files and make later tasks like listing, moving, and cleanup straightforward.
Use a setup step that is safe to re-run. Create folders if they do not exist, and do nothing if they already do. Then verify the expected tree is present before you write any report files.

Create reports/ and any required year subfolders using os.makedirs(path, exist_ok=True)

Keep the setup idempotent (re-running it should not overwrite or delete files)

Confirm expected paths exist (for example, check os.path.isdir("reports") and os.path.isdir(f"reports/{year}")) and stop early if something is missing

Generate text report files in the correct year folder
A report file should be predictable to generate and easy to locate later. Keep the format minimal and the filename self-describing. A practical convention is:

Folder: reports/<YEAR>/

Filename: pymart_report_<YYYY-MM-DD>.txt

Contents: a short header plus a few key-value lines (date, store, total, notes)

This gives you stable paths for automation and avoids vague names like report_final.txt.

Create the year folder path, then write the report using a context manager so the file is always closed properly:

from pathlib import Path

year = 2024
report_date = "2024-03-15"

folder = Path("reports") / str(year)
folder.mkdir(parents=True, exist_ok=True)

filename = f"pymart_report_{report_date}.txt"
path = folder / filename

contents = (
    "PyMart Daily Report\n"
    f"Date: {report_date}\n"
    "Store: Downtown\n"
    "Total Sales: 15420.55\n"
    "Notes: Auto-generated\n"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(contents)
After writing, confirm it landed where you expect and that it is readable:

print("Wrote:", path.resolve())
assert path.exists() and path.is_file()
print(path.read_text(encoding="utf-8"))
If either assertion fails or the printed text looks wrong, check that year matches the folder you intended and that you are using the same path for both writing and reading.

Traverse the reports tree and list every report with os.walk
To inventory what your script created, walk the reports/ directory recursively and collect every path you find. os.walk yields each folder (root), its subfolders (dirs), and its files (files). For deterministic, audit-friendly logs, sort dirs and files as you go, and log paths relative to reports/ so output is stable across machines.

from pathlib import Path
import os

BASE = Path("reports")

all_paths = []

for root, dirs, files in os.walk(BASE):
    dirs.sort()
    files.sort()

    root_path = Path(root)

    # Log folders
    for d in dirs:
        p = (root_path / d).relative_to(BASE)
        all_paths.append(("DIR", p.as_posix()))

    # Log files
    for f in files:
        p = (root_path / f).relative_to(BASE)
        all_paths.append(("FILE", p.as_posix()))

# Deterministic listing
for kind, rel in sorted(all_paths, key=lambda x: (x[0], x[1])):
    print(f"{kind:4} {rel}")
When you only care about certain report types, filter by extension while still keeping the folder traversal. A common mistake is to assume os.walk only returns files. It returns both, so apply your filter to files and keep dirs intact so recursion continues.

wanted_exts = {".txt", ".csv"}

for root, dirs, files in os.walk(BASE):
    dirs.sort()
    for name in sorted(files):
        p = Path(root) / name
        if p.suffix.lower() in wanted_exts:
            print(p.relative_to(BASE).as_posix())
Move or copy reports between folders based on a rule
Start with a rule that is unambiguous and easy to test. For example: if a report filename contains _FINAL, copy it into an archive/ folder (keep the original). Otherwise, if it contains _DRAFT, move it into a needs_review/ folder (remove it from its current location). The important part is that the condition only depends on information you can reliably read, such as the filename, extension, or modification time.
Use shutil.copy and shutil.move with explicit, full destination paths, not “current directory” assumptions. Add a dry-run switch so you can confirm what would happen before you alter anything, and guard against name collisions by generating a unique destination name:

from pathlib import Path
import shutil

def unique_dest(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    i = 1
    while True:
        candidate = dest.with_name(f"{stem} ({i}){suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def move_or_copy_by_rule(src: Path, base: Path, dry_run: bool = True) -> None:
    # Concrete triggers (edit to match your naming conventions)
    name = src.name
    if "_FINAL" in name:
        action = "copy"
        dest_dir = base / "archive"
    elif "_DRAFT" in name:
        action = "move"
        dest_dir = base / "needs_review"
    else:
        return  # no rule matched

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = unique_dest(dest_dir / src.name)

    if dry_run:
        print(f"DRY-RUN: would {action} {src} -> {dest}")
        return

    # Explicit destinations. copy2 preserves metadata.
    if action == "copy":
        shutil.copy2(src, dest)
    else:
        shutil.move(str(src), str(dest))


# Example usage (call this for each report you discovered earlier)
# move_or_copy_by_rule(Path("reports/2025/sales_FINAL.txt"), Path("reports"), dry_run=True)
Dry-run output should match your expectations before you flip dry_run=False. Ask yourself: are you copying only what should be preserved, and moving only what should leave the source folder? If you see frequent collisions, that is a signal your naming convention or rule is too broad. When it is correct, remove the dry-run and run the script once, then re-run it to confirm it is idempotent (a second pass should do little or nothing).
Clean up files and remove empty directories safely
Deleting and removing directories is where automation can do the most damage. Treat cleanup as a rules-driven step: decide what qualifies as “old” (by filename pattern or age), delete only those files, then remove a year folder only after it is confirmed empty and still under reports/.
Delete old report files with os.remove() by checking each candidate path against your rule (for example: only files ending in .txt that match a known naming convention, or files older than N days based on os.path.getmtime). Before calling os.remove, add guardrails: resolve the absolute path and verify it starts with the absolute path of reports/. If it does not, skip it. This protects you from unexpected traversal results, mistaken relative paths, or a misconfigured base directory.
After file cleanup, remove empty year folders using os.rmdir() only when they are truly empty. A safe approach is to inspect the directory contents with os.listdir(year_dir) and proceed only if it returns an empty list. If you expect nested subfolders, re-check from the deepest level upward so you do not attempt to remove a parent that still contains children. Keep directory removal just as constrained as file deletion: confirm the target directory is inside reports/ and looks like a year folder you created (for example, a four-digit name) before calling os.rmdir.
Concrete outcome: a single script that organizes PyMart reports on disk
Run one script to create a small PyMart reports workspace, write a few sample reports into year folders, traverse the tree, move or copy files based on a simple rule, and then clean up empty directories. The script below is intentionally linear. You can run it repeatedly and it will converge on the same organized state.
from __future__ import annotations

import shutil
from pathlib import Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def safe_remove_empty_dirs(root: Path) -> None:
    # Bottom-up removal of empty directories under root
    for p in sorted(root.rglob("*"), key=lambda x: len(x.parts), reverse=True):
        if p.is_dir():
            try:
                p.rmdir()
            except OSError:
                pass


def inventory_reports(root: Path) -> list[Path]:
    return sorted([p for p in root.rglob("*.txt") if p.is_file()])


def main() -> None:
    base = Path.cwd() / "pymart_workspace"
    reports_root = base / "reports"

    # 1) Setup
    ensure_dir(reports_root)
    ensure_dir(reports_root / "archive")

    # 2) Write sample inputs (idempotent. overwrites same files)
    write_text(reports_root / "2024" / "inventory_2024-01.txt", "PyMart inventory report. 2024-01\n")
    write_text(reports_root / "2024" / "sales_2024-01.txt", "PyMart sales report. 2024-01\n")
    write_text(reports_root / "2025" / "inventory_2025-02.txt", "PyMart inventory report. 2025-02\n")
    write_text(reports_root / "2025" / "sales_2025-02.txt", "PyMart sales report. 2025-02\n")

    # 3) Walk and organize
    # Rule used here:
    # - inventory_*.txt files are moved into reports/archive/inventory/<year>/
    # - sales_*.txt files are copied into reports/archive/sales/<year>/
    for src in inventory_reports(reports_root):
        # Skip anything already in archive
        if "archive" in src.parts:
            continue

        year = src.parent.name
        if src.name.startswith("inventory_"):
            dest = reports_root / "archive" / "inventory" / year / src.name
            ensure_dir(dest.parent)
            shutil.move(str(src), str(dest))
        elif src.name.startswith("sales_"):
            dest = reports_root / "archive" / "sales" / year / src.name
            ensure_dir(dest.parent)
            shutil.copy2(str(src), str(dest))

    # 4) Cleanup
    safe_remove_empty_dirs(reports_root)

    # 5) Quick verification. print final inventory
    final_files = inventory_reports(reports_root)
    print("Final report inventory:")
    for p in final_files:
        print("-", p.relative_to(base))


if __name__ == "__main__":
    main()
Expected final directory state after running:

pymart_workspace/reports/archive/inventory/2024/inventory_2024-01.txt (moved)

pymart_workspace/reports/archive/inventory/2025/inventory_2025-02.txt (moved)

pymart_workspace/reports/archive/sales/2024/sales_2024-01.txt (copied)

pymart_workspace/reports/archive/sales/2025/sales_2025-02.txt (copied)

The verification step prints the final inventory so you can confirm both the archive structure and which files remain outside it.