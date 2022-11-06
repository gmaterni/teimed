Lista dei programmi che coprono il ciclo completo dalfile 
con tatg teimed al file TEI.
Per ognuno digitando <nomeprogramma> -h 
viene stampato l'elenco dei parametri e relativi argomenti
Ogni file produce un output nel file di log che viene
AUTOMATICAMENTE preso come input dal programma successivo
che lo deduce dal nome del file text.txt.
Quindi i programmi devono essere lanciati nella sequenza indicata.


- text.txt è il testo sorgente che utilizza le entities teimed
- teimcfg è la dir contenente i files di configurazione per le elaborazione

checkover.py -i text.txt -c teimcfg/teimoverflow.csv
  controlla i tag per la gestione dell'overflow

checktxt.py -i text.txt
    controlla nel file teimed sorgente le entities.
    Controlla la forma del tipo 
    &abcd;
    e la chiusura delle parentesi  nel tipo
    &abcd;(arg1,arg2)

teimxml.py -i text.txt -t teimcfg/teimtags.csv
    Trasformare un file testo codificato secondo
    le specifiche teimed in un file xml
    La sostituzione delle entities teimed con
    i tag xml viene effettuato utilizzando
    un file temtags.csv dove sono definiti le entities.
    
Esempio iniziale di file teimtags.csv
#categorie|tag TEI-Med|tag TEI-XML
log|chB|<div type="chapter">
log|chE|</div>
log|hdB|<head type="rubrica">
log|hdE|</head>
log|parB|<p>
log|parE|</p>
log|sB|<seg type="ms-phrase">
log|sEB|</seg><seg type="ms-phrase">
log|sE|</seg>
note|ptr-d|<ptr type="dipl" target="#$" n="d$" />
note|ptr-i|<ptr type="int" target="#$" n="i$" />
note|note-per|<note type="peritextuelle">$</note>
codic|gb|<gb n="$"/>
codic|pb|<pb n="$"/>
codic|fw-c-bc|<fw type="catch" place="bot-center">$</fw>
codic|fw-c-br|<fw type="catch" place="bot-right">$</fw>
codic|fw-s-bc|<fw type="sig" place="bot-center">$</fw>
codic|fw-s-br|<fw type="sig" place="bot-right">$</fw>
codic|fw-s-tc|<fw type="sig" place="top-center">$</fw>
codic|fw-s-tr|<fw type="sig" place="top-right">$</fw>

-------------------------------------------------

teimsetid.py -i text.txt -t teimcfg/teimxmlid.csv
    Setta gli attributi xml:id nei tag xml.
    Il criterio di assegnazione e numerazione è
    definitio in un file teimxmlid.csv

    Esempio di teimxmlid.csv  

    #key|tag_id|id|children
    div_episode|K|0|div_chapter:cb:pb:p:lg:l:persName:geogName:placeName:choice
    div_chapter|ch|0|head:w:p
    head|h|0|w:pc:gap
    cb|cb|0|
    pb|pb|0|
    p|p|0|w:pc:gap
    lg|lg|0|    
    l|l|0|w:pc:gap
    w|w|0|
    pc|pc|0|
    gap|gap|0|
    persName|peNm|0|
    geogName|geNm|0|
    placeName|plNm|0|
    choice|chc|0|

    La numerazione è definita a partire da div_episode
    Viene stampato un file json che rappresenta la
    logica della numerazione.
    Se non vi sono direttive la numerazione degli id e delgi n 
    inizia da 1

    DIRETTIVE 
    E' possibile settare id iniziale di episode
    e n di capitoli e pargrafi

    Numera <l> dopo il primo <lg> se NON hanno l'atributo n=..
    La numerazione inizia dai valori settati con i flag id all'inizio
    del file testo.
    
    @episode:sign=A
    @episode:id=100
    @chapter:n=100
    @head:n=100
    @p:n=100
    @l:n=100

    ATTENZIONE 
    - il sign del flag sostituisce quello definito nel file csv
    - utilizzare id per episode (il solo tag per il quale è possibile)
    - utilizzare n per gli altri

