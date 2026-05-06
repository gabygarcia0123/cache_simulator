# Cache Simulator

Computer architecture cache simulator for CS 3853. The project is organized as a small Python package with thin milestone scripts at the repository root.

## Project Layout

- `milestone1.py`: prints input parameters, cache geometry, and physical memory calculations.
- `milestone2.py`: runs milestone 1 output plus virtual memory simulation.
- `milestone3.py`: runs virtual memory setup and prints cache simulation results.
- `cache_simulator/`: shared simulator implementation.
- `tests/`: regression tests with small synthetic traces.
- `Team_14_Sim_*`: saved sample outputs.

## Usage

```bash
python3 milestone2.py -s 64 -b 64 -a 2 -r RR -p 1024 -u 75 -n 10000 -f path/to/trace.trc
python3 milestone3.py -s 64 -b 64 -a 2 -r RR -p 1024 -u 75 -n 10000 -f path/to/trace.trc
```

Use repeated `-f` arguments to simulate multiple trace files.

## Notes

- Virtual memory uses 4 KB pages.
- Page misses are counted as page faults whether the page comes from the free list or from replacement.
- Cache replacement supports `RR` and `RND`; `RND` uses a fixed seed so runs are repeatable.

## Tests

```bash
python3 -m unittest discover tests
```
