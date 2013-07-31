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

    '''
    def reinit(self):

        if self.isDirty:
            shape = self.modifier.compileWarpTarget(self.human)
            saveWarpedTarget(shape, self.modifier.warppath)
            self.__init__(self.modifier, self.human)
            self.isDirty = False


    def apply(self, obj, morphFactor, update=True, calcNormals=True, faceGroupToUpdateName=None, scale=(1.0,1.0,1.0)):

        self.reinit()
        algos3d.Target.apply(self, obj, morphFactor, update, calcNormals, faceGroupToUpdateName, scale)
    '''

def saveWarpedTarget(shape, path):
    slist = list(shape.items())
    slist.sort()
    fp = open(path, "w")
    for (n, dr) in slist:
        fp.write("%d %.4f %.4f %.4f\n" % (n, dr[0], dr[1], dr[2]))
    fp.close()

#----------------------------------------------------------
#   class WarpSlider
#----------------------------------------------------------

class WarpSlider(humanmodifier.ModifierSlider):

    # Override
    def resetWarpTargets(self):
        #log.debug("Reset NOT %s" % self)
        pass

#----------------------------------------------------------
#   class WarpModifier
#----------------------------------------------------------

class BaseSpec:
    def __init__(self, path, factors):
        self.path = path
        self.factors = factors
        self.value = -1

    def __repr__(self):
        return ("<BaseSpec %s %.4f %s>" % (self.path, self.value, self.factors))


class TargetSpec:
    def __init__(self, path, factors):
        self.path = path.replace("-${tone}","").replace("-${weight}","")
        self.factors = factors
        self.verts = None
        if "$" in self.path:
            log.debug("TS %s %s" % (self.path, path))
            halt

    def __repr__(self):
        return ("<TargetSpec %s %s>" % (self.path, self.factors))


class WarpModifier (humanmodifier.SimpleModifier):

    def __init__(self, template, bodypart, modtype):
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
        self.template = template
        self.bodypart = bodypart
        self.slider = None
        self.refTargets = {}
        self.modtype = modtype

        self.fallback = None
        for (tlabel, tname, tvar) in _warpGlobals.modifierTypes[modtype]:
            self.fallback = humanmodifier.MacroModifier(tlabel, tname, tvar)
            break

        self.remaps = {}
        for ethnic in _warpGlobals.ethnics:
            self.remaps[ethnic] = ethnic
        for age in _warpGlobals.ages:
            self.remaps[age] = age
        for gender in _warpGlobals.genders:
            self.remaps[gender] = gender

        self.bases = {}
        self.targetSpecs = {}
        if modtype == "GenderAge":
            self.setupBaseCharacters("Gender", "Age", None, None, None)
        elif modtype == "Ethnic":
            self.setupBaseCharacters(None, None, "Ethnic", None, None)
        elif modtype == "GenderAgeEthnic":
            self.setupBaseCharacters("Gender", "Age", "Ethnic", None, None)
        elif modtype == "GenderAgeToneWeight":
            self.setupBaseCharacters("Gender", "Age", None, "Tone", "Weight")


    def setupBaseCharacters(self, genders, ages, ethnics, tones, weights):
        global _warpGlobals

        for gender in ["female", "male"]:
            for age in ["baby", "child", "young", "old"]:
                for ethnic in _warpGlobals.baseCharacterParts[ethnics]:
                    path1 = str(self.template)
                    key1 = ""
                    factors1 = []
                    base1 = mh.getSysDataPath("targets/macrodetails/")

                    if ethnic is None:
                        base1 += "caucasian-"
                        for e in _warpGlobals.ethnics:
                            self.remaps[e] = "caucasian"
                    else:
                        base1 += ethnic + "-"
                        key1 += ethnic + "-"
                        factors1.append(ethnic)
                        path1 = path1.replace("${ethnic}", ethnic)

                    base1 += gender + "-"
                    key1 += gender + "-"
                    factors1.append(gender)
                    path1 = path1.replace("${gender}", gender)

                    base1 += age + ".target"
                    key1 += age
                    factors1.append(age)
                    if ages is None:
                        path1 = path1.replace("${age}", "young")
                    else:
                        path1 = path1.replace("${age}", age)

                    if key1[-1] == "-":
                        key1 = key1[:-1]
                    key1 = base1
                    self.bases[key1] = BaseSpec(base1, factors1)
                    self.targetSpecs[key1] = TargetSpec(path1, factors1)

                    if tones is None or weights is None:
                        #log.debug("Bases %s" % self.bases.items())
                        continue

                    for tone in _warpGlobals.baseCharacterParts[tones]:
                        for weight in _warpGlobals.baseCharacterParts[weights]:
                            base2 = mh.getSysDataPath("targets/macrodetails/universal-%s-%s-%s-%s.target") % (gender, age, tone, weight)
                            key2 = "universal-%s-%s-%s-%s" % (gender, age, tone, weight)
                            factors2 = factors1 + [tone, weight]
                            key2 = base2
                            self.bases[key2] = BaseSpec(base2, factors2)
                            path2 = path1.replace("${tone}", tone).replace("${weight}", weight)
                            self.targetSpecs[key2] = TargetSpec(path2, factors2)


    def __repr__(self):
        return ("<WarpModifier %s>" % (os.path.basename(self.template)))


    def setValue(self, human, value):
        self.compileTargetIfNecessary(human)
        humanmodifier.SimpleModifier.setValue(self, human, value)


    def updateValue(self, human, value, updateNormals=1):
        self.compileTargetIfNecessary(human)
        humanmodifier.SimpleModifier.updateValue(self, human, value, updateNormals)
        human.warpNeedReset = False


    def clampValue(self, value):
        return max(0.0, min(1.0, value))


    def compileTargetIfNecessary(self, human):
        try:
            target = algos3d.warpTargetBuffer[self.warppath]
        except KeyError:
            target = None
        if target:
            if not isinstance(target, WarpTarget):
                raise NameError("%s is not a warp target" % target)
        else:
            target = WarpTarget(self, human)
            algos3d.warpTargetBuffer[self.warppath] = target
            shape = self.compileWarpTarget(human)
            saveWarpedTarget(shape, self.warppath)


    def compileWarpTarget(self, human):
        global _warpGlobals
        log.message("COMPWARP %s", self)
        landmarks = _warpGlobals.getLandMarks(self.bodypart)

        obj = human.meshData
        srcCharCoord = obj.orig_coord.copy()
        trgCharCoord = obj.orig_coord.copy()
        srcTargetCoord = {}

        sumtargets = 0
        for charpath,value in human.targetsDetailStack.items():
            if charpath in self.bases.keys():
                sumtargets += value
        if sumtargets == 0:
            log.debug("No targets: %s" % human.targetsDetailStack.keys())
        factor = 1.0/sumtargets

        for charpath,value in human.targetsDetailStack.items():
            try:
                target = algos3d.targetBuffer[charpath]
            except KeyError:
                continue
            log.debug("  CHAR %s %s %s" % (charpath, value, target))
            srcVerts = np.s_[...]
            dstVerts = target.verts[srcVerts]
            data = value * target.data[srcVerts]
            trgCharCoord[dstVerts] += data
            if charpath in self.bases.keys():
                srcCharCoord[dstVerts] += data
                trgspec = self.targetSpecs[charpath]
                srcTrg = readTarget(trgspec.path)
                addVerts(srcTargetCoord, factor*value, srcTrg)

        if srcTargetCoord:
            shape = warp.warp_target(srcTargetCoord, srcCharCoord, trgCharCoord, landmarks)
        else:
            shape = {}
        log.message("...done")
        return shape

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

