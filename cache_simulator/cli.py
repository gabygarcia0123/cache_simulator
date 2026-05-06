import argparse

from .models import SimulationConfig


def parse_args() -> SimulationConfig:
    parser = argparse.ArgumentParser(description="Computer architecture cache simulator")
    parser.add_argument("-s", type=int, required=True, help="cache size in KB")
    parser.add_argument("-b", type=int, required=True, help="block size in bytes")
    parser.add_argument("-a", type=int, required=True, help="cache associativity")
    parser.add_argument("-r", choices=("RR", "RND", "rr", "rnd"), required=True, help="replacement policy")
    parser.add_argument("-p", type=int, required=True, help="physical memory in MB")
    parser.add_argument("-u", type=float, required=True, help="percent of physical memory used by the OS")
    parser.add_argument("-n", type=int, required=True, help="instructions per time slice")
    parser.add_argument("-f", action="append", required=True, help="trace file path; repeat for multiple files")

    args = parser.parse_args()

    config = SimulationConfig(
        cache_size_kb=args.s,
        block_size=args.b,
        associativity=args.a,
        replacement_policy=args.r.upper(),
        physical_memory_mb=args.p,
        system_memory_percent=args.u,
        instructions_per_time_slice=args.n,
        trace_files=tuple(args.f),
    )
    validation_error = validate_config(config)
    if validation_error:
        parser.error(validation_error)

    return config


def validate_config(config: SimulationConfig) -> str | None:
    cache_size_bytes = config.cache_size_kb * 1024

    if config.cache_size_kb <= 0:
        return "cache size must be greater than 0 KB"
    if config.block_size <= 0:
        return "block size must be greater than 0 bytes"
    if config.associativity <= 0:
        return "associativity must be greater than 0"
    if config.physical_memory_mb <= 0:
        return "physical memory must be greater than 0 MB"
    if not 0 <= config.system_memory_percent <= 100:
        return "system memory percent must be between 0 and 100"
    if config.instructions_per_time_slice <= 0:
        return "instructions per time slice must be greater than 0"
    if not is_power_of_two(config.block_size):
        return "block size must be a power of two"
    if not is_power_of_two(cache_size_bytes):
        return "cache size must be a power of two"
    if cache_size_bytes < config.block_size:
        return "cache size must be at least one block"
    if cache_size_bytes % config.block_size != 0:
        return "cache size must be evenly divisible by block size"

    total_blocks = cache_size_bytes // config.block_size
    if total_blocks % config.associativity != 0:
        return "total cache blocks must be evenly divisible by associativity"

    rows = total_blocks // config.associativity
    if rows <= 0:
        return "cache must contain at least one row"
    if not is_power_of_two(rows):
        return "number of cache rows must be a power of two"

    return None


def is_power_of_two(value: int) -> bool:
    return value > 0 and (value & (value - 1)) == 0
