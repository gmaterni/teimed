#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import sys
import os
import argparse
import re
from lxml import etree
from teimedlib.ualog import Log
from teimedlib.teim_paths import *

__date__ = "29-07-2021"
__version__ = "1.1.6"
__author__ = "Marta Materni"


def do_main(path_in,path_out,add_div):
    """
    formatta un file xml 
    se add_div aggiunge
    <div> </div>
    """
    path_err=path_out.replace('.xml',".xml.ERR.log")
    log_err = Log("w").open(path_err, 1).log
    def make_xml_err(xml, err):
        m = re.search(r'(line )([0-9]+)(,)', err)
        if m is not None:
            s = m.group(2)
            n = int(s)
        else:
            n = -1
        rows = xml.split(os.linesep)
        for i, row in enumerate(rows):
            rows[i] = f'{i+1}){row}'
            if i+1 == n:
                rows[i] = f'\nERRROR\n{rows[i]}\n{err}\n'
        text = os.linesep.join(rows)
        return text

    try:
        with open(path_in, "r") as f:
            src = f.read()
    except Exception as e:
        msg_err = f"ERROR format_xml()\n read xml\n{e}"
        log_err(msg_err)
        return
    try:
        if add_div:
            xml_src = f'<div>{src}</div>'
        else:
            xml_src=src
        #xml_src = f'<div>{src}</div>'
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.XML(xml_src, parser)
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
        msg_err = f"ERROR format_xml()\n{e}"
        xml_err = make_xml_err(src, str(e))
        log_err(xml_err, os.linesep)
        log_err(msg_err)
        try:
            os.remove(path_out)
        except:
            pass
    else:
        with open(path_out, "w") as f:
            f.write(xml)

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
                        help="-i <file>")
    parser.add_argument('-o',
                        dest="xml",
                        required=True,
                        metavar="",
                        help="-o <file.xml>")
    parser.add_argument('-a',
                        action="store_true",
                        required=False,
                        help="-a add <div></div>")
    args = parser.parse_args()
    do_main(args.src,args.xml,args.a)
