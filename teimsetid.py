#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import sys
from teimed.ualog import Log
from teimed.xml_const import *
from teimed.readovertags import read_over_tags
import re
import stat
from pdb import set_trace
# import pprint

__date__ = "11-04-2021"
__version__ = "0.9.7"
__author__ = "Marta Materni"

"""
def pp_data(data):
    if data is None:
        return ""
    retrn pprint.pformat(data, indent=0, width=80)
"""

SP = " "
SPW = "|"    # carattere temp di SP  dentro tag
CUND = "_"   # carattere _ UNDERLINE
CUNDT = "@@" # carattere temporaneo di CU per parole composte
CT1 = "$$"   # carattere temporaneo
CT2 = "§§ "  # carattere temporaneo
CNT = "$"    # carattere temp per note

# segmentazione
AP = "'"   # <w ana="#elis">$</w>
SL = "\\"  # <w ana="#encl">$</w>
CR = "°"   # <w ana="#degl">$</w>
# tags
OPB = "<pb"
OCB = "<cb"
OLG = "<lg"
OL = "<l"
OW = "<w"
OPC = "<pc"
OPTR = "<ptr"

PERSNAME="<persName"
GEOGNAME="<geogName"
PLACENAME="<placeName"
CHOICE="<choice"
TAGS_TEI=[PERSNAME,GEOGNAME,PLACENAME,CHOICE]

