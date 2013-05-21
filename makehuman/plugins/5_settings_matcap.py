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

class MatcapTextureChooserTaskView(gui3d.TaskView):
    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Matcap')

        self.human = gui3d.app.selectedHuman

        self.sysPath = 'data/matcaps'
        self.userPath = os.path.join(mh.getPath(''), 'data', 'matcaps')
        if not os.path.exists(self.userPath):
            os.makedirs(self.userPath)
        self.paths = [self.userPath, self.sysPath]

        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.paths, 'png', ['thumb', 'png'], None, 'MatCap texture'))
        self.filechooser.setIconSize(50,50)
        self.addLeftWidget(self.filechooser.createSortBox())

        previewBox = self.addLeftWidget(gui.GroupBox("MatCap texture"))
        self.image = previewBox.addWidget(gui.ImageView())

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            self.human.mesh.setShaderParameter("matcapTexture", filename)
            self.image.setImage(filename)

    def onShow(self, event):
        if "matcapTexture" in self.human.meshData.shaderParameters:
            current = self.human.meshData.shaderParameters["matcapTexture"]
            self.filechooser.selectItem(os.path.relpath(current))
            self.image.setImage(current)

def load(app):
    category = app.getCategory('Settings')
    taskview = MatcapTextureChooserTaskView(category)
    taskview.sortOrder = 10
    category.addTask(taskview)

def unload(app):
    pass

