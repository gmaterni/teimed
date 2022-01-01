checkover.py
checktxt.py
prjmgr.py
setup.py
teimedit.py
teiminfo.py
teimnote.py
teimover.py
teimprjfind.py
teimprjmapprn.py
teimprjsave.py
teimprjtextmake.py
teimprjxmlmake.py
teimsetid.py
teimxmlfh.py
teimxmlformat.py
teimxmllint.py
teimxml.py
teixml2txt.py

=================
file di teimedlib e file che li utilizzano
=================
check_teimed.py
    teimedit.py

clean_text.py
    teimedit.py

edit_constants.py
    teimedit.py
    teimxmlfh.py
        findreplace.py
        listboox.py
        textedit.py
        textpad.py
    
findfile.py
    teimedity.py
    teimcmlfh.py

findreplace.py
    teimedit.py

listbox.py
    teimedit.py
    teimcmlfh.py

pathutils.py
    teimedit.py
    teimcmlfh.py
        findfile.py
        uarec.py

readovertags.py
    checkover.py
    teimedit.py
    teimover.py

teim_constants.py
    teimedit.py
    teimxmlfh.py

teimprjmap.
    teimprjmapprn.py
    teimxmlfh.py
    
template_xml_prj.py
    teimprjxmlmake.py

textedit.py
    teimedit.py

textentities_log.py
    teimxml.py

textentities.py
    teimxml.py

textpad.py
    teimedit.py
    teimxmlfh.py

txtbuilder.py
    teimxml2txt.py
    txtbuilder.py

ualog.py
    (utilizzato in tutti i files)

uarc.py
    teimedit.py

xml_const.py
    teimnote.py
    teimsetid.py
    teimxml.py

========================================
quick help
========================================
checkover.py
  controlla i tag per la gestione dell'overflow

checktxt.py
    controlla nel file teimed sorgente le entitities.
    Controlla la froma nel tipo 
    &abcd;
    e la chusura delle parentesi  nel tipo
    &abcd;(arg1,arg2)

prjmgr.py
    gestisce i progetti codificti in json.
    digitando senza argomenti
    vengono visualizzate tutte le opzioni

setup.py
    installazione applicativi

teimedit.py
    edita i file teimed sorgenti , controlla le
    entities e  gestisce i  programmi di trasfromazio

teiminfo.py
    elenca cli applicativi installati
    
teimnote.py
    legge il testo delle note dal fille note.csv
    modifica il file xml
    aggiunge le note in fond e setta xml:id di ptrn

teimover.py
    legge da un file csv i tag per la gestion degli overflog
    aggiunge in coda al file xml gli elementi
    from=.. to=..

teimprjfind.py
    Programma di utility
    Cerca il primo file __prj__ contenuto in un progetto
    a partire dalla dir dalla quale è lanciato.
    Il nome del progetto è passato per psoizione.

teimprjmapprn.py
    programma di utility
    Cerca il primo __prj__ trovato a partire
    dalla dir di esecuzione e ne stampa la mappa
    Il nome del progetto è passato per posizione

teimprjsave.py
    File di utility 
    Utilizzato da teimedit.py e teimxnlfh.py per
    salvare in una di back i sorgetnti dei file testo

teimprjtextmake.py
    Crea le direttory per i file di testo che sono stati aggiunti
    al witness indicato
    teimprjtextmake.py <project_name> <witness>
    Se si esegue lo script  nella dir del progetto
    teimprjtextmake.py <witness>
    gli argomenti soo passati per psoizione,
    es.
    teimprjtextmake.py <project_name> <witness>  
    teimprjtextmake.py <witness>

teimprjxmlmake.py
    Crea  la struttua di un progetto
    può essere lancaito in varie modalità:
    Crea le directory SE NON esistno
    Senza argomenti stampa un help di spiegazione
    utilizzanod un file csv:
    es. project.csv
    flori_xml|par1|eps
    flori_xml|tor1|eps
    flori_xml|ven1|eps
    teimprhxmlmake.py project.csv
    con diversi argomenti passati per psozione    
    teimprjxmlmake.py <project_name> <witnes> "
    teimprjxmlmake.py <project_name> <witnes> < text>")

teimsetid.py
    Setta gli attributi xml:id nei tag xml.
    Il criterio di aseggnazione e numerazione è
    definitio in un fule csv,
    
    #key | tag_id|id start|children
    div_episode||-1|div_chapter:head:cb:pb:p:lg:persName:geogName:placeName:choice
    div_chapter|chp|0|head:p:lg:l
    head|he|0|w
    cb|cb|0|
    pb|pb|0|
    p|p|0|w:pc
    lg|lg|0|    
    l|l|0|w:pc
    w|w|0|
    pc|pc|0|
    persName|peNm|0|
    geogName|geNm|0|
    placeName|plNm|0|
    choice|chc|0|

    La numerazione è definita a partire dall'elemento
    con id==-1

    Viene stampato un file json che rappresenta la
    logica dell numerazione.

teimxmlfh.py
    Gestisce in modalità grafica un progetto

teimxmlformat.py
    formatta un file xml aggiungendo al sorgente <div></div>

teimxmllint.py
    formatta un file xml

teimxml.py
    Trasfroma un file testo codificato secondo
    le specifiche teimed in un file xml
    La sostituzione delle entities teimed con
    i tag xml viene effettuato utilizzanod
    un file csv dove sono definiti l entity

teixml2txt.py
    Estrae un file di testo da un file tei xml
