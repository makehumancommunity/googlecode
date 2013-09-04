#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier, Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Material library plugin.

"""

__docformat__ = 'restructuredtext'

import material
import os
import gui3d
import mh
import download
import gui
import filechooser as fc
from humanobjchooser import HumanObjectSelector
import log
from getpath import isSubPath

class MaterialAction(gui3d.Action):
    def __init__(self, obj, after):
        super(MaterialAction, self).__init__("Change material of %s" % obj.mesh.name)
        self.obj = obj
        self.before = material.Material().copyFrom(obj.material)
        self.after = after

    def do(self):
        self.obj.material = self.after
        return True

    def undo(self):
        self.obj.material = self.before
        return True


class MaterialTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Material', label='Skin/Material')
        self.human = gui3d.app.selectedHuman

        self.skinBlender = EthnicSkinBlender(self.human)

        # Paths, in order, in which relative material filepaths will be searched
        self.searchPaths = [mh.getPath(''), mh.getSysDataPath()]
        self.searchPaths = [os.path.abspath(p) for p in self.searchPaths]

        self.systemSkins = mh.getSysDataPath('skins')
        self.systemClothes = os.path.join(mh.getSysDataPath('clothes'), 'materials')
        self.systemHair = mh.getSysDataPath('hairstyles')
        self.systemEyes = mh.getSysDataPath('eyes')
        self.systemGenitals = mh.getSysDataPath('genitals')

        self.userSkins = os.path.join(mh.getPath(''), 'data', 'skins')
        self.userClothes = os.path.join(mh.getPath(''), 'data', 'clothes', 'materials')
        self.userHair = os.path.join(mh.getPath(''), 'data', 'hairstyles')
        self.userEyes = os.path.join(mh.getPath(''), 'data', 'eyes')
        self.userGenitals = os.path.join(mh.getPath(''), 'data', 'genitals')

        for path in (self.userSkins, self.userClothes, self.userEyes):
            if not os.path.exists(path):
                os.makedirs(path)

        self.defaultClothes = [self.systemClothes, self.userClothes]
        self.defaultHair = [self.systemHair, self.userHair]
        self.defaultEyes = [self.systemEyes, self.userEyes]

        self.materials = self.defaultClothes

        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.userSkins, 'mhmat', ['thumb', 'png'], mh.getSysDataPath('skins/notfound.thumb'), 'Material'))
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(False)
        self.filechooser.setFileLoadHandler(fc.MhmatFileLoader())
        self.addLeftWidget(self.filechooser.createSortBox())

        self.update = self.filechooser.sortBox.addWidget(gui.Button('Check for updates'))
        self.mediaSync = None
        self.mediaSync2 = None

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            mat = material.fromFile(filename)
            human = self.human

            obj = self.humanObjSelector.selected
            if obj == 'skin':
                gui3d.app.do(MaterialAction(human,
                    mat))
            elif obj == 'hair':
                gui3d.app.do(MaterialAction(human.hairObj,
                    mat))
            elif obj == 'eyes':
                gui3d.app.do(MaterialAction(human.eyesObj,
                    mat))
            elif obj == 'genitals':
                gui3d.app.do(MaterialAction(human.genitalsObj,
                    mat))
            else: # Clothes
                if obj:
                    uuid = obj
                    gui3d.app.do(MaterialAction(human.clothesObjs[uuid],
                        mat))

        @self.update.mhEvent
        def onClicked(event):
            self.syncMedia()

        self.humanObjSelector = self.addLeftWidget(HumanObjectSelector(self.human))
        @self.humanObjSelector.mhEvent
        def onActivate(value):
            self.reloadMaterialChooser(value)


    def onShow(self, event):

        # When the task gets shown, set the focus to the file chooser
        gui3d.TaskView.onShow(self, event)
        human = self.human

        self.reloadMaterialChooser(self.humanObjSelector.selected)

        # Offer to download skins if none are found
        self.numSkin = len([filename for filename in os.listdir(os.path.join(mh.getPath(''), 'data', 'skins')) if filename.lower().endswith('png')])
        if self.numSkin < 1:
            gui3d.app.prompt('No skins found', 'You don\'t seem to have any skins, download them from the makehuman media repository?\nNote: this can take some time depending on your connection speed.', 'Yes', 'No', self.syncMedia)


    def applyClothesMaterial(self, uuid, filename):
        human = self.human
        if uuid not in human.clothesObjs.keys():
            log.warning("Cannot set material for clothes with UUID %s, no such item", uuid)
            return False
        clo = human.clothesObjs[uuid]
        clo.mesh.material = material.fromFile(filename)
        return True

    def getClothesMaterial(self, uuid):
        """
        Get the currently set material for clothing item with specified UUID.
        """
        human = self.human
        if uuid not in human.clothesObjs.keys():
            return None
        clo = human.clothesObjs[uuid]
        return clo.material.filename

    def reloadMaterialChooser(self, obj):
        human = self.human
        selectedMat = None

        if obj == 'skin':
            self.materials = [self.systemSkins, self.userSkins]
            selectedMat = human.material.filename
        elif obj == 'hair':
            proxy = human.hairProxy
            if proxy:
                self.materials = [os.path.dirname(proxy.file)] + self.defaultHair
            else:
                self.materials = self.defaultHair
            selectedMat = human.hairObj.material.filename
        elif obj == 'eyes':
            proxy = human.eyesProxy
            if proxy:
                self.materials = [os.path.dirname(proxy.file)] + self.defaultEyes
            else:
                self.materials = self.defaultEyes
            selectedMat = human.eyesObj.material.filename
        elif obj == 'genitals':
            proxy = human.genitalsProxy
            if proxy:
                self.materials = [os.path.dirname(proxy.file)] + self.defaultGenitals
            else:
                self.materials = self.defaultGenitals
            selectedMat = human.genitalsObj.material.filename
        else: # Clothes
            if obj:
                uuid = obj
                clo = human.clothesObjs[uuid]
                filepath = human.clothesProxies[uuid].file
                self.materials = [os.path.dirname(filepath)] + self.defaultClothes
                selectedMat = clo.material.filename
            else:
                # TODO maybe dont show anything?
                self.materials = self.defaultClothes

                filec = self.filechooser
                log.debug("fc %s %s %s added", filec, filec.children.count(), str(filec.files))

        # Reload filechooser
        self.filechooser.deselectAll()
        self.filechooser.setPaths(self.materials)
        self.filechooser.refresh()
        if selectedMat:
            self.filechooser.setHighlightedItem(selectedMat)
        self.filechooser.setFocus()

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

    def onHumanChanging(self, event):
        self.skinBlender.onSkinUpdateEvent(event)

    def onHumanChanged(self, event):
        self.skinBlender.onSkinUpdateEvent(event)

    def loadHandler(self, human, values):

        if values[0] == 'skinMaterial':
            path = values[1]
            if os.path.isfile(path):
                mat = material.fromFile(path)
                human.material = mat
                return
            else:
                for d in [self.systemSkins, self.userSkins]:
                    absP = os.path.join(d, path)
                    if os.path.isfile(absP):
                        mat = material.fromFile(path)
                        human.material = mat
                        return
            log.warning('Could not find material %s for skinMaterial parameter.', values[1])
        elif values[0] == 'material':
            uuid = values[1]
            filepath = values[2]

            if human.hairProxy and human.hairProxy.getUuid() == uuid:
                proxy = human.hairProxy
                filepath = self.getMaterialPath(filepath, proxy.file)
                human.hairObj.material = material.fromFile(filepath)
                return
            elif human.eyesProxy and human.eyesProxy.getUuid() == uuid:
                proxy = human.eyesProxy
                filepath = self.getMaterialPath(filepath, proxy.file)
                human.eyesObj.material = material.fromFile(filepath)
                return
            elif human.genitalsProxy and human.genitalsProxy.getUuid() == uuid:
                proxy = human.genitalsProxy
                filepath = self.getMaterialPath(filepath, proxy.file)
                human.genitalsObj.material = material.fromFile(filepath)
                return
            elif not uuid in human.clothesProxies.keys():
                log.error("Could not load material for object with uuid %s!" % uuid)
                return

            proxy = human.clothesProxies[uuid]
            proxy = human.clothesProxies[uuid]
            filepath = self.getMaterialPath(filepath, proxy.file)
            self.applyClothesMaterial(uuid, filepath)
            return

    def getRelativeMaterialPath(self, filepath, objFile = None):
        """
        Produce a portable path for writing to file.
        """
        _originalPath = filepath
        filepath = os.path.abspath(filepath)
        if objFile:
            objFile = os.path.abspath(objFile)
            if os.path.isdir(objFile):
                objFile = os.path.dirname(objFile)[0]
            searchPaths = [ objFile ] + self.searchPaths
        else:
            searchPaths = self.searchPaths

        for dataPath in searchPaths:
            if isSubPath(filepath, dataPath):
                return os.path.relpath(filepath, dataPath).replace('\\', '/')

        return _originalPath.replace('\\', '/')

    def getMaterialPath(self, relPath, objFile = None):
        if objFile:
            objFile = os.path.abspath(objFile)
            if os.path.isdir(objFile):
                objFile = os.path.split(objFile)[0]
            searchPaths = [ objFile ] + self.searchPaths
        else:
            searchPaths = self.searchPaths

        for dataPath in searchPaths:
            path = os.path.join(dataPath, relPath)
            if os.path.isfile(path):
                return path

        return relPath

    def saveHandler(self, human, file):

        file.write('skinMaterial %s\n' % self.getRelativeMaterialPath(human.material.filename))
        for name, clo in human.clothesObjs.items():
            if clo:
                proxy = human.clothesProxies[name]
                if clo.material.filename !=  proxy.material.filename:
                    materialPath = self.getRelativeMaterialPath(clo.material.filename, proxy.file)
                    file.write('material %s %s\n' % (proxy.getUuid(), materialPath))
        if human.hairObj and human.hairProxy:
            proxy = human.hairProxy
            hairObj = human.hairObj
            materialPath = self.getRelativeMaterialPath(hairObj.material.filename, proxy.file)
            file.write('material %s %s\n' % (proxy.getUuid(), materialPath))
        if human.eyesObj and human.eyesProxy:
            proxy = human.eyesProxy
            eyesObj = human.eyesObj
            materialPath = self.getRelativeMaterialPath(eyesObj.material.filename, proxy.file)
            file.write('material %s %s\n' % (proxy.getUuid(), materialPath))
        if human.genitalsObj and human.genitalsProxy:
            proxy = human.genitalsProxy
            genitalsObj = human.genitalsObj
            materialPath = self.getRelativeMaterialPath(genitalsObj.material.filename, proxy.file)
            file.write('material %s %s\n' % (proxy.getUuid(), materialPath))

    def syncMedia(self):

        if self.mediaSync:
            return
        if not os.path.isdir(self.userSkins):
            os.makedirs(self.userSkins)
        self.mediaSync = download.MediaSync(gui3d.app, self.userSkins, 'http://download.tuxfamily.org/makehuman/skins/', self.syncMediaFinished)
        self.mediaSync.start()
        self.mediaSync2 = None

    def syncMediaFinished(self):
        '''
        if not self.mediaSync2:
            if not os.path.isdir(self.userClothes):
                os.makedirs(self.userClothes)
            self.mediaSync2 = download.MediaSync(gui3d.app, self.userClothes, 'http://download.tuxfamily.org/makehuman/clothes/textures/', self.syncMediaFinished)
            self.mediaSync2.start()
            self.mediaSync = None
        else:
            self.mediaSync = None
            self.filechooser.refresh()
        '''

        self.mediaSync = None
        self.filechooser.refresh()

import image
import image_operations
class EthnicSkinBlender(object):
    # TODO move this someplace else (in Human maybe?) In the future we probably want a more generic mechanism for blending textures

    def __init__(self, human):
        self.human = human
        self.skinCache = { 'caucasian' : image.Image(mh.getSysDataPath('litspheres/skinmat_caucasian.png')),
                           'african'   : image.Image(mh.getSysDataPath('litspheres/skinmat_african.png')),
                           'asian'    : image.Image(mh.getSysDataPath('litspheres/skinmat_asian.png')) }

    def onSkinUpdateEvent(self, event):
        if "litsphereTexture" not in self.human.meshData.shaderParameters:
            return

        current = self.human.meshData.shaderParameters["litsphereTexture"]
        if current and (isinstance(current, image.Image) or \
           os.path.realpath(current) == os.path.realpath(mh.getSysDataPath("litspheres/adaptive_skin_tone.png"))):
            if event.change == "caucasian" or event.change == "african" or \
              event.change == "asian" or event.change == "material":
                self.updateAdaptiveSkin()

    def updateAdaptiveSkin(self):
        img = self.getEthnicityBlendMaterial()
        # Set parameter so the image can be referenced when material is written to file
        img.sourcePath = mh.getSysDataPath("litspheres/adaptive_skin_tone.png")
        self.human.setShaderParameter("litsphereTexture", img)

    def getEthnicityBlendMaterial(self):
        caucasianWeight = self.human.getCaucasian()
        africanWeight   = self.human.getAfrican()
        asianWeight     = self.human.getAsian()
        blends = []

        if caucasianWeight > 0:
            blends.append( ('caucasian', caucasianWeight) )
        if africanWeight > 0:
            blends.append( ('african', africanWeight) )
        if asianWeight > 0:
            blends.append( ('asian', asianWeight) )

        if len(blends) == 1:
            img = self.skinCache[blends[0][0]]
            img.markModified()
            return img
        else:
            img = image_operations.mix(self.skinCache[blends[0][0]], self.skinCache[blends[1][0]], blends[0][1], blends[1][1])
            if len(blends) > 2:
                img = image_operations.mix(img, self.skinCache[blends[2][0]], 1.0, blends[2][1])
            return img



# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Materials')
    taskview = MaterialTaskView(category)
    taskview.sortOrder = 0
    category.addTask(taskview)

    app.addLoadHandler('material', taskview.loadHandler)
    app.addLoadHandler('skinMaterial', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass
