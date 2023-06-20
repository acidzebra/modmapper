# modmapper

DEMO: https://acidzebra.github.io/modmapper/ - currently tracks 2000+ mods and the changes they make to exterior and interior cells.

Nexus: https://www.nexusmods.com/morrowind/mods/53069

Python 3.7+ script for Morrowind to generate a heatmap of exterior cells showing which/how many mods affect each cell. Includes a list of interior cells and what mods alter them. Does not alter game files, generates a single html file with the map + lists you can open in any browser. 

A toy I wrote for myself while working on Lawnmower, it might be of some use if you're trying to find mod conflict areas.

It will examine a folder of mods and build a html file with a map of exterior cells. It will show which mods alter cell with brighter colors meaning more mods affecting that cell. Mouse over a cell to see a tooltip with mods affecting that cell. Click on any cell with yellow text to jump to a list entry for that cell with the mods affecting it. Use [back] function of your browser to return to map. Modmapper will also build a list of interior cells and which mods alter them and add that list to the end of the html file.

Modmapper does not alter any game files, it will read mods in a folder and produce a HTML file called "modmapper.html" in the same folder.

Tested on English-language Windows with English-language game. Might need some altering to run on other OSes.

REQUIREMENTS

- Python 3.7 or later﻿
- tes3conv.exe﻿
- folder of mods


If you use MO2, you will likely have to use VFS explorer or similar tricks; I don't use MO2 so I couldn't tell you what to do.

HOW TO USE

- put modmapper.py + tes3conv.exe in the folder with mods you want to build a map for (this can be your data folder)
- open a command prompt python modmapper.py "path_to_the_folder_you_put_everything_in
- wait 1-2 minutes while modmapper examines all mods, and open the resulting modmapper.html file in a browser.

The wait time is dependent on how many mods it has to inspect, I have ~350 mods and it takes a minute or so. If you want to rerun multiple times, consider setting deletemodjson = False (open modmapper.py with a text editor)

INTERPRETING THE MAP
After opening modmapper.html you will see some program info and the start of the map.
Examined 334 files, skipped 4 files on the exclude list. Failed to convert 0 mods
Mods on the "failed to convert" list couldn't be converted with tes3conv.exe, this usually means there's a broken thing somewhere in the mod. It does not affect the functionality of modmapper.

Scroll to the right and maybe down a bit.

Green cells with yellow text: Morrowind/Bloodmoon area. Hover over cells to see tooltip with list of mods. Click on cell to go to list entry.
Red/Gray/Other color cells with yellow text: a new lands or other large mod is altering these cells. Modmapper will colorize cells for some mods it knows about: TR, SHotN, Cyrodiil, some others. This is to help distinguish from vanilla cells.
Blue cells with black text: no mod or game file alters this area at all (flat textureless ocean). Not clickable, no tooltip on hover.

INTERIOR CELLS
Interiors are listed at the bottom of the page, use CTRL+F and type (for instance) guild of mages to look for any interior cells with that name, and see what mods alter them.

ADVANCED/ADVENTUROUS USERS
It's a python script, edit it as you like. I tried to keep user-configurable things near the top of the page. Cell colorization for other mods was added as an afterthought and could be implemented better. This goes for most of the script. The CSS is pretty awful as I know less about CSS than I do about Python and I know very little about Python, but I did what I had to in order to make everything display more or less correctly.
