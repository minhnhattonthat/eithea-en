-- Dump PS1 VRAM (1024x512 16-bit, 1 MB) at given frames: --var DUMP_AT=1530,1620 -> <out>/v<frame>.vram.bin + .ram.bin (2 MB main RAM).
-- Decode with tools/vram.py; find the source with tools/vram.py find.
local at = {}
for n in tostring(DUMP_AT or ""):gmatch("%d+") do at[tonumber(n)] = true end
L.on_frame(function(n)
  if at[n] then L.dump_ppu(string.format("v%06d", n)); L.dump_ram(string.format("v%06d.ram.bin", n)) end
end)
