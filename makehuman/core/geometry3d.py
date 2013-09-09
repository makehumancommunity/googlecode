#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module contains classes for commonly used geometry
"""

import module3d
import numpy as np

class RectangleMesh(module3d.Object3D):

    """
    A filled rectangle.
    
    :param width: The width.
    :type width: int or float
    :param height: The height.
    :type height: int or float
    :param centered True to center the mesh around its local origin.
    :type centered bool
    :param texture: The texture.
    :type texture: str
    """
            
    def __init__(self, width, height, centered = False, texture=None):

        module3d.Object3D.__init__(self, 'rectangle_%s' % texture)

        self.centered = centered
        
        # create group
        fg = self.createFaceGroup('rectangle')
        
        # The 4 vertices
        v = self._getVerts(width, height)
        
        # The 4 uv values
        uv = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
        
        # The face
        fv = [(0,1,2,3)]
        fuv = [(0,1,2,3)]

        self.setCoords(v)
        self.setUVs(uv)
        self.setFaces(fv, fuv, fg.idx)

        self.setTexture(texture)
        self.setCameraProjection(1)
        self.setShadeless(1)
        self.updateIndexBuffer()

    def _getVerts(self, width, height):
        if self.centered:
            v = [
                (-width/2, -height/2, 0.0),
                (width/2, -height/2, 0.0),
                (width/2, height/2, 0.0),
                (-width/2, height/2, 0.0)
                ]
        else:
            v = [
                (0.0, 0.0, 0.0),
                (width, 0.0, 0.0),
                (width, height, 0.0),
                (0.0, height, 0.0)
                ]
        return v

    def move(self, dx, dy):
        self.coord += (dx, dy, 0)
        self.markCoords(coor=True)
        self.update()

    def setPosition(self, x, y):
        width, height = self.getSize()
        v = np.asarray(self._getVerts(width, height), dtype=np.float32)
        v += (x, y, 0)
        self.changeCoords(v)
        self.update()

    def resetPosition(self):
        width, height = self.getSize()
        v = self._getVerts(width, height)
        self.changeCoords(v)
        self.update()

    def resize(self, width, height):
        dx, dy = self.getOffset()
        v = np.asarray(self._getVerts(width, height), dtype=np.float32)
        v[:, 0] += dx
        v[:, 1] += dy
        self.changeCoords(v)
        self.update()

    def getSize(self):
        ((x0,y0,z0),(x1,y1,z1)) = self.calcBBox()
        return (x1 - x0, y0 - y1)

    def getOffset(self):
        ((x0,y0,z0),(x1,y1,z1)) = self.calcBBox()
        if self.centered:
            w, h = (x1 - x0, y0 - y1)
            dx = x0+w/2
            dy = y1+h/2
        else:
            dx = x0
            dy = y1
        return dx, dy
       
class FrameMesh(module3d.Object3D):
    """
    A wire rectangle.

    :param width: The width.
    :type width: int or float
    :param height: The height.
    :type height: int or float
    """
            
    def __init__(self, width, height):

        module3d.Object3D.__init__(self, 'frame', 2)
        
        # create group
        fg = self.createFaceGroup('frame')

        # The 4 vertices
        v = [
            (0.0, 0.0, 0.0),
            (width, 0.0, 0.0),
            (width, height, 0.0),
            (0.0, height, 0.0)
            ]
        
        # The 4 uv values
        uv = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
        
        # The faces
        f = [(0,3),(1,0),(2,1),(3,2)]

        self.setCoords(v)
        self.setUVs(uv)
        self.setFaces(f, f, fg.idx)
        
        self.setCameraProjection(1)
        self.setShadeless(1)
        self.updateIndexBuffer()

    def move(self, dx, dy):
        self.coord += (dx, dy, 0)
        self.markCoords(coor=True)
        self.update()

    def resize(self, width, height):
        v = [
            (0.0, 0.0, 0.0),
            (width, 0.0, 0.0),
            (width, height, 0.0),
            (0.0, height, 0.0)
            ]
        self.changeCoords(v)
        self.update()     

class Cube(module3d.Object3D):

    """
    A cube.
    
    :param width: The width.
    :type width: int or float
    :param height: The height, if 0 it will be equal to width.
    :type height: int or float
    :param depth: The depth, if 0 it will be equal to width.
    :type depth: int or float
    :param texture: The texture.
    :type texture: str
    """
            
    def __init__(self, width, height=0, depth=0, texture=None):

        module3d.Object3D.__init__(self, 'cube_%s' % texture)
        
        self.width = width
        self.height = height or width
        self.depth = depth or width
        
        # create group
        fg = self.createFaceGroup('cube')
        
        # The 8 vertices
        v = [(x,y,z) for z in [0,self.depth] for y in [0,self.height] for x in [0,self.width]]

        #         /0-----1\
        #        / |     | \
        #       |4---------5|
        #       |  |     |  |
        #       |  3-----2  |  
        #       | /       \ |
        #       |/         \|
        #       |7---------6|
        
        # The 4 uv values
        #uv = ([0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0])
        
        # The 6 faces
        f = [
            (4, 5, 6, 7), # front
            (1, 0, 3, 2), # back
            (0, 4, 7, 3), # left
            (5, 1, 2, 6), # right
            (0, 1, 5, 4), # top
            (7, 6, 2, 3), # bottom
            ]

        self.setCoords(v)
        # self.setUVs(uv)
        self.setFaces(f, fg.idx)

        self.setTexture(texture)
        self.setCameraProjection(0)
        self.setShadeless(0)
        self.updateIndexBuffer()
        
    def resize(self, width, height, depth):
        v = [(x,y,z) for z in [0,depth] for y in [0,height] for x in [0,width]]
        self.changeCoords(v)
        self.update()
