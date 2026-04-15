"""Theoretical best / average / worst time and space for common sorts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SortComplexity:
    name: str
    best_time: str
    average_time: str
    worst_time: str
    space: str
    best_note: str
    worst_note: str


ROWS: tuple[SortComplexity, ...] = (
    SortComplexity(
        "Bubble sort",
        "O(n)",
        "O(n²)",
        "O(n²)",
        "O(1)",
        "Single pass with swap check when already sorted (optimized variant).",
        "Reverse order; many swaps per pass.",
    ),
    SortComplexity(
        "Selection sort",
        "O(n²)",
        "O(n²)",
        "O(n²)",
        "O(1)",
        "Still scans unsorted region every time; no adaptive best case.",
        "Same as average — work is dominated by the nested structure.",
    ),
    SortComplexity(
        "Insertion sort",
        "O(n)",
        "O(n²)",
        "O(n²)",
        "O(1)",
        "Each element inserts in O(1) when already sorted.",
        "Reverse sorted — every insert shifts the whole prefix.",
    ),
    SortComplexity(
        "Merge sort",
        "O(n log n)",
        "O(n log n)",
        "O(n log n)",
        "O(n)",
        "Always divides evenly; same recursion depth pattern.",
        "No pathological input for time; cost is stable.",
    ),
    SortComplexity(
        "Quicksort (typical)",
        "O(n log n)",
        "O(n log n)",
        "O(n²)",
        "O(log n) avg",
        "Balanced partitions (e.g. good pivot, random pivot).",
        "Bad pivots every time (e.g. min/max on sorted with naive pivot).",
    ),
    SortComplexity(
        "Heapsort",
        "O(n log n)",
        "O(n log n)",
        "O(n log n)",
        "O(1)",
        "Build-heap + repeated extract-max are always Θ(n log n).",
        "Same — no adaptive best case for time.",
    ),
)


def format_table() -> str:
    headers = ("Algorithm", "Best", "Average", "Worst", "Extra space")
    lines = [
        " | ".join(headers),
        " | ".join("---" for _ in headers),
    ]
    for r in ROWS:
        lines.append(
            " | ".join(
                (
                    r.name,
                    r.best_time,
                    r.average_time,
                    r.worst_time,
                    r.space,
                )
            )
        )
    return "\n".join(lines)


def format_notes() -> str:
    parts = []
    for r in ROWS:
        parts.append(f"{r.name}\n  Best: {r.best_note}\n  Worst: {r.worst_note}")
    return "\n\n".join(parts)
