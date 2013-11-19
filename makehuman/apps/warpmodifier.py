#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

__docformat__ = 'restructuredtext'

import numpy as np
from operator import mul
from getpath import getPath, getSysDataPath, canonicalPath, localPath
import os

import algos3d
import meshstat
import humanmodifier
import targets
import log
from core import G


#----------------------------------------------------------
#   class WarpTarget
#----------------------------------------------------------

_warpTargetCache = {}
_refTargetCache = {}


class WarpTarget(algos3d.Target):

    def __init__(self, name, shape, modifier, human):
        self.name = name
        self.morphFactor = -1

        data = list(shape.items())
        data.sort()
        raw = np.asarray(data, dtype=algos3d.Target.dtype)
        self.verts = raw['index']

        self.human = human
        self.modifier = modifier

        self.data = raw['vector']

        self.faces = self.human.meshData.getFacesForVertices(self.verts)

    def apply(self, obj, morphFactor, faceGroupToUpdateName=None, update=1, calcNorm=1, scale=[1.0,1.0,1.0]):
        print 'Apply()ing warp target %s at %s' % (self.name, morphFactor)
        super(WarpTarget, self).apply(obj, morphFactor, faceGroupToUpdateName, update, calcNorm, scale)

    def __repr__(self):
        return ( "<WarpTarget %s>" % (self.name) )


def saveWarpedTarget(shape, path):
    slist = list(shape.items())
    slist.sort()
    fp = open(path, "w")
    for (n, dr) in slist:
        fp.write("%d %.4f %.4f %.4f\n" % (n, dr[0], dr[1], dr[2]))
    fp.close()

#----------------------------------------------------------
#   class WarpModifier
#----------------------------------------------------------

