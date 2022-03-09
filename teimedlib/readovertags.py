#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

# ['damage_high', '{3%', '%3}', 'ODAMH', 'CDAMH'],
# ['damage_medium', '{2%', '%2}', 'ODAMM', 'CDAMM'],
# ['damage_low', '{1%', '%1}', 'ODAML', 'CDAML'],
# ['damage', '{0%', '%0}', 'ODAM', 'CDAM'],
# ['monologue', '{_', '_}', 'OMON', 'CMON'],
# ['directspeech', '{', '}', 'ODRD', 'CDRD'],
# ['agglutination_uncert', '[_', '_]', 'OAGLU', 'CAGLU'],
# ['agglutination', '[', ']', 'OAGLS', 'CAGLS'],

def read_over_tags(csv_path):
    """
    lettura tag per gestione overflow
    Args:
        csv_path ([type]):  
    TYPE|TAG_FROM|TAG_TO|SIGLA_FROM|SIGLA_TO
    directspeech|{|}|ODRD|CDRD
    Returns:
        [type]: list of list
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
        return csv_rows
    except Exception as e:
        s=str(e)
        raise Exception(s)

def read_tags_over_sorted(csv_path):
    """
    tags per la gestione di overflow da teimoverflow.csv
    ordinati per len decrescente
    """        
    csv_rows=read_over_tags(csv_path)
    rows= sorted(csv_rows, key=lambda x: (len(x[1]), x[0]), reverse=True)
    return rows
