"""Demo: stream, filter, and compare lazy vs eager sales processing (lab 10)."""

from __future__ import annotations

import _bootstrap  # noqa: F401

import sys
import tracemalloc

from pymart.streaming import (
    build_sales_dataset,
    make_threshold_filter,
    read_sales_records,
)


def main() -> None:
    dataset = build_sales_dataset(size=500)
    print(f"Raw lines (incl. header): {len(dataset)}")

    # Pull only the first cleaned records — proves streaming starts immediately.
    stream = read_sales_records(dataset)
    first = next(stream)
    second = next(stream)
    print("First cleaned record:", first)
    print("Second cleaned record:", second)

    print("\nNext 3 cleaned records:")
    for i, rec in enumerate(stream):
        print(f"  {i + 3}. order={rec['order_id']} total={rec['total']} pay={rec['payment_method']}")
        if i == 2:
            break

    # Closure-built filters + generator expressions (still lazy).
    high_value = make_threshold_filter(min_total=200.0)
    mid_value = make_threshold_filter(min_total=50.0)

    high_stream = (r for r in read_sales_records(dataset) if high_value(r))
    print("\nHigh-value sample (total >= 200):")
    for i, sale in enumerate(high_stream):
        print(
            f"  order={sale['order_id']} total={sale['total']:.2f} "
            f"ts={sale['timestamp']}"
        )
        if i == 4:
            break

    mid_count = sum(1 for _ in (r for r in read_sales_records(dataset) if mid_value(r)))
    print(f"\nMid-value count (total >= 50): {mid_count}")

    # Memory comparison: eager list vs streaming sum.
    tracemalloc.start()
    eager = list(read_sales_records(dataset))
    eager_peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    tracemalloc.start()
    streaming_total = sum(r["total"] for r in read_sales_records(dataset))
    stream_peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    print("\nMemory / runtime comparison:")
    print(f"  eager list size     : {len(eager)} records")
    print(f"  eager peak memory   : {eager_peak} bytes")
    print(f"  streaming sum total : ${streaming_total:,.2f}")
    print(f"  streaming peak mem  : {stream_peak} bytes")
    print(
        "  note: streaming keeps memory closer to one-record work; "
        "list(...) pays for the full snapshot."
    )


if __name__ == "__main__":
    main()
    sys.exit(0)
