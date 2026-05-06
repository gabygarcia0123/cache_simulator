import math
from collections import deque

from .models import (
    CACHE_COST_PER_KB,
    PAGE_SIZE_BYTES,
    PAGE_TABLE_ENTRIES,
    CacheGeometry,
    PhysicalMemory,
    SimulationConfig,
    VirtualMemoryStats,
)
from .trace import iter_trace_accesses


def calculate_cache(config: SimulationConfig) -> CacheGeometry:
    cache_size_bytes = config.cache_size_kb * 1024
    total_blocks = cache_size_bytes // config.block_size
    rows = total_blocks // config.associativity
    physical_memory_bytes = config.physical_memory_mb * 1024 * 1024

    offset_bits = int(math.log2(config.block_size))
    index_bits = int(math.log2(rows))
    physical_bits = int(math.log2(physical_memory_bytes))
    tag_bits = physical_bits - index_bits - offset_bits

    overhead_bits_per_block = tag_bits + 1
    overhead_bytes = (overhead_bits_per_block * total_blocks) // 8
    implementation_bytes = cache_size_bytes + overhead_bytes
    implementation_kb = implementation_bytes / 1024

    return CacheGeometry(
        total_blocks=total_blocks,
        rows=rows,
        offset_bits=offset_bits,
        index_bits=index_bits,
        tag_bits=tag_bits,
        overhead_bytes=overhead_bytes,
        implementation_bytes=implementation_bytes,
        implementation_kb=implementation_kb,
        cost=implementation_kb * CACHE_COST_PER_KB,
    )


def calculate_physical_memory(config: SimulationConfig) -> PhysicalMemory:
    physical_memory_bytes = config.physical_memory_mb * 1024 * 1024
    physical_pages = physical_memory_bytes // PAGE_SIZE_BYTES
    system_pages = int(physical_pages * (config.system_memory_percent / 100))
    entry_size_bits = 1 + int(math.log2(physical_pages))
    total_ram_bytes = (PAGE_TABLE_ENTRIES * entry_size_bits // 8) * len(config.trace_files)

    return PhysicalMemory(
        physical_pages=physical_pages,
        system_pages=system_pages,
        entry_size_bits=entry_size_bits,
        total_page_table_ram_bytes=total_ram_bytes,
    )


def simulate_virtual_memory(
    config: SimulationConfig,
    physical_memory: PhysicalMemory,
) -> tuple[VirtualMemoryStats, list[dict[int, int]]]:
    free_pages = deque(range(physical_memory.system_pages, physical_memory.physical_pages))
    page_tables: list[dict[int, int]] = [dict() for _ in config.trace_files]

    mapped = 0
    hits = 0
    from_free = 0
    faults = 0

    for pid, trace_file in enumerate(config.trace_files):
        for access in iter_trace_accesses((trace_file,)):
            virtual_page = access.address // PAGE_SIZE_BYTES
            mapped += 1

            if virtual_page in page_tables[pid]:
                hits += 1
                continue

            faults += 1
            if free_pages:
                page_tables[pid][virtual_page] = free_pages.popleft()
                from_free += 1
                continue

            if page_tables[pid]:
                evicted_virtual_page = next(iter(page_tables[pid]))
                evicted_physical_page = page_tables[pid].pop(evicted_virtual_page)
                page_tables[pid][virtual_page] = evicted_physical_page

    return (
        VirtualMemoryStats(
            virtual_pages_mapped=mapped,
            page_hits=hits,
            pages_from_free=from_free,
            page_faults=faults,
        ),
        page_tables,
    )

