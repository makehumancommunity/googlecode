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
import pickle

class Light(object):
    def __init__(self):
        self.pos = (-10.99, 20.0, 20.0)
        self.focus = (0,0,0)
        self.color = (1,1,1)
        self.fov = 180
        self.attenuation = 0


class Scene(object):
    def __init__(self, path = None):
        if path is None:
            self.camera = Camera()
            self.lights = [Light()]

            self.unsaved = False
            self.path = None
        else:
            self.load(path)

    def load(self, path):
        # Load scene from a .mhscene file.
        self.unsaved = False
        self.path = path
        
        hfile = open(self.path, 'rb')
        self.camera = pickle.load(hfile)
        nlig = pickle.load(hfile)
        self.lights = []
        for i in range(nlig):
            self.lights.append(pickle.load(hfile))
        hfile.close()

    def save(self, path = None):
        # Save scene to a .mhscene file.
        if path is not None:
            self.path = path
        self.unsaved = False
        
        hfile = open(self.path, 'wb')
        pickle.dump(self.camera, hfile)
        pickle.dump(len(self.lights), hfile)
        for light in self.lights:
            pickle.dump(light, hfile)
        hfile.close()

    def close(self):
        self.__init__()

    def addLight(self):
        self.unsaved = True
        newlight = Light()
        self.lights.append(newlight)
        return self.lights.index(newlight)
        
