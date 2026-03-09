# utils.py
import timeit
import tracemalloc
import statistics
import sys
from io import StringIO
from config import BENCHMARK_RUNS, BENCHMARK_ITERATIONS


def robust_benchmark(code: str, runs: int = None, iterations: int = None):
    """
    Benchmark code execution time and memory usage.
    Uses a shared namespace dict so variables persist across lines within exec(),
    fixing the Python 3 list-comprehension scope issue.
    """
    if runs is None:
        runs = BENCHMARK_RUNS
    if iterations is None:
        iterations = BENCHMARK_ITERATIONS

    # Compile once for faster repeated execution
    try:
        compiled = compile(code, "<benchmark>", "exec")
    except SyntaxError:
        return None

    samples = []
    mem_samples = []

    for run_num in range(runs):
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO()
            tracemalloc.start()

            # Use a shared namespace dict so variables defined on one line
            # are visible to subsequent lines and inside comprehensions
            def _run():
                ns = {}
                exec(compiled, ns)

            t = timeit.timeit(_run, number=iterations)

            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            sys.stdout = old_stdout

            samples.append(t * 1000 / iterations)
            mem_samples.append(peak / (1024 ** 2))
        except Exception:
            sys.stdout = old_stdout
            if tracemalloc.is_tracing():
                tracemalloc.stop()

    if not samples:
        return None

    mean_ms = statistics.mean(samples)
    variance_pct = 0.0
    if len(samples) > 1 and mean_ms > 0:
        variance_pct = round((statistics.stdev(samples) / mean_ms) * 100, 2)

    return {
        "runtime_ms": round(mean_ms, 3),
        "memory_mb": round(max(mem_samples), 2),
        "runs": len(samples),
        "variance_pct": variance_pct
    }
