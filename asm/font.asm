; English text: every 2-byte code with lead >= 0x88 is a PAIR of half-width (6 px) characters.
; tools/font.py encodes pairs, builds the half-width font and prepends it (plus this ext code) to KANJI.IN.
; Assemble: tools/armips/armips.exe asm/font.asm -root <dir with EITHEA.EXE> -strequ CODEOUT "fontext.bin"
.psx

; offsets inside KANJI.IN (must match tools/font.py)
HWOFF   equ 0          ; 106 half glyphs x 24 bytes (1 byte per row per plane, pixels in bits 7..3)
SCROFF  equ 106*24     ; 48-byte scratch glyph
CODEOFF equ SCROFF+48  ; ext code below
MAGICOFF equ (94*24)   ; first unused half-glyph slot holds the "EXT1" marker
PADIDX  equ (0x5e-0x20)  ; slot of the invisible PAD character ('^'), see tools/font.py (equ is textual: keep the parentheses)

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

; ---- EXE stubs. Region 0x800627f0..0x8006294f held the bodies of the battle party-name switch (see below);
; they are rewritten here as three small trampolines into the ext code (the ext code is at KANJI.IN + CODEOFF;
; its base pointer is at 0x800e6e54).
; 1) battle "<name>, choose a command!": the switch at 0x800627d0 copied each party name with a fixed-length inline
;    copy of the Japanese string. All six cases now run namesw (ext): exact NUL-terminated English names.
.org 0x800192D8                 ; the switch's jump table: every case -> the same stub
    .word 0x800627F0, 0x800627F0, 0x800627F0, 0x800627F0, 0x800627F0, 0x800627F0
.org 0x800627F0                 ; entered with jr; v1 = &table[case], s0 = destination
    lui   a1, 0x8002
    addiu a1, a1, -0x6d28       ; 0x800192d8
    subu  v1, v1, a1            ; case * 4
    lui   v0, 0x800e
    lw    v0, 0x6e54(v0)
    nop                         ; load delay
    addiu v0, v0, CODEOFF+namesw
    jr    v0
    nop
; 2) strcat (0x8006b2ec): merge an odd-length (PAD-ended) string with the piece appended to it
strcat_tramp:                   ; strcat runs during start-up too, when 0x800e6e54 still holds stale data from the
    lui   t0, 0x800e            ; previous program: only enter the ext code if the pointer is sane AND the block
    lw    t0, 0x6e54(t0)        ; carries the "EXT1" marker (an unused glyph slot, see tools/font.py)
    lui   t1, 0x8010
    sltu  t2, t0, t1            ; below 0x80100000?
    bnez  t2, strcat_orig
    lui   t1, 0x801f
    sltu  t2, t0, t1            ; at/above 0x801f0000?
    beqz  t2, strcat_orig
    andi  t2, t0, 3             ; unaligned?
    bnez  t2, strcat_orig
    nop
    lw    t2, MAGICOFF(t0)
    lui   t3, 0x3154
    ori   t3, t3, 0x5845        ; "EXT1"
    bne   t2, t3, strcat_orig
    nop
    addiu t0, t0, CODEOFF+strcat_hook
    jr    t0
    nop
strcat_orig:                    ; the two instructions overwritten at the strcat entry
    addiu sp, sp, -0x20
    sw    s1, 0x14(sp)
    j     0x8006b2f4
    nop
; 3) script command pad_flag N,MASK (replaces the unused bast_off): flag[N] = ((pad & MASK) == MASK)
padflag_tramp:
    lui   v0, 0x800e
    lw    v0, 0x6e54(v0)
    nop                         ; load delay
    addiu v0, v0, CODEOFF+padflag
    jr    v0
    nop

.org 0x8006B2EC                 ; strcat entry
    j     strcat_tramp
    nop
.org 0x8002C250                 ; handler of command 4 (was bast_off)
    j     padflag_tramp
    nop
.org 0x80010E00                 ; its name string (same length as "bast_off")
    .ascii "pad_flag"
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

; ---- battle party names. in: v1 = case*4, s0 = destination. Names are 8-byte slots, written by tools/font.py:
; Shou Yuka Hikaru Akiho Lou Imul Hermie (case 5 is Imul or Hermie by the byte at 0x8009d7e1, as in the original).
namesw:
    sll   v1, v1, 1             ; case * 8
    addiu t0, zero, 40
    bne   v1, t0, @@go
    nop
    lui   t1, 0x800a
    lbu   t1, -0x281f(t1)
    nop                         ; load delay
    bnez  t1, @@go
    nop
    addiu v1, v1, 8             ; Hermie
@@go:
    bal   @@b
    nop
@@b:
    addiu a2, ra, names-@@b
    addu  a2, a2, v1
@@copy:
    lbu   v0, 0(a2)
    addiu a2, a2, 1
    sb    v0, 0(s0)
    bnez  v0, @@copy
    addiu s0, s0, 1
    lui   v0, 0x8006
    addiu v0, v0, 0x29a4
    jr    v0                    ; back to the switch epilogue
    nop

