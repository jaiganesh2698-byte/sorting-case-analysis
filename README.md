# Sorting: best, worst, and average cases

Companion project that summarizes **asymptotic time complexity** for common comparison sorts and includes a small **Python demo** that contrasts inputs where each algorithm behaves well vs. poorly.

## Setup

Uses Python 3.9+ and the standard library only.

```bash
cd sorting-case-analysis
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

No third-party packages are required.

## Run

Print the theory table and run empirical timings:

```bash
python demo.py
```

Optional: larger arrays and more repeats (slower):

```bash
python demo.py --n 5000 --repeats 5
```

## What “best / average / worst” means

- **Best case**: input shape and model assumptions that minimize work (e.g. already sorted for insertion sort).
- **Average case**: typical random input under the usual model (e.g. random order, all orderings equally likely for quicksort analysis).
- **Worst case**: input that maximizes work (e.g. reverse sorted for naive quicksort with a bad pivot rule).

Constants and cache effects matter in practice; Big-O describes growth as **n** gets large.
