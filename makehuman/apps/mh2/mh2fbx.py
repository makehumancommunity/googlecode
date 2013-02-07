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

#fbxpath = "tools/blender26x"
#if fbxpath not in sys.path:
#    sys.path.append(fbxpath)
    
import io_fbx
# bpy must be imported after io_fbx
import bpy


def exportFbx(human, filepath, options):
    posemode.exitPoseMode()        
    posemode.enterPoseMode()
    
    cfg = exportutils.config.exportConfig(human, True, [])
    cfg.separatefolder = True
    outfile = exportutils.config.getOutFileFolder(filepath, cfg)        
    (outpath, ext) = os.path.splitext(outfile)

    log.message("Write FBX file %s" % outfile)

    rawTargets = []
    if options["expressions"]:
        shapeList = exportutils.shapekeys.readExpressionUnits(human, 0, 1)
        rawTargets += shapeList

    if options["customshapes"]:
        cfg.customshapes = True
        exportutils.custom.listCustomFiles(cfg)                            

        log.message("Custom shapes:")    
        for path,name in cfg.customShapeFiles:
            log.message("    %s", path)
            shape = exportutils.custom.readCustomTarget(path)
            target = (name,shape)
            rawTargets.append(target)

    rigfile = "data/rigs/%s.rig" % options["fbxrig"]
    stuffs = exportutils.collect.setupObjects(
        os.path.splitext(outfile)[0], 
        human, 
        rigfile, 
        rawTargets=rawTargets,
        helpers=options["helpers"], 
        hidden=options["hidden"], 
        eyebrows=options["eyebrows"], 
        lashes=options["lashes"])

    (scale, unit) = options["scale"]   

    bpy.initialize(human, cfg)
    name = os.path.splitext(os.path.basename(filepath))[0]
    boneInfo = stuffs[0].boneInfo
    rig = bpy.addRig(name, boneInfo)
    for stuff in stuffs:
        ob = bpy.addMesh(stuff.name, stuff, True)
        ob.parent = rig
        
    #name = os.path.splitext(os.path.basename(filepath))[0]
    #bpy.addMesh(name, human.meshData, False)
    
    filename = "%s.fbx" % outpath
    gui3d.app.progress(0, text="Exporting %s" % filename)
    io_fbx.fbx_export.exportFbxFile(bpy.context, filename)
    gui3d.app.progress(1)
    posemode.exitPoseMode()        
    return