; ---- pad_flag N,MASK. flag array at 0x8009d458 (byte per flag), pad held state at 0x8009d454
; (PAD_L2 1, R2 2, L1 4, R1 8, TRIANGLE 0x10, CIRCLE 0x20, CROSS 0x40, SQUARE 0x80, SELECT 0x100, START 0x800).
padflag:
    jal   0x8002b168            ; next integer argument
    nop
    move  s1, v0                ; flag number
    jal   0x8002b168
    nop
    move  s2, v0                ; mask
    lui   v1, 0x800a
    lw    v1, -0x2bac(v1)
    nop                         ; load delay
    and   v1, v1, s2
    xor   v1, v1, s2
    sltiu v1, v1, 1             ; 1 when every mask bit is held
    lui   a0, 0x800a
    addiu a0, a0, -0x2ba8
    addu  a0, a0, s1
    sb    v1, 0(a0)
    j     0x8002e514            ; end of the command dispatcher
    nop

; ---- strcat hook. a0 = dest, a1 = src; returns dest. Only acts when dest ends with a PAD code (c, PAD) and src is
; made of pair codes: the pad is dropped and src is re-paired one character earlier, so "Doggy" + " defeated!"
; reads "Doggy defeated!" (one space) whatever the parity of the name. Anything else: the original strcat.
strcat_hook:
    move  t9, ra
    beqz  a0, sh_fb
    nop
    beqz  a1, sh_fb
    nop
    move  t0, a0                ; find the end of dest
sh_end:
    lbu   v0, 0(t0)
    nop
    bnez  v0, sh_end
    addiu t0, t0, 1
    addiu t0, t0, -1            ; t0 = &NUL
    subu  v0, t0, a0
    sltiu v1, v0, 2
    bnez  v1, sh_fb             ; shorter than one code
    andi  v1, v0, 1
    bnez  v1, sh_fb             ; odd length: not a stream of pair codes
    nop
    lbu   t1, -2(t0)            ; last code
    lbu   t2, -1(t0)
    sltiu v1, t1, 0x88
    bnez  v1, sh_fb
    nop
    bal   decode                ; t7 = first char, t8 = second char of that code
    nop
    addiu v1, t8, -PADIDX
    bnez  v1, sh_fb             ; second char isn't PAD
    nop
    move  t4, t7                ; pending char = the name's last letter
    move  t6, a1                ; check that src is all pair codes
sh_val:
    lbu   v0, 0(t6)
    nop
    beqz  v0, sh_ok
    sltiu v1, v0, 0x88
    bnez  v1, sh_fb
    nop
    lbu   v0, 1(t6)
    nop
    beqz  v0, sh_fb             ; odd byte count
    nop
    b     sh_val
    addiu t6, t6, 2
sh_ok:
    move  t6, a1
    addiu a2, t0, -2            ; overwrite the name's last code
sh_loop:
    lbu   t1, 0(t6)
    nop
    beqz  t1, sh_done
    nop
    lbu   t2, 1(t6)
    addiu t6, t6, 2
    bal   decode                ; t7 = src first char, t8 = src second char
    nop
    move  t3, t8                ; keep: second char of this src code
    move  t8, t7                ; emit (pending, src first)
    move  t7, t4
    bal   encode
    nop
    b     sh_loop
    move  t4, t3                ; pending = src second
sh_done:
    addiu v0, t4, -PADIDX
    beqz  v0, sh_term           ; ends on a pad: nothing left to place
    nop
    move  t7, t4                ; odd tail: (pending, PAD)
    addiu t8, zero, PADIDX
    bal   encode
    nop
sh_term:
    sb    zero, 0(a2)
    jr    t9
    move  v0, a0
sh_fb:                          ; the original strcat (its first two instructions were replaced by the trampoline)
    move  ra, t9
    addiu sp, sp, -0x20
    sw    s1, 0x14(sp)
    lui   v0, 0x8006
    ori   v0, v0, 0xb2f4        ; ori: addiu would sign-extend to 0x8005b2f4
    jr    v0
    nop

; decode: t1 = lead, t2 = trail -> t7 = first char index, t8 = second char index (0..93). clobbers v1.
decode:
    addiu t8, t2, -0x40
    sltiu v1, t2, 0x80
    bnez  v1, @@t
    nop
    addiu t8, t8, -1
@@t:
    addiu t7, t1, -0x88
    sltiu v1, t1, 0xe0
    bnez  v1, @@l
    nop
    addiu t7, t7, -0x40
@@l:
    sll   t7, t7, 1
    sltiu v1, t8, 94
    bnez  v1, @@h
    nop
    addiu t8, t8, -94
    addiu t7, t7, 1
@@h:
    jr    ra
    nop

; encode: t7 = first char index, t8 = second char index -> 2 bytes at a2, a2 += 2. clobbers v0 v1 t8.
encode:
    srl   v0, t7, 1
    addiu v0, v0, 0x88
    sltiu v1, v0, 0xa0
    bnez  v1, @@l
    nop
    addiu v0, v0, 0x40
@@l:
    sb    v0, 0(a2)
    andi  v1, t7, 1
    beqz  v1, @@b
    nop
    addiu t8, t8, 94
@@b:
    addiu v0, t8, 0x40
    sltiu v1, v0, 0x7f
    bnez  v1, @@t
    nop
    addiu v0, v0, 1
@@t:
    sb    v0, 1(a2)
    jr    ra
    addiu a2, a2, 2

names:                          ; 7 slots x 8 bytes, patched by tools/font.py (must stay last)
    .fill 56, 0
.close
