from cache_simulator.cli import parse_args
from cache_simulator.memory import calculate_cache, calculate_physical_memory
from cache_simulator.output import print_milestone_1


def main() -> None:
    config = parse_args()
    cache = calculate_cache(config)
    physical = calculate_physical_memory(config)
    print_milestone_1(config, cache, physical)


if __name__ == "__main__":
    main()
