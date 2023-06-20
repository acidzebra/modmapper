# User-configurable variables, defaults should be fine

# split into multiple web pages- good for very big modlists
splitpages = True

# produces a LOT of noise if turned on (pipe output to a file)
moreinfo = False

# normally modmapper cleans up after itself, set to False to disable (for repeated runs for instance)
deletemodjson = False

# some padding around the map
tableborder = 2

# whether the TR landmass colors should override other landmass colors (other overlapping mods will be seen as a brightening of the colors), defaults to true because the alternative is a clown car of a map (bit arguably better to see conflicts there)
overridetr = True

# skip these mods if found. You can add any mods you don't want on the map here.
excludelist = ["autoclean_cities_vanilla.esp","autoclean_cities_TR.ESP","Cyrodiil_Grass.ESP","Sky_Main_Grass.esp","TR_Data.esm","Tamriel_Data.esm","Better Heads Bloodmoon addon.esm","Better Heads Tribunal addon.esm","Better Heads.esm","OAAB_Data.esm","Better Clothes_v1.1.esp","Better Bodies.esp"]

#  Map color control settings, not really fiddled with this beyond making them available
# controls coloring for cells, min value 0 max value should be less than maxbrightness, default 10
minbrightness = 15

# sensible values between ~100 and 200, min is a value above minbrightness, max 255. No checks or guard rails. Lower values produce more muted colors, default 200
maxbrightness = 180

# improve contrast for cells with few mods affecting them (only for mods, not base game)
lowmodcountcontrastincrease = True

# what is considered a "low mod count"
lowmodcount = 10

# controls the increase of values between steps (somewhat), values between 0-1 make the most sense, not really tested beyond that, default 1
stepmodifier = 1

# background and text color
bgcolor = "101010"
txcolor = "808080"

# water/untouched cell color in web/hex RGB
watercolor = "2B65EC"
watertextcolor = "1010ff"

# color overrides, can add your own here or change colors, just copy one of the earlier lines, color format is "modname":"web/hex RGB". CASE sEnSItIvE.
coloroverride = {}
coloroverride.update({"Morrowind.esm":"002000"})
coloroverride.update({"TR_Mainland.esm":"000040"})
coloroverride.update({"TR_Restexteriors.ESP":"400000"})
coloroverride.update({"Bloodmoon.esm":"003030"})
coloroverride.update({"Solstheim Tomb of The Snow Prince.esm":"300030"})
coloroverride.update({"Cyr_Main.esm":"909000"})
coloroverride.update({"Sky_Main.esm":"001060"})
# ---
