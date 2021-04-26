esempio:
progettto: flor_html
witnes: par1

N.B.
nelle applicazioni i fllag
-i indicano file di input
-o file di OUTPUT
-wa output in modalità w/a (write / append)
-c,-t  file di configurazione

Negli script con argomenti particolarmente lunghi
o numerosi è possubile andare a cao suandop \
es.

script.py \
-x arg1 \
-y arg2  \
..

======================================
situarsi nella dir flori_html
lanciare:

pej_mgr.py prj/par1.json

sone esegue le seguenti elaborazioni

prjmgr.py prj/par1_xml.json
prjmgr.py prj/par1_syn.json
prjmgr.py prj/par1_syn_pannel.json
prjmgr.py prj/par1_txt.json
prjmgr.py prj/par1_txt_pannel.jso

INPUT
flori_html/xml/par1.xml

OUTPUT
flori_html/html/par1/txt/par1.html
flori_html/html/par1/txt/eps01.html
..
flori_html/html/par1/txt/eps0n.html

flori_html/html/par1/syn/par1.html
flori_html/html/par1/syn/eps01.html
..
flori_html/html/par1/syn/eps0n.html

================================
elaborazioni singole
================================
prjmgr.py prj/par1_xml.json
esegue:
splitteixml.py -i xml/par1.xml -o xml/par1/ -m par1
-------------------------------
prjmgr.py prj/par1_syn.json

writehtml.py \
-o html/par1/syn/$F.html \
-i '<div id=\par1_dipl_id\ class=\text_pannel tei_dipl\>' \
-wa w

teixml2html.py \
-i xml/par1/$F.xml \
-o html/par1/syn/$F.html \
-c prj_teimcfg/par1_dipl_syn.json \
-wa a 

writehtml.py \
-o html/par1/syn/$F.html \
-i '</div><div id=\par1_int_id\ class=\text_pannel tei_int\>' \
-wa a

teixml2html.py
-i xml/par1/$F.xml
-o html/par1/syn/$F.html
-c prj_teimcfg/par1_inter_syn.json
-wa a 

writehtml.py
-o html/par1/syn/$F.html
-i '</div>'
-wa a
-------------------------------
prjmgr.py prj/par1_syn_pannel.json
 
writehtml.py
-o html/tor1/syn/tor1.html
-i '<div id=\tor1_dip_id\ class=\text_pannel tei_dip\>'
-wa w

teixml2html.py
-i xml/tor1/tor1_list.xml
-o html/tor1/syn/tor1.html
-c prj_teimcfg/list_dipl_syn.json
-wa a

writehtml.py
-o html/tor1/syn/tor1.html
-i '</div>
<div id=\tor1_int_id\ class=\text_pannel tei_int\>'
-wa a

teixml2html.py
-i xml/tor1/tor1_list.xml
-o html/tor1/syn/tor1.html
-c prj_teimcfg/list_inter_syn.json
-wa a

writehtml.py
-o html/tor1/syn/tor1.html
-i '</div>'
-wa a
-------------------------------
prjmgr.py prj/par1_txt.json

writehtml.py \
-o html/par1/txt/$F.html \
-i '<div id=\par1_dipl_id\ class=\text_pannel tei_dipl\>' \
-wa w

teixml2html.py \
-i xml/par1/$F.xml \
-o html/par1/txt/$F.html \
-c prj_teimcfg/par1_dipl_txt.json \
-wa a 

writehtml.py \
-o html/par1/txt/$F.html \
-i '</div><div id=\par1_int_id\ class=\text_pannel tei_int\>' \
-wa a

teixml2html.py
-i xml/par1/$F.xml
-o html/par1/txt/$F.html
-c prj_teimcfg/par1_inter_txt.json
-wa a 

writehtml.py
-o html/par1/txt/$F.html
-i '</div>'
-wa a
-------------------------------
prjmgr.py prj/par1_txt_pannel.json
 
writehtml.py
-o html/tor1/txt/tor1.html
-i '<div id=\tor1_dip_id\ class=\text_pannel tei_dip\>'
-wa w

teixml2html.py
-i xml/tor1/tor1_list.xml
-o html/tor1/txt/tor1.html
-c prj_teimcfg/list_dipl_txt.json
-wa a

writehtml.py
-o html/tor1/txt/tor1.html
-i '</div>
<div id=\tor1_int_id\ class=\text_pannel tei_int\>'
-wa a

teixml2html.py
-i xml/tor1/tor1_list.xml
-o html/tor1/txt/tor1.html
-c prj_teimcfg/list_inter_txt.json
-wa a

writehtml.py
-o html/tor1/txt/tor1.html
-i '</div>'
-wa a
======================================
files dei arametri per le singole applicazioni in
flori_html/prj_teimcfg
=======================================
par1_dipl_syn.json
{
  "html_params": {
    "_MAN_": "par1",
    "text_null": "",
    "_QA_": "\"",
    "_QC_": "\""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "d:syn",
  "dipl_inter": "d",
  "before_id": "d"
}
--------------------------------------
par1_dipl_txt.json
{
  "html_params": {
    "_MAN_": "par1",
    "text_null": "",
    "_QA_": "\"",
    "_QC_": "\""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "d:txt",
  "dipl_inter": "d",
  "before_id": "d"
}
--------------------------------------
par1_inter_syn.json
{
  "html_params": {
    "text_null": "",
    "_QA_": "\"",
    "_QC_": "\""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "i:syn",
  "dipl_inter": "i",
  "before_id": "i"
}
--------------------------------------
par1_inter_txt.json
{
  "html_params": {
    "text_null": "",
    "_QA_": "\"",
    "_QC_": "\""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "i:txt",
  "dipl_inter": "i",
  "before_id": "i"
}
--------------------------------------
list_dipl_syn.json
{
  "html_params": {
    "text_null": "",
    "<null>": "",
    "</null>": ""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "d:syn",
  "dipl_inter": "d",
  "before_id": "d"
}
--------------------------------------
list_dipl_txt.json
{
  "html_params": {
    "text_null": "",
    "<null>": "",
    "</null>": ""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "d",
  "dipl_inter": "d",
  "before_id": "d"
}
--------------------------------------
list_inter_syn.json
{
  "html_params": {
    "text_null": "",
    "<null>": "",
    "</null>": ""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "i:syn",
  "dipl_inter": "i",
  "before_id": "i"
}
--------------------------------------
list_inter_txt.json
{
  "html_params": {
    "text_null": "",
    "<null>": "",
    "</null>": ""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "i",
  "dipl_inter": "i",
  "before_id": "i"
}
