#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import sys
import argparse
from teimedlib.clean_text import clean_text
from teimedlib.ualog import Log

__date__ = "29-11-2022"
__version__ = "0.0.1"
__author__ = "Marta Materni"


def check_open_close_tag(text_path, tag_open, tag_close):
    text = open(text_path, "r").read()
    text = clean_text(text)
    ptr = fr"({tag_open})|({tag_close})"
    lst = []
    n = 0
    oc = 0
    err=False
    for m in re.finditer(ptr, text):
        s = m.group()
        x0 = m.start()
        x1 = m.end() + 50
        t = text[x0:x1]
        if s == tag_open:
            n += 1
            if oc != 0:
                lst.append(f"ERROR\n")
                err=True
                oc = 0
            lst.append(f"\n{n}")
            oc += 1
        if s == tag_close:
            oc -= 1
        lst.append(t)

    op_cl = f'{tag_open.strip()}_{tag_close.strip()}'.replace(";", "").replace('&','')
    if err:
        log_path = text_path.replace(".txt", f"_{op_cl}_ERR.log.")
    else:
        log_path = text_path.replace(".txt", f"_{op_cl}.log")
    log = Log("w").open(log_path, 1).log
    for x in lst:
        log(x)

def do_main(text_path, tag_open, tag_close):
    check_open_close_tag(text_path, tag_open, tag_close)


# text_path = "tr_gre_teimed_005.txt"
# tag_open = "&chB;"
# tag_close = "&chE;"
# do_main(text_path, tag_open, tag_close)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit(1)
    parser.add_argument('-t',
                        dest="txt_path",
                        required=True,
                        default=None,
                        type=str,
                        metavar="files match",
                        help="-t <file.txt>")
    parser.add_argument('-o',
                        dest="op",
                        required=True,
                        metavar="",
                        help='-o "<tag_open>" ')
    parser.add_argument('-c',
                        dest="cl",
                        required=True,
                        metavar="",
                        help='-c "<tag_close>"')
    args = parser.parse_args()
    do_main(args.txt_path, args.op, args.cl)
