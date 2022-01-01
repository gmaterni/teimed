#!/usr/bin/env python3
# coding: utf-8
import sys
from io import StringIO

TEI_HEAD_OPEN="""
<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml"
	schematypens="http://purl.oclc.org/dsdl/schematron"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
      <fileDesc>
         <titleStmt>
            <title>Title</title>
         </titleStmt>
         <publicationStmt>
            Publication Information
         </publicationStmt>
         <sourceDesc>
            Information about the source
         </sourceDesc>
      </fileDesc>
  </teiHeader>
  <text>
"""

TEI_HEAD_CLOSE="""
  </text>
</TEI>
"""

def add_tei_head(xml=""):
    try:
        f = StringIO()
        f.write(TEI_HEAD_OPEN.strip())
        f.write(xml)
        f.write(TEI_HEAD_CLOSE)
        xml_tei = f.getvalue()
        f.close()
    except Exception as e:
        msg = f'\nERROR. tei_head.py\n {e}'
        print(msg)
        sys.exit(msg)
    else:
        return xml_tei

