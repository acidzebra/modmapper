# Modmapper for Morrowind
version = "0.7"
#
# examines all mods in a folder and builds a HTML file with a map showing and linking to exterior cell details, specifically which mods modify that cell.
# additionally provides list of interior cells with a list of mods modifying them.
#
# usage: put modmapper.py, tes3conv.exe and the mods you want to examine all in a folder
# (or just dump modmapper.py and tes3conv.exe in your data folder, that's what I do)
#
# run python modmapper.py "path-to-modfolder"
# 
# 0.1 - initial release
# 0.2 - a little code cleanup and some cosmetic fixes (forgot to close a HTML tag), made esp/esm search case insensitive because some monsters name their file something.EsM
# 0.3 - added hacky support for both rfuzzo's and G7's versions of tes3conv.exe css improvements - cell lights up on hover, entire cell (when linked) is now clickable. Might not work on all browsers.
# 0.4 - missed interior flag(s?), added, shrunk table a little, made highlighted cell white to avoid clash with gray cells,cleaned up the version check code a bit
# 0.5 - implemented random colors, increased contrast for cells with low modcount, got rid of stupid tooltip pointer since I couldn't get it to point to the cell itself, made sure mw.esm and bm.esm load first if present (to preserve color overrides)
# 0.6 - more map stuff, some new user switches for map color control, brought back color overrides now that randomness seems to work
# 0.7 - export now defaults to index.html instead of modmapper.html, split out ints and exts to separate export files (as the main file is getting chunky), some more config switches, search/text filters on interior and exterior pages, some css/presentation cleanup, better cell coloration function (more saturation, less trend to white)
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
# skip these mods if found. You can add any mods you don't want on the map here.
excludelist = ["autoclean_cities_vanilla.esp","autoclean_cities_TR.ESP","Cyrodiil_Grass.ESP","Sky_Main_Grass.esp","TR_Data.esm","Tamriel_Data.esm","Better Heads Bloodmoon addon.esm","Better Heads Tribunal addon.esm","Better Heads.esm","OAAB_Data.esm","Better Clothes_v1.1.esp","Better Bodies.esp"]
#  Map color control settings, not really fiddled with this beyond making them available
# controls coloring for cells, min value 0 max value should be less than maxbrightness, default 10
minbrightness = 5
# sensible values between ~100 and 200, min is a value above minbrightness, max 255. No checks or guard rails. Lower values produce more muted colors, default 200
maxbrightness = 200
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
# add empty cells to the exterior cell list. This will make that list VERY long and the program VERY slow.
addemptycells = False
# color overrides, can add your own here or change colors, just copy one of the earlier lines, color format is "modname":"web/hex RGB". CASE sEnSItIvE.
coloroverride = {}
coloroverride.update({"Morrowind.esm":"002000"})
coloroverride.update({"TR_Mainland.esm":"000040"})
coloroverride.update({"TR_Restexteriors.ESP":"400000"})
coloroverride.update({"Bloodmoon.esm":"003030"})
coloroverride.update({"Solstheim Tomb of The Snow Prince.esm":"300030"})
coloroverride.update({"Cyr_Main.esm":"909000"})
coloroverride.update({"Sky_Main.esm":"001060"})
# the default name of the exported file (THIS SWITCH DOES NOTHING CURRENTLY)
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





