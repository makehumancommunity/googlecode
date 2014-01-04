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


class DaeConfig(Config):
    def __init__(self, exporter):
        from armature.options import ArmatureOptions

        Config.__init__(self)
        self.selectedOptions(exporter)

        self.useRelPaths = True
        self.useNormals = exporter.useNormals.selected
        self.yup = exporter.yup.selected
        self.zup = exporter.zup.selected
        self.secondlife = exporter.secondlife.selected
        self.expressions     = exporter.expressions.selected
        self.useCustomTargets = exporter.useCustomTargets.selected

        self.rigOptions = exporter.getRigOptions()
        if not self.rigOptions:
            return
            self.rigOptions = ArmatureOptions()
        self.rigOptions.setExportOptions(
            useExpressions = self.expressions,
            useTPose = self.useTPose,
        )



class ExporterCollada(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Collada (dae)"
        self.filter = "Collada (*.dae)"
        self.fileExtension = "dae"

    def build(self, options, taskview):
        Exporter.build(self, options, taskview)
        self.useNormals = options.addWidget(gui.CheckBox("Normals", False))
        self.expressions     = options.addWidget(gui.CheckBox("Expressions", False))
        self.useCustomTargets = options.addWidget(gui.CheckBox("Custom targets", False))

        #orientBox = self.addWidget(gui.GroupBox('Orientation'))
        orients = []
        self.yup = options.addWidget(gui.RadioButton(orients, "Y up, face Z", True))
        self.zup = options.addWidget(gui.RadioButton(orients, "Z up, face -Y", False))
        self.secondlife = options.addWidget(gui.RadioButton(orients, "Second Life (Z up, face X)", False))

    def export(self, human, filename):
        from .mh2collada import exportCollada
        self.taskview.exitPoseMode()
        exportCollada(human, filename("dae"), DaeConfig(self))
        self.taskview.enterPoseMode()


def load(app):
    app.addExporter(ExporterCollada())

def unload(app):
    pass
