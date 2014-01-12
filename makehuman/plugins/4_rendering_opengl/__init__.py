#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Internal OpenGL Renderer Plugin.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

from . import mh2opengl

import os
import gui3d
import gui
import guipose
import mh

class OpenGLTaskView(guipose.PoseModeTaskView):

    def __init__(self, category):
        guipose.PoseModeTaskView.__init__(self, category, 'Internal')

        settingsBox = self.addLeftWidget(gui.GroupBox('Settings'))
        settingsBox.addWidget(gui.TextView("Resolution"))
        self.resBox = settingsBox.addWidget(gui.TextEdit(
            "x".join([str(self.resWidth), str(self.resHeight)])))
        self.AAbox = settingsBox.addWidget(gui.ToggleButton("Anti-aliasing"))
        self.AAbox.setSelected( gui3d.app.settings.get('GL_RENDERER_AA', True) )
        self.lightmapSSS = settingsBox.addWidget(gui.CheckBox("Lightmap SSS", False))
        self.renderButton = settingsBox.addWidget(gui.Button('Render'))

        if not mh.hasRenderToRenderbuffer():
            # Can only use screen grabbing as fallback, resolution option disabled
            self.resBox.setEnabled(False)

        @self.resBox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                res = [int(x) for x in value.split("x")]
                self.resWidth = res[0]
                self.resHeight = res[1]
            except: # The user hasn't typed the value correctly yet.
                pass

        @self.AAbox.mhEvent
        def onClicked(value):
            gui3d.app.settings['GL_RENDERER_AA'] = self.AAbox.selected

        @self.renderButton.mhEvent
        def onClicked(event):
            try:
                mhscene = gui3d.app.getCategory('Rendering').getTaskByName('Scene').scene
            except:
                import scene
                mhscene = scene.Scene()

            settings = dict()
            settings['scene'] = mhscene
            settings['AA'] = self.AAbox.selected
            settings['dimensions'] = (self.resWidth, self.resHeight)
            settings['lightmapSSS'] = self.lightmapSSS.selected
            
            reload(mh2opengl)
            mh2opengl.Render(settings)

    @property
    def resWidth(self):
        return gui3d.app.settings.get('rendering_width', 800)

    @property
    def resHeight(self):
        return gui3d.app.settings.get('rendering_height', 600)

    @resWidth.setter
    def resWidth(self, value = None):
        gui3d.app.settings['rendering_width'] = 0 if not value else int(value)

    @resHeight.setter
    def resHeight(self, value = None):
        gui3d.app.settings['rendering_height'] = 0 if not value else int(value)

    def onShow(self, event):
        guipose.PoseModeTaskView.onShow(self, event)
        self.renderButton.setFocus()


def load(app):
    category = app.getCategory('Rendering')
    taskview = OpenGLTaskView(category)
    taskview.sortOrder = 1.3
    category.addTask(taskview)

def unload(app):
    pass