html_header = """
<!DOCTYPE html>
<HTML>
<HEAD>
<title>Morrowind Modmapper v"""+str(version)+"""+</title>
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
  font-weight: bold;
  text-decoration: normal;
}

a.linkstuff:visited {
  color: #a0a0a0; !important;
  font-weight: bold;
  text-decoration: normal;
}

a.linkstuff:hover {
  color: #c0c0c0; !important;
  font-weight: bold;
  text-decoration: normal;
}

a.linkstuff:active {
  color: #b0b0b0; !important;
  font-weight: bold;
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
  font-weight: bold;
  text-decoration: none;
  color: ff0000;
}
a:active {
  color: #909090;
  text-decoration: none;
} 

table {
  width: 100%;
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
  font-weight: bold;
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
  border: 1px solid #a0a0a0;
  margin-bottom: 12px;
  display: inline;
  margin-left: auto;
  margin-right: auto;
  display: inline;
  width: 100%;
  border-collapse: separate;
}

.intexttable a {
  display: inline;
  font-weight: normal;
  background-color: #101010;
  color: #808080;
}

.intexttable td:hover {
  font-weight: normal;
  background-color: #101010;
  color: #808080;
}

.intexttable a:hover {
  font-weight: bold;
  background-color: #101010;
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

intexttableopen = """

    <table class="intexttable">
    """

intexttableclose = """
</table>
<script>
function intextsearch() {
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("intextinput");
  filter = input.value.toUpperCase();
  table = document.getElementById("intexttable");
  tr = table.getElementsByTagName("tr");
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
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
intcelllist = ""
maxmodcellist = 0
tes3convversion = 0
interiorcell = False
generationdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
global textcolors
textcolors = "000000"


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
    valuestep = stepmodifier*(255/maxmodcellist)
    if mymodcount <= lowmodcount and not "Morrowind.esm" in mymodlist and not "Bloodmoon.esm" in mymodlist and lowmodcountcontrastincrease:
        valuestep += 15
    finalcolorincrease = min(int(basevalue+(mymodcount*valuestep)),255)
    for items in mymodlist:
        currentmod = items
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
if overridetr:
    if "TR_Update.ESP" in esplist:
        esplist.insert(0, esplist.pop(esplist.index("TR_Update.ESP")))
    if "TR_Restexteriors.ESP" in esplist:
        esplist.insert(0, esplist.pop(esplist.index("TR_Restexteriors.ESP")))
    if "TR_Mainland.esm" in esplist:
        esplist.insert(0, esplist.pop(esplist.index("TR_Mainland.esm")))
if "Solstheim Tomb of The Snow Prince.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Solstheim Tomb of The Snow Prince.esm")))   
if "Siege at Firemoth.esp" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Siege at Firemoth.esp")))    
if "Tribunal.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Tribunal.esm")))
if "Bloodmoon.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Bloodmoon.esm")))
if "Morrowind.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Morrowind.esm")))


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
                        if keys["data"]["grid"][0] > tablexmax:
                            tablexmax = keys["data"]["grid"][0]
                        if keys["data"]["grid"][1] < tableymin:
                            tableymin = keys["data"]["grid"][1]
                        if keys["data"]["grid"][1] > tableymax:
                            tableymax = keys["data"]["grid"][1]
# TODO: fix up this list/dict mess, I started using one and switched to the other, then ended up using both. Shitshow. A working shitshow but still.
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
                        intcellname = ""
                        if tes3convversion == 0:
                            intcellname = keys["id"]
                        else:
                            intcellname = keys["name"]
                        if intcellname not in masterintdict:
                            masterintdict[intcellname] = str(files)
                            if moreinfo:
                                print("new int cell",intcellname)
                        else:
                            intcelllist = masterintdict[intcellname]
                            intcelllist = intcelllist + ", " + files
                            masterintdict[intcellname] = intcelllist
                    interiorcell = False
        filecounter+=1
    else:
        print("skipping file",filecounter,"of",len(esplist),":",files,"(excludelist)")
        filecounter+=1
        excludecounter+=1

print("Sorting through mods and assembling tables, this will take a while...")

tablexmin = tablexmin - tableborder
tablexmax = tablexmax + tableborder
tableymin = tableymin - tableborder
tableymax = tableymax + tableborder
tablewidth = int(abs(tablexmax)+abs(tablexmin)+1)
tablelength = int(abs(tableymax)+abs(tableymin)+1)
midvaluex = int(tablexmin+abs(tablewidth/2))
midvaluey = int(tableymin+abs(tablelength/2))

if moreinfo:
    print("cell x min:",tablexmin,"cells x max",tablexmax,"cell y min",tableymin,"cell y max",tableymax,"tableborder",tableborder)
    print("calculated table width",tablewidth,"calculated table length",tablelength)

