#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pdb import set_trace
import argparse
import sys
import pprint
import re
from teimedlib.ualog import Log
from teimedlib.teimtxtread import TeimTxtRead
from teimedlib.teim_paths import *


__date__ = "20-07-2021"
__version__ = "1.1.1"
__author__ = "Marta Materni"


def pp(data,w=40):
    s = pprint.pformat(data, indent=0, width=w)
    return s


class CheckText(object):
    BLK = '                                                                                  '
    SEP1 = "...................................................."
    SEP2 = "======================================================="
    OP = '('
    CL = ')'

    """
    controlla nel file teimed sorgente le entitities.
    Controlla la froma nel tipo 
    &abcd;
    e la chusura delle parentesi  nel tipo
    &abcd;(arg1,arg2)
    """
    def __init__(self, path_text):
        self.path_text = path_text

        path_out=set_path_checktxt_out(path_text)
        self.log_info = Log("w").open(path_out, 1).log

        path_err=set_path_checktxt_err(path_text)
        self.log_err = Log("w").open(path_err, 1).log

        self.trace = False
        self.rows = []
        self.rnd_rows = []

    # def read_text(self):
    #     self.rows = []
    #     with open(self.path_src, "r") as f:
    #         for row in f:
    #             #row = row.replace('\ufeff', '', -1)
    #             #row = row.replace('\t', ' ', -1)
    #             pc = row.find('<!')
    #             if pc > -1:
    #                 row = row[0:pc - 1]
    #             if row.strip() != "":
    #                 # row=row.strip()
    #                 pass
    #             self.rows.append(row)
    
    def read_text(self):
        ttr=TeimTxtRead(self.path_text,self.log_err)
        rows=ttr.read_text_rows()
        # UA VERIFICARE rows=ttr.add_spc_to_punct(rows)
        rows = ttr.join_words_wrap(rows)
        rows = ttr.clean_brackets(rows)
        self.rows=rows  
    
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
                        self.log_info(f'{row_num+1}')
                        self.log_info(row.strip())
                    prn_root = False
                    sp = self.BLK[0:x+x0]
                    t = r[x0:x1+1]
                    s = f'{sp}{t}'
                    self.log_info(s)
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
        #self.log.log(self.SEP2)
        self.rnd_rows = []
        for row_num, row in enumerate(self.rows):
            rnd_row = []
            open_close = 0
            closing = 0
            num = 0
            for i, c in enumerate(row):
                if c == self.OP:
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
                elif c == self.CL:
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
                self.log_info_err(row_num, row, err_lst)

    def log_info_err(self, row_num, row, err_lst):
        self.log_info(f'.{row_num+1}')
        self.log_info(row.strip())
        for err in err_lst:
            x0 =err['x0']
            x1=err['x1']
            msg=err['msg']
            expr=row[x0:x1+1]
            s=f"{self.SEP1[0:x0]}{expr}"
            spc=self.BLK[:2]
            self.log_info(f'{s}{spc}{msg}')

    def expr_err(self, row, e0, e1):
        open_close = e1['open_close']
        msg = ''
        err = 0
        if open_close > 0:
            err = 1
            msg = f'{-open_close}{self.CL}'
        elif open_close < 0:
            err = 2
            msg = f'{open_close}{self.OP}'
        #msg = f"  {self.OP} {self.CL}"
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
            self.log_info(row.strip())
            for i, r in enumerate(lst):
                s=pp(r)
                self.log_info(s)

    def check_txt(self):
        head = f"{self.path_text}"
        self.log_info(self.SEP2[0:30])
        self.log_info('checktxt')
        self.log_info(head)
        self.log_info(self.SEP2[0:30])
        self.read_text()
        self.check_entity()
        self.check_round()

def do_main(path_text):
    check = CheckText(path_text)
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
    args = parser.parse_args()
    do_main(args.src)
