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
        self.isWarp = True
        self.isDirty = True
        self.isObsolete = False


    def __repr__(self):
        return ( "<WarpTarget %s d:%s o:%s>" % (os.path.basename(self.modifier.warppath), self.isDirty, self.isObsolete) )


    def reinit(self):

        if self.isObsolete:
            halt
        if self.isDirty:
            shape = self.modifier.compileWarpTarget(self.human)
            saveWarpedTarget(shape, self.modifier.warppath)
            self.__init__(self.modifier, self.human)
            self.isDirty = False


    def apply(self, obj, morphFactor, update=True, calcNormals=True, faceGroupToUpdateName=None, scale=(1.0,1.0,1.0)):

        self.reinit()
        algos3d.Target.apply(self, obj, morphFactor, update, calcNormals, faceGroupToUpdateName, scale)


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


class BaseSpec:
    def __init__(self, path, factors):
        self.path = path
        self.factors = factors
        self.value = -1

    def __repr__(self):
        return ("<BaseSpec %s %.4f %s>" % (self.path, self.value, self.factors))


class TargetSpec:
    def __init__(self, path, factors):
        self.path = path
        self.factors = factors

    def __repr__(self):
        return ("<TargetSpec %s %s>" % (self.path, self.factors))


class WarpModifier (humanmodifier.SimpleModifier):

    def __init__(self, template, bodypart, modtype):
        global _warpGlobals

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
        self.isWarp = True
        self.bodypart = bodypart
        self.slider = None
        self.refTargets = {}
        self.refTargetVerts = {}
        self.modtype = modtype

        self.fallback = None
        for (tlabel, tname, tvar) in _warpGlobals.modifierTypes[modtype]:
            self.fallback = humanmodifier.MacroModifier(tlabel, tname, tvar)
            break

        self.bases = {}
        self.targetSpecs = {}
        if modtype == "GenderAge":
            self.setupBaseCharacters("Gender", "Age", "NoEthnic", "NoUniv", "NoUniv")
        elif modtype == "GenderAgeEthnic":
            self.setupBaseCharacters("Gender", "Age", "Ethnic", "NoUniv", "NoUniv")
        elif modtype == "GenderAgeToneWeight":
            self.setupBaseCharacters("Gender", "Age", "NoEthnic", "Tone", "Weight")


    def setupBaseCharacters(self, genders, ages, ethnics, tones, weights):
        global _warpGlobals

        for gender in _warpGlobals.baseCharacterParts[genders]:
            for age in _warpGlobals.baseCharacterParts[ages]:
                for ethnic1 in _warpGlobals.baseCharacterParts[ethnics]:
                    path1 = self.template

                    if ethnic1 is None:
                        base1 = "data/targets/macrodetails/caucasian-%s-%s.target" % (gender, age)
                        key1 = "%s-%s" % (gender, age)
                        factors1 = [gender, age]
                    else:
                        if ethnic1 == "caucasian":
                            ethnic2 = "caucasian"
                        else:
                            ethnic2 = ethnic1
                        base1 = "data/targets/macrodetails/%s-%s-%s.target" % (ethnic2, gender, age)
                        key1 = "%s-%s-%s" % (ethnic1, gender, age)
                        factors1 = [ethnic1, gender, age]
                        path1 = path1.replace("${ethnic}", ethnic1)

                    self.bases[key1] = BaseSpec(base1, factors1)
                    path1 = path1.replace("${gender}", gender).replace("${age}",age)

                    for tone in _warpGlobals.baseCharacterParts[tones]:
                        for weight in _warpGlobals.baseCharacterParts[weights]:
                            if tone and weight:
                                base2 = "data/targets/macrodetails/universal-%s-%s-%s-%s.target" % (gender, age, tone, weight)
                                key2 = "universal-%s-%s-%s-%s" % (gender, age, tone, weight)
                                factors2 = factors1 + [tone, weight]
                                self.bases[key2] = BaseSpec(base2, factors2)
                                path2 = path1.replace("${tone}", tone).replace("${weight}", weight)
                                self.targetSpecs[key2] = TargetSpec(path2, factors2)

                            elif tone:
                                base2 = "data/targets/macrodetails/universal-%s-%s-%s.target" % (gender, age, tone)
                                key2 = "universal-%s-%s-%s" % (gender, age, tone)
                                factors2 = factors1 + [tone, 'averageweight']
                                self.bases[key2] = BaseSpec(base2, factors2)
                                path2 = path1.replace("${tone}", tone).replace("-${weight}", "")
                                self.targetSpecs[key2] = TargetSpec(path2, factors2)

                            elif weight:
                                base2 = "data/targets/macrodetails/universal-%s-%s-%s.target" % (gender, age, weight)
                                key2 = "universal-%s-%s-%s" % (gender, age, weight)
                                factors2 = factors1 + ['averagemuscle', weight]
                                self.bases[key2] = BaseSpec(base2, factors2)
                                path2 = path1.replace("-${tone}", "").replace("${weight}", weight)
                                self.targetSpecs[key2] = TargetSpec(path2, factors2)

                            else:
                                factors2 = factors1 + ['averagemuscle', 'averageweight']
                                path2 = path1.replace("-${tone}", "").replace("-${weight}", "")
                                self.targetSpecs[key1] = TargetSpec(path2, factors2)




    def __repr__(self):
        return ("<WarpModifier %s>" % (os.path.basename(self.template)))


    def setValue(self, human, value):
        humanmodifier.SimpleModifier.setValue(self, human, value)
        human.warpNeedReset = False


    def updateValue(self, human, value, updateNormals=1):
        target = self.getWarpTarget(G.app.selectedHuman)
        if not target:
            return
        target.reinit()
        humanmodifier.SimpleModifier.updateValue(self, human, value, updateNormals)
        human.warpNeedReset = False


    def clampValue(self, value):
        return max(0.0, min(1.0, value))


    def compileWarpTarget(self, human):
        global _warpGlobals
        log.message("Compile %s", self)
        landmarks = _warpGlobals.getLandMarks(self.bodypart)
        objectChanged = self.getRefObject(human)
        self.getRefTarget(human, objectChanged)
        roVerts = _warpGlobals.getRefObjectVerts(self.modtype)
        unwarpedCoords = _warpGlobals.getUnwarpedCoords(human)
        if (self.refTargetVerts and roVerts is not None):
            log.debug("BP %s" % self.bodypart)
            log.debug("RTV %s" % self.refTargetVerts)
            log.debug("ROV %s" % roVerts)
            log.debug("SHC %s" % unwarpedCoords)
            log.debug("LMK %s" % landmarks)
            shape = warp.warp_target(self.refTargetVerts, roVerts, unwarpedCoords, landmarks)
        else:
            shape = {}
        log.message("...done")
        return shape


    def getRefTarget(self, human, objectChanged):
        targetChanged = self.getBases(human)
        if targetChanged or objectChanged:
            log.message("Reference target changed")
            if not self.makeRefTarget(human):
                log.message("Updating character")
                human.applyAllTargets()
                self.getBases(human)
                if not self.makeRefTarget(human):
                    raise NameError("Character is empty")


    def getBases(self, human):
        targetChanged = False
        for key,base in self.bases.items():
            verts = self.getRefObjectVerts(base.path)
            if verts is None:
                base.value = 0
                continue

            cval1 = human.getDetail(base.path)
            if base.value != cval1:
                base.value = cval1
                targetChanged = True
        return targetChanged


    def makeRefTarget(self, human):
        self.refTargetVerts = {}
        madeRefTarget = False
        factors = self.fallback.getFactors(human, 1.0)
        print factors.keys()

        for target in self.targetSpecs.values():
            cval = reduce(mul, [factors[factor] for factor in target.factors])
            if cval > 0:
                log.debug("  reftrg %s %s", target.path, cval)
                madeRefTarget = True
                verts = self.getRefTargetVertsInsist(target.path)
                if verts is not None:
                    addVerts(self.refTargetVerts, cval, verts)
        return madeRefTarget


    def getRefTargetVertsInsist(self, path):
        verts = self.getTarget(path)
        if verts is not None:
            self.refTargets[path] = verts
            return verts

        for string in ["minmuscle", "maxmuscle", "minweight", "maxweight"]:
            if string in path:
                log.message("  Did not find %s", path)
                return None

        path1 = path.replace("/asian", "/caucasian").replace("/african", "/caucasian")
        verts = self.getTarget(path1)
        if verts is not None:
            self.refTargets[path] = verts
            log.message("   Replaced %s\n  -> %s", path, path1)
            return verts

        path2 = path1.replace("/baby", "/young").replace("/child", "/young").replace("/old", "/young")
        verts = self.getTarget(path2)
        if verts is not None:
            self.refTargets[path] = verts
            log.message("   Replaced %s\n  -> %s", path, path2)
            return verts

        path3 = path2.replace("/male", "/female")
        if verts is not None:
            self.refTargets[path] = verts
            log.message("   Replaced %s\n  -> %s", path, path2)
            return verts

        path4 = path3.replace("/female_young", "")
        verts = self.getTarget(path4)
        self.refTargets[path] = verts

        if verts is None:
            log.message("Warning: Found none of:\n    %s\n    %s\n    %s\n    %s\n    %s" %
                (path, path1, path2, path3, path4))
        else:
            log.message("   Replaced %s\n  -> %s" % (path, path4))
        return verts


    def getTarget(self, path):
        try:
            verts = self.refTargets[path]
        except KeyError:
            verts = None
        if verts is None:
            verts = readTarget(path)
        return verts


    def getWarpTarget(self, human):
        try:
            target = algos3d.targetBuffer[self.warppath]
        except KeyError:
            target = None

        if target:
            if not hasattr(target, "isWarp"):
                log.message("Found non-warp target: %s. Deleted", target.name)
                del algos3d.targetBuffer[self.warppath]
                return None
                #raise NameError("%s should be warp" % target)
            return target

        target = WarpTarget(self, human)
        algos3d.targetBuffer[self.warppath] = target
        return target


    def removeTarget(self):
        try:
            target = algos3d.targetBuffer[self.warppath]
        except KeyError:
            return
        del algos3d.targetBuffer[self.warppath]


    def getRefObject(self, human):
        global _warpGlobals

        if _warpGlobals.getRefObjectVerts(self.modtype) is not None:
            return False
        else:
            log.message("Reset warps")
            refverts = np.array(G.app.selectedHuman.meshData.orig_coord)
            for char in _warpGlobals.getRefObjects().keys():
                cval = human.getDetail(char)
                if cval:
                    log.debug("  refobj %s %s", os.path.basename(char), cval)
                    verts = self.getRefObjectVerts(char)
                    if verts is not None:
                        addVerts(refverts, cval, verts)
            _warpGlobals.setRefObjectVerts(self.modtype, refverts)
            return True


    def getRefObjectVerts(self, path):
        global _warpGlobals
        refObjects = _warpGlobals.getRefObjects()
        if refObjects[path]:
            return refObjects[path]
        else:
            verts = readTarget(path)
            if verts is not None:
                _warpGlobals.sefRefObject(path, verts)
            return verts


