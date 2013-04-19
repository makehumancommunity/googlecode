#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

BVH exporter.
Supports exporting of selected skeleton and animations in BVH format.
"""

import mh2bvh    # TODO move most of this module into shared/bvh.py

from export import Exporter
from exportutils.config import Config
import gui
import gui3d
import log

import os

# TODO add options such as scale and z-up, feetonground, etc

class BvhConfig(Config):

    def __init__(self, exporter):
        Config.__init__(self)
        self.selectedOptions(exporter)
        self.useRelPaths = True
    
class ExporterBVH(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.group = "rig"
        self.name = "Biovision Hierarchy BVH"
        self.filter = "Biovision Hierarchy (*.bvh)"

    def build(self, options, taskview):
        self.taskview       = taskview
        self.exportAnimations = options.addWidget(gui.CheckBox("Animations", True))

    def export(self, human, filename):
        if not human.getSkeleton():
            gui3d.app.prompt('Error', 'You did not select a skeleton from the library.', 'OK')
            return

        if self.exportAnimations and len(human.animated.getAnimations()) > 0:
            baseFilename = os.path.splitext(filename("bvh"))[0]
            for animName in human.animated.getAnimations():
                fn = baseFilename + "_%s.bvh" % animName
                log.message("Exporting file %s.", fn)
                mh2bvh.exportSkeleton(fn, False)
                mh2bvh.exportAnimation(fn, animName)
        else:
            fn = filename("bvh")
            log.message("Exporting file %s.", fn)
            mh2bvh.exportSkeleton(fn, True)

    def onShow(self, exportTaskView):
        exportTaskView.encodingBox.hide()
        exportTaskView.scaleBox.hide()

    def onHide(self, exportTaskView):
        exportTaskView.encodingBox.show()
        exportTaskView.scaleBox.show()

def load(app):
    app.addExporter(ExporterBVH())

def unload(app):
    pass
