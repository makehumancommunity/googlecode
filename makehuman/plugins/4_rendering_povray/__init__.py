#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Graphical user interface plugin that creates the Povray task view, for
rendering images with pov-ray.
"""

import os
import sys

from . import mh2povray

import gui
import gui3d
import guirender

class PovrayTaskView(guirender.RenderTaskView):

    def __init__(self, category):
        guirender.RenderTaskView.__init__(self, category, 'Povray')

        # for path to PovRay binaries file
        binary = ''

        bintype = []
        pathBox = self.addLeftWidget(gui.GroupBox('Povray  bin  path'))
        # Try to guess where povray might be located. [maybe reading a reg/env key can help?]
        defPovFolder = ''
        if os.name == 'nt':
            defPovFolder = 'C:/Program Files/POV-Ray'
            if not os.path.isdir(defPovFolder):
                defPovFolder = 'C:/Program Files/'
        else:
            defPovFolder = '/usr/local/bin'
        if not os.path.isdir(defPovFolder):
            defPovFolder = ''
        povray_bin = gui3d.app.settings.get('povray_bin', defPovFolder)
        self.path= pathBox.addWidget(gui.TextEdit(str(povray_bin)), 0, 0, 1, 2)
        self.browse = pathBox.addWidget(gui.BrowseButton('dir'), 1, 0, 1, 1)
        self.browse.setPath(povray_bin)
        if sys.platform == 'win32':
            self.browse.setFilter('Executable programs (*.exe);;All files (*.*)')

        if os.name == 'nt':
            if os.environ['PROCESSOR_ARCHITECTURE'] == 'x86':
                self.win32sse2Button = pathBox.addWidget(gui.CheckBox('Use SSE2 bin', True))
        
        @self.path.mhEvent
        def onChange(value):
            gui3d.app.settings['povray_bin'] = 'Enter your path' if not value else str(value)

        @self.browse.mhEvent
        def onClicked(path):
            if os.path.isdir(path):
                gui3d.app.settings['povray_bin'] = path
                self.path.setText(path)

        settingsBox = self.addLeftWidget(gui.GroupBox('Settings'))
        settingsBox.addWidget(gui.TextView("Resolution"))
        self.resBox = settingsBox.addWidget(gui.TextEdit(
            "x".join([str(self.renderingWidth), str(self.renderingHeight)])))
        self.AAbox = settingsBox.addWidget(gui.Slider(value=gui3d.app.settings.get('POV_AA', 0.5), label="AntiAliasing"))

        materialsBox = self.addRightWidget(gui.GroupBox('Materials'))
        self.moist = materialsBox.addWidget(gui.Slider(value=0.7, label="Moisturization"))

        self.renderButton = settingsBox.addWidget(gui.Button('Render'))

        @self.resBox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                res = [int(x) for x in value.split("x")]
                self.renderingWidth = res[0]
                self.renderingHeight = res[1]
            except: # The user hasn't typed the value correctly yet.
                pass

        @self.AAbox.mhEvent
        def onChange(value):
            gui3d.app.settings['POV_AA'] = value

        #
        @self.renderButton.mhEvent
        def onClicked(event):
            reload(mh2povray)  # Avoid having to close and reopen MH for every coding change (can be removed once testing is complete)
            # it is necessary to put this code here, so that it is executed with the 'renderButton.event'
            if os.name == 'nt':
                #
                if os.environ['PROCESSOR_ARCHITECTURE'] == "x86":
                    binary = 'win32'
                    if self.win32sse2Button.selected:
                        binary = 'win32sse2'
                else:
                    binary = 'win64'
            # for Ubuntu.. atm
            if sys.platform == 'linux2':
                binary = 'linux'

            settings = dict()
            settings['scene'] = self.getScene()
            settings['subdivide'] = gui3d.app.actions.smooth.isChecked()
            settings['AA'] = 0.5-0.49*self.AAbox.getValue()
            settings['bintype'] = binary
            settings['moist'] = self.moist.getValue()
            
            mh2povray.povrayExport(settings)

    def onShow(self, event):
        guirender.RenderTaskView.onShow(self, event)
        self.renderButton.setFocus()


def load(app):
    pass
    # Development of povray plugin halted for now.
'''
    category = app.getCategory('Rendering')
    taskview = PovrayTaskView(category)
    taskview.sortOrder = 2.0
    category.addTask(taskview)
'''

def unload(app):
    pass
