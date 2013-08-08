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
import log

import gui3d
import exportutils

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

    if amt:
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
        '    <unit meter="0.1" name="meter"/>\n' +
        '    <up_axis>Y_UP</up_axis>\n' +
        '  </asset>\n')

    gui3d.app.progress(0.55, text="Exporting images")
    dae_materials.writeLibraryImages(fp, rmeshes, config)

    gui3d.app.progress(0.6, text="Exporting effects")
    dae_materials.writeLibraryEffects(fp, rmeshes, config)

    gui3d.app.progress(0.65, text="Exporting materials")
    dae_materials.writeLibraryMaterials(fp, rmeshes, config)

    gui3d.app.progress(0.7, text="Exporting controllers")
    dae_controller.writeLibraryControllers(fp, rmeshes, amt, config)

    gui3d.app.progress(0.75, text="Exporting geometry")
    dae_geometry.writeLibraryGeometry(fp, rmeshes, config)

    gui3d.app.progress(0.9, text="Exporting scene")
    dae_node.writeLibraryVisualScenes(fp, rmeshes, amt, config)

    fp.write(
        '  <scene>\n' +
        '    <instance_visual_scene url="#Scene"/>\n' +
        '  </scene>\n' +
        '</COLLADA>\n')

    fp.close()
    gui3d.app.progress(1)
    time2 = time.clock()
    log.message("Wrote Collada file in %g s: %s" % (time2-time1, filepath))
    return

