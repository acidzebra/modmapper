# Modmapper for Morrowind
version = "0.8b3"
#
# examines all mods in a folder and builds a HTML file with a map showing and linking to exterior cell details, specifically which mods modify that cell.
# additionally provides list of interior cells with a list of mods modifying them.
#
# usage: put modmapper.py, tes3conv.exe and the mods you want to examine all in a folder
# (or just dump modmapper.py and tes3conv.exe in your data folder, that's what I do)
#
# run python modmapper.py "path-to-modfolder"
# 
version_history = """
# 0.1 - initial release<br>
# 0.2 - a little code cleanup and some cosmetic fixes (forgot to close a HTML tag), made esp/esm search case insensitive because some monsters name their file something.EsM<br>
# 0.3 - added hacky support for both rfuzzo's and G7's versions of tes3conv.exe css improvements - cell lights up on hover, entire cell (when linked) is now clickable. Might not work on all browsers.<br>
# 0.4 - missed interior flag(s?), added, shrunk table a little, made highlighted cell white to avoid clash with gray cells,cleaned up the version check code a bit<br>
# 0.5 - implemented random colors, increased contrast for cells with low modcount, got rid of stupid tooltip pointer since I couldn't get it to point to the cell itself, made sure mw.esm and bm.esm load first if present (to preserve color overrides)<br>
# 0.6 - more map stuff, some new user switches for map color control, brought back color overrides now that randomness seems to work<br>
# 0.7 - export now defaults to index.html instead of modmapper.html, split out ints and exts to separate export files (as the main file is getting chunky), some more config switches, search/text filters on interior and exterior pages, some css/presentation cleanup, better cell coloration function (more saturation, less trend to white)<br>
# 0.8 - added separate page with mod author/details/links. Linked up mods to nexusmods/archive.org Added about page (pretty convoluted, I should rewrite it as a function), this is done through a seperate script "modidentifier.py" which also does some other tricks (you can find this in the <a href=\"https://github.com/acidzebra/modmapper/tree/modmapper-website-gen\">website-gen</a> branch on github but it's pretty rough. I'm mostly working on the transfer to a proper DB and a more generalized way to interact with mods (including generating maps on the fly).<br>
"""

#
# not tested on anything except Windows OS+(open)MW, English-language versions.

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
excludetr = False
# skip these mods if found. You can add any mods you don't want on the map here.
excludelist = ["autoclean_cities_vanilla.esp","autoclean_cities_TR.ESP","Cyrodiil_Grass.ESP","Sky_Main_Grass.esp","TR_Data.esm","Tamriel_Data.esm","Better Heads Bloodmoon addon.esm","Better Heads Tribunal addon.esm","Better Heads.esm","OAAB_Data.esm","Better Clothes_v1.1.esp","Better Bodies.esp","Eden.esp"]
#  Map color control settings, not really fiddled with this beyond making them available
# controls coloring for cells, min value 0 max value should be less than maxbrightness, default 10
minbrightness = 5
# sensible values between ~100 and 200, min is a value above minbrightness, max 255. No checks or guard rails. Lower values produce more muted colors, default 200
maxbrightness = 160
# improve contrast for cells with few mods affecting them (only for mods, not base game)
lowmodcountcontrastincrease = True
# what is considered a "low mod count"
lowmodcount = 25
# controls the increase of values between steps (somewhat), values between 0-1 make the most sense, not really tested beyond that, default 1
stepmodifier = 1
# background and text color
bgcolor = "101010"
txcolor = "808080"
# water/untouched cell color in web/hex RGB
watercolor = "2B65EC"
watertextcolor = "1010ff"
# add empty cells to the exterior cell list. This will make that list VERY long and the program VERY slow.
addemptycells = False

# higlighted mods, put mod(s) here that you want "on top" of the map; their cell color will override whatever other mods normally get loaded first (normal = first original game, TR stuff, then rest of the content in alphabetical order). E.g. you can highlight a mod on the main continent with this, which normally would be a shade of green.You may also want to set a specific color override below.
highlightmodlist = [
                    "blacklightv1.34.esp",
                    "The Island v1.3.esp",
                    "The Island.esp",
                    "Skeleton_Island_V3.00.esp",
                    "The Isles.esp",
                    "Nebula Isles.ESP",
                    "Mournblade.esp",
                    "Sonta.esp",
                    "AshlanderTent_LothavorsLegacy.esp",
                    "Rise of the Witches",
                    "TheBlackMill.esp",
                    "Clean Black Queen Chronicles Ver 2.5.esp",
                    "Bal_Gurandok_FINAL.ESP",
                    "Dulsya Isle.esp",
                    "Fort Selgrim.esp",
                    "Specter Island.esp",
                    "KN01_KeeningCity.esp",
                    "TheManifoldSpires.esp",
                    "Bitter_Island.esp",
                    "SOPBeta1.4.esp",
                    "MD_Azurian Isles.esm",
                    "PMR _ Sea of Destiny 1.1 (fixed).esp",
                    "legato.esp",
                    "Rahj.esm",
                    "Tel_Meskoa_Tel_Matouigius_1.3.8_EV.esp",
                    "Hadeborg Castle V1.0.esp",
                    "NON1.LoveintheTimeofDaedra.v1.03.esp",
                    "TheGloryRoad.esm",
                    "Silgrad_Tower_external_build_1_4_4.esp",
                    "Shadowfel.ESP","Harsh outlands 0.1.ESP",
                    "elskjiver.esp",
                    "witchwoodXx.esp",
                    "TheBlackMill11.esp",
                    "The Goblin Lab v1.1.esp",
                    "Inferno's Island Revisited.esp",
                    "Havish.esm",
                    "Tel Nechim.esp",
                    "The_Outlands.esp",
                    "Clean New Roman City002b001b.esp",
                    "Clean Roman city v.4 expansion added #4.esp",
                    "Clean Roman city v.4 MORROWIND ONLY.esp",
                    "Frankenfell.esp",
                    "Beyond YsGramor v2.5.esm",
                    "Boe_Shuu.esp",
                    "Mournhold Downtown.esp",
                    "BT_Whitewolf_2_0_HOTV.esm",
                    "BT_Whitewolf_2_0_HOTV.esp",
                    "BT_Whitewolf_2_0_TOTSP_1624000965.esm",
                    "GS_Tamriel Part1_Black Marsh.esp",
                    "Booty.esp",
                    "Cixe_UnofficialExpansion.esp",
                    "DA_Sobitur_Facility_Clean.ESP",
                    "DA_Sobitur_Repurposed_1.ESP",
                    "Isengard (v1.2).esp",
                    "Isengard (v1.3).esp",
                    "Korobal v1.1.esp",
                    "Kalendaar_V1 _ Eng.esm"
                    ]


