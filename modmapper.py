#!/usr/bin/env python

# Modmapper for Morrowind
# Modmapper for Morrowind
version = "0.7b4"
#
# examines all mods in a folder and builds a HTML file with a map showing and linking to exterior cell details, specifically which mods modify that cell.
# additionally provides list of interior cells with a list of mods modifying them.
#
# usage: put modmapper.py, tes3conv.exe and the mods you want to examine all in a folder
# (or just dump modmapper.py and tes3conv.exe in your data folder, that's what I do)
#
# run python modmapper.py "path-to-modfolder"
# 0.1 - initial release
# 0.2 - a little code cleanup and some cosmetic fixes (forgot to close a HTML tag), made esp/esm search case insensitive because some monsters name their file something.EsM
# 0.3 - added hacky support for both rfuzzo's and G7's versions of tes3conv.exe css improvements - cell lights up on hover, entire cell (when linked) is now clickable. Might not work on all browsers.
# 0.4 - missed interior flag(s?), added, shrunk table a little, made highlighted cell white to avoid clash with gray cells,cleaned up the version check code a bit
# 0.5 - implemented random colors, increased contrast for cells with low modcount, got rid of stupid tooltip pointer since I couldn't get it to point to the cell itself, made sure mw.esm and bm.esm load first if present (to preserve color overrides)
# 0.6 - more map stuff, some new user switches for map color control, brought back color overrides now that randomness seems to work
# 0.7 - export now defaults to index.html instead of modmapper.html, split out ints and exts to separate export files (as the main file is getting chunky), some more config switches, search/text filters on interior and exterior pages, some css/presentation cleanup
#
# not tested on anything except Windows OS+(open)MW, English-language versions.

import io
import json
import sys
from os import listdir, path, remove, system
from random import randrange
from datetime import datetime
import static_config as conf
import html_template as html

basecolorhex = masterintdict = mastermoddict = {}
intcelllist = modcelllist = failedmodlist = ""
modcelltable = esplist = []

failcounter = excludecounter = tablexmin = tablexmax = tableymax = tableymin = maxmodcelllist = tes3convversion = 0
filecounter = 1

interiorcell = False
generationdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

# Somewhat unfamiliar with the `global` keyword but seems unnecessary in a monoscript
global textcolors
textcolors = "000000"

def int2hex(x):
    """
    Converts an integer into hex representation without the leading 0x, e.g.
    25 returns 19
    """
    val = hex(x)[2:]
    val = "0"+val if len(val)<2 else val
    return val

def calcoutputcellcolor(mymodcount,mymodlist):
    """
    What the fuck is happening here oh my god
    """
    # Redeclaration ?
    # global textcolors

    # Bool determining if mod was found?
    foundmod = False
    # Looks like a static color value
    returnvalue = "606060"

    #Based ? Idk
    basevalue = 0

    # Current mod being evaluated ?
    currentmod = ""

    # Profit
    valuestep = conf.stepmodifier*(250/maxmodcellist)

    # On short load orders, conditionally increase the contrast of this cell (the literal cell represented by the cell in the table
    # [I hate this terminology])
    if mymodcount <= conf.lowmodcount and not "Morrowind.esm" in mymodlist and not "Bloodmoon.esm" in mymodlist and conf.lowmodcountcontrastincrease:
        valuestep += 10

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
            reductionfactor = 2
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

            # Dead code? Oh god I just realized the indentation is wrong
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
if not path.isdir(target_folder):
    print("FATAL: target directory \"",target_folder,"\"does not exist.")
    sys.exit()

if not path.isfile("tes3conv.exe"):
    print("FATAL: cannot find path to tes3conv.exe, is it in the same folder as this script?")
    sys.exit()

# esplist += [each for each in listdir(target_folder) if each.lower().endswith('.esm')]
# I'm kind skeptical about this but we'll have to test it at runtime, fam
try:
    esplist += [filename for filename in listdir(target_folder) if filename.lower().rsplit('.')[1] in ["esp", "esm", "omwaddon"]]
except KeyError as badKey:
    print("Bad key at " + badKey)
