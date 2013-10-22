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

__docformat__ = 'restructuredtext'

import numpy as np
from operator import mul
from getpath import getPath, getSysDataPath
import os

import algos3d
import meshstat
import warp
import humanmodifier
import log
from core import G

#----------------------------------------------------------
#   class WarpTarget
#----------------------------------------------------------

class WarpTarget(algos3d.Target):

    def __init__(self, shape, modifier, human):

        algos3d.Target.__init__(self, human.meshData, None)

        self.human = human
        self.modifier = modifier

        data = list(shape.items())
        data.sort()
        raw = np.asarray(data, dtype=algos3d.Target.dtype)
        self.verts = raw['index']
        self.data = raw['vector']

        self.faces = human.meshData.getFacesForVertices(self.verts)


    def __repr__(self):
        return ( "<WarpTarget %s>" % (os.path.basename(self.modifier.warppath)) )


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

class WarpModifier (humanmodifier.SimpleModifier):

    def __init__(self, template, bodypart):
        global _warpGlobals
        _warpGlobals.modifiers.append(self)

        warppath = template.replace('$','').replace('{','').replace('}','')
        humanmodifier.SimpleModifier.__init__(self, warppath)
        self.eventType = 'warp'
        self.warppath = warppath
        self.template = str(template)
        self.bodypart = bodypart
        self.slider = None

        #for (tlabel, tname, tvar) in self.modifierTypes:
        #    self.fallback = humanmodifier.MacroModifier(tlabel, tname, tvar)
        #    break

        self.setupReferences()
        self.refTargetVerts = {}


    def __repr__(self):
        return ("<WarpModifier %s>" % (os.path.basename(self.template)))


    def setValue(self, human, value):
        self.compileTargetIfNecessary(human)
        humanmodifier.SimpleModifier.setValue(self, human, value)
        return
        log.debug("SETVAL")
        human.traceStacks()


    def updateValue(self, human, value, updateNormals=1):
        self.compileTargetIfNecessary(human)
        humanmodifier.SimpleModifier.updateValue(self, human, value, updateNormals)


    def clampValue(self, value):
        return max(0.0, min(1.0, value))


    def compileTargetIfNecessary(self, human):
        try:
            target = algos3d.targetBuffer[self.warppath]
        except KeyError:
            target = None
        if target:
            if not isinstance(target, WarpTarget):
                raise TypeError("%s is not a warp target" % target)
        else:
            shape = self.compileWarpTarget(human)
            target = WarpTarget(shape, self, human)
            algos3d.targetBuffer[self.warppath] = target
            human.hasWarpTargets = True
            #saveWarpedTarget(shape, self.warppath)


    def compileWarpTarget(self, human):
        global _warpGlobals
        log.message("COMPWARP %s", self)
        landmarks = _warpGlobals.getLandMarks(self.bodypart)
        srcTargetCoord, srcCharCoord, trgCharCoord = self.getReferences(human)
        #human.traceStacks()
        #self.traceReference()

        obj = human.meshData
        #printDebugCoord("mesh", obj.orig_coord, obj)
        printDebugCoord("src_targ", srcCharCoord, obj, srcTargetCoord)
        printDebugCoord("src_char", srcCharCoord, obj)
        printDebugCoord("trg_char", trgCharCoord, obj)

        if srcTargetCoord:
            shape = warp.warp_target(srcTargetCoord, srcCharCoord, trgCharCoord, landmarks)
        else:
            shape = {}

        printDebugCoord("trg_targ", trgCharCoord, obj, shape)

        return shape


    def traceReference(self):
        log.debug("self.refCharacters:")
        for key,value in self.refCharacters.items():
            log.debug("  %s: %s" % (key, value))


    def getReferences(self, human):
        """
        Building source and target characters from scratch.
        The source character is the sum of reference characters.
        The target character is the sum of all non-warp targets.
        Cannot use human.getSeedMesh() which returns sum of all targets.
        """

        srcCharCoord = human.meshData.orig_coord.copy()
        trgCharCoord = srcCharCoord.copy()
        srcTargetCoord = {}

        sumtargets = 0
        for charpath,value in human.targetsDetailStack.items():
            try:
                self.refCharacters[charpath]
                sumtargets += value
            except KeyError:
                continue
        if abs(sumtargets-1) > 1e-3 and abs(sumtargets-2) > 1e-3:
            log.debug("Inconsistent target sum %s." % sumtargets)
            human.traceStacks()
            self.traceReference()
            raise NameError("Warping problem")

        for charpath,value in human.targetsDetailStack.items():
            try:
                trgChar = algos3d.targetBuffer[charpath]
            except KeyError:
                continue    # Warp target? - ignore
            if isinstance(trgChar, WarpTarget):
                continue

            srcVerts = np.s_[...]
            dstVerts = trgChar.verts[srcVerts]
            trgCharCoord[dstVerts] += value * trgChar.data[srcVerts]

            try:
                refchar = self.refCharacters[charpath]
            except KeyError:
                refchar = None

            if refchar:
                srcChar = readTarget(refchar)
                dstVerts = srcChar.verts[srcVerts]
                srcCharCoord[dstVerts] +=  value * srcChar.data[srcVerts]

            try:
                reftrg = self.refTargets[charpath]
            except KeyError:
                reftrg = None
            if reftrg:
                srcTrg = readTarget(reftrg)
                addVerts(srcTargetCoord, value, srcTrg)

        return srcTargetCoord, srcCharCoord, trgCharCoord


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
#   Specialized warp modifiers
#----------------------------------------------------------

