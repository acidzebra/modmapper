# Modmapper for Morrowind
version = "0.5"
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
# 0.6 - more map stuff, some new user switches for map color control, brough back color overrides now that randomness seems to work
#
# not tested on anything except Windows OS+(open)MW, English-language versions.

# User-configurable variables, defaults should be fine
# produces a LOT of noise if turned on (pipe output to a file)
moreinfo = False
# normally modmapper cleans up after itself, set to False to disable (for repeated runs for instance)
deletemodjson = False
# some padding around the map
tableborder = 2
# whether the TR landmass colors should override other landmass colors (other overlapping mods will be seen as a brightening of the colors), defaults to true because the alternative is a clown car of a map
overridetr = True
# skip these mods if found. You can add any mods you don't want on the map here.
excludelist = ["autoclean_cities_vanilla.esp","autoclean_cities_TR.ESP","Cyrodiil_Grass.ESP","Sky_Main_Grass.esp","TR_Data.esm","Tamriel_Data.esm","Better Heads Bloodmoon addon.esm","Better Heads Tribunal addon.esm","Better Heads.esm","OAAB_Data.esm","Better Clothes_v1.1.esp","Better Bodies.esp"]
#  Map color control settings, not really fiddled with this beyond making them available
# controls coloring for cells, min value 0 max value should be less than maxbrightness, default 10
minbrightness = 10
# sensible values between ~100 and 200, min 11, max 255. No checks or guard rails. Lower values produce more muted colors, default 200
maxbrightness = 200
# improve contrast for cells with few mods affecting them (only for mods, not base game)
lowmodcountcontrastincrease = True
# water/untouched cell color in web/hex RGB
watercolor = "2B65EC"
watertextcolor = "1010ff"
# color overrides, can add your own here or change colors, color format is web/hex RGB
coloroverride = {}
coloroverride.update({"Morrowind.esm":"003000"})
coloroverride.update({"TR_Mainland.esm":"000030"})
coloroverride.update({"TR_Restexteriors.ESP":"300000"})
coloroverride.update({"Bloodmoon.esm":"003030"})
coloroverride.update({"Solstheim Tomb of The Snow Prince.esm":"300030"})
coloroverride.update({"Cyr_Main.esm":"303000"})
# ---  
        
import json
import io
import sys
import os
from os import listdir
from os.path import isfile, join
from random import randrange
from datetime import datetime

html_header = """
<HTML>
<HEADER>
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<STYLE>
body {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 100%;
}

a.linkstuff {
  color: blue; !important;
  font-weight: bold;
  text-decoration: normal;
}

a.linkstuff:visited {
  color: blue; !important;
  font-weight: bold;
  text-decoration: normal;
}

a.linkstuff:hover {
  color: blue; !important;
  font-weight: bold;
  text-decoration: normal;
}

a.linkstuff:active {
  color: blue; !important;
  font-weight: bold;
  text-decoration: normal;
}

a:link {
  color: 000000;
  text-decoration: none;
}
a:visited {
  color: 000000;
  text-decoration: none;
}
a:hover {
  background-color: #ffffff;
  font-weight: bold;
  text-decoration: none;
  color: ff0000;
}
a:active {
  color: 000000;
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
  background-color: #ffffff;
  font-weight: bold;
  color: 000000;
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
</STYLE>
</HEADER>
<BODY>
"""

html_footer = """
</BODY>
</HTML>
"""

modlist = []
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
    basevalue = 10
    currentmod = ""
    valuestep = (245/maxmodcellist)
    if mymodcount <= 5 and not "Morrowind.esm" in mymodlist and not "Bloodmoon.esm" in mymodlist and lowmodcountcontrastincrease:
        valuestep += 10
    finalcolorincrease = min(int(basevalue+(mymodcount*valuestep)),255)
    for items in mymodlist:
        currentmod = items
        if not foundmod and currentmod in basecolorhex:
            found = True
            # the following code is a crime in at least six nations
            hexcolors = (basecolorhex[currentmod])
            colorg= hexcolors[:-2]
            finaloutr=int2hex(min((int((int(hexcolors[:2],16))+finalcolorincrease)), 255))
            finaloutb=int2hex(min((int((int(hexcolors[4:],16))+finalcolorincrease)), 255))
            finaloutg=int2hex(min((int(int(colorg[2:],16)+finalcolorincrease)), 255))
            lumi = min((0.2126*int(finaloutr,16) + 0.7152*int(finaloutg,16) + 0.0722*int(finaloutb,16)),255)
            if lumi <= 120:
                lumi = (lumi-(lumi*0.75))
                if lumi < 0:
                    lumi = 0
            if lumi > 120:
                lumi = (lumi+(lumi*0.75))
            greygradient = int2hex(min(abs(int(255-lumi)),255))
            textcolors = str(greygradient)+str(greygradient)+str(greygradient)
            returnvalue = str(finaloutr)+str(finaloutg)+str(finaloutb)
        if foundmod:
            break
    return returnvalue

try:
    target_folder = sys.argv[1]
    target_folder = str(target_folder)
except:
    print("usage: put mods + modmapper.py + tes3conv.exe in same folder") 
    print("run: python modmapper.py \"target directory\"")
    print("output will be saved as modmapper.html")
    sys.exit()

if not os.path.isdir(target_folder):
    print("FATAL: target directory \"",target_folder,"\"does not exist.")
    sys.exit()

