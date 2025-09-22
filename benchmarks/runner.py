from time import perf_counter
from .hasher_base import PASSWORD, Hasher


class BenchmarkRunner:
    """Runs benchmarks for a list of password hasher configs."""

    def __init__(self, configs, loops: int = 3):
        self.configs = configs
        self.loops = loops

    def _time_call(self, fn):
        t0 = perf_counter()
        for _ in range(self.loops):
            fn()
        t1 = perf_counter()
        return (t1 - t0) / self.loops

    def run(self):
        print("== Password Hash Benchmark ==")
        for config in self.configs:
            self._run_config(config)

    def _run_config(self, config: Hasher):
        hash_time = self._time_call(config.hash_once)
        hashes = [config.hash_once() for _ in range(self.loops)]

        t0 = perf_counter()
        results = [config.verify_once(PASSWORD, h) for h in hashes]
        t1 = perf_counter()
        verify_time = (t1 - t0) / self.loops

        assert all(results), f"Verification failed for {config.label}"
        print(f"[{config.label}] hash: {hash_time:.3f}s | verify: {verify_time:.3f}s")