# color overrides, can add your own here or change colors, just copy one of the earlier lines, color format is "modname":"web/hex RGB". CASE sEnSItIvE.
coloroverride = {}
coloroverride.update({"Beautiful cities of Morrowind.ESP":"002010"})
coloroverride.update({"Morrowind.esm":"002000"})
coloroverride.update({"TR_Mainland.esm":"000040"})
coloroverride.update({"TR_Restexteriors.ESP":"400000"})
coloroverride.update({"Bloodmoon.esm":"003030"})
coloroverride.update({"Solstheim Tomb of The Snow Prince.esm":"300030"})
coloroverride.update({"Cyr_Main.esm":"909000"})
coloroverride.update({"Sky_Main.esm":"001060"})
# the default name of the exported file
exportfilename = "index.html"

# ---  
        
import json
import io
import sys
import os
from os import listdir
from os.path import isfile, join
from random import randrange
from datetime import datetime
import ast

# reading the data from the file
with open('zipdict.txt') as f:
    data = f.read()
myzipdict = ast.literal_eval(data)

with open('linkdict.txt') as f:
    data = f.read()
mylinkdict = ast.literal_eval(data)

with open('nonnexusdict.txt') as f:
    data = f.read()
myexternalsitedict = ast.literal_eval(data)



html_header = """
<!DOCTYPE html>
<HTML>
<HEAD>
<title>Morrowind Modmapper v"""+str(version)+"""+</title>
<meta name="keywords" content="HTML, CSS, JavaScript">
<meta name="description" content="A map of many (maybe most) Morrowind landmass mods and other mods affecting interior/exterior cells, with links to the website where you can find them. And a record of decades and thousands of hours worth of fan creations, from the silly to the sublime.">
<meta name="author" content="acidzebra">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<STYLE>
* {
  box-sizing: border-box;
}

body {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 100%;
  background-color: #101010;
  color: #808080;
}

a.linkstuff {
  color: #a0a0a0; !important;
  font-weight: normal;
  text-decoration: normal;
}

a.linkstuff:visited {
  color: #a0a0a0; !important;
  font-weight: normal;
  text-decoration: normal;
}

a.linkstuff:hover {
  color: #c0c0c0; !important;
  font-weight: normal;
  text-decoration: normal;
}

a.linkstuff:active {
  color: #b0b0b0; !important;
  font-weight: normal;
  text-decoration: normal;
}

a:link {
  color: #909090;
  text-decoration: none;
}
a:visited {
  color: #909090;
  text-decoration: none;
}
a:hover {
  background-color: #909090;
  text-decoration: none;
  color: #ff0000;
}
a:active {
  color: #909090;
  text-decoration: none;
} 

table {
  width: 100%;
  margin-top: 90px;
  border: none;
  border-spacing:0;
  border-collapse: collapse;
}
td .content {
  white-space: pre;
  aspect-ratio: 1 / 1 ;
  text-align: center;
  font-family:"Courier New", Courier, monospace;
  font-size: 70%;
}

td:hover {
  background-color: #909090;
  font-weight: normal;
  color: #ff0000;
}
td a {
  display: inline-block;
  height:100%;
  width:100%;
}
.tooltip {
  position: relative;
  display: inline-block;
  font-size: 100%;
}
.tooltip .tooltiptext {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 100%;
  white-space: normal;
  font-weight: normal;
  visibility: hidden;
  width: 1000%;
  background-color: #555;
  color: #fff;
  text-align: left;
  border-radius: 6px;
  padding: 5px 5px 5px 5px;
  position: absolute;
  z-index: 1;
  bottom: 125%;
  left: 50%;
  margin-left: -60px;
  opacity: 0;
  transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
  white-space: normal;
  visibility: visible;
  font-size: 100%;
  opacity: 1;
}
.nav {
  position: fixed;
  background-color: #06111c;
  background: #06111c;
  top: 0;
  left: 0;
  right: 0;
  z-index: 500;
}
.flex-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0px 2px;
}
.nav ul {
  display: flex;
  list-style-type: none;
  align-items: center;
  justify-content: center;
}
.nav a {
  color: #fff;
  text-decoration: none;
  padding: 0px 5px;
}

#intextinput {
  width: 40%;
  padding: 12px 20px 12px 40px;
  border: 1px solid #ddd;
  margin-bottom: 12px;
  display: block;
  margin-left: auto;
  margin-right: auto;
}

.intexttable {
  width: 100%;
  border: none;
  margin-bottom: 12px;
  margin-top: 90px;
  margin-left: auto;
  margin-right: auto;
  font-size: 80%;
  border-collapse: separate;
}

.intexttable a {
  display: inline;
  font-weight: normal;
  background-color: #101010;
  color: #a0a0a0;
}

.intexttable td:hover {
  font-weight: normal;
  background-color: #101010;
  color: #808080;
}

.intexttable a:hover {
  font-weight: normal;
  background-color: #101010;
  color: #ffff00;
}

.modtable {
  width: 100%;
  border: none;
  margin-bottom: 12px;
  margin-top: 90px;
  margin-left: auto;
  margin-right: auto;
  font-size: 80%;
}

.modtable a {
  display: inline;
  font-weight: normal;
}

.modtable td:hover {
  font-weight: normal;
  
}

.modtable td:hover {
  font-weight: normal;
  background-color: #101010;
  color: #808080;
}

.modtable a:hover {
  font-weight: normal;
  background-color: #101010;
  color: #ffff00;
}

.programlink {
  color: #ffff00;
}

.programlink a {
  color: #ffff00;
}
  </STYLE>
</HEAD>
<BODY>
"""

