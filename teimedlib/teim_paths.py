#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#import pathlib as pth
import os

__date__ = "26-07-2021"
__version__ = "0.1.2"
__author__ = "Marta Materni"


def add_log2path(path):
    #path=os.path.abspath(path)
    dirname=os.path.dirname(path)
    basename = os.path.basename(path)
    path_log=os.path.join(dirname,'log',basename)
    return path_log
##############################################

# testo.txt => ./log/testo_teim.txt
def set_path_teim_out(path_text):
    path = path_text.replace('.txt', '_teim.txt')
    return add_log2path(path)

# testo.txt => t./log/esto_teim.log
def set_path_teim_log(path_text):
    path = path_text.replace('.txt', '_teim.log')
    return add_log2path(path)

# testo.txt => ./log/testo_teim.ERR.log
def set_path_teim_err(path_text):
    path = path_text.replace('.txt', '_teim.ERR.log')
    return add_log2path(path)

###################################

# test.txt => ./log/testo_teim.txt
def set_path_id_in(path_text):
    return set_path_teim_out(path_text)

# test.txt => ./log/testo_id.xml
def set_path_id_out(path_text):
    path = path_text.replace('.txt', '_id.xml')
    return add_log2path(path)

# test.txt => ./log/testo_id.log
def set_path_id_log(path_text):
    path = path_text.replace('.txt', '_id.log')
    return add_log2path(path)

# test.txt => ./log/testo_id.ERR.log
def set_path_id_err(path_text):
    path = path_text.replace('.txt', '_id.ERR.log')
    return add_log2path(path)

#################################

# test.txt => ./log/testo_checkover.log
def set_path_checkover_out(path_text):
    path = path_text.replace('.txt', '_checkover.log')
    return add_log2path(path)

# test.txt => ./log/testo_checkover.ERR.log
def set_path_checkover_err(path_text):
    path = path_text.replace('.txt', '_checkover.ERR.log')
    return add_log2path(path)

###################################

# test.txt => ./log/testo_checktxt.log
def set_path_checktxt_out(path_text):
    path = path_text.replace('.txt', '_checktxt.log')
    return add_log2path(path)

# test.txt => ./log/testo_checktxtr.ERR.log
def set_path_checktxt_err(path_text):
    path = path_text.replace('.txt', '_checktxt.ERR.log')
    return add_log2path(path)

###################################

# test.txt => testo_id.xml
def set_path_over_in(path_text):
    return set_path_id_out(path_text)

# test.txt => ./lg/testo_id_over.xml
def set_path_over_out(path_text):
    path = path_text.replace('.txt', '_id_over.xml')
    return add_log2path(path)

# test.txt => ./log/testo_id_over.log
def set_path_over_log(path_text):
    path = path_text.replace('.txt', '_id_over.log')
    return add_log2path(path)

# test.txt => ./log/testo_id_over.ERR.log
def set_path_over_err(path_text):
    path = path_text.replace('.txt', '_id_over.ERR.log')
    return add_log2path(path)

##################################

# test.txt => ./log/testo_id_over.xml
def set_path_note_in(path_text):
    return set_path_over_out(path_text)

# test.txt => ./log/testo_id_over_note.xml
def set_path_note_out(path_text):
    path = path_text.replace('.txt', '_id_over_note.xml')
    return add_log2path(path)

# test.txt => ./log/testo_id_over_note.log
# def set_path_note_log(path_text):
#     path = path_text.replace('.txt', '_id_over_note.log')
#     return add_log2path(path)

# test.txt => ./log/testo_id_over_note.ERR.log
def set_path_note_err(path_text):
    path = path_text.replace('.txt', '_id_over_note.ERR.log')
    return add_log2path(path)

##################################

#test.txt => ./log/testo_id_over_note.xml
def set_path_xml_in(path_text):
    return set_path_note_out(path_text)

# test.txt => testo.xml
def set_path_xml_out(path_text):
    path = path_text.replace('.txt', '.xml')
    return path

#test.txt => ./log/testo.xml.ERR.log
def set_path_xml_err(path_text):
    path = path_text.replace('.txt', '.xml.ERR.log')
    return add_log2path(path)

#####################################

#test.txt => ./log/testo_id_over_note.xml
def set_path_tei_in(path_text):
    return set_path_note_out(path_text)
    #return set_path_xml_out(path_text)

# test.txt => testo_tei.xml
def set_path_tei_out(path_text):
    path = path_text.replace('.txt', '_tei.xml')
    return path

#test.txt => ./log/testo_tei.xml.ERR.log
def set_path_tei_err(path_text):
    path = path_text.replace('.txt', '_tei.xml.ERR.log')
    return add_log2path(path)