def compileWarpTarget(template, fallback, human, bodypart):
    mod = WarpModifier(template, bodypart, fallback)
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

    log.debug("GETTARG %s" % filepath)
    try:
        return _warpGlobals.refTargets[filepath]
    except KeyError:
        pass

    log.debug("READTARG %s" % filepath)
    words = filepath.rsplit("-",3)
    if words[0] == mh.getSysDataPath("targets/macrodetails/universal"):
        if words[1] == "averagemuscle":
            if words[2] == "averageweight.target":
                return {}
            else:
                filepath = words[0] + "-" + words[2]
        elif words[2] == "averageweight.target":
            filepath = words[0] + "-" + words[1] + ".target"
        log.debug("  NEW %s" % filepath)

    try:
        fp = open(filepath, "rU")
    except:
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
        _warpGlobals.refTargets[filepath] = target
        return target
    else:
        halt
        return None


def findReplacementFile(filepath):
    # If some targets are missing, try to find a good default
    replacements = [
        (["-averagemuscle", "-averageweight"], ""),
        (["/asian", "/african"], "/caucasian"),
        (["/baby", "/child", "/old"], "/young"),
        (["/male"], "/female"),
        (["/female_young"], ""),
    ]

    filepath1 = filepath
    tried = [filepath]
    for variants,default in replacements:
        for variant in variants:
            filepath1 = filepath1.replace(variant, default)
            try:
                fp = open(filepath1, "rU")
                log.message("   Replaced %s\n  -> %s", filepath, filepath1)
                return fp
            except IOError:
                continue

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
        self.refTargets = {}

        self.ethnics = ["african", "asian", "caucasian"]
        self.genders = ["female", "male"]
        self.ages = ["baby", "child", "young", "old"]

        self.modifierTypes = {
            "GenderAge" : [
                ("macrodetails", None, "Gender"),
                ("macrodetails", None, "Age"),
            ],
            "Ethnic" : [
                ("macrodetails", None, "African"),
                ("macrodetails", None, "Asian"),
            ],
            "GenderAgeEthnic" : [
                ("macrodetails", None, "Gender"),
                ("macrodetails", None, "Age"),
                ("macrodetails", None, "African"),
                ("macrodetails", None, "Asian"),
            ],
            "GenderAgeToneWeight" : [
                ("macrodetails", None, "Gender"),
                ("macrodetails", None, "Age"),
                ("macrodetails", "universal", "Muscle"),
                ("macrodetails", "universal", "Weight"),
                #("macrodetails", "universal-stature", "Height"),
            ],
        }

        self.baseCharacterParts = {
            "Gender" : ("male", "female"),
            "Age" : ("child", "young", "old"),
            "Ethnic" : ("caucasian", "african", "asian"),
            "Tone" : ("minmuscle", "averagemuscle", "maxmuscle"),
            "Weight" : ("minweight", "averageweight", "maxweight"),
            None : [None]
        }


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


def touchWarps():
    global _warpGlobals
    _warpGlobals.dirty = True


_warpGlobals = GlobalWarpData()


def order(dict):
    stru = list(dict.items())
    stru.sort()
    return stru