html_footer = """
</div>
</BODY>
</HTML>
"""
about_page_top = """
<h2 style=\"margin-top: 90px;\">About ModMapper</h2>
<p>A toy I wrote for myself while working on <a href=\"https://www.nexusmods.com/morrowind/mods/53034\" target="_blank">Lawnmower</a>. It might be of some use if you're trying to find mod conflict areas, when you are hunting for a good place to make a new mod (hint: it's not Balmora) or see if landmass mods conflict. Or just because you like very low-rez maps rendered as a HTML table.</p>

<p>It also serves as a record of decades of Morrowind modding and the thousands of hours fans have put into building new content, adding links to places where you can find this content. The overarching goals are to be comprehensive, produce simple yet attractive output, be zero-cost & zero-maintenance, robust, and durable. Will Github vanish eventually? Sure. Will it last longer than my ability and/or interest in maintaining my own page? Definitely. Sites die. Morrowind modding history is littered with dead sites, dead links, content that people worked hard on and now has all but disappeared.</p>

<p>Modmapper will examine a folder of one or more mods and build a html file with a map of exterior cells. It will show which mods alter a cell, with brighter colors meaning more mods affecting that cell. Mouse over a cell to see a tooltip with mods affecting that cell. Click on any cell with yellow text to jump to a list entry for that cell with the mods affecting it. Use [back] function of your browser to return to map. Modmapper will also build a list of interior cells and which mods alter them and add that list to the end of the html file, you can search like you would on any web page. Finally, it will build a table of mods, the name of the zip file it was found in, and if known, a link to Nexus or other places where the mod can be found.</p>

<p>Modmapper does not alter any game files, it will read esp/esm files in a folder and produce a few HTML files in the same folder. It does not require access to other resources of a mod, just the esp or esm. You can use it to inspect entire modlists, or just look at a specific mod, the overlap between two mods, etc.</p>

<h2>Known Issues</h2>
<ul>The Interiors page is getting a little unwieldy (and the Exteriors too). Not really sure what to do about it, it's a lot of data. Maybe pagination? But that would require some boring pagination code.</ul>

<h2>Version History</h2>
<p>
"""

about_page_bottom = """
</p>
<h2>Web Page Changelog</h2>
<p>
<a href=\"https://github.com/acidzebra/modmapper/activity?ref=modmapper-page\" target=\"_blank\">https://github.com/acidzebra/modmapper/activity?ref=modmapper-page</a>
</p>
<h2>Overview of Entire Map</h2>
<img src=\"https://i.imgur.com/45Xuc9k.png\" alt=\"zoomed-out image of map\" style=\"border:3px solid white;display: block;margin-left: auto;margin-right: auto; width: 90%;\">
"""

intexttableopen = """
    <table id="bigtable" class="intexttable">
    """
modtableopen = """
    <table id="bigtable" class="modtable">
    """
intexttableclose = """
</table>
<script>
function intextsearch() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("intextinput");
    filter = input.value.toUpperCase();
    table = document.getElementById("bigtable");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        var allTDs = tr[i].getElementsByTagName("td");

        for (index = 0; index < allTDs.length; index++) {
            txtValue = allTDs[index].textContent || allTDs[index].innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
                break;
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}
</script>
"""

modtableclose = """
</table>
<script>
function intextsearch() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("intextinput");
    filter = input.value.toUpperCase();
    table = document.getElementById("bigtable");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        var allTDs = tr[i].getElementsByTagName("td");

        for (index = 0; index < allTDs.length; index++) {
            txtValue = allTDs[index].textContent || allTDs[index].innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
                break;
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}
</script>
"""

esplist = []
modcelltable = []
mastermoddict = {}
masterintdict = {}
basecolorhex = {}
filecounter = 1
tablexmin = 0
tablexmax = 0
tableymin = 0
tableymax = 0
excludecounter = 0
failcounter = 0
failedmodlist = ""
modcelllist = ""
intcelllist = []
maxmodcellist = 0
tes3convversion = 0
interiorcell = False
generationdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
global textcolors
textcolors = "000000"
mostfaroutmodxmin = ""
mostfaroutmodxmax = ""
mostfaroutmodymin = ""
mostfaroutmodymax = ""
authordict = {}
descdict = {}

def int2hex(x):
    val = hex(x)[2:]
    val = "0"+val if len(val)<2 else val
    return val

