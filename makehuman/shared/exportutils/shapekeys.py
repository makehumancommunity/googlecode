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

TODO
"""

import os
import math
import meshstat
import warpmodifier
import algos3d
import log
from getpath import getSysDataPath


#----------------------------------------------------------
#   Setup expressions
#----------------------------------------------------------

def loadExpressions(folder, prefix):
    expressions = []
    try:
        files = os.listdir(folder)
    except:
        log.debug('WARNING: Folder "%s" does not exist.' % folder)
        return(expressions)

    for file in files:
        (fname, ext) = os.path.splitext(file)
        if ext == ".target":
            if prefix:
                (before, sep, after) = fname.partition(prefix)
                if sep:
                    expressions.append(after)
            else:
                expressions.append(fname)
    return(expressions)

_expressionUnits = None

def getExpressionUnits():
    global _expressionUnits
    if _expressionUnits is None:
        _expressionUnits = loadExpressions(getSysDataPath("targets/expression/units/caucasian"), "")
    return _expressionUnits


def readShape(filename):
    try:
        fp = open(filename, "rU")
    except:
        log.error("*** Cannot open %s", filename)
        return None

    shape = {}
    for line in fp:
        words = line.split()
        n = int(words[0])
        if n < meshstat.numberOfVertices:
            shape[n] = (float(words[1]), float(words[2]), float(words[3]))
    fp.close()
    log.message("    %s copied", filename)
    return shape

#----------------------------------------------------------
#
#----------------------------------------------------------

def readExpressionUnits(human, t0, t1, progressCallback = None):
    shapeList = []
    t,dt = initTimes(getExpressionUnits(), 0.0, 1.0)

    referenceVariables = { 'gender': 'female',
                           'age':    'young' }

    for name in getExpressionUnits():
        if progressCallback:
            progressCallback(t, text="Reading expression %s" % name)

        shape = warpmodifier.compileWarpTarget('expression-units', name, human, "face", referenceVariables)

        shapeList.append((name, shape))
        t += dt
    return shapeList


def initTimes(flist, t0, t1):
    dt = t1-t0
    n = len(flist)
    if n > 0:
        dt /= n
    return t0,dt


def readExpressionMhm(folder):
    exprList = []
    for file in os.listdir(folder):
        (fname, ext) = os.path.splitext(file)
        if ext == ".mhm":
            path = os.path.join(folder, file)
            fp = open(path, "rU")
            units = []
            for line in fp:
                words = line.split()
                if len(words) < 3:
                    pass
                elif words[0] == "expression":
                    units.append(words[1:3])
            fp.close()
            exprList.append((fname,units))
    return exprList




