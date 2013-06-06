#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------
Exports proxy mesh to obj

"""

import os
import math
import exportutils

#
#    exportObj(human, filepath, config):
#

def exportObj(human, filepath, config=None):
    if config is None:
        config = exportutils.config.Config()
    obj = human.meshData
    config.setHuman(human)
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    stuffs,_amt = exportutils.collect.setupObjects(
        name,
        human,
        config=config,
        helpers=config.helpers,
        eyebrows=config.eyebrows,
        lashes=config.lashes,
        subdivide=config.subdivide)

    fp = open(filepath, 'w')
    mtlfile = "%s.mtl" % os.path.splitext(filepath)[0]
    mtlfile = mtlfile.encode(config.encoding, 'replace')
    fp.write(
        "# MakeHuman exported OBJ\n" +
        "# www.makehuman.org\n\n" +
        "mtllib %s\n" % os.path.basename(mtlfile))

    # Vertices

    for stuff in stuffs:
        obj = stuff.richMesh.object
        for co in obj.coord:
            fp.write("v %.4g %.4g %.4g\n" % tuple(co))

    # Vertex normals

    if config.useNormals:
        for stuff in stuffs:
            obj = stuff.richMesh.object
            obj.calcFaceNormals()
            #obj.calcVertexNormals()
            for no in obj.fnorm:
                no = no/math.sqrt(no.dot(no))
                fp.write("vn %.4g %.4g %.4g\n" % tuple(no))


    # UV vertices

    for stuff in stuffs:
        obj = stuff.richMesh.object
        if obj.has_uv:
            for uv in obj.texco:
                fp.write("vt %.4g %.4g\n" % tuple(uv))

    # Faces

    nVerts = 1
    nTexVerts = 1
    for stuff in stuffs:
        fp.write("usemtl %s\n" % stuff.name)
        fp.write("g %s\n" % stuff.name)
        obj = stuff.richMesh.object
        for fn,fv in enumerate(obj.fvert):
            fp.write('f ')
            fuv = obj.fuvs[fn]
            if fv[0] == fv[3]:
                nv = 3
            else:
                nv = 4
            if config.useNormals:
                if obj.has_uv:
                    for n in range(nv):
                        vn = fv[n]+nVerts
                        fp.write("%d/%d/%d " % (vn, fuv[n]+nTexVerts, fn))
                else:
                    for n in range(nv):
                        vn = fv[n]+nVerts
                        fp.write("%d//%d " % (vn, fn))
            else:
                if obj.has_uv:
                    for n in range(nv):
                        vn = fv[n]+nVerts
                        fp.write("%d/%d " % (vn, fuv[n]+nTexVerts))
                else:
                    for n in range(nv):
                        vn = fv[n]+nVerts
                        fp.write("%d " % (vn))
            fp.write('\n')

        nVerts += len(obj.coord)
        nTexVerts += len(obj.texco)

    fp.close()

    fp = open(mtlfile, 'w')
    fp.write(
        '# MakeHuman exported MTL\n' +
        '# www.makehuman.org\n\n')
    for stuff in stuffs:
        writeMaterial(fp, stuff, human, config)
    fp.close()
    return

#
#   writeMaterial(fp, stuff, human, config):
#

def writeMaterial(fp, stuff, human, config):
    fp.write("\nnewmtl %s\n" % stuff.name)
    mat = stuff.material
    di = mat.diffuseIntensity
    diff = mat.diffuseColor
    si = mat.specularIntensity
    spec =  mat.specularColor
    fp.write(
        "Kd %.4g %.4g %.4g\n" % (di*diff.r, di*diff.g, di*diff.b) +
        "Ks %.4g %.4g %.4g\n" % (si*spec.r, si*spec.g, si*spec.b) +
        "d %.4g\n" % (1-mat.transparencyIntensity)
    )

    writeTexture(fp, "map_Kd", mat.diffuseTexture, human, config)
    writeTexture(fp, "map_Ks", mat.specularMapTexture, human, config)
    #writeTexture(fp, "map_Tr", mat.translucencyMapTexture, human, config)
    writeTexture(fp, "map_Disp", mat.normalMapTexture, human, config)
    writeTexture(fp, "map_Disp", mat.specularMapTexture, human, config)
    writeTexture(fp, "map_Disp", mat.displacementMapTexture, human, config)

    #    writeTexture(fp, "map_Kd", ("data/textures", "texture.png"), human, config)


def writeTexture(fp, key, filepath, human, config):
    if not filepath:
        return
    newpath = config.copyTextureToNewLocation(filepath)
    fp.write("%s %s\n" % (key, newpath))


"""
Ka 1.0 1.0 1.0
Kd 1.0 1.0 1.0
Ks 0.33 0.33 0.52
illum 5
Ns 50.0
map_Kd texture.png
"""
