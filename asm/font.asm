; English text: every 2-byte code with lead >= 0x88 is a PAIR of half-width (6 px) characters.
; tools/font.py encodes pairs, builds the half-width font and prepends it (plus this ext code) to KANJI.IN.
; Assemble: tools/armips/armips.exe asm/font.asm -root <dir with EITHEA.EXE> -equ CODEOUT "fontext.bin"
.psx

; offsets inside KANJI.IN (must match tools/font.py)
HWOFF   equ 0          ; 106 half glyphs x 24 bytes (1 byte per row per plane, pixels in bits 7..3)
SCROFF  equ 106*24     ; 48-byte scratch glyph
CODEOFF equ SCROFF+48  ; ext code below

; ---- glyph blitter 0x800367d4 (x=a0, y=a1, code=a2, buf=a3): replace the KANJI.BL search ----
.open "EITHEA.EXE", 0x80010000-0x800
.org 0x800367E4
    lui   t3, 0x800e
    lw    t8, 0x20(sp)          ; stride
    lbu   t5, 0x28(sp)          ; colour
    lw    t1, 0x6e54(t3)        ; KANJI.IN base
    lw    a1, 0x6e4c(t3)        ; KANJI.BL base
    andi  a2, a2, 0xffff
    addiu v0, t1, CODEOFF
    move  t4, ra
    jalr  v0                    ; -> t1 = glyph pointer
    nop
    move  ra, t4
    srl   v0, t2, 31
    addu  v0, t2, v0
    sra   t7, v0, 1             ; x/2
    addiu t6, zero, 12
    j     0x80036878
    move  t0, zero
.fill 0x80036878-., 0

; ---- battle "<name>, choose a command!": switch at 0x800627d0 copies each party name with a fixed-length inline
; copy (翔 3 bytes, 秋穂 5 bytes), too short for "Shou"/"Akiho". Cases 0 and 3 now jump to a NUL-terminated copy
; in the ext code (s0 = destination; the epilogue at 0x800629a4 restores s0/ra).
.org 0x800627F0
    lui   v0, 0x800e
    lw    v0, 0x6e54(v0)
    nop                         ; load delay
    addiu v0, v0, CODEOFF+name_shou
    jr    v0
    nop
.fill 0x80062818-., 0
.org 0x8006287C
    lui   v0, 0x800e
    lw    v0, 0x6e54(v0)
    nop                         ; load delay
    addiu v0, v0, CODEOFF+name_akiho
    jr    v0
    nop
.fill 0x800628A4-., 0
.close

; ---- ext code, position independent, lives in KANJI.IN at CODEOFF ----
; in: a2 code, a1 BL, t1 IN base. out: t1 glyph ptr. keeps t2 t4 t5 t8 t9 a3 ra.
.create CODEOUT, 0
ext:
    srl   v1, a2, 8             ; lead (sltiu sign-extends 0x8800, so compare the lead byte)
    sltiu v0, v1, 0x88
    bnez  v0, search
    nop
    andi  a0, a2, 0xff
    addiu a0, a0, -0x40         ; trail index (0x7f skipped)
    sltiu v0, a0, 0x40
    bnez  v0, @@t_ok
    nop
    addiu a0, a0, -1
@@t_ok:
    addiu v1, v1, -0x88         ; lead index (0xa0..0xdf skipped)
    sltiu v0, v1, 24
    bnez  v0, @@l_ok
    nop
    addiu v1, v1, -0x40
@@l_ok:
    sll   v1, v1, 1
    sltiu v0, a0, 94
    bnez  v0, @@h_ok
    nop
    addiu a0, a0, -94
    addiu v1, v1, 1
@@h_ok:                         ; v1 = first char index, a0 = second
    sll   v0, v1, 3
    sll   v1, v1, 4
    addu  v1, v1, v0
    addu  v1, v1, t1            ; + HWOFF (0)
    sll   v0, a0, 3
    sll   a0, a0, 4
    addu  a0, a0, v0
    addu  a0, a0, t1
    addiu t0, t1, SCROFF
    addiu t3, zero, 24
@@loop:                         ; out = A | B >> 6 (big-endian 16-bit rows)
    lbu   v0, 0(v1)
    lbu   a1, 0(a0)
    addiu v1, v1, 1
    addiu a0, a0, 1
    srl   a2, a1, 6
    or    v0, v0, a2
    sll   a1, a1, 2
    sb    v0, 0(t0)
    sb    a1, 1(t0)
    addiu t3, t3, -1
    bnez  t3, @@loop
    addiu t0, t0, 2
    jr    ra
    addiu t1, t1, SCROFF

search:                         ; original linear search of KANJI.BL (0xff ends)
    move  t0, zero
    addiu t3, zero, 0xff
@@s:
    lbu   v0, 0(a1)
    lbu   v1, 1(a1)
    beq   v0, t3, @@done
    sll   v0, v0, 8
    addu  v0, v0, v1
    beq   v0, a2, @@done
    nop
    addiu a1, a1, 2
    b     @@s
    addiu t0, t0, 1
@@done:
    sll   v0, t0, 1
    addu  v0, v0, t0
    sll   v0, v0, 4
    jr    ra
    addu  t1, t1, v0

name_shou:                      ; entered with jr from the EXE stubs above
    bal   @@b0
    nop
@@b0:
    b     namecopy
    addiu a2, ra, str_shou-@@b0
name_akiho:
    bal   @@b1
    nop
@@b1:
    addiu a2, ra, str_akiho-@@b1
namecopy:
    lbu   v0, 0(a2)
    addiu a2, a2, 1
    sb    v0, 0(s0)
    bnez  v0, namecopy
    addiu s0, s0, 1
    lui   v0, 0x8006
    addiu v0, v0, 0x29a4
    jr    v0                    ; back to the switch epilogue
    nop
.align 4
str_shou:                       ; tools/font.py writes the pair-encoded names here (last 16 bytes)
    .fill 8, 0
str_akiho:
    .fill 8, 0
.close
