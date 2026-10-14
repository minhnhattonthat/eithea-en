"""Hidden access to the developer debug menu (DEBUG.XT): hold L1 + R1 while choosing New Game.
START.XT (run by New Game) ends with `change IVENT01.TXT`; the patched script first asks the engine for the pad
(new command pad_flag N,MASK, see asm/font.asm: flag[N] = all MASK bits held) and jumps to DEBUG.TXT when L1+R1 are down.
Pad bits: L2 1, R2 2, L1 4, R1 8, TRIANGLE 0x10, CIRCLE 0x20, CROSS 0x40, SQUARE 0x80, SELECT 0x100, START 0x800.
"""
FLAG = 899        # unused flag (scripts use up to 960; the array is indexed by byte)
LABEL = 99001     # unused label number
MASK = 0x0C       # L1 + R1


def start_script(data):
    old = b"change IVENT01.TXT"
    assert data.count(old) == 1
    new = (f"pad_flag {FLAG},{MASK}\r\nif (flag[{FLAG}] == 1) goto {LABEL}\r\n".encode() + old +
           f"\r\n\r\n*****{LABEL}\r\nchange DEBUG.TXT".encode())
    return data.replace(old, new)
