"""Organize PyMart report files on disk (lab 11)."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def write_daily_report(
    reports_root: Path,
    *,
    year: int,
    report_date: str,
    store: str,
    total_sales: float,
    notes: str = "Auto-generated",
) -> Path:
    folder = reports_root / str(year)
    ensure_dir(folder)
    path = folder / f"pymart_report_{report_date}.txt"
    contents = (
        "PyMart Daily Report\n"
        f"Date: {report_date}\n"
        f"Store: {store}\n"
        f"Total Sales: {total_sales:.2f}\n"
        f"Notes: {notes}\n"
    )
    write_text(path, contents)
    return path


def list_tree(base: Path) -> None:
    """Traverse with os.walk and print a deterministic inventory."""
    all_paths: list[tuple[str, str]] = []
    for root, dirs, files in os.walk(base):
        dirs.sort()
        files.sort()
        root_path = Path(root)
        for directory in dirs:
            rel = (root_path / directory).relative_to(base)
            all_paths.append(("DIR", rel.as_posix()))
        for name in files:
            rel = (root_path / name).relative_to(base)
            all_paths.append(("FILE", rel.as_posix()))

    print("Tree inventory:")
    for kind, rel in sorted(all_paths, key=lambda item: (item[0], item[1])):
        print(f"{kind:4} {rel}")


def unique_dest(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    index = 1
    while True:
        candidate = dest.with_name(f"{stem} ({index}){suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def move_or_copy_by_rule(
    src: Path, base: Path, *, dry_run: bool = True
) -> None:
    """Apply FINAL/DRAFT filename rules with optional dry-run."""
    name = src.name
    if "_FINAL" in name:
        action = "copy"
        dest_dir = base / "archive"
    elif "_DRAFT" in name:
        action = "move"
        dest_dir = base / "needs_review"
    else:
        return

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = unique_dest(dest_dir / src.name)
    if dry_run:
        print(f"DRY-RUN: would {action} {src} -> {dest}")
        return

    if action == "copy":
        shutil.copy2(src, dest)
    else:
        shutil.move(str(src), str(dest))


def inventory_reports(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.txt") if path.is_file())


def safe_remove_empty_dirs(root: Path) -> None:
    """Bottom-up removal of empty directories under root."""
    root_resolved = root.resolve()
    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if not path.is_dir():
            continue
        if not str(path.resolve()).startswith(str(root_resolved)):
            continue
        try:
            path.rmdir()
        except OSError:
            pass


def organize_year_reports(reports_root: Path) -> None:
    """
    Rule:
    - inventory_*.txt moved into reports/archive/inventory/<year>/
    - sales_*.txt copied into reports/archive/sales/<year>/
    """
    for src in inventory_reports(reports_root):
        if "archive" in src.parts or "needs_review" in src.parts:
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


def main() -> None:
    base = Path.cwd() / "pymart_workspace"
    reports_root = base / "reports"

    # 1) Setup (idempotent)
    ensure_dir(reports_root)
    ensure_dir(reports_root / "2024")
    ensure_dir(reports_root / "2025")
    ensure_dir(reports_root / "archive")
    assert reports_root.is_dir()
    assert (reports_root / "2024").is_dir()

    # 2) Write sample inputs
    write_text(
        reports_root / "2024" / "inventory_2024-01.txt",
        "PyMart inventory report. 2024-01\n",
    )
    write_text(
        reports_root / "2024" / "sales_2024-01.txt",
        "PyMart sales report. 2024-01\n",
    )
    write_text(
        reports_root / "2025" / "inventory_2025-02.txt",
        "PyMart inventory report. 2025-02\n",
    )
    write_text(
        reports_root / "2025" / "sales_2025-02.txt",
        "PyMart sales report. 2025-02\n",
    )
    daily = write_daily_report(
        reports_root,
        year=2024,
        report_date="2024-03-15",
        store="Downtown",
        total_sales=15420.55,
    )
    print("Wrote daily report:", daily.resolve())
    assert daily.exists() and daily.is_file()

    # Demo FINAL/DRAFT rules once (skip if already organized)
    draft = reports_root / "2025" / "returns_DRAFT.txt"
    final = reports_root / "2025" / "returns_FINAL.txt"
    draft_done = (reports_root / "needs_review" / "returns_DRAFT.txt").exists()
    final_done = (reports_root / "archive" / "returns_FINAL.txt").exists()
    if not draft_done and not draft.exists():
        write_text(draft, "Draft returns summary\n")
    if not final_done and not final.exists():
        write_text(final, "Final returns summary\n")
    if draft.exists():
        move_or_copy_by_rule(draft, reports_root, dry_run=True)
        move_or_copy_by_rule(draft, reports_root, dry_run=False)
    if final.exists():
        move_or_copy_by_rule(final, reports_root, dry_run=True)
        move_or_copy_by_rule(final, reports_root, dry_run=False)

    print()
    list_tree(reports_root)
    print()

    # 3) Organize inventory/sales into archive
    organize_year_reports(reports_root)

    # 4) Cleanup empty year folders when possible
    safe_remove_empty_dirs(reports_root)

    # 5) Verification
    final_files = inventory_reports(reports_root)
    print("Final report inventory:")
    for path in final_files:
        print("-", path.relative_to(base))


if __name__ == "__main__":
    main()