class EthnicGenderAgeWarpModifier (WarpModifier):

    def getRefChar(self, ethnic, gender, age):
        return getSysDataPath("targets/macrodetails/%s-%s-%s.target" % (ethnic, gender, age))

    def setupReferences(self):
        self.refTargets = {}
        self.refCharacters = {}

        for ethnic in ["caucasian", "african", "asian"]:
            for gender in ["female", "male"]:
                for age in ["baby", "child", "young", "old"]:
                    reftrg = self.template.replace("${ethnic}", ethnic).replace("${gender}", gender).replace("${age}", age)
                    refchar = self.getRefChar(ethnic, gender, age)
                    base = getSysDataPath("targets/macrodetails/%s-%s-%s.target" % (ethnic, gender, age))
                    self.refCharacters[base] = refchar
                    self.refTargets[base] = reftrg


class GenderAgeWarpModifier (EthnicGenderAgeWarpModifier):

    def getRefChar(self, ethnic, gender, age):
        return getSysDataPath("targets/macrodetails/caucasian-%s-%s.target" % (gender, age))


class EthnicWarpModifier (EthnicGenderAgeWarpModifier):

    def getRefChar(self, ethnic, gender, age):
        return getSysDataPath("targets/macrodetails/%s-female-young.target" % (ethnic))


class EthnicGenderAgeToneWeightWarpModifier (WarpModifier):

    def getRefChar(self, ethnic, gender, age):
        return getSysDataPath("targets/macrodetails/%s-%s-%s.target" % (ethnic, gender, age))

    def setupReferences(self):
        self.refTargets = {}
        self.refCharacters = {}

        for ethnic in ["caucasian", "african", "asian"]:
            for gender in ["female", "male"]:
                for age in ["baby", "child", "young", "old"]:
                    refchar = self.getRefChar(ethnic, gender, age)
                    base = getSysDataPath("targets/macrodetails/%s-%s-%s.target" % (ethnic, gender, age))
                    self.refCharacters[base] = refchar
                    path = self.template.replace("${ethnic}", ethnic).replace("${gender}", gender).replace("${age}", age)
                    for tone in ["minmuscle", "averagemuscle", "maxmuscle"]:
                        for weight in ["minweight", "averageweight", "maxweight"]:
                            univ = getSysDataPath("targets/macrodetails/universal-%s-%s-%s-%s.target") % (gender, age, tone, weight)
                            self.refCharacters[univ] = univ
                            self.refTargets[univ] = path.replace("${tone}", tone).replace("${weight}", weight)


class GenderAgeToneWeightWarpModifier (EthnicGenderAgeToneWeightWarpModifier):

    def getRefChar(self, ethnic, gender, age):
        return getSysDataPath("targets/macrodetails/caucasian-%s-%s.target" % (gender, age))


#----------------------------------------------------------
#   Reset warp buffer
#----------------------------------------------------------

def resetWarpBuffer():
    global _warpGlobals

    human = G.app.selectedHuman
    if human.hasWarpTargets:
        log.debug("WARP RESET")
        for path,target in algos3d.targetBuffer.items():
            if isinstance(target, WarpTarget):
                log.debug("  DEL %s" % path)
                human.setDetail(path, 0)
                del algos3d.targetBuffer[path]
        human.applyAllTargets()
        human.hasWarpTargets = False

#----------------------------------------------------------
#   Call from exporter
#----------------------------------------------------------

