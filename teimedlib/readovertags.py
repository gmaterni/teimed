#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

def read_over_tags(csv_path):
    """
    lettura tag per gestione overflow
    Args:
        csv_path ([type]):  
    TYPE|TAG_FROM|TAG_TO|SIGLA_FROM|SIGLA_TO
    directspeech|{|}|ODRD|CDRD
    Returns:
        [type]: rows ordinate ler len(TAG_FROM)
    """        
    try:
        with open(csv_path, "r") as f:
            txt = f.read()
        # txt=txt.replace(f'\{os.linesep}','')
        csv = txt.split(os.linesep)
        csv_rows = []
        for row in csv:
            row = row.strip()
            if row == "":
                continue
            row = row.replace(os.linesep, '')
            row = row.replace(' ', '')
            flds = row.split('|')
            x = flds[0]
            if x.lower() == 'type':
                continue
            csv_rows.append(flds)
        rows= sorted(csv_rows, key=lambda x: (len(x[1]), x[0]), reverse=True)
        return rows
    except Exception as e:
        s=str(e)
        raise Exception(s)
