#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pdb import set_trace
import os
import argparse
import sys
import re
import shutil
import teimedlib.teim_paths as tpth
from teimedlib.ualog import Log
from teimedlib.xml_const import *

__date__ = "09-09-2021"
__version__ = "1.1.0"
__author__ = "Marta Materni"


class TeimNote(object):
    """
    legge il testo delle note dal fille note.csv
    modifica il file xml
    aggiunge le note in fondo e setta xml:id di ptrn

    """    
    NOTE_TYPE = "note_type"
    NOTE_ID = "note_id"
    NOTE_TEXT = "note_text"
    
    def __init__(self, path_text='', path_note=''):
        # testo.txt => testo_id_over.xml
        self.path_in =tpth.set_path_note_in(path_text) 
        
        # testo.txt => testo_id_over_note.xml
        self.path_out = tpth.set_path_note_out(path_text)
        #teimnote.csv
        self.note_path = path_note
        
        # testo.txt => testo_id_over_note.ERR.log
        path_err=tpth.set_path_note_err(path_text)
        self.log_err = Log("w").open(path_err, 1).log
        
        self.delimiter = '|'

    def read_note(self):
        note_list = []
        item = {}
        txt = ""
        with open(self.note_path, "rt") as f:
            for line in f:
                if line.strip() == '':
                    continue
                if line.find(self.delimiter) > -1:
                    item[self.NOTE_TEXT] = txt
                    note_list.append(item)
                    item = {}
                    cols = line.split(self.delimiter)
                    item[self.NOTE_TYPE] = cols[0].strip()
                    item[self.NOTE_ID] = cols[1].strip()
                    txt = cols[2].strip()
                    continue
                txt = txt + os.linesep + line.strip()
        item[self.NOTE_TEXT] = txt
        note_list.append(item)
        del note_list[0]
        return note_list

    def add_to_xml(self):
        if not os.path.exists(self.note_path):
            # copia il file in nel file out se NON esistono note
            shutil.copyfile(self.path_in, self.path_out)
            self.log_err(f"WARNING {self.note_path} Not Found.")
            return
        try:
            note_list = self.read_note()
            ls = []
            for note in note_list:
                note_id = note[self.NOTE_ID]
                note_text = note[self.NOTE_TEXT]
                text = note_text.strip().replace(os.linesep, " ")
                s = f'<teimed_note xml:id="{note_id}">{text}</teimed_note>'
                ls.append(s)
            note = os.linesep.join(ls)
            #
            with open(self.path_in, "rt") as f:
                xml = f.read()
            xml_sp = re.split(BODY_BOTTOM_PATTERN, xml)
            with open(self.path_out, 'w') as f:
                f.write(xml_sp[0])
                f.write(BODY_BOTTOM+os.linesep)
                f.write(BACK_TOP+os.linesep)
                f.write(NOTE_TOP+os.linesep)
                f.write(note)
                f.write(os.linesep+NOTE_BOTTOM+os.linesep)
                f.write(BACK_BOTTOM+os.linesep)
                f.write(xml_sp[1])
            os.chmod(self.path_out, 0o777)
        except Exception as e:
            msg=f'ERROR teimnote.py add_to_xml()\n{e}'
            self.log_err(msg)
            sys.exit(msg)

def do_main(path_text, path_note):
    teimnote = TeimNote(path_text, path_note)
    teimnote.add_to_xml()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit()
    parser.add_argument('-n',
                        dest="note",
                        required=True,
                        metavar="",
                        help="-n <file note> ")
    parser.add_argument('-i',
                        dest="src",
                        required=True,
                        metavar="",
                        help="-i <file text>")
    args = parser.parse_args()
    do_main(args.src, args.note)
