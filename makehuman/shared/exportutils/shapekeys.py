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
import targets


#----------------------------------------------------------
#   Setup expressions
#----------------------------------------------------------

def _loadExpressions():
    expressions = []
    exprTargets = targets.getTargets().findTargets('expression-units')
    for eComponent in exprTargets:
        name = eComponent.key
        # Remove 'expression-units' components from group name
        name = name[2:]
        expressions.append('-'.join(name))
    return expressions

_expressionUnits = None

def getExpressionUnits():
    global _expressionUnits
    if _expressionUnits is None:
        _expressionUnits = _loadExpressions()
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

        target = warpmodifier.compileWarpTarget('expression-units', name, human, "face", referenceVariables)
        shape = {}
        for i in xrange(len(target.verts)):
            vIdx = target.verts[i]
            shape[vIdx] = target.data[i]

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




