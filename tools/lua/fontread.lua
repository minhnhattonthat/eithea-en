-- Log distinct PCs that read the KANJI.BIN glyph buffer (0x80118000..+0x14100) once frame >= START_AT.
-- Needs emu.py --debugger (interpreter).
local seen = {}
L.on_read(0x80118000, 0x8012c000, function(addr, width)
  local pc = L.pc()
  local k = string.format("%08x", pc)
  if not seen[k] then seen[k] = true; L.log(string.format("read pc=%s addr=%08x w=%d frame=%d", k, addr, width, L.frame)) end
end)
L.on_frame(function(n) L.frame = n end)
