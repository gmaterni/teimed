#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from pdb import set_trace

def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def class_dir(class_name):
    clazz=get_class(class_name)
    lst = dir(clazz)
    for x in lst:
        s = x.strip()
        if s[0:2] == '__':
            continue
        print(x)


if __name__ == "__main__":
    class_name = sys.argv[1]
    #class_name = "teimedlib.textentities.TextEntities"
    #class_name = "teimsetid.TeimSetId"
    class_dir(class_name)
