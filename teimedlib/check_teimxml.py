#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import argparse
import os
import re
import sys
from lxml import etree
from teimedlib.ualog import Log

__date__ = "20-05-2022"
__version__ = "0.0.1"
__author__ = "Marta Materni"


class CheckTeimXml:
    """
    controlla l'uso dei tag in tei-xml
    """

    def __init__(self):
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
        id_ = self.node_id(nd)
        tag = self.node_tag(nd)
        if tag == 'w':
            # set_trace()
            pass
        liv = self.node_liv(nd)
        if tag.lower() in ('div', 'body'):
            val = ''
        else:
            val = self.node_val(nd)
        js = {
            'id': id_,
            'liv': liv,
            'tag': tag,
            'text': self.node_text(nd),
            'tail': self.node_tail(nd),
            'val': val,
            'is_parent': self.node_is_parent(nd),
            'row_num': nd.sourceline
        }
        return js

    def check_tag(self, data):
        err = ""
        tag = data.get('tag', "")
        tail = data.get("tail", '')
        text = data.get("text", '')
        val = data.get("val", '')
        row_num = data.get('row_num', '')
        if tag == 'w':
            if tail != '':
                err = f"\n{row_num}) {tag}: text  out of word "
                self.logerr(f"{err}")
                msg = f"text:{text}"
                self.logerr(msg)
                msg = f"tail:{tail} "
                self.logerr(msg)

    def check_tei_xml(self, path_xml, logerr):
        self.logerr = logerr
        try:
            parser = etree.XMLParser(ns_clean=True)
            xml_root = etree.parse(path_xml, parser)
        except Exception as e:
            self.logerr("ERROR_0 check_tei_xml()")
            self.logerr(e)
            sys.exit(str(e))
        # controllo dei tag
        for nd in xml_root.iter():
            nd_data = self.get_node_data(nd)
            self.check_tag(nd_data)


def do_main(path_xml):
    path_err = path_xml.replace(".xml", ".tei_xml_ERR.log")
    logerr = Log("w").open(path_err, 1).log
    ctx = CheckTeimXml()
    ctx.check_tei_xml(path_xml, logerr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit(1)
    parser.add_argument('-i',
                        dest="xml",
                        required=True,
                        metavar="",
                        help="-i <file_in.xml>")
    args = parser.parse_args()
    do_main(args.xml)