class WarpModifier (humanmodifier.UniversalModifier):

    def __init__(self, groupName, targetName, bodypart, referenceVariables):
        super(WarpModifier, self).__init__(groupName, targetName)

        self.eventType = 'warp'
        self.bodypart = bodypart
        self.slider = None
        self.referenceVariables = referenceVariables

        self.nonfixedDependencies = list(self.macroDependencies)
        self.macroDependencies.extend(self.referenceVariables.keys())

        self.refTargetVerts = {}

    def setHuman(self, human):
        super(WarpModifier, self).setHuman(human)
        self.setupReferences()

    def setupReferences(self):
        self.referenceGroups = []

        # Gather all dependent targets
        groups = self.human.getModifierDependencies(self)
        targets = []
        for g in groups:
            m = self.human.getModifiersByGroup(g)[0]
            targets.extend(m.targets)
        factors = self.getFixedFactors().values()

        # Gather reference targets
        self.referenceTargets = []
        for tpath, tfactors in targets:
            # Reference targets are targets whose macro variables match the fixed variables for this warpmodifier
            # When all is correct, only the variables in self.nonfixedDependencies should still be free in this set of targets.
            if all([bool(f in tfactors) for f in factors]):
                self.referenceTargets.append( (tpath, tfactors) )

        self.refTargetPaths = {}
        self.refCharPaths = {}

    def getFixedFactors(self):
        """
        Get the macro variables for which this warpmodifier has no explicitly
        defined varieties of source warp targets. Instead those are the variables
        fixed to a certain value on which the source warp targets were modeled.
        These are the variables over which the actual warping will happen.

        Returns a dict of (var category, var name) tuples.
        """
        return self.referenceVariables

    def getDependentFactors(self, factors):
        """
        Get the macro variables for which this warpmodifier has varieties of
        source warp target files.

        Factors should either be a dict of (var category, var name) tuples, or
        should be a list with variable names.

        Returns either a dict of (var category, var name) tuples, when input was
        a dict, or a list.
        """
        if isinstance(factors, list):
            # Factors is a list of variable names
            return [f for f in factors if targets._value_cat.get(f, 'unknown') not in self.getFixedFactors()]
        else:
            # Factors is a dict of (macro variable category, variable name paris)
            return dict([(v,f) for v,f in factors.items() if v not in self.getFixedFactors()])

    # TODO add extended debug printing for warpmodifiers

    def setValue(self, value, skipDependencies = False):
        self.compileTargetIfNecessary()
        value = self.clampValue(value)

        self.human.setDetail(canonicalPath(self.fullName), value)

        #super(WarpModifier, self).setValue(value, skipDependencies)


    def updateValue(self, value, updateNormals=1, skipUpdate=False):
        return  # TODO allow updating while dragging slider

        self.compileTargetIfNecessary()
        #super(WarpModifier, self).updateValue(value, updateNormals, skipUpdate)


    def clampValue(self, value):
        return max(0.0, min(1.0, value))


    def compileTargetIfNecessary(self):
        # TODO find out when compile is needed
        #if alreadyCompiled:
        #    return

        shape = self.compileWarpTarget()
        targetName = self.groupName + '-' + self.targetName
        target = WarpTarget(targetName, shape, self, self.human)
        algos3d._targetBuffer[canonicalPath(self.fullName)] = target    # TODO remove direct use of the target buffer?
        self.human.hasWarpTargets = True

        log.debug("DONE %s" % target)
        #self.human.traceStack()


    def compileWarpTarget(self):
        log.message("Compile %s", self)
        srcTargetCoord, srcPoints, trgPoints = self.getReferences()
        if srcTargetCoord:
            #shape = srcTargetCoord
            shape = self.scaleTarget(srcTargetCoord, srcPoints, trgPoints)
        else:
            shape = {}
        return shape


    def scaleTarget(self, morph, srcPoints, trgPoints):
        scale = np.array((1.0,1.0,1.0))
        for n in range(3):
            tvec = trgPoints[2*n] - trgPoints[2*n+1]
            svec = srcPoints[2*n] - srcPoints[2*n+1]
            scale[n] = abs(tvec[n]/svec[n])
        log.debug("Scale %s" % scale)
        smorph = {}
        for vn,dr in morph.items():
            smorph[vn] = scale*dr
        return smorph


    def traceReference(self):
        log.debug("self.refCharPaths:")
        for key,value in self.refCharPaths.items():
            log.debug("  %s: %s" % (key, value))

    # Reference keypoints
    BodySizes = {
        "face" : [
            (5399, 11998, 1.4800),
            (791, 881, 2.3298),
            (962, 5320, 1.9221),
        ],
        "body" : [
            (13868, 14308, 9.6806),
            (881, 13137, 16.6551),
            (10854, 10981, 2.4356),
        ],
    }

    def getKeypoints(self):
        """
        Get landmark points used for warping
        """
        keypoints = []
        for n in range(3):
            keypoints += self.BodySizes[self.bodypart][n][0:2]
        return keypoints

    def getReferences(self):
        """
        Building source and target characters from scratch.
        The source character is the sum of reference characters.
        The target character is the sum of all non-warp targets.
        Cannot use human.getSeedMesh() which returns sum of all targets.
        """
        srcCharCoord = self.human.meshData.orig_coord.copy()
        trgCharCoord = srcCharCoord.copy()
        srcTargetCoord = {}

        keypoints = self.getKeypoints()
        trgPoints = np.zeros(6, float)
        srcPoints = np.zeros(6, float)


        # Traverse targets on stack
        for charpath,value in self.human.targetsDetailStack.items():
            if 'expression' in charpath:
                # TODO remove this stupid hack
                continue

            # The original target
            try:
                trgChar = algos3d.getTarget(self.human.meshData, charpath)
            except KeyError:
                continue    # Warp target? - ignore
            if isinstance(trgChar, WarpTarget):
                continue

            # TODO This is very wasteful, because we only need trgCharCoord and
            # srcCharCoord at the six keypoints

            srcVerts = np.s_[...]
            dstVerts = trgChar.verts[srcVerts]
            trgCharCoord[dstVerts] += value * trgChar.data[srcVerts]    # TODO replace with getting whole stack
        del charpath
        del value


        # The reference target (from reference variables)
        factors = self.getFactors(1.0)  # Calculate the fully applied warp target (weight = 1.0)
        factors = self.toReferenceFactors(factors)

        refTargets = self.referenceTargets
        tWeights = humanmodifier.getTargetWeights(refTargets, factors, ignoreNotfound = True)
        for tpath, tweight in tWeights.items():
            srcChar = algos3d.getTarget(self.human.meshData, tpath)
            dstVerts = srcChar.verts[srcVerts]
            srcCharCoord[dstVerts] += tweight * srcChar.data[srcVerts]


        # The warp target
        warpTargets = self.targets
        tWeights = humanmodifier.getTargetWeights(warpTargets, factors, ignoreNotfound = True)
        for tpath, tweight in tWeights.items():
            srcTrg = readTargetCoords(tpath)
            addVerts(srcTargetCoord, tweight, srcTrg)

        # Aggregate the keypoints differences
        trgPoints = trgCharCoord[keypoints]
        srcPoints = srcCharCoord[keypoints]
        return srcTargetCoord, srcPoints, trgPoints

    def toReferenceFactors(self, factors):
        vars_per_cat = dict()
        for (varName, varValue) in factors.items():
            varCateg = targets._value_cat.get(varName, 'unknown')
            if varCateg not in vars_per_cat:
                vars_per_cat[varCateg] = []
            vars_per_cat[varCateg].append(varName)

        result = dict()
        for (varCateg, varList) in vars_per_cat.items():
            if varCateg in self.getFixedFactors():
                # Replace fixed variables to reference target
                value = sum([factors[v] for v in varList])
                result[self.getFixedFactors()[varCateg]] = value
            else:
                for v in varList:
                    result[v] = factors[v]
        return result