def calcoutputcellcolor(mymodcount,mymodlist):
    global textcolors
    foundmod = False
    returnvalue = "606060"
    basevalue = 0
    currentmod = ""
    valuestep = stepmodifier*(300/maxmodcellist)
    if mymodcount <= lowmodcount and not "Morrowind.esm" in mymodlist and not "Bloodmoon.esm" in mymodlist and lowmodcountcontrastincrease:
        valuestep += 10
    finalcolorincrease = min(int(basevalue+(mymodcount*valuestep)),255)
    for items in mymodlist:
        currentmod = items
        foundmod = False
        if not foundmod and currentmod in basecolorhex:
            foundmod = True
            hexcolors = (basecolorhex[currentmod])
            colorg= hexcolors[:-2]
            colorg= int(colorg[2:],16)
            colorr= int(hexcolors[:2],16)
            colorb= int(hexcolors[4:],16)
            reductionfactor = 1.5
            if colorr > colorg and colorr > colorb:        
                finaloutr=min((colorr+finalcolorincrease), 255)
                finaloutb=min((colorb+(finalcolorincrease/reductionfactor)), 255)
                finaloutg=min((colorg+(finalcolorincrease/reductionfactor)), 255)
            elif colorg > colorr and colorg > colorb:        
                finaloutg=min((colorg+finalcolorincrease), 255)
                finaloutb=min((colorb+(finalcolorincrease/reductionfactor)), 255)
                finaloutr=min((colorr+(finalcolorincrease/reductionfactor)), 255)
            elif colorb > colorg and colorb > colorr:        
                finaloutb=min((colorb+finalcolorincrease), 255)
                finaloutr=min((colorr+(finalcolorincrease/reductionfactor)), 255)
                finaloutg=min((colorg+(finalcolorincrease/reductionfactor)), 255)
            else:
                finaloutr=min((colorr+finalcolorincrease), 255)
                finaloutg=min((colorg+finalcolorincrease), 255)
                finaloutb=min((colorb+finalcolorincrease), 255)
            lumi = min((0.2126*finaloutr + 0.7152*finaloutg + 0.0722*finaloutb),255)
            if lumi >= 50 and lumi <= 100:
                lumi = (lumi-(lumi*0.75))
                if lumi < 0:
                    lumi = 0
            if lumi > 100 and lumi <= 150:
                lumi = min((lumi+(lumi*0.75)),255)
            greygradient = int2hex(min(int(255-lumi),255))
            textcolors = str(greygradient)+str(greygradient)+str(greygradient)
            returnvalue = str(int2hex(int(finaloutr)))+str(int2hex(int(finaloutg)))+str(int2hex(int(finaloutb)))
        if foundmod:
            break
    return returnvalue

try:
    target_folder = sys.argv[1]
    target_folder = str(target_folder)
except:
    print("usage: put mods + modmapper.py + tes3conv.exe in same folder") 
    print("run: python modmapper.py \"target directory\"")
    print("output will be saved as index.html")
    sys.exit()

if not os.path.isdir(target_folder):
    print("FATAL: target directory \"",target_folder,"\"does not exist.")
    sys.exit()

if not os.path.isfile("tes3conv.exe"):
    print("FATAL: cannot find path to tes3conv.exe, is it in the same folder as this script?")
    sys.exit()
    
esplist += [each for each in os.listdir(target_folder) if (each.lower().endswith('.esm') or each.lower().endswith('.esp') or each.lower().endswith('.omwaddon'))]
#esplist += [each for each in os.listdir(target_folder) if each.lower().endswith('.esp')]

# esplist += [filename for filename in listdir(target_folder) if filename.lower().rsplit('.')[2] in ["esp", "esm", "omwaddon"]]
esplist = sorted(esplist, key=str.casefold)
if "Cyr_Main.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Cyr_Main.esm")))
if "Sky_Main.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Sky_Main.esm"))) 
if excludetr:
    if "TR_" in esplist or "_TR" in esplist:
        esplist.pop()
if overridetr:
    if "TR_Restexteriors.ESP" in esplist:
        esplist.insert(0, esplist.pop(esplist.index("TR_Restexteriors.ESP")))
    if "TR_Mainland.esm" in esplist:
        esplist.insert(0, esplist.pop(esplist.index("TR_Mainland.esm")))
if "Solstheim Tomb of The Snow Prince.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Solstheim Tomb of The Snow Prince.esm"))) 
for items in highlightmodlist:
    for stuff in esplist:
        if str(items).casefold() == str(stuff).casefold():
            esplist.insert(0, esplist.pop(esplist.index(stuff)))
            print("popped",stuff)
if "Siege at Firemoth.esp" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Siege at Firemoth.esp")))  
if "Tribunal.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Tribunal.esm")))
if "Bloodmoon.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Bloodmoon.esm")))
if "Morrowind.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Morrowind.esm")))

