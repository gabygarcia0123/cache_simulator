from pathlib import Path
import tempfile
import unittest

from cache_simulator.cache import simulate_cache
from cache_simulator.memory import calculate_cache, calculate_physical_memory, simulate_virtual_memory
from cache_simulator.models import SimulationConfig


def make_config(trace_file: Path, **overrides) -> SimulationConfig:
    values = {
        "cache_size_kb": 1,
        "block_size": 16,
        "associativity": 1,
        "replacement_policy": "RR",
        "physical_memory_mb": 1,
        "system_memory_percent": 0.0,
        "instructions_per_time_slice": 100,
        "trace_files": (str(trace_file),),
    }
    values.update(overrides)
    return SimulationConfig(**values)


class SimulatorTests(unittest.TestCase):
    def test_cache_geometry_uses_expected_bit_counts(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            trace = Path(tmp_dir) / "trace.trc"
            trace.write_text("EIP 0x0\n", encoding="utf-8")
            config = make_config(
                trace,
                cache_size_kb=64,
                block_size=64,
                associativity=2,
                physical_memory_mb=1024,
            )

            geometry = calculate_cache(config)

            self.assertEqual(geometry.total_blocks, 1024)
            self.assertEqual(geometry.rows, 512)
            self.assertEqual(geometry.offset_bits, 6)
            self.assertEqual(geometry.index_bits, 9)
            self.assertEqual(geometry.tag_bits, 15)
            self.assertEqual(geometry.overhead_bytes, 2048)

    def test_virtual_memory_counts_page_faults_for_new_pages(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            trace = Path(tmp_dir) / "trace.trc"
            trace.write_text("EIP 0x0000\nEIP 0x0004\nsrcM: 0x1000\n", encoding="utf-8")
            config = make_config(trace)
            physical = calculate_physical_memory(config)

            stats, page_tables = simulate_virtual_memory(config, physical)

            self.assertEqual(stats.virtual_pages_mapped, 3)
            self.assertEqual(stats.page_hits, 1)
            self.assertEqual(stats.page_faults, 2)
            self.assertEqual(stats.pages_from_free, 2)
            self.assertEqual(len(page_tables[0]), 2)

    def test_cache_counts_hits_and_misses(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            trace = Path(tmp_dir) / "trace.trc"
            trace.write_text("EIP 0x0000\nEIP 0x0004\nsrcM: 0x0010\nEIP 0x0000\n", encoding="utf-8")
            config = make_config(trace)
            physical = calculate_physical_memory(config)
            vm_stats, _ = simulate_virtual_memory(config, physical)

            stats = simulate_cache(config, vm_stats)

            self.assertEqual(stats.accesses, 4)
            self.assertEqual(stats.hits, 2)
            self.assertEqual(stats.misses, 2)
            self.assertEqual(stats.compulsory_misses, 2)
            self.assertEqual(stats.conflict_misses, 0)
            self.assertEqual(stats.instruction_bytes, 12)
            self.assertEqual(stats.source_destination_bytes, 4)


if __name__ == "__main__":
    unittest.main()
