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

Master bone
"""

from .flags import *
from .rig_joints import *

Joints = []

HeadsTails = {
    'master' :              ('ground', ('ground', (0,0,-1))),
    'root' :                (('spine-4', (0,-1,0)), 'spine-4'),    
}

Armature = {
    'master' :              (0, None, F_WIR, L_MAIN),
    'root' :                (0, 'master', F_WIR, L_MAIN+L_UPSPNFK),
}

CustomShapes = {
    'master' :          'GZM_Root',
    'root' :            'GZM_Crown',
}