authordict = {}
descdict = {}
masterdict = {}
objectdict = {}
finalesplist = []
for files in esplist:
    if files not in excludelist:
        colr = int2hex(randrange(minbrightness, maxbrightness))
        colg = int2hex(randrange(minbrightness, maxbrightness))
        colb = int2hex(randrange(minbrightness, maxbrightness))
        if files in coloroverride:
            hexcolors = (coloroverride[files])
            colr = hexcolors[:2]
            colg = hexcolors[:-2]
            colg = colg[2:]
            colb = hexcolors[4:]
        if "zzzzz" in str(files):
            hexcolors = "000020"
        if files not in basecolorhex:
            basecolorhex.update({files:str(colr)+str(colg)+str(colb)})
        tes3convversion = 0
        jsonfilename = files[:-4]+".json"
        if deletemodjson and os.path.isfile(str(jsonfilename)):
            os.remove(jsonfilename)
        if not os.path.isfile(str(jsonfilename)):
            try:
                target = "tes3conv.exe \""+str(files)+"\" \""+str(jsonfilename)+"\""
                print("running",target)
                os.system(target)
            except Exception as e:
                print("unable to convert mod to json: "+repr(e)) 
        if not os.path.isfile(str(jsonfilename)):
            failcounter+=1
            failedmodlist = failedmodlist + str(files) + " "
        if os.path.isfile(str(jsonfilename)):
            finalesplist.append(files)
            f = io.open(jsonfilename, mode="r", encoding="utf-8")
            espfile_contents = f.read()
            modfile_parsed_json = json.loads(espfile_contents) 
            f.close()
            del espfile_contents
            if deletemodjson:
                os.remove(jsonfilename)
            print("examining file",filecounter,"of",len(esplist),":",files)
            for keys in modfile_parsed_json:
                extcellcounter = 0
                if keys["type"] == "Header":
                    if len(keys["author"])>0:
                        authordict[files] = str(keys["author"])
                    else:
                        authordict[files] = "N/A"
                    if len(keys["description"])>0:
                        descdict[files] = str(keys["description"])
                    else:
                        descdict[files] = "N/A"
                    if len(keys["masters"])>0:
                        masterdict[files] = str(keys["masters"])
                    else:    
                        masterdict[files] = "N/A"
                    objectdict[files] = str(keys["num_objects"])
                if keys["type"] == "Cell" and len(keys["references"])>0:
                    extcellcounter += 1
                    tes3convversioncheck = 0
                    tes3convversioncheck = str(keys["data"]["flags"])
                    if tes3convversioncheck.isdigit():
                        tes3convversion = 0
                        intlist = [1,5,3,7,135,131,137]
                        if int(tes3convversioncheck) in intlist:
                            interiorcell = True
                        else:
                            interiorcell = False
                    else:
                        tes3convversion = 1
                        if "INTERIOR" in tes3convversioncheck:
                            interiorcell = True
                        else:
                            interiorcell = False
                    if not interiorcell:
                        if keys["data"]["grid"][0] < tablexmin:
                            tablexmin = keys["data"]["grid"][0]
                            mostfaroutmodxmin = files
                        if keys["data"]["grid"][0] > tablexmax:
                            tablexmax = keys["data"]["grid"][0]
                            mostfaroutmodxmax = files
                        if keys["data"]["grid"][1] < tableymin:
                            tableymin = keys["data"]["grid"][1]
                            mostfaroutmodymin = files
                        if keys["data"]["grid"][1] > tableymax:
                            tableymax = keys["data"]["grid"][1]
                            mostfaroutmodymax = files
                        if keys["data"]["grid"] not in modcelltable:
                            modcelltable.append(keys["data"]["grid"])
                        if str(keys["data"]["grid"]) not in mastermoddict:
                            mastermoddict[str(keys["data"]["grid"])] = str(files)
                            if moreinfo:
                                print("new ext cell",str(keys["data"]["grid"]))
                        else:
                            modcelllist = mastermoddict[str(keys["data"]["grid"])]
                            modcelllist = modcelllist + ", " + files
                            modcelllistcounter = int(len(str(modcelllist).split(",")))
                            if modcelllistcounter > maxmodcellist:
                                maxmodcellist = modcelllistcounter
                            mastermoddict[str(keys["data"]["grid"])] = modcelllist
                    else:
                        intcellname = None
                        if tes3convversion == 0:
                            intcellname = keys["id"]
                        else:
                            intcellname = keys["name"]
                        intcellname.replace(",", ".")
                        if intcellname:
                            if intcellname not in masterintdict.keys():
                                masterintdict[str(intcellname)] = str(files)
                                if moreinfo:
                                    print("new int cell",intcellname)
                            else:
                                tempvalue = ""
                                tempvalue = masterintdict[intcellname]
                                tempvalue = tempvalue + ", " + files
                                masterintdict[str(intcellname)] = tempvalue
                    interiorcell = False
                    intappendlist = None
                    intcelllist = []
        filecounter+=1
    else:
        print("skipping file",filecounter,"of",len(esplist),":",files,"(excludelist)")
        filecounter+=1
        excludecounter+=1

print("Sorting through mods and assembling and linking tables, this will take a while...")
print("topmost:",mostfaroutmodymax,"bottommost:",mostfaroutmodymin,"leftmost:",mostfaroutmodxmin,"rightmost:",mostfaroutmodxmax)
tablexmin = tablexmin - tableborder
tablexmax = tablexmax + tableborder
tableymin = tableymin - tableborder
tableymax = tableymax + tableborder
tablewidth = int(abs(tablexmax)+abs(tablexmin)+1)
tablelength = int(abs(tableymax)+abs(tableymin)+1)
midvaluex = int(tablexmin+abs(tablewidth/2))
midvaluey = int(tableymin+abs(tablelength/2))
totalcells = tablewidth * tablelength
if moreinfo:
    print("cell x min:",tablexmin,"cells x max",tablexmax,"cell y min",tableymin,"cell y max",tableymax,"tableborder",tableborder)
    print("calculated table width",tablewidth,"calculated table length",tablelength)

foundmycell = False
foundthemod = False