def removeAllWarpTargets(human):
    log.message("Removing all warp targets")
    for target in algos3d.targetBuffer.values():
        if hasattr(target, "isWarp"):
            log.message("  %s", target)
            target.isDirty = True
            target.isObsolete = True
            human.setDetail(target.name, 0)
            target.morphFactor = 0
            target.modifier.setValue(human, 0)
            if target.modifier.slider:
                target.modifier.slider.update()
            del algos3d.targetBuffer[target.name]


#----------------------------------------------------------
#   Call from exporter
#----------------------------------------------------------

def compileWarpTarget(template, fallback, human, bodypart):
    mod = WarpModifier(template, bodypart, fallback)
    return mod.compileWarpTarget(human)

#----------------------------------------------------------
#   Read target
#----------------------------------------------------------

def readTarget(path):
    try:
        fp = open(path, "r")
    except:
        fp = None
    if fp:
        target = {}
        for line in fp:
            words = line.split()
            if len(words) >= 4 and words[0][0] != '#':
                n = int(words[0])
                if n < algos3d.NMHVerts:
                    target[n] = np.array([float(words[1]), float(words[2]), float(words[3])])
        fp.close()
        return target
    else:
        log.message("Could not find %s" % os.path.realpath(path))
        return None

#----------------------------------------------------------
#   For testing np
#----------------------------------------------------------

