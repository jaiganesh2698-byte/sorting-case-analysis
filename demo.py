"""Print complexity reference and time naive vs Python's Timsort on shaped inputs."""

from __future__ import annotations

import argparse
import random
import time
from copy import copy

from theory import ROWS, format_notes, format_table


def bubble_sort(a: list[int]) -> None:
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break


def insertion_sort(a: list[int]) -> None:
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key


def quicksort_lomuto(a: list[int]) -> None:
    """In-place quicksort with first-element pivot (worst Θ(n²) time on sorted input).

    Iterative explicit stack avoids Python recursion limits on pathological depth.
    """

    if len(a) < 2:
        return
    stack = [(0, len(a) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        pivot = a[lo]
        i = lo + 1
        for j in range(lo + 1, hi + 1):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[lo], a[i - 1] = a[i - 1], a[lo]
        p = i - 1
        stack.append((lo, p - 1))
        stack.append((p + 1, hi))


def builtin_sort(a: list[int]) -> None:
    a.sort()


def bench(name: str, sort_fn, data: list[int], repeats: int) -> float:
    total = 0.0
    for _ in range(repeats):
        work = copy(data)
        t0 = time.perf_counter()
        sort_fn(work)
        total += time.perf_counter() - t0
    return total / repeats


def main() -> None:
    parser = argparse.ArgumentParser(description="Sorting case comparison demo")
    parser.add_argument("--n", type=int, default=2000, help="Array length")
    parser.add_argument("--repeats", type=int, default=3, help="Averages per scenario")
    args = parser.parse_args()
    n = max(2, args.n)
    repeats = max(1, args.repeats)

    print("## Theoretical comparison (Big-O)\n")
    print(format_table())
    print("\n## Notes\n")
    print(format_notes())

    print("\n## Empirical timings (seconds, mean over repeats)\n")
    print(f"n = {n}, repeats = {repeats}\n")

    sorted_arr = list(range(n))
    reverse_arr = list(range(n - 1, -1, -1))
    rng = random.Random(42)
    random_arr = [rng.randint(0, n) for _ in range(n)]

    scenarios = (
        ("already sorted (often best for insertion / optimized bubble)", sorted_arr),
        ("reverse sorted (often bad for insertion / naive quicksort)", reverse_arr),
        ("random order", random_arr),
    )

    sorters = (
        ("Python list.sort (Timsort)", builtin_sort),
        ("Bubble sort (stops early if no swaps)", bubble_sort),
        ("Insertion sort", insertion_sort),
        ("Quicksort (Lomuto, first pivot)", quicksort_lomuto),
    )

    for label, data in scenarios:
        print(f"### {label}")
        for sname, fn in sorters:
            ms = bench(sname, fn, data, repeats) * 1000
            print(f"  {sname}: {ms:.2f} ms")
        print()

    print(
        "Takeaway: the same algorithm can look 'fast' or 'slow' depending on input shape; "
        "the table above explains the asymptotic story, while timings show real overhead and constants."
    )


if __name__ == "__main__":
    main()
