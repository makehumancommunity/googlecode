#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Export to the Ogre3d mesh format.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

The is an exporter that exports the human mesh to the Ogre3d mesh XML format.
(http://www.ogre3d.org/)
Supports both mesh and skeleton export.
A description of this format can be found here: https://bitbucket.org/sinbad/ogre/src/aebcd1e27621d9135c9355cb981838d46bf3835d/Tools/XMLConverter/docs/
"""

__docformat__ = 'restructuredtext'

import os
import numpy as np
import exportutils
import skeleton

def exportOgreMesh(human, filepath, config):
    obj = human.meshData
    config.setHuman(human)
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = formatName(config.goodName(os.path.splitext(filename)[0]))

    stuffs = exportutils.collect.setupObjects(
        name, 
        human,
        config=config,
        helpers=config.helpers, 
        hidden=config.hidden, 
        eyebrows=config.eyebrows, 
        lashes=config.lashes,
        subdivide=config.subdivide)

    writeMeshFile(human, filepath, stuffs, config)
    if human.getSkeleton():
        writeSkeletonFile(human, filepath, config)
    writeMaterialFile(human, filepath, stuffs, config)


def writeMeshFile(human, filepath, stuffs, config):
    filename = os.path.basename(filepath)
    name = formatName(config.goodName(os.path.splitext(filename)[0]))

    f = open(filepath, 'w')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<!-- Exported from MakeHuman (www.makehuman.org) -->\n')
    f.write('<mesh>\n')
    f.write('    <submeshes>\n')

    for stuffIdx, stuff in enumerate(stuffs):
        obj = stuff.meshInfo.object
        numVerts = len(obj.coord)
        if obj.vertsPerPrimitive == 4:
            # Quads
            numFaces = len(obj.fvert) * 2
        else:
            # Tris
            numFaces = len(obj.fvert)

        f.write('        <submesh material="%s_%s_%s" usesharedvertices="false" use32bitindexes="false" operationtype="triangle_list">\n' % (formatName(name), stuffIdx, formatName(stuff.name) if formatName(stuff.name) != name else "human"))

        # Faces
        f.write('            <faces count="%s">\n' % numFaces)
        for fv in obj.fvert:
            f.write('                <face v1="%s" v2="%s" v3="%s" />\n' % (fv[0], fv[1], fv[2]))
            if obj.vertsPerPrimitive == 4:
                f.write('                <face v1="%s" v2="%s" v3="%s" />\n' % (fv[2], fv[3], fv[0]))
        f.write('            </faces>\n')

        # Vertices
        f.write('            <geometry vertexcount="%s">\n' % numVerts)
        f.write('                <vertexbuffer positions="true" normals="true">\n')
        for vIdx, co in enumerate(obj.coord):
            # Note: Ogre3d uses a y-up coordinate system (just like MH)
            norm = obj.vnorm[vIdx]
            f.write('                    <vertex>\n')
            f.write('                        <position x="%s" y="%s" z="%s" />\n' % (co[0], co[1], co[2]))
            f.write('                        <normal x="%s" y="%s" z="%s" />\n' % (norm[0], norm[1], norm[2]))
            f.write('                    </vertex>\n')
        f.write('                </vertexbuffer>\n')

        # UV Texture Coordinates
        uvs = np.zeros(len(obj.coord), dtype=np.uint32)
        uvs[obj.fvert] = obj.fuvs
        f.write('                <vertexbuffer texture_coord_dimensions_0="2" texture_coords="1">\n')
        for vIdx in xrange(numVerts): 
            if obj.has_uv:
                u, v = obj.texco[uvs[vIdx]]
                v = 1-v
            else:
                u, v = 0, 0
            f.write('                    <vertex>\n')
            f.write('                        <texcoord u="%s" v="%s" />\n' % (u, v))
            f.write('                    </vertex>\n')
        f.write('                </vertexbuffer>\n')
        f.write('            </geometry>\n')
        del uvs

        # Skeleton bone assignments
        if human.getSkeleton():
            bodyWeights = human.getVertexWeights()
            if stuff.type:
                # Determine vertex weights for proxy
                weights = skeleton.getProxyWeights(stuff.proxy, bodyWeights, obj)
            else:
                # Use vertex weights for human body
                weights = bodyWeights

            f.write('            <boneassignments>\n')
            boneNames = [ bone.name for bone in human.getSkeleton().getBones() ]
            for (boneName, (verts,ws)) in weights.items():
                bIdx = boneNames.index(boneName)
                for i in xrange(len(verts)):
                    vIdx = verts[i]
                    w = ws[i]
                    f.write('                <vertexboneassignment vertexindex="%s" boneindex="%s" weight="%s" />\n' % (vIdx, bIdx, w))
            f.write('            </boneassignments>\n')
            f.write('        </submesh>\n')

    f.write('    </submeshes>\n')
    f.write('    <submeshnames>\n')
    for stuffIdx, stuff in enumerate(stuffs):
        f.write('        <submeshname name="%s" index="%s" />\n' % (formatName(stuff.name) if formatName(stuff.name) != name else "human", stuffIdx))
    f.write('    </submeshnames>\n')

    if human.getSkeleton():
        f.write('    <skeletonlink name="%s.skeleton" />\n' % name)
    f.write('</mesh>')
    f.close()


def writeSkeletonFile(human, filepath, config):
    filename = os.path.basename(filepath)
    name = formatName(config.goodName(os.path.splitext(filename)[0]))
    filename = name + ".skeleton.xml"
    filepath = os.path.join(os.path.dirname(filepath), filename)

    skel = human.getSkeleton()

    f = open(filepath, 'w')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<!-- Exported from MakeHuman (www.makehuman.org) -->\n')
    f.write('<skeleton>\n')
    f.write('    <bones>\n')
    for bIdx, bone in enumerate(skel.getBones()):
        pos = bone.getRestHeadPos()
        f.write('        <bone id="%s" name="%s">\n' % (bIdx, bone.name))
        f.write('            <position x="%s" y="%s" z="%s" />\n' % (pos[0], pos[1], pos[2]))
        f.write('            <rotation angle="0">\n')
        f.write('                <axis x="1" y="0" z="0" />\n')
        f.write('            </rotation>\n')
        f.write('        </bone>\n')
    f.write('    </bones>\n')

    f.write('    <bonehierarchy>\n')
    for bone in skel.getBones():
        if bone.parent:
            f.write('        <boneparent bone="%s" parent="%s" />\n' % (bone.name, bone.parent.name))
    f.write('    </bonehierarchy>\n')

    # TODO export animations
    f.write('    <animations>\n')
    f.write('    </animations>\n')
    f.write('</skeleton>')
    f.close()


def writeMaterialFile(human, filepath, stuffs, config):
    folderpath = os.path.dirname(filepath)
    name = formatName(config.goodName(os.path.splitext(os.path.basename(filepath))[0]))
    filename = name + ".material"
    filepath = os.path.join(folderpath, filename)

    f = open(filepath, 'w')
    for stuffIdx, stuff in enumerate(stuffs):
        texfolder, texfile = stuff.texture
        texpath = os.path.join(texfolder, texfile)
        if stuffIdx > 0:
            f.write('\n')
        f.write('material %s_%s_%s\n' % (formatName(name), stuffIdx, formatName(stuff.name) if formatName(stuff.name) != name else "human"))
        f.write('{\n')
        f.write('    technique\n')
        f.write('    {\n')
        f.write('        pass\n')
        f.write('        {\n')
        f.write('            texture_unit\n')
        f.write('            {\n')
        f.write('                texture %s\n' % texfile)
        f.write('            }\n')
        # TODO add support for normal maps, material properties, ...
        f.write('        }\n')
        f.write('    }\n')
        f.write('}\n')
    f.close()

def formatName(name):
    return name.rstrip('.mesh')
