from cache_simulator.cli import parse_args
from cache_simulator.memory import calculate_cache, calculate_physical_memory, simulate_virtual_memory
from cache_simulator.output import print_milestone_1, print_milestone_2


def main() -> None:
    config = parse_args()
    cache = calculate_cache(config)
    physical = calculate_physical_memory(config)
    vm_stats, page_tables = simulate_virtual_memory(config, physical)

    print_milestone_1(config, cache, physical)
    print_milestone_2(config, physical, vm_stats, page_tables)


if __name__ == "__main__":
    main()
