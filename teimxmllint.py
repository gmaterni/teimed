#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import argparse
from lxml import etree
from teimedlib.ualog import Log
import stat
__date__ = "19-02-2021"
__version__ = "0.3.3"
__author__ = "Marta Materni"



def do_main(path_xml, path_out):
    path_err = path_out.replace('.xml', '_ERR.log')
    logerr = Log("w")
    logerr.open(path_err, 1)
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.parse(path_xml, parser)
        src = etree.tostring(root,
                             method='xml',
                             xml_declaration=None,
                             encoding='unicode',
                             with_tail=True,
                             pretty_print=True)
        # s = etree.tostring(root, pretty_print=True)
        with open(path_out, "w+") as fw:
            fw.write(src)
        os.chmod(path_out, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)

    except etree.Error as e:
        s = str(e)
        logerr.log("ERROR XML")
        logerr.log(s)
        sys.exit(1)


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
                        help="-i <file input>")
    parser.add_argument('-o',
                        dest="out",
                        required=True,
                        metavar="",
                        help="-o <file output>")
    args = parser.parse_args()
    if args.src == args.out:
        print("Name File output errato")
        sys.exit(0)
    do_main(args.src, args.out)