lookup = []
table = []
table.append("""</table>""")
tablecounter = 0
tablerows = 0
tablecolumns = 0
tooltipdata = ""
formattedextlist = ""
formattedintlist = ""
formattedintlist += intexttableopen
masterintdict = dict(sorted(masterintdict.items())) 
intcounter = 1
cyclecounter = 1
totalints= len(masterintdict)
#mastermoddict = dict(sorted(mastermoddict.items()))

html_body = ""
html_int_body = ""
html_ext_body = ""

html_allpage_navbar_start = """
<nav class="nav">
<div class="flex-container">
<h2 class="logo"><a href="index.html#map["""+str(midvaluex)+""", """+str(midvaluey)+"""]" title="jump to map center (more or less)">Morrowind Modmapper """+str(version)+"""</a></h2>"""

html_mainpage_navbar_mid = """Mapped """+str(len(esplist))+""" files, """+str(totalcells)+""" exterior and """+str(totalints)+""" interior cells."""

html_intextpage_navbar_mid = """    <input type="text" id="intextinput" onkeyup="intextsearch()" placeholder="Filter cells or mods.. (wait for page load!)" title="Type something">"""

html_modpage_navbar_mid = """    <input type="text" id="intextinput" onkeyup="intextsearch()" placeholder="Filter any word on the page... (wait for page load!)" title="Type something">"""

html_allpage_navbar_end = """
    <ul>
      <li><a href="index.html#map["""+str(midvaluex)+""", """+str(midvaluey)+"""]" title="jump to map center (more or less)">Map</a></li>
      <li><a href="modmapper_interiors.html" title="open page of Interior cells">Interiors</a></li>
      <li><a href="modmapper_exteriors.html" title="open page of Exterior cells">Exteriors</a></li>
      <li><a href="modmapper_mods.html" title="open mod list page">Mods</a></li>
      <li>||</li>
      <li><a href="modmapper_about.html" title="about modmapper">About</a></li>
      <li>||</li>
      <li><div class="programlink"><a href="https://www.nexusmods.com/morrowind/mods/53069" title="go to modmapper NexusMods mod page (new tab)" target="_blank">NexusMods</a></div></li>
      <li><div class="programlink"><a href="https://github.com/acidzebra/modmapper" title="go to modmapper GitHub page (new tab)" target="_blank">Github</a></div></li>
    </ul>
  </div>
</nav>
"""

about_page_gendetails = """
<h2> Current Page Details</h2>
<p>Page generated on """+str(generationdate)+""", examined """+str(len(esplist))+""" files. </p>
<p>Failed to convert """+str(failcounter)+""" mods:"""+str(failedmodlist)+"""</p>
"""


