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

class MatcapTextureChooserTaskView(gui3d.TaskView):
    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Matcap')

        self.human = gui3d.app.selectedHuman

        self.extensions = ['png', 'tif', 'tiff', 'jpg', 'jpeg', 'bmp']

        self.skinCache = { 'caucasian' : image.Image('data/matcaps/skinmat_caucasian.png'),
                           'african'   : image.Image('data/matcaps/skinmat_african.png'),
                           'asian'    : image.Image('data/matcaps/skinmat_asian.png') }

        self.sysPath = 'data/matcaps'
        self.userPath = os.path.join(mh.getPath(''), 'data', 'matcaps')
        if not os.path.exists(self.userPath):
            os.makedirs(self.userPath)
        self.paths = [self.userPath, self.sysPath]

        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.paths, self.extensions, None, None, 'MatCap texture'))
        self.filechooser.setIconSize(50,50)
        self.addLeftWidget(self.filechooser.createSortBox())

        previewBox = self.addLeftWidget(gui.GroupBox("MatCap texture"))
        self.image = previewBox.addWidget(gui.ImageView())

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            self.human.setShaderParameter("matcapTexture", filename)
            self.image.setImage(filename)

    def onShow(self, event):
        if "matcapTexture" in self.human.meshData.shaderParameters:
            current = self.human.meshData.shaderParameters["matcapTexture"]
            self.filechooser.selectItem(os.path.relpath(current))
            self.image.setImage(current)

    def onHumanChanging(self, event):
        if "matcapTexture" not in self.human.meshData.shaderParameters:
            return
        current = self.human.meshData.shaderParameters["matcapTexture"]
        if current == "data/matcaps/skinmat.png" or isinstance(current, image.Image):
            if event.change == "caucasian" or event.change == "african" or \
              event.change == "asian":
                img = self.getEthnicityBlendMaterial()
                self.human.setShaderParameter("matcapTexture", img)

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
    taskview = MatcapTextureChooserTaskView(category)
    taskview.sortOrder = 10
    category.addTask(taskview)

def unload(app):
    pass

