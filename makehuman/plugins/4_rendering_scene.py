#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           ...none yet

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Scene library.
"""

import gui3d
import filechooser as fc

import os
import shutil
import mh
import scene

class SceneLibraryTaskView(gui3d.PoseModeTaskView):
    def __init__(self, category):
        gui3d.PoseModeTaskView.__init__(self, category, 'Scene')
        self.scene = scene.Scene()

        sceneDir = mh.getPath('scenes')
        if not os.path.exists(sceneDir):
            os.makedirs(sceneDir)
        self.currentScene = os.path.join(sceneDir, "Default.mhscene")
        if os.path.exists(self.currentScene):
            self.scene.load(self.currentScene)
        else:
            self.scene.save(self.currentScene)
        if not os.path.exists(os.path.join(sceneDir, "notfound.thumb")):
            shutil.copy(os.path.normpath(mh.getSysDataPath("uvs/notfound.thumb")), sceneDir)
        self.filechooser = self.addRightWidget( \
        fc.IconListFileChooser(sceneDir , 'mhscene', ['thumb', 'png'], 'notfound.thumb', 'Scene'))
        self.addLeftWidget(self.filechooser.createSortBox())
        self.filechooser.enableAutoRefresh(False)

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            self.currentScene = filename
            self.scene.load(filename)

    def onShow(self, event):
        gui3d.PoseModeTaskView.onShow(self, event)
        self.filechooser.refresh()
        self.filechooser.setHighlightedItem(self.currentScene)
        self.filechooser.setFocus()


def load(app):
    category = app.getCategory('Rendering')
    taskview = SceneLibraryTaskView(category)
    taskview.sortOrder = 1.0
    category.addTask(taskview)

def unload(app):
    pass
