from dataclasses import dataclass


PAGE_SIZE_BYTES = 4096
PAGE_TABLE_ENTRIES = 512 * 1024
CACHE_COST_PER_KB = 0.07


@dataclass(frozen=True)
class SimulationConfig:
    cache_size_kb: int
    block_size: int
    associativity: int
    replacement_policy: str
    physical_memory_mb: int
    system_memory_percent: float
    instructions_per_time_slice: int
    trace_files: tuple[str, ...]


@dataclass(frozen=True)
class CacheGeometry:
    total_blocks: int
    rows: int
    offset_bits: int
    index_bits: int
    tag_bits: int
    overhead_bytes: int
    implementation_bytes: int
    implementation_kb: float
    cost: float


@dataclass(frozen=True)
class PhysicalMemory:
    physical_pages: int
    system_pages: int
    entry_size_bits: int
    total_page_table_ram_bytes: int


@dataclass(frozen=True)
class VirtualMemoryStats:
    virtual_pages_mapped: int
    page_hits: int
    pages_from_free: int
    page_faults: int


@dataclass(frozen=True)
class CacheStats:
    accesses: int
    hits: int
    misses: int
    compulsory_misses: int
    conflict_misses: int
    cycles: int
    cpi: float
    hit_rate: float
    miss_rate: float
    instruction_bytes: int
    source_destination_bytes: int
    total_blocks: int
    unused_blocks: int
    unused_kb: float

