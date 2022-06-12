"""
Utility functions for the SIC/XE assembler.
"""


def parse_line(line):
    """
    Parse a single line of SIC/XE assembly source code.

    Returns a dict with keys: label, mnemonic, operand, comment, is_comment
    Handles lines with or without labels, and comment lines starting with '.'.
    """
    line = line.rstrip('\n').rstrip()

    if not line or line.startswith('.'):
        return {'label': None, 'mnemonic': None, 'operand': None,
                'comment': line if line.startswith('.') else None,
                'is_comment': bool(line)}

    parts = line.split()
    if len(parts) == 0:
        return {'label': None, 'mnemonic': None, 'operand': None,
                'comment': None, 'is_comment': False}

    # Determine if first token is a label or mnemonic
    # Labels start at column 0 (no leading whitespace)
    # Mnemonics are indented
    has_label = not line[0].isspace()

    if has_label:
        label = parts[0]
        mnemonic = parts[1] if len(parts) > 1 else None
        operand = parts[2] if len(parts) > 2 else None
    else:
        label = None
        mnemonic = parts[0]
        operand = parts[1] if len(parts) > 1 else None

    return {
        'label': label,
        'mnemonic': mnemonic,
        'operand': operand,
        'comment': None,
        'is_comment': False,
    }


def hex_str(value, width):
    """Convert an integer to a zero-padded uppercase hex string of given width."""
    if value < 0:
        # Two's complement for negative values
        value = value & ((1 << (width * 4)) - 1)
    return format(value, f'0{width}X')


def parse_byte_operand(operand):
    """
    Parse a BYTE directive operand like C'EOF' or X'F1'.

    Returns the byte string as hex characters.
    """
    if operand.startswith("C'") and operand.endswith("'"):
        chars = operand[2:-1]
        return ''.join(format(ord(c), '02X') for c in chars)
    elif operand.startswith("X'") and operand.endswith("'"):
        return operand[2:-1].upper()
    else:
        raise ValueError(f"Invalid BYTE operand: {operand}")


def byte_length(operand):
    """Return the number of bytes a BYTE directive occupies."""
    if operand.startswith("C'") and operand.endswith("'"):
        return len(operand[2:-1])
    elif operand.startswith("X'") and operand.endswith("'"):
        hex_chars = operand[2:-1]
        return len(hex_chars) // 2
    else:
        raise ValueError(f"Invalid BYTE operand: {operand}")


def parse_operand(operand):
    """
    Parse an operand string and determine addressing mode.

    Returns: (symbol_or_value, addressing_flags)
    addressing_flags is a dict with keys: immediate, indirect, indexed
    """
    if operand is None:
        return None, {'immediate': False, 'indirect': False, 'indexed': False}

    flags = {'immediate': False, 'indirect': False, 'indexed': False}

    # Check for indexed addressing
    if ',X' in operand:
        flags['indexed'] = True
        operand = operand.replace(',X', '')

    # Check for immediate or indirect
    if operand.startswith('#'):
        flags['immediate'] = True
        operand = operand[1:]
    elif operand.startswith('@'):
        flags['indirect'] = True
        operand = operand[1:]

    return operand, flags
