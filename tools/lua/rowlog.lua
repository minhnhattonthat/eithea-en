-- Text coverage (QA builds with build.py --qa-cover): log "ROW <script> <row+1> f<frame>" each time flag[990] changes.
-- Flag array = bytes at 0x8009d458; 0x8009b948 = current script name. Read by tools/debug/cover.py.
-- Logged on value change only, so a value left over from the previous script isn't credited to the new one.
local mem = PCSX.getMemPtr()
local CELL = (0x8009d458 + 990) & 0x1fffff
local function name()
  local s = {}
  for i = 0, 15 do
    local c = mem[0x9b948 + i]
    if c == 0 then break end
    s[#s+1] = string.char(c)
  end
  return table.concat(s)
end
local last = 0
L.on_frame(function(n)
  local v = mem[CELL]
  if v ~= last then last = v; L.log(string.format("ROW %s %d f%d", name(), v, n)) end
end)
