#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import sys
import re
import io
from teimedlib.teimtxtread import TeimTxtRead

__date__ = "18-07-2021"
__version__ = "1.3.1"
__author__ = "Marta Materni"


"""
get_rows_entities
    ttread.read_text_rows
    ttread.add_spc2punct
    ttread.join_words_wrap
    ttread.clean_brackets
    # add_row_tag(rows)
    read_tags
    build_rows_entities
        build_row_words
            build_word_entites
                get_word_liv_data_lst
                    ent_partition
                    entity_liv
                liv_list2stack
                set_sep_args
                get_tag_csv
            build_word_entities_ch2
            build_word_entities_ch1
            build_word_entities_punt

"""


class Tag(object):

    def __init__(self, tp='', name='', text='', nargs=0):
        self.tp = tp
        self.name = name
        self.text = text
        self.nargs = nargs


class Entity(object):

    def __init__(self,
                 src,
                 name,
                 src_args,
                 liv,
                 err,
                 tag_csv):
        self.src = src
        self.name = name
        self.src_args = "" if src_args is None else src_args
        self.liv = liv
        self.err = err
        self.tag_tp = tag_csv.tp
        self.tag_name = tag_csv.name
        self.tag_text = tag_csv.text
        self.tag_nargs = tag_csv.nargs

    def get_fields(self):
        return self.src, self.name, self.src_args, self.liv, self.err

    def get_tag_fields(self):
        return self.tag_name, self.tag_text, self.tag_nargs


class WordEnt(object):

    def __init__(self, num, text, entities):
        self.num = num
        self.text = text
        self.entities = entities
        self.entities_ch2 = []
        self.entities_ch1 = []
        self.entities_punt = []

    def set_entities_ch2(self, entities_ch2):
        self.entities_ch2 = entities_ch2

    def set_entities_ch1(self, entities_ch1):
        self.entities_ch1 = entities_ch1

    def set_entities_punt(self, entities_punt):
        self.entities_punt = entities_punt


class RowEnt(object):

    def __init__(self, num, text):
        self.num = num
        self.text = text
        self.words = []

    def set_words(self, words):
        self.words = words