if not os.path.isfile("tes3conv.exe"):
    print("FATAL: cannot find path to tes3conv.exe, is it in the same folder as this script?")
    sys.exit()
    
esplist += [each for each in os.listdir(target_folder) if each.lower().endswith('.esm')]
esplist += [each for each in os.listdir(target_folder) if each.lower().endswith('.esp')]
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
if "Tribunal.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Tribunal.esm")))
if "Bloodmoon.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Bloodmoon.esm")))
if "Morrowind.esm" in esplist:
    esplist.insert(0, esplist.pop(esplist.index("Morrowind.esm")))

for files in esplist:
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
    if files not in excludelist:
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
                if keys["type"] == "Cell" and len(keys["references"])>0:
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
    table.append("""\n\t</tr>\n""")
    td = []
    tablecolumns = 0
    while tablecolumns < tablewidth:
        tooltipdata = ""
        done = 0
        found = 0
        docellcolor = "0099ff"
        for values in modcelltable:
            if values[0] == (tablecolumns-abs(tablexmin)) and values[1] == (tablerows-abs(tableymin)):
                found = True
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
                tooltipdata = """cell: <b>"""+str(values)+"""</b><BR>mods: """+str(modifyingmodlist)
                formattedextlist = formattedextlist + """<BR><p id=\""""+str(values)+"""\"</p>"""+str(tooltipdata)
            if found:
                break
# TODO: this is a truly terrible way to do padding, I should probably manipulate the CSS of the individual table cells instead. BUUUUUT this works for my purposes.
        paddingleft = ""
        paddingright = ""
        if abs(values[0]) < 100:
            paddingleft = " "
        if abs(values[0]) < 10:
            paddingleft = "  "
        if paddingleft and values[0] > -1:
            paddingleft = paddingleft + " "
        if abs(values[1]) < 100:
            paddingright = "  "
        if abs(values[1]) < 10:
            paddingright = "   "
        if paddingright and values[1] > -1:
            paddingright = paddingright + " "
        if found:
            docellcolor = calcoutputcellcolor(modcount,modifyingmodlist)
            td.append("""<td bgcolor=#"""+str(docellcolor)+""" opacity=1 style=\"color:#"""+textcolors+""";\"><div class="content"><div class="tooltip"><a href=\"#"""+str(values)+"""\" style=\"color: #"""+textcolors+""";text-decoration:none;\">"""+str(paddingleft)+"["+str(tablecolumns-abs(tablexmin))+""",<BR>"""+str(tablerows-abs(tableymin))+"]"+str(paddingright)+"""</a><span class="tooltiptext">"""+tooltipdata+"""</span></div></div></td>\n""")
        else:
            td.append("""<td bgcolor=#"""+watercolor+""" opacity=1 style=\"color:#"""+watertextcolor+""";\"><div class="content">"""+str(paddingleft)+"["+str(tablecolumns-abs(tablexmin))+""",<BR>"""+str(tablerows-abs(tableymin))+"]"+str(paddingright)+"""</div></td>\n""")
        found = False
        tablecolumns+=1
    table.append("\t\t"+"".join(td))
    table.append("""\t<tr>\n""")
    tablerows+=1
table.append("""<table>\n""")
table.reverse()

formattedintlist = ""
masterintdict = dict(sorted(masterintdict.items())) 
for items in masterintdict:
    formattedintlist = formattedintlist + str("""<P>Interior Cell: <b>"""+str(items)+"""</b><BR>Mods:"""+str(masterintdict[items])+"""</P>\n""")

print("exporting HTML")
html_body = """<p><b>MODMAPPER """+str(version)+"""</b><br>Last ran on """+str(generationdate)+""", mapped """+str(len(esplist))+""" files, skipped """+str(excludecounter)+""" files on the exclude list. Failed to convert """+str(failcounter)+""" mods: """+str(failedmodlist)+"""<br>"""
html_body = html_body + """<p> Scroll around map with mouse or keyboard. Hover over cells to see mods affecting cell. Click cell to go to details on exterior cell list (use browser back function to return to map position).<BR>"""
html_body = html_body + """You will probably want to scroll a good bit to the right and down, there's a lot of sea out there.<BR>"""
html_body = html_body + """Use browser search to find interior cells or specific mods (example: search for \"guild of\" or \"Akamora\"). Zoom page out with brower zoom function. It's not very responsive or mobile device aware (yet?).<BR>"""
html_body = html_body + """Blue cells with blue text means no game file or mod touches this cell (textureless ocean). Each mod has a random color assigned which will change every time modmapper runs.</p>"""
html_body = html_body + """<p>This is a primitive alpha but it seems to run well enough. Demo <a href="https://acidzebra.github.io/modmapper/" class="linkstuff">here</a>,code <a href = "https://github.com/acidzebra/modmapper" class="linkstuff">here</a>,nexus page <a href="https://www.nexusmods.com/morrowind/mods/53069" class="linkstuff"">here</a>.</p>"""
html_body = html_body+"".join(table)
html_body = html_body+formattedextlist
html_body = html_body+formattedintlist
html_output = html_header+html_body+html_footer

Html_file= open("modmapper.html","w")
Html_file.write(html_output)
Html_file.close()
print("all done! I hope you enjoy modmapper.")

# Copyright © 2023 acidzebra

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.