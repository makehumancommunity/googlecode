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


class Options:
    def __init__(self, rig, exporter):
        self.daerig = rig,
        self.rotate90X = exporter.colladaRot90X.selected
        self.rotate90Z = exporter.colladaRot90Z.selected
        self.eyebrows =  exporter.colladaEyebrows.selected
        self.lashes =    exporter.colladaLashes.selected
        self.helpers =   exporter.colladaHelpers.selected
        self.hidden =    exporter.colladaHidden.selected
        self.scale, self.unit = exporter.getScale(exporter.daeScales)


class ExporterCollada(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Collada (dae)"
        self.filter = "Collada (*.dae)"

    def build(self, options):
        # Collada options
        self.colladaRot90X = options.addWidget(gui.CheckBox("Rotate 90 X", False))
        self.colladaRot90Z = options.addWidget(gui.CheckBox("Rotate 90 Z", False))
        self.colladaEyebrows = options.addWidget(gui.CheckBox("Eyebrows", True))
        self.colladaLashes = options.addWidget(gui.CheckBox("Eyelashes", True))
        self.colladaHelpers = options.addWidget(gui.CheckBox("Helper geometry", False))
        self.colladaHidden = options.addWidget(gui.CheckBox("Keep hidden faces", True))
        # self.colladaSeparateFolder = options.addWidget(gui.CheckBox("Separate folder", False))
        # self.colladaPngTexture = options.addWidget(gui.CheckBox("PNG texture", selected=True))

        self.daeScales = self.addScales(options)
        self.daeRigs = self.addRigs(options)

    def export(self, human, filename):
        import mh2collada

        for (button, rig) in self.daeRigs:
            if button.selected:
                break                

        options = Options(rig, self)
        mh2collada.exportCollada(human, filename("dae"), options)

def load(app):
    app.addExporter(ExporterCollada())

def unload(app):
    pass
