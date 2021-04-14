#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aggiunge span from=.. to=..
es. tag from to

TYPE|TAG_FROM|TAG_TO|SIGLA_FROM!SIGLA_TO
directspeech|{|}|ODRD|CDRD
monologue|{_|_}|OMON|CMON
agglutination|[|]|OAGLS|CAGLS
agglutination_uncert|[_|_]|OAGLU|CAGLU
damage|{0%|%0}|ODAM|CDAM
damagel_low|{1%|%1}|ODAML|CDAML
damage_medium|{2%|%2}|ODAMM|CDAMM
damage_high|{3%|%3}|ODAMH|CDAMH
"""
from pdb import set_trace
from lxml import etree
import os
import argparse
import sys
from teimed.ualog import Log
import pprint
import re
import stat
from teimed.readovertags import read_over_tags

__date__ = "11-04-2021"
__version__ = "0.10.6"
__author__ = "Marta Materni"


def pp(data):
    if data is None:
        return ""
    return pprint.pformat(data, indent=2, width=80)


DATA_TYPE = "tp"
DATA_FROM = "from"
DATA_TO = "to"

OP = 'op'
CL = 'cl'
LOP = 'lop'
LCL = 'lcl'
TP = 'tp'
CTRL = 'ctrl'


class Addspan(object):

    def __init__(self, src_path, out_path):
        self.src_path = src_path
        self.path_out = out_path
        self.root = None
        self.span_data = None
        self.key_span_data = ''
        self.row_js = {}
        self.op_alter = []
        self.cl_alter = []
        self.op_lst = []
        self.cl_lst = []
        self.over_tag_rows = []
        # self.over_op_set=[]
        # self.over_cl_set=[]
        # self.over_tag_set=[]
        path_span = out_path.replace('.xml', '.log')
        path_err = out_path.replace('.xml', '.ERR.log')
        self.logspan = Log('w')
        self.logerr = Log('w')
        self.logspan.open(path_span, 0)
        self.logerr.open(path_err, 1)

    def set_row_js(self, i):
        #  0        1       2      3       4
        # descr|from tag|to tag|log opn|log close
        row = self.over_tag_rows[i]
        self.row_js = {
            OP: row[1],
            CL: row[2],
            LOP: row[3],
            LCL: row[4],
            TP: row[0],
            CTRL: 0
        }
        # ordinati per lunghezza ddesc.
        for r in self.over_tag_rows:
            self.op_lst.append(r[1])
            self.cl_lst.append(r[2])          
        self.op_alter = []  # tag alternativi a quello selezionato
        self.cl_alter = []
        op = row[1]         # tag open
        # nella lista di controllo son settati i tag di lunghezza
        # > del tag selezionato
        for j, r in enumerate(self.over_tag_rows):
            o = r[1]
            c = r[2]
            if j == i:
                continue
            if len(o) > len(op):
                self.op_alter.append(o)
                self.cl_alter.append(c)      

    def node_liv(self, node):
        d = 0
        while node is not None:
            d += 1
            node = node.getparent()
        return d - 1

    def node_tag(self, nd):
        tag = nd.tag
        tag = tag if type(nd.tag) is str else "XXX"
        p = tag.rfind('}')
        if p > 1:
            self.logerr.log(os.linesep+"ERROR teimover node_tag()")
            self.logerr.log(tag)
            sys.exit(1)
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
        """
        ls = []
        for x in nd.itertext():
            ls.append(x)
        text = " ".join(ls)
        return text
        """
        val = ""
        for t in nd.itertext():
            val = val + t
        return val

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

    # nodo precedente <w> or <pc>
    def get_prev(self, node):
        nd_prev = node.getprevious()
        tag = nd_prev.tag if type(nd_prev.tag) is str else "XXX"
        if tag.strip() in ['w', 'pc']:
            return nd_prev
        node_data = self.get_node_data(node)
        node_id = node_data['id']
        node_l = self.get_parent_l(node)
        nd_prev = node.getprevious()
        for nd in node_l.iterdescendants():
            tag = node.tag if type(node.tag) is str else "XXX"
            if tag.strip() in ['w', 'pc']:
                nd_data = self.get_node_data(nd)
                nd_id = nd_data['id']
                if nd_id == node_id:
                    break
                nd_prev = nd
        return nd_prev

    # rtorna la linea <l> parent
    def get_parent_l(self, node):
        nd = None
        while node is not None:
            node = node.getparent()
            if node is None:
                break
            tag = node.tag if type(node.tag) is str else "XXX"
            if tag == 'l':
                nd = node
                break
        return nd

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
        tp = self.row_js[TP]
        item = {}
        item[DATA_TYPE] = tp
        item[DATA_TO] = ''
        item[DATA_FROM] = from_id
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
            item[DATA_TO] = to_id
        except Exception as e:
            self.logerr.log(os.linesep+"ERROR teimover set_id_to()")
            self.logerr.log(f'TYPE:{self.row_js[TP]}')
            self.logerr.log(str(e)+os.linesep)
            self.logspan.log(str(e)+os.linesep)
            sys.exit(1)

    def log_open(self, nd):
        xml = self.xml2str(nd).strip()
        #log = self.row_js[LOP]
        log = self.row_js[OP]
        d = self.get_node_data(nd)
        id = f"from:{d['id']}"
        val = d['val']
        # s = '{:<6}{:<15}{:<15}{}'.format(log, id, val, xml)
        s = '{:<18}{:<18}{}'.format(id, val, xml)
        s = s.replace(os.linesep, ' ', -1)
        self.logspan.log(s)

    def log_close(self, nd):
        xml = self.xml2str(nd).strip()
        #log = self.row_js[LCL]
        log = self.row_js[CL]
        d = self.get_node_data(nd)
        id = f"to  :{d['id']}"
        val = d['val']
        #s = '{:<6}{:<15}{:<15}{}'.format(log, id, val, xml)
        s = '{:<18}{:<18}{}'.format(id, val, xml)
        s = s.replace(os.linesep, ' ', -1)
        self.logspan.log(s)
        self.logspan.log("")

    def control_open(self, nd):
        self.row_js[CTRL] += 1
        if self.row_js[CTRL] > 1:
            # log_cl = self.row_js[LCL]
            log_cl = self.row_js[CL]
            xml = self.xml2str(nd).strip()
            e = f"** ERROR missing {log_cl}"
            s = '{:<30}{}'.format(e, xml)
            self.logspan.log(s)
            self.logspan.log("")
            self.row_js[CTRL] -= 1
            self.logerr.log(s)

    def control_close(self, nd):
        self.row_js[CTRL] -= 1
        if self.row_js[CTRL] < 0:
            # log_op = self.row_js[LOP]
            log_op = self.row_js[OP]
            xml = self.xml2str(nd).strip()
            e = f"** ERROR missing {log_op}"
            s = '{:<30}{}'.format(e, xml)
            self.logspan.log(s)
            self.row_js[CTRL] += 1
            self.logerr.log(s)

    """
    testo: 
        pipppo {% esempio
    pattern: {%
       testa tutti pattern di lunghezza >'{%' 
       qunidi '{' non viene testato 
       ritorna true
    pattern: {
        testa tutti i pattern dilunghezza > '{'
        viene trovato per '{%' 
        ritona false
    ATTNZIONE
        in chiusura la ricerca avviene a partire da destra
        utilizzanod re group.end()
    
    """
    def find_tag_from(self, s):
        t = self.row_js[OP]
        p0 = s.find(t)
        if p0 < 0:
            return False
        ok = True
        for x in self.op_alter:
            p1 = s.find(x)
            if p1 > -1 and p0 == p1:
                return False
        return ok

    def find_tag_to(self, s):
        try:
            t = self.row_js[CL]
            m = re.search(t, s)
            if m is None:
                return False
            p0 = m.end()
            ok = True
            for x in self.cl_alter:
                m = re.search(x, s)
                p1 = -1 if m is None else m.end()
                if p1 > -1 and p0 == p1:
                    return False
            return ok
        except Exception as e:
            self.logerr.log("ERROR teimover.py rfind_tag_to()")
            self.logerr.log(f"{s}")
            sys.exit(1)

    def fill_span(self):
        tp = self.row_js[TP]
        op=self.row_js[OP]
        cl=self.row_js[CL]
        self.logspan.log(f">>>     {tp}   {op} {cl}  <<<"+os.linesep)
        nd_data_last=None
        nd_last=None
        for nd in self.root.iter():
            trace = False
            # esclude iltag body(liv 0)
            tag = self.node_tag(nd)
            if tag == 'body':
                continue
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            """
            id=nd_data.get('id','XXX')
            if id=='Gl4w2':
                #trace=True
                #set_trace()
                pass
            """    
            if tag in ['w','pc']:
                text = nd_data['text']
                val = nd_data['val']
                tail= nd_data['tail']
                nd_data_last=nd_data
                nd_last=nd

                if self.find_tag_from(val):
                    # print(f"{self.row_js[LOP]} {self.row_js[OP]}  {val} {text}")
                    self.set_from_id(nd_data)
                    self.control_open(nd)
                    self.log_open(nd)

                if self.find_tag_from(tail):
                    # print(f"{self.row_js[LOP]} {self.row_js[OP]}  {tail} {text}")
                    self.set_from_id(nd_data)
                    self.control_open(nd)
                    self.log_open(nd)

                if self.find_tag_to(val):
                    if text.strip() == self.row_js[CL]:
                        #print(f"{self.row_js[OP]}_A {self.row_js[OP]}  {val} {text}")
                        nd_prev = self.get_prev(nd)
                        nd_data = self.get_node_data(nd_prev)
                        self.set_to_id(nd_data)
                        self.control_close(nd)
                        self.log_close(nd)
                    else:
                        # print(f"{self.js[LOP]}_B {self.js[OP]}  {val} {text}")
                        self.set_to_id(nd_data)
                        self.control_close(nd)
                        self.log_close(nd)
        if self.row_js['ctrl'] > 0:
            self.control_open(nd_last)
            self.log_open(nd_last)
        

    def add_span(self, nd, sp_data):
        parent_node = self.get_span_parent(nd)
        if parent_node is None:
            self.logerr.log(
                "ERROR teimover.py add_span() parent node <div>  Not Found.")
            sys.exit(1)
        from_id = sp_data[DATA_FROM]
        to_id = sp_data[DATA_TO]
        tp = sp_data[DATA_TYPE]
        s = f'<span from="{from_id}" to="{to_id}" type="{tp}" />'
        if from_id.strip()=="" :
            self.logerr.log(f"{tp} not open")
            self.logerr.log(s)
            self.logerr.log("")
        if to_id.strip()=="":
            self.logerr.log(f"{tp} not close")
            self.logerr.log(s)
            self.logerr.log("")
        # log di xml span
        # self.logspan.log(s)
        span = etree.XML(s)
        parent_node.append(span)

    def update_xml(self):
        for nd in self.root.iter():
            # esclude iltag body(liv 0)
            tag = self.node_tag(nd)
            if tag == 'body':
                continue
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            if tag in ['w', 'pc']:
                nd_id = nd_data['id']
                sp_data = self.span_data.get(nd_id, None)
                if sp_data is not None:
                    self.add_span(nd, sp_data)
                # elimina word vuote
                val = nd_data['val']
                if val == '':
                    nd_p = nd.getparent()
                    nd_p.remove(nd)

    def add_span_to_root(self, csv_path):
        try:
            self.root = etree.parse(self.src_path)
        except Exception as e:
            self.logerr.log(os.linesep+"ERROR teimover.py add_span_to_root()")
            self.logerr.log(str(e))
            #ssys.exit(1)
            return
        try:
            self.over_tag_rows = read_over_tags(csv_path)
        except Exception as e:
            self.logerr.log("ERROR teimover.py read_overTags()")
            self.logerr.log(str(e))
            #sys.exit(1)
            return
        for i in range(0, len(self.over_tag_rows)):
            self.set_row_js(i)
            self.span_data = {}
            self.key_span_data = None
            self.fill_span()
            self.update_xml()
        xml = etree.tostring(self.root,
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
        for i, x in enumerate(self.op_lst):
            xml = xml.replace(x, '')
            y = self.cl_lst[i]
            xml = xml.replace(y, '')
        with open(self.path_out, "w") as f:
            f.write(xml)
        os.chmod(self.path_out, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)

def do_main(src_path, out_path, csv_path):
    Addspan(src_path, out_path).add_span_to_root(csv_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit(1)
    try:
        parser.add_argument('-i',
                            dest="src",
                            required=True,
                            metavar="",
                            help="-i <file input>")
        parser.add_argument('-o',
                            dest="out",
                            required=True,
                            metavar="",
                            help="-o <file output>")
        parser.add_argument('-c',
                            dest="cfg",
                            required=True,
                            metavar="",
                            help="-c <file csv dei tag>")
        args = parser.parse_args()
    except Exception as e:
        print("ERROR args in teimover.py ")
        print(str(e))
        sys.exit(1)
    do_main(args.src, args.out, args.cfg)
