# background and text color
bgcolor = "101010"
txcolor = "808080"

from modmapper import version

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
