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

        basic.BasicParser.__init__(self, amt)
        amt.visibleLayers = "002804aa"



class BasicArmature(ExportArmature):

    def __init__(self, name, human, options):
        ExportArmature.__init__(self, name, human, options)
        self.parser = BasicParser(self)


    def setupCustomShapes(self, fp):
        import gizmos_general
        gizmos = gizmos_general.asString()
        self.writeGizmos(fp, gizmos)


    def writeDrivers(self, fp):
        rig_face.DeformDrivers(fp, self)
        mhx_drivers.writePropDrivers(fp, self, rig_face.PropDrivers, "", "Mha")
        mhx_drivers.writePropDrivers(fp, self, rig_face.SoftPropDrivers, "", "Mha")
        return []

