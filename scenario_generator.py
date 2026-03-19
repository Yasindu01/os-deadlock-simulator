from __future__ import annotations
import random
from typing import List, Tuple


def generate_safe_scenario(
    n_processes: int,
    n_resources: int,
    seed: int = 42,
) -> Tuple[List[int], List[List[int]], List[List[int]]]:

    rng = random.Random(seed)

    total = [rng.randint(n_processes, n_processes * 2) for _ in range(n_resources)]

    allocation: List[List[int]] = []
    col_sums = [0] * n_resources
    for _ in range(n_processes):
        row: List[int] = []
        for j in range(n_resources):
            upper = max(0, (total[j] * 6 // 10) - col_sums[j])
            val = rng.randint(0, max(0, upper // max(1, n_processes // 2)))
            row.append(val)
            col_sums[j] += val
        allocation.append(row)

    max_demand: List[List[int]] = []
    for i in range(n_processes):
        row: List[int] = []
        for j in range(n_resources):
            extra = rng.randint(0, max(1, total[j] * 3 // 10))
            row.append(allocation[i][j] + extra)
        max_demand.append(row)

    available = [total[j] - col_sums[j] for j in range(n_resources)]
    return available, max_demand, allocation


def generate_unsafe_scenario(
    n_processes: int,
    n_resources: int,
    seed: int = 42,
) -> Tuple[List[int], List[List[int]], List[List[int]]]:

    rng = random.Random(seed)

    total = [rng.randint(1, max(2, n_processes // 2)) for _ in range(n_resources)]

    allocation: List[List[int]] = []
    remaining = list(total)
    for i in range(n_processes):
        row: List[int] = []
        for j in range(n_resources):
            if i < n_processes - 1:
                val = rng.randint(0, max(0, remaining[j] // max(1, n_processes - i)))
            else:
                val = remaining[j]
            row.append(val)
            remaining[j] -= val
        allocation.append(row)

    max_demand: List[List[int]] = []
    for i in range(n_processes):
        row: List[int] = []
        for j in range(n_resources):
            row.append(allocation[i][j] + rng.randint(total[j] + 1, total[j] * 3 + 2))
        max_demand.append(row)

    available = list(remaining)
    return available, max_demand, allocation


def generate_random_scenario(
    n_processes: int,
    n_resources: int,
    seed: int = 42,
) -> Tuple[List[int], List[List[int]], List[List[int]]]:
    """Generate a scenario whose safe/unsafe outcome is NOT predetermined.

    Resources are sized so that the system lands near the safe/unsafe
    boundary — the Banker's Algorithm genuinely decides the result.
    """
    rng = random.Random(seed)

    # Total resources: roughly 1× to 2× the process count — tight enough
    # that some seeds produce safe states and others don't.
    total = [rng.randint(n_processes, n_processes * 2) for _ in range(n_resources)]

    # Allocate a random fraction (0-70 %) of each resource across processes
    allocation: List[List[int]] = []
    col_sums = [0] * n_resources
    for _ in range(n_processes):
        row: List[int] = []
        for j in range(n_resources):
            ceiling = max(0, total[j] - col_sums[j])
            val = rng.randint(0, max(0, ceiling // max(1, n_processes)))
            row.append(val)
            col_sums[j] += val
        allocation.append(row)

    # Max demand = allocation + random extra (0 … remaining total)
    max_demand: List[List[int]] = []
    for i in range(n_processes):
        row: List[int] = []
        for j in range(n_resources):
            extra = rng.randint(0, max(1, total[j] - allocation[i][j]))
            row.append(allocation[i][j] + extra)
        max_demand.append(row)

    available = [total[j] - col_sums[j] for j in range(n_resources)]
    return available, max_demand, allocation



