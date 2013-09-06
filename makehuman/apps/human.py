#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Manuel Bastioni, Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import numpy as np
import algos3d
import guicommon
from core import G
import os
import events3d
from getpath import getSysDataPath
import log
import material

from makehuman import getBasemeshVersion, getShortVersion, getVersionStr, getVersion

class Human(guicommon.Object):

    def __init__(self, mesh, hairObj=None, eyesObj=None, genitalsObj=None):

        guicommon.Object.__init__(self, [0, 0, 0], mesh, True)

        self.hasWarpTargets = False

        self.MIN_AGE = 1.0
        self.MAX_AGE = 90.0
        self.MID_AGE = 25.0

        self.mesh.setCameraProjection(0)
        self.mesh.setShadeless(0)
        self.mesh.setCull(1)
        self.meshData = self.mesh

        self.maskFaces()

        self.hairObj = hairObj
        self.hairProxy = None
        self.eyesObj = eyesObj
        self.eyesProxy = None
        self.genitalsObj = genitalsObj
        self.genitalsProxy = None
        self.clothesObjs = {}
        self.clothesProxies = {}

        self.targetsDetailStack = {}  # All details targets applied, with their values
        self.symmetryModeEnabled = False

        self.uvset = None   # TODO probably deprecated (old UV library) but still referenced by MHX exporter

        self.setDefaultValues()

        self.bodyZones = ['l-eye','r-eye', 'jaw', 'nose', 'mouth', 'head', 'neck', 'torso', 'hip', 'pelvis', 'r-upperarm', 'l-upperarm', 'r-lowerarm', 'l-lowerarm', 'l-hand',
                          'r-hand', 'r-upperleg', 'l-upperleg', 'r-lowerleg', 'l-lowerleg', 'l-foot', 'r-foot', 'ear']

        self.material = material.fromFile(getSysDataPath('skins/default.mhmat'))
        self._defaultMaterial = material.Material().copyFrom(self.material)

    def getFaceMask(self):
        mesh = self.meshData
        group_mask = np.ones(len(mesh._faceGroups), dtype=bool)
        for g in mesh._faceGroups:
            if g.name.startswith('joint-') or g.name.startswith('helper-'):
                group_mask[g.idx] = False
        face_mask = group_mask[mesh.group]
        return face_mask

    def maskFaces(self):
        self.meshData.changeFaceMask(self.getFaceMask())
        self.meshData.updateIndexBufferFaces()


    def traceStacks(self, all=True, vertsToList=0):
        import warpmodifier
        log.debug("human.targetsDetailStack:")
        for path,value in self.targetsDetailStack.items():
            if all or path[0:4] != "data":
                log.debug("  %s: %s" % (path, value))
        log.debug("algos3d.targetBuffer:")
        for path,target in algos3d.targetBuffer.items():
            if isinstance(target, warpmodifier.WarpTarget):
                stars = " *** "
            else:
                stars = " "
            if all or path[0:4] != "data":
                log.debug("  %s:%s%s %d" % (path, stars, target, vertsToList))
                for n,vn in enumerate(target.verts[0:vertsToList]):
                    log.debug("   %d : %s %s" % (vn, target.data[n], self.mesh.coord[vn]))


    # Overriding hide and show to account for both human base and the hairs!

    def show(self):
        self.visible = True
        for obj in [self.hairObj, self.eyesObj, self.genitalsObj]:
            if obj:
                obj.show()
        for obj in self.clothesObjs.values():
            if obj:
                obj.show()
        self.setVisibility(True)
        self.callEvent('onShown', self)

    def hide(self):

        self.visible = False
        for obj in [self.hairObj, self.eyesObj, self.genitalsObj]:
            if obj:
                obj.hide()
        for obj in self.clothesObjs.values():
            if obj:
                obj.hide()
        self.setVisibility(False)
        self.callEvent('onHidden', self)

    # Overriding methods to account for both hair and base object

    def setPosition(self, position):
        dv = [x-y for x, y in zip(position, self.getPosition())]
        guicommon.Object.setPosition(self, position)
        for obj in [self.hairObj, self.eyesObj, self.genitalsObj]:
            if obj:
                obj.setPosition([x+y for x, y in zip(obj.getPosition(), dv)])
        for obj in self.clothesObjs.values():
            if obj:
                obj.setPosition([x+y for x, y in zip(obj.getPosition(), dv)])

        self.callEvent('onTranslated', self)

    def setRotation(self, rotation):
        guicommon.Object.setRotation(self, rotation)
        for obj in [self.hairObj, self.eyesObj, self.genitalsObj]:
            if obj:
                obj.setRotation(rotation)
        for obj in self.clothesObjs.values():
            if obj:
                obj.setRotation(rotation)

        self.callEvent('onRotated', self)

    def setSolid(self, *args, **kwargs):
        guicommon.Object.setSolid(self, *args, **kwargs)
        for obj in [self.hairObj, self.eyesObj, self.genitalsObj]:
            if obj:
                obj.setSolid(*args, **kwargs)
        for obj in self.clothesObjs.values():
            if obj:
                obj.setSolid(*args, **kwargs)

    def setSubdivided(self, *args, **kwargs):
        guicommon.Object.setSubdivided(self, *args, **kwargs)
        for obj in [self.hairObj, self.eyesObj, self.genitalsObj]:
            if obj:
                obj.setSubdivided(*args, **kwargs)
        for obj in self.clothesObjs.values():
            if obj:
                obj.setSubdivided(*args, **kwargs)

    def setShader(self, path):
        """
        Make sure the seed mesh is updated as well, so that visual appearence
        of the mesh remains consistent during dragging of target sliders.
        Because while dragging sliders, the original seed mesh is shown.
        """
        self.mesh.setShader(path)
        if self.isSubdivided() or self.isProxied():
            # Update seed mesh
            self.getSeedMesh().setShader(path)

    def setShaderParameter(self, name, value):
        """
        This method updates the shader parameters for the currently shown human
        mesh, but also that of the original seed mesh if it is subdivided or
        proxied. Use this method when you want to stream in shader parameters
        while sliders are being moved, because while dragging only the seed mesh
        is shown.
        """
        self.mesh.setShaderParameter(name, value)
        if self.isSubdivided() or self.isProxied():
            # Update seed mesh
            self.getSeedMesh().setShaderParameter(name, value)

    def setGender(self, gender):
        """
        Sets the gender of the model. 0 is female, 1 is male.

        Parameters
        ----------

        amount:
            *float*. An amount, usually between 0 and 1, specifying how much
            of the attribute to apply.
        """

        gender = min(max(gender, 0.0), 1.0)
        if self.gender == gender:
            return
        self.gender = gender
        self._setGenderVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'gender'))

    def getGender(self):
        """
        The gender of this human as a float between 0 and 1.
        0 for completely female, 1 for fully male.
        """
        return self.gender

    def _setGenderVals(self):
        self.maleVal = self.gender
        self.femaleVal = 1 - self.gender

    def setAge(self, age):
        """
        Sets the age of the model. 0 for 0 years old, 1 is 70. To set a
        particular age in years, use the formula age_value = age_in_years / 70.

        Parameters
        ----------

        amount:
            *float*. An amount, usually between 0 and 1, specifying how much
            of the attribute to apply.
        """
        age = min(max(age, 0.0), 1.0)
        if self.age == age:
            return
        self.age = age
        self._setAgeVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'age'))

    def getAge(self):
        """
        Age of this human as a float between 0 and 1.
        """
        return self.age

    def getAgeYears(self):
        """
        Return the approximate age of the human in years.
        """
        if self.getAge() < 0.5:
            return self.MIN_AGE + ((self.MID_AGE - self.MIN_AGE) * 2) * self.getAge()
        else:
            return self.MID_AGE + ((self.MAX_AGE - self.MID_AGE) * 2) * (self.getAge() - 0.5)

    def setAgeYears(self, ageYears):
        """
        Set age in amount of years.
        """
        ageYears = float(ageYears)
        if ageYears < self.MIN_AGE or ageYears > self.MAX_AGE:
            raise RuntimeError("Invalid age specified, should be minimum %s and maximum %s." % (self.MIN_AGE, self.MAX_AGE))
        if ageYears < self.MID_AGE:
            age = (ageYears - self.MIN_AGE) / ((self.MID_AGE - self.MIN_AGE) * 2)
        else:
            age = ( (ageYears - self.MID_AGE) / ((self.MAX_AGE - self.MID_AGE) * 2) ) + 0.5
        self.setAge(age)

    def _setAgeVals(self):
        """
        New system (A8):
        ----------------

        1y       10y       25y            90y
        baby    child     young           old
        |---------|---------|--------------|
        0      0.1875      0.5             1  = age [0, 1]

        val ^     child young     old
          1 |baby\ / \ /   \    /
            |     \   \      /
            |    / \ / \  /    \ young
          0 ______________________________> age
               0  0.1875 0.5      1
        """
        if self.age < 0.5:
            self.oldVal = 0.0
            self.babyVal = max(0.0, 1 - self.age * 5.333)  # 1/0.1875 = 5.333
            self.youngVal = max(0.0, (self.age-0.1875) * 3.2) # 1/(0.5-0.1875) = 3.2
            self.childVal = max(0.0, min(1.0, 5.333 * self.age) - self.youngVal)
        else:
            self.childVal = 0.0
            self.babyVal = 0.0
            self.oldVal = max(0.0, self.age * 2 - 1)
            self.youngVal = 1 - self.oldVal

    def setWeight(self, weight):
        """
        Sets the amount of weight of the model. 0 for underweight, 1 for heavy.

        Parameters
        ----------

        amount:
            *float*. An amount, usually between 0 and 1, specifying how much
            of the attribute to apply.
        """

        weight = min(max(weight, 0.0), 1.0)
        if self.weight == weight:
            return
        self.weight = weight
        self._setWeightVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'weight'))

    def getWeight(self):
        return self.weight

    def _setWeightVals(self):
        self.maxweightVal = max(0.0, self.weight * 2 - 1)
        self.minweightVal = max(0.0, 1 - self.weight * 2)
        self.averageweightVal = 1 - (self.maxweightVal + self.minweightVal)

    def setMuscle(self, muscle):
        """
        Sets the amount of muscle of the model. 0 for flacid, 1 for muscular.

        Parameters
        ----------

        amount:
            *float*. An amount, usually between 0 and 1, specifying how much
            of the attribute to apply.
        """

        muscle = min(max(muscle, 0.0), 1.0)
        if self.muscle == muscle:
            return
        self.muscle = muscle
        self._setMuscleVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'muscle'))

    def getMuscle(self):
        return self.muscle

    def _setMuscleVals(self):
        self.maxmuscleVal = max(0.0, self.muscle * 2 - 1)
        self.minmuscleVal = max(0.0, 1 - self.muscle * 2)
        self.averagemuscleVal = 1 - (self.maxmuscleVal + self.minmuscleVal)

    def setHeight(self, height):
        height = min(max(height, 0.0), 1.0)
        if self.height == height:
            return
        self.height = height
        self._setHeightVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'height'))

    def getHeight(self):
        return self.height

    def getHeightCm(self):
        """
        The height in cm.
        """
        bBox = self.mesh.calcBBox()
        return 10*(bBox[1][1]-bBox[0][1])

    def _setHeightVals(self):
        self.dwarfVal = max(0.0, 1 - self.height * 2)
        self.giantVal = max(0.0, self.height * 2 - 1)

    def setBreastSize(self, size):
        size = min(max(size, 0.0), 1.0)
        if self.breastSize == size:
            return
        self.breastSize = size
        self._setBreastSizeVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'breastSize'))

    def getBreastSize(self):
        return self.breastSize

    def _setBreastSizeVals(self):
        self.cup2Val = max(0.0, self.breastSize * 2 - 1)
        self.cup1Val = max(0.0, 1 - self.breastSize * 2)

    def setBreastFirmness(self, firmness):
        firmness = min(max(firmness, 0.0), 1.0)
        if self.breastFirmness == firmness:
            return
        self.breastFirmness = firmness
        self._setBreastFirmnessVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'breastFirmness'))

    def getBreastFirmness(self):
        return self.breastFirmness

    def _setBreastFirmnessVals(self):
        self.firmness1Val = self.breastFirmness
        self.firmness0Val = 1 - self.breastFirmness

    def setCaucasian(self, caucasian, sync=True):
        caucasian = min(max(caucasian, 0.0), 1.0)
        old = 1 - self.caucasianVal
        self.caucasianVal = caucasian
        if not sync:
            return
        new = 1 - self.caucasianVal
        if old < 1e-6:
            self.asianVal = new / 2
            self.africanVal = new / 2
        else:
            self.asianVal *= new / old
            self.africanVal *= new / old
        self.callEvent('onChanging', events3d.HumanEvent(self, 'caucasian'))

    def getCaucasian(self):
        return self.caucasianVal

    def setAfrican(self, african, sync=True):
        african = min(max(african, 0.0), 1.0)
        old = 1 - self.africanVal
        self.africanVal = african
        if not sync:
            return
        new = 1 - self.africanVal
        if old < 1e-6:
            self.caucasianVal = new / 2
            self.asianVal = new / 2
        else:
            self.caucasianVal *= new / old
            self.asianVal *= new / old
        self.callEvent('onChanging', events3d.HumanEvent(self, 'african'))

    def getAfrican(self):
        return self.africanVal

    def setAsian(self, asian, sync=True):
        asian = min(max(asian, 0.0), 1.0)
        old = 1 - self.asianVal
        self.asianVal = asian
        if not sync:
            return
        new = 1 - self.asianVal
        if old < 1e-6:
            self.caucasianVal = new / 2
            self.africanVal = new / 2
        else:
            self.caucasianVal *= new / old
            self.africanVal *= new / old
        self.callEvent('onChanging', events3d.HumanEvent(self, 'asian'))

    def getAsian(self):
        return self.asianVal

    def syncRace(self):
        total = self.caucasianVal + self.asianVal + self.africanVal
        if total < 1e-6:
            self.caucasianVal = self.asianVal = self.africanVal = 1.0/3
        else:
            scale = 1.0 / total
            self.caucasianVal *= scale
            self.asianVal *= scale
            self.africanVal *= scale

    def setDetail(self, name, value):
        if value:
            self.targetsDetailStack[name] = value
        elif name in self.targetsDetailStack:
            del self.targetsDetailStack[name]

    def getDetail(self, name):
        return self.targetsDetailStack.get(name, 0.0)

    def getSymmetryGroup(self, group):
        if group.name.find('l-', 0, 2) != -1:
            return self.mesh.getFaceGroup(group.name.replace('l-', 'r-', 1))
        elif group.name.find('r-', 0, 2) != -1:
            return self.mesh.getFaceGroup(group.name.replace('r-', 'l-', 1))
        else:
            return None

    def getSymmetryPart(self, name):
        if name.find('l-', 0, 2) != -1:
            return name.replace('l-', 'r-', 1)
        elif name.find('r-', 0, 2) != -1:
            return name.replace('r-', 'l-', 1)
        else:
            return None

    def applyAllTargets(self, progressCallback=None, update=True):
        """
        This method applies all targets, in function of age and sex

        **Parameters:** None.

        """
        algos3d.resetObj(self.meshData)

        if progressCallback:
            progressCallback(0.0)
        progressVal = 0.0
        progressIncr = 0.5 / (len(self.targetsDetailStack) + 1)

        for (targetPath, morphFactor) in self.targetsDetailStack.iteritems():
            algos3d.loadTranslationTarget(self.meshData, targetPath, morphFactor, None, 0, 0)

            progressVal += progressIncr
            if progressCallback:
                progressCallback(progressVal)


        # Update all verts
        self.getSeedMesh().update()
        self.updateProxyMesh()
        if self.isSubdivided():
            self.updateSubdivisionMesh()
            if progressCallback:
                progressCallback(0.7)
            self.mesh.calcNormals()
            if progressCallback:
                progressCallback(0.8)
            if update:
                self.mesh.update()
        else:
            self.meshData.calcNormals(1, 1)
            if progressCallback:
                progressCallback(0.8)
            if update:
                self.meshData.update()

        if progressCallback:
            progressCallback(1.0)

        self.traceStacks(all=False, vertsToList=10)

        self.callEvent('onChanged', events3d.HumanEvent(self, 'targets'))


    def getPartNameForGroupName(self, groupName):
        for k in self.bodyZones:
            if k in groupName:
                return k
        return None

    def applySymmetryLeft(self):
        """
        This method applies right to left symmetry to the currently selected
        body parts.

        **Parameters:** None.

        """

        self.symmetrize('l')

    def applySymmetryRight(self):
        """
        This method applies left to right symmetry to the currently selected
        body parts.

        **Parameters:** None.

        """

        self.symmetrize('r')

    def symmetrize(self, direction='r'):
        """
        This method applies either left to right or right to left symmetry to
        the currently selected body parts.


        Parameters
        ----------

        direction:
            *string*. A string indicating whether to apply left to right
            symmetry (\"r\") or right to left symmetry (\"l\").

        """

        if direction == 'l':
            prefix1 = 'l-'
            prefix2 = 'r-'
        else:
            prefix1 = 'r-'
            prefix2 = 'l-'

        # Remove current values

        for target in self.targetsDetailStack.keys():
            targetName = os.path.basename(target)

            # Reset previous targets on symm side

            if targetName[:2] == prefix2:
                targetVal = self.targetsDetailStack[target]
                algos3d.loadTranslationTarget(self.meshData, target, -targetVal, None, 1, 0)
                del self.targetsDetailStack[target]

        # Apply symm target. For horiz movement the value must be inverted

        for target in self.targetsDetailStack.keys():
            targetName = os.path.basename(target)
            if targetName[:2] == prefix1:
                targetSym = os.path.join(os.path.dirname(target), prefix2 + targetName[2:])
                targetSymVal = self.targetsDetailStack[target]
                if 'trans-in' in targetSym:
                    targetSym = targetSym.replace('trans-in', 'trans-out')
                elif 'trans-out' in targetSym:
                    targetSym = targetSym.replace('trans-out', 'trans-in')
                algos3d.loadTranslationTarget(self.meshData, targetSym, targetSymVal, None, 1, 1)
                self.targetsDetailStack[targetSym] = targetSymVal

        self.updateProxyMesh()
        if self.isSubdivided():
            self.getSubdivisionMesh()

    def setDefaultValues(self):
        self.age = 0.5
        self.gender = 0.5
        self.weight = 0.5
        self.muscle = 0.5
        self.height = 0.5
        self.breastSize = 0.5
        self.breastFirmness = 0.5

        self._setGenderVals()
        self._setAgeVals()
        self._setWeightVals()
        self._setMuscleVals()
        self._setHeightVals()
        self._setBreastSizeVals()
        self._setBreastFirmnessVals()

        self.caucasianVal = 1.0/3
        self.asianVal = 1.0/3
        self.africanVal = 1.0/3

    def resetMeshValues(self):
        self.setDefaultValues()

        self.targetsDetailStack = {}

        self.setMaterial(self._defaultMaterial)

        self.callEvent('onChanging', events3d.HumanEvent(self, 'reset'))
        self.callEvent('onChanged', events3d.HumanEvent(self, 'reset'))

    def getMaterial(self):
        return super(Human, self).getMaterial()

    def setMaterial(self, mat):
        self.callEvent('onChanging', events3d.HumanEvent(self, 'material'))
        super(Human, self).setMaterial(mat)
        self.callEvent('onChanged', events3d.HumanEvent(self, 'material'))

    material = property(getMaterial, setMaterial)

    def load(self, filename, update=True, progressCallback=None):

        self.resetMeshValues()

        f = open(filename, 'r')

        for data in f.readlines():
            lineData = data.split()

            if len(lineData) > 0 and not lineData[0] == '#':
                if lineData[0] == 'version':
                    log.message('Version %s', lineData[1])
                elif lineData[0] == 'tags':
                    for tag in lineData:
                        log.message('Tag %s', tag)
                elif lineData[0] in G.app.loadHandlers:
                    G.app.loadHandlers[lineData[0]](self, lineData)
                else:
                    log.message('Could not load %s', lineData)

        f.close()

        self.syncRace()

        self.callEvent('onChanged', events3d.HumanEvent(self, 'load'))

        if update:
            self.applyAllTargets(progressCallback)

    def save(self, filename, tags):

        f = open(filename, 'w')
        f.write('# Written by MakeHuman %s\n' % getVersionStr())
        f.write('version %s\n' % getShortVersion())
        f.write('tags %s\n' % tags)

        for handler in G.app.saveHandlers:
            handler(self, f)

        f.close()

