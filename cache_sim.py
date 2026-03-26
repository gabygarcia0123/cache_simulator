import argparse

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

import math

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

    return {
        "total_blocks": total_blocks,
        "rows": rows,
        "offset_bits": offset_bits,
        "index_bits": index_bits,
        "tag_bits": tag_bits,
        "physical_bits": physical_bits
    }

def calculate_physical_memory(params):
    page_size = 4096  # 4 KB
    physical_memory_bytes = params.p * 1024 * 1024

    physical_pages = physical_memory_bytes // page_size
    system_pages = int(physical_pages * (params.u / 100))

    page_offset_bits = 12
    vpn_bits = 32 - page_offset_bits

    entry_size_bits = 1 + int(math.log2(physical_pages))  # valid + PPN

    total_entries = 2 ** vpn_bits

    total_ram_bytes = (total_entries * entry_size_bits) // 8
    total_ram_bytes *= len(params.f)  # multiply by trace files

    return {
        "physical_pages": physical_pages,
        "system_pages": system_pages,
        "entry_size_bits": entry_size_bits,
        "total_ram_bytes": total_ram_bytes
    }
