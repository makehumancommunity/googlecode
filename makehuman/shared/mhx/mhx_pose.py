#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makeinfo.human.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makeinfo.human.org/node/318)

**Coding Standards:**  See http://www.makeinfo.human.org/node/165

Abstract
--------

Pose
"""

import log

import mh2proxy
import exportutils
import armature as amtpkg

from . import rig_shoulder_25
from . import rig_arm_25
from . import rig_leg_25
from . import rig_panel_25


def writePose(fp, amt):

    fp.write("""
# --------------- Shapekeys ----------------------------- # 
""")

    proxyShapes('Cage', 'T_Cage', amt, fp)
    proxyShapes('Proxy', 'T_Proxy', amt, fp)
    proxyShapes('Clothes', 'T_Clothes', amt, fp)
    proxyShapes('Hair', 'T_Clothes', amt, fp)

    fp.write("#if toggle&T_Mesh\n")
    writeShapeKeys(fp, amt, "%sMesh" % amt.name, None)
    
    fp.write("""    
#endif

# --------------- Actions ----------------------------- # 

#if toggle&T_Armature
""")

    fp.write(
        "Pose %s\n" % amt.name +
        "end Pose\n")
    #amt.writeAllActions(fp)

    fp.write("Pose %s\n" % amt.name)
    amt.writeControlPoses(fp)
    fp.write("  ik_solver 'LEGACY' ;\nend Pose\n")

    if amt.config.rigtype == "mhx":
        fp.write("AnimationData %s True\n" % amt.name)
        amt.writeDrivers(fp)
        fp.write(
"""        
  action_blend_type 'REPLACE' ;
  action_extrapolation 'HOLD' ;
  action_influence 1 ;
  use_nla True ;
end AnimationData
""")

    fp.write("CorrectRig %s ;\n" % amt.name)

    fp.write("""
