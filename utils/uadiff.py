#!/usr/bin/env python3
from difflib import *
import sys


def read_data(path):
    txt = open(path, "r").read()
    lst = txt.splitlines()
    return lst


def save_data(path, lst):
    data = "\n".join(lst)
    open(path, "w").write(data)


def diff(lst1, lst2):
    path = "diff0.txt"
    path1 = "diff1.txt"
    path2 = "diff2.txt"
    d = Differ()
    diff = d.compare(lst1, lst2)

    diff_lst = list(diff)
    save_data(path, diff_lst)

    diff_lst1 = [x for x in diff_lst if len(x.strip()) > 0 and x[0] != '?']
    save_data(path1, diff_lst1)

    diff_lst2 = [x for x in diff_lst1 if x[0] in ('-', '+', '^')]
    save_data(path2, diff_lst2)

    print('\n'.join(list(diff_lst2)))


l1 = sys.argv[1]
l2 = sys.argv[2]

lst1 = read_data(l1)
lst2 = read_data(l2)
diff(lst1, lst2)