def _factorsDict(factors):
    return dict([(targets._value_cat.get(f, 'unknown'), f) for f in factors])


def printDebugCoord(string, coord, obj=None, offset=None):
    return

    log.debug(string)
    for vn in [5171, 11833]:
        try:
            log.debug("  %d: %s" % (vn, coord[vn]))
        except KeyError:
            pass

    if offset:
        coord = coord.copy()
        for n,dx in offset.items():
            coord[n] += dx

    if obj:
        folder = getPath('debug')
        if not os.path.exists(folder):
            os.makedirs(folder)

        unit = np.array((1,1,1,1))
        filepath = os.path.join(folder, "%s.obj" % string)
        fp = open(filepath, "w")
        fp.write("".join(["v %f %f %f\n" % tuple(co) for co in coord]))
        fp.write("".join(["f %d %d %d %d\n" % tuple(fv+unit) for fv in obj.fvert]))
        fp.close()


#----------------------------------------------------------
#   Reset warp buffer
#----------------------------------------------------------

def resetWarpBuffer():
    human = G.app.selectedHuman
    if human.hasWarpTargets:
        log.debug("WARP RESET")
        for path,target in algos3d._targetBuffer.items():
            if isinstance(target, WarpTarget):
                log.debug("  DEL %s" % path)
                human.setDetail(localPath(path), 0)
                del algos3d._targetBuffer[path]
        human.applyAllTargets()
        human.hasWarpTargets = False

#----------------------------------------------------------
#   Call from exporter
#----------------------------------------------------------

def compileWarpTarget(groupName, targetName, human, bodypart, referenceVariables):
    mod = WarpModifier(groupName, targetName, bodypart, referenceVariables)
    mod.setHuman(human)
    return mod.compileWarpTarget(human)

#----------------------------------------------------------
#   Add verts. 
# TODO Replace with something faster using numpy.
#----------------------------------------------------------

def addVerts(targetVerts, value, verts):
    for n,v in verts.items():
        dr = value*v
        try:
            targetVerts[n] += dr
        except KeyError:
            targetVerts[n] = dr

#----------------------------------------------------------
#   Read target
#----------------------------------------------------------

def readTargetCoords(filepath):
    global _refTargetCache

    # Ref targets are cached, but never appear directly in the target buffer
    try:
        return _refTargetCache[filepath]
    except KeyError:
        pass

    try:
        fp = open(filepath, "rU")
    except IOError:
        fp = None

    if fp:
        target = {}
        for line in fp:
            words = line.split()
            if len(words) >= 4 and words[0][0] != '#':
                n = int(words[0])
                if n < meshstat.numberOfVertices:
                    target[n] = np.array([float(words[1]), float(words[2]), float(words[3])])
        fp.close()
        _refTargetCache[filepath] = target
        return target
    else:
        raise IOError("Can't find neither %s nor a replacement target" % filepath)

