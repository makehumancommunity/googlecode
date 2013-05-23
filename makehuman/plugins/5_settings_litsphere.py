#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import filechooser as fc
import mh
import gui3d
import os
import gui
import log
import shader
import image
import image_operations

class LitSphereTextureChooserTaskView(gui3d.TaskView):
    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'LitSphere material')

        self.human = gui3d.app.selectedHuman

        self.extensions = ['png', 'tif', 'tiff', 'jpg', 'jpeg', 'bmp']

        self.skinCache = { 'caucasian' : image.Image('data/litspheres/skinmat_caucasian.png'),
                           'african'   : image.Image('data/litspheres/skinmat_african.png'),
                           'asian'    : image.Image('data/litspheres/skinmat_asian.png') }

        self.sysPath = 'data/litspheres'
        self.userPath = os.path.join(mh.getPath(''), 'data', 'litspheres')
        if not os.path.exists(self.userPath):
            os.makedirs(self.userPath)
        self.paths = [self.userPath, self.sysPath]

        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.paths, self.extensions, None, None, 'LitSphere texture'))
        self.filechooser.setIconSize(50,50)
        self.addLeftWidget(self.filechooser.createSortBox())

        settingsBox = self.addLeftWidget(gui.GroupBox("Shader settings"))
        self.diffuseChk = settingsBox.addWidget(gui.CheckBox("Diffuse texture", False))

        @self.diffuseChk.mhEvent
        def onClicked(event):
            if self.diffuseChk.selected:
                self.human.mesh.addShaderDefine('DIFFUSE')
            else:
                self.human.mesh.removeShaderDefine('DIFFUSE')

        previewBox = self.addLeftWidget(gui.GroupBox("LitSphere texture"))
        self.image = previewBox.addWidget(gui.ImageView())

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            if os.path.samefile(filename, "data/litspheres/adaptive_skin_tone.png"):
                self.updateAdaptiveSkin()
            else:
                self.human.setShaderParameter("litsphereTexture", filename)
                self.image.setImage(filename)

    def onShow(self, event):
        if "litsphereTexture" in self.human.meshData.shaderParameters:
            current = self.human.meshData.shaderParameters["litsphereTexture"]
            if isinstance(current, image.Image):
                current = "data/litspheres/adaptive_skin_tone.png"
            self.filechooser.selectItem(os.path.relpath(current))
            self.image.setImage(current)
        self.diffuseChk.setChecked("DIFFUSE" in self.human.mesh.shaderDefines)

    def onHumanChanging(self, event):
        if "litsphereTexture" not in self.human.meshData.shaderParameters:
            return
        current = self.human.meshData.shaderParameters["litsphereTexture"]
        if isinstance(current, image.Image) or os.path.samefile(current, "data/litspheres/adaptive_skin_tone.png"):
            if event.change == "caucasian" or event.change == "african" or \
              event.change == "asian":
                self.updateAdaptiveSkin()

    def updateAdaptiveSkin(self):
        img = self.getEthnicityBlendMaterial()
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
            return self.skinCache[blends[0][0]]
        else:
            img = image_operations.mix(self.skinCache[blends[0][0]], self.skinCache[blends[1][0]], blends[0][1], blends[1][1])
            if len(blends) > 2:
                img = image_operations.mix(img, self.skinCache[blends[2][0]], 1.0, blends[2][1])
            return img

def load(app):
    category = app.getCategory('Settings')
    taskview = LitSphereTextureChooserTaskView(category)
    taskview.sortOrder = 10
    category.addTask(taskview)

    # Set default litsphere mat at startup
    taskview.updateAdaptiveSkin()

def unload(app):
    pass

