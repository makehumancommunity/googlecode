#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Definition of the scene class and some of the subclasses it uses.
"""

from camera import Camera

class Light:
    def __init__(self):
        pos = (-10.99, 20.0, 20.0)
        focus = (0,0,0)
        color = (1,1,1)
        fov = 180
        attenuation = 0


class Scene:
    def __init__(self, path = None):
        if path is not None:
            self.load(path)
        else:
            self.camera = Camera()
            self.lights = []

    def load(self, path):
        # Load scene from a .mhscene file
        pass

    def save(self, path):
        # Save scene to a .mhscene file
        pass
    
