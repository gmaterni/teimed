#!/usr/bin/env python3
# coding: utf-8

import sys
import os


def splitlines(path_in, path_ou, rl):
    with open(path_in, "r") as f:
        text=f.read()
    text=text.replace(os.linesep," ")
    fou = open(path_ou, "w")
    n = 0
    r=list(text)
    lst=[]
    le=int(rl)
    for i, ch in enumerate(r):
        lst.append(ch)
        if i > 0 and i % le == 0:
            s = "".join(lst).strip()
            print(s)
            fou.write(s)
            fou.write(os.linesep)
            lst = []
    fou.close()


if __name__ == '__main__':
    args = sys.argv[1:]
    inp = args[0]
    ou = args[1]
    rowlen = args[2]
    splitlines(inp, ou, rowlen)
