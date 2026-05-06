from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TraceAccess:
    address: int
    is_instruction: bool
    is_data: bool


def iter_trace_accesses(trace_files: Iterable[str]) -> Iterable[TraceAccess]:
    for trace_file in trace_files:
        with Path(trace_file).open("r", encoding="utf-8") as handle:
            for line in handle:
                parts = line.strip().split()
                if not parts:
                    continue

                address_text = parts[-1]
                address = parse_address(address_text)
                if address is None:
                    continue

                yield TraceAccess(
                    address=address,
                    is_instruction=line.startswith("EIP"),
                    is_data=("srcM:" in line) or ("dstM:" in line),
                )


def parse_address(address_text: str) -> int | None:
    if address_text.startswith("0x"):
        base = 16
    elif address_text.isdigit():
        base = 10
    else:
        return None

    try:
        return int(address_text, base)
    except ValueError:
        return None