while tablerows < tablelength:
    print("Assembling map row",tablerows,"of",(tablelength-1),"(",(tablewidth-1),"columns/cells per row). topmost:",mostfaroutmodymax,"bottommost:",mostfaroutmodymin,"leftmost:",mostfaroutmodxmin,"rightmost:",mostfaroutmodxmax )
    table.append("""\n\t</tr>\n""")
    td = []
    tablecolumns = 0
    while tablecolumns < tablewidth:
        #print("assembling column",tablecolumns)
        tooltipdata = ""
        done = 0
        foundmycell = False
        docellcolor = "0099ff"
        for values in modcelltable:
            if values[0] == (tablecolumns-abs(tablexmin)) and values[1] == (tablerows-abs(tableymin)):
                foundmycell = True
                modcount = mastermoddict[str(values)]
                modcount = len(modcount.split(","))
                modifyingmodlist = []
                modifyingmodlist = str(mastermoddict[str(values)]).split(",")
                dedupe_modlist = []
                for item in modifyingmodlist:
                    if item not in dedupe_modlist:
                        dedupe_modlist.append(item)
                modifyingmodlist = []
                modifyingmodlist = dedupe_modlist
                tooltipdisplaymodlist = []
                limittooltip = True
                limittooltiplimit = 15
                nexusmodlink = ""
                extcelldatamodlist = ""
                extcelldatamodlistfound = ""
                extcelldatamodlistnotfound = ""
                # THIS SHOULD BE A FUNCTION
                # take the list of mod affecting cell, go through them 1 by 1
                for bunchofmods in modifyingmodlist:
                    foundthemod= False
                    #now take zipfiles in the zipdict and go through them one by one
                    for allthezips in myzipdict:
                        # get the list of mods in the current zipfile
                        listofzipmods = myzipdict[allthezips]
                        #go through each individual mod and try to match to the outer loop mod we started with
                        for individualmods in listofzipmods:
                            if (str(bunchofmods).lower() in str(individualmods).lower() or str(individualmods).lower() in str(bunchofmods).lower()) and str(bunchofmods) != "Morrowind.esm" and str(bunchofmods) != "Bloodmoon.esm" and str(bunchofmods) != "Tribunal.esm":
                                foundthemod = True
                                nexusmodslink = None
                                try:
                                    nexusmodlink = mylinkdict[allthezips]

                                    if moreinfo:
                                        print("nexus link for",bunchofmods,"is",nexusmodlink,"zip file",allthezips)
                                except:
                                    foundthemod = False
                            if foundthemod:
                                break
                        if foundthemod:
                            break
                    if foundthemod:
                        #extcelldatamodlistfound += """<a class=\"extlink\" href=\""""+str(nexusmodlink)+"""\" target=\"_blank\">"""+str(bunchofmods)+"""</a>, """
                        extcelldatamodlistfound += """<a class=\"extlink\" href=\"modmapper_mods.html#"""+str(individualmods).lstrip()+"""\">"""+str(bunchofmods).lstrip()+"""</a>, """
                    else:
                        extcelldatamodlistnotfound += str(bunchofmods).lstrip()+""", """
                    foundthemod=False
                    nexusmodslink=""
                extcelldatamodlist += extcelldatamodlistfound
                extcelldatamodlist += extcelldatamodlistnotfound
                
                if limittooltip and modcount > limittooltiplimit:
                    tooltipdisplaymodlist = modifyingmodlist[:limittooltiplimit]
                    tooltipdisplaymodlist.append(" <br>(tooltip limited to "+str(limittooltiplimit)+" of "+str(modcount)+" mods, click cell to see all)")
                else:
                    tooltipdisplaymodlist = modifyingmodlist
                tooltipdata = """cell: <b>"""+str(values)+"""</b> ("""+str(modcount)+""" mods)<BR>mods: """+str(tooltipdisplaymodlist)
                formattedextlist += """<tr><td><br><a class=\"extlink\" href=\"index.html#map"""+str(values)+"""\" id=\""""+str(values)+"""\">cell: <b>"""+str(values)+"""</b></a> ("""+str(modcount)+""" mods)<BR>mods: """+str(extcelldatamodlist)+"""</td></tr>\n"""
            if foundmycell:
                break
        paddingleft = ""
        paddingright = ""
        if abs(values[0]) < 100:
            paddingleft = " "
        if abs(values[0]) < 10:
            paddingleft = "  "
        if paddingleft and values[0] > -1:
            paddingleft += " "
        if abs(values[1]) < 100:
            paddingright = "  "
        if abs(values[1]) < 10:
            paddingright = "   "
        if paddingright and values[1] > -1:
            paddingright += " "
        cellx = str(int(tablecolumns-abs(tablexmin)))
        celly = str(int(tablerows-abs(tableymin)))
        if foundmycell:
            docellcolor = calcoutputcellcolor(modcount,modifyingmodlist)
            td.append("""<td bgcolor=#"""+str(docellcolor)+""" style=\"color:#"""+textcolors+""";\"><div class="content"><div class="tooltip"><a href=\"modmapper_exteriors.html#"""+str(values)+"""\" id=\"map"""+str(values)+"""\" style=\"color: #"""+textcolors+""";text-decoration:none;\">"""+str(paddingleft)+"["+cellx+""",<BR>"""+celly+"]"+str(paddingright)+"""</a><span class="tooltiptext">"""+tooltipdata+"""</span></div></div></td>\n""")
        else:
            td.append("""<td bgcolor=#"""+str(watercolor)+""" style=\"color:#"""+watertextcolor+""";\"><div class="content"><a id=\"map["""+cellx+""", """+celly+"""]\">"""+str(paddingleft)+"["+cellx+""",<BR>"""+celly+"]"+str(paddingright)+"""</a></div></td>\n""")
            if addemptycells:
                formattedextlist += """<tr><td><a href=\"index.html#map["""+cellx+""", """+celly+"""]\" id=\"["""+cellx+""", """+celly+"""]\" class="linkstuff">cell: <b>["""+cellx+""", """+celly+"""]</b></a><BR>mods: EMPTY CELL</td></tr>"""
        foundmycell = False
        tablecolumns+=1
    table.append("\t\t"+"".join(td))
    table.append("""\t<tr>\n""")
    tablerows+=1
table.append("""<table>\n""")
table.reverse()

print("generating and linking interior list for "+str(totalints)+" interior cells.")
for items in masterintdict:
    if cyclecounter > 499:
        print(str(intcounter),"of",str(totalints),"interiors, currently at",str(items))
        cyclecounter = 1
    else:
        cyclecounter += 1
    modcount = str(masterintdict[items])
    modcount = len(modcount.split(","))
    intmodifyingmodlist = []
    intmodifyingmodlist = str(masterintdict[str(items)]).split(",")
    intdedupe_modlist = []
    for item in intmodifyingmodlist:
        if item not in intdedupe_modlist:
            intdedupe_modlist.append(item)
    intmodifyingmodlist = []
    intmodifyingmodlist = intdedupe_modlist
    intcelldata = ""
    # THIS SHOULD BE A FUNCTION
    # take the list of mod affecting cell, go through them 1 by 1
    for bunchofmods in intmodifyingmodlist:
        foundthemod= False
        #now take zipfiles in the zipdict and go through them one by one
        for allthezips in myzipdict:
            # get the list of mods in the current zipfile
            listofzipmods = myzipdict[allthezips]
            #go through each individual mod and try to match to the outer loop mod we started with
            for individualmods in listofzipmods:
                if (str(bunchofmods).lower() in str(individualmods).lower() or str(individualmods).lower() in str(bunchofmods).lower()) and bunchofmods != "Morrowind.esm" and bunchofmods != "Bloodmoon.esm" and bunchofmods != "Tribunal.esm":
                    foundthemod = True
                    nexusmodslink = None
                    try:
                        nexusmodlink = mylinkdict[allthezips]
                        if moreinfo:
                            print("nexus link for",bunchofmods,"is",nexusmodlink,"zip file",allthezips)
                    except:
                        foundthemod = False

                if foundthemod:
                    break
            if foundthemod:
                break
        bunchofmods.replace(".", ",")
        if foundthemod:
            intcelldata += """<a href=\"modmapper_mods.html#"""+str(bunchofmods).lstrip()+"""\" id=\""""+str(bunchofmods).lstrip()+"""\">"""+str(bunchofmods).lstrip()+"""</a>"""
        else:
            intcelldata += str(bunchofmods)+""" """
    formattedintlist += """<tr><td><b>"""+str(items)+"""</b></td><td>"""+str(modcount)+"""</td><td>"""+str(intcelldata)+"""</td></tr>"""
    intcounter += 1
