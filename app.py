import os
import io
import base64
import time

from flask import Flask, render_template, request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bankers_algorithm import is_safe_state

app = Flask(__name__)


def _parse_matrix(text: str) -> list[list[int]]:
    rows = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line:
            rows.append([int(x) for x in line.split()])
    return rows


def _parse_vector(text: str) -> list[int]:
    return [int(x) for x in text.strip().split()]


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return encoded


def _make_need_chart(need: list[list[int]], n_proc: int, n_res: int) -> str:
    totals = [sum(need[i]) for i in range(n_proc)]
    labels = [f"P{i}" for i in range(n_proc)]

    fig, ax = plt.subplots(figsize=(6, max(2.5, n_proc * 0.35)))
    colors = ["#2563eb" if t > 0 else "#94a3b8" for t in totals]
    ax.barh(labels, totals, color=colors, edgecolor="white", height=0.6)
    ax.set_xlabel("Total Need (sum across resources)")
    ax.set_title("Per-Process Resource Need", fontweight="bold")
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_base64(fig)


def _make_allocation_chart(allocation: list[list[int]], n_proc: int, n_res: int) -> str:
    labels = [f"P{i}" for i in range(n_proc)]
    palette = ["#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6",
               "#ec4899", "#14b8a6", "#f97316"]

    fig, ax = plt.subplots(figsize=(6, max(2.5, n_proc * 0.35)))
    left = [0] * n_proc
    for j in range(n_res):
        vals = [allocation[i][j] for i in range(n_proc)]
        ax.barh(labels, vals, left=left, label=f"R{j}",
                color=palette[j % len(palette)], edgecolor="white", height=0.6)
        left = [left[i] + vals[i] for i in range(n_proc)]

    ax.set_xlabel("Allocated Instances")
    ax.set_title("Current Allocation per Process", fontweight="bold")
    ax.legend(loc="lower right", fontsize=8, framealpha=0.9)
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_base64(fig)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/result", methods=["POST"])
def result():
    try:
        available = _parse_vector(request.form["available"])
        max_demand = _parse_matrix(request.form["max_demand"])
        allocation = _parse_matrix(request.form["allocation"])

        n_processes = len(max_demand)
        n_resources = len(available)

        for i, row in enumerate(max_demand):
            if len(row) != n_resources:
                raise ValueError(
                    f"Max row {i} has {len(row)} values, expected {n_resources}"
                )
        for i, row in enumerate(allocation):
            if len(row) != n_resources:
                raise ValueError(
                    f"Allocation row {i} has {len(row)} values, expected {n_resources}"
                )
        if len(allocation) != n_processes:
            raise ValueError(
                f"Allocation has {len(allocation)} rows but Max has {n_processes}"
            )

        need = [
            [max_demand[i][j] - allocation[i][j] for j in range(n_resources)]
            for i in range(n_processes)
        ]

        start = time.perf_counter()
        is_safe, safe_sequence, metrics = is_safe_state(
            available, max_demand, allocation, n_processes, n_resources
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        need_chart = _make_need_chart(need, n_processes, n_resources)
        alloc_chart = _make_allocation_chart(allocation, n_processes, n_resources)

        return render_template(
            "result.html",
            is_safe=is_safe,
            safe_sequence=safe_sequence,
            need=need,
            metrics=metrics,
            elapsed_ms=round(elapsed_ms, 3),
            n_processes=n_processes,
            n_resources=n_resources,
            available=available,
            max_demand=max_demand,
            allocation=allocation,
            need_chart=need_chart,
            alloc_chart=alloc_chart,
        )

    except Exception as exc:
        return render_template("index.html", error=str(exc))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