#endif 
""")

# *** material-drivers


def proxyShapes(typ, test, amt, fp):
    fp.write("#if toggle&%s\n" % test)
    for proxy in amt.proxies.values():
        if proxy.name and proxy.type == typ:
            writeShapeKeys(fp, amt, amt.name+proxy.name+"Mesh", proxy)
    fp.write("#endif\n")
        

def writeCorrectives(fp, amt, drivers, folder, landmarks, proxy, t0, t1):  
    try:
        shapeList = amt.loadedShapes[folder]
    except KeyError:
        shapeList = None
    if shapeList is None:
        shapeList = exportutils.shapekeys.readCorrectives(drivers, amt.human, folder, landmarks, t0, t1)
        amt.loadedShapes[folder] = shapeList
    for (shape, pose, lr) in shapeList:
        writeShape(fp, pose, lr, shape, 0, 1, proxy, amt.config.scale)
    

def writeShape(fp, pose, lr, shape, min, max, proxy, scale):
    fp.write(
        "ShapeKey %s %s True\n" % (pose, lr) +
        "  slider_min %.3g ;\n" % min +
        "  slider_max %.3g ;\n" % max)
    if proxy:
        pshapes = mh2proxy.getProxyShapes([("shape",shape)], proxy, scale)
        name,pshape = pshapes[0]
        print pshape
        for (pv, dr) in pshape.items():
            (dx, dy, dz) = dr
            fp.write("  sv %d %.4f %.4f %.4f ;\n" %  (pv, dx, -dz, dy))
    else:
        for (vn, dr) in shape.items():
           fp.write("  sv %d %.4f %.4f %.4f ;\n" %  (vn, scale*dr[0], -scale*dr[2], scale*dr[1]))
    fp.write("end ShapeKey\n")


def writeShapeKeys(fp, amt, name, proxy):

    isHuman = ((not proxy) or proxy.type == 'Proxy')
    isHair = (proxy and proxy.type == 'Hair')
    scale = amt.config.scale
    
    fp.write(
"#if toggle&T_Shapekeys\n" +
"ShapeKeys %s\n" % name +
"  ShapeKey Basis Sym True\n" +
"  end ShapeKey\n")

    if isHuman and amt.config.facepanel:
        shapeList = exportutils.shapekeys.readFaceShapes(amt.human, rig_panel_25.BodyLanguageShapeDrivers, 0.6, 0.7)
        for (pose, shape, lr, min, max) in shapeList:
            writeShape(fp, pose, lr, shape, min, max, proxy, scale)
    
    if isHuman and amt.config.expressions:
        try:
            shapeList = amt.loadedShapes["expressions"]
        except KeyError:
            shapeList = None
        if shapeList is None:
            shapeList = exportutils.shapekeys.readExpressionUnits(amt.human, 0.7, 0.9)
            amt.loadedShapes["expressions"] = shapeList
        for (pose, shape) in shapeList:
            writeShape(fp, pose, "Sym", shape, -1, 2, proxy, scale)
        
    if amt.config.bodyShapes and amt.config.rigtype == "mhx" and not isHair:
        writeCorrectives(fp, amt, rig_shoulder_25.ShoulderTargetDrivers, "shoulder", "shoulder", proxy, 0.88, 0.90)
        writeCorrectives(fp, amt, rig_leg_25.HipTargetDrivers, "hips", "hips", proxy, 0.90, 0.92)                
        writeCorrectives(fp, amt, rig_arm_25.ElbowTargetDrivers, "elbow", "body", proxy, 0.92, 0.94)                
        writeCorrectives(fp, amt, rig_leg_25.KneeTargetDrivers, "knee", "knee", proxy, 0.94, 0.96)                

    if isHuman:
        for path,name in amt.config.customShapeFiles:
            try:
                shape = amt.loadedShapes[path]
            except KeyError:
                shape = None
            if shape is None:
                log.message("    %s", path)
                shape = exportutils.custom.readCustomTarget(path)
                amt.loadedShapes[path] = shape
            writeShape(fp, name, "Sym", shape, -1, 2, proxy, scale)                        

    fp.write("  AnimationData None (toggle&T_Symm==0)\n")
        
    if amt.config.bodyShapes and amt.config.rigtype == "mhx" and not isHair:
        amtpkg.drivers.writeTargetDrivers(fp, rig_shoulder_25.ShoulderTargetDrivers, amt.name)
        amtpkg.drivers.writeTargetDrivers(fp, rig_leg_25.HipTargetDrivers, amt.name)
        amtpkg.drivers.writeTargetDrivers(fp, rig_arm_25.ElbowTargetDrivers, amt.name)
        amtpkg.drivers.writeTargetDrivers(fp, rig_leg_25.KneeTargetDrivers, amt.name)

        amtpkg.drivers.writeRotDiffDrivers(fp, rig_arm_25.ArmShapeDrivers, proxy)
        amtpkg.drivers.writeRotDiffDrivers(fp, rig_leg_25.LegShapeDrivers, proxy)
        #amtpkg.drivers.writeShapePropDrivers(fp, amt, rig_body_25.bodyShapes, proxy, "Mha")

    fp.write("#if toggle&T_ShapeDrivers\n")

    if isHuman:
        for path,name in amt.config.customShapeFiles:
            amtpkg.drivers.writeShapePropDrivers(fp, amt, [name], proxy, "")    

        if amt.config.expressions:
            amtpkg.drivers.writeShapePropDrivers(fp, amt, exportutils.shapekeys.ExpressionUnits, proxy, "Mhs")
            
        if amt.config.facepanel:
            amtpkg.drivers.writeShapeDrivers(fp, amt, rig_panel_25.BodyLanguageShapeDrivers, proxy)
        
        skeys = []
        for (skey, val, string, min, max) in  amt.customProps:
            skeys.append(skey)
        amtpkg.drivers.writeShapePropDrivers(fp, amt, skeys, proxy, "Mha")    
    fp.write("#endif\n")
        
    fp.write("  end AnimationData\n\n")

    if amt.config.expressions and not proxy:
        exprList = exportutils.shapekeys.readExpressionMhm("data/expressions")
        writeExpressions(fp, exprList, "Expression")        
        visemeList = exportutils.shapekeys.readExpressionMhm("data/visemes")
        writeExpressions(fp, visemeList, "Viseme")        

    fp.write(
        "  end ShapeKeys\n" +
        "#endif\n")
    return    


def writeExpressions(fp, exprList, label):
    for (name, units) in exprList:
        fp.write("  %s %s\n" % (label, name))
        for (unit, value) in units:
            fp.write("    %s %s ;\n" % (unit, value))
        fp.write("  end\n")
            
