'''
Created on Oct 9, 2010

@author: Mark V Systems Limited
(c) Copyright 2010 Mark V Systems Limited, All rights reserved.
'''
import csv, io
from lxml import etree
from arelle.FileSource import FileNamedStringIO

CSV = 0
HTML = 1
XML = 2

class View:
    def __init__(self, modelXbrl, outfile, rootElementName, lang=None, style="table"):
        self.modelXbrl = modelXbrl
        self.lang = lang
        if isinstance(outfile, FileNamedStringIO):
            if outfile.fileName in ("html", "xhtml"):
                self.type = HTML
            elif outfile.fileName == "csv":
                self.type = CSV
            else:
                self.type = XML
        elif outfile.endswith(".html") or outfile.endswith(".htm") or outfile.endswith(".xhtml"):
            self.type = HTML
        elif outfile.endswith(".xml"):
            self.type = XML
        else:
            self.type = CSV
        self.outfile = outfile
        self.numHdrCols = 0
        self.treeCols = 0  # set to number of tree columns for auto-tree-columns
        if modelXbrl:
            if not lang: 
                self.lang = modelXbrl.modelManager.defaultLang
        if self.type == CSV:
            if isinstance(self.outfile, FileNamedStringIO):
                self.csvFile = self.outfile
            else:
                self.csvFile = open(outfile, "w", newline='')
            self.csvWriter = csv.writer(self.csvFile, dialect="excel")
        elif self.type == HTML:
            if style == "rendering":
                html = io.StringIO(
'''
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <STYLE type="text/css"> 
            table {font-family:Arial,sans-serif;vertical-align:middle;white-space:normal;}
            th {background:#eee;}
            td {} 
            .tableHdr{border-top:.5pt solid windowtext;border-right:none;border-bottom:none;border-left:.5pt solid windowtext;}
            .zAxisHdr{border-top:.5pt solid windowtext;border-right:.5pt solid windowtext;border-bottom:none;border-left:.5pt solid windowtext;}
            .xAxisSpanLeg,.yAxisSpanLeg,.yAxisSpanArm{border-top:none;border-right:none;border-bottom:none;border-left:.5pt solid windowtext;}
            .xAxisHdrValue{border-top:.5pt solid windowtext;border-right:none;border-bottom:none;border-left:1.0pt solid windowtext;}
            .xAxisHdr{border-top:.5pt solid windowtext;border-right:none;border-bottom:none;border-left:.5pt solid windowtext;} 
            .yAxisHdrWithLeg{vertical-align:middle;border-top:.5pt solid windowtext;border-right:none;border-bottom:none;border-left:.5pt solid windowtext;}
            .yAxisHdrWithChildrenFirst{border-top:none;border-right:none;border-bottom:.5pt solid windowtext;border-left:.5pt solid windowtext;}
            .yAxisHdrAbstract{border-top:.5pt solid windowtext;border-right:none;border-bottom:none;border-left:.5pt solid windowtext;}
            .yAxisHdrAbstractChildrenFirst{border-top:none;border-right:none;border-bottom:.5pt solid windowtext;border-left:.5pt solid windowtext;}
            .yAxisHdr{border-top:.5pt solid windowtext;border-right:none;border-bottom:none;border-left:.5pt solid windowtext;}
            .cell{border-top:1.0pt solid windowtext;border-right:.5pt solid windowtext;border-bottom:.5pt solid windowtext;border-left:.5pt solid windowtext;}
            .blockedCell{border-top:1.0pt solid windowtext;border-right:.5pt solid windowtext;border-bottom:.5pt solid windowtext;border-left:.5pt solid windowtext;background:#eee;}
            .tblCell{border-top:.5pt solid windowtext;border-right:.5pt solid windowtext;border-bottom:.5pt solid windowtext;border-left:.5pt solid windowtext;}
        </STYLE>
    </head>
    <body>
        <table border="1" cellspacing="0" cellpadding="4" style="font-size:8pt;">
        </table>
    </body>
</html>
'''
                )
            else:
                html = io.StringIO(
'''
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <STYLE type="text/css"> 
            table {font-family:Arial,sans-serif;vertical-align:middle;white-space:normal;
                    border-top:.5pt solid windowtext;border-right:1.5pt solid windowtext;border-bottom:1.5pt solid windowtext;border-left:.5pt solid windowtext;}
            th {background:#eee;}
            td {} 
            .tableHdr{border-top:.5pt solid windowtext;border-right:none;border-bottom:.5pt solid windowtext;border-left:.5pt solid windowtext;}
            .rowSpanLeg{width:1.0em;border-top:none;border-right:none;border-bottom:none;border-left:.5pt solid windowtext;}
            .tableCell{border-top:.5pt solid windowtext;border-right:none;border-bottom:none;border-left:.5pt solid windowtext;}
            .tblCell{border-top:.5pt solid windowtext;border-right:none;border-bottom:.5pt solid windowtext;border-left:.5pt solid windowtext;}
        </STYLE>
    </head>
    <body>
        <table cellspacing="0" cellpadding="4" style="font-size:8pt;">
        </table>
    </body>
</html>
'''
                )
            self.xmlDoc = etree.parse(html)
            html.close()
            self.tblElt = None
            for self.tblElt in self.xmlDoc.iter(tag="{http://www.w3.org/1999/xhtml}table"):
                break
        elif self.type == XML:
            html = io.StringIO("<{0}/>".format(rootElementName[0].lower() + rootElementName.title().replace(' ','')[1:]))
            self.xmlDoc = etree.parse(html)
            html.close()
            self.docEltLevels = [self.xmlDoc.getroot()]
        
    def addRow(self, cols, asHeader=False, treeIndent=0, colSpan=1, xmlRowElementName=None, xmlRowEltAttr=None, xmlRowText=None, xmlCol0skipElt=False, xmlColElementNames=None, lastColSpan=None):
        if asHeader and len(cols) > self.numHdrCols:
            self.numHdrCols = len(cols)
        if self.type == CSV:
            self.csvWriter.writerow(cols if not self.treeCols else
                                    ([None for i in range(treeIndent)] +
                                     cols[0:1] + 
                                     [None for i in range(treeIndent, self.treeCols - 1)] +
                                     cols[1:]))
        elif self.type == HTML:
            tr = etree.SubElement(self.tblElt, "{http://www.w3.org/1999/xhtml}tr")
            td = None
            for i, col in enumerate(cols + [None for emptyCol in range(self.numHdrCols - colSpan + 1 - len(cols))]):
                attrib = {}
                if asHeader:
                    attrib["class"] = "tableHdr"
                    colEltTag = "{http://www.w3.org/1999/xhtml}th"
                else:
                    colEltTag = "{http://www.w3.org/1999/xhtml}td"
                    attrib["class"] = "tableCell"
                if i == 0:
                    if self.treeCols - 1 > treeIndent:
                        attrib["colspan"] = str(self.treeCols - treeIndent + colSpan - 1)
                    elif colSpan > 1:
                        attrib["colspan"] = str(colSpan)
                if i == 0 and self.treeCols:
                    for indent in range(treeIndent):
                        etree.SubElement(tr, colEltTag,
                                         attrib={"class":"rowSpanLeg"},
                                         ).text = '&nbsp;'
                td = etree.SubElement(tr, colEltTag, attrib=attrib)
                td.text = str(col) if col else '&nbsp;'
            if lastColSpan and td is not None:
                td.set("colspan", str(lastColSpan))
        elif self.type == XML:
            if asHeader:
                # save column element names
                self.xmlRowElementName = xmlRowElementName or "row"
                self.columnEltNames = [col[0].lower() + col[1:].replace(' ','').replace('&#173;','').replace('-','')
                                       for col in cols]
            else:
                if treeIndent < len(self.docEltLevels) and self.docEltLevels[treeIndent] is not None:
                    parentElt = self.docEltLevels[treeIndent]
                else:
                    # problem, error message? unexpected indent
                    parentElt = self.docEltLevels[0] 
                rowElt = etree.SubElement(parentElt, xmlRowElementName or self.xmlRowElementName, attrib=xmlRowEltAttr)
                if treeIndent + 1 >= len(self.docEltLevels): # extend levels as needed
                    for extraColIndex in range(len(self.docEltLevels) - 1, treeIndent + 1):
                        self.docEltLevels.append(None)
                self.docEltLevels[treeIndent + 1] = rowElt
                if not xmlColElementNames: xmlColElementNames = self.columnEltNames
                if len(cols) == 1 and not xmlCol0skipElt:
                    rowElt.text = xmlRowText if xmlRowText else cols[0]
                else:
                    for i, col in enumerate(cols):
                        if (i != 0 or not xmlCol0skipElt) and col:
                            etree.SubElement(rowElt, xmlColElementNames[i]).text = str(col)
        if asHeader and lastColSpan: 
            self.numHdrCols += lastColSpan - 1
                                
    def close(self):
        if self.type == CSV:
            if not isinstance(self.outfile, FileNamedStringIO):
                self.csvFile.close()
            self.modelXbrl = None
        else:
            try:
                from arelle import XmlUtil
                if isinstance(self.outfile, FileNamedStringIO):
                    fh = self.outfile
                else:
                    fh = open(self.outfile, "w")
                XmlUtil.writexml(fh, self.xmlDoc, encoding="utf-8")
                if not isinstance(self.outfile, FileNamedStringIO):
                    fh.close()
                self.modelXbrl.info("info", _("Saved output html to %(file)s"), file=self.outfile)
            except (IOError, EnvironmentError) as err:
                self.modelXbrl.exception("arelle:htmlIOError", _("Failed to save output html to %(file)s: \s%(error)s"), file=self.outfile, error=err)
            self.modelXbrl = None
            if self.type == HTML:
                self.tblElt = None
            elif self.type == XML:
                self.docEltLevels = None

