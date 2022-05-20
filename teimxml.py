#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import argparse
import sys
import os
import re
from io import StringIO
from lxml import etree
import pprint
from teimedlib.ualog import Log
from teimedlib.textentities import TextEntities
from teimedlib.textentities_log import *
from teimedlib.xml_const import *
from teimedlib.teim_paths import *
from teimedlib.check_teimxml import CheckTeimXml

__date__ = "20-05-2022"
__version__ = "1.7.0"
__author__ = "Marta Materni"

"""
TextEntities.get_rows_entities

?err_inp

elab_rows
    get_rows_entities 
    elab_row
        elab_word_entities
            set_args
            is_tag_to_add_w
            subst_add_w
            supplied_add_w
            set_word_attr
                remove_word_underscore
            check_xml
    check_xml
"""


LOG = Log("w").open("XXX.log", 1).log


"""
   CNT = "$"    # carattere temp per note

    def preserve_note(self, line):
        p0 = line.find("<note")
        p1 = line.find("</note>")
        s0 = line[0:p0]
        s1 = line[p0:p1]
        s2 = line[p1:]
        s1 = s1.replace(" ", CNT, -1)
        t = s0 + s1 + s2
        t = t.replace("<note", " <note", -1).replace("</note>", "</note> ", -1)
        return t
 
        if line.find("<note") > -1:
            line = self.preserve_note(line)
"""


def pp(data, w=40):
    s = pprint.pformat(data, indent=2, width=w)
    return s


