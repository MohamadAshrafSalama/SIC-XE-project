# SIC/XE Two-Pass Assembler

A Python implementation of a two-pass assembler for the SIC/XE (Simplified Instructional Computer with Extra Equipment) architecture. Built as part of a Systems Programming course at AAST.

## What is SIC/XE?

SIC/XE is an extended version of the SIC architecture, a hypothetical computer system used in systems programming education. It was introduced by Leland Beck in *System Software: An Introduction to Systems Programming* and is widely used to teach assembler, linker, and loader concepts.

SIC/XE extends the basic SIC with:
- Additional registers (B, S, T, F)
- Floating point support
- Multiple instruction formats (1, 2, 3, and 4 bytes)
- Addressing modes: immediate (`#`), indirect (`@`), indexed (`,X`)
- PC-relative and base-relative addressing for format 3
- 20-bit addresses in format 4 for full memory range

## How the Assembler Works

This is a **two-pass assembler**:

### Pass 1
- Reads the source program line by line
- Assigns addresses using the location counter (LOCCTR)
- Builds the **symbol table** (SYMTAB), mapping each label to its assigned address
- Detects duplicate symbol definitions
- Calculates the total program length

### Pass 2
- Translates each instruction into its machine code representation
- Resolves symbol references using the symbol table from Pass 1
- Computes displacement values for format 3 (PC-relative or base-relative)
- Generates the complete object program as H/T/E/M records

## Supported Instructions

### Instruction Formats
| Format | Size | Description |
|--------|------|-------------|
| 1 | 1 byte | Opcode only (e.g., `FIX`, `FLOAT`, `SIO`) |
| 2 | 2 bytes | Opcode + register operands (e.g., `ADDR`, `COMPR`, `CLEAR`) |
| 3 | 3 bytes | Opcode + nixbpe flags + 12-bit displacement |
| 4 | 4 bytes | Opcode + nixbpe flags + 20-bit address (prefix: `+`) |

### Addressing Modes
- **Simple**: `LDA ALPHA` -- direct memory reference
- **Immediate**: `LDA #100` -- operand is the value itself
- **Indirect**: `J @RETADR` -- operand is the address of the target address
- **Indexed**: `LDCH BUFFER,X` -- effective address = operand + X register

### Assembler Directives
| Directive | Description |
|-----------|-------------|
| `START` | Set program name and starting address |
| `END` | Mark end of source, specify first executable instruction |
| `BYTE` | Define byte constant (`C'EOF'` for characters, `X'F1'` for hex) |
| `WORD` | Define one-word (3-byte) integer constant |
| `RESB` | Reserve bytes of memory |
| `RESW` | Reserve words (3 bytes each) of memory |
| `BASE` | Set base register value for base-relative addressing |
| `NOBASE` | Unset the base register |
| `EQU` | Define a symbol with a computed value |
| `ORG` | Reset the location counter |

## Output Format

The assembler produces object program records following the standard SIC/XE format:

### Header Record (H)
```
H<name><start_address><program_length>
```
Example: `HCOPY  001000001077`

### Text Record (T)
```
T<start_address><length><object_code>
```
Contains the actual machine code. Each record holds up to 30 bytes. Records break at `RESW`/`RESB` gaps.

### Modification Record (M)
```
M<address><length>
```
Marks locations in format 4 instructions that need relocation by the loader.

### End Record (E)
```
E<first_executable_address>
```

## Usage

```bash
# Assemble a source file
python -m src tests/test1.asm

# Specify output directory
python -m src tests/test1.asm -o my_output/
```

### Output Files
The assembler generates three files in the output directory:
- `<name>_symtab.txt` -- Symbol table with labels and addresses
- `<name>_object.txt` -- Object program (H/T/E/M records)
- `<name>_listing.txt` -- Full assembly listing with addresses and object code

## Source File Format

Assembly source files use a fixed-column format:
```
LABEL   MNEMONIC   OPERAND
```
- Labels start at column 0 (no leading whitespace)
- Mnemonics are indented with whitespace if no label is present
- Comment lines begin with `.`
- Format 4 instructions are prefixed with `+` (e.g., `+JSUB`)

## Example

Input (`test2.asm`):
```asm
SUM     START   0
        LDA     N
        STA     COUNT
        LDX     #0
        LDA     #0
LOOP    ADD     TABLE,X
        TIX     COUNT
        JLT     LOOP
        STA     TOTAL
        RSUB
N       WORD    5
TABLE   WORD    10
COUNT   RESW    1
TOTAL   RESW    1
        END     SUM
```

Object program output:
```
HSUM   000000000033
T0000001E0320180F20270500000100001BA00F2F201B3B2FF70F20184F0000000005
T00001E0F00000A00001400001E000028000032
E000000
```

## Project Structure

```
SIC-XE-project/
  src/
    __init__.py
    __main__.py
    assembler.py    # main entry point, file I/O
    pass1.py        # first pass: symbol table + addresses
    pass2.py        # second pass: object code generation
    opcodes.py      # opcode table and register mappings
    utils.py        # parsing and formatting helpers
  tests/
    test1.asm       # copy program (format 3/4, subroutines, BASE)
    test2.asm       # summation (basic instructions, indexed addressing)
    test3.asm       # immediate and indirect addressing
  output/           # generated output files
  requirements.txt
  README.md
```

## Requirements

Python 3.6 or higher. No external dependencies -- uses only the standard library.
