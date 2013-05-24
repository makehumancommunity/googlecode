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

import armature
from armature import basic
from . import mhx_armature


class BasicArmature(mhx_armature.ExportArmature, basic.BasicArmature):

    def __init__(self, name, human, config):   
        import gizmos_general
        
        mhx_armature.ExportArmature. __init__(self, name, human, config)
        basic.BasicArmature. __init__(self, name, human, config)
        self.gizmos = gizmos_general.asString()
        
    
    def createBones(self, bones):
        basic.BasicArmature.createBones(self, bones)
        mhx_armature.ExportArmature.createBones(self, bones)
            

    def writeDrivers(self, fp):
        rig_face.DeformDrivers(fp, self)        
        mhx_drivers.writePropDrivers(fp, self, rig_face.PropDrivers, "", "Mha")
        mhx_drivers.writePropDrivers(fp, self, rig_face.SoftPropDrivers, "", "Mha")
        return []