class TeimXml(object):
    """
        Trasforma un file testo codificato secondo
        le specifiche teimed in un file xml
        La sostituzione delle entities teimed con
        i tag xml viene effettuato utilizzanod
        un file csv dove sono definiti l entity
    """
    # segmentazione
    # AP = "'"   # <w ana="#elis">$</w>
    # SL = "\\"  # <w ana="#encl">$</w>
    # CR = "°"   # <w ana="#degl">$</w>

    # gestione underline
    SP = " "
    UNDER = '_'   # carattere _ UNDERLINE
    SP_TMP = '|'     # spazio temporaneo usato neitag di riga
    LB_TMP = "XXXX"  # flag gestione parla spezzata a fine riga

    def __init__(self, path_text, path_tags):
        # testo.txt => testo_txt,txt
        self.path_out = set_path_teim_out(path_text)

        # testo.txt => testo_txt.log
        path_info = set_path_teim_log(path_text)
        self.log_info = Log("w").open(path_info, 0).log

        # testo.txt => testo_teim_.xml
        self.path_xml = set_path_teim_xml_log(path_text)
        self.log_teim_xml = Log("w").open(self.path_xml, 0).log

        # testo.txt => testo_txt.ERR.log
        path_err = set_path_teim_err(path_text)
        self.log_err = Log("w").open(path_err, 1).log
        try:
            self.text_entities = TextEntities(path_text,
                                              path_tags,
                                              self.log_err)
        except Exception as e:
            sys.exit(e)
        self.row_num = -1
        # self.rows_entities = []

        # tipo numerazione righe
        self.LB = 'lb'
        self.LG_L = 'lg_l'
        self.type_line = self.LB

        self.trace = False

        #XXX self.input_err_active = True
        self.input_err_active = False

    def input_err(self, msg='?'):
        if self.input_err_active:
            x = input(msg)
            if x == '.':
                self.input_err_active = False

    def set_args(self, entity):
        """
            settta gli argomenti di tag_text con i valori estratti
            da src_args
        """
        nargs = entity.tag_nargs
        args = entity.src_args.split('|')
        nc = len(args)
        nc = 0 if entity.src_args.strip() == '' else nc
        if nargs != nc:
            # ename=entity.name.replace('&','').replace(';','')
            # tag=self.text_entities.get_tag_csv(ename,"?")
            # set_trace()
            self.log_err(f'\nERROR_0 numero argomenti')
            self.log_err(f'row num.  : {self.row_num}')
            self.log_err(f'text      : {entity.src}')
            self.log_err(f'tag name  : {entity.tag_name}')
            self.log_err(f'tag text  : {entity.tag_text}')
            self.log_err(f'src_args  : {entity.src_args}')
            self.log_err(f'tag n.args: {nargs}')
            self.log_err(f'(n.args)  : {nc}')
            self.log_err(f'tag_txt   : {entity.tag_text} ')
            self.input_err('set_args>')

        for arg in args:
            entity.tag_text = entity.tag_text.replace('$', arg, 1)
        return entity

    def remove_word_underscore(self, text):
        # serve ad inserire in una word due testi.
        # _ => ''
        # preparazione caratteri underline
        text = text.replace('{_', '{{').replace('_}', '}}')
        text = text.replace('[_', '[[').replace('_]', ']]')
        text = text.replace(self.UNDER, self.SP)
        # riattiva caratteri underline delle parentesi
        text = text.replace('{{', '{_').replace('}}', '_}')
        text = text.replace('[[', '[_').replace(']]', '_]')
        return text

    def set_word_attr(self, text):
        """
        sostiuisce underscore '_' => ' '
        tipizza le word taggate con <w>
        in base alle entity di un solo carattere
         ° ' \
        """
        # prima<w>  ?Xtoken</w>dopo
        # prima<w   ?Xtoken ... >...</w>
        def find_w_open_close(sl):
            po = -1
            pc = -1
            le = len(sl)-1
            for i in range(le, -1, -1):
                c = sl[i]
                if c == '<':
                    m = re.search(r'<[\w]+', sl[i:])
                    if m is None:
                        raise Exception(
                            f'ERROR B teimxml.py\nfind_w_open_close()\n{sl}')
                    po = i + m.end()
                    m = re.search(r'w>', sl[i:])
                    if m is not None:
                        pc = i + m.end()
                    break
            return po, pc

        def replace_attr(ptrn, s):
            prn = False
            while True:
                m = re.search(ptrn, s)
                if m is None:
                    break
                g = m.group()
                m_start = m.start()
                m_end = m.end()
                tag = self.text_entities.get_tag_csv(g)
                k, v = tag.text.split('=')
                sl = s[:m_start]
                sr = s[m_end:]
                if prn:
                    print(f'\n({self.row_num})\n{s}')
                    print(f'g:  {g}')
                    print(f'sl:  {sl}')
                    print(f'sr:  {sr}')
                po, pc = find_w_open_close(sl)
                if pc > -1:
                    a = sl[:pc-1]
                    b = sl[pc:]
                    sl = f'{a}{b}'
                    s = f'{a} {k}={v} >{b}{sr}'
                    if prn:
                        print(f'a:  {a}')
                        print(f'b:  {b}')
                        print(f'sl:  {sl}')
                        print(f'sr:  {sr}')
                        print(s)
                        input('A>')
                else:
                    a = sl[:po]
                    b = sl[po:]
                    sl = f'{a} {k}={v} {b}'
                    s = f'{sl}{sr}'
                    if prn:
                        print(f'a:  {a}')
                        print(f'b:  {b}')
                        print(f'sl:  {sl}')
                        print(f'sr:  {sr}')
                        print(s)
                        input('B>')
                s = re.sub(r'\s{2,}', self.SP, s)
            return s

        #####################
        ptr_attr = r'[\\]{1}\w{1,}[\\]{1}'
        ptr_attr1 = r'\\'
        ptr_attr2 = r"'"
        ptr_attr3 = r'°'
        #####################
        if text.find(self.UNDER) > -1:
            text = self.remove_word_underscore(text)
        # importante ordine  chiamate
        # \..\
        text = replace_attr(ptr_attr, text)
        # SL "\"
        text = replace_attr(ptr_attr1, text)
        # self.AP "'" apice
        text = replace_attr(ptr_attr2, text)
        # CR "°"
        text = replace_attr(ptr_attr3, text)
        return text

    def is_tag_to_add_w(self, text):
        if text.find('<gap') > -1:
            return False
        if text.find('<note') > -1:
            return False
        # modifica da controllare
        # xw_children=['c','expan','hi','add']
        # w_children = ['</c>',
        #               '</expan>',
        #               '</hi>',
        #               '</add>']
        w_children = ['</c>',
                      '</expan>',
                      '</hi>',
                      '</add>',
                      '<gap>',
                      '<gap'
                      '</space>',
                      '<space']
        w_add_tag = False
        for tag in w_children:
            #if text.find(f'</{tag}>') > -1:
            if text.find(tag) > -1:
                w_add_tag = True
                break
        return w_add_tag

    # def xis_tag_to_add_w(self, text):
    #     no_word = ['lg', 'l', 'cb', 'pb', 'p', 'div', 'seg', 'head', 'note']
    #     if text.find('<note'):
    #         return False
    #     is_tag_in_text = False
    #     for tag in no_word:
    #         ptr = rf'(<{tag})|(</{tag}>|(<{tag}/>))'
    #         m = re.search(ptr, text)
    #         if m is not None:
    #             # esiste almeno un tag della lista in text
    #             # qundi NON vaggaiunto <w>
    #             is_tag_in_text = True
    #             break
    #     w_add_tag = not is_tag_in_text
    #     return w_add_tag

    def subst_add_w(self, text):
        """
        aggiune tag <w> a subst in due modalità

        applicato a parti di parola
        pa<subst><del rend="exp">ro</del><add place="interl">RO</add></subst>la
        <w>pa<subst><del rend="exp">ro</del><add place="interl">RO</add></subst>la</w>

        applicato a parole intere
        <subst><del rend="exp">ro</del><add place="interl">RO</add> </subst>
        <subst><del rend="exp"><w>parola</w></del><add place="interl"><w>PAROLA</w></add></subst>

        Returns:
            text [str]: testo modificato da aggiunta <w>
                        ritona None se non è subst 
        """
        psubst0 = r'(<subst)([\w\s=#"-]*)(>)'
        msubst0 = re.search(psubst0, text)
        if msubst0 is None:
            return None
        psubst1 = r'</subst>'
        pdel0 = r'(<del)([\w\s=#"-]*)(>)'
        pdel1 = r'</del>'
        padd0 = r'(<add)([\w\s=#"-]*)(>)'
        padd1 = r'</add>'
        try:
            le = len(text)
            msubst1 = re.search(psubst1, text)
            if msubst1 is None:
                raise Exception(f'\nERROR_1 </subst> Not Found')
            if (msubst0.start() > 0) or (msubst1.end() < le):
                text = f'<w>{text}</w>'
                return text

            mdel0 = re.search(pdel0, text)
            if mdel0 is None:
                raise Exception(f'\nERROR_2 <del .. Not Found')
            mdel1 = re.search(pdel1, text)
            if mdel1 is None:
                raise Exception(f'\nERROR_3 </del> Not Found')
            s0 = text[:mdel0.end()]
            s1 = text[mdel0.end():mdel1.start()]
            s2 = text[mdel1.start():]
            text = f'{s0}<w>{s1}</w>{s2}'

            madd0 = re.search(padd0, text)
            if madd0 is None:
                raise Exception(f'\nERROR_4 <add .. Not Found')
            madd1 = re.search(padd1, text)
            if madd1 is None:
                raise Exception(f'\nERROR_5  </add> Not Found')
            s0 = text[:madd0.end()]
            s1 = text[madd0.end():madd1.start()]
            s2 = text[madd1.start():]
            text = f'{s0}<w>{s1}</w>{s2}'
        except Exception as e:
            self.log_err('\nERROR_6  subst_add_w()\n{e}')
            self.log_err(f"row.num: {self.row_num}")
            self.log_err(f'{text}\n')
            self.input_err('subst_add_w>')
        return text

    def supplied_add_w(self, text):
        """
        aggiune tag <> a suppled in due modalità
        applicato a parti di parola
        pa<supplied>ro</supplied>la
        <w>pa<supplied>ro></supplied>la</w>

        applicato a parola intera
        <supplied>parola</supplied>
        <supplied><w>parola<w></supplied>

        Returns:
            text [str]: testo modificato da aggiunta <w>
            ritona None se non è supplied 

        """
        psupplied0 = r'(<supplied)([\w\s=#"-]*)(>)'
        msupplied0 = re.search(psupplied0, text)
        if msupplied0 is None:
            return None
        psupplied1 = r'</supplied>'
        try:
            le = len(text)
            msupplied1 = re.search(psupplied1, text)
            if msupplied1 is None:
                raise Exception(f'\nERROR_7 </supplied> Not Found')
            if (msupplied0.start() > 0) or (msupplied1.end() < le):
                text = f'<w>{text}</w>'
                return text
            s0 = text[:msupplied0.end()]
            s1 = text[msupplied0.end():msupplied1.start()]
            s2 = text[msupplied1.start():]
            text = f'{s0}<w>{s1}</w>{s2}'
        except Exception as e:
            self.log_err('\nERROR_8 supplied_add_w()\n{e}')
            self.log_err(f"row.num: {self.row_num}")
            self.log_err(f'{text}\n')
            self.input_err('supplied_add_w>')
        return text

    def elab_word_entities(self, word_ent):
        """
        elabora le entities di word partendo dal livello
        di nidificazione più alto in ordine decrescente
        alla fine dell'alaborazione è settato word_ent.text

        partendo da livello immediatamente successivo a quello corrente
        sostituisce le entities fino al livello 0
        """
        
        # if word_ent.text == "°por&space-d;fitable":
        # if word_ent.text.find("&space-d") > -1:
        #     self.trace = True
        #     we = word_ent
        #     print(we.num)
        #     print(we.text)
        #     for e in we.entities:
        #         print(f'  liv :{e.liv}')
        #         print(f'  src:{e.src}')
        #         print(f'  name:{e.name} ')
        #         print(f'  src_args:{e.src_args} ')
        #         print(f'  err:{e.err}:  {ERR[e.err]}')
        #         print(f'  tag_tp:{e.tag_tp} ')
        #         print(f'  tag_name:{e.tag_name}')
        #         print(f'  tag_text:{e.tag_text}')
        #         print(f'  tag_nargs:{e.tag_nargs} ')
        #         if e.src == we.text:
        #             print(f' *** {e.src} ')
        #     print(we.entities_ch2)
        #     print(we.entities_ch1)
        #     print(we.entities_punt)
        #     print("----")
        #     # input("?")

        word_text_orig = word_ent.text
        if word_text_orig.strip() == '':
            return word_ent

        # controlla se esistono tag parametri di riga
        # nel testo sono del tiop <l:n:>
        # sono trasformati in <l|n="1"!/>
        # if word_text_orig.find(self.SP_TMP) > -1:
        #     # <l|n="1"!/> => <l n="1" />
        #     word_ent.text = word_text_orig.replace(self.SP_TMP, self.SP)
        #     return word_ent

        # LOG("\n"+word_ent.text)
        self.log_info(f'{word_ent.text}')

        if len(word_ent.entities) > 0:
            liv_last = word_ent.entities[0].liv
        else:
            liv_last = -1

        for liv in range(liv_last, -1, -1):
            # seleziona le entities del livello liv
            e_lst = [x for x in word_ent.entities if x.liv == liv]
            for e in e_lst:
                # modifica e.tag_text se vi sono gli argomernti
                e = self.set_args(e)
                if liv == liv_last:
                    continue
                for liv2 in range(liv+1, -1, -1):
                    # seleziona le entiti del livello 2
                    e2_lst = [x for x in word_ent.entities if x.liv == liv2]
                    for e2 in e2_lst:
                        e.tag_text = e.tag_text.replace(e2.src, e2.tag_text, 1)

        # setta word_text con le entity elaborate
        # che hanno modificat e.tag_text in liv==0
        for e in word_ent.entities:
            if e.liv == 0:
                word_ent.text = word_ent.text.replace(e.src, e.tag_text, 1)

        # flag per la gestione del tag <w>
        is_add_w = True

        # entity di tipo CH2
        for et in word_ent.entities_ch2:
            e_tag_name, tag_text = et
            word_ent.text = word_ent.text.replace(e_tag_name, tag_text, 1)

        # entity di tipo CH1
        for et in word_ent.entities_ch1:
            e_tag_name, tag_text = et
            word_ent.text = word_ent.text.replace(e_tag_name, tag_text, 1)

        # entity di tipo PUNT
        for et in word_ent.entities_punt:
            e_tag_name, tag_text = et
            word_ent.text = word_ent.text.replace(e_tag_name, tag_text, 1)
            is_add_w = False

        #print(f"1 {is_add_w}")
        # aggiunta del tag <w> </w> alle word NON taggate
        if word_text_orig == word_ent.text:
            word_ent.text = f'<w>{word_ent.text}</w>'

        # word taggate ma NON con <w>
        if is_add_w and word_ent.text.find('<w') < 0:
            # if word_ent.text.find('<c ') > -1:
            #     print(word_ent.text)
            #     set_trace()
            #print(f"2 {is_add_w}")
            if is_add_w:
                # se è subst aggiunge <w> nelle modalità indicate nel metodo
                # altrimenti ritorna None
                text = self.subst_add_w(word_ent.text)
                if text is not None:
                    word_ent.text = text
                    is_add_w = False
                    msg = f'subst add <w> row num:{self.row_num}'
                    s, err = self.check_xml(text, msg)
                    if err:
                        self.log_err(s)
                        self.input_err('subst_add_w>')

            #print(f"3 {is_add_w}")
            if is_add_w:
                # se è supplied aggiunge <w> nelle modalità indicate nel metodo
                # altrimenti ritorna None
                text = self.supplied_add_w(word_ent.text)
                if text is not None:
                    word_ent.text = text
                    is_add_w = False
                    msg = f'supplied_add_w row num:{self.row_num}'
                    s, err = self.check_xml(text, msg)
                    if err:
                        self.log_err(s)
                        self.input_err('supplied_add_w>')

            # word con un tag che prevedono ANCHE il tag <w>
            # che NON sono subst e supplied
            #print(f"4 {is_add_w}")
            if is_add_w:
                is_add_w = self.is_tag_to_add_w(word_ent.text)
                ####################
                # controllo funzione per add word
                # n_add = self.xis_tag_to_add_w(word_ent.text)
                # if is_add_w != n_add:
                #     LOG(f'{self.row_num}  {word_text_orig}')
                #     LOG(word_ent.text)
                #     LOG(f'{is_add_w}  {n_add}')
                #     self.input_err('X>')
                #######################
            #print(f"5 {is_add_w}")
            # aggiunge <w>
            if is_add_w:
                word_ent.text = f'<w>{word_ent.text}</w>'
                msg = f'add_w  row num:{self.row_num}'
                s, err = self.check_xml(word_ent.text, msg)
                if err:
                    self.log_err(s)
                    self.input_err('add_w>')
            # if self.trace:
            #     input("?")
        # tipizazione di word e sostituzione underscore
        if word_ent.text.find('<w') > -1:
            word_ent.text = self.set_word_attr(word_ent.text)
            msg = f'set_attr_word row num:{self.row_num}'
            s, err = self.check_xml(word_ent.text, msg)
            if err:
                self.log_err(s)
                self.input_err('set_attr_word>')

        if word_ent.text.find('&') > 0:
            self.log_err("\nERROR_9 elab_word_entities()\n& error")
            self.log_err(f"row.num: {self.row_num}")
            self.log_err(f'({word_ent.num})  {word_ent.text}')
            self.log_err('\n')
            self.input_err('remain &>')
        return word_ent

    def elab_row(self, row_ent, bl_in_word):
        self.log_info(f'\nR({row_ent.num})')
        if row_ent.text.strip() == '':
            return ''
        self.log_info(f'{row_ent.text}')
        lst = []
        for word_ent in row_ent.words:
            word_ent = self.elab_word_entities(word_ent)
            self.log_info(f'W: {word_ent.text}')
            lst.append(word_ent.text)
        row_text = ' '.join(lst).strip()

        # UA setta il tipo di numerazione delle linee
        # inizio numerazione linea tipo lg
        if row_text.find('<lg') > -1:
            self.type_line = self.LG_L
        # fine numerazione riga tipo lg
        if row_text.find('</lg>') > -1:
            self.type_line = self.LB

        # tag numerazione righe
        # aggiunge <lb/> all'inizio se la riga precedente
        # non finisce con una parola spezzata
        if self.type_line == self.LB:
            if row_text.find('<w') > -1:
                if not bl_in_word:
                    row_text = f'<lb/>{row_text}'
        elif self.type_line == self.LG_L:
            if row_text.find('<w') > -1:
                row_text = f'<l>{row_text}</l>'

        row_text = row_text.replace('> <', '><')
        self.log_info(f'R: {row_text}')
        return row_text

    def elab_rows(self):

        try:
            rows_entities = self.text_entities.get_rows_entities()
        except Exception as e:
            msg = f'\nERROR_10 elab_rows()\n {e}'
            self.log_err(msg)
            sys.exit(msg)

        try:
            f = StringIO()
            f.write(BODY_TOP)
            # flag controllo a capo con parloa spezzata
            bl_in_word = False
            for row_ent in rows_entities:
                self.row_num = row_ent.num
                row_text = self.elab_row(row_ent, bl_in_word)
                if row_text == '':
                    continue
                # UA controlla se nella riga l'ultima parola contiene LB_TMP
                # il flag per non far insrire <lb/> nella riga successiva
                bl_in_word = row_text.find(self.LB_TMP) > -1
                if bl_in_word:
                    row_text = row_text.replace(self.LB_TMP, "<lb/>")
                f.write(row_text)
                f.write(os.linesep)
            f.write(BODY_BOTTOM)
            src = f.getvalue()
            f.close()

            with open(self.path_out, "w+") as f:
                f.write(src)
            os.chmod(self.path_out, 0o777)

        except Exception as e:
            msg = f'\nERROR_11 elab_rows()\n {e}'
            self.log_err(msg)
            sys.exit(msg)

        # controllo finale XML
        # controolo costruzione strttura
        xml, err = self.check_xml(src, "check xml")
        if err:
            rs=xml.split(os.linesep)
            for i,r in enumerate(rs):
                rs[i]=f'{i+1}) {r}'
            xml=os.linesep.join(rs)
            self.log_err(f'\n{xml}')
        self.log_teim_xml(xml)

        #controllo tag teim in XML
        CheckTeimXml().check_tei_xml(self.path_xml,self.log_err)

    def check_xml(self, src='', msg=''):
        """
        controllo e format xml
        Returns:
            str : xml formattato o src
            bolean: true se si verifica un errore fals altrimenti
        """
        s = src
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            src = f'<DIV>{src}</DIV>'
            root = etree.XML(src, parser)
            xml = etree.tostring(root,
                                 method='xml',
                                 xml_declaration=None,
                                 encoding='unicode',
                                 with_tail=True,
                                 pretty_print=True,
                                 standalone=None,
                                 doctype=None,
                                 exclusive=False,
                                 inclusive_ns_prefixes=None,
                                 strip_text=False)
        except etree.ParseError as e:
            err = f'ERROR XML\n{msg} \n{e}'
            self.log_err(err)
            return s, True
        else:
            return xml, False

def do_main(path_text, path_tags):
    TeimXml(path_text, path_tags).elab_rows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print(f"release: {__version__} { __date__}")
        parser.print_help()
        sys.exit()
    parser.add_argument('-t',
                        dest="tag",
                        required=True,
                        default=" ",
                        metavar="",
                        help="-t <file tags>")
    parser.add_argument('-i',
                        dest="src",
                        required=True,
                        metavar="",
                        help="-i <file text>")
    args = parser.parse_args()
    do_main(args.src, args.tag)
