-- Log the distinct PCs that read SPU registers (0x1f801c00..0x1f801dff) after frame START_AT. Needs emu.py --debugger.
local seen, n = {}, 0
L.on_read(0x1f801c00, 0x1f801dff, function(addr, width)
  if L.frame < (START_AT or 0) then return end
  local pc = L.pc()
  local k = string.format("%08x@%08x", pc, addr)
  if not seen[k] then seen[k] = true; L.log("spu read pc=" .. k) end
end)
L.on_frame(function(n) L.frame = n end)
