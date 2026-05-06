import math
import random

from .models import CacheStats, SimulationConfig, VirtualMemoryStats
from .trace import iter_trace_accesses


def simulate_cache(config: SimulationConfig, vm_stats: VirtualMemoryStats) -> CacheStats:
    cache_size = config.cache_size_kb * 1024
    total_blocks = cache_size // config.block_size
    num_sets = total_blocks // config.associativity
    cache_sets: list[list[int]] = [[] for _ in range(num_sets)]
    rng = random.Random(0)

    hits = 0
    misses = 0
    compulsory = 0
    conflict = 0
    accesses = 0
    cycles = 0
    instruction_count = 0
    instruction_bytes = 0
    srcdst_bytes = 0
    seen_blocks: set[int] = set()

    block_reads = math.ceil(config.block_size / 4)
    miss_penalty = 4 * block_reads

    for access in iter_trace_accesses(config.trace_files):
        if access.is_instruction:
            instruction_count += 1
            instruction_bytes += 4
            cycles += 2

        if access.is_data:
            srcdst_bytes += 4
            cycles += 1

        block = access.address // config.block_size
        set_index = block % num_sets
        tag = block // num_sets

        accesses += 1
        cycles += 1

        if tag in cache_sets[set_index]:
            hits += 1
            continue

        misses += 1
        if block not in seen_blocks:
            compulsory += 1
            seen_blocks.add(block)
        else:
            conflict += 1

        cycles += miss_penalty
        insert_cache_line(cache_sets[set_index], tag, config.associativity, config.replacement_policy, rng)

    cycles += vm_stats.page_faults * 100
    cpi = cycles / instruction_count if instruction_count else 0
    used_blocks = sum(len(cache_set) for cache_set in cache_sets)
    unused_blocks = max(0, total_blocks - used_blocks)

    return CacheStats(
        accesses=accesses,
        hits=hits,
        misses=misses,
        compulsory_misses=compulsory,
        conflict_misses=conflict,
        cycles=cycles,
        cpi=cpi,
        hit_rate=(hits / accesses * 100) if accesses else 0,
        miss_rate=(misses / accesses * 100) if misses else 0,
        instruction_bytes=instruction_bytes,
        source_destination_bytes=srcdst_bytes,
        total_blocks=total_blocks,
        unused_blocks=unused_blocks,
        unused_kb=(unused_blocks * config.block_size) / 1024,
    )


def insert_cache_line(
    cache_set: list[int],
    tag: int,
    associativity: int,
    replacement_policy: str,
    rng: random.Random,
) -> None:
    if len(cache_set) < associativity:
        cache_set.append(tag)
        return

    if replacement_policy == "RND":
        cache_set[rng.randrange(associativity)] = tag
        return

    cache_set.pop(0)
    cache_set.append(tag)

