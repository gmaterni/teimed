#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pdb import set_trace
# from xml.etree.ElementTree import ElementTree
from lxml import etree
import os
import argparse
import sys
import pprint
import re
import stat
from teimedlib.ualog import Log
from teimedlib.readovertags import read_tags_over_sorted
from teimedlib.teim_paths import *
import teimxmlformat as xmf

__date__ = "29-03-2022"
__version__ = "0.2.1"
__author__ = "Marta Materni"


def pp(data, w=40):
    return pprint.pformat(data, indent=2, width=w)


LGDB = Log("w").open("debug.log", 1).log


class TeimOverFlow(object):
    DATA_TYPE = "tp"
    DATA_FROM = "from"
    DATA_TO = "to"

    OP = 'op'
    CL = 'cl'
    LOP = 'lop'
    LCL = 'lcl'
    TP = 'tp'
    OPEN_CLOSE = 'ctrl'

    """
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
    """

    def __init__(self, path_text, path_csv):
        # test.txt => testo_id.xml
        self.path_in = set_path_over_in(path_text)

        # test.txt => testo_id_over.xml
        self.path_out = set_path_over_out(path_text)

        # test.txt => testo_id_over.log
        path_span = set_path_over_log(path_text)
        self.logspan = Log("w").open(path_span, 0).log

        # test.txt => testo_id_over.ERR.log
        path_err = set_path_over_err(path_text)
        self.logerr = Log("w").open(path_err, 1).log

        self.root_xml = etree
        self.span_data = {}
        self.key_span_data = ''
        self.row_tag_over_js = {}
        self.tag_op_alter = []
        self.tag_cl_alter = []
        self.tag_op_lst = []
        self.tag_cl_lst = []
        self.rows_tag_over = []
        # self.over_op_set=[]
        # self.over_cl_set=[]
        # self.over_tag_set=[]
        self.add_xml_span_overflow_list(path_csv)

    def set_row_tag_js(self, i):
        # costruisce una riga della struttura json dei tagovwrflo
        #  0        1       2      3       4
        # descr|from tag|to tag|log opn|log close
        row_tag = self.rows_tag_over[i]
        self.row_tag_over_js = {
            self.OP: row_tag[1],
            self.CL: row_tag[2],
            self.LOP: row_tag[3],
            self.LCL: row_tag[4],
            self.TP: row_tag[0],
            self.OPEN_CLOSE: 0
        }
        # LGDB(f"\n{i}-----------")
        # LGDB(pp(row_tag))

        # tag alternativi a quello selezionato
        # nella lista son settati i tag di
        # lunghezza > del tag selezionato
        self.tag_op_alter = []
        self.tag_cl_alter = []
        op = row_tag[1]
        for j, r in enumerate(self.rows_tag_over):
            o = r[1]
            c = r[2]
            if j == i:
                continue
            if len(o) > len(op):
                self.tag_op_alter.append(o)
                self.tag_cl_alter.append(c)
        # LGDB(f"op_alter:\n{pp(self.tag_op_alter)}")
        # LGDB(f"cl_alter:\n{pp(self.tag_cl_alter)}")

    #############################################

    def node_liv(self, node):
        d = 0
        while node is not None:
            d += 1
            node = node.getparent()
        return d - 1

    def node_tag(self, nd):
        try:
            tag = nd.tag
            tag = tag if type(nd.tag) is str else "XXX"
            pid = tag.find('}')
            if pid > 0:
                tag = tag[pid + 1:]
        except Exception as e:
            self.logerr("ERROR 0 in xml")
            self.logerr(str(e))
            return "XXX"
        else:
            return tag.strip()

    def node_id(self, nd):
        s = ''
        kvs = nd.items()
        for kv in kvs:
            if kv[0].rfind('id') > -1:
                s = kv[1]
                break
        return s

    def node_text(self, nd):
        text = nd.text
        text = '' if text is None else text.strip()
        text = text.strip().replace(os.linesep, ',,')
        return text

    def node_tail(self, nd):
        tail = '' if nd.tail is None else nd.tail
        tail = tail.strip().replace(os.linesep, '')
        return tail

    def node_val(self, nd):
        ls = []
        for x in nd.itertext():
            ls.append(x)
        text = " ".join(ls)
        return text
        # val = ""
        # for t in nd.itertext():
        #     val = val + t
        # return val

    def get_node_data(self, nd):
        tag = self.node_tag(nd)
        id = self.node_id(nd)
        text = self.node_text(nd)
        val = self.node_val(nd)
        tail = self.node_tail(nd)
        liv = self.node_liv(nd)
        nd_data = {
            'tag': tag.strip(),
            'id': id,
            'text': text,
            'val': val,
            'tail': tail,
            'liv': liv
        }
        return nd_data

    # nodo precedente <w> , <pc> <gap>
    def get_prev(self, node):

        def get_container(node):
            nd = None
            while node is not None:
                node = node.getparent()
                if node is None:
                    break
                tag = self.get_node_data(node)['tag']
                if tag in ['l', 'p', 'seg']:
                    nd = node
                    break
            return nd

        nd_prev = node.getprevious()
        if not nd_prev is None:
            tag = self.get_node_data(nd_prev)['tag']
            if tag in ['w', 'pc', 'gap']:
                return nd_prev
        node_data = self.get_node_data(node)
        node_id = node_data['id']
        nd_container = get_container(node)
        #nd_prev = node.getprevious()
        for nd in nd_container.iterdescendants():
            #tag = node.tag if type(node.tag) is str else "XXX"
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            if tag.strip() in ['w', 'pc', 'gap']:
                nd_id = nd_data['id']
                if nd_id == node_id:
                    break
                nd_prev = nd
        if nd_prev is None:
            nd_data = self.get_node_data(node)
            msg = f"ERROR Z Not found node previus.\n{pp(nd_data)}"
            raise Exception(msg)
        return nd_prev

    # rtorna il <div> parent

    def get_span_parent(self, node):
        nd = None
        while node is not None:
            node = node.getparent()
            if node is None:
                break
            tag = node.tag if type(node.tag) is str else "XXX"
            if tag == 'div':
                nd = node
                break
        return nd

    def xml2str(self, nd):
        if nd is None:
            return "<null/>"
        s = etree.tostring(nd,
                           xml_declaration=None,
                           encoding='unicode',
                           method="xml",
                           pretty_print=True,
                           with_tail=True,
                           standalone=None,
                           doctype=None,
                           exclusive=False,
                           inclusive_ns_prefixes=None,
                           strip_text=False)
        return s

    def set_from_id(self, nd_data):
        """
        estrae tag span dal sorgente xml
        aggiunge un elemento a span_data
        setta self.from_id_open
        Args:
            nd_data (dict): dati del nodo xml
        """
        from_id = nd_data['id']
        tp = self.row_tag_over_js[self.TP]
        item = {}
        item[self.DATA_TYPE] = tp
        item[self.DATA_TO] = ''
        item[self.DATA_FROM] = from_id
        self.span_data[from_id] = item
        self.key_span_data = from_id

    # setta to_id in span_data utilizzando from_id_open
    def set_to_id(self, nd_data):
        try:
            if self.key_span_data is None:
                return
            if nd_data is None:
                raise Exception(f"nd_data is nill")
            to_id = nd_data['id']
            item = self.span_data.get(self.key_span_data, None)
            if item is None:
                raise Exception(f"key_span:{self.key_span_data} Not Found.")
            item[self.DATA_TO] = to_id
        except Exception as e:
            self.logspan(f'{e}\n')
            msg = f'ERROR 1 set_id_to()\n{e}'
            self.logerr(msg)
            sys.exit(msg)

    def log_open(self, nd):
        xml = self.xml2str(nd).strip()
        # log = self.row_js[self.LOP]
        # log = self.row_js[self.OP]
        d = self.get_node_data(nd)
        id = f"from:{d['id']}"
        val = d['val']
        # s = '{:<6}{:<15}{:<15}{}'.format(log, id, val, xml)
        s = '{:<18} {:<18} {}'.format(id, val, xml)
        s = s.replace(os.linesep, ' ', -1)
        self.logspan(s)

    def log_close(self, nd):
        xml = self.xml2str(nd).strip()
        # log = self.row_js[self.LCL]
        # log = self.row_js[self.CL]
        d = self.get_node_data(nd)
        id = f"to  :{d['id']}"
        val = d['val']
        # s = '{:<6}{:<15}{:<15}{}'.format(log, id, val, xml)
        s = '{:<18} {:<18} {}'.format(id, val, xml)
        s = s.replace(os.linesep, ' ', -1)
        self.logspan(s)
        self.logspan("")

    def control_open(self, nd):
        self.row_tag_over_js[self.OPEN_CLOSE] += 1
        if self.row_tag_over_js[self.OPEN_CLOSE] > 1:
            # log_cl = self.row_js[self.LCL]
            log_cl = self.row_tag_over_js[self.CL]
            xml = self.xml2str(nd).strip()
            e = f"\nERROR 2 missing {log_cl}"
            s = '{:<20}{}'.format(e, xml)
            self.logspan(s)
            self.logspan("")
            self.row_tag_over_js[self.OPEN_CLOSE] -= 1
            self.logerr(s)

    def control_close(self, nd):
        self.row_tag_over_js[self.OPEN_CLOSE] -= 1
        if self.row_tag_over_js[self.OPEN_CLOSE] < 0:
            # log_op = self.row_js[self.LOP]
            log_op = self.row_tag_over_js[self.OP]
            xml = self.xml2str(nd).strip()
            e = f"ERROR 3 missing {log_op}"
            s = '{:<30}{}'.format(e, xml)
            self.logspan(s)
            self.row_tag_over_js[self.OPEN_CLOSE] += 1
            self.logerr(s)

    # text = val or tail
    def find_tag_from(self, text):
        """
        testo:
            pipppo {% esempio

        pattern: {%
        se non lo trova ritorna Faòse
        se lo trova testa tutti pattern di 
        lunghezza >'{%' come {2% , {3%
        qunidi sono piu testati { , {%,  {_
        se ne trova uno con la settasa posizione di {%
        ritorna false
        altrimenti  ritorna true

        pattern: {
        se non lo trova ritorna Faòse
        se lo trova testa tutti pattern di 
        lunghezza >'{' come {_, {%. {2% , {3%
        qunidi sono piu testati { 
        se ne trova uno con la settasa posizione di {
        ritorna false
        altrimenti  ritorna true

        ATTNZIONE
            in chiusura la ricerca avviene a partire da destra
            utilizzanod re group.end()
        """
        t = self.row_tag_over_js[self.OP]
        p0 = text.find(t)
        if p0 < 0:
            return False
        ok = True
        for x in self.tag_op_alter:
            p1 = text.find(x)
            if p1 > -1 and p0 == p1:
                return False
        return ok

    # text = val
    def find_tag_to(self, text):
        try:
            t = self.row_tag_over_js[self.CL]
            m = re.search(t, text)
            if m is None:
                return False
            p0 = m.end()
            ok = True
            for x in self.tag_cl_alter:
                m = re.search(x, text)
                p1 = -1 if m is None else m.end()
                if p1 > -1 and p0 == p1:
                    return False
            return ok
        except Exception as e:
            self.logerr("ERROR 4 rfind_tag_to()")
            self.logerr(f"{text}")
            sys.exit(1)

    def fill_span(self):
        # popola  self.span_data
        #         self.key_span_data
        # per una specifica
        # self.row_tag_over_js
        tp = self.row_tag_over_js[self.TP]
        op = self.row_tag_over_js[self.OP]
        cl = self.row_tag_over_js[self.CL]
        self.logspan(f">>>     {tp}   {op} {cl}  <<<"+os.linesep)
        # nd_data_last=None
        nd_last = None
        # LGDB(pp(self.row_tag_over_js))
        # input('js')
        for nd in self.root_xml.iter():
            trace = False
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            if tag == "body":
                continue
            l = nd_data['liv']
            if l < 3:
                continue
            id_ = nd_data.get('id', 'XXX')
            # if id_ == 'Kch3p1w978':
            #     # trace=True
            #     # LGDB(pp(nd_data))
            #     # set_trace()
            #     pass
            if not tag.lower() in ['w', 'pc', 'gap', 'persname', 'geogname', 'placename']:
                continue
            val = nd_data['val'].strip()
            text = nd_data['text'].strip()
            tail = nd_data['tail'].strip()
            if tag.lower() in ['persname', 'geogname', 'placename']:
                src = tail
            else:
                src = val+tail
            nd_last = nd
            op_ = self.row_tag_over_js[self.OP]
            cl_ = self.row_tag_over_js[self.CL]
            # if len(text)> len(val) :
            # LGDB(f'----------')
            #     LGDB(f"op_cl:{op_} {cl_}\nnode:\n{pp(nd_data)}")
            # continue
            if self.find_tag_from(src):
                #LGDB(f"F {op_} {cl_} src:{src}")
                self.set_from_id(nd_data)
                self.control_open(nd)
                self.log_open(nd)
            if self.find_tag_to(src):
                # il testo coincide con il tag
                if src == self.row_tag_over_js[self.CL]:
                    #LGDB(f"T0 {op_} {cl_} src:{src}")
                    nd_prev = self.get_prev(nd)
                    nd_data = self.get_node_data(nd_prev)
                    self.set_to_id(nd_data)
                    self.control_close(nd)
                    self.log_close(nd)
                else:
                    #LGDB(f"T1 {op_} {cl_} src:{src}")
                    self.set_to_id(nd_data)
                    self.control_close(nd)
                    self.log_close(nd)
            # LGDB(f'span:\n{pp(self.span_data)}')
            # LGDB(pp(self.key_span_data))
            # input("?")
        if self.row_tag_over_js[self.OPEN_CLOSE] > 0:
            # input(self.row_js[self.OPEN_CLOSE])
            # set_trace()
            self.control_open(nd_last)
            self.log_open(nd_last)
            msg = f"ERROR OVERFLOW \n{pp(self.row_js)}\n{pp(nd_data)}"
            self.logerr(msg)
            # UA  controllo errore temporaneo
            input("ERROR W teimover.py overflow")

    ###################################

    def add_xml_span(self, nd, sp_data):
        parent_node = self.get_span_parent(nd)
        if parent_node is None:
            self.logerr("ERROR 5 add_span() parent node <div>  Not Found.")
            sys.exit(1)
        from_id = sp_data[self.DATA_FROM]
        to_id = sp_data[self.DATA_TO]
        tp = sp_data[self.DATA_TYPE]
        s = f'<span from="{from_id}" to="{to_id}" type="{tp}" />'
        if from_id.strip() == "":
            self.logerr(f"\nERROR X {tp} not open")
            self.logerr(s)
            self.logerr("")
        if to_id.strip() == "":
            self.logerr(f"\nERROR Y {tp}  not close")
            self.logerr(s)
            self.logerr("")
        span = etree.XML(s)
        parent_node.append(span)

    def update_xml(self):
        for nd in self.root_xml.iter():
            # esclude iltag body(liv 0)
            tag = self.node_tag(nd)
            if tag == 'body':
                continue
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            if tag in ['w', 'pc', 'gap']:
                nd_id = nd_data['id']
                sp_data = self.span_data.get(nd_id, None)
                if sp_data is not None:
                    self.add_xml_span(nd, sp_data)
                # elimina word vuote
                val = nd_data['val']
                if val == '':
                    nd_p = nd.getparent()
                    nd_p.remove(nd)

    # start
    def add_xml_span_overflow_list(self, csv_path):

        try:
            self.root_xml = etree.parse(self.path_in)
        except Exception as e:
            msg = f"ERROR 6 add_span_to_xml()1\n{self.path_in}\n{e}"
            self.logerr(msg)
            # ssys.exit(1)
            return

        try:
            self.rows_tag_over = read_tags_over_sorted(csv_path)
        except Exception as e:
            msg = f"ERROR 7 add_span_to_xml()2\n{self.path_in}\n{e}"
            self.logerr(msg)
            # sys.exit(1)
            return

        for r in self.rows_tag_over:
            self.tag_op_lst.append(r[1])
            self.tag_cl_lst.append(r[2])
        # LGDB(f"op_lst:\n{pp(self.tag_op_lst)}")
        # LGDB(f"cl_lst:\n{pp(self.tag_cl_lst)}")

        for i in range(0, len(self.rows_tag_over)):
            self.set_row_tag_js(i)

            self.span_data = {}
            self.key_span_data = None

            # per tutti i nodi xml e i tag w,pc
            # crea la lista from to
            # controllo apertura e chiusura dei tag
            self.fill_span()

            # per tutti i nodi xml
            # aggiunge a xml i le righe xml
            # fromm to
            self.update_xml()

        xml = etree.tostring(self.root_xml,
                             xml_declaration=None,
                             encoding='unicode',
                             method="xml",
                             pretty_print=False,
                             with_tail=True,
                             standalone=None,
                             doctype=None,
                             exclusive=False,
                             inclusive_ns_prefixes=None,
                             strip_text=False)

        # rimuove da xml tutti i pattern iniziando
        # da quelli pià lunghi]
        for i, x in enumerate(self.tag_op_lst):
            xml = xml.replace(x, '')
            y = self.tag_cl_lst[i]
            xml = xml.replace(y, '')

        with open(self.path_out, "w") as f:
            f.write(xml)
        os.chmod(self.path_out, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)

        # salva xml formattato
        try:
            xml_path = self.path_out.replace("_over.xml", "_over_format.xml")
            xmf.do_main(self.path_out, xml_path, False)
        except Exception:
            pass


def do_main(path_text,  path_csv):
    TeimOverFlow(path_text, path_csv)
    # self.add_xml_span_overflow_list(path_csv)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit(1)
    parser.add_argument('-i',
                        dest="src",
                        required=True,
                        metavar="",
                        help="-i <file text>")
    parser.add_argument('-c',
                        dest="csv",
                        required=True,
                        metavar="",
                        help="-c <file csv dei tag>")
    args = parser.parse_args()
    do_main(args.src, args.csv)
