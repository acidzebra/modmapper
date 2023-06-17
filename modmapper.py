# Modmapper for Morrowind
version = "0.3"
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
# 0.3.1 - now that the panic has subsided, cleaned up the version check a little. Should probably implement a function sometime.

# not tested on anything except Windows OS+(open)MW, English-language versions.

# User-configurable variables, defaults should be fine

# produces a LOT of noise if turned on (pipe output to a file)
moreinfo = False
# normally modmapper cleans up after itself, set to False to disable (for repeated runs for instance)
deletemodjson = True
# some padding around the map
tableborder = 5
# skip these mods if found. You can add any mods you don't want on the map here.
excludelist = ["autoclean_cities_vanilla.esp","autoclean_cities_TR.ESP","Cyrodiil_Grass.ESP","Sky_Main_Grass.esp"]

# ---

import json
import io
import sys
import os
from os import listdir
from os.path import isfile, join

html_header = """
<HTML>
<HEADER>
<STYLE>
body {
  font-family: Arial, Helvetica, sans-serif;
}
a:link {
  color: ffff00;
  text-decoration: none;
}
a:visited {
  color: ffff00;
  text-decoration: none;
}
a:hover {
  background-color: #606060;
  font-weight: bold;
  text-decoration: none;
  color: ffffff;
}
a:active {
  color: ffff00;
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
}
td:hover {
  background-color: #606060;
  font-weight: bold;
  color: ffffff;
}
td a {
  display: inline-block;
  height:100%;
  width:100%;
}
.tooltip {
  position: relative;
  display: inline-block;
}
.tooltip .tooltiptext {
  font-family: Arial, Helvetica, sans-serif;
  white-space: normal;
  font-weight: normal;
  visibility: hidden;
  width: 1000%;
  height: 400%;
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
.tooltip .tooltiptext::after {
  white-space: normal;
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: #555 transparent transparent transparent;
}
.tooltip:hover .tooltiptext {
  white-space: normal;
  visibility: visible;
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
def int2hex(x):
    val = hex(x)[2:]
    val = "0"+val if len(val)<2 else val
    return val
    
def calcoutputcellcolor(mymodcount,mymodlist):
    satincrease = 1.5
    returnvalue = "606060"
    basevalue = 20
    override = False
    satincrease = int(8*(satincrease*mymodcount)+10)
    if satincrease > 255:
        satincrease = 255
    if satincrease < basevalue:
        satincrease = basevalue
    finalcolorincrease = str(int2hex(satincrease))
# TODO: this is a mess, rewrite
    for items in mymodlist:
        if "Morrowind.esm" in items or "Bloodmoon.esm" in items:
            returnvalue = "00"+str(finalcolorincrease)+"00"
            override = True
        elif "TR_" in items and not override:
            returnvalue = str(finalcolorincrease)+"0000"
        elif "Sky_" in items and not override:
            returnvalue = "0020"+str(finalcolorincrease)
        elif "Cyr_" in items and not override:
            returnvalue = str(finalcolorincrease)+str(finalcolorincrease)+"00"
        elif "Wyrmhaven" in items and not override:
            returnvalue = str(finalcolorincrease)+"00"+str(finalcolorincrease)
        elif "MD_Azurian" in items and not override:
            returnvalue = str(finalcolorincrease)+str(finalcolorincrease)+str(finalcolorincrease)
        if override:
            break
    if override:
        returnvalue = "00"+str(finalcolorincrease)+"00"
        override = False
    return returnvalue

modlist = []
esplist = []
modcelltable = []
mastermoddict = {}
masterintdict = {}
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
tes3convversion = 0
interiorcell = False
for files in esplist:
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
                    #print(tes3convversioncheck)
                    if tes3convversioncheck.isdigit():
                        tes3convversion = 0
                        if int(tes3convversioncheck) == 5 or int(tes3convversioncheck) == 3 or int(tes3convversioncheck) ==  1 or int(tes3convversioncheck) == 7 or int(tes3convversioncheck) == 135:
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
                  
                            
        filecounter+=1
    else:
        print("skipping file",filecounter,"of",len(esplist),":",files,"(excludelist)")
        filecounter+=1
        excludecounter+=1

mastermoddict = dict(sorted(mastermoddict.items()))  
dedupe_modcelltable = list()
for item in modcelltable:
    if item not in dedupe_modcelltable:
        dedupe_modcelltable.append(item)
modcelltable = []
modcelltable = dedupe_modcelltable

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
            td.append("""<td bgcolor=#"""+str(docellcolor)+""" opacity=1><div class="content"><div class="tooltip"><a href=\"#"""+str(values)+"""\">"""+str(paddingleft)+"["+str(tablecolumns-abs(tablexmin))+""",<BR>"""+str(tablerows-abs(tableymin))+"]"+str(paddingright)+"""</a><span class="tooltiptext">"""+tooltipdata+"""</span></div></div></td>\n""")
        else:
            td.append("""<td bgcolor=#2B65EC opacity=1 style=\"color:#000000;\"><div class="content">"""+str(paddingleft)+"["+str(tablecolumns-abs(tablexmin))+""",<BR>"""+str(tablerows-abs(tableymin))+"]"+str(paddingright)+"""</div></td>\n""")
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
html_body = """<p><b>MODMAPPER 0.1</b><br>Examined """+str(len(esplist))+""" files, skipped """+str(excludecounter)+""" files on the exclude list. Failed to convert """+str(failcounter)+""" mods: """+str(failedmodlist)+"""</p>"""
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