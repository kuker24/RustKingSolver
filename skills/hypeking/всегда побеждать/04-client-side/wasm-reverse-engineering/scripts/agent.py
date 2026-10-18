#!/usr/bin/env python3
"""
WebAssembly Reverse Engineering Tool
Parses WASM binary files to extract imports, exports, function
signatures, memory sections, and table information.

MITRE ATT&CK:
  T1595 - Active Scanning
  T1203 - Exploitation for Client Execution
"""

import argparse
import sys
import signal
import struct
import io
import tempfile
from typing import Optional, List, Tuple, Dict, Any

import requests
from colorama import init, Fore, Style

init(autoreset=True)

RUNNING = True

# WASM section IDs
SECTION_NAMES = {
    0: "Custom",
    1: "Type",
    2: "Import",
    3: "Function",
    4: "Table",
    5: "Memory",
    6: "Global",
    7: "Export",
    8: "Start",
    9: "Element",
    10: "Code",
    11: "Data",
    12: "DataCount",
}

# Value types
VAL_TYPES = {
    0x7F: "i32",
    0x7E: "i64",
    0x7D: "f32",
    0x7C: "f64",
    0x7B: "v128",
    0x70: "funcref",
    0x6F: "externref",
}

# Import/Export kinds
IMPORT_KINDS = {0: "func", 1: "table", 2: "mem", 3: "global"}


def signal_handler(sig, frame):
    global RUNNING
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Exiting gracefully...{Style.RESET_ALL}")
    RUNNING = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class LEB128Reader:
    """Read LEB128-encoded unsigned integers from a byte stream."""

    @staticmethod
    def read_uint(data: bytes, offset: int = 0) -> Tuple[int, int]:
        result = 0
        shift = 0
        pos = offset
        while pos < len(data):
            byte = data[pos]
            result |= (byte & 0x7F) << shift
            shift += 7
            pos += 1
            if not (byte & 0x80):
                break
        return result, pos - offset

    @staticmethod
    def read_int(data: bytes, offset: int = 0) -> Tuple[int, int]:
        result = 0
        shift = 0
        pos = offset
        size = 0
        while pos < len(data):
            byte = data[pos]
            result |= (byte & 0x7F) << shift
            shift += 7
            pos += 1
            size += 1
            if not (byte & 0x80):
                if shift < 32 and (byte & 0x40):
                    result |= -(1 << shift)
                break
        return result, size


