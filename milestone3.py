from cache_simulator.cache import simulate_cache
from cache_simulator.cli import parse_args
from cache_simulator.memory import calculate_physical_memory, simulate_virtual_memory
from cache_simulator.output import print_milestone_3


def main() -> None:
    config = parse_args()
    physical = calculate_physical_memory(config)
    vm_stats, _ = simulate_virtual_memory(config, physical)
    cache_stats = simulate_cache(config, vm_stats)
    print_milestone_3(cache_stats)


if __name__ == "__main__":
    main()
