#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Utility reading and writing JSON files. Optionally the file may be
gzipped for saving space.
"""

import json
import gzip

def loadJson(filepath):
    try:
        with gzip.open(filepath, 'rb') as fp:
            bytes = fp.read()
    except IOError:
        bytes = None

    if bytes:
        string = bytes.decode("utf-8")
        struct = json.loads(string)
    else:
        with open(filepath, "rU") as fp:
            struct = json.load(fp)

    return struct


def saveJson(struct, filepath, binary=False):
    if binary:
        bytes = json.dumps(struct)
        with gzip.open(realpath, 'wb') as fp:
            fp.write(bytes)
    else:
        with open(filepath, "w", encoding="utf-8") as fp:
            json.dump(struct, fp,
                sort_keys=False,
                indent=4,
                separators=(',', ':'))
