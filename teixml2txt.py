#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import argparse
import os
import stat
from io import StringIO
import pprint
import re
import sys
import traceback
from lxml import etree
from teimedlib.txtbuilder import TxtBuilder
from teimedlib.ualog import Log
import teimedlib.pathutils as ptu

__date__ = "26-03-2022"
__version__ = "0.2.6"
__author__ = "Marta Materni"


#sostituire con libreria def make_dir_of_file(path):
# def make_dir_of_file(path):
    # dirname = os.path.dirname(path)
    # if dirname.strip() == '':
    #     return
    # make_dir(dirname)

# def make_dir(dirname):
    # try:
    #     if not os.path.isdir(dirname):
    #         os.mkdir(dirname)
    #         os.chmod(dirname, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)
    #         return True
    #     else:
    #         return False
    # except Exception as e:
    #     s = str(e)
    #     msg = f"ERROR make_dir{os.linesep}{s}"
    #     raise Exception(msg)


def chmod(path):
    os.chmod(path, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)


def pp(data, w=40):
    s = pprint.pformat(data, indent=2, width=w)
    return s


class Xml2Txt:
    """
    Estrae un file di testo da un file tei xml
    """

    def __init__(self,
                 path_xml='',
                 path_txt='',
                 write_append='w'):
        self.path_xml = path_xml
        self.path_txt = path_txt
        self.write_append = write_append

        path_err = path_txt.replace(".txt", ".ERR.log")
        self.logerr = Log("w").open(path_err, 1).log

        self.txt_builder = None
        self.w_liv = 1000
        self.trace = False

    def node_liv(self, node):
        d = 0
        while node is not None:
            d += 1
            node = node.getparent()
        return d - 1

    def clean_key(self, k):
        s = k
        p0 = k.find("{http")
        if (p0 > -1):
            p1 = k.rfind('}')
            if p1 > -1:
                s = k[p1+1:]
        return s

    def node_items(self, nd):
        kvs = nd.items()
        js = {}
        for kv in kvs:
            k = self.clean_key(kv[0])
            v = kv[1]
            js[k] = v
        return js

    def node_tag(self, nd):
        try:
            tag = nd.tag
            tag = tag if type(nd.tag) is str else "XXX"
            pid = tag.find('}')
            if pid > 0:
                tag = tag[pid + 1:]
            return tag.strip()
        except Exception as e:
            self.logerr("ERROR in xml")
            self.logerr(str(e))
            return "XXX"

    def node_id(self, nd):
        s = ''
        kvs = nd.items()
        for kv in kvs:
            if kv[0].rfind('id') > -1:
                s = kv[1]
                break
        return s

    def node_id_num(self, id):
        if id == '':
            return ''
        m = re.search(r'\d', id)
        if m is None:
            return -1
        p = m.start()
        return id[p:]

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
            s = x.strip().replace(os.linesep, '')
            ls.append(s)
        texts = ' '.join(ls)
        s = re.sub(r"\s{2,}", ' ', texts)
        return s

    def node_is_parent(self, nd):
        cs = nd.getchildren()
        le = len(cs)
        return le > 0

    def get_node_data(self, nd):
        items = self.node_items(nd)
        id = self.node_id(nd)
        if id != '':
            id_num = self.node_id_num(id)
            items['id_num'] = id_num
        tag = self.node_tag(nd)
        liv = self.node_liv(nd)
        if tag == 'w':
            self.w_liv = liv
        if liv >= self.w_liv:
            val = self.node_val(nd)
        else:
            val = ''
        js = {
            'id': id,
            'liv': liv,
            'tag': tag,
            'text': self.node_text(nd),
            'tail': self.node_tail(nd),
            'items': items,
            # 'keys': self.node_keys(nd)
            'val': val,
            'is_parent': self.node_is_parent(nd)
        }
        return js

    def build_txt_data(self, nd):
        """ crea un json contenente
        x_data (estratto da xml)
        t_data (empty per la furua elaborazione)
        Args:
            nd : nod xml
        Returns:
            json: json=x_data + c_data + t_data
        """
        nd_data = self.get_node_data(nd)
        txt_data = {
            'id': nd_data.get('id', 0),
            'is_parent': nd_data.get('is_parent', False),
            'items': nd_data.get('items', {}),
            'liv': nd_data.get('liv', 0),
            'tag': nd_data.get('tag', ''),
            'text': nd_data.get('text', ''),
            'tail': nd_data.get('tail', ''),
            'val': nd_data.get('val', ''),
            't_i': 0,
            't_type': '',
            't_up': False,
            't_start': '',
            't_end': '',
            't_sp': '',
            't_ln': False,
            't_flag': False
        }
        return txt_data

    def write_txt(self):
        try:
            parser = etree.XMLParser(ns_clean=True)
            xml_root = etree.parse(self.path_xml, parser)
        except Exception as e:
            self.logerr("ERROR teixml2txt.py write_txt() parse_xml")
            self.logerr(e)
            sys.exit(str(e))
        try:
            self.txt_builder = TxtBuilder()
            ########################
            for nd in xml_root.iter():
                txt_data = self.build_txt_data(nd)

                # 
                # x_id = txt_data['id']
                # if x_id == "Kch1p1w104":
                #     # self.trace = True
                #     pass
                # if self.trace:
                #     print(x_id)
                #     print(pp(txt_data, 20))
                #     tag = txt_data['tag']
                #     if tag in ('w', 'expan','ex'):
                #         xml = etree.tostring(nd,
                #                              method='xml',
                #                              xml_declaration=None,
                #                              encoding='unicode',
                #                              with_tail=True,
                #                              pretty_print=False,
                #                              standalone=None,
                #                              doctype=None,
                #                              exclusive=False,
                #                              inclusive_ns_prefixes=None)
                #         xml = xml.replace(os.linesep, '')
                #         p = xml.find(f'<{tag}')
                #         print(xml[p:])
                #     set_trace()

                self.txt_builder.add(txt_data)
            ########################
            self.txt_builder.elab()
            txt = self.txt_builder.txt
            ptu.make_dir_of_file(self.path_txt)
            with open(self.path_txt, self.write_append) as f:
                f.write(txt)
            chmod(self.path_txt)
        except Exception as e:
            self.logerr("ERROR teixml2txt.py write_html()")
            self.logerr(e)
            ou = StringIO()
            traceback.print_exc(file=ou)
            st = ou.getvalue()
            ou.close()
            self.logerr(st)
            sys.exit(1)
        return self.path_txt


def do_main(xml, txt, wa='w'):
    Xml2Txt(xml, txt, wa).write_txt()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit(1)
    parser.add_argument('-wa',
                        dest="wa",
                        required=False,
                        metavar="",
                        default="w",
                        help="[-wa w/a (w)rite a)ppend) default w")
    parser.add_argument('-i',
                        dest="xml",
                        required=True,
                        metavar="",
                        help="-i <file_in.xml>")
    parser.add_argument('-o',
                        dest="txt",
                        required=True,
                        metavar="",
                        help="-o <file_out.txt>")
    args = parser.parse_args()
    do_main(args.xml, args.txt, args.wa)
