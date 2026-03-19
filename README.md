# Formal Modeling, Algorithmic Evaluation, and Computational Analysis of Deadlock Management Frameworks in Multiprogramming Operating Systems

## 1. Introduction

This project implements, evaluates, and visualizes the **Banker's Algorithm** for deadlock avoidance in multiprogramming operating systems. The theoretical scope of the accompanying report discusses deadlock prevention, avoidance, and detection; the simulation and empirical analysis focus specifically on deadlock **avoidance** through the Banker's Algorithm.

---

## 2. Background Theory

### 2.1 What is Deadlock?

A **deadlock** is a situation in which a set of processes are permanently blocked because each process holds at least one resource and is waiting to acquire a resource held by another process in the set. No process can proceed, release its resources, or be terminated without external intervention.

Four **necessary conditions** must hold simultaneously for a deadlock to occur (Coffman conditions):

| # | Condition | Description |
|---|-----------|-------------|
| 1 | **Mutual Exclusion** | At least one resource must be held in a non-shareable mode. |
| 2 | **Hold and Wait** | A process holding resources can request additional ones. |
| 3 | **No Preemption** | Resources cannot be forcibly taken from a process. |
| 4 | **Circular Wait** | A circular chain of processes exists, each waiting for a resource held by the next. |

### 2.2 What is a Safe State?

A system state is **safe** if there exists at least one ordering of all processes (a *safe sequence*) such that every process can obtain its maximum required resources, complete its execution, and release its resources — even in the worst case. If no such sequence exists, the state is **unsafe**. An unsafe state does not guarantee deadlock, but it means that deadlock *cannot* be prevented by any scheduling order.

### 2.3 What is the Banker's Algorithm?

The **Banker's Algorithm**, proposed by Edsger Dijkstra, is a resource-allocation and deadlock-avoidance algorithm. Before granting a resource request, the operating system simulates the allocation and checks whether the resulting state remains safe. If so, the request is granted; otherwise, the process must wait.

**Key data structures:**

- `Available[j]` — number of instances of resource *j* currently free.
- `Max[i][j]` — maximum demand of process *i* for resource *j*.
- `Allocation[i][j]` — resources of type *j* currently held by process *i*.
- `Need[i][j] = Max[i][j] − Allocation[i][j]` — remaining demand.

**Safety check (simplified):**

1. Set `Work = Available`, `Finish[i] = false` for all *i*.
2. Find an unfinished process *i* such that `Need[i] ≤ Work`.
3. Simulate its completion: `Work = Work + Allocation[i]`, `Finish[i] = true`.
4. Repeat until all processes finish (safe) or no eligible process is found (unsafe).

---

## 3. Metrics Used

| Metric | What it measures |
|--------|-----------------|
| **Execution Time (ms)** | Wall-clock time to run one safety check. |
| **Comparisons** | Number of element-wise `Need[i][j] ≤ Work[j]` checks. |
| **Iterations** | Number of outer-loop passes through the process list. |
| **Safe / Unsafe Ratio** | Percentage of experiments yielding a safe vs. unsafe state at each process count. |

### Why These Metrics Matter

- **Execution time** directly measures the computational cost an OS scheduler would incur. As this grows, the overhead of deadlock avoidance becomes significant and may outweigh its benefits.
- **Comparisons** quantify the inner-loop work and reveal the algorithm's dependence on both process count and resource count. Because every unfinished process may be scanned on every iteration, comparisons grow roughly as *O(n²·m)*.
- **Iterations** count full scans of the process list. In the best case (safe state with favourable ordering) the algorithm finishes in *n* iterations; in the worst case (unsafe) it may still require *n* iterations before concluding no progress is possible.
- **Safe / unsafe ratio** shows how the probability of a safe state changes with system scale. Higher process counts lead to greater resource contention, making unsafe states more frequent — a key insight for OS capacity planning.

---

## 4. Analysis of Results

### Why Execution Time Increases
More processes means more comparisons per iteration and more iterations overall. The safety algorithm's inner loop checks `Need[i] ≤ Work` for each unfinished process on each pass. As *n* grows, the total work grows super-linearly (approximately *O(n²)*), leading to a clear upward trend in execution time.

### Why Comparisons Increase
The Banker's Algorithm performs an element-wise comparison `Need[i][j] > Work[j]` for each resource *j* of each unfinished process *i*. With *n* processes and *m* resource types, each full scan costs up to *n × m* comparisons, and up to *n* scans may be needed. The total comparison count therefore scales as *O(n² × m)*.

### Why the Safe/Unsafe Ratio Changes
As the number of concurrent processes increases with a fixed resource pool, resource contention intensifies. Each process's *Need* is more likely to exceed the *Available* vector, making it harder for the algorithm to find any process that can finish. Consequently, the proportion of unsafe states rises with scale — demonstrating that multiprogramming degree must be balanced against available resources to maintain system safety.

---

## 5. Limitations

> **Banker's Algorithm requires prior knowledge of the maximum resource demand of every process before execution begins.** In most real-world systems this information is unavailable or impractical to obtain, which limits the algorithm's applicability to controlled environments such as embedded or safety-critical systems. Furthermore, the algorithm assumes a fixed number of processes and resources, does not handle dynamic process creation, and introduces computational overhead that grows quadratically with the number of processes.

---

## 6. Project Structure

```
OS_A_Deadlock_Project/
├── bankers_algorithm.py      Core Banker's Algorithm implementation
├── scenario_generator.py     Reproducible safe / unsafe scenario generation
├── metrics_evaluation.py     Evaluation harness, charts, and CSV export
├── requirements.txt          Python dependencies
├── README.md                 This file
│
├── execution_time.png        ← generated
├── comparisons.png           ← generated
├── iterations.png            ← generated
├── safe_vs_unsafe_ratio.png  ← generated
└── evaluation_results.csv    ← generated
```

---

## 7. How to Run

### Prerequisites

- Python 3.8 or later
- `pip` package manager

### Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the evaluation (generates PNGs and CSV)
python metrics_evaluation.py
```

After execution, the output artefacts (`*.png`, `evaluation_results.csv`) will appear in the project root.

### Quick Smoke Test

Verify the algorithm on the classic textbook example:

```bash
python -c "from bankers_algorithm import is_safe_state; s,seq,m = is_safe_state([3,3,2],[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]],[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]],5,3); print('Safe' if s else 'Unsafe', seq)"
```

Expected output: `Safe [1, 3, 4, 0, 2]`