def addVerts(targetVerts, cval, verts):
    for n,v in verts.items():
        dr = cval*v
        try:
            targetVerts[n] += dr
        except KeyError:
            targetVerts[n] = dr

#----------------------------------------------------------
#   Global warp data
#----------------------------------------------------------

class GlobalWarpData:
    def __init__(self):
        self._refObjectVerts = None
        self._landMarks = None
        self._refObjects = None
        self._unwarpedCoords = None
        self._warpedCoords = None
        self.dirty = False

        self.modifierTypes = {
            "GenderAge" : [
                ("macrodetails", None, "Gender"),
                ("macrodetails", None, "Age"),
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
            "NoEthnic" : [None],
            "Tone" : ("minmuscle", None, "maxmuscle"),
            "Weight" : ("minweight", None, "maxweight"),
            "NoUniv" : [None]
        }


    def reset(self):
        self._unwarpedCoords = None
        self._warpedCoords = None
        self.dirty = False


    def getUnwarpedCoords(self, human):
        if self.dirty:
            self.reset()
        elif self._unwarpedCoords is not None:
            return self._unwarpedCoords
        coords = np.array(G.app.selectedHuman.meshData.orig_coord)
        for target in algos3d.targetBuffer.values():
            if not hasattr(target, "isWarp"):
                verts = algos3d.targetBuffer[target.name].verts
                coords[verts] += target.morphFactor * target.data
        self._unwarpedCoords = coords
        return coords


    def getWarpedCoords(self, human):
        if self.dirty:
            self.reset()
        elif self._warpedCoords is not None:
            return self._warpedCoords
        coords = np.array(G.app.selectedHuman.meshData.orig_coord)
        for target in algos3d.targetBuffer.values():
            if hasattr(target, "isWarp"):
                verts = algos3d.targetBuffer[target.name].verts
                coords[verts] += target.morphFactor * target.data
        self._warpedCoords = coords
        return coords


    def getRefObjectVerts(self, modtype):
        if self._refObjectVerts is None:
            return None
        else:
            return self._refObjectVerts[modtype]


    def setRefObjectVerts(self, modtype, refverts):
        self._refObjectVerts[modtype] = refverts


    def getLandMarks(self, bodypart):
        if self._landMarks is not None:
            return self._landMarks[bodypart]

        self._landMarks = {}
        folder = "data/landmarks"
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


    def clearRefObject(self):
        self._refObjectVerts = {}
        for mtype in self.modifierTypes.keys():
            self._refObjectVerts[mtype] = None


    def getRefObjects(self):
        if self._refObjects is not None:
            return self._refObjects

        self.clearRefObject()
        self._refObjects = {}

        for ethnic in ["african", "asian", "caucasian"]:
            for age in ["baby", "child", "young", "old"]:
                for gender in ["female", "male"]:
                    path = "data/targets/macrodetails/%s-%s-%s.target" % (ethnic, gender, age)
                    self._refObjects[path] = None

        for age in ["baby", "child", "young", "old"]:
            for gender in ["female", "male"]:
                for tone in ["minmuscle", "maxmuscle"]:
                    path = "data/targets/macrodetails/universal-%s-%s-%s.target" % (gender, age, tone)
                    self._refObjects[path] = None
                    for weight in ["minweight", "maxweight"]:
                        path = "data/targets/macrodetails/universal-%s-%s-%s-%s.target" % (gender, age, tone, weight)
                        self._refObjects[path] = None
                for weight in ["minweight", "maxweight"]:
                    path = "data/targets/macrodetails/universal-%s-%s-%s.target" % (gender, age, weight)
                    self._refObjects[path] = None

        return self._refObjects


    def sefRefObject(self, path, verts):
        self._refObjects[path] = verts


def compromiseWarps():
    global _warpGlobals
    _warpGlobals.dirty = True


_warpGlobals = GlobalWarpData()


