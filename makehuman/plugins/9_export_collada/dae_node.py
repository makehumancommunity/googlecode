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

Node export

"""

import math
import numpy as np
import transformations as tm

#----------------------------------------------------------------------
#   library_visual_scenes
#----------------------------------------------------------------------

def writeLibraryVisualScenes(fp, rmeshes, amt, config):
    fp.write(
        '\n  <library_visual_scenes>\n' +
        '    <visual_scene id="Scene" name="Scene">\n' +
        '      <node id="%s">\n' % amt.name)

    if config.rotate90X:
        mat = tm.rotation_matrix(-math.pi/2, (1,0,0))
    else:
        mat = np.identity(4, float)

    if config.rotate90Z:
        rotZ = tm.rotation_matrix(math.pi/2, (0,0,1))
        mat = np.dot(mat, rotZ)
    writeMatrix(fp, mat, "transform", "        ")

    for root in amt.hierarchy:
        writeBone(fp, root, [0,0,0], 'layer="L1"', "  ", amt, config)

    for rmesh in rmeshes:
        writeNode(fp, "        ", rmesh, amt, config)

    fp.write(
        '      </node>\n' +
        '    </visual_scene>\n' +
        '  </library_visual_scenes>\n')


_Identity = np.identity(4, float)

def writeNode(fp, pad, rmesh, amt, config):
    mat = rmesh.material
    matname = mat.name.replace(" ", "_")
    fp.write('\n%s<node id="%sObject" name="%s">\n' % (pad, rmesh.name, rmesh.name))
    writeMatrix(fp, _Identity, "transform", pad+"  ")
    fp.write(
        '%s  <instance_controller url="#%s-skin">\n' % (pad, rmesh.name) +
        '%s    <skeleton>#%sSkeleton</skeleton>\n' % (pad, amt.roots[0].name)+
        '%s    <bind_material>\n' % pad +
        '%s      <technique_common>\n' % pad +
        '%s        <instance_material symbol="%s" target="#%s">\n' % (pad, matname, matname) +
        '%s          <bind_vertex_input semantic="UVTex" input_semantic="TEXCOORD" input_set="0"/>\n' % pad +
        '%s        </instance_material>\n' % pad +
        '%s      </technique_common>\n' % pad +
        '%s    </bind_material>\n' % pad +
        '%s  </instance_controller>\n' % pad +
        '%s</node>\n' % pad)
    return


def writeBone(fp, hier, orig, extra, pad, amt, config):
    (bone, children) = hier
    bname = goodBoneName(bone.name)
    if bone:
        nameStr = 'sid="%s"' % bname
        idStr = 'id="%s" name="%s"' % (bname, bname)
    else:
        nameStr = ''
        idStr = ''

    fp.write('%s      <node %s %s type="JOINT" %s>\n' % (pad, extra, nameStr, idStr))
    writeMatrix(fp, bone.matrixRelative, "transform", pad+"        ")

    for child in children:
        writeBone(fp, child, bone.head, '', pad+'  ', amt, config)

    fp.write('%s      </node>\n' % pad)
    return


def writeMatrix(fp, mat, sid, pad):
    fp.write('%s<matrix sid="%s">\n' % (pad, sid))
    for i in range(4):
        fp.write('%s  %.5g %.5g %.5g %.5g\n' % (pad, mat[i][0], mat[i][1], mat[i][2], mat[i][3]))
    fp.write('%s</matrix>\n' % pad)


def rotateLoc(loc, config):
    return loc
    (x,y,z) = loc
    if config.rotate90X:
        yy = -z
        z = y
        y = yy
    if config.rotate90Z:
        yy = x
        x = -y
        y = yy
    return (x,y,z)


# To avoid error message about Sax FWL Error in Blender
def goodBoneName(bname):
    return bname.replace(".","_")
