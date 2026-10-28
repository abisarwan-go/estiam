"""Print a cleaned, standardized PyMart customer report (lab 3)."""

import _bootstrap  # noqa: F401

from pymart.customers import INVALID, normalize_record

RAW_CUSTOMERS = [
    " ada lovelace | ADA@Example.COM | (555) 010-2000 ",
    "grACE hopper| grace.hopper@NAVY.mil|555.010.2001",
    "ALAN turing | alan.turing @computing.org | 5550102002",
    " katherine JOHNSON|k.johnson@nasa.gov| +1 555 010 2003 ",
]


def print_report(raw_records: list[str]) -> None:
    print("PyMart Customer Report")
    print(f"{'Name':<22} {'Email':<32} {'Phone':<16}")
    print("-" * 72)

    total = 0
    invalid_name = 0
    invalid_email = 0
    invalid_phone = 0

    for raw in raw_records:
        customer = normalize_record(raw)
        total += 1

        if customer["name"] == INVALID:
            invalid_name += 1
        if customer["email"] == INVALID:
            invalid_email += 1
        if customer["phone"] == INVALID:
            invalid_phone += 1

        print(
            f"{customer['name']:<22} "
            f"{customer['email']:<32} "
            f"{customer['phone']:<16}"
        )

    print("-" * 72)
    print(f"Customers processed: {total}")
    print(
        f"Invalid fields — name: {invalid_name}, "
        f"email: {invalid_email}, phone: {invalid_phone}"
    )


def main() -> None:
    print_report(RAW_CUSTOMERS)


if __name__ == "__main__":
    main()
