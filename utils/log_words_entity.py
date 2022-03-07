#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from teimedlib.textentities import TextEntities
from teimedlib.textentities_log import *
from teimedlib.ualog import Log

def do_main(path_src,path_tags):
    path_err=path_src.replace(".txt","_words.ERR.log")
    log_err=Log("w").open(path_err,1).log
    te = TextEntities(path_src, path_tags,log_err)
    lst = te.get_rows_entities()
    path_log=path_src.replace(".txt","_words.log")
    print(path_log)
    word_entities_log(lst,path_log)

if __name__ == "__main__":
    path_text = sys.argv[1]
    #path_tags=sys.argv[2]
    path_tags="teimcfg/teimtags.csv"
    do_main(path_text,path_tags)
