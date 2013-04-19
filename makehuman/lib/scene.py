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

import camera
import events3d
import pickle

mhscene_version = 3


class Light(object):
    def __init__(self, scene = None):
        self._scene = scene
        self._pos = (-10.99, 20.0, 20.0)
        self._focus = (0.0, 0.0, 0.0)
        self._color = (1.0, 1.0, 1.0)
        self._fov = 180.0
        self._att = 0.0

    def changed(self):
        if (self._scene is not None):
            self._scene.changed()
        
    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, value):
        self._pos = value
        self.changed()

    @property
    def focus(self):
        return self._focus

    @focus.setter
    def focus(self, value):
        self._focus = value
        self.changed()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.changed()

    @property
    def fov(self):
        return self._fov

    @fov.setter
    def fov(self, value):
        self._fov = value
        self.changed()

    @property
    def attenuation(self):
        return self._att

    @attenuation.setter
    def attenuation(self, value):
        self._att = value
        self.changed()


class Human(object):
    def __init__(self, scene = None):
        self._scene = scene
        self._pos = (0.0, 0.0, 0.0)        
        self._rot = (0.0, 0.0, 0.0)        

    def changed(self):
        if (self._scene is not None):
            self._scene.changed()
        
    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, value):
        self._pos = value
        self.changed()

    @property
    def rotation(self):
        return self._rot

    @rotation.setter
    def rotation(self, value):
        self._rot = value
        self.changed()


class Scene(events3d.EventHandler):
    def __init__(self, path = None):
        if path is None:
            self.lights = [Light(self)]
            self.camera = camera.Camera()
            self.human = Human(self)

            self._ambience = (0.1, 0.1, 0.1)

            self.unsaved = False
            self.path = None
        else:
            self.load(path)

        @self.camera.mhEvent
        def onChanged(cam):
            self.changed()

    def changed(self):
        self.unsaved = True
        self.callEvent('onChanged', self)

    def load(self, path):
        # Load scene from a .mhscene file.
        self.unsaved = False
        self.path = path
        
        hfile = open(self.path, 'rb')
        filever = pickle.load(hfile)
        self.camera = pickle.load(hfile)
        if filever >= 3:
            self.human = pickle.load(hfile)
        if filever >= 2:
            self._ambience = pickle.load(hfile)
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
        pickle.dump(mhscene_version, hfile)
        pickle.dump(self.camera, hfile)
        pickle.dump(self.human, hfile)
        pickle.dump(self._ambience, hfile)
        pickle.dump(len(self.lights), hfile)
        for light in self.lights:
            pickle.dump(light, hfile)
        hfile.close()

    def close(self):
        self.__init__()

    def addLight(self):
        self.changed()
        newlight = Light(self)
        self.lights.append(newlight)

    def removeLight(self, light):
        self.changed()
        self.lights.remove(light)
        
    @property
    def ambience(self):
        return self._ambience;

    @ambience.setter
    def ambience(self, value):
        self.changed()
        self._ambience = value
        
