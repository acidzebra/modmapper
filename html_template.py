
header = """
<HTML>
<HEAD>
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<STYLE>
body {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 100%;
  background-color: """+conf.bgcolor+""";
  color: """+conf.txcolor+""";
}

a.linkstuff {
  color: a0a0a0; !important;
  font-weight: bold;
  text-decoration: normal;
}

a.linkstuff:visited {
  color: a0a0a0; !important;
  font-weight: bold;
  text-decoration: normal;
}

a.linkstuff:hover {
  color: c0c0c0; !important;
  font-weight: bold;
  text-decoration: normal;
}

a.linkstuff:active {
  color: b0b0b0; !important;
  font-weight: bold;
  text-decoration: normal;
}

a:link {
  color: 909090;
  text-decoration: none;
}
a:visited {
  color: 909090;
  text-decoration: none;
}
a:hover {
  background-color: #909090;
  font-weight: bold;
  text-decoration: none;
  color: ff0000;
}
a:active {
  color: 909090;
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
  color: ff0000;
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
  </STYLE>
</HEAD>
<BODY>

"""

footer = """
</BODY>
</HTML>
"""
