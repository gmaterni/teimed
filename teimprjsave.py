#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import stat
import shutil
import datetime

def chmod(path):
    os.chmod(path, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)

def save_text():
    """
    File di utility 
    Utilizzato da teimedit.py e teimxnlfh.py per
    salvare in una di back i sorgetnti dei file testo
    """    
    ymd = str(datetime.datetime.today().strftime('%Y_%m_%d_%H_%M_%S'))
    #ymd = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
    #ymd = str(datetime.datetime.today().strftime('%Y%m%d_%H_%M'))
    ymd_txt=f"_{ymd}.txt"
    pwd=os.getcwd()
    back=f"back"
    if not os.path.isdir(back):
        os.mkdir(back)
        chmod(back)
    d=pwd
    for f in os.listdir(d):
        path_witnes = os.path.join(d, f)
        if os.path.isdir(path_witnes):
            witness=os.path.basename(path_witnes)
            if witness.find('prj')> -1:
                continue
            if witness.find('back')> -1:
                continue
            #print(basename)
            for text in os.listdir(path_witnes):
                if os.path.isdir(text):
                    continue
                # text=os.path.basename(text)  
                path_src=os.path.join(path_witnes,text)
                src_name=os.path.basename(path_src)
                if src_name.find(".txt")<0:
                    continue
                pat_trg=os.path.join(pwd,back,witness)
                if not os.path.isdir(pat_trg):
                    os.mkdir(pat_trg)
                    chmod(pat_trg)
                path_trg=os.path.join(pwd,back,witness,text)
                path_trg=path_trg.replace(".txt",ymd_txt)
                print(path_src)
                print(path_trg)
                print("")
                shutil.copyfile(path_src,path_trg)
                chmod(path_trg)


if __name__ == "__main__":
    save_text()