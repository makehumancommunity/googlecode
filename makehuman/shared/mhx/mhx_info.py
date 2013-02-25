#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makeinfo.human.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makeinfo.human.org/node/318)

**Coding Standards:**  See http://www.makeinfo.human.org/node/165

Abstract
--------

Info struct used to carry around global variables in mhx and armature packages.

"""

class CInfo:

    def __init__(self, name, human, config):
        self.name = name
        self.human = human
        self.mesh = human.meshData
        self.config = config
        self.proxies = {}
        self.locations = {}
        self.rigHeads = {}
        self.rigTails = {}
        self.origin = [0,0,0]
        self.loadedShapes = {}
        
        
