# Please leave me alone <3
version = "0.7b4"

# User-configurable variables, defaults should be fine
# add empty cells to the exterior cell list. This will make that list VERY long and the program VERY slow.
addemptycells = False

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

# HTML background and text color
bgcolor = "101010"
txcolor = "808080"
# ---

header = """
<!DOCTYPE html>
<HTML>
<HEAD>
<title>Morrowind Modmapper v"""+str(version)+"""+</title>
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
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
  width: 1500%;
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

#intexttable {
  border-collapse: collapse;
  width: 100%;
  border: 1px solid #ddd;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 80%;
}

#intexttable th, #intexttable td {
  text-align: left;
  padding: 12px;
  font-weight: normal;
  text-decoration: none;
  color: #d0d0d0;
}

#intexttable tr {
  border-bottom: 1px solid #ddd;
}

#intexttable tr.header, #intexttable tr:hover {
  background-color: #ocococ;
}
  </STYLE>
</HEAD>
<BODY>
"""

footer = """
</div>
</BODY>
</HTML>
"""


intexttableopen = """

    <table id="intexttable">
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
