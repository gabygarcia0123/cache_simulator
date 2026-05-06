from .models import PAGE_TABLE_ENTRIES, CacheGeometry, CacheStats, PhysicalMemory, SimulationConfig, VirtualMemoryStats


def print_milestone_1(config: SimulationConfig, cache: CacheGeometry, physical: PhysicalMemory) -> None:
    print("MILESTONE #1:  Input Parameters and Calculated Values")
    print("Cache Simulator - CS 3853 - Team #14\n")

    print("Trace File(s):")
    for trace_file in config.trace_files:
        print(f"        {trace_file}")
    print()

    print("***** Cache Input Parameters *****\n")
    print(f"Cache Size:                     {config.cache_size_kb} KB")
    print(f"Block Size:                     {config.block_size} bytes")
    print(f"Associativity:                  {config.associativity}")
    print(f"Replacement Policy:             {replacement_policy_name(config.replacement_policy)}")
    print(f"Physical Memory:                {config.physical_memory_mb} MB")
    print(f"Percent Memory Used by System:  {config.system_memory_percent:.1f}%")
    print(f"Instructions / Time Slice:      {config.instructions_per_time_slice}\n")

    print("***** Cache Calculated Values *****\n")
    print(f"Total # Blocks:                 {cache.total_blocks}")
    print(f"Tag Size:                       {cache.tag_bits} bits")
    print(f"Index Size:                     {cache.index_bits} bits")
    print(f"Total # Rows:                   {cache.rows}")
    print(f"Overhead Size:                  {cache.overhead_bytes} bytes")
    print(f"Implementation Memory Size:     {cache.implementation_kb:.2f} KB")
    print(f"Cost:                           ${cache.cost:.2f}\n")

    print("***** Physical Memory Calculated Values *****\n")
    print(f"Number of Physical Pages:       {physical.physical_pages}")
    print(f"Number of Pages for System:     {physical.system_pages}")
    print(f"Size of Page Table Entry:       {physical.entry_size_bits} bits")
    print(f"Total RAM for Page Table(s):    {physical.total_page_table_ram_bytes} bytes")


def print_milestone_2(
    config: SimulationConfig,
    physical: PhysicalMemory,
    stats: VirtualMemoryStats,
    page_tables: list[dict[int, int]],
) -> None:
    print("\nMILESTONE #2: - Virtual Memory Simulation Results\n")
    print("***** VIRTUAL MEMORY SIMULATION RESULTS *****\n")

    user_pages = physical.physical_pages - physical.system_pages
    print(f"Physical Pages Used By SYSTEM:  {physical.system_pages}")
    print(f"Pages Available to User:         {user_pages}\n")

    print(f"Virtual Pages Mapped:           {stats.virtual_pages_mapped}")
    print("        ------------------------------")
    print(f"        Page Table Hits:        {stats.page_hits}")
    print(f"        Pages from Free:         {stats.pages_from_free}")
    print(f"        Total Page Faults:       {stats.page_faults}\n")

    print("Page Table Usage Per Process:")
    print("------------------------------")

    for index, table in enumerate(page_tables):
        used_entries = len(table)
        percent_used = (used_entries / PAGE_TABLE_ENTRIES) * 100
        wasted_bytes = (PAGE_TABLE_ENTRIES - used_entries) * physical.entry_size_bits // 8

        print(f"[{index}] Trace File {config.trace_files[index]}:")
        print(f"        Used Page Table Entries: {used_entries} ({percent_used:.2f}%)")
        print(f"        Page Table Wasted: {wasted_bytes} bytes\n")


def print_milestone_3(stats: CacheStats) -> None:
    print("\nCache Simulator - CS 3853 - Team #14\n")
    print("\nMILESTONE #3: - Cache Simulation Results\n")
    print("***** CACHE SIMULATION RESULTS *****\n")

    print(f"Total Cache Accesses:   {stats.accesses}")
    print(f"--- Instruction Bytes:  {stats.instruction_bytes}")
    print(f"--- SrcDst Bytes:       {stats.source_destination_bytes}\n")

    print(f"Cache Hits:             {stats.hits}")
    print(f"Cache Misses:           {stats.misses}")
    print(f"--- Compulsory Misses:  {stats.compulsory_misses}")
    print(f"--- Conflict Misses:    {stats.conflict_misses}\n")

    print("***** CACHE HIT & MISS RATE *****\n")
    print(f"Hit Rate:               {stats.hit_rate:.4f}%")
    print(f"Miss Rate:              {stats.miss_rate:.4f}%\n")

    print(f"CPI:                    {stats.cpi:.2f} Cycles/Instruction ({stats.cycles})\n")
    print("***** ADDITIONAL CACHE METRICS *****\n")
    print(f"Total Cache Blocks:     {stats.total_blocks}")
    print(f"Unused Cache Blocks:    {stats.unused_blocks}")
    print(f"Unused Cache Space:     {stats.unused_kb:.2f} KB")


def replacement_policy_name(policy: str) -> str:
    return "Random" if policy == "RND" else "Round Robin"

