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
Fbx exporter

"""

import os.path
import sys

import gui3d
import exportutils
import posemode
import log

import io_fbx
# bpy must be imported after io_fbx
import bpy


def exportFbx(human, filepath, config):
    posemode.exitPoseMode()        
    posemode.enterPoseMode()
    
    config.addObjects(human)
    config.setupTexFolder(filepath)        

    log.message("Write FBX file %s" % filepath)
    print(config)

    rigfile = "data/rigs/%s.rig" % config.rigtype
    rawTargets = exportutils.collect.readTargets(human, config)
    stuffs = exportutils.collect.setupObjects(
        os.path.splitext(filepath)[0], 
        human, 
        config=config,
        rigfile=rigfile, 
        rawTargets=rawTargets,
        helpers=config.helpers, 
        hidden=config.hidden, 
        eyebrows=config.eyebrows, 
        lashes=config.lashes)

    bpy.initialize(human, config)
    name = os.path.splitext(os.path.basename(filepath))[0]
    boneInfo = stuffs[0].boneInfo
    rig = bpy.addRig(name, boneInfo)
    for stuff in stuffs:
        ob = bpy.addMesh(stuff.name, stuff, rig, True)
        
    #name = os.path.splitext(os.path.basename(filepath))[0]
    #bpy.addMesh(name, human.meshData, False)
    
    gui3d.app.progress(0, text="Exporting %s" % filepath)
    io_fbx.fbx_export.exportFbxFile(bpy.context, filepath, 1.0)
    gui3d.app.progress(1)
    posemode.exitPoseMode()        
    return

