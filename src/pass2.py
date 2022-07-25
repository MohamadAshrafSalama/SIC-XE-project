"""
Pass 2 of the SIC/XE two-pass assembler.

Responsibilities:
- Generate object code for each instruction
- Handle all addressing modes (immediate, indirect, indexed, PC-relative, base-relative)
- Produce H, T, E, and M records for the object program
"""

from .opcodes import get_opcode, get_format, REGISTERS
from .utils import hex_str, parse_byte_operand, parse_operand


def pass2(symtab, intermediate, program_name, start_address, program_length):
    """
    Perform pass 2 of the assembler.

    Returns:
        object_code: list of (address, hex_string) tuples for each instruction
        records: dict with 'H', 'T', 'E', 'M' record strings
        listing: list of dicts with full listing info
    """
    object_code = []
    modification_records = []
    listing = []
    base_register = None

    for i, entry in enumerate(intermediate):
        if entry['is_comment']:
            listing.append({
                'address': '',
                'label': '',
                'mnemonic': '',
                'operand': '',
                'object_code': '',
                'source': entry['source'],
            })
            continue

        mnemonic = entry['mnemonic']
        operand = entry['operand']
        address = entry['address']
        label = entry['label'] if entry['label'] else ''

        obj = ''

        if mnemonic == 'START' or mnemonic == 'END':
            pass

        elif mnemonic == 'BASE':
            # Set base register for base-relative addressing
            if operand:
                base_register = symtab.lookup(operand)
            obj = ''

        elif mnemonic == 'NOBASE':
            base_register = None
            obj = ''

        elif mnemonic == 'EQU' or mnemonic == 'ORG':
            obj = ''

        elif mnemonic == 'BYTE':
            obj = parse_byte_operand(operand)

        elif mnemonic == 'WORD':
            val = int(operand)
            obj = hex_str(val, 6)

        elif mnemonic == 'RESW' or mnemonic == 'RESB':
            obj = ''

        else:
            # Machine instruction
            fmt = get_format(mnemonic)
            clean_mnemonic = mnemonic.lstrip('+')
            opcode_val, _ = get_opcode(clean_mnemonic)

            if fmt == 1:
                obj = hex_str(opcode_val, 2)

            elif fmt == 2:
                obj = _generate_format2(opcode_val, operand)

            elif fmt == 3:
                # Get next instruction address for PC-relative
                pc = _get_next_address(intermediate, i)
                obj = _generate_format3(
                    opcode_val, operand, symtab, pc, base_register
                )

            elif fmt == 4:
                obj = _generate_format4(opcode_val, operand, symtab)
                # Format 4 with relocatable addresses needs modification records.
                # Immediate values (#) that are constants don't need relocation,
                # but immediate references to symbols do.
                if operand:
                    _, addr_flags = parse_operand(operand)
                    symbol_name = operand.lstrip('#@').replace(',X', '')
                    is_constant = symbol_name.isdigit()
                    if not is_constant:
                        mod_addr = address + 1
                        modification_records.append(
                            f"M{hex_str(mod_addr, 6)}05"
                        )

        object_code.append((address, obj))
        listing.append({
            'address': hex_str(address, 6) if address is not None else '',
            'label': label,
            'mnemonic': mnemonic if mnemonic else '',
            'operand': operand if operand else '',
            'object_code': obj,
            'source': entry['source'],
        })

    # Generate records
    records = _generate_records(
        program_name, start_address, program_length,
        object_code, modification_records, intermediate
    )

    return object_code, records, listing


def _get_next_address(intermediate, current_index):
    """Get the address of the next executable statement (PC value after current)."""
    for j in range(current_index + 1, len(intermediate)):
        if not intermediate[j]['is_comment'] and intermediate[j]['address'] is not None:
            return intermediate[j]['address']
    return 0


def _generate_format2(opcode_val, operand):
    """Generate object code for format 2 instructions."""
    parts = operand.split(',') if operand else ['']
    r1 = REGISTERS.get(parts[0].strip(), 0)
    r2 = REGISTERS.get(parts[1].strip(), 0) if len(parts) > 1 else 0
    return hex_str(opcode_val, 2) + format(r1, '1X') + format(r2, '1X')


