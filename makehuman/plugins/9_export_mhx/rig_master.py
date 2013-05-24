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

Hip bones for basic and mhx rigs
"""

import armature
from armature.flags import *

Joints = []

HeadsTails = {
    'master' :             ('ground', ('ground', (0,0,-1))),
}

Armature = {
    'master' :             (0, None, F_WIR, L_MAIN),
}

CustomShapes = {
    'master' :          'GZM_Root',
}
