from __future__ import annotations

import csv
import time
import statistics
from typing import List, Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bankers_algorithm import is_safe_state
from scenario_generator import generate_safe_scenario, generate_unsafe_scenario, generate_random_scenario

PROCESS_COUNTS = [10, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
N_RESOURCES = 5
REPEATS = 10
RANDOM_REPEATS = 30
BASE_SEED = 2024


def _run_experiment(n_proc: int, safe: bool, seed: int) -> Dict:
    if safe:
        available, max_demand, allocation = generate_safe_scenario(
            n_proc, N_RESOURCES, seed
        )
    else:
        available, max_demand, allocation = generate_unsafe_scenario(
            n_proc, N_RESOURCES, seed
        )

    start = time.perf_counter()
    is_safe, _, metrics = is_safe_state(
        available, max_demand, allocation, n_proc, N_RESOURCES
    )
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return {
        "n_processes": n_proc,
        "scenario": "safe" if safe else "unsafe",
        "is_safe": is_safe,
        "time_ms": elapsed_ms,
        "comparisons": metrics["comparisons"],
        "iterations": metrics["iterations"],
    }


def _run_random_experiment(n_proc: int, seed: int) -> Dict:
    available, max_demand, allocation = generate_random_scenario(
        n_proc, N_RESOURCES, seed
    )

    start = time.perf_counter()
    is_safe, _, metrics = is_safe_state(
        available, max_demand, allocation, n_proc, N_RESOURCES
    )
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return {
        "n_processes": n_proc,
        "scenario": "random",
        "is_safe": is_safe,
        "time_ms": elapsed_ms,
        "comparisons": metrics["comparisons"],
        "iterations": metrics["iterations"],
    }


def run_evaluation() -> List[Dict]:
    rows: List[Dict] = []
    total = len(PROCESS_COUNTS) * 2 * REPEATS
    done = 0

    for n_proc in PROCESS_COUNTS:
        for repeat_idx in range(REPEATS):
            seed = BASE_SEED + repeat_idx
            for safe in (True, False):
                row = _run_experiment(n_proc, safe, seed)
                row["repeat"] = repeat_idx
                rows.append(row)
                done += 1
        pct = done / total * 100
        print(f"  [{pct:5.1f}%] n_processes = {n_proc:>5} done")

    return rows


def _run_random_experiments() -> Dict[int, Dict]:
    rows: List[Dict] = []
    total = len(PROCESS_COUNTS) * RANDOM_REPEATS
    done = 0

    for n_proc in PROCESS_COUNTS:
        for trial in range(RANDOM_REPEATS):
            seed = BASE_SEED + 1000 + trial
            row = _run_random_experiment(n_proc, seed)
            row["repeat"] = trial
            rows.append(row)
            done += 1
        pct = done / total * 100
        print(f"  [{pct:5.1f}%] n_processes = {n_proc:>5} done")

    return _aggregate(rows)


def _aggregate(rows: List[Dict]):
    agg: Dict[int, Dict] = {}
    for n in PROCESS_COUNTS:
        subset = [r for r in rows if r["n_processes"] == n]
        agg[n] = {
            "avg_time_ms": statistics.mean(r["time_ms"] for r in subset),
            "avg_comparisons": statistics.mean(r["comparisons"] for r in subset),
            "avg_iterations": statistics.mean(r["iterations"] for r in subset),
            "safe_count": sum(1 for r in subset if r["is_safe"]),
            "unsafe_count": sum(1 for r in subset if not r["is_safe"]),
            "total": len(subset),
        }
    return agg


_COLORS = {"primary": "#2563eb", "secondary": "#f59e0b", "danger": "#ef4444",
           "grid": "#e5e7eb", "bg": "#fafbfc"}


def _style_ax(ax, title: str, xlabel: str, ylabel: str):
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(True, linestyle="--", linewidth=0.6, color=_COLORS["grid"], alpha=0.8)
    ax.set_facecolor(_COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _plot_metric(xs, ys, title, ylabel, filename):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(xs, ys, marker="o", linewidth=2, markersize=6,
            color=_COLORS["primary"], markerfacecolor="white",
            markeredgewidth=2, markeredgecolor=_COLORS["primary"])
    _style_ax(ax, title, "Number of Processes", ylabel)
    ax.set_xticks(xs)
    ax.set_xticklabels(xs, rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(filename, dpi=180)
    plt.close(fig)
    print(f"  [OK] Saved {filename}")


def _plot_safe_unsafe(random_agg, filename):
    xs = list(random_agg.keys())
    safe_pct = [random_agg[n]["safe_count"] / random_agg[n]["total"] * 100 for n in xs]
    unsafe_pct = [random_agg[n]["unsafe_count"] / random_agg[n]["total"] * 100 for n in xs]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bar_w = 0.35
    x_pos = list(range(len(xs)))

    bars_safe = ax.bar([p - bar_w / 2 for p in x_pos], safe_pct, bar_w,
                       label="Safe %", color=_COLORS["primary"], edgecolor="white")
    bars_unsafe = ax.bar([p + bar_w / 2 for p in x_pos], unsafe_pct, bar_w,
                         label="Unsafe %", color=_COLORS["danger"], edgecolor="white")

    for bar in list(bars_safe) + list(bars_unsafe):
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 1,
                    f"{h:.0f}%", ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(xs, rotation=45, ha="right")
    _style_ax(ax, "Safe vs Unsafe Outcomes (Randomized Scenarios)",
              "Number of Processes", "Percentage (%)")
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(filename, dpi=180)
    plt.close(fig)
    print(f"  [OK] Saved {filename}")


def _write_csv(rows: List[Dict], filename: str):
    fieldnames = ["n_processes", "repeat", "scenario", "is_safe",
                  "time_ms", "comparisons", "iterations"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [OK] Saved {filename}")


def main():
    print("=" * 60)
    print("  Banker's Algorithm - Metrics Evaluation")
    print("=" * 60)

    print("\n> Running deterministic experiments ...")
    rows = run_evaluation()

    print("\n> Aggregating results ...")
    agg = _aggregate(rows)
    xs = PROCESS_COUNTS
    avg_time = [agg[n]["avg_time_ms"] for n in xs]
    avg_comp = [agg[n]["avg_comparisons"] for n in xs]
    avg_iter = [agg[n]["avg_iterations"] for n in xs]

    print("\n> Generating charts ...")
    _plot_metric(xs, avg_time,
                 "Execution Time vs Number of Processes",
                 "Execution Time (ms)", "execution_time.png")

    _plot_metric(xs, avg_comp,
                 "Number of Comparisons vs Number of Processes",
                 "Comparisons", "comparisons.png")

    _plot_metric(xs, avg_iter,
                 "Number of Iterations vs Number of Processes",
                 "Iterations", "iterations.png")

    print("\n> Running randomized Safe/Unsafe experiments ...")
    random_agg = _run_random_experiments()
    _plot_safe_unsafe(random_agg, "safe_vs_unsafe_ratio.png")

    print("\n> Exporting CSV ...")
    _write_csv(rows, "evaluation_results.csv")

    print("\n" + "=" * 60)
    print("  Done - all artefacts written.")
    print("=" * 60)


if __name__ == "__main__":
    main()