def _generate_format3(opcode_val, operand, symtab, pc, base_register):
    """
    Generate object code for format 3 instructions.

    Uses PC-relative addressing first, falls back to base-relative.
    """
    symbol, flags = parse_operand(operand)

    # Determine n, i bits
    if flags['immediate']:
        n, i = 0, 1
    elif flags['indirect']:
        n, i = 1, 0
    else:
        n, i = 1, 1  # simple/direct addressing

    x = 1 if flags['indexed'] else 0
    b, p, e = 0, 0, 0  # e=0 for format 3

    # RSUB has no operand
    if mnemonic_is_rsub(opcode_val):
        disp = 0
        first_byte = (opcode_val & 0xFC) | (n << 1) | i
        second_half = (x << 15) | (b << 14) | (p << 13) | (e << 12) | (disp & 0xFFF)
        return hex_str(first_byte, 2) + hex_str(second_half, 4)

    # Resolve target address
    if symbol is None:
        target = 0
    elif symbol.isdigit() or (symbol.startswith('-') and symbol[1:].isdigit()):
        # Immediate numeric value
        target = int(symbol)
        disp = target
        # No PC or base relative for immediate constants
        first_byte = (opcode_val & 0xFC) | (n << 1) | i
        second_half = (x << 15) | (b << 14) | (p << 13) | (e << 12) | (disp & 0xFFF)
        return hex_str(first_byte, 2) + hex_str(second_half, 4)
    else:
        target = symtab.lookup(symbol)
        if target is None:
            raise ValueError(f"Undefined symbol: {symbol}")

    # Try PC-relative first (disp must fit in 12 bits signed: -2048 to 2047)
    disp = target - pc
    if -2048 <= disp <= 2047:
        p = 1
        disp = disp & 0xFFF
    elif base_register is not None:
        # Try base-relative (disp must be 0-4095)
        disp = target - base_register
        if 0 <= disp <= 4095:
            b = 1
            p = 0
        else:
            raise ValueError(
                f"Cannot compute displacement for target {target:#X}, "
                f"PC={pc:#X}, BASE={base_register:#X}"
            )
    else:
        raise ValueError(
            f"Cannot compute displacement for target {target:#X}, PC={pc:#X}. "
            f"No BASE register set."
        )

    first_byte = (opcode_val & 0xFC) | (n << 1) | i
    second_half = (x << 15) | (b << 14) | (p << 13) | (e << 12) | (disp & 0xFFF)

    return hex_str(first_byte, 2) + hex_str(second_half, 4)


def _generate_format4(opcode_val, operand, symtab):
    """Generate object code for format 4 instructions."""
    symbol, flags = parse_operand(operand)

    if flags['immediate']:
        n, i = 0, 1
    elif flags['indirect']:
        n, i = 1, 0
    else:
        n, i = 1, 1

    x = 1 if flags['indexed'] else 0
    b, p, e = 0, 0, 1  # e=1 for format 4

    # Resolve address
    if symbol is None:
        addr = 0
    elif symbol.isdigit():
        addr = int(symbol)
    else:
        addr = symtab.lookup(symbol)
        if addr is None:
            raise ValueError(f"Undefined symbol: {symbol}")

    first_byte = (opcode_val & 0xFC) | (n << 1) | i
    flags_nibble = (x << 3) | (b << 2) | (p << 1) | e
    second_byte_high = flags_nibble

    # Build full 4-byte instruction
    result = hex_str(first_byte, 2)
    result += format(second_byte_high, '1X')
    result += hex_str(addr, 5)

    return result


def mnemonic_is_rsub(opcode_val):
    """
    Check if an opcode value corresponds to RSUB (0x4C).
    RSUB is special because it has no operand - the return
    address is implicitly in the L register.
    """
    return opcode_val == 0x4C


def _generate_records(program_name, start_address, program_length,
                      object_code, modification_records, intermediate):
    """Generate the complete object program records."""
    records = []

    # Header record
    name = program_name.ljust(6) if program_name else '      '
    h_record = f"H{name}{hex_str(start_address, 6)}{hex_str(program_length, 6)}"
    records.append(h_record)

    # Text records - max 30 bytes (60 hex chars) per record
    text_records = _build_text_records(object_code, intermediate)
    records.extend(text_records)

    # Modification records
    records.extend(modification_records)

    # End record
    e_record = f"E{hex_str(start_address, 6)}"
    records.append(e_record)

    return records


def _build_text_records(object_code, intermediate):
    """
    Build text records from object code.
    Breaks on RESW/RESB gaps and when record exceeds 30 bytes.
    """
    text_records = []
    current_text = ''
    current_start = None
    current_length = 0

    for i, (addr, obj) in enumerate(object_code):
        if not obj:
            # Empty object code (RESW, RESB, directives) - flush current record
            if current_text:
                t_record = f"T{hex_str(current_start, 6)}{hex_str(current_length, 2)}{current_text}"
                text_records.append(t_record)
                current_text = ''
                current_start = None
                current_length = 0
            continue

        obj_bytes = len(obj) // 2

        # Check if adding this would exceed 30 bytes
        if current_length + obj_bytes > 30:
            if current_text:
                t_record = f"T{hex_str(current_start, 6)}{hex_str(current_length, 2)}{current_text}"
                text_records.append(t_record)
            current_text = obj
            current_start = addr
            current_length = obj_bytes
        else:
            if current_start is None:
                current_start = addr
            current_text += obj
            current_length += obj_bytes

    # Flush remaining
    if current_text:
        t_record = f"T{hex_str(current_start, 6)}{hex_str(current_length, 2)}{current_text}"
        text_records.append(t_record)

    return text_records