# esplist += [each for each in listdir(target_folder) if each.lower().endswith('.esp') or each.lower().endswith('.esm')]
esplist = sorted(esplist, key=str.casefold)
if conf.overridetr:
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
    if files not in conf.excludelist:
        # Save for later to dedupe below
        # colors = [randrange(conf.minbrightness, conf.maxbrightness) for _ in range(3)]
        colr = int2hex(randrange(conf.minbrightness, conf.maxbrightness))
        colg = int2hex(randrange(conf.minbrightness, conf.maxbrightness))
        colb = int2hex(randrange(conf.minbrightness, conf.maxbrightness))
        if files in conf.coloroverride:
            hexcolors = (conf.coloroverride[files])
            colr = hexcolors[:2]
            colg = hexcolors[:-2]
            colg = colg[2:]
            colb = hexcolors[4:]
        if files not in basecolorhex:
            basecolorhex.update({files:str(colr)+str(colg)+str(colb)})
        tes3convversion = 0
        jsonfilename = files[:-4]+".json"
        if conf.deletemodjson and path.isfile(str(jsonfilename)):
            remove(jsonfilename)
        if not path.isfile(str(jsonfilename)):
            try:
                target = "tes3conv.exe \""+str(files)+"\" \""+str(jsonfilename)+"\""
                print("running",target)
                system(target)
            except Exception as e:
                print("unable to convert mod to json: "+repr(e))
        if not path.isfile(str(jsonfilename)):
            failcounter+=1
            failedmodlist = failedmodlist + str(files) + " "
        if path.isfile(str(jsonfilename)):
            f = io.open(jsonfilename, mode="r", encoding="utf-8")
            espfile_contents = f.read()
            modfile_parsed_json = json.loads(espfile_contents)
            f.close()
            del espfile_contents
            if conf.deletemodjson:
                remove(jsonfilename)
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
                            if conf.moreinfo:
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
                            if conf.moreinfo:
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
tablexmin = tablexmin - conf.tableborder
tablexmax = tablexmax + conf.tableborder
tableymin = tableymin - conf.tableborder
tableymax = tableymax + conf.tableborder
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
                formattedextlist = formattedextlist + """<tr><td><a href=\"index.html#map"""+str(values)+"""\" id=\""""+str(values)+"""\" class="linkstuff">cell: <b>"""+str(values)+"""</b></a><BR>mods: """+str(modifyingmodlist)+"""</td></tr>\n"""
            if found:
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
            td.append("""<td bgcolor=#"""+str(conf.watercolor)+""" style=\"color:#"""+conf.watertextcolor+""";\"><div class="content"><a id=\"map["""+cellx+""", """+celly+"""]\">"""+str(paddingleft)+"["+cellx+""",<BR>"""+celly+"]"+str(paddingright)+"""</a></div></td>\n""")

            # This variable *is* defined, but seeingly is complaining due to other factors
            if addemptycells:
                formattedextlist = formattedextlist + """<tr><td><a href=\"index.html#map["""+cellx+""", """+celly+"""]\" id=\"["""+cellx+""", """+celly+"""]\" class="linkstuff">cell: <b>["""+cellx+""", """+celly+"""]</b></a><BR>mods: EMPTY CELL</td></tr>"""
        found = False
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
    formattedintlist += """<tr><span class="tooltiptext"><td>Cell: <b>"""+str(items)+"""</b><BR>Mods: """+str(masterintdict[items])+"""</td></span></tr>\n"""
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
    html_mainpage_navbar_mid += """ Failed to convert """+str(failcounter)+""" mods."""

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


if conf.splitpages:
    html_body = html_body+"".join(table)
    index_output = html.header+html_body+html.footer

    html_int_body = html.navbarheader
    i = 0
    while i < 6:
        html_int_body += """<br>"""
        i+=1
    html_int_body += formattedintlist
    interior_output = html.header+html_int_body+html.footer

    html_ext_body += html_allpage_navbar_start
    html_ext_body += html_intextpage_navbar_mid
    html_ext_body += html_allpage_navbar_end
    i = 0
    while i < 6:
        html_ext_body += """<br>"""
        i+=1
    html_ext_body += html.intexttableopen
    html_ext_body += formattedextlist
    html_ext_body += html.intexttableclose
    exterior_output = html.header+html_ext_body+html.footer
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
    index_output = html.header+html_body+html.footer
    Html_file= open("index.html","w")
    Html_file.write(index_output)
    Html_file.close()



print("all done! I hope you enjoy modmapper.")

# Copyright © 2023 acidzebra

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
