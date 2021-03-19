#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import argparse
from lxml import etree
from ualog import Log
from teimxmllint import do_main as do_main_xmllint

__date__ = "02-04-2021"
__version__ = "0.1.2"
__author__ = "Marta Materni"

def do_main(path_xml, path_out):
    logerr = Log("w")
    path_err = path_out.replace('.xml', '_ERR.log')
    logerr.open(path_err, 1)
    path_tmp= path_out.replace('.xml', '.tmp')
    try:
        with open(path_xml,"r") as f:
            text=f.read()
        with open(path_tmp,"w") as f:
            f.write(f"<div>{text}</div>")
        do_main_xmllint(path_tmp,path_out)
        os.remove(path_tmp)
    except etree.Error as e:
        s = str(e)
        logerr.log("ERROR teimxmlformat.py")
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
        sys.exit(1)
    do_main(args.src, args.out)
