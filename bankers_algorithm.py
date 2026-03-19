from __future__ import annotations
from typing import List, Dict, Tuple


def is_safe_state(
    available: List[int],
    max_demand: List[List[int]],
    allocation: List[List[int]],
    n_processes: int,
    n_resources: int,
) -> Tuple[bool, List[int], Dict[str, int]]:

    need = [
        [max_demand[i][j] - allocation[i][j] for j in range(n_resources)]
        for i in range(n_processes)
    ]

    work = list(available)
    finish = [False] * n_processes
    safe_sequence: List[int] = []
    comparisons = 0
    iterations = 0

    finished_count = 0
    while finished_count < n_processes:
        iterations += 1
        found = False

        for i in range(n_processes):
            if finish[i]:
                continue

            can_finish = True
            for j in range(n_resources):
                comparisons += 1
                if need[i][j] > work[j]:
                    can_finish = False
                    break

            if can_finish:
                for j in range(n_resources):
                    work[j] += allocation[i][j]
                finish[i] = True
                safe_sequence.append(i)
                finished_count += 1
                found = True
                break

        if not found:
            break

    is_safe = finished_count == n_processes
    if not is_safe:
        safe_sequence = []

    metrics = {"comparisons": comparisons, "iterations": iterations}
    return is_safe, safe_sequence, metrics
