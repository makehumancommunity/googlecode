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

MakeHuman to Collada (MakeHuman eXchange format) exporter. Collada files can be loaded into
Blender by collada_import.py.

TODO
"""

import os.path
import time
import codecs
import math
import numpy as np
import transformations as tm
import log

import gui3d
import exportutils
import posemode

from . import dae_materials
from . import dae_controller
from . import dae_geometry
from . import dae_node

#
#    Size of end bones = 1 mm
#
Delta = [0,0.01,0]


#
# exportCollada(human, filepath, config):
#

def exportCollada(human, filepath, config):
    #posemode.exitPoseMode()
    #posemode.enterPoseMode()
    gui3d.app.progress(0, text="Preparing")

    time1 = time.clock()
    config.setHuman(human)
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    rawTargets = exportutils.collect.readTargets(human, config)
    rmeshes,amt = exportutils.collect.setupObjects(
        name,
        human,
        config=config,
        rawTargets = rawTargets,
        useHelpers=config.useHelpers)

    amt.calcBindMatrices()

    gui3d.app.progress(0.5, text="Exporting %s" % filepath)

    try:
        fp = codecs.open(filepath, 'w', encoding="utf-8")
        log.message("Writing Collada file %s" % filepath)
    except:
        log.error("Unable to open file for writing %s" % filepath)

    date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())
    fp.write('<?xml version="1.0" encoding="utf-8"?>\n' +
        '<COLLADA version="1.4.0" xmlns="http://www.collada.org/2005/11/COLLADASchema">\n' +
        '  <asset>\n' +
        '    <contributor>\n' +
        '      <author>www.makehuman.org</author>\n' +
        '    </contributor>\n' +
        '    <created>%s</created>\n' % date +
        '    <modified>%s</modified>\n' % date +
        '    <unit meter="1.0" name="meter"/>\n' +
        '    <up_axis>Y_UP</up_axis>\n' +
        '  </asset>\n' +
        '  <library_images>\n')

    for rmesh in rmeshes:
        dae_materials.writeImages(fp, rmesh, config)

    fp.write(
        '  </library_images>\n' +
        '  <library_effects>\n')

    gui3d.app.progress(0.1, text="Exporting effects")
    for rmesh in rmeshes:
        dae_materials.writeEffects(fp, rmesh)

    fp.write(
        '  </library_effects>\n' +
        '  <library_materials>\n')

    gui3d.app.progress(0.2, text="Exporting materials")
    for rmesh in rmeshes:
        dae_materials.writeMaterials(fp, rmesh)

    fp.write(
        '  </library_materials>\n'+
        '  <library_controllers>\n')

    gui3d.app.progress(0.3, text="Exporting controllers")
    for rmesh in rmeshes:
        dae_controller.writeController(fp, rmesh, amt, config)

    fp.write(
        '  </library_controllers>\n'+
        '  <library_geometries>\n')

    dt = 0.4/len(rmeshes)
    t = 0.4
    for rmesh in rmeshes:
        gui3d.app.progress(t, text="Exporting %s" % rmesh.name)
        t += dt
        dae_geometry.writeGeometry(fp, rmesh, config)

    gui3d.app.progress(0.8, text="Exporting bones")
    fp.write(
        '  </library_geometries>\n\n' +
        '  <library_visual_scenes>\n' +
        '    <visual_scene id="Scene" name="Scene">\n' +
        '      <node id="%s">\n' % name +
        '        <matrix sid="transform">\n')


    if config.rotate90X:
        mat = tm.rotation_matrix(-math.pi/2, (1,0,0))
    else:
        mat = np.identity(4, float)
    if config.rotate90Z:
        rotZ = tm.rotation_matrix(math.pi/2, (0,0,1))
        mat = np.dot(mat, rotZ)
    for i in range(4):
        fp.write('          %.4f %.4f %.4f %.4f\n' % (mat[i][0], mat[i][1], mat[i][2], mat[i][3]))

    fp.write('        </matrix>\n')

    for root in amt.hierarchy:
        dae_node.writeBone(fp, root, [0,0,0], 'layer="L1"', '    ', amt, config)

    gui3d.app.progress(0.9, text="Exporting nodes")
    for rmesh in rmeshes:
        dae_node.writeNode(fp, "        ", rmesh, amt, config)

    fp.write(
        '      </node>\n' +
        '    </visual_scene>\n' +
        '  </library_visual_scenes>\n' +
        '  <scene>\n' +
        '    <instance_visual_scene url="#Scene"/>\n' +
        '  </scene>\n' +
        '</COLLADA>\n')

    fp.close()
    time2 = time.clock()
    log.message("Wrote Collada file in %g s: %s" % (time2-time1, filepath))
    gui3d.app.progress(1)
    #posemode.exitPoseMode()
    return

