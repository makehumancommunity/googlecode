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

TODO
"""

import os
import numpy
import guicommon
from core import G
import getpath
import log
from collections import OrderedDict

import material
import io_json

_A7converter = None
Unit = numpy.array((1.0,1.0,1.0))

class CProxyRefVert:

    def __init__(self, parent):
        self._parent = parent


    def fromSingle(self, words, vnum, proxy):
        self._exact = True
        v0 = int(words[0])
        self._verts = (v0,v0,v0)
        self._weights = (1,0,0)
        self._offset = numpy.array((0,0,0), float)
        self.addProxyVertWeight(proxy, v0, vnum, 1)
        return self


    def fromTriple(self, words, vnum, proxy):
        self._exact = False
        v0 = int(words[0])
        v1 = int(words[1])
        v2 = int(words[2])
        w0 = float(words[3])
        w1 = float(words[4])
        w2 = float(words[5])
        if len(words) > 6:
            d0 = float(words[6])
            d1 = float(words[7])
            d2 = float(words[8])
        else:
            (d0,d1,d2) = (0,0,0)

        self._verts = (v0,v1,v2)
        self._weights = (w0,w1,w2)
        self._offset = numpy.array((d0,d1,d2), float)

        self.addProxyVertWeight(proxy, v0, vnum, w0)
        self.addProxyVertWeight(proxy, v1, vnum, w1)
        self.addProxyVertWeight(proxy, v2, vnum, w2)
        return self


    def addProxyVertWeight(self, proxy, v, pv, w):
        try:
            proxy.vertWeights[v].append((pv, w))
        except KeyError:
            proxy.vertWeights[v] = [(pv,w)]
        return

    def getHumanVerts(self):
        return self._verts

    def getWeights(self):
        return self._weights

    def getOffset(self):
        return self._offset

    def getCoord(self, scale):
        rv0,rv1,rv2 = self._verts
        v0 = self._parent.coord[rv0]
        v1 = self._parent.coord[rv1]
        v2 = self._parent.coord[rv2]
        w0,w1,w2 = self._weights
        return (w0*v0 + w1*v1 + w2*v2 + scale*self._offset)

    def getConvertedCoord(self, converter, scale):
        rv0,rv1,rv2 = self._verts
        v0 = converter.refVerts[rv0].getCoord(Unit)
        v1 = converter.refVerts[rv1].getCoord(Unit)
        v2 = converter.refVerts[rv2].getCoord(Unit)
        w0,w1,w2 = self._weights
        return (w0*v0 + w1*v1 + w2*v2 + scale*self._offset)


#
#    class CProxy
#

class CProxy:
    def __init__(self, file, typ, layer):
        log.debug("Loading proxy file: %s.", file)
        name = os.path.splitext(os.path.basename(file))[0]
        self.name = name.capitalize().replace(" ","_")
        self.type = typ
        self.file = file
        self.uuid = None
        self.basemesh = "alpha_7"
        self.tags = []

        self.vertWeights = {}       # (proxy-vert, weight) list for each parent vert
        self.refVerts = []

        self.scaleData = [None, None, None]
        self.scale = numpy.array((1.0,1.0,1.0), float)

        self.z_depth = 50
        self.cull = False
        self.layer = layer

        self.uvLayers = {}

        self.useBaseMaterials = False
        self.rig = None
        self.mask = None

        self.material = material.Material(self.name)

        self.obj_file = None
        self.vertexgroup_file = None
        self.vertexGroups = None
        self.material_file = None
        self.mhxMaterial_file = None
        self.maskLayer = -1
        self.textureLayer = 0
        self.objFileLayer = 0   # TODO what is this used for?
        self.texVertsLayers = {}
        self.texFacesLayers = {}

        self.deleteGroups = []
        self.deleteVerts = None

        self.wire = False
        self.cage = False
        self.modifiers = []
        self.shapekeys = []
        self.weights = None
        self.clothings = []
        self.transparencies = dict()
        return


    def __repr__(self):
        return ("<CProxy %s %s %s %s>" % (self.name, self.type, self.file, self.uuid))


    def getObject(self):
        import object3d, module3d

        human = G.app.selectedHuman
        # TODO use more generic way of retrieving a proxy type
        if self.type == "Clothes":
            obj = human.clothesObjs[self.getUuid()]
        elif self.type == "Proxymeshes":
            if not human.proxy:
                return None
            obj = human.getProxyMesh()
        elif self.type == "Hair":
            obj = human.hairObj
        elif self.type == "Eyes":
            obj = human.eyesObj
        elif self.type == "Genitals":
            obj = human.genitalsObj
        elif self.type == "Cage":
            return None
        elif self.type == "Converter":
            return None
        else:
            raise NameError("Unknown proxy type %s" % self.type)

        if isinstance(obj, guicommon.Object):
            obj = obj.mesh
        if not (isinstance(obj, module3d.Object3D) or isinstance(obj, object3d.Object3D)):
            raise NameError("%s is not an object" % obj)
        return obj


    def getActualTexture(self, human):
        uuid = self.getUuid()
        if uuid in human.clothesObjs.keys() and human.clothesObjs[uuid]:
            obj = human.clothesObjs[uuid]
        elif human.hairProxy and uuid == human.hairProxy.uuid:
            obj = human.hairObj
        elif human.eyesProxy and uuid == human.eyesProxy.uuid:
            obj = human.eyesObj
        elif human.genitalsProxy and uuid == human.genitalsProxy.uuid:
            obj = human.genitalsObj
        elif human.proxy and uuid == human.proxy.uuid:
            obj = human
        else:
            return None
        return getpath.formatPath(obj.mesh.texture)


    def getCoords(self):
        obj = G.app.selectedHuman.meshData
        for n in range(3):
            self.scale[n] = self.getScale(self.scaleData[n], obj, n)

        converter = self.getConverter()
        if converter:
            return [refVert.getConvertedCoord(converter, self.scale) for refVert in self.refVerts]
        else:
            return [refVert.getCoord(self.scale) for refVert in self.refVerts]


    def update(self, obj):
        log.debug("Updating proxy %s.", self.name)
        coords = self.getCoords()
        obj.changeCoords(coords)


    def getUuid(self):
        if self.uuid:
            return self.uuid
        else:
            return self.name


    def getConverter(self):
        if self.basemesh in ["alpha_7", "alpha7"]:
            global _A7converter
            if _A7converter is None:
                _A7converter = readProxyFile(G.app.selectedHuman.meshData, getpath.getSysDataPath("3dobjs/a7_converter.proxy"), type="Converter")
            log.debug("Converting %s with %s", self.name, _A7converter)
            return _A7converter
        elif self.basemesh == "hm08":
            return None
        else:
            raise NameError("Unknown basemesh for mhclo file: %s" % self.basemesh)


    def getScale(self, data, obj, index):
        if not data:
            return 1.0
        (vn1, vn2, den) = data

        converter = self.getConverter()
        if converter:
            co1 = converter.refVerts[vn1].getCoord(Unit)
            co2 = converter.refVerts[vn2].getCoord(Unit)
        else:
            co1 = obj.coord[vn1]
            co2 = obj.coord[vn2]

        num = abs(co1[index] - co2[index])
        return num/den


    def getWeights(self, rawWeights, amt=None):
        if amt and self.vertexGroups:
            weights = OrderedDict()
            for name,data in self.vertexGroups:
                for bone in amt.bones.values():
                    if bone.origName == name:
                        name1 = bone.name
                        break
                for name2 in [
                    "DEF-"+name1,
                    "DEF-"+name1.replace(".L", ".03.L"),
                    "DEF-"+name1.replace(".R", ".03.R"),
                    name1]:
                    if name2 in rawWeights:
                        weights[name2] = data
                        break
            return weights

        converter = self.getConverter()
        if converter:
            rawWeights = converter.getWeights1(rawWeights)
        return self.getWeights1(rawWeights)


    def getWeights1(self, rawWeights):
        weights = OrderedDict()
        if not rawWeights:
            return weights

        for key in rawWeights.keys():
            vgroup = []
            empty = True
            for (v,wt) in rawWeights[key]:
                try:
                    vlist = self.vertWeights[v]
                except KeyError:
                    vlist = []
                for (pv, w) in vlist:
                    pw = w*wt
                    if (pw > 1e-4):
                        vgroup.append((pv, pw))
                        empty = False
            if not empty:
                weights[key] = self.fixVertexGroup(vgroup)
        return weights


    def fixVertexGroup(self, vgroup):
        fixedVGroup = []
        vgroup.sort()
        pv = -1
        while vgroup:
            (pv0, wt0) = vgroup.pop()
            if pv0 == pv:
                wt += wt0
            else:
                if pv >= 0 and wt > 1e-4:
                    fixedVGroup.append((pv, wt))
                (pv, wt) = (pv0, wt0)
        if pv >= 0 and wt > 1e-4:
            fixedVGroup.append((pv, wt))
        return fixedVGroup


    def getShapes(self, rawShapes, scale):
        if (not rawShapes) or (self.type not in ['Proxymeshes', 'Clothes']):
            return []
        shapes = []
        for (key, rawShape) in rawShapes:
            shape = []
            for (v,dr) in rawShape.items():
                (dx,dy,dz) = dr
                try:
                    vlist = self.vertWeights[v]
                except KeyError:
                    vlist = []
                for (pv, w) in vlist:
                    shape.append((pv, scale*w*dx, scale*w*dy, scale*w*dz))
            if shape != []:
                fixedShape = self.fixShape(shape)
                shapes.append((key,fixedShape))
        return shapes


    def fixShape(self, shape):
        fixedShape = {}
        shape.sort()
        pv = -1
        for (pv0, dx0, dy0, dz0) in shape:
            if pv0 == pv:
                dx += dx0
                dy += dy0
                dz += dz0
            else:
                if pv >= 0 and (dx*dx + dy*dy + dz*dz) > 1e-8:
                    fixedShape[pv] = (dx, dy, dz)
                (pv, dx, dy, dz) = (pv0, dx0, dy0, dz0)
        if pv >= 0 and (dx*dx + dy*dy + dz*dz) > 1e-8:
            fixedShape[pv] = (dx, dy, dz)
        return fixedShape

#
#    readProxyFile(obj, file, evalOnLoad=False, scale=1.0):
#

doRefVerts = 1
doWeights = 2
doDeleteVerts = 3

def readProxyFile(obj, filepath, type="Clothes", layer=4):
    folder = os.path.realpath(os.path.expanduser(os.path.dirname(filepath)))

    try:
        fp = open(filepath, "rU")
    except IOError:
        log.error("*** Cannot open %s", filepath)
        return None

    proxy = CProxy(filepath, type, layer)
    proxy.deleteVerts = numpy.zeros(len(obj.coord), bool)

    proxy.useProjection = True
    proxy.ignoreOffset = False
    status = 0
    vnum = 0
    for line in fp:
        words = line.split()

        if len(words) == 0:
            # Reset status on empty line
            #status = 0
            continue

        if words[0].startswith('#') or words[0].startswith('//'):
            # Comment
            continue

        key = words[0]

        if key == 'name':
            proxy.name = " ".join(words[1:])
        elif key == 'uuid':
            proxy.uuid = " ".join(words[1:])
        elif key == 'tag':
            proxy.tags.append( " ".join(words[1:]) )
        elif key == 'z_depth':
            proxy.z_depth = int(words[1])

        elif key == 'verts':
            status = doRefVerts
        elif key == 'weights':
            status = doWeights
            if proxy.weights == None:
                proxy.weights = {}
            weights = []
            proxy.weights[words[1]] = weights
        elif key == "delete_verts":
            status = doDeleteVerts

        elif key == 'obj_file':
            proxy.obj_file = getFileName(folder, words[1], ".obj")

        elif key == 'vertexgroup_file':
            proxy.vertexgroup_file = getFileName(folder, words[1], ".json")
            proxy.vertexGroups = io_json.loadJson(proxy.vertexgroup_file)

        elif key == 'material':
            matFile = getFileName(folder, words[1], ".mhmat")
            proxy.material_file = matFile
            proxy.material.fromFile(matFile)

        elif key == 'mhx_material':
            # Read .mhx material file (or only set a filepath reference to it)
            # MHX material file is supposed to contain only shading parameters that are specific for blender export that are not stored in the .mhmat file
            matFile = getFileName(folder, words[1], ".mhx")
            proxy.mhxMaterial_file = matFile
            #readMaterial(line, material, proxy, False)
            pass
        elif key == 'useBaseMaterials':
            # TODO deprecated?
            proxy.useBaseMaterials = True

        elif key == 'backface_culling':
            # TODO remove in future
            log.warning('Deprecated parameter "backface_culling" used in proxy file. Set property backfaceCull in material instead.')
        elif key == 'transparent':
            # TODO remove in future
            log.warning('Deprecated parameter "transparent" used in proxy file. Set property in material file instead.')

        elif key == 'uvLayer':
            if len(words) > 2:
                layer = int(words[1])
                uvFile = words[2]
            else:
                layer = 0
                uvFile = words[1]
            #uvMap = material.UVMap(proxy.name+"UV"+str(layer))
            #uvMap.read(proxy.mesh, getFileName(folder, uvFile, ".mhuv"))
            # Delayed load, only store path here
            proxy.uvLayers[layer] = getFileName(folder, uvFile, ".mhuv")

        elif key == 'x_scale':
            proxy.scaleData[0] = getScaleData(words)
            proxy.scale[0] = proxy.getScale(proxy.scaleData[0], obj, 0)
        elif key == 'y_scale':
            proxy.scaleData[1] = getScaleData(words)
            proxy.scale[1] = proxy.getScale(proxy.scaleData[1], obj, 1)
        elif key == 'z_scale':
            proxy.scaleData[2] = getScaleData(words)
            proxy.scale[2] = proxy.getScale(proxy.scaleData[2], obj, 2)
        elif key == 'use_projection':
            # TODO still used?
            proxy.useProjection = int(words[1])
        elif key == 'ignoreOffset':
            # TODO still used?
            proxy.ignoreOffset = int(words[1])
        elif key == 'delete':
            proxy.deleteGroups.append(words[1])

        elif key == 'mask_uv_layer':
            if len(words) > 1:
                proxy.maskLayer = int(words[1])
        elif key == 'texture_uv_layer':
            if len(words) > 1:
                proxy.textureLayer = int(words[1])

        # TODO keep this costume stuff?
        elif key == 'clothing':
            if len(words) > 2:
                clothingPiece = (words[1], words[2])
            else:
                clothingPiece = (words[1], None)
            proxy.clothings.append(clothingPiece)
        elif key == 'transparencies':
            uuid = words[1]
            proxy.transparencies[uuid] = words[2].lower() in ["1", "yes", "true", "enable", "enabled"]

        # Blender-only properties
        elif key == 'wire':
            proxy.wire = True
        elif key == 'cage':
            proxy.cage = True
        elif key == 'subsurf':
            levels = int(words[1])
            if len(words) > 2:
                render = int(words[2])
            else:
                render = levels+1
            proxy.modifiers.append( ['subsurf', levels, render] )
        elif key == 'shrinkwrap':
            offset = float(words[1])
            proxy.modifiers.append( ['shrinkwrap', offset] )
        elif key == 'solidify':
            thickness = float(words[1])
            offset = float(words[2])
            proxy.modifiers.append( ['solidify', thickness, offset] )
        elif key == 'shapekey':
            proxy.shapekeys.append( words[1] )
        elif key == 'basemesh':
            proxy.basemesh = words[1]

        elif key in ['objfile_layer', 'uvtex_layer']:
            pass


        elif status == doRefVerts:
            refVert = CProxyRefVert(obj)
            proxy.refVerts.append(refVert)
            if len(words) == 1:
                refVert.fromSingle(words, vnum, proxy)
            else:
                refVert.fromTriple(words, vnum, proxy)
            vnum += 1

        elif status == doWeights:
            v = int(words[0])
            w = float(words[1])
            weights.append((v,w))

        elif status == doDeleteVerts:
            sequence = False
            for v in words:
                if v == "-":
                    sequence = True
                else:
                    v1 = int(v)
                    if sequence:
                        for vn in range(v0,v1+1):
                            proxy.deleteVerts[vn] = True
                        sequence = False
                    else:
                        proxy.deleteVerts[v1] = True
                    v0 = v1

        else:
            log.warning('Unknown keyword %s found in proxy file %s', key, filepath)

    return proxy


def getFileName(folder, file, suffix):
    (name, ext) = os.path.split(file)
    if ext:
        return os.path.join(folder, file)
    else:
        return os.path.join(folder, file+suffix)

def getScaleData(words):
    v1 = int(words[1])
    v2 = int(words[2])
    den = float(words[3])
    return (v1, v2, den)


def newFace(first, words, group, proxy):
    face = []
    texface = []
    nCorners = len(words)
    for n in range(first, nCorners):
        numbers = words[n].split('/')
        face.append(int(numbers[0])-1)
        if len(numbers) > 1:
            texface.append(int(numbers[1])-1)
    proxy.faces.append((face,group))
    if texface:
        proxy.texFaces.append(texface)
        if len(face) != len(texface):
            raise NameError("texface %s %s", face, texface)
    return


def newTexFace(words, proxy):
    texface = [int(word) for word in words]
    proxy.texFaces.append(texface)


def newTexVert(first, words, proxy):
    vt = [float(word) for word in words[first:]]
    proxy.texVerts.append(vt)


#
#
#


def updateProxyFileCache(paths, fileExt, cache = None):
    """
    Update cache of proxy files in the specified paths. If no cache is given as
    parameter, a new cache is created.
    This cache contains per canonical filename (key) the UUID and tags of that
    proxy file.
    Cache entries are invalidated if their modification time has changed, or no
    longer exist on disk.
    """
    if cache is None:
        cache = dict()
    proxyFiles = []
    entries = dict((key, True) for key in cache.keys()) # lookup dict for old entries in cache
    for folder in paths:
        proxyFiles.extend(_findProxyFiles(folder, fileExt, 6))
    for proxyFile in proxyFiles:
        proxyId = getpath.canonicalPath(proxyFile)

        mtime = os.path.getmtime(proxyFile)
        if proxyId in cache:
            del entries[proxyId]    # Mark that old cache entry is still valid
            cached_mtime = cache[proxyId][0]
            if not (mtime > cached_mtime):
                continue

        (uuid, tags) = peekMetadata(proxyFile)
        cache[proxyId] = (mtime, uuid, tags)
    # Remove entries from cache that no longer exist
    for key in entries.keys():
        del cache[key]
    return cache

def _findProxyFiles(folder, fileExt = "mhclo", depth = 6):
    if depth < 0:
        return []
    try:
        files = os.listdir(folder)
    except OSError:
        return []
    result = []
    for pname in files:
        path = os.path.join(folder, pname)
        if os.path.isfile(path):
            if os.path.splitext(path)[1] == "."+fileExt:
                result.append(path)
        elif os.path.isdir(path):
            result.extend(_findProxyFiles(path, fileExt, depth-1))
    return result

def peekMetadata(proxyFilePath):
    """
    Read UUID and tags from proxy file, and return as soon as vertex data
    begins. Reads only the necessary lines of the proxy file from disk, not the
    entire proxy file is loaded in memory.
    """
    fp = open(proxyFilePath)
    uuid = None
    tags = set()
    for line in fp:
        words = line.split()
        if len(words) == 0:
            pass
        elif words[0] == 'uuid':
            uuid = words[1]
        elif words[0] == 'tag':
            tags.add(words[1])
        elif words[0] == 'verts':
            break
    fp.close()
    return (uuid, tags)

