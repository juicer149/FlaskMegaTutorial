import argparse
from time import perf_counter
from .hasher import PBKDF2Config, BcryptConfig, Argon2Config
from .runner import BenchmarkRunner
from .hasher_base import PASSWORD

TARGET_TIME = 0.25  # seconds


def time_call(fn, loops=3):
    t0 = perf_counter()
    for _ in range(loops):
        fn()
    t1 = perf_counter()
    return (t1 - t0) / loops


def calibrate_pbkdf2():
    iterations = 10_000
    while True:
        config = PBKDF2Config(iterations)
        duration = time_call(config.hash_once)
        if duration >= TARGET_TIME:
            print(f"{config.label} → {duration:.3f} sec")
            break
        iterations = int(iterations * 1.2)


def calibrate_bcrypt():
    rounds = 4
    while True:
        config = BcryptConfig(rounds)
        duration = time_call(config.hash_once)
        if duration >= TARGET_TIME:
            print(f"{config.label} → {duration:.3f} sec")
            break
        rounds += 1


def calibrate_argon2():
    time_cost = 2
    memory_cost = 65536  # 64 MB
    parallelism = 2
    while True:
        config = Argon2Config(time_cost, memory_cost, parallelism)
        duration = time_call(config.hash_once)
        if duration >= TARGET_TIME:
            print(f"{config.label} → {duration:.3f} sec")
            break
        time_cost += 1


def run_calibration():
    print("== Calibration to ~250ms ==")
    calibrate_pbkdf2()
    calibrate_bcrypt()
    calibrate_argon2()


def run_profiles():
    configs = [
        PBKDF2Config(260000),
        BcryptConfig(13),
        Argon2Config(4, 32768, 1, "Small device"),
        Argon2Config(6, 65536, 2, "Balanced"),
        Argon2Config(8, 131072, 2, "Production"),
        Argon2Config(10, 131072, 3, "High security"),
        Argon2Config(4, 262144, 1, "Memory-heavy"),
    ]
    runner = BenchmarkRunner(configs, loops=3)
    runner.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--calibrate", action="store_true",
        help="Run auto-calibration instead of fixed configs"
    )
    args = parser.parse_args()

    if args.calibrate:
        run_calibration()
    else:
        run_profiles()

