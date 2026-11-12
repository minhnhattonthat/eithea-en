-- Probe: log distinct string pointers (a2) passed to the string print routine 0x80036958. Needs emu.py --debugger.
local seen = {}
L.on_exec(0x80036958, function()
  local r = PCSX.getRegisters().GPR.n
  local k = string.format("%08x", r.a2)
  if not seen[k] then seen[k] = true; L.log(string.format("PRINT a2=%s ra=%08x", k, r.ra)) end
end)
