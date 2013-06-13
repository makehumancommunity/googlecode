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

import os
import gui3d
import mh
import mh2proxy
import filechooser as fc
import log
import numpy as np

class UVMapAction(gui3d.Action):
    def __init__(self, name, human, before, after):
        super(UVMapAction, self).__init__(name)
        self.human = human
        self.before = before
        self.after = after

    def do(self):
        self.human.setUVMap(self.after)
        gui3d.app.redraw()
        return True

    def undo(self):
        self.human.setUVMap(self.before)
        gui3d.app.redraw()
        return True


class UvTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'UV')
        uvDir = os.path.join(mh.getPath(''), 'data', 'uvs')
        if not os.path.exists(uvDir):
            os.makedirs(uvDir)
        self.filechooser = self.addRightWidget( \
        fc.IconListFileChooser([uvDir , 'data/uvs'], 'mhuv', ['thumb', 'png'], 'data/uvs/notfound.thumb', 'UV Map'))
        self.addLeftWidget(self.filechooser.createSortBox())

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            if os.path.basename(filename) == "default.mhuv":
                filename = None
            gui3d.app.do(UVMapAction("Changing UV map",
                                     gui3d.app.selectedHuman,
                                     gui3d.app.selectedHuman.mesh.material.uvMap,
                                     filename))

    def onShow(self, event):
        # When the task gets shown, set the focus to the file chooser
        gui3d.TaskView.onShow(self, event)
        self.filechooser.setFocus()

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)
        
    def onHumanChanging(self, event):
        human = event.human
        #if event.change == 'reset':
        #    human.setUVMap(None)
        #    gui3d.app.redraw()
            
    def onHumanChanged(self, event):
        human = event.human

    def loadHandler(self, human, values):
        mhuv = values[1]
        if not os.path.exists(os.path.realpath(mhuv)):
            log.notice('UvTaskView.loadHandler: %s does not exist. Skipping.', mhuv)
            return
        human.setUVMap(mhuv)
        gui3d.app.redraw()
        
    def saveHandler(self, human, file):
        if human.uvset:
            file.write('uvset %s\n' % human.uvset.filename)

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    #return  # Disabled, UVs will not be chosen explicitly in the future
    category = app.getCategory('Textures')
    taskview = UvTaskView(category)
    taskview.sortOrder = 9
    category.addTask(taskview)

    app.addLoadHandler('uvset', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass

