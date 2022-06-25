"""
SIC/XE Two-Pass Assembler

Main entry point for the assembler. Reads a source assembly file,
runs both passes, and writes the output files:
  - Symbol table (SYMTAB)
  - Object program (H/T/E/M records)
  - Assembly listing
"""

import argparse
import os
import sys

from .pass1 import pass1
from .pass2 import pass2
from .utils import hex_str


def read_source(filepath):
    """Read source file and return lines."""
    with open(filepath, 'r') as f:
        return f.readlines()


def write_symbol_table(symtab, filepath):
    """Write the symbol table to a file."""
    with open(filepath, 'w') as f:
        f.write(f"{'Symbol':<12} {'Address':>8}\n")
        f.write('-' * 22 + '\n')
        for symbol, address in sorted(symtab.items(), key=lambda x: x[1]):
            f.write(f"{symbol:<12} {hex_str(address, 6):>8}\n")


def write_object_program(records, filepath):
    """Write the object program records to a file."""
    with open(filepath, 'w') as f:
        for record in records:
            f.write(record + '\n')


def write_listing(listing, filepath):
    """Write the assembly listing to a file."""
    with open(filepath, 'w') as f:
        f.write(f"{'Loc':<8} {'Label':<10} {'Mnemonic':<10} {'Operand':<16} {'Object Code':<12}\n")
        f.write('-' * 60 + '\n')
        for entry in listing:
            if entry.get('source', '').startswith('.'):
                f.write(f"{'':8} {entry['source']}\n")
                continue
            f.write(
                f"{entry['address']:<8} "
                f"{entry['label']:<10} "
                f"{entry['mnemonic']:<10} "
                f"{entry['operand']:<16} "
                f"{entry['object_code']:<12}\n"
            )


def assemble(source_path, output_dir=None):
    """
    Run the full two-pass assembly process.

    Args:
        source_path: path to the assembly source file
        output_dir: directory for output files (defaults to ./output/)
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')

    os.makedirs(output_dir, exist_ok=True)

    # Read source
    source_lines = read_source(source_path)
    base_name = os.path.splitext(os.path.basename(source_path))[0]

    print(f"Assembling: {source_path}")

    # Pass 1
    print("Running Pass 1...")
    symtab, intermediate, program_name, start_addr, program_length = pass1(source_lines)
    print(f"  Program: {program_name}")
    print(f"  Start address: {hex_str(start_addr, 6)}")
    print(f"  Program length: {hex_str(program_length, 6)} ({program_length} bytes)")
    print(f"  Symbols defined: {len(list(symtab.items()))}")

    # Pass 2
    print("Running Pass 2...")
    object_code, records, listing = pass2(
        symtab, intermediate, program_name, start_addr, program_length
    )

    # Write outputs
    symtab_path = os.path.join(output_dir, f"{base_name}_symtab.txt")
    object_path = os.path.join(output_dir, f"{base_name}_object.txt")
    listing_path = os.path.join(output_dir, f"{base_name}_listing.txt")

    write_symbol_table(symtab, symtab_path)
    write_object_program(records, object_path)
    write_listing(listing, listing_path)

    print(f"\nOutput files written to {output_dir}/")
    print(f"  Symbol table: {os.path.basename(symtab_path)}")
    print(f"  Object program: {os.path.basename(object_path)}")
    print(f"  Listing: {os.path.basename(listing_path)}")

    return symtab, records, listing


def main():
    parser = argparse.ArgumentParser(
        description='SIC/XE Two-Pass Assembler'
    )
    parser.add_argument(
        'source',
        help='Path to the SIC/XE assembly source file'
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output directory (default: ./output/)'
    )

    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"Error: Source file not found: {args.source}")
        sys.exit(1)

    try:
        assemble(args.source, args.output)
    except Exception as e:
        print(f"Assembly error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
