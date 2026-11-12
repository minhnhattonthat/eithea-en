-- Text coverage probe: log the script interpreter's position each time it changes (no --debugger needed).
-- RAM: 0x8009b948 current script name ("IVENT04.TXT"), script buffer 0x8012e000, read offsets 0x80094914/18.
-- Log line: "POS <name> <off14> <off18>" (hex offsets into the script buffer). tools/debug/cover.py maps them to rows.
local mem = PCSX.getMemPtr()
local function u32(a) a = a & 0x1fffff; return mem[a] | (mem[a+1] << 8) | (mem[a+2] << 16) | (mem[a+3] << 24) end
local function name()
  local s = {}
  for i = 0, 15 do
    local c = mem[0x9b948 + i]
    if c == 0 then break end
    s[#s+1] = string.char(c)
  end
  return table.concat(s)
end
local last = ""
L.on_frame(function(n)
  local k = string.format("POS %s %x %x", name(), u32(0x80094914), u32(0x80094918))
  if k ~= last then last = k; L.log(k .. " f" .. n) end
end)