class AddId(object):
    def __init__(self, path_src, path_out, sigla_scrpt, ids_start):
        self.path_src = path_src
        self.path_out = path_out

        self.logerr = Log('w')
        path_err = path_out.replace(".xml", ".ERR.log")
        self.logerr.open(path_err, 1)

        self.logdeb = Log('w')
        path_deb = path_out.replace(".xml", ".log")
        self.logdeb.open(path_deb, 0)

        self.sigla = sigla_scrpt
        self.pb_id = 1
        self.cb_id = 1
        self.lg_id = 1
        self.l_id = 1
        self.ptr_id = 1
        # self.pc_num = 1
        self.line_num = 1
        self.set_ids_start(ids_start)
        self.LINE_NUM = 0
        self.NLINE = 0
        self.DEBUG = False
        # self.over_tags=[]

    def set_ids_start(self, ids_start):
        if ids_start.strip() == "":
            return
        tgs = ids_start.split(",")
        for tg in tgs:
            kv = tg.split(":")
            k = kv[0]
            v = kv[1]
            if k == "pb":
                self.pb_id = int(v)
            elif k == "cb":
                self.cb_id = int(v)
            elif k == "lg":
                self.lg_id = int(v)
            elif k == "ptr":
                self.ptr_id = int(v)
            elif k == "l":
                self.l_id = int(v)
                self.line_num = 1

    def preserve_note(self, line):
        p0 = line.find("<note")
        p1 = line.find("</note>")
        s0 = line[0:p0]
        s1 = line[p0:p1]
        s2 = line[p1:]
        s1 = s1.replace(" ", CNT, -1)
        t = s0 + s1 + s2
        t = t.replace("<note", " <note", -1).replace("</note>", "</note> ", -1)
        return t

    def is_container(self, line):
        """tag di separazione:
        <div
        <pb
        <cb
        <lg
        """        
        s = line.strip()
        n1 = s.count("<")
        n2 = s.count(">")
        if n1!=1 or n2!=1:
            return False
        ok = (s[0] == "<" and s[-1] == ">")
        return ok

    def set_container_id(self, line):
        if line.find(OPB) > -1:
            id = '<pb xml:id="%spb%s" ' % (self.sigla, self.pb_id)
            line = line.replace("<pb", id)
            self.pb_id += 1
            return line
        if line.find(OCB) > -1:
            id = '<cb xml:id="%scb%s" ' % (self.sigla, self.cb_id)
            line = line.replace("<cb", id)
            self.cb_id += 1
            return line
        if line.find(OLG) > -1:
            id = '<lg xml:id="%slg%s" ' % (self.sigla, self.lg_id)
            line = line.replace("<lg", id)
            self.lg_id += 1
            return line
        return line

    def set_line_id(self, line):
        s = '<l n="%s" xml:id="%sl%s">%s</l> %s' % (
            self.line_num,
            self.sigla,
            self.l_id,
            line,
            os.linesep,
        )
        self.l_id += 1
        self.line_num += 1
        return s

    def set_words_id(self, line):
        wn = line.count(OW)
        if wn == 0:
            return line
        for i in range(0, wn):
            w_id = i + 1
            sid = '%s xml:id="%sl%sw%s" ' % (
                CT1, self.sigla, self.l_id, w_id)
            line = line.replace(OW, sid, 1)
        line = line.replace(CT1, OW, -1)
        return line

    def set_pcs_id(self, line):
        pn = line.count(OPC)
        if pn == 0:
            return line
        for i in range(0, pn):
            pc_id = i + 1
            sid = '%s xml:id="%sl%spc%s" ' % (
                CT1, 
                self.sigla, 
                self.l_id, 
                pc_id)
            line = line.replace(OPC, sid, 1)
        line = line.replace(CT1, OPC, -1)
        return line
    
    def set_tag_tei_id(self, line,tag):
        nt = line.count(tag)
        if nt == 0:
            return line
        for i in range(0, nt):
            tag_id = i + 1
            sid = '%s xml:id="%sl%s%s%s" ' % (
                CT1, 
                self.sigla, 
                self.l_id,
                tag.replace('<',''), 
                tag_id)
            line = line.replace(tag, sid, 1)
        line = line.replace(CT1, tag, -1)
        return line

    def set_ptr_id(self, line):
        ptr = line.count(OPTR)
        if ptr == 0:
            return line
        for i in range(0, ptr):
            sid = '%s xml:id="%sptr%s" ' % (CT2, self.sigla, self.ptr_id)
            line = line.replace(OPTR, sid, 1)
            self.ptr_id += 1
        line = line.replace(CT2, OPTR, -1)
        return line

    # <w>text<c>n</c><sp><c>x</c></sp>text<c>a</c></w>
    # elenca gli item dei diversi lvelli per la stampa nel log
    def line_text_check(self, line, liv):
        le = len(line) - 1
        txtliv = -1
        tg = False
        tcop = False
        ls = []
        txtls = []
        for i, c in enumerate(line):
            cn = line[i + 1] if i < le else " "
            if c == "<":
                tg = True
                if cn == "/":
                    tcop = False
                    txt = "".join(ls)
                    txtls.append(txt)
                    ls = []
                else:
                    tcop = True
                    ls = []
            if tg is False and txtliv == liv:
                ls.append(c)
            if c == ">":
                tg = False
                if tcop:
                    txtliv += 1
                else:
                    txtliv -= 1
        return txtls

    def line_text_check_log(self, line):
        for liv in range(1, 8):
            lst = self.line_text_check(line, liv)
            if len("".join(lst)) > 0:
                self.logdeb.log("%s) %s" % (liv, lst))

    def set_w_type(self, w):
        # print("w " + w)
        ls = w.split('<w')
        ws = []
        ws.append(ls[0])
        for x in ls[1:]:
            s = '<w' + x
            # SL "\"
            if s.find(SL) > -1:
                s = s.replace(SL, "", -1)
                s = s.replace("<w", '<w ana="#encl" ')
            # AP "'" apice
            elif s.find(AP) > -1:
                s = s.replace(AP, "", -1)
                s = s.replace("<w", '<w ana="#elis" ')
            # CR "°"
            elif s.find(CR) > -1:
                s = s.replace(CR, "", -1)
                s = s.replace("<w", '<w ana="#degl" ')
            ws.append(s)
            w = ''.join(ws)
        return w

    def add_line_word(self, line):
        if line.find("<note") > -1:
            line = self.preserve_note(line)
        # aggiunge spazio a sinistra per isolare i tag della punteggiatura
        line = line.replace("<pc", " <pc", -1)
        line = line.replace("<ptr", " <ptr", -1)
        # aggiunge spazio a destra
        line = line.replace("</pc>", "</pc> ", -1)
        line = line.replace("</ptr>", "</ptr> ", -1)
        # stacca parentesi a quando fuori da w
        """
        for tag in self.over_tags:
            op=tag[1]
            cl=tag[2]
            line=line.replace(op,f" {op} ")
            line=line.replace(cl,f" {cl} ")
        """
        line = line.replace(">_}", "> _} ", -1)
        line = line.replace(">}", "> } ", -1)
        line = line.replace(">_]", "> _] ", -1)
        line = line.replace(">]", "> ] ", -1)
        # elimina spazi multipli
        line = re.sub(r"\s{2,}", SP, line)
        # attacca laparentesi di apetura alla parola
        line = line.replace("{_ ", "{_", -1)
        line = line.replace("{ ", "{", -1)
        line = line.replace("[_ ", "[_", -1)
        line = line.replace("[ ", "[", -1)
        
        # elimina spazi multipli
        line = re.sub(r"\s{2,}", SP, line)
        lst = []
        # preparazione caratteri underline per split SP
        line = line.replace('{_', '{{').replace('_}', '}}')
        line = line.replace('[_', '[[').replace('_]', ']]')
        is_in_tag = False
        for c in line:
            if c == "<":
                is_in_tag = True
            if c == ">":
                is_in_tag = False
                lst.append(c)
                continue
            # " " => "|"
            if is_in_tag:
                c = SPW if c == SP else c
            else:
                # trasfroma _ in $$ fuori i tag 
                c = CUNDT if (c == CUND) else c
            lst.append(c)
        s = "".join(lst).strip()
        s = s.replace('{{', '{_').replace('}}', '_}')
        s = s.replace('[[', '[_').replace(']]', '_]')
        words = []
        ws = s.split(SP)
        for i, w in enumerate(ws):
            # "|" => " "
            s = w.strip().replace(SPW, SP, -1)
            # segop, s = self.add_seg_open(s)
            segop = ""
            # segcl, s = self.add_seg_close(s)
            segcl = ""
            #  "@@"" =>" "
            #  paroloe composte es.  for_se => for se
            s = s.replace(CUNDT, SP, -1)
            if s.find("<pc") > -1:
                words.append("%s%s%s" % (segop, s, segcl))
            elif s.find("<ptr") > -1:
                words.append("%s%s%s" % (segop, s, segcl))
            # espansioni che iniziano con <w
            elif s.find("<w") == 0:
                s = self.set_w_type(s)
                words.append("%s%s%s" % (segop, s, segcl))
            elif s.find("<w") > 0:
                s = self.set_w_type(s)
                words.append("%s%s%s" % (segop, s, segcl))
            # gestione note
            elif s.find("<note") > -1:
                s = s.replace(CNT, " ", -1)
                words.append(s)
            # SL "\"
            elif s.find(SL) > -1:
                s = s.replace(SL, "", -1)
                words.append('%s<w ana="#encl">%s</w>%s' % (segop, s, segcl))
            # AP "'" apice
            elif s.find(AP) > -1:
                s = s.replace(AP, "", -1)
                words.append('%s<w ana="#elis">%s</w>%s' % (segop, s, segcl))
            # CR "°"
            elif s.find(CR) > -1:
                s = s.replace(CR, "", -1)
                words.append('%s<w ana="#degl">%s</w>%s' % (segop, s, segcl))
            elif s.strip() == "":
                words.append("%s" % (segcl))
            else:
                words.append("%s<w>%s</w>%s" % (segop, s, segcl))
        line = "".join(words)
        line = self.set_words_id(line)
        line = self.set_pcs_id(line)
        for tag in TAGS_TEI:
            line=self.set_tag_tei_id(line,tag)
        line = self.set_ptr_id(line)
        line = self.set_line_id(line)
        # line = line.replace("  ", SP, -1)
        line = re.sub(r"\s{2,}", SP, line)
        line = line.replace("> <", "><", -1)
        self.logdeb.log("")
        self.logdeb.log(line.strip())
        self.line_text_check_log(line)
        for w in words:
            self.logdeb.log(w.strip())
            self.line_text_check_log(w)
        """
        if line.find("kl18w1") < -1:
            pass
            # print("***** %s" % (self.NLINE))
        """
        self.NLINE += 1
        return line

    def addtags(self):
        # path_over_csv="cfg/overflow.csv"
        # self.over_tags=read_over_tags(path_over_csv)
        fw = open(self.path_out, "w+")
        fw.write(TEI_TOP)
        fw.write(BODY_TOP)
        fw.write(os.linesep)
        self.LINE_NUM = 0
        try:
            with open(self.path_src, "r") as f:
                for line in f:
                    self.LINE_NUM += 1
                    line = line.replace("\ufeff", "")
                    if line.strip() == "":
                        continue
                    if self.is_container(line):
                        line = self.set_container_id(line)
                        fw.write(line)
                        continue
                    s = self.add_line_word(line)
                    fw.write(s)
            fw.write(BODY_BOTTOM)
            fw.write(TEI_BOTTOM)
            fw.close()
            os.chmod(self.path_out, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)
        except Exception as e:
            self.logerr.log("ERROR in teimsetid ")
            self.logerr.log(str(e))
            sys.exit(1)


def do_main(path_src, path_out, sigla_scrp, ids_start=""):
    alwp = AddId(path_src, path_out, sigla_scrp, ids_start)
    alwp.addtags()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit()
    try:
        parser.add_argument(
            "-i",
            dest="src",
            required=True,
            metavar="",
            help="-i <file input>"
        )
        parser.add_argument(
            "-o",
            dest="out",
            required=True,
            metavar="",
            help="-o <file output>"
        )
        parser.add_argument(
            "-s",
            dest="sms",
            required=True,
            metavar="",
            help="-s <sigla mano scritto> (prefisso id)",
        )
        parser.add_argument(
            "-n",
            dest="ids",
            required=False,
            default="",
            metavar="",
            help="-n <'pb:1,cb:1,lg:1,l:1,ptr:1'>  (start id elementi)",
        )
        args = parser.parse_args()
    except Exception as e:
        print("ERROR args in teimsetid ")
        print(str(e))
        sys.exit(1)
    do_main(args.src, args.out, args.sms, args.ids)
