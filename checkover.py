#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pdb import set_trace
import argparse
import re
import sys
from teimedlib.ualog import Log
import pprint
from teimedlib.readovertags import read_over_tags_sorted

__date__ = "28-04-2021"
__version__ = "0.1.4"
__author__ = "Marta Materni"

"""
TYPE|TAG_FROM|TAG_TO|SIGLA_FROM!SIGLA_TO

TP|OP|CL|LOP|LCL |ctrl

directspeech|{|}|ODRD|CDRD
monologue|{_|_}|OMON|CMON
agglutination|[|]|OAGLS|CAGLS
agglutination_uncert|[_|_]|OAGLU|CAGLU
damage|{0%|%0}|ODAM|CDAM
damage_low|{1%|%1}|ODAML|CDAML
damage_medium|{2%|%2}|ODAMM|CDAMM
damage_high|{3%|%3}|ODAMH|CDAMH
"""
def pp(data):
    if data is None:
        return ""
    s = pprint.pformat(data, indent=0, width=90)
    return s


ls = [' ' for i in range(0, 1000)]
BLK = ''.join(ls)
SEP1 = "...................................................."
SEP2 = "======================================================="
CNTST_LFT = 20
CNTST_RGT = 20


class CheckOverflow(object):

    def __init__(self, path_src, path_csv, path_out):
        self.path_src = path_src
        self.path_csv = path_csv
        out_name = path_out.split('.')[0]
        path_info = path_out
        path_err = f"{out_name}.ERR.log"
        self.log = Log("w")
        self.logerr = Log("w")
        self.log.open(path_info, 1)
        self.logerr.open(path_err, 1)
        self.text = ''
        self.spc = ''
        self.len_text=0
        self.brk_lst=[]
        self.tag_trype = ""
        self.tag_open=""
        self.tag_close=""
        self.err1=0
        self.err2=0

    def read_text(self):
        rows = []
        with open(self.path_src, "r") as f:
            for n,row in enumerate(f):
                # row = row.replace('\ufeff', '', -1)
                # row = row.replace('\t', ' ', -1)
                pc = row.find('<!')
                if pc > -1:
                    row = row[0:pc - 1]
                row=row.strip()
                if row == "":
                    continue
                row=f"<{n}> {row}"
                rows.append(row)
        self.text = " ".join(rows)


    # index di sinistra di x
    # se non esiste ritorna -1
    #             x
    # pippo] [test]   => [test]
    # [pippo] [test]  => [tet]
    # test]           => test]
    def find_lft(self, s, txt, x):
        i0 = 0
        ls = []
        while True:
            i = txt.find(s, i0)
            ls.append(i)
            if i < 0:
                break
            if i >= x:
                break
            i0 = i+1
        le = len(ls)
        if le <= 1:
            return -1
        else:
            return ls[le-2]

    def new_brk(self):
        js = {
            "tag": "",
            "is_open": False,
            #"is_close": False,
            #"open_close": 0,
            #"num": 0,
            "x": 0,
            "err":0,
            "txt": "",
            "row_num":""
            # "closing": 0,
            # "is_first": False,
            # "is_last": False
        }
        return js

    #  0        1       2      3       4
    # descr|from tag|to tag|log opn|log close

    def check_tag(self):
        op = self.tag_open
        cl = self.tag_close
        op_x0 = 0
        cl_x0 = 0
        op_num = 0
        cl_num = 0
        self.brk_lst = []
        ptrn=r"<[\d]+>"
        while True:
            brk={}
            op_x = self.text.find(op, op_x0)
            if op_x > -1:
                op_x0 = op_x+1
                op_num += 1
                brk = self.new_brk()
                brk['tag'] = op
                brk['x']=op_x
                brk['is_open'] = True
                #
                s=self.text[op_x+1:]
                m=re.search(ptrn,s)
                if m is None:
                    rnum=""
                else:
                    rnum=m.group().replace('<','').replace('>','')
                brk['row_num']=rnum
                #
                self.brk_lst.append(brk)
            cl_x = self.text.find(cl, cl_x0)
            if cl_x > -1:
                cl_x0 = cl_x+1
                cl_num += 1
                brk = self.new_brk()
                brk['tag'] = cl
                brk['x'] = cl_x
                #
                s=self.text[cl_x+1:]
                m=re.search(ptrn,s)
                if m is None:
                    rnum=""
                else:
                    rnum=m.group().replace('<','').replace('>','')
                brk['row_num']=rnum
                #
                #brk['is_close'] = True
                self.brk_lst.append(brk)
            if op_x < 0 and cl_x < 0:
                break


    # ..[y...[x...]....  y:err=1
    # .0[1...[21..]0...
    #
    # ..[....]....]x..   x:err=2
    # .0[1...]0...]-1..
    #
    # ..[y...[x...]....]z..  y:err=1
    # .0[1...[21..]0...]-1.. z:err-1
    def find_err(self):
        self.err1 = 0
        self.err2 = 0
        oc = 0
        for i, brk in enumerate(self.brk_lst):
            if brk["is_open"]:
                oc += 1
                if oc > 1:
                    bk = self.brk_lst[i-1]
                    bk["err"] = 1
                    self.err1 += 1
                    oc = 1
            else:
                oc -= 1
                if oc < 0:
                    brk["err"] = 2
                    self.err2 +=1
                    oc = 0
        if oc==0:
            return
        # quando manca la chiusura dell'ultimo tag
        brk=self.brk_lst[-1:][0]
        if brk["is_open"]:
            brk["err"]=1

    def trunc_rgt(self,txt,x):
        o=txt.find(self.tag_open,x+1)
        o=o if o > -1 else sys.maxsize
        c=txt.find(self.tag_close,x+1)
        c=c if c > -1 else sys.maxsize
        x=min(o,c,len(txt))
        return txt[0:x]

    def log_err(self):
        s0=""
        s1=""
        s2=""
        if self.err1 + self.err2  !=0:
            s0=f"{self.tag_type}  {self.tag_open}  {self.tag_close}"
            self.log.log(SEP2[0:len(s0)])
        if self.err1 > 0:
            s1=f"missing:({self.err1}) {self.tag_close}"
        if self.err2 > 0:
            s2=f"missing:({self.err2}) {self.tag_open}"
        if s0!="":
            s="{:<30}{:<20}{}".format(s0,s1,s2)
            self.log.log(s)
            msg=f"missing"
            self.log.log("{:.<60}{}".format("",msg))
        CNTST_LFT=20
        CNTST_RGT=20
        for brk in self.brk_lst:
           err = brk.get("err", 0)
           row_num=brk.get("row_num","")
           # missing cllose
           if err==1:
               x=brk["x"]
               rgt = x+min(self.len_text-x, CNTST_RGT)
               txt = self.text[x:rgt]
               txt=txt.strip()
               #brk['txt']=txt
               msg=f"{self.tag_close}"
               s1 = "{:<5}) {:.<60}  {}".format(row_num,txt,msg)
               self.log.log(s1)
               self.log.log(self.tag_open)
               self.log.log("")
           # missing open
           elif err ==2:
               x=brk["x"]
               lft = x-min(x, CNTST_LFT)
               rgt = x+len(self.tag_close)+1
               txt = self.text[lft:rgt]
               txt=txt.strip()
               brk['txt']=txt             
               msg=f"{self.tag_open}"
               s1 = "{:<5}) {:.<60}  {}".format(row_num,txt,msg)
               self.log.log(s1)
               s1=BLK[0:rgt-lft-len(self.tag_close)-1]+self.tag_close
               self.log.log(s1)
               self.log.log("")
           else:
               x=brk["x"]
               lft = x-min(x, 5)
               rgt = x+len(self.tag_close)+5
               txt = self.text[lft:rgt]
               brk['txt']=txt             

    def log_deb(self):
        for n, brk in enumerate(self.brk_lst):
                err=brk['err']
                if err <100:
                    s=pp(brk)
                    self.log.log(s)

    def check_over(self):
        s=f"{self.path_src}"
        self.log.log(SEP2[0:len(s)])
        self.log.log(s)
        self.log.log(SEP2[0:len(s)])
        # sself.log.log(SEP2[0:len(s)])
        self.read_text()
        # csv= self.read_tag_csv()
        # rows= sorted(csv, key=lambda x: (len(x[1]), x[0]), reverse=True)
        try:
            over_tags=read_over_tags_sorted(self.path_csv)
        except Exception as e:
            self.logerr.log("ERROR teimcheckover.py read_over_tags()v")
            self.logerr.log(str(e))
            sys.exit(1)      
        for tag_data in over_tags:
            self.len_text=len(self.text)
            self.tag_open=tag_data[1]
            self.tag_close=tag_data[2]
            self.tag_type=tag_data[0]
            # s=f"{tag_data}"
            self.check_tag()
            self.brk_lst= sorted(self.brk_lst, key=lambda x: (int(x["x"])))
            self.find_err()
            self.log_err()
            # self.log_deb()
            self.text = self.text.replace(self.tag_open, '')
            self.text = self.text.replace(self.tag_close, '')

def do_main(path_src, path_csv, path_out):
    check=CheckOverflow(path_src, path_csv, path_out)
    check.check_over()

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit()
    parser.add_argument('-c',
                        dest = "teimcfg",
                        required = True,
                        metavar = "",
                        help = "-c <file csv dei tag overflow>")
    parser.add_argument('-i',
                        dest = "src",
                        required = True,
                        metavar = "",
                        help = "-i <file text>")
    parser.add_argument('-o',
                        dest = "out",
                        required = True,
                        metavar = "",
                        help = "-o <file output>")
    args=parser.parse_args()
    if args.src == args.out:
        print("Name File output errato")
        sys.exit(0)
    do_main(args.src, args.teimcfg, args.out)