VALORI DI DEFAULT
    episode:sign=K
    episode:id=1
    chapter:n=1
    head:n=1
    p:n=1
    l:n=1

-----------------------------------------------------

teimover.py -i text.txt -c teimcfg/teimoverflow.csv
    legge da un file csv i tag per la gestione degli overflow
    aggiunge in coda al file xml gli elementi
    from=.. to=..

Esempio di teimoverflow.csv
TYPE|TAG_FROM|TAG_TO|SIGLA_FROM|SIGLA_TO
directspeech|{|}|ODRD|CDRD
monologue|{_|_}|OMON|CMON
agglutination|[|]|OAGLS|CAGLS
agglutination_uncert|[_|_]|OAGLU|CAGLU
damage|{0%|%0}|ODAM|CDAM
damage_low|{1%|%1}|ODAML|CDAML
damage_medium|{2%|%2}|ODAMM|CDAMM
damage_high|{3%|%3}|ODAMH|CDAMH
    
teimnote.py -i text.txt -n teimnote.csv
    legge il testo delle note dal fille note.csv
    modifica il file xml aggiungendo le note in fondo 
    collegandole alla/e righe che hanno il "target" corrispondente
    a quello indictao nel file csv,

Esempio

tag definiti in teimtags.csv
note|ptr-d|<ptr type="dipl" target="#$" n="d$" />
note|ptr-i|<ptr type="int" target="#$" n="i$" />

note definite in note.csv
nota|ind1|J'ignore un tilde d'abréviation audessus de "Aimes".
nota|ind3|le scribe conserve le tilde d'abbréviation audessus de "p".


File XML TEI
<ptr xml:id="kptr1" type="dipl" target="#ind1" n="d1"/>
....
<ptr xml:id="kptr3" type="dipl" target="#ind3" n="dd3"/>
....
....
<teimed_note xml:id="ind1">
J'ignore un tilde d'abréviation audessus de "Aimes".
</teimed_note>
....
<teimed_note xml:id="ind3">
le scribe conserve le tilde d'abbréviation audessus de "p".
</teimed_note>

teimxmlformat.py -i log/text_id_over_note.xml, -o text.xml, -a
    formatta un file xml aggiungendo al sorgente <div></div>

==================================================
!! N.B
Il parametro -i indica il nome del file codificato 
con teimed. SOLO nel caso di teimxml.py è l'effettivo 
input del programma.
Un caso a partrte per teimxmlformat.py per il quale
vanno settati i parametri di input ed output ed è
di uso generico per la formattazione ed il controllo
fi file XML.
Negl gli altri casi l'input è definito AUTOMATICAMENTE
a partire dal nome del file iniziale.

teimxml.py -i eps01.txt -t teimcfg/teimtags.csv
<== eps01.txt
==> ./log/eps01_teim.txt
    ./log/eps01_teim.log	

teimsetid.py -i eps01.txt -t teimcfg/teimxmlid.csv 
<== ./log/eps01_teim.txt
==> ./log/eps01_id.xml
    ./log/eps01_id.log
    ./log/eps01_id.json (definizione geraerchia per l'assegnazione id)

teimover.py -i eps01.txt -c teimcfg/teimoverflow.csv 
<== ./log/eps01_id.xml
==> ./log/eps01_id_over.xml
    ./log/eps01_id_over.log

teimnote.py -i eps01.txt -n teimnote.csv 
<== ./log/eps01_id_over.xml
==> ./log/eps01_id_over_note.xml

teimxmlformat.py -i log/eps01_id_over_note.xml -o eps01.xml -a
<== log/eps01_id_over_note.xml
==> eps01.xml
Il parametro -a è necessario in questo caso perchè
aggiunge <div></div> al file XML per poterne fare
il checck.
Nella versione definitiva del file dovrà essere 
decorato coni tag TEI.

