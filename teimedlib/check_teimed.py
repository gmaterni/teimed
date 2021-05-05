#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os


def clean_rows(text):
    BL = " "
    try:
        rows = text.split(os.linesep)
        lst = []
        for row in rows:
            row = row.replace('\t', BL, -1)
            # elimina i commenti
            pc = row.find('<!')
            if pc > -1:
                row = row[0:pc - 1].strip()
            row = row.replace('\ufeff', '', -1)
            row = re.sub(r"[ ]{2,}", BL, row)
            if row.strip() != '':
                lst.append(row)
        return lst
    except Exception as e:
        raise(Exception(f"Error clen_rows() {os.linesep}{e}"))


def clean_text(text):
    BL = " "
    try:
        rows = clean_rows(text)
        text = os.linesep.join(rows)
        text = text.replace(os.linesep, BL)
        # rimuove spazi multipli
        text = re.sub(r"[ ]{2,}", BL, text)
        return text
    except Exception as e:
        raise(Exception(f"Error clen_text() {os.linesep}{e}"))


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

# lista de patter del tipo from to


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


tag_list = [
    ['damage_medium', '{2%', '%2}', 'ODAMM', 'CDAMM'],
    ['damage_low', '{1%', '%1}', 'ODAML', 'CDAML'],
    ['damage_high', '{3%', '%3}', 'ODAMH', 'CDAMH'],
    ['damage', '{0%', '%0}', 'ODAM', 'CDAM'],
    ['monologue', '{_', '_}', 'OMON', 'CMON'],
    ['agglutination_uncert', '[_', '_]', 'OAGLU', 'CAGLU'],
    ['directspeech', '{', '}', 'ODRD', 'CDRD'],
    ['agglutination', '[', ']', 'OAGLS', 'CAGLS'],
]

def build_pattern_over(tag_lst=tag_list):
    js = {}
    for tag in tag_lst:
        po = tag[1]
        pc = tag[2]
        name = tag[0]
        j = {
            'o': po,
            'c': pc
        }
        if po == "[":
            # agglutination [ ]
            po = po.replace('[', r'\[[^_]')
            pc = pc.replace(']', r'[^_]\]')
        elif po == "[_":
            # agglutination_uncert [_ _]
            po = po.replace('[', r'\[')
            pc = pc.replace(']', r'\]')
        elif po == "{":
            # directspeech {}
            po = po.replace('{', r'\{[^_]\w')
            pc = pc.replace('}', r'\w[^_]\}')
        j['po'] = po
        j['pc'] = pc
        js[name] = j
    return js