class WASMParser:
    """Parser for WebAssembly binary format."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.sections: Dict[int, Dict[str, Any]] = {}
        self.type_entries: List[Dict[str, Any]] = []
        self.imports: List[Dict[str, Any]] = []
        self.exports: List[Dict[str, Any]] = []
        self.functions: List[Dict[str, Any]] = []
        self.tables: List[Dict[str, Any]] = []
        self.memories: List[Dict[str, Any]] = []
        self.globals: List[Dict[str, Any]] = []
        self.error: Optional[str] = None

    def _read_leb128_u(self) -> int:
        val, consumed = LEB128Reader.read_uint(self.data, self.pos)
        self.pos += consumed
        return val

    def _read_leb128_i(self) -> int:
        val, consumed = LEB128Reader.read_int(self.data, self.pos)
        self.pos += consumed
        return val

    def _read_bytes(self, n: int) -> bytes:
        result = self.data[self.pos:self.pos + n]
        self.pos += n
        return result

    def _read_name(self) -> str:
        length = self._read_leb128_u()
        raw = self._read_bytes(length)
        return raw.decode("utf-8", errors="replace")

    def _read_val_type(self) -> str:
        byte = self.data[self.pos]
        self.pos += 1
        return VAL_TYPES.get(byte, f"0x{byte:02X}")

    def _read_type_entry(self) -> Dict[str, Any]:
        form = self.data[self.pos]
        self.pos += 1
        entry: Dict[str, Any] = {"params": [], "results": []}
        if form == 0x60:
            param_count = self._read_leb128_u()
            for _ in range(param_count):
                entry["params"].append(self._read_val_type())
            result_count = self._read_leb128_u()
            for _ in range(result_count):
                entry["results"].append(self._read_val_type())
        return entry

    def _read_limits(self) -> Dict[str, Any]:
        flags = self.data[self.pos]
        self.pos += 1
        limits: Dict[str, Any] = {"min": 0, "max": None}
        limits["min"] = self._read_leb128_u()
        if flags & 0x01:
            limits["max"] = self._read_leb128_u()
        return limits

    def parse(self) -> bool:
        try:
            # Magic bytes
            magic = self._read_bytes(4)
            if magic != b"\x00asm":
                self.error = "Invalid WASM magic bytes"
                return False

            version = struct.unpack("<I", self._read_bytes(4))[0]
            if version != 1:
                self.error = f"Unsupported WASM version: {version}"
                return False

            # Parse sections
            while self.pos < len(self.data):
                section_id = self.data[self.pos]
                self.pos += 1
                section_size = self._read_leb128_u()
                section_end = self.pos + section_size

                if section_id == 0:
                    # Custom section - skip
                    self.pos = section_end
                    continue

                section_data = self._read_bytes(section_size)
                self._parse_section(section_id, section_data)

                # Ensure position is correct
                self.pos = section_end

            return True

        except (IndexError, struct.error) as e:
            self.error = f"Parse error: {e}"
            return False

    def _parse_section(self, section_id: int, data: bytes) -> None:
        old_pos = self.pos
        self.pos = 0
        self.data = data

        try:
            if section_id == 1:  # Type section
                count = self._read_leb128_u()
                for _ in range(count):
                    self.type_entries.append(self._read_type_entry())

            elif section_id == 2:  # Import section
                count = self._read_leb128_u()
                for _ in range(count):
                    module = self._read_name()
                    field = self._read_name()
                    kind_byte = self.data[self.pos]
                    self.pos += 1
                    kind = IMPORT_KINDS.get(kind_byte, f"unknown(0x{kind_byte:02X})")
                    imp: Dict[str, Any] = {
                        "module": module,
                        "field": field,
                        "kind": kind,
                    }
                    if kind == "func":
                        imp["type_index"] = self._read_leb128_u()
                    elif kind == "table":
                        imp["elem_type"] = self._read_val_type()
                        imp["limits"] = self._read_limits()
                    elif kind == "mem":
                        imp["limits"] = self._read_limits()
                    elif kind == "global":
                        imp["val_type"] = self._read_val_type()
                        imp["mutability"] = "mutable" if self.data[self.pos] else "immutable"
                        self.pos += 1
                    self.imports.append(imp)

            elif section_id == 3:  # Function section
                count = self._read_leb128_u()
                for _ in range(count):
                    self.functions.append({"type_index": self._read_leb128_u()})

            elif section_id == 4:  # Table section
                count = self._read_leb128_u()
                for _ in range(count):
                    elem_type = self._read_val_type()
                    limits = self._read_limits()
                    self.tables.append({"elem_type": elem_type, "limits": limits})

            elif section_id == 5:  # Memory section
                count = self._read_leb128_u()
                for _ in range(count):
                    self.memories.append(self._read_limits())

            elif section_id == 6:  # Global section
                count = self._read_leb128_u()
                for _ in range(count):
                    val_type = self._read_val_type()
                    mutability = "mutable" if self.data[self.pos] else "immutable"
                    self.pos += 1
                    self.globals.append({
                        "val_type": val_type,
                        "mutability": mutability,
                    })

            elif section_id == 7:  # Export section
                count = self._read_leb128_u()
                for _ in range(count):
                    field = self._read_name()
                    kind_byte = self.data[self.pos]
                    self.pos += 1
                    kind = IMPORT_KINDS.get(kind_byte, f"unknown(0x{kind_byte:02X})")
                    index = self._read_leb128_u()
                    self.exports.append({
                        "field": field,
                        "kind": kind,
                        "index": index,
                    })

        finally:
            self.pos = old_pos
            self.data = b""

    def get_function_signature(self, type_index: int) -> str:
        if type_index < len(self.type_entries):
            entry = self.type_entries[type_index]
            params = ", ".join(entry["params"])
            results = " -> ".join(entry["results"]) if entry["results"] else "void"
            return f"({params}) -> {results}"
        return f"(type_index={type_index})"

    def display_info(self) -> None:
        """Display parsed WASM information."""
        print(f"{Fore.CYAN}File Size: {len(self.data)} bytes{Style.RESET_ALL}")

        if self.type_entries:
            print(f"\n{Fore.GREEN}Type Entries ({len(self.type_entries)}):{Style.RESET_ALL}")
            for i, t in enumerate(self.type_entries):
                sig = self.get_function_signature(i)
                print(f"  [{i}] {sig}")

        if self.imports:
            print(f"\n{Fore.YELLOW}Imports ({len(self.imports)}):{Style.RESET_ALL}")
            for imp in self.imports:
                kind = imp["kind"]
                if kind == "func":
                    sig = self.get_function_signature(imp["type_index"])
                    print(f"  func {imp['module']}.{imp['field']}{sig}")
                elif kind == "mem":
                    lim = imp["limits"]
                    max_str = f", max={lim['max']}" if lim['max'] is not None else ""
                    print(f"  mem  {imp['module']}.{imp['field']} "
                          f"min={lim['min']}{max_str}")
                elif kind == "table":
                    lim = imp["limits"]
                    print(f"  table {imp['module']}.{imp['field']} "
                          f"({imp.get('elem_type', '?')}) "
                          f"min={lim['min']}")
                elif kind == "global":
                    print(f"  global {imp['module']}.{imp['field']} "
                          f"({imp.get('val_type', '?')}, {imp.get('mutability', '?')})")

        if self.exports:
            print(f"\n{Fore.BLUE}Exports ({len(self.exports)}):{Style.RESET_ALL}")
            for exp in self.exports:
                kind = exp["kind"]
                idx = exp["index"]
                if kind == "func":
                    sig = "?"
                    type_idx = idx
                    if idx < len(self.functions):
                        type_idx = self.functions[idx]["type_index"]
                    sig = self.get_function_signature(type_idx)
                    print(f"  func    {exp['field']} [{idx}]{sig}")
                elif kind == "mem":
                    print(f"  memory  {exp['field']} [{idx}]")
                elif kind == "table":
                    print(f"  table   {exp['field']} [{idx}]")
                elif kind == "global":
                    print(f"  global  {exp['field']} [{idx}]")

        if self.functions:
            import_count = sum(1 for i in self.imports if i["kind"] == "func")
            print(f"\n{Fore.MAGENTA}Functions: {len(self.functions)} defined, "
                  f"{import_count} imported{Style.RESET_ALL}")

        if self.tables:
            print(f"\n{Fore.CYAN}Table Sections ({len(self.tables)}):{Style.RESET_ALL}")
            for t in self.tables:
                max_str = f", max={t['limits']['max']}" if t['limits']['max'] is not None else ""
                print(f"  {t['elem_type']} min={t['limits']['min']}{max_str}")

        if self.memories:
            print(f"\n{Fore.CYAN}Memory Sections ({len(self.memories)}):{Style.RESET_ALL}")
            for m in self.memories:
                max_str = f", max={m['max']}" if m['max'] is not None else ""
                print(f"  initial={m['min']} pages{max_str}")

        if self.globals:
            print(f"\n{Fore.CYAN}Globals ({len(self.globals)}):{Style.RESET_ALL}")
            for g in self.globals:
                print(f"  {g['val_type']} ({g['mutability']})")


def load_wasm(source: str) -> Optional[bytes]:
    """Load WASM data from file path or URL."""
    if source.startswith(("http://", "https://", "ftp://")):
        try:
            resp = requests.get(source, timeout=30, headers={
                "User-Agent": "WASMReverseEngineeringTool/1.0",
            })
            if resp.status_code == 200:
                print(f"  {Fore.GREEN}[+] Fetched {len(resp.content)} bytes from URL"
                      f"{Style.RESET_ALL}")
                return resp.content
            else:
                print(f"  {Fore.RED}[!] HTTP {resp.status_code} fetching URL"
                      f"{Style.RESET_ALL}")
        except requests.exceptions.RequestException as e:
            print(f"  {Fore.RED}[!] Request error: {e}{Style.RESET_ALL}")
        return None
    else:
        try:
            with open(source, "rb") as f:
                data = f.read()
            print(f"  {Fore.GREEN}[+] Loaded {len(data)} bytes from {source}"
                  f"{Style.RESET_ALL}")
            return data
        except IOError as e:
            print(f"  {Fore.RED}[!] File error: {e}{Style.RESET_ALL}")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="WebAssembly Reverse Engineering Tool - Parse WASM binaries "
                    "and extract imports, exports, and function signatures",
        epilog="MITRE ATT&CK: T1595 (Active Scanning), T1203 (Exploitation for "
               "Client Execution)"
    )
    parser.add_argument("-f", "--file", required=True,
                        help="Path to .wasm file or URL to fetch")
    parser.add_argument("--dump-functions", action="store_true",
                        help="Dump all function signatures with indices")
    parser.add_argument("--dump-imports", action="store_true",
                        help="Dump detailed import information")
    parser.add_argument("--dump-exports", action="store_true",
                        help="Dump detailed export information")
    args = parser.parse_args()

    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  WebAssembly Reverse Engineering Tool{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  Source: {args.file}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")

    data = load_wasm(args.file)
    if data is None:
        sys.exit(1)
    if not RUNNING:
        sys.exit(0)

    parser_inst = WASMParser(data)
    if not parser_inst.parse():
        print(f"{Fore.RED}[!] Parse failed: {parser_inst.error}{Style.RESET_ALL}")
        sys.exit(1)

    parser_inst.display_info()

    if args.dump_imports or args.dump_exports or args.dump_functions:
        if args.dump_imports and parser_inst.imports:
            print(f"\n{Fore.YELLOW}{'='*50}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  Full Import Dump{Style.RESET_ALL}")
            for i, imp in enumerate(parser_inst.imports):
                print(f"  [{i}] {imp}")

        if args.dump_functions and parser_inst.functions:
            print(f"\n{Fore.MAGENTA}{'='*50}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}  Function Index -> Type Index{Style.RESET_ALL}")
            for i, fn in enumerate(parser_inst.functions):
                ti = fn["type_index"]
                sig = parser_inst.get_function_signature(ti)
                print(f"  func[{i}] -> type[{ti}] {sig}")

        if args.dump_exports and parser_inst.exports:
            print(f"\n{Fore.BLUE}{'='*50}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}  Full Export Dump{Style.RESET_ALL}")
            for exp in parser_inst.exports:
                print(f"  {exp}")

    print(f"\n{Fore.GREEN}[+] Analysis complete{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
