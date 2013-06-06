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

A rich mesh, with vertex weights, shapes and an armature

TODO
"""

import module3d


class RichMesh:

    def __init__(self, name, amt):
        self.name = name
        self.object = None
        self.weights = {}
        self.shapes = []
        self.armature = amt

        self.vertexMask = None
        self.faceMask = None
        self.vertexMapping = None   # Maps vertex index of original object to the attached filtered object


    def fromProxy(self, coords, texVerts, faceVerts, faceUvs, weights, shapes, scale=1.0):
        obj = self.object = module3d.Object3D(self.name)
        if scale != 1.0:
            coords = [scale*co for co in coords]
        obj.setCoords(coords)
        obj.setUVs(texVerts)

        for fv in faceVerts:
            if len(fv) != 4:
                raise NameError("Mesh %s has non-quad faces and can not be handled by MakeHuman" % self.name)

        obj.createFaceGroup("Full Object")
        obj.setFaces(faceVerts, faceUvs)
        self.weights = weights
        self.shapes = shapes
        return self


    def fromObject(self, object3d, weights, shapes):
        self.object = object3d
        self.name = object3d.name
        self.weights = weights
        self.shapes = shapes
        return self


    def __repr__(self):
        return ("<RichMesh %s w %d t %d>" % (self.object, len(self.weights), len(self.shapes)))



def getRichMesh(obj, proxy, config, rawWeights, rawShapes, rigname, amt):
    if proxy:
        coords = proxy.getCoords()
        faceVerts = [[v for v in f] for (f,g) in proxy.faces]

        if proxy.texVerts:
            texVerts = proxy.texVertsLayers[proxy.objFileLayer]
            texFaces = proxy.texFacesLayers[proxy.objFileLayer]
            fnmax = len(texFaces)
            faceVerts = faceVerts[:fnmax]
        else:
            texVerts = []
            texFaces = []

        weights = proxy.getWeights(rawWeights)
        shapes = proxy.getShapes(rawShapes, config.scale)
        richMesh = RichMesh(proxy.name, amt).fromProxy(coords, texVerts, faceVerts, texFaces, weights, shapes, scale=config.scale)

    else:
        richMesh = RichMesh(obj.name, amt).fromObject(obj, rawWeights, rawShapes)
    return richMesh
