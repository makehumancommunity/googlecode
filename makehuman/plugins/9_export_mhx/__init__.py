#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import gui
from export import Exporter
from exportutils.config import Config


class MhxConfig(Config):

    def __init__(self, exporter):
        from armature.options import ArmatureOptions

        Config.__init__(self)
        self.selectedOptions(exporter)

        self.useTexFolder =         exporter.useTexFolder.selected
        self.scale,self.unit =      exporter.taskview.getScale()
        self.useRelPaths =          True
        self.helpers =              True
        self.encoding =             exporter.taskview.getEncoding()

        self.feetOnGround =         exporter.feetOnGround.selected
        self.useMasks =             exporter.masks.selected
        self.expressions =          exporter.expressions.selected
        self.bodyShapes =           False # exporter.bodyShapes.selected
        self.useCustomTargets =     exporter.useCustomTargets.selected

        self.rigOptions =           exporter.getRigOptions()
        if not self.rigOptions:
            self.rigOptions = ArmatureOptions()
        self.rigOptions.setExportOptions(
            useCustomShapes = True,
            useCorrectives = self.bodyShapes,
            useExpressions = self.expressions,
            feetOnGround = self.feetOnGround,
            useMasks = self.useMasks,
        )


class ExporterMHX(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Blender exchange (mhx)"
        self.filter = "Blender Exchange (*.mhx)"


    def build(self, options, taskview):
        Exporter.build(self, options, taskview)
        #self.taskview       = taskview
        #self.useTexFolder   = options.addWidget(gui.CheckBox("Separate folder", True))

        self.feetOnGround   = options.addWidget(gui.CheckBox("Feet on ground", True))
        self.expressions    = options.addWidget(gui.CheckBox("Expressions", False))
        # self.facepanel      = options.addWidget(gui.CheckBox("Face rig", False))
        # self.bodyShapes     = options.addWidget(gui.CheckBox("Body shapes", False))
        self.useCustomTargets = options.addWidget(gui.CheckBox("Custom targets", False))
        self.masks          = options.addWidget(gui.CheckBox("Clothes masks", False))
        #self.clothesRig     = options.addWidget(gui.CheckBox("Clothes rig", False))
        #self.cage           = options.addWidget(gui.CheckBox("Cage", False))
        #self.advancedSpine  = options.addWidget(gui.CheckBox("Advanced spine", False))
        #self.maleRig        = options.addWidget(gui.CheckBox("Male rig", False))


    def export(self, human, filename):
        from . import mhx_main
        #from mhx import mhx_main
        mhx_main.exportMhx(human, filename("mhx"), MhxConfig(self))


def load(app):
    app.addExporter(ExporterMHX())

def unload(app):
    pass
