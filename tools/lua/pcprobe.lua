-- Log the PC every 100 frames; dump main RAM to OUT/ram<frame>.bin at each frame in DUMPS (comma list, e.g.
-- --var DUMPS='"1200,2400"').
local dumps = {}
for f in string.gmatch(DUMPS or "4000", "%d+") do dumps[tonumber(f)] = true end
L.on_frame(function(n)
  if n % 100 == 0 then L.log(string.format("f%d pc=%08x", n, L.pc())) end
  if dumps[n] then L.dump_ram(OUT .. "ram" .. n .. ".bin") end
end)
