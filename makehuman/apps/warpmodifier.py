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

import math
import numpy as np
from operator import mul
import mh
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

    def __init__(self, modifier, human):

        algos3d.Target.__init__(self, human.meshData, modifier.warppath)

        self.human = human
        self.modifier = modifier


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

        string = template.replace('$','').replace('{','').replace('}','')
        warppath = os.path.join(mh.getPath(""), "warp", string)
        if not os.path.exists(os.path.dirname(warppath)):
            os.makedirs(os.path.dirname(warppath))
        if not os.path.exists(warppath):
            fp = open(warppath, "w")
            fp.close()

        humanmodifier.SimpleModifier.__init__(self, warppath)
        self.eventType = 'warp'
        self.warppath = warppath
        self.template = str(template)
        self.bodypart = bodypart
        self.slider = None

        for (tlabel, tname, tvar) in self.modifierTypes:
            self.fallback = humanmodifier.MacroModifier(tlabel, tname, tvar)
            break

        self.setupReferences()
        self.refTargetVerts = {}


    def __repr__(self):
        return ("<WarpModifier %s>" % (os.path.basename(self.template)))


    def setValue(self, human, value):
        self.compileTargetIfNecessary(human)
        humanmodifier.SimpleModifier.setValue(self, human, value)
        return
        log.debug("SETVAL")
        loglist(algos3d.targetBuffer)
        loglist(algos3d.warpTargetBuffer)
        loglist(human.targetsDetailStack)


    def updateValue(self, human, value, updateNormals=1):
        self.compileTargetIfNecessary(human)
        humanmodifier.SimpleModifier.updateValue(self, human, value, updateNormals)


    def clampValue(self, value):
        return max(0.0, min(1.0, value))


    def compileTargetIfNecessary(self, human):
        try:
            target = algos3d.warpTargetBuffer[self.warppath]
        except KeyError:
            target = None
        if target:
            if not isinstance(target, WarpTarget):
                raise TypeError("%s is not a warp target" % target)
        else:
            target = WarpTarget(self, human)
            algos3d.warpTargetBuffer[self.warppath] = target
            shape = self.compileWarpTarget(human)
            saveWarpedTarget(shape, self.warppath)


    def compileWarpTarget(self, human):
        global _warpGlobals
        log.message("COMPWARP %s", self)
        landmarks = _warpGlobals.getLandMarks(self.bodypart)
        srcTargetCoord, srcCharCoord, trgCharCoord = self.getReferences(human)
        if srcTargetCoord:
            shape = warp.warp_target(srcTargetCoord, srcCharCoord, trgCharCoord, landmarks)
        else:
            shape = {}
        return shape


    def getReferences(self, human):
        #obj = human.meshData
        #srcCharCoord = obj.orig_coord.copy()
        srcCharCoord = human.getSeedMesh().coord.copy()
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
            log.debug("self.refCharacters:")
            for key,value in self.refCharacters.items():
                log.debug("  %s: %s" % (key, value))
            raise NameError("Warping problem")

        for charpath,value in human.targetsDetailStack.items():
            try:
                trgChar = algos3d.targetBuffer[charpath]
            except KeyError:
                continue    # Warp target - ignore

            srcVerts = np.s_[...]
            dstVerts = trgChar.verts[srcVerts]
            trgCharCoord[dstVerts] += value * trgChar.data[srcVerts]

            try:
                refchar = self.refCharacters[charpath]
            except KeyError:
                continue
            reftrg = self.refTargets[charpath]

            srcChar = readTarget(refchar)
            dstVerts = srcChar.verts[srcVerts]
            srcCharCoord[dstVerts] +=  value * srcChar.data[srcVerts]

            srcTrg = readTarget(reftrg)
            addVerts(srcTargetCoord, value, srcTrg)

        return srcTargetCoord, srcCharCoord, trgCharCoord

#----------------------------------------------------------
#   Specialized warp modifiers
#----------------------------------------------------------

class GenderAgeWarpModifier (WarpModifier):

    modifierTypes = [
            ("macrodetails", None, "Gender"),
            ("macrodetails", None, "Age"),
        ]


class EthnicWarpModifier (WarpModifier):

    modifierTypes = [
            ("macrodetails", None, "African"),
            ("macrodetails", None, "Asian"),
        ]

    def setupReferences(self):
        self.refTargets = {}
        self.refCharacters = {}

        for ethnic in ["caucasian", "african", "asian"]:
            reftrg = self.template.replace("${ethnic}", ethnic)
            refchar = mh.getSysDataPath("targets/macrodetails/%s-female-young.target" % (ethnic))
            for gender in ["female", "male"]:
                for age in ["baby", "child", "young", "old"]:
                    base = mh.getSysDataPath("targets/macrodetails/%s-%s-%s.target" % (ethnic, gender, age))
                    self.refCharacters[base] = refchar
                    self.refTargets[base] = reftrg


class GenderAgeEthnicWarpModifier (WarpModifier):

    modifierTypes = [
            ("macrodetails", None, "Gender"),
            ("macrodetails", None, "Age"),
            ("macrodetails", None, "African"),
            ("macrodetails", None, "Asian"),
        ]


class GenderAgeToneWeightWarpModifier (WarpModifier):

    modifierTypes = [
            ("macrodetails", None, "Gender"),
            ("macrodetails", None, "Age"),
            ("macrodetails", "universal", "Muscle"),
            ("macrodetails", "universal", "Weight"),
            #("macrodetails", "universal-stature", "Height"),
        ]

    def setupReferences(self):
        self.refTargets = {}
        self.refCharacters = {}

        for ethnic in ["caucasian", "african", "asian"]:
            for gender in ["female", "male"]:
                for age in ["baby", "child", "young", "old"]:
                    path = self.template.replace("${ethnic}", ethnic).replace("${gender}", gender).replace("${age}", age)
                    reftrg = path.replace("-${tone}", "averagemuscle").replace("-${weight}", "averageweight")
                    refchar = mh.getSysDataPath("targets/macrodetails/%s-%s-%s.target" % (ethnic, gender, age))
                    base = mh.getSysDataPath("targets/macrodetails/%s-%s-%s.target" % (ethnic, gender, age))
                    #self.refCharacters[base] = refchar
                    #self.refTargets[base] = reftrg

                    for tone in ["minmuscle", "averagemuscle", "maxmuscle"]:
                        for weight in ["minweight", "averageweight", "maxweight"]:
                            univ = mh.getSysDataPath("targets/macrodetails/universal-%s-%s-%s-%s.target") % (gender, age, tone, weight)
                            self.refCharacters[univ] = univ
                            self.refTargets[univ] = path.replace("${tone}", tone).replace("${weight}", weight)


#----------------------------------------------------------
#   Reset warp buffer
#----------------------------------------------------------

def resetWarpBuffer():
    global _warpGlobals
    import gui3d

    if algos3d.warpTargetBuffer:
        log.debug("WARP RESET")
        human = gui3d.app.selectedHuman
        for trgpath in algos3d.warpTargetBuffer:
            human.setDetail(trgpath, 0)
        algos3d.warpTargetBuffer = {}
        human.applyAllTargets()

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
    words = filepath.rsplit("-",3)
    if words[0] == mh.getSysDataPath("targets/macrodetails/universal"):
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
        folder = mh.getSysDataPath("landmarks")
        for file in os.listdir(folder):
            (name, ext) = os.path.splitext(file)
            if ext != ".lmk":
                continue
            path = os.path.join(folder, file)
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