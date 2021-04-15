#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from pdb import set_trace
from teimedlib.ualog import Log
import pprint
import re

__date__ = "19-02-2021"
__version__ = "0.2.1"
__author__ = "Marta Materni"


def pp(data):
    if data is None:
        return ""
    s = pprint.pformat(data, indent=0, width=90)
    return s



ls = [' ' for i in range(0, 1000)]
BLK = ''.join(ls)
SEP1 = "...................................................."
SEP2 = "======================================================="
OP = '('
CL = ')'


class CheckRound(object):

    def __init__(self, path_src,  path_out):
        self.path_src = path_src
        out_name = path_out.split('.')[0]
        path_out = path_out
        path_err = f"{out_name}.ERR.log"
        self.log = Log("w")
        self.log.open(path_out, 1)
        self.logerr = Log("w")
        self.logerr.open(path_err, 1)
        self.trace = False
        self.rows = []
        self.rnd_rows = []

    def read_text(self):
        self.rows = []
        with open(self.path_src, "r") as f:
            for row in f:
                #row = row.replace('\ufeff', '', -1)
                #row = row.replace('\t', ' ', -1)
                pc = row.find('<!')
                if pc > -1:
                    row = row[0:pc - 1]
                if row.strip() != "":
                    # row=row.strip()
                    pass
                self.rows.append(row)

    def check_entity(self):
        ptrn = r"&{1}[\w-]*[;]{0,1}[(]{0,1}"
        for row_num, row in enumerate(self.rows):
            r = row
            x = 0
            prn_root = True
            while True:
                r = r if x == 0 else r[x:]
                m = re.search(ptrn, r)
                if m is None:
                    break
                s = m.group()
                x0 = m.start()
                x1 = m.end()
                if s.find(';') < 0:
                    if prn_root:
                        #self.log.log("")
                        self.log.log(f'{row_num+1}')
                        self.log.log(row.strip())
                    prn_root = False
                    sp = BLK[0:x+x0]
                    t = r[x0:x1+1]
                    s = f'{sp}{t}'
                    self.log.log(s)
                x = m.end()

    def new_rnd(self):
        js = {
            "num": 0,
            "x": 0,
            "c": '',
            "open_close": 0,
            "closing": 0,
            "is_first": False,
            "is_last": False
        }
        return js

    def check_round(self):
        self.log.log(SEP2)
        self.rnd_rows = []
        for row_num, text in enumerate(self.rows):
            rnd_row = []
            open_close = 0
            closing = 0
            num = 0
            for i, c in enumerate(text):
                if c == OP:
                    is_first = (open_close == 0)
                    open_close += 1
                    if is_first:
                        num += 1
                    ro = self.new_rnd()
                    ro["x"] = i
                    ro["c"] = c
                    ro["is_first"] = is_first
                    ro["open_close"] = open_close
                    ro["closing"] = closing
                    ro["num"] = num
                    rnd_row.append(ro)
                elif c == CL:
                    open_close -= 1
                    is_last = (open_close == 0)
                    if is_last:
                        closing += 1
                    rc = self.new_rnd()
                    rc["x"] = i
                    rc["c"] = c
                    rc["is_last"] = is_last
                    rc["open_close"] = open_close
                    rc["closing"] = closing
                    rc["num"] = num
                    rnd_row.append(rc)
            self.rnd_rows.append(rnd_row)
        ######
        self.find_err()
        #self.log_deb()

    def find_err(self):
        for row_num, row in enumerate(self.rows):
            rnd_lst = self.rnd_rows[row_num]
            if len(rnd_lst) == 0:
                continue
            num_lst = [r["num"] for r in rnd_lst]
            num_lst = sorted(list(set(num_lst)))
            err_lst = []
            for num in num_lst:
                elm_lst = [x for x in rnd_lst if x['num'] == num]
                e_first = elm_lst[0]
                e_last = elm_lst[-1:][0]
                open_close = e_last['open_close']
                if open_close != 0:
                    err = self.expr_err(row, e_first, e_last)
                    err_lst.append(err)
            if len(err_lst) > 0:
                self.log_err(row_num, row, err_lst)

    def log_err(self, row_num, row, err_lst):
        self.log.log(f'.{row_num+1}')
        self.log.log(row.strip())
        for err in err_lst:
            x0 =err['x0']
            x1=err['x1']
            msg=err['msg']
            expr=row[x0:x1+1]
            s=f"{SEP1[0:x0]}{expr}"
            spc=BLK[:2]
            self.log.log(f'{s}{spc}{msg}')

    def expr_err(self, row, e0, e1):
        open_close = e1['open_close']
        msg = ''
        err = 0
        if open_close > 0:
            err = 1
            msg = f'{-open_close}{CL}'
        elif open_close < 0:
            err = 2
            msg = f'{open_close}{OP}'
        #msg = f"  {OP} {CL}"
        x0 = e0['x']
        x1 = e1['x']
        js = {'x0': x0,
              'x1': x1,
              'err': err,
              "msg": msg}
        return js


    def log_deb(self):
        for row_num, row in enumerate(self.rows):
            lst = self.rnd_rows[row_num]
            if len(lst) == 0:
                continue
            self.log.log(row.strip())
            for i, r in enumerate(lst):
                s=pp(r)
                self.log.log(s)


    def check_txt(self):
        head = f"{self.path_src}"
        self.log.log(SEP2[0:len(head)])
        self.log.log(head)
        self.log.log(SEP2[0:len(head)])
        self.read_text()
        self.check_entity()
        self.check_round()


def do_main(path_src, path_out):
    check = CheckRound(path_src,  path_out)
    check.check_txt()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print(f"release: {__version__} { __date__}")
        parser.print_help()
        sys.exit()
    parser.add_argument('-i',
                        dest="src",
                        required=True,
                        metavar="",
                        help="-i <file text>")
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