found = False
lookup = []
table = []
table.append("""</table>""")
tablecounter = 0
tablerows = 0
tablecolumns = 0
tooltipdata = ""
formattedextlist = ""
while tablerows < tablelength:
    print("Assembling map row",tablerows,"of",(tablelength-1),"(",(tablewidth-1),"columns/cells per row)")
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
                limittooltiplimit = 30
                nexusmodlink = ""
                extcelldatamodlist = ""
                nexusmodslink = ""
                # take the list of mod affecting cell, go through them 1 by 1
                for bunchofmods in modifyingmodlist:
                    foundthemod= False
                    #now take zipfiles in the zipdict and go through them one by one
                    for allthezips in myzipdict:
                        # get the list of mods in the current zipfile
                        listofzipmods = myzipdict[allthezips]
                        #go through each individual mod and try to match to the outer loop mod we started with
                        for individualmods in listofzipmods:
                            # I DON'T KNOW ANYMORE IF ONE OF THESE THINGS MATCHES THE OTHER ITS FINE. I SAID ITS FINE.
                            if bunchofmods in individualmods or bunchofmods in listofzipmods or individualmods in bunchofmods:
                                foundthemod = True
                                nexusmodslink = None
                                try:
                                    nexusmodlink = mylinkdict[allthezips]
                                    nexusmodlink = "https://www.nexusmods.com/morrowind/mods/"+str(nexusmodlink)
                                    if moreinfo:
                                        print("nexus link for",bunchofmods,"is",nexusmodlink,"zip file",allthezips)
                                except:
                                    foundthemod = False
                            if foundthemod:
                                break
                        if foundthemod:
                            break
                    if foundthemod and bunchofmods != "Morrowind.esm" and bunchofmods != "Bloodmoon.esm" and bunchofmods != "Tribunal.esm":
                        extcelldatamodlist += """<a class=\"extlink\" href=\""""+str(nexusmodlink)+"""\" target=\"_blank\">"""+str(bunchofmods)+"""</a>, """
                    else:
                        #print("unable to find",bunchofmods)
                        extcelldatamodlist += str(bunchofmods)+""", """
                    foundthemod=False
                    nexusmodslink=""
                if limittooltip and modcount > limittooltiplimit:
                    tooltipdisplaymodlist = modifyingmodlist[:limittooltiplimit]
                    tooltipdisplaymodlist.append(" <br>(tooltip limited to "+str(limittooltiplimit)+" of "+str(modcount)+" mods, click cell to see all)")
                else:
                    tooltipdisplaymodlist = modifyingmodlist
                tooltipdata = """cell: <b>"""+str(values)+"""</b> ("""+str(modcount)+""" mods)<BR>mods: """+str(tooltipdisplaymodlist)
                formattedextlist += """<tr><td><a class=\"extlink\" href=\"index.html#map"""+str(values)+"""\" id=\""""+str(values)+"""\">cell: <b>"""+str(values)+"""</b></a> ("""+str(modcount)+""" mods)<BR>mods: """+str(extcelldatamodlist)+"""</td></tr>\n"""
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
        if found:
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

print("generating interior list for "+str(len(masterintdict))+" interior cells.")
formattedintlist = ""
formattedintlist += intexttableopen

