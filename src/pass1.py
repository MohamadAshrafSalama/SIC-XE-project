"""
Pass 1 of the SIC/XE two-pass assembler.

Responsibilities:
- Assign addresses to all statements (location counter)
- Build the symbol table (SYMTAB)
- Detect duplicate symbol definitions
- Calculate program length
"""

from .opcodes import get_format, is_directive, DIRECTIVES
from .utils import parse_line, byte_length


class AssemblyError(Exception):
    """Custom exception for assembly errors with line number context."""
    def __init__(self, message, line_num=None):
        self.line_num = line_num
        if line_num:
            super().__init__(f"Line {line_num}: {message}")
        else:
            super().__init__(message)


class SymbolTable:
    """
    Symbol table for the assembler.

    Stores label -> address mappings. Duplicate definitions
    raise an error since SIC/XE does not allow redefinition.
    """

    def __init__(self):
        self.symbols = {}

    def insert(self, label, address):
        """Insert a symbol. Raises AssemblyError on duplicate."""
        if label in self.symbols:
            raise AssemblyError(f"Duplicate symbol: {label}")
        self.symbols[label] = address

    def lookup(self, label):
        """Look up a symbol address. Returns None if not found."""
        return self.symbols.get(label)

    def contains(self, label):
        """Check if a symbol exists in the table."""
        return label in self.symbols

    def items(self):
        """Return all symbol-address pairs."""
        return self.symbols.items()


def pass1(source_lines):
    """
    Perform pass 1 of the assembler.

    Args:
        source_lines: list of source code lines

    Returns:
        symtab: SymbolTable with all symbols and their addresses
        intermediate: list of dicts with parsed line info + assigned addresses
        program_name: name from START directive
        start_address: starting address from START
        program_length: total program length in bytes
    """
    symtab = SymbolTable()
    intermediate = []
    locctr = 0
    start_address = 0
    program_name = ''

    line_num = 0

    for line in source_lines:
        line_num += 1
        parsed = parse_line(line)

        # Skip blank/comment lines
        if parsed['mnemonic'] is None:
            if parsed['is_comment']:
                intermediate.append({
                    'address': None,
                    'label': None,
                    'mnemonic': None,
                    'operand': None,
                    'is_comment': True,
                    'source': line.rstrip('\n'),
                })
            continue

        label = parsed['label']
        mnemonic = parsed['mnemonic']
        operand = parsed['operand']

        # Handle START directive
        if mnemonic == 'START':
            start_address = int(operand, 16) if operand else 0
            locctr = start_address
            program_name = label if label else ''
            if label:
                symtab.insert(label, locctr)
            intermediate.append({
                'address': locctr,
                'label': label,
                'mnemonic': mnemonic,
                'operand': operand,
                'is_comment': False,
                'source': line.rstrip('\n'),
            })
            continue

        # Record current address for this statement
        current_address = locctr

        # Handle END
        if mnemonic == 'END':
            intermediate.append({
                'address': current_address,
                'label': label,
                'mnemonic': mnemonic,
                'operand': operand,
                'is_comment': False,
                'source': line.rstrip('\n'),
            })
            break

        # Add label to symbol table
        if label:
            if mnemonic == 'EQU':
                if operand == '*':
                    symtab.insert(label, locctr)
                else:
                    value = _evaluate_expression(operand, symtab)
                    symtab.insert(label, value)
            else:
                symtab.insert(label, locctr)

        # Build intermediate record
        intermediate.append({
            'address': current_address,
            'label': label,
            'mnemonic': mnemonic,
            'operand': operand,
            'is_comment': False,
            'source': line.rstrip('\n'),
        })

        # Advance location counter
        if mnemonic == 'EQU':
            pass  # EQU does not advance LOCCTR
        elif mnemonic == 'ORG':
            # ORG resets the location counter to the specified value
            if operand == '*':
                pass  # ORG * does nothing special here
            else:
                locctr = _evaluate_expression(operand, symtab)
        elif mnemonic == 'BASE' or mnemonic == 'NOBASE':
            pass  # Directives that don't occupy memory
        elif mnemonic == 'RESW':
            locctr += int(operand) * 3
        elif mnemonic == 'RESB':
            locctr += int(operand)
        elif mnemonic == 'WORD':
            locctr += 3
        elif mnemonic == 'BYTE':
            locctr += byte_length(operand)
        else:
            # Machine instruction
            fmt = get_format(mnemonic)
            if fmt is None:
                raise AssemblyError(f"Unknown instruction '{mnemonic}'", line_num)
            locctr += fmt

    program_length = locctr - start_address
    return symtab, intermediate, program_name, start_address, program_length


def _evaluate_expression(expr, symtab):
    """
    Evaluate a simple expression for EQU directives.
    Supports symbol+symbol, symbol-symbol, or a single symbol/number.
    """
    if '+' in expr:
        parts = expr.split('+')
        left = _resolve_value(parts[0].strip(), symtab)
        right = _resolve_value(parts[1].strip(), symtab)
        return left + right
    elif '-' in expr:
        parts = expr.split('-')
        left = _resolve_value(parts[0].strip(), symtab)
        right = _resolve_value(parts[1].strip(), symtab)
        return left - right
    else:
        return _resolve_value(expr, symtab)


def _resolve_value(token, symtab):
    """Resolve a token to a numeric value (either a symbol or a literal number)."""
    addr = symtab.lookup(token)
    if addr is not None:
        return addr
    try:
        return int(token)
    except ValueError:
        try:
            return int(token, 16)
        except ValueError:
            raise ValueError(f"Undefined symbol or invalid value: {token}")
