import argparse
import math
from collections import defaultdict

# reads command-line inputs and turns them into usable variables
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", type=int, required=True)  # cache size (KB)
    parser.add_argument("-b", type=int, required=True)  # block size (bytes)
    parser.add_argument("-a", type=int, required=True)  # associativity
    parser.add_argument("-r", type=str, required=True)  # RR or RND
    parser.add_argument("-p", type=int, required=True)  # physical memory (MB)
    parser.add_argument("-u", type=float, required=True)  # % OS usage
    parser.add_argument("-n", type=int, required=True)  # instructions/time slice
    parser.add_argument("-f", action="append", required=True)  # trace files

    return parser.parse_args()


# CACHE CALCULATION
def calculate_cache(params):
    cache_size_bytes = params.s * 1024
    block_size = params.b
    associativity = params.a
    physical_memory_bytes = params.p * 1024 * 1024

    total_blocks = cache_size_bytes // block_size
    rows = total_blocks // associativity

    offset_bits = int(math.log2(block_size))
    index_bits = int(math.log2(rows))
    physical_bits = int(math.log2(physical_memory_bytes))
    tag_bits = physical_bits - index_bits - offset_bits

    overhead_bits_per_block = tag_bits + 1
    overhead_bytes = (overhead_bits_per_block * total_blocks) // 8

    impl_bytes = cache_size_bytes + overhead_bytes
    impl_kb = impl_bytes / 1024

    cost = impl_kb * 0.07

    return {
        "total_blocks": total_blocks,
        "rows": rows,
        "offset_bits": offset_bits,
        "index_bits": index_bits,
        "tag_bits": tag_bits,
        "overhead_bytes": overhead_bytes,
        "impl_bytes": impl_bytes,
        "impl_kb": impl_kb,
        "cost": cost
    }


# PHYSICAL MEMORY MODEL
def calculate_physical_memory(params):
    page_size = 4096
    physical_memory_bytes = params.p * 1024 * 1024

    physical_pages = physical_memory_bytes // page_size
    system_pages = int(physical_pages * (params.u / 100))

    entry_size_bits = 1 + int(math.log2(physical_pages))

    total_entries = 512 * 1024

    base_ram_bytes = (total_entries * entry_size_bits) // 8
    total_ram_bytes = base_ram_bytes * len(params.f)

    return {
        "physical_pages": physical_pages,
        "system_pages": system_pages,
        "entry_size_bits": entry_size_bits,
        "total_ram_bytes": total_ram_bytes
    }


# VIRTUAL MEMORY SIMULATION (FIXED)
def simulate_virtual_memory(params, phys):
    page_size = 4096

    total_physical_pages = phys["physical_pages"]
    system_pages = phys["system_pages"]

    free_pages = list(range(system_pages, total_physical_pages))
    page_tables = [dict() for _ in params.f]

    stats = {
        "virtual_pages_mapped": 0,
        "page_hits": 0,
        "pages_from_free": 0,
        "page_faults": 0
    }

    for pid, file in enumerate(params.f):
        with open(file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) == 0:
                    continue

                addr_str = parts[-1]

                # filter junk like "ret", "call"
                if not (addr_str.startswith("0x") or addr_str.isdigit()):
                    continue

                try:
                    address = int(addr_str, 16) if addr_str.startswith("0x") else int(addr_str)
                except ValueError:
                    continue

                virtual_page = address // page_size
                stats["virtual_pages_mapped"] += 1

                # HIT
                if virtual_page in page_tables[pid]:
                    stats["page_hits"] += 1
                    continue

                # MISS = PAGE FAULT
                stats["page_faults"] += 1

                if free_pages:
                    phys_page = free_pages.pop(0)
                    page_tables[pid][virtual_page] = phys_page
                    stats["pages_from_free"] += 1
                else:
                    # FIFO eviction (per-process)
                    evict_vpage = next(iter(page_tables[pid]))
                    evict_ppage = page_tables[pid].pop(evict_vpage)
                    page_tables[pid][virtual_page] = evict_ppage

    return stats, page_tables


# OUTPUT - MILESTONE 1
def print_results(params, cache, phys):
    print("MILESTONE #1:  Input Parameters and Calculated Values")
    print("Cache Simulator - CS 3853 – Team #14\n")

    print("Trace File(s):")
    for f in params.f:
        print(f"        {f}")
    print()

    print("***** Cache Input Parameters *****\n")
    print(f"Cache Size:                     {params.s} KB")
    print(f"Block Size:                     {params.b} bytes")
    print(f"Associativity:                  {params.a}")
    print(f"Replacement Policy:             {'Round Robin' if params.r.lower() == 'rr' else 'Random'}")
    print(f"Physical Memory:                {params.p} MB")
    print(f"Percent Memory Used by System:  {params.u:.1f}%")
    print(f"Instructions / Time Slice:      {params.n}\n")

    print("***** Cache Calculated Values *****\n")
    print(f"Total # Blocks:                 {cache['total_blocks']}")
    print(f"Tag Size:                       {cache['tag_bits']} bits")
    print(f"Index Size:                     {cache['index_bits']} bits")
    print(f"Total # Rows:                   {cache['rows']}")
    print(f"Overhead Size:                  {cache['overhead_bytes']} bytes")
    print(f"Implementation Memory Size:     {cache['impl_kb']:.2f} KB")
    print(f"Cost:                           ${cache['cost']:.2f}\n")

    print("***** Physical Memory Calculated Values *****\n")
    print(f"Number of Physical Pages:       {phys['physical_pages']}")
    print(f"Number of Pages for System:     {phys['system_pages']}")
    print(f"Size of Page Table Entry:       {phys['entry_size_bits']} bits")
    print(f"Total RAM for Page Table(s):    {phys['total_ram_bytes']} bytes")


# OUTPUT - MILESTONE 2
def print_vm_results(params, stats, page_tables, phys):
    print("\nMILESTONE #2: - Virtual Memory Simulation Results\n")

    page_size = 4096
    physical_memory_bytes = params.p * 1024 * 1024
    physical_pages = physical_memory_bytes // page_size
    system_pages = int(physical_pages * (params.u / 100))
    user_pages = physical_pages - system_pages

    entry_size_bits = phys["entry_size_bits"]

    print("***** VIRTUAL MEMORY SIMULATION RESULTS *****\n")

    print(f"Physical Pages Used By SYSTEM:  {system_pages}")
    print(f"Pages Available to User:         {user_pages}\n")

    print(f"Virtual Pages Mapped:           {stats['virtual_pages_mapped']}")
    print("        ------------------------------")
    print(f"        Page Table Hits:        {stats['page_hits']}")
    print(f"        Pages from Free:         {stats['pages_from_free']}")
    print(f"        Total Page Faults:       {stats['page_faults']}\n")

    print("Page Table Usage Per Process:")
    print("------------------------------")

    for i, table in enumerate(page_tables):
        used = len(table)
        total_entries = 512 * 1024
        percent = (used / total_entries) * 100

        wasted_bytes = (total_entries - used) * entry_size_bits // 8

        print(f"[{i}] Trace File {params.f[i]}:")
        print(f"        Used Page Table Entries: {used} ({percent:.2f}%)")
        print(f"        Page Table Wasted: {wasted_bytes} bytes\n")


# MAIN
def main():
    params = parse_args()

    cache = calculate_cache(params)
    phys = calculate_physical_memory(params)

    print_results(params, cache, phys)

    vm_stats, page_tables = simulate_virtual_memory(params, phys)

    print_vm_results(params, vm_stats, page_tables, phys)


if __name__ == "__main__":
    main()