class TextEntities(object):

    def __init__(self, path_text, path_tags, log_err):
        self.path_text = path_text
        self.path_tags = path_tags
        self.log_err = log_err
        self.row_num = -1
        self.rows_entities = []
        # patter entity standard
        #self.ptrn_en = r'&[\w\°\-]+;'
        self.ptrn_ent = r"&[\w\-\'\°\\]+;"
        # patter entity 1 char con args
        #self.ptr_ch1_arg = r"['°\\]"
        self.ptrn_ch1_arg = r"(['°\\])([\w&;-]+)"
        # pattern entity 2 char senza args
        self.ptrn_ch2 = r'[*^`~]{1}[a-zA-Z]{1}'
        # patter entity 1 char senza args
        self.ptrn_ch1 = r'[àéèìòùÀÈÉÌÒÙ]{1}'
        # set punt
        self.set_punt = '.,:?!;'
        self.tags_csv_js = {}

        #AAA self.input_err_active = True
        self.input_err_active = False

    def input_err(self, msg='?'):
        if self.input_err_active:
            x = input(msg)
            if x == '.':
                self.input_err_active = False

    # text_rgt, group
    def ent_partition(self, word_text, group, start):
        """
        in un'espessione seleziona fino alla prima )
        che bilancia ( saltando le entity argomento
        Args:
            s (str): sorgente da entity in avanti:       &x;(a,b))..
            df (str): valore di default  per err =4,3,2
        Returns:
            [tupla]: (e, e_lft, e_rgt, 0)
            e: espressione da antity a la prima ) bilanciata: &x;(a,b)
            e_lft: pentity. arte sinistra prima di (.          &x;
            e_rgt: testo nelle parentes                        (a,b)
            err: codice errore
                                        0  '()' bilanciano
                                        1  non trovata ')' che bilancia
                                        2  una ) precede la prima '('
                                        3  non esiste '('
                                        35 una '&'  prima di '('
                                        4  espr == None
        # word_text, group
        romay&n;&sub-tr-sup;(z,s), &n;
        txt : &n;&sub-tr-sup;(z,s)
        src : &n;
        name: &n;
        rnd : ''
        t   : 35

        # word_text, group
        romay&n;&sub-tr-sup;(z,s), &sub-tr-sup;
        txt : &sub-tr-sup;(z,s)
        src : &sub-tr-sup;(z,s)
        name: &sub-tr-sup;
        rnd : (z,s)
        t   : 0

        """
        # group ed il testo a destra
        text = word_text[start:]
        op = text.find('(')
        cl = text.find(')')

        if op > -1 and cl > -1 and cl < op:
            # esiste ')' prima del primo '('
            return (group, group, '', 2)

        if op < 0:
            # non esiste '('
            return (group, group, '', 3)
        else:
            # esiste '('
            ent_next = text.find('&', len(group), op)
            if ent_next > -1:
                # esiite & successiva prima di '(
                s = text[:ent_next]
                return (s, group, '', 35)

        # verifica bilanciamento parentesi
        op_text = text[op:]
        oc = 0
        i = 0
        for c in op_text:
            i += 1
            if c == '(':
                oc += 1
            elif c == ')':
                oc -= 1
            if oc == 0:
                # eiste una ')' che bilancia
                break
        else:
            # non esiste ')' che bilanci
            self.log_err("\nERROR parentesi '()' non bilanciate")
            self.log_err(f"{word_text}")
            self.log_err(f'{group}')
            self.log_err(f'row num:{self.row_num}')
            self.input_err()
            return (group, group, '', 1)

        # '()' bilanciate
        end = op+i
        src = text[:end]
        name = text[:op]
        #rnd = op_text[:i]
        rnd = text[op:end]
        rt = (src, name, rnd, 0)
        return rt

    def entity_liv(self, text_lft):
        """
            utilizza ( ) a sniistra di s per stabilire
            il livello di nidificazione
        """
        if text_lft.find('(') < 0:
            return 0
        liv = 0
        for c in text_lft:
            if c == '(':
                liv += 1
            elif c == ')':
                liv -= 1
        return liv

    def get_word_liv_data_lst(self, word_text):
        """
            data una tupla per ogni entitiy della word:
            (src,name,rnd,liv,err)

            lista di liste di livello
            ogni lista di livello è una lista di tuple
            lst=[
                [a0,b0,..], # livello 0
                [a1,b1,..], # livello 1
                [a2,b3,..],
                .....
            ]
        """
        # lst = [[], [], [], [], [], ..]
        lst = [[] for i in range(0, 10)]
        for m in re.finditer(self.ptrn_ent, word_text):
            m_group = m.group()
            m_start = m.start()
            src, name, rnd, err = self.ent_partition(word_text,
                                                     m_group,
                                                     m_start)
            text_lft = word_text[0:m_start]
            # livello di inclusione clacolato sulla base dell (
            # che precedono l'espesssione selezionata
            liv = self.entity_liv(text_lft)
            # if word_text.count('&') > 1:
            #     print('...................')
            #     print(f'{self.row_num}')
            #     print(f'word_text : {word_text}')
            #     print(f'm_group   : {m_group}')
            #     print(f'liv       : {liv}')
            #     print(f'src       : {src}')
            #     print(f'name      : {name}')
            #     print(f'ren       : {rnd}')
            #     print(f'err       : {err}')
            #     input('? :')

            # ent_src, ent_name, (ent_args)
            data = (src, name, rnd, liv, err)
            lst[liv].append(data)
        return lst

    def liv_list2stack(self, lst):
        """
        riordina la lista delle tuple per livello
        in una lista di tuple ordinata per livello decrscente
        """
        stack = []
        ll = len(lst)-1
        for l in range(ll, -1, -1):
            ls = lst[l]
            for e_fileds in ls:
                stack.append(e_fileds)
        return stack

    def set_sep_args(self, s):
        """
        separa gli argomenti con '|'
        """
        if s.find(',') < 0:
            return s
        SEP = '|'
        liv = 0
        out = io.StringIO("")
        for c in s:
            if c == '(':
                liv += 1
            elif c == ')':
                liv -= 1
            if c == ',' and liv == 0:
                out.write(SEP)
            else:
                out.write(c)
        s = out.getvalue()
        out.close()
        return s

    def build_word_entites(self, word_text):
        """
        ritorna una lista di entity per la word
        ordinate per livello di inclusione decrscente
        """
        lst = []
        liv_lst = self.get_word_liv_data_lst(word_text)
        stack = self.liv_list2stack(liv_lst)
        for e_fileds in stack:
            ent_src, ent_name, ent_rnd, liv, err = e_fileds
            # text entro brackets
            if ent_rnd.find('(') > -1:
                s = ent_rnd[1:]
                ent_args = s[:-1]
            else:
                ent_args = ent_rnd
            ent_args_sep = self.set_sep_args(ent_args)
            # aggiunge tag_csv preso dal js dei tag
            tag_name = ent_name.replace('&', '').replace(';', '')
            tag_csv = self.get_tag_csv(tag_name, None)
            if tag_csv is None:
                tag_csv = Tag()
                self.log_err(f"\nERROR. tag:{tag_name}  Not Found.")
                self.log_err(f'{word_text}')
                self.log_err(f'row num:{self.row_num}\n')
            ent = Entity(ent_src,
                         ent_name,
                         ent_args_sep,
                         liv,
                         err,
                         tag_csv)
            lst.append(ent)
        return lst

    def build_word_entities_ch2(self, word_text):
        """
        entitè a due caratteri |*a|<c ../c>
        r'[*^`~]{1}[a-zA-Z]{1}'
        """
        lst = []
        for m in re.finditer(self.ptrn_ch2, word_text):
            g = m.group()
            tag_name = g
            tag_csv = self.get_tag_csv(tag_name, None)
            if tag_csv is None:
                self.log_err(f"\nERROR. CH2 tag:{tag_name}  Not Found.")
                self.log_err(f'{word_text}')
                self.log_err(f'row num:{self.row_num}\n')
            else:
                et = (tag_name, tag_csv.text)
                lst.append(et)
        return lst

    def build_word_entities_ch1(self, word_text):
        """
        entitèa a un carattere
        r'[àéèìòùÀÈÉÌÒÙ]{1}'
        """
        lst = []
        for m in re.finditer(self.ptrn_ch1, word_text):
            g = m.group()
            tag_name = g
            tag_csv = self.get_tag_csv(tag_name, None)
            if tag_csv is None:
                self.log_err(f"\nERROR. CH1 tag:{tag_name}  Not Found.")
                self.log_err(f'{word_text}')
                self.log_err(f'row num:{self.row_num}\n')
                self.input_err()
            else:
                et = (tag_name, tag_csv.text)
                lst.append(et)
        return lst

    def build_word_entities_punt(self, word_text, word_ent):
        """
        entitè a un carattere di punteggiatura
        r'[.,:?!;]'
        """
        p = word_text.strip()
        le = len(p)
        if le == 0 or le > 1:
            return []
        if not p in self.set_punt:
            return []
        tag_name = p
        tag_csv = self.get_tag_csv(tag_name, None)
        lst = []
        if tag_csv is None:
            self.log_err(f"\nERROR. punctuation tag:{tag_name}  Not Found.")
            self.log_err(f'{word_text}')
            self.log_err(f'row num:{self.row_num}\n')
            self.input_err()
        else:
            et = (tag_name, tag_csv.text)
            lst.append(et)
        return lst

    def build_row_words(self, row_ent):
        """
        ritorna a lista di liste delle word
        contenute nlla row
        """
        word_text_lst = row_ent.text.split(' ')
        lst = []
        for i, word_text in enumerate(word_text_lst):
            if word_text.find('&') < 0:
                entities = []
            else:
                entities = self.build_word_entites(word_text)
            word_ent = WordEnt(i, word_text, entities)

            # entity 2 char
            # |~i|<c ana="#hiat">i</c
            ch2_lst = self.build_word_entities_ch2(word_text)
            word_ent.set_entities_ch2(ch2_lst)

            # entity 1 char
            # |à|<c ana= "#diacr-desamb">a</c>
            ch1_lst = self.build_word_entities_ch1(word_text)
            word_ent.set_entities_ch1(ch1_lst)

            # entity punteggiatura
            punt_lst = self.build_word_entities_punt(word_text, word_ent)
            word_ent.set_entities_punt(punt_lst)

            lst.append(word_ent)
        row_ent.set_words(lst)
        return row_ent

    def build_rows_entities(self, rows):
        """
        lista  contenenti le informazione sulla
        row e sulle sue entities
        """
        self.rows_entities = []
        for n, row_text in enumerate(rows):
            self.row_num = n+1
            row_ent = RowEnt(self.row_num, row_text)
            row_ent = self.build_row_words(row_ent)
            self.rows_entities.append(row_ent)

    def get_tag_csv(self, tag_name, df=None):
        tag = self.tags_csv_js.get(tag_name, df)
        return tag

    def read_tags(self, path_tags):
        """ Lettura tags da csv
        """
        self.tags_csv_js = {}
        DELIMITER = '|'
        dupl = []
        with open(path_tags, "rt") as f:
            for line in f:
                if line.strip() == '':
                    continue
                try:
                    if line[0] == '#':
                        continue
                    cols = line.split(DELIMITER)
                    if len(cols) < 3:
                        continue
                    tag_type = cols[0].strip()
                    tag_name = cols[1].strip()
                    tag_text = cols[2].strip()
                    tag_nargs = tag_text.count('$')
                    tag = Tag(tag_type, tag_name, tag_text, tag_nargs)
                    # controllo duplicati
                    x = self.get_tag_csv(tag_name, '')
                    if x != '':
                        dupl.append(tag_name)
                    self.tags_csv_js[tag_name] = tag
                except Exception as e:
                    err = f'ERROR. textentities.py read_tags()\n{e}\nline:{line}'
                    self.log_err(err)
                    sys.exit(err)
        if len(dupl) > 0:
            self.log_err("\nERROR. read_tags_() Tag Duplicate")
            for x in dupl:
                self.log_err(x)

    # def add_row_tag(self, rows):
    #     """
    #     utilizza tag del tipo <l:n:1/> che sono aggiunti
    #     alla riga nella forma <l|n="1"|/>
    #     successivamente sono trasformati in
    #     <l n="1" />
    #     DEVONO essere staccati da ogni parola
    #     """
    #     SP = ' '
    #     SP_TMP = '|'
    #     ptr_row = r'([<]{1})([\w\s:]*)([>]{1})'
    #     for i, row in enumerate(rows):
    #        while (m := re.search(ptr_row, row)) is not None:    
    #             try:
    #                 g2 = m.group(2)
    #                 m_start = m.start()
    #                 m_end = m.end()
    #                 sp = g2.split(':')
    #                 tag = sp[0].strip()
    #                 if len(sp) > 1:
    #                     attr = sp[1].strip()
    #                     val = sp[2].strip()
    #                     s = f'<{tag}{SP_TMP}{attr}="{val}"{SP_TMP}/>'
    #                 else:
    #                     s = f'<{tag}/>'
    #                 row = f'{row[:m_start]} {s} {row[m_end:]}'
    #                 rows[i] = re.sub(r'\s{2,}', SP, row)
    #             except Exception as e:
    #                 msg = f'ERROR textentities.py add_row_tag()\n{e}\n{row}'
    #                 self.log_err(msg)
    #                 self.input_err()
    #     return rows

    def get_rows_entities(self):
        """
        lista di tutte le entities del testo
        """
        ttread = TeimTxtRead(self.path_text, self.log_err)
        rows = ttread.read_text_rows()
        rows = ttread.join_words_wrap(rows)
        rows = ttread.add_spc_to_punct(rows)
        rows = ttread.clean_brackets(rows)
        # rows = self.add_row_tag(rows)        
        self.read_tags(self.path_tags)
        self.build_rows_entities(rows)
        return self.rows_entities
