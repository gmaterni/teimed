#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from teimedlib.textentities import *
import os
ERR = ["trovata ) che bilancia",
       "non trovata ) che bilancia",
       "una ) precede la prima (",
       "( non esiste"]


def word_entities_log(rows_entities, path_out=None):
    def prn(msg):
        f.write(msg)
        f.write('\n')

    f = io.StringIO("")
    for row_ent in rows_entities:
        n = row_ent.num
        prn(f'\n(R)({n}) {row_ent.text}')
        for word in row_ent.words:
            i = word.num
            prn(f'(W)({i}) {word.text}')
            for e in word.entities:
                prn(f'liv :{e.liv}')
                prn(f'src:{e.src}')
                prn(f'name:{e.name} ')
                prn(f'src_args:{e.src_args} ')
                prn(f'err:{e.err}:  {ERR[e.err]}')
                prn(f'tag_tp:{e.tag_tp} ')
                prn(f'tag_name:{e.tag_name}')
                prn(f'tag_text:{e.tag_text}')
                prn(f'tag_nargs:{e.tag_nargs} ')
                if e.src == word.text:
                    prn(f' *** {e.src} ')

            for x in word.entities_ch2:
                e, t = x
                prn(f'ch2: {e} => {t}')

            for x in word.entities_ch1:
                e, t = x
                prn(f'ch1: {e} => {t}')

            for x in word.entities_punt:
                e, t = x
                prn(f'punt: {e} => {t}')
    f.seek(0)
    s = f.read()
    f.close()
    if not path_out is None:
        open(path_out, 'w').write(s)
    return s


def entities_log(rows_entities, path_out=None):
    def prn(msg):
        f.write(msg)
        f.write(os.linesep)

    f = io.StringIO("")
    for row_ent in rows_entities:
        prn(f'\nR:({row_ent.num})')
        for word in row_ent.words:
            prn(f"\nR,W:({row_ent.num},{word.num})")
            prn(f'{word.text}')
            for e in word.entities:
                prn(f'\nliv :{e.liv}')
                prn(f'src:{e.src}')
                prn(f'name:{e.name} ')
                prn(f'src_args:{e.src_args} ')
                prn(f'err:{e.err}:  {ERR[e.err]}')
                prn(f'tag_tp:{e.tag_tp} ')
                prn(f'tag_name:{e.tag_name}')
                prn(f'tag_text:{e.tag_text}')
                prn(f'tag_nargs:{e.tag_nargs} ')

            for x in word.entities_ch2:
                e, t = x
                prn(f'ch2: {e} => {t}')

            for x in word.entities_ch1:
                e, t = x
                prn(f'ch1: {e} => {t}')

            #     for x in word.entities_ch1_arg:
            #         e, t = x
            #         prn(f'ch1_arg: {e} => {t}')

            for x in word.entities_punt:
                e, t = x
                prn(f'punt: {e} => {t}')

    f.write(os.linesep)
    f.seek(0)
    s = f.read()
    f.close()
    if not path_out is None:
        open(path_out, 'w').write(s)
    return s
