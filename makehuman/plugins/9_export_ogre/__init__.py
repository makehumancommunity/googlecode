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

Exporter plugin for the Ogre3d mesh format.
"""

import gui
from export import Exporter
from exportutils.config import Config

class OgreConfig(Config):

    def __init__(self, exporter):
        Config.__init__(self)
        self.selectedOptions(exporter)
        self.useRelPaths = True
    

class ExporterOgre(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Ogre3D"
        self.filter = "Ogre3D Mesh XML (*.mesh.xml)"

    def export(self, human, filename):
        import mh2ogre
        mh2ogre.exportOgreMesh(human, filename("mesh.xml"), OgreConfig(self))

    def build(self, options, taskview):
        self.taskview       = taskview
        self.useTexFolder   = options.addWidget(gui.CheckBox("Separate texture folder", True))
        self.eyebrows       = options.addWidget(gui.CheckBox("Eyebrows", True))
        self.lashes         = options.addWidget(gui.CheckBox("Eyelashes", True))
        self.helpers        = options.addWidget(gui.CheckBox("Helper geometry", False))
        self.hidden         = False
        self.smooth         = False
        #self.scales         = self.addScales(options)

def load(app):
    app.addExporter(ExporterOgre())

def unload(app):
    pass