def compileWarpTarget(modtype, template, human, bodypart):
    if modtype == 'Ethnic':
        mod = EthnicWarpModifier(template, bodypart)
    elif modtype == 'GenderAgeToneWeight':
        mod = GenderAgeToneWeightWarpModifier(template, bodypart)
    else:
        raise TypeError("compileWarpTarget modtype = %s" % modtype)

    return mod.compileWarpTarget(human)

#----------------------------------------------------------
#   Add verts. Replace with something faster using numpy.
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

def readTarget(filepath):
    global _warpGlobals

    # Target cached?
    try:
        return _warpGlobals.targetCache[filepath]
    except KeyError:
        pass

    # Target already on global target stack?
    try:
        target = algos3d.targetBuffer[filepath]
        _warpGlobals.targetCache[filepath] = target
        #log.debug("GLOBTAR %s" % target)
        return target
    except KeyError:
        pass

    # If neither, read target
    #log.debug("READTAR %s" % filepath)
    filepath = filepath.replace("\\","/")
    words = filepath.rsplit("-",3)
    if words[0] == getSysDataPath("targets/macrodetails/universal"):
        if words[1] == "averagemuscle":
            if words[2] == "averageweight.target":
                return {}
            else:
                filepath = words[0] + "-" + words[2]
        elif words[2] == "averageweight.target":
            filepath = words[0] + "-" + words[1] + ".target"
        #log.debug("  NEW %s" % filepath)

    try:
        fp = open(filepath, "rU")
    except IOError:
        fp = None

    if fp is None:
        fp = findReplacementFile(filepath)

    if fp:
        target = {}
        for line in fp:
            words = line.split()
            if len(words) >= 4 and words[0][0] != '#':
                n = int(words[0])
                if n < meshstat.numberOfVertices:
                    target[n] = np.array([float(words[1]), float(words[2]), float(words[3])])
        fp.close()
        _warpGlobals.targetCache[filepath] = target
        return target
    else:
        raise IOError("Can't find neither %s nor a replacement target" % filepath)


def findReplacementFile(filepath):
    # If some targets are missing, try to find a good default
    replacements = [
        (["-minmuscle"], "-averagemuscle"),
        (["-maxmuscle"], "-averagemuscle"),
        (["-minweight"], "-averageweight"),
        (["-maxweight"], "-averageweight"),
        (["-asian", "-african"], "-caucasian"),
        (["/asian", "/african"], "/caucasian"),
        (["\\asian", "\\african"], "\\caucasian"),
        (["-baby"], "-child"),
        (["-child", "-old"], "-young"),
        (["/baby", "/child", "/old"], "/young"),
        (["\\baby", "\\child", "\\old"], "/young"),
        (["-male"], "-female"),
        (["/male"], "/female"),
        (["\\male"], "\\female"),
        (["-female"], "-male"),
        (["/female"], "/male"),
        (["\\female"], "\\male"),
    ]

    filepath1 = filepath
    tried = [filepath]
    for variants,default in replacements:
        for variant in variants:
            filepath1 = filepath1.replace(variant, default)
            if filepath1 not in tried:
                try:
                    fp = open(filepath1, "rU")
                    log.message("   Replaced %s\n  -> %s", filepath, filepath1)
                    return fp
                except IOError:
                    log.debug("  Tried %s" % filepath1)
                    tried.append(filepath1)

    string = "Warning: Found none of:"
    for filepath1 in tried:
        string += "\n    %s" % filepath1
    log.message(string)
    return None

#----------------------------------------------------------
#   Global warp data
#----------------------------------------------------------

class GlobalWarpData:
    def __init__(self):
        self.modifiers = []
        self._landMarks = None
        self.targetCache = {}


    def getLandMarks(self, bodypart):
        if self._landMarks is not None:
            return self._landMarks[bodypart]

        self._landMarks = {}
        folder = getSysDataPath("landmarks")
        for file_ in os.listdir(folder):
            (name, ext) = os.path.splitext(file_)
            if ext != ".lmk":
                continue
            path = os.path.join(folder, file_)
            with open(path, "r") as fp:
                landmark = []
                for line in fp:
                    words = line.split()
                    if len(words) > 0:
                        m = int(words[0])
                        landmark.append(m)
            self._landMarks[name] = landmark

        return self._landMarks[bodypart]


_warpGlobals = GlobalWarpData()


def order(dict):
    stru = list(dict.items())
    stru.sort()
    return stru


def loglist(dict):
    #return
    stru = list(dict.items())
    stru.sort()
    log.debug("  [")
    for x,y in stru:
        log.debug("    %s: %s" % (x,y))
    log.debug("  ]")
