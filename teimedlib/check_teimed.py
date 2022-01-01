#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import re


def check_entitys(text):
    ptrn = r"(&{1})([\w-]+)([;]{0,1})"
    lst = []
    for m in re.finditer(ptrn, text):
        s = m.group()
        g2 = m.groups()[2]
        t = 0 if g2 == ';' else 1
        lst.append({'s': s, 't': t})
    return lst

def check_entity_brackets(text):
    ptrn = r"([;(])(\S+)(\)*)"
    lst = []
    for m in re.finditer(ptrn, text):
        s = m.group()
        nop = s.count('(')
        noc = s.count(')')
        if nop+noc == 0:
            continue
        s = s if s.find(';') < 0 else s[1:]
        t = 0 if nop == noc else 1
        e = {'s': s, 't': t}
        lst.append(e)
    return lst

# lista de pattern del tipo from to
def check_overflow(text, po, pc):
    lst = []
    pc = re.compile(pc)
    po = re.compile(po)
    so_last = ""
    c1_ = 0
    for mo in re.finditer(po, text):
        so = mo.group()
        o0 = mo.start()
        o1 = mo.end()
        js = {'so': so,
              'sc': '',
              's': '',
              't': 0}
        if o0 < c1_:
            l = len(lst)-1
            lst[l]['s'] = so_last
            lst[l]['t'] = 1
        so_last = so
        mc = re.search(pc, text[o1:])
        if mc is None:
            js['s'] = so
            js['t'] = 1
            lst.append(js)
            continue
        c0 = mc.start()
        c1 = mc.end()
        c1_ = o1+c0
        s = text[o0:o1+c1]
        js['s'] = s
        js['sc'] = mc.group()
        lst.append(js)
    return lst

OVER_KEY_TYPE_LIST = (
    ('g3', '{3%',0),
    ('g2', '{2%',0),
    ('g1', '{1%',0),
    ('g0', '{0%',0),

    ('gu', '{_' ,0),
    ('qu', '[_' ,1),
    
    ('g', '{'   ,0),
    ('q', '['   ,1)
)


def fill_tag_over_lst(tag_lst):
    
    def find_over_key_type(tag_op):
        k=None
        t=None
        for kpt in OVER_KEY_TYPE_LIST:
            if tag_op==kpt[1]:
                k=kpt[0]
                t=kpt[2]
                break
        return k,t        
    
    lst=[]
    for tag in tag_lst:
        key,func_type=find_over_key_type(tag[1])
        if key is None:
            continue
        po = tag[1]
        pc = tag[2]
        so=po
        sc=pc
        if po == "[":
            po = po.replace('[', r'\[[^_]')
            pc = pc.replace(']', r'[^_]\]')
        elif po == "[_":
            po = po.replace('[', r'\[')
            pc = pc.replace(']', r'\]')
        elif po == "{":
            po = po.replace('{', r'\{[^_]\w')
            pc = pc.replace('}', r'\w[^_]\}')
        name = tag[0]
        lst.append([func_type,name,so,sc,po,pc])
    return lst