formattedintlist += intexttableclose 

# MODS PAGE
#basecolorhex.update({files:str(colr)+str(colg)+str(colb)})
print("assembling mods table...")
modpage_table = ""
modpage_table += modtableopen
modpage_table += """<tr><td>color</td><td>esp/esm</td><td>author(s)</td><td>description</td><td>masters</td><td># of objects</td><td>zipfile</td><td>nexuslink</td></tr>"""
filteredesps = len(finalesplist)
print("assembling mods page table for",filteredesps,"esp/esm files")
for myfiles in finalesplist:
    color = basecolorhex[myfiles]
    foundthemod = False
    nexusmodlink = "#"
    modzipfile = "N/A"
    for allthezips in myzipdict:
        nexusmodlink = "#"
        # get the list of mods in the current zipfile
        listofzipmods = myzipdict[allthezips]
        #go through each individual mod and try to match to the outer loop mod we started with
        for individualmods in listofzipmods:
            if (str(myfiles).lower() in str(individualmods).lower() or str(individualmods).lower() in str(myfiles).lower()) and myfiles != "Morrowind.esm" and myfiles != "Bloodmoon.esm" and myfiles != "Tribunal.esm":
                foundthemod = True
                modzipfile = str(allthezips)
                try:
                    nexusmodlink = mylinkdict[allthezips]
                    if moreinfo:
                        print("nexus link for",files,"is",nexusmodlink,"zip file",allthezips)
                except:
                    foundthemod = False
            if foundthemod:
                break
        if foundthemod:
            break
    modauthor = str(authordict[myfiles])
    moddesc = str(descdict[myfiles])
    modmasters = str(masterdict[myfiles])
    modobjects = str(objectdict[myfiles])
    myfileslist = []
    myfileslist.append(myfiles)
    docellcolor= calcoutputcellcolor(0,myfileslist)
    modpage_table += """<tr><td bgcolor=#"""+str(docellcolor)+""" style=\"color:#"""+textcolors+""";\">#"""+str(docellcolor).upper()+"""</td><td><a href=\""""+str(nexusmodlink)+"""\" target=\"_blank\" id=\""""+str(myfiles)+"""\">"""+str(myfiles)+"""</a></td><td>"""+modauthor+"""</td><td>"""+moddesc+"""</td><td>"""+modmasters+"""</td><td>"""+modobjects+"""</td><td>"""+modzipfile+"""</td><td><a href=\""""+str(nexusmodlink)+"""\" target=\"_blank\">"""+str(nexusmodlink)+"""</a></td></tr>\n"""
    #print(str(files),str(color),str(nexusmodlink))
modpage_table += modtableclose

print("assembling and exporting HTML...")
mods_body = ""
if splitpages:
# mods page
    mods_body += html_header
    mods_body += html_allpage_navbar_start
    mods_body += html_modpage_navbar_mid
    mods_body += html_allpage_navbar_end
    mods_body += modpage_table
    mods_body += html_footer 
    mods_output = mods_body
    # index page
    html_body += html_allpage_navbar_start
    html_body += html_mainpage_navbar_mid
    html_body += html_allpage_navbar_end
    html_body += "".join(table)
    index_output = html_header+html_body+html_footer
# int page
    html_int_body += html_allpage_navbar_start
    html_int_body += html_intextpage_navbar_mid
    html_int_body += html_allpage_navbar_end
    html_int_body += formattedintlist
    interior_output = html_header+html_int_body+html_footer
# ext page
    html_ext_body += html_allpage_navbar_start
    html_ext_body += html_intextpage_navbar_mid
    html_ext_body += html_allpage_navbar_end
    html_ext_body += intexttableopen
    html_ext_body += formattedextlist
    html_ext_body += intexttableclose
    exterior_output = html_header+html_ext_body+html_footer
    html_file= open(exportfilename,"w")
    html_file.write(index_output)
    html_file.close()
    html_file= open("modmapper_interiors.html","w")
    html_file.write(interior_output)
    html_file.close()
    html_file= open("modmapper_exteriors.html","w")
    html_file.write(exterior_output)
    html_file.close
    html_file= open("modmapper_mods.html","w")
    html_file.write(mods_output)
    html_file.close
# about page
    about_body = ""
    about_body += html_allpage_navbar_start
    about_body += html_mainpage_navbar_mid
    about_body += html_allpage_navbar_end
    about_body += about_page_top
    about_body += version_history
    about_body += about_page_bottom
    about_body += about_page_gendetails
    about_body = html_header+about_body+html_footer
    html_file= open("modmapper_about.html","w")
    html_file.write(about_body)
    html_file.close
else:
    html_body += "".join(table)
    html_body += formattedextlist
    html_body += formattedintlist
    index_output = html_header+html_body+html_footer
    html_file= open(exportfilename,"w")
    html_file.write(index_output)
    html_file.close()

print("cell x min:",tablexmin,"cells x max",tablexmax,"cell y min",tableymin,"cell y max",tableymax,"tableborder",tableborder)
print("calculated table width",tablewidth,"calculated table length",tablelength)
print("topmost:",mostfaroutmodymax,"bottommost:",mostfaroutmodymin,"leftmost:",mostfaroutmodxmin,"rightmost:",mostfaroutmodxmax)
if excludecounter > 0:
    print(""" Skipped """+str(excludecounter)+""" files on the exclude list. """)
if failcounter > 0:
    print(""" Failed to convert """+str(failcounter)+""" mods."""+str(failedmodlist))
print("all done! I hope you enjoy modmapper.")

# Copyright © 2023 acidzebra

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.