masterintdict = dict(sorted(masterintdict.items())) 
for items in masterintdict:
    modcount = str(masterintdict[items])
    modcount = len(modcount.split(","))
    

    # for bunchofmods in modifyingmodlist:
        # foundthezip = False
        # foundthemod= False
        # #now take zipfiles in the zipdict and go through them one by one
        # for allthezips in myzipdict:
            # # get the list of mods in the current zipfile
            # listofzipmods = myzipdict[allthezips]
            # #go through each individual mod
            # foundthemod = False
            # for individualmods in listofzipmods:
                # #print("does",individualmods,"match",bunchofmods")
                # if bunchofmods in individualmods:
                    # #print("the mod",bunchofmods,"was found in",allthezips)
                    # if allthezips in mylinkdict.keys():
                        # #print("nexusmodlink is", mylinkdict[allthezips])
                        # #print("nexusmodlink is ", mylinkdict[findmod])
                        # nexusmodlink = mylinkdict[allthezips]
                        # nexusmodlink = "https://www.nexusmods.com/morrowind/mods/"+str(nexusmodlink)
                        # #print(nexusmodlink)
                        # extcelldatamodlist += """<a href=\""""+str(nexusmodlink)+"""\">"""+str(bunchofmods)+"""</a>, """
                        # foundthemod = True
                # else:
                        # extcelldatamodlist += str(bunchofmods)+""", """
                        # foundthemod = True
                # if foundthemod:
                    # break
            # if foundthemod:
                # foundthemod= False
                # break





    formattedintlist += """<tr><td>Cell: <b>"""+str(items)+"""</b> ("""+str(modcount)+""" mods)<BR>Mods: """+str(masterintdict[items])+"""</td></tr>\n"""
formattedintlist += intexttableclose 

print("exporting HTML")

html_body = ""
html_int_body = ""
html_ext_body = ""

html_allpage_navbar_start = """
<nav class="nav">
<div class="flex-container">
<h2 class="logo"><a href="index.html#map["""+str(midvaluex)+""", """+str(midvaluey)+"""]" title="jump to map center (more or less)">Morrowind Modmapper """+str(version)+"""</a></h2>"""

html_mainpage_navbar_mid = """Last ran on """+str(generationdate)+""", mapped """+str(len(esplist))+""" files."""
if excludecounter > 0:
    html_mainpage_navbar_mid += """ Skipped """+str(excludecounter)+""" files on the exclude list. """
if failcounter > 0:
    html_mainpage_navbar_mid += """ Failed to convert """+str(failcounter)+""" mods."""+str(failedmodlist)

html_intextpage_navbar_mid = """    <input type="text" id="intextinput" onkeyup="intextsearch()" placeholder="Filter cells or mods.." title="Type something">"""

html_allpage_navbar_end = """
    <ul>
      <li><a href="index.html#map["""+str(midvaluex)+""", """+str(midvaluey)+"""]" title="jump to map center (more or less)">Map</a></li>
      <li><a href="modmapper_interiors.html" title="open page of Interior cells">Interiors</a></li>
      <li><a href="modmapper_exteriors.html" title="open page of Exterior cells">Exteriors</a></li>
      <li><a href="https://www.nexusmods.com/morrowind/mods/53069" title="NexusMods mod page (new tab)" target="_blank">NexusMods</a></li>
      <li><a href="https://github.com/acidzebra/modmapper" title="Modmapper GitHub page (new tab)" target="_blank">Github</a></li>
    </ul>
  </div>
</nav>
"""

if splitpages:
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
    i = 0
    while i < 6:
        html_int_body += """<br>"""
        i+=1
    html_int_body += formattedintlist
    interior_output = html_header+html_int_body+html_footer
    # ext page
    html_ext_body += html_allpage_navbar_start
    html_ext_body += html_intextpage_navbar_mid
    html_ext_body += html_allpage_navbar_end
    i = 0
    while i < 6:
        html_ext_body += """<br>"""
        i+=1
    html_ext_body += intexttableopen
    html_ext_body += formattedextlist
    html_ext_body += intexttableclose
    exterior_output = html_header+html_ext_body+html_footer
    html_file= open("index.html","w")
    html_file.write(index_output)
    html_file.close()
    html_file= open("modmapper_interiors.html","w")
    html_file.write(interior_output)
    html_file.close()
    html_file= open("modmapper_exteriors.html","w")
    html_file.write(exterior_output)
    html_file.close()
else:
    html_body += "".join(table)
    html_body += formattedextlist
    html_body += formattedintlist
    index_output = html_header+html_body+html_footer
    html_file= open("index.html","w")
    html_file.write(index_output)
    html_file.close()



print("all done! I hope you enjoy modmapper.")

# Copyright © 2023 acidzebra

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.