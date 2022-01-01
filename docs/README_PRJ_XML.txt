esempio:
progettto: flor_xml
witnes: par1,ven1

N.B.
nelle applicazioni i fllag
-i      indicano file di input
-o      file di OUTPUT
-c,ty   file di configurazione

situarsi nella dir flori_xml
lanciare:
prjmgr.py prj/par1.json

esegue le seguenti elaborazioni

prjmgr.py prj/par1_removelog.json,
prjmgr.py prj/par1_merge.json,
prjmgr.py prj/par1_txt.json,
prjmgr.py prj/par1_xml.json

INPUT
flori_xml/par1/eps01.txt
....
flori_xml/par1/eps0n.txt

OUTPUT/INPUT elaborazione
flori_xml/par1/par1.txt
    output dell'elaborazione precedente
    input elaborazxioni successive

OUTPUT FINALE
flor_xml/par1/par1_format.xml
        xml formattato er consultazione
flori_xml/xml/par1.xml
        xml da utilizzare in produzione

================================
elaborazioni singole
================================
prjmgr.py prj/par1_removelog.json,
    rimuove i file di log di elaborazioni precedenti
----------------------------------
prjmgr.py prj/par1_merge.json,
    fa il merge di tutti gli episodi del manoscritto:

INPUT
flori_xml/par1/eps01.txt
....
flori_xml/par1/eps0n.txt

OUTPUT
flory_xml/par1/par1.txt
-----------------------------------
prjmgr.py prj/par1_txt.json,
    esegue:
teimxml.py -i par1/par1.txt -t teimcfg/teimedlib.csv -o par1/log/par1_teim.tx

INPUT
flori_xml/par1/par1.txt

OUTPUT
flori_xml/par1/log/par1_teim.txt
    applica la prima trasfromazione teimedlib = XML
-------------------------------------
prjmgr.py prj/par1_xml.json
    esegue:

teimsetid.py -i par1/log/par1_teim.txt -o par1/log/par1_id.xml, -s G -n 'pb:1,cb:1,lg:1,l:1'
    seconda trasformazione teimedlib => XML
    sono settati gli ID

teimover.py -i par1/log/par1_id.xml -o par1/log/par1_id_over.xml, -c teimcfg/teimoverflow.csv
    crea tutti i riferimenti per la gestione degli overflow

teimnote.py -i par1/log/par1_id_over.xml -o par1/log/par1_id_over_note.xml, -n par1/teimnote.csv
    gestisce le note relative al manoscritto

include: {
host: teimcfg/tei.xml,
dest: xml/par1.xml,
params: [],
files: [XML_MANO|par1/log/par1_id_over_note.xml]
    inserisce l'intestazione TEI nel file XML

teimxmllint.py -i xml/par1.xml -o par1/par1_format.xml 
    formatta il file XML per la consultazione
...................................
INPUT
flori_xml/par1/log/par1_teim.txt

OUTPUT / INPUT elaborazione
flori_xml/par1/log/par1_id.xml
    generato da teimsetid.py
flori_xml/par1/log/par1_id_over.xml
    generato da teimover.py
flori_xml/par1/log/par1_id_over_note.xml
    generato da teimnote.py

OUTPUT FINALE
flor_xml/par1/par1_format.xml
        xml formattato er consultazione
flori_xml/xml/par1.xml
        xml da utilizzare in produzione
--------------------------------------
Controlli sul sorgente txt

prjmgr.py prj/par1_chectext.json
    controlla le entity teimedlib
esegue:
checktxt.py -i par1/par1.txt -o par1/log/par1_checktxt.log

prjmgr.py prj/par1_checkover.json
    controlla apertura chiusura overflow
esegue:
checkover.py -i par1/par1.txt -c teimcfg/teimoverflow.csv -o par1/log/par1_checkover.log

************************************************
Gestione dei singoli episodi.
************************************************
Sono utilizzate le stesse procedure che elaborano
un singolo episodio

esempio:
progettto: flor_xml
witnes: par1
teseto:eps01_txt

situarsi nella dir flori_xml
lanciare:

pej_mgr.py par1_prj/eps01.json

sone esegue le seguenti elaborazioni:
----------------------------------
prjmgr.py par1_prj/eps01_txt.json
esegue
teimxml.py -i par1/eps01.txt -t teimcfg/teimedlib.csv -o par1/log/eps01_teim.tx
----------------------------------
prjmgr.py par1_prj/eps01_setid.json
esegue:
teimsetid.py, -i par1/log/eps01_teim.txt -o par1/log/eps01_id.xml -s G -n 'pb:1,cb:1,lg:1,l:1'
-------------------------------------
prjmgr.py par1_prj/eps01_over.json
esegue:
teimover.py -i par1/log/eps01_id.xml -o par1/log/eps01_id_over.xml -c teimcfg/teimoverflow.csv
--------------------------------------
prjmgr.py par1_prj/eps01_note.json
esegue:
teimnote.py -i par1/log/eps02_id_over.xml -o par1/log/eps02_id_over_note.xml -n par1/teimnote.csv
--------------------------------------
prjmgr.py par1_prj/eps01_format.json
esegue:
teimxmlformat.py -i par1/log/eps01_id_over_note.xml -o par1/eps01.xml 
--------------------------------------
Controlli sul sorgente txt

prjmgr.py par1_prj/eps01_chectext.json
esegue:
checktxt.py -i par1/eps01.txt -o par1/log/eps01_checktxt.log

prjmgr.py par1_prj/eps01_checkover.json
esegue:
checkover.py -i par1/eps01.txt -c teimcfg/teimoverflow.csv -o par1/log/eps01_checkover.log









