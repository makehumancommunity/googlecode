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

Basic armature
"""

from armature import basic
from . import mhx_armature
from .mhx_armature import ExportArmature


class BasicParser(basic.BasicParser):

    def __init__(self, amt):
        import gizmos_general

        basic.BasicParser.__init__(self, amt)
        self.gizmos = gizmos_general.asString()
        amt.visibleLayers = "002804aa"



class BasicArmature(ExportArmature):

    def __init__(self, name, human, options):
        ExportArmature.__init__(self, name, human, options)
        self.parser = BasicParser(self)


    def setupCustomShapes(self, fp):
        mhx_armature.writeCustomEmpty(fp)
        fp.write(self.parser.gizmos)
        mhx_armature.setupSimpleCustomTargets(fp)
        if self.options.facepanel:
            import gizmos_panel
            setupCube(fp, "MHCube025", 0.25, 0)
            setupCube(fp, "MHCube05", 0.5, 0)
            gizmos = gizmos_panel.asString()
            fp.write(gizmos)


    def writeDrivers(self, fp):
        rig_face.DeformDrivers(fp, self)
        mhx_drivers.writePropDrivers(fp, self, rig_face.PropDrivers, "", "Mha")
        mhx_drivers.writePropDrivers(fp, self, rig_face.SoftPropDrivers, "", "Mha")
        return []

