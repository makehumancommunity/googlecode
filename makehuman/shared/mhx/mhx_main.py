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

MakeHuman to MHX (MakeHuman eXchange format) exporter. MHX files can be loaded into Blender
"""

MAJOR_VERSION = 1
MINOR_VERSION = 14
BODY_LANGUAGE = True

import module3d
import gui3d
import os
import time
import numpy
import math
import log

#import cProfile

import mh2proxy
import exportutils
import armature as amtpkg
import warpmodifier
import posemode
import exportutils


import armature as amtpkg
from armature.flags import *
from armature.rigdefs import CArmature

from . import posebone
from . import rig_body_25
from . import rig_shoulder_25
from . import rig_arm_25
from . import rig_finger_25
from . import rig_leg_25
from . import rig_toe_25
from . import rig_face_25
from . import rig_panel_25
from . import rig_skirt_25
from . import rigify_rig

#
#    exportMhx(human, filepath, config):
#

def exportMhx(human, filepath, config):  
    time1 = time.clock()
    posemode.exitPoseMode()        
    posemode.enterPoseMode()
    
    config.setHuman(human)
    config.setupTexFolder(filepath)    

    fname = os.path.basename(os.path.splitext(filepath)[0])
    name = fname.capitalize().replace(' ','_')
    try:
        fp = open(filepath, 'w')
        log.message("Writing MHX file %s", filepath)
    except:
        log.message("Unable to open file for writing %s", filepath)
        fp = 0
    if fp:
        if config.rigtype == 'mhx':
            amt = MhxArmature(name, human, config)
        elif config.rigtype == 'rigify':
            amt = RigifyArmature(name, human, config)
        else:
            amt = ExportArmature(name, human, config)

        exportMhx_25(amt, fp)
        fp.close()
        time2 = time.clock()
        log.message("Wrote MHX file in %g s: %s", time2-time1, filepath)

    posemode.exitPoseMode()        
    return        


def exportMhx_25(amt, fp):
    gui3d.app.progress(0, text="Exporting MHX")
    log.message("Export MHX")
    
    fp.write(
        "# MakeHuman exported MHX\n" +
        "# www.makeinfo.human.org\n" +
        "MHX %d %d ;\n" % (MAJOR_VERSION, MINOR_VERSION) +
        "#if Blender24\n" +
        "  error 'This file can only be read with Blender 2.5' ;\n" +
        "#endif\n")

    amt.scanProxies()
    amt.setup()
    
    if not amt.config.cage:
        fp.write(
            "#if toggle&T_Cage\n" +
            "  error 'This MHX file does not contain a cage. Unselect the Cage import option.' ;\n" +
            "#endif\n")

    fp.write(
        "NoScale True ;\n" +
        "Object CustomShapes EMPTY None\n" +
        "  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n" +
        "end Object\n\n")

    amt.setupCustomShapes(fp)
        
    gui3d.app.progress(0.1, text="Exporting amtpkg")
    copyFile25("shared/mhx/templates/rig-armature25.mhx", fp, None, amt)    
    
    gui3d.app.progress(0.15, text="Exporting materials")    
    fp.write("\nNoScale False ;\n\n")
    if amt.human.uvset:
        writeMultiMaterials(amt, fp)
    else:
        copyFile25("shared/mhx/templates/materials25.mhx", fp, None, amt)    

    if amt.config.cage:
        proxyCopy('Cage', 'T_Cage', amt, fp, 0.2, 0.25)
    
    gui3d.app.progress(0.25, text="Exporting main mesh")    
    fp.write("#if toggle&T_Mesh\n")
    copyFile25("shared/mhx/templates/meshes25.mhx", fp, None, amt)    
    fp.write("#endif\n")

    proxyCopy('Proxy', 'T_Proxy', amt, fp, 0.35, 0.4)
    proxyCopy('Clothes', 'T_Clothes', amt, fp, 0.4, 0.55)
    proxyCopy('Hair', 'T_Clothes', amt, fp, 0.55, 0.6)

    copyFile25("shared/mhx/templates/rig-poses25.mhx", fp, None, amt) 

    if amt.config.rigtype == 'rigify':
        fp.write("Rigify %s ;\n" % amt.name)

    gui3d.app.progress(1.0)
    return
    

def proxyCopy(type, test, amt, fp, t0, t1):
    n = 0
    for proxy in amt.proxies.values():
        if proxy.type == type:
            n += 1
    if n == 0:
        return
        
    dt = (t1-t0)/n
    t = t0
    for proxy in amt.proxies.values():
        if proxy.type == type:
            gui3d.app.progress(t, text="Exporting %s" % proxy.name)
            fp.write("#if toggle&%s\n" % test)
            copyFile25("shared/mhx/templates/proxy25.mhx", fp, proxy, amt)    
            fp.write("#endif\n")
            t += dt
        
#
#    copyFile25(tmplName, fp, proxy, amt):
#

def copyFile25(tmplName, fp, proxy, amt):
    tmpl = open(tmplName)
    if tmpl == None:
        log.error("*** Cannot open %s", tmplName)
        return

    bone = None
    config = amt.config
    #faces = loadFacesIndices(amt.mesh)
    ignoreLine = False
    for line in tmpl:
        words= line.split()
        if len(words) == 0:
            fp.write(line)
        elif words[0] == '***':
            key = words[1]

            if key == 'refer-human':
                if len(words) > 3:
                    suffix = words[3]
                else:
                    suffix = ""
                fp.write("    %s Refer Object %s%s ;\n" % (words[2], amt.name, suffix))

            elif key == 'rig-bones':
                fp.write("Armature %s %s   Normal \n" % (amt.name, amt.name))
                amt.writeArmature(fp)

            elif key == 'human-object':
                if words[2] == 'Mesh':
                    fp.write(
                        "Object %sMesh MESH %sMesh\n"  % (amt.name, amt.name) +
                        "  Property MhxOffsetX %.4f ;\n" % amt.origin[0] +
                        "  Property MhxOffsetY %.4f ;\n" % amt.origin[1] +
                        "  Property MhxOffsetZ %.4f ;\n" % amt.origin[2])
                elif words[2] == 'ControlRig':
                    fp.write(
                        "Object %s ARMATURE %s\n"  % (amt.name, amt.name) +
                        "  Property MhxVersion %d ;\n" % MINOR_VERSION)

            elif key == 'rig-poses':
                fp.write("Pose %s\n" % amt.name)
                amt.writeControlPoses(fp)
                fp.write("  ik_solver 'LEGACY' ;\nend Pose\n")

            elif key == 'rig-actions':
                fp.write("Pose %s\nend Pose\n" % amt.name)
                amt.writeAllActions(fp)

            elif key == 'if-true':
                value = eval(words[2])
                log.debug("if %s %s", words[2], value)
                fp.write("#if %s\n" % value)

            elif key == 'rig-drivers':
                if amt.config.rigtype == "mhx":
                    fp.write("AnimationData %s True\n" % amt.name)
                    amt.writeDrivers(fp)
                    rigDriversEnd(fp)

            elif key == 'rig-correct':
                fp.write("CorrectRig %s ;\n" % amt.name)

            elif key == 'recalc-roll':
                if amt.config.rigtype == "mhx":
                    fp.write("  RecalcRoll %s ;\n" % amt.config.recalcRoll)

            elif key == 'ProxyMesh':
                writeProxyMesh(fp, amt, proxy)

            elif key == 'ProxyObject':
                writeProxyObject(fp, amt, proxy)

            elif key == 'ProxyLayers':
                fp.write("layers Array ")
                for n in range(20):
                    if n == proxy.layer:
                        fp.write("1 ")
                    else:
                        fp.write("0 ")
                fp.write(";\n")

            elif key == 'MeshAnimationData':
                writeHideAnimationData(fp, amt, "", amt.name)

            elif key == 'ProxyAnimationData':
                writeHideAnimationData(fp, amt, amt.name, proxy.name)

            elif key == 'toggleCage':
                if proxy and proxy.cage:
                    fp.write(
                    "  draw_type 'WIRE' ;\n" +
                    "  #if False\n")
                elif amt.config.cage:                    
                    fp.write("  #if toggle&T_Cage\n")
                else:
                    fp.write("  #if False\n")

            elif key == 'ProxyVerts':
                ox = amt.origin[0]
                oy = amt.origin[1]
                oz = amt.origin[2]
                scale = amt.config.scale
                for refVert in proxy.refVerts:
                    (x,y,z) = refVert.getCoord()
                    fp.write("  v %.4f %.4f %.4f ;\n" % (scale*(x-ox), scale*(-z+oz), scale*(y-oy)))

            elif key == 'Verts':
                proxy = None
                fp.write("Mesh %sMesh %sMesh\n  Verts\n" % (amt.name, amt.name))
                ox = amt.origin[0]
                oy = amt.origin[1]
                oz = amt.origin[2]
                scale = amt.config.scale
                for co in amt.mesh.coord:
                    fp.write("  v %.4f %.4f %.4f ;\n" % (scale*(co[0]-ox), scale*(-co[2]+oz), scale*(co[1]-oy)))

            elif key == 'ProxyFaces':
                for (f,g) in proxy.faces:
                    fp.write("    f")
                    for v in f:
                        fp.write(" %s" % v)
                    fp.write(" ;\n")
                if proxy.faceNumbers:
                    for ftn in proxy.faceNumbers:
                        fp.write(ftn)
                else:
                    fp.write("    ftall 0 1 ;\n")

            elif key == 'Faces':
                for fverts in amt.mesh.fvert:
                    if fverts[0] == fverts[3]:
                        fp.write("    f %d %d %d ;\n" % tuple(fverts[0:3]))
                    else:
                        fp.write("    f %d %d %d %d ;\n" % tuple(fverts))
                fp.write("#if False\n")

            elif key == 'EndFaces':
                writeFaceNumbers(fp, amt)

            elif key == 'FTTriangles':
                pass
                #for f in amt.mesh.faces:
                #    if f.isTriangle():
                #        fp.write("    mn %d 1 ;\n" % f.idx)

            elif key == 'ProxyUVCoords':
                layers = list(proxy.uvtexLayerName.keys())
                layers.sort()
                for layer in layers:
                    try:
                        texfaces = proxy.texFacesLayers[layer]
                        texverts = proxy.texVertsLayers[layer]
                    except KeyError:
                        continue
                    fp.write(                   
                        '  MeshTextureFaceLayer %s\n' % proxy.uvtexLayerName[layer] +
                        '    Data \n')
                    for f in texfaces:
                        fp.write("    vt")
                        for v in f:
                            uv = texverts[v]
                            fp.write(" %.4g %.4g" % (uv[0], uv[1]))
                        fp.write(" ;\n")
                    fp.write(
                        '    end Data\n' +
                        '  end MeshTextureFaceLayer\n')

            elif key == 'TexVerts':
                if amt.human.uvset:
                    for ft in amt.human.uvset.texFaces:
                        fp.write("    vt")
                        for vt in ft:
                            uv = amt.human.uvset.texVerts[vt]
                            fp.write(" %.4g %.4g" %(uv[0], uv[1]))
                        fp.write(" ;\n")
                else:
                    for fuv in amt.mesh.fuvs:
                        uv0 = amt.mesh.texco[fuv[0]]
                        uv1 = amt.mesh.texco[fuv[1]]
                        uv2 = amt.mesh.texco[fuv[2]]
                        uv3 = amt.mesh.texco[fuv[3]]
                        if fuv[0] == fuv[3]:
                            fp.write("    vt %.4g %.4g %.4g %.4g %.4g %.4g ;\n" % (uv0[0], uv0[1], uv1[0], uv1[1], uv2[0], uv2[1]))
                        else:
                            fp.write("    vt %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g ;\n" % (uv0[0], uv0[1], uv1[0], uv1[1], uv2[0], uv2[1], uv3[0], uv3[1]))

            elif key == 'Material':
                fp.write("Material %s%s\n" % (amt.name, words[2]))

            elif key == 'Materials':
                writeBaseMaterials(fp, amt)

            elif key == 'ProxyMaterials':
                if proxy.useBaseMaterials:
                    writeBaseMaterials(fp, amt)
                elif proxy.material:
                    fp.write("  Material %s%s ;\n" % (amt.name, proxy.material.name))

            elif key == 'VertexGroup':
                writeVertexGroups(fp, amt, proxy)

            elif key == 'group':
                writeGroups(fp, amt)

            elif key == 'mesh-shapeKey':
                writeShapeKeys(fp, amt, "%sMesh" % amt.name, None)

            elif key == 'proxy-shapeKey':
                proxyShapes('Cage', 'T_Cage', amt, fp)
                proxyShapes('Proxy', 'T_Proxy', amt, fp)
                proxyShapes('Clothes', 'T_Clothes', amt, fp)
                proxyShapes('Hair', 'T_Clothes', amt, fp)

            elif key == 'ProxyModifiers':
                writeProxyModifiers(fp, amt, proxy)

            elif key == 'MTex':
                n = nMasks + int(words[2])
                fp.write("  MTex %d %s %s %s\n" % (n, words[3], words[4], words[5]))

            elif key == 'SkinStart':
                nMasks = writeSkinStart(fp, proxy, amt)

            elif key == 'curves':
                amt.writeCurves(fp)

            elif key == 'properties':
                amt.writeProperties(fp, words[2])
                writeHideProp(fp, amt.name)
                for proxy in amt.proxies.values():
                    writeHideProp(fp, proxy.name)
                if amt.config.useCustomShapes: 
                    exportutils.custom.listCustomFiles(amt.config)                            
                for path,name in amt.config.customShapeFiles:
                    fp.write("  DefProp Float %s 0 %s  min=-1.0,max=2.0 ;\n" % (name, name[3:]))

            elif key == 'material-drivers':
                fp.write("  use_textures Array")
                for n in range(nMasks):
                    fp.write(" 1")
                for n in range(3):
                    fp.write(" 1")
                fp.write(" ;\n")
                fp.write("  AnimationData %sMesh True\n" % amt.name)
                #amtpkg.drivers.writeTextureDrivers(fp, rig_panel_25.BodyLanguageTextureDrivers)
                writeMaskDrivers(fp, amt)
                fp.write("  end AnimationData\n")

            elif key == 'Filename':
                file = amt.config.getTexturePath(words[2], words[3], True, amt.human)
                fp.write("  Filename %s ;\n" % file)

            else:
                raise NameError("Unknown *** %s" % words[1])
        else:
            fp.write(line)

    log.message("    %s copied", tmplName)
    tmpl.close()

    return

#
#   writeFaceNumbers(fp, amt):
#

MaterialNumbers = {
    ""       : 0,     # skin
    "skin"   : 0,     # skin
    "nail"   : 0,     # nail
    "teeth"  : 1,     # teeth
    "eye"    : 2,     # eye
    "cornea" : 2,     # cornea
    "brow"   : 3,     # brows
    "joint"  : 4,     # joint
    "red"    : 5,     # red
    "green"  : 6,     # green
    "blue"   : 7      # blue
}
    
def writeFaceNumbers(fp, amt):
    fp.write("#else\n")
    if amt.human.uvset:
        for ftn in amt.human.uvset.faceNumbers:
            fp.write(ftn)
    else:            
        obj = amt.mesh
        fmats = numpy.zeros(len(obj.coord), int)
        for fn,mtl in obj.materials.items():
            fmats[fn] = MaterialNumbers[mtl]
            
        if amt.config.hidden:
            deleteVerts = None
            deleteGroups = []
        else:
            deleteGroups = []
            deleteVerts = numpy.zeros(len(obj.coord), bool)
            for proxy in amt.proxies.values():
                deleteGroups += proxy.deleteGroups
                deleteVerts = deleteVerts | proxy.deleteVerts
                    
        for fg in obj.faceGroups: 
            fmask = obj.getFaceMaskForGroups([fg.name])
            if mh2proxy.deleteGroup(fg.name, deleteGroups):
                fmats[fmask] = 6
            elif "joint" in fg.name:
                fmats[fmask] = 4
            elif fg.name == "helper-tights":                    
                fmats[fmask] = 5
            elif fg.name == "helper-skirt":                    
                fmats[fmask] = 7
            elif ("tongue" in fg.name):
                fmats[fmask] = 1
            elif ("eyebrown" in fg.name) or ("lash" in fg.name):
                fmats[fmask] = 3
                    
        if deleteVerts != None:
            for fn,fverts in enumerate(obj.fvert):
                if deleteVerts[fverts[0]]:
                    fmats[fn] = 6                        
                
        mn = -1
        fn = 0
        f0 = 0
        for fverts in obj.fvert:
            if fmats[fn] != mn:
                if fn != f0:
                    fp.write("  ftn %d %d 1 ;\n" % (fn-f0, mn))
                mn = fmats[fn]
                f0 = fn
            fn += 1
        if fn != f0:
            fp.write("  ftn %d %d 1 ;\n" % (fn-f0, mn))
    fp.write("#endif\n")

def writeBaseMaterials(fp, amt):      
    if amt.human.uvset:
        for mat in amt.human.uvset.materials:
            fp.write("  Material %s_%s ;\n" % (amt.name, mat.name))
    else:
        fp.write(
"  Material %sSkin ;\n" % amt.name +
"  Material %sMouth ;\n" % amt.name +
"  Material %sEye ;\n" % amt.name +
"  Material %sBrows ;\n" % amt.name +
"  Material %sInvisio ;\n" % amt.name +
"  Material %sRed ;\n" % amt.name +
"  Material %sGreen ;\n" % amt.name +
"  Material %sBlue ;\n" % amt.name
)
    
def addMaskImage(fp, amt, mask):            
    (folder, file) = mask
    path = amt.config.getTexturePath(file, folder, True, amt.human)
    fp.write(
"Image %s\n" % file +
"  Filename %s ;\n" % path +
#"  alpha_mode 'PREMUL' ;\n" +
"end Image\n\n" +
"Texture %s IMAGE\n" % file  +
"  Image %s ;\n" % file +
"end Texture\n\n")
    return
    
def addMaskMTex(fp, mask, proxy, blendtype, n):            
    if proxy:
        try:
            uvLayer = proxy.uvtexLayerName[proxy.maskLayer]
        except KeyError:
            return n

    (dir, file) = mask
    fp.write(
"  MTex %d %s UV ALPHA\n" % (n, file) +
"    texture Refer Texture %s ;\n" % file +
"    use_map_alpha True ;\n" +
"    use_map_color_diffuse False ;\n" +
"    alpha_factor 1 ;\n" +
"    blend_type '%s' ;\n" % blendtype +
"    mapping 'FLAT' ;\n" +
"    invert True ;\n" +
"    use_stencil True ;\n" +
"    use_rgb_to_intensity True ;\n")
    if proxy:
        fp.write("    uv_layer '%s' ;\n" %  uvLayer)
    fp.write("  end MTex\n")
    return n+1


def writeSkinStart(fp, proxy, amt):
    if not amt.config.useMasks:
        fp.write("Material %sSkin\n" % amt.name)
        return 0
        
    if proxy:
        fp.write("Material %s%sSkin\n" % (amt.name, proxy.name))
        return 0

    nMasks = 0
    prxList = list(amt.proxies.values())
    
    for prx in prxList:
        if prx.mask:
            addMaskImage(fp, amt, prx.mask)
            nMasks += 1
    fp.write("Material %sSkin\n" % amt.name)
             #"  MTex 0 diffuse UV COLOR\n" +
             #"    texture Refer Texture diffuse ;\n" +
             #"  end MTex\n"

    n = 0    
    for prx in prxList:
        if prx.mask:
            n = addMaskMTex(fp, prx.mask, proxy, 'MULTIPLY', n)
            
    return nMasks
               

def writeMaskDrivers(fp, amt):
    if not amt.config.useMasks:
        return
    fp.write("#if toggle&T_Clothes\n")
    n = 0
    for prx in amt.proxies.values():
        if prx.type == 'Clothes' and prx.mask:
            (dir, file) = prx.mask
            amtpkg.drivers.writePropDriver(fp, amt, ["Mhh%s" % prx.name], "1-x1", 'use_textures', n)
            n += 1            
    fp.write("#endif\n")
    return
    

def writeVertexGroups(fp, amt, proxy):                
    if proxy and proxy.weights:
        writeRigWeights(fp, proxy.weights)
        return

    if amt.vertexWeights:
        if proxy:
            weights = mh2proxy.getProxyWeights(amt.vertexWeights, proxy)
        else:
            weights = amt.vertexWeights                    
        writeRigWeights(fp, weights)
    else:
        for file in amt.vertexGroupFiles:
            copyVertexGroups(file, fp, proxy)
            
    #for path in amt.config.customvertexgroups:
    #    print("    %s" % path)
    #    copyVertexGroups(path, fp, proxy)    

    if amt.config.cage and not (proxy and proxy.cage):
        fp.write("#if toggle&T_Cage\n")
        copyVertexGroups("cage", fp, proxy)    
        fp.write("#endif\n")

    copyVertexGroups("leftright", fp, proxy)    
    copyVertexGroups("tight-leftright", fp, proxy)    
    copyVertexGroups("skirt-leftright", fp, proxy)    
    return
    

def rigDriversEnd(fp):                                        
    fp.write(
        "  action_blend_type 'REPLACE' ;\n" +
        "  action_extrapolation 'HOLD' ;\n" +
        "  action_influence 1 ;\n" +
        "  use_nla True ;\n" +
        "end AnimationData\n")


def writeGroups(fp, amt):                
    fp.write(
        "PostProcess %sMesh %s 0000003f 00080000 0068056b 0000c000 ;\n" % (amt.name, amt.name) + 
        "Group %s\n"  % amt.name +
        "  Objects\n" +
        "    ob %s ;\n" % amt.name +
        "#if toggle&T_Mesh\n" +
        "    ob %sMesh ;\n" % amt.name +
        "#endif\n")
    groupProxy('Cage', 'T_Cage', fp, amt)
    groupProxy('Proxy', 'T_Proxy', fp, amt)
    groupProxy('Clothes', 'T_Clothes', fp, amt)
    groupProxy('Hair', 'T_Clothes', fp, amt)
    fp.write(
        "    ob CustomShapes ;\n" + 
        "  end Objects\n" +
        "  layers Array 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1  ;\n" +
        "end Group\n")
    return
    
def groupProxy(typ, test, fp, amt):
    fp.write("#if toggle&%s\n" % test)
    for proxy in amt.proxies.values():
        if proxy.type == typ:
            name = amt.name + proxy.name
            fp.write("    ob %sMesh ;\n" % name)
    fp.write("#endif\n")
    return

def writeProxyMesh(fp, amt, proxy):                
    mat = proxy.material
    if mat:
        if proxy.material_file:
            copyProxyMaterialFile(fp, proxy.material_file, mat, proxy, amt)
        else:
            writeProxyMaterial(fp, mat, proxy, amt)
    name = amt.name + proxy.name
    fp.write("Mesh %sMesh %sMesh \n" % (name, name))
    return


def writeProxyObject(fp, amt, proxy): 
    name = amt.name + proxy.name
    fp.write(
        "Object %sMesh MESH %sMesh \n" % (name, name) +
        "  parent Refer Object %s ;\n" % amt.name +
        "  hide False ;\n" +
        "  hide_render False ;\n")
    if proxy.wire:
        fp.write("  draw_type 'WIRE' ;\n")    
    return


def writeProxyModifiers(fp, amt, proxy):
    for mod in proxy.modifiers:
        if mod[0] == 'subsurf':
            fp.write(
                "    Modifier SubSurf SUBSURF\n" +
                "      levels %d ;\n" % mod[1] +
                "      render_levels %d ;\n" % mod[2] +
                "    end Modifier\n")
        elif mod[0] == 'shrinkwrap':
            offset = mod[1]
            fp.write(
                "    Modifier ShrinkWrap SHRINKWRAP\n" +
                "      target Refer Object %sMesh ;\n" % amt.name +
                "      offset %.4f ;\n" % offset +
                "      use_keep_above_surface True ;\n" +
                "    end Modifier\n")
        elif mod[0] == 'solidify':
            thickness = mod[1]
            offset = mod[2]
            fp.write(
                "    Modifier Solidify SOLIDIFY\n" +
                "      thickness %.4f ;\n" % thickness +
                "      offset %.4f ;\n" % offset +
                "    end Modifier\n")
    return


def writeHideProp(fp, name):                
    fp.write("  DefProp Bool Mhh%s False Control_%s_visibility ;\n" % (name, name))
    return


def writeHideAnimationData(fp, amt, prefix, name):
    fp.write("AnimationData %s%sMesh True\n" % (prefix, name))
    amtpkg.drivers.writePropDriver(fp, amt, ["Mhh%s" % name], "x1", "hide", -1)
    amtpkg.drivers.writePropDriver(fp, amt, ["Mhh%s" % name], "x1", "hide_render", -1)
    fp.write("end AnimationData\n")
    return    
       

def copyProxyMaterialFile(fp, pair, mat, proxy, amt):
    prxList = sortedMasks(amt)
    nMasks = countMasks(proxy, prxList)
    tex = None
    
    (folder, file) = pair
    folder = os.path.realpath(os.path.expanduser(folder))
    infile = os.path.join(folder, file)
    tmpl = open(infile, "rU")
    for line in tmpl:
        words= line.split()
        if len(words) == 0:
            fp.write(line)
        elif words[0] == 'Texture':
            words[1] = amt.name + words[1]
            for word in words:
                fp.write("%s " % word)
            fp.write("\n")
            tex = os.path.join(folder,words[1])
        elif words[0] == 'Material':
            words[1] = amt.name + words[1]
            for word in words:
                fp.write("%s " % word)
            fp.write("\n")
            addProxyMaskMTexs(fp, mat, proxy, prxList, tex)
        elif words[0] == 'MTex':
            words[2] = amt.name + words[2]
            for word in words:
                fp.write("%s " % word)
            fp.write("\n")                
        elif words[0] == 'Filename':
            file = amt.config.getTexturePath(words[1], folder, True, amt.human)
            fp.write("  Filename %s ;\n" % file)
        else:
            fp.write(line)
    tmpl.close()
    return
       

def writeProxyTexture(fp, texture, mat, extra, amt):        
    (folder,name) = texture
    tex = os.path.join(folder,name)
    #print(amt.name)
    log.debug("Tex %s", tex)
    texname = amt.name + os.path.basename(tex)
    fromDir = os.path.dirname(tex)
    texfile = amt.config.getTexturePath(tex, fromDir, True, None)
    fp.write(
        "Image %s\n" % texname +
        "  Filename %s ;\n" % texfile +
#        "  alpha_mode 'PREMUL' ;\n" +
        "end Image\n\n" +
        "Texture %s IMAGE\n" % texname +
        "  Image %s ;\n" % texname)
    writeProxyMaterialSettings(fp, mat.textureSettings)             
    fp.write(extra)
    fp.write("end Texture\n\n")
    return (tex, texname)
    
    
def writeProxyMaterial(fp, mat, proxy, amt):
    alpha = mat.alpha
    tex = None
    bump = None
    normal = None
    displacement = None
    transparency = None
    if proxy.texture:
        uuid = proxy.getUuid()
        if uuid in amt.human.clothesObjs.keys() and amt.human.clothesObjs[uuid]:
            # Apply custom texture
            clothesObj = amt.human.clothesObjs[uuid]
            texture = clothesObj.mesh.texture
            texPath = (os.path.dirname(texture), os.path.basename(texture))
            (tex,texname) = writeProxyTexture(fp, texPath, mat, "", amt)
        else:
            (tex,texname) = writeProxyTexture(fp, proxy.texture, mat, "", amt)
    if proxy.bump:
        (bump,bumpname) = writeProxyTexture(fp, proxy.bump, mat, "", amt)
    if proxy.normal:
        (normal,normalname) = writeProxyTexture(fp, proxy.normal, mat, 
            ("    use_normal_map True ;\n"),
            amt)
    if proxy.displacement:
        (displacement,dispname) = writeProxyTexture(fp, proxy.displacement, mat, "", amt)
    if proxy.transparency:
        (transparency,transname) = writeProxyTexture(fp, proxy.transparency, mat, "", amt)
           
    prxList = sortedMasks(amt)
    nMasks = countMasks(proxy, prxList)
    slot = nMasks
    
    fp.write("Material %s%s \n" % (amt.name, mat.name))
    addProxyMaskMTexs(fp, mat, proxy, prxList, tex)
    writeProxyMaterialSettings(fp, mat.settings)   
    uvlayer = proxy.uvtexLayerName[proxy.textureLayer]

    if tex:
        fp.write(
            "  MTex %d %s UV COLOR\n" % (slot, texname) +
            "    texture Refer Texture %s ;\n" % texname +
            "    use_map_alpha True ;\n" +
            "    diffuse_color_factor 1.0 ;\n" +
            "    uv_layer '%s' ;\n" % uvlayer)
        writeProxyMaterialSettings(fp, mat.mtexSettings)             
        fp.write("  end MTex\n")
        slot += 1
        alpha = 0
        
    if bump:
        fp.write(
            "  MTex %d %s UV NORMAL\n" % (slot, bumpname) +
            "    texture Refer Texture %s ;\n" % bumpname +
            "    use_map_normal True ;\n" +
            "    use_map_color_diffuse False ;\n" +
            "    normal_factor %.3f ;\n" % proxy.bumpStrength + 
            "    use_rgb_to_intensity True ;\n" +
            "    uv_layer '%s' ;\n" % uvlayer +
            "  end MTex\n")
        slot += 1
        
    if normal:
        fp.write(
            "  MTex %d %s UV NORMAL\n" % (slot, normalname) +
            "    texture Refer Texture %s ;\n" % normalname +
            "    use_map_normal True ;\n" +
            "    use_map_color_diffuse False ;\n" +
            "    normal_factor %.3f ;\n" % proxy.normalStrength + 
            "    normal_map_space 'TANGENT' ;\n" +
            "    uv_layer '%s' ;\n" % uvlayer +
            "  end MTex\n")
        slot += 1
        
    if displacement:
        fp.write(
"  MTex %d %s UV DISPLACEMENT\n" % (slot, dispname) +
"    texture Refer Texture %s ;\n" % dispname +
"    use_map_displacement True ;\n" +
"    use_map_color_diffuse False ;\n" +
"    displacement_factor %.3f ;\n" % proxy.dispStrength + 
"    use_rgb_to_intensity True ;\n" +
"    uv_layer '%s' ;\n" % uvlayer +
"  end MTex\n")
        slot += 1

    if transparency:        
        fp.write(
"  MTex %d %s UV ALPHA\n" % (slot, transname) +
"    texture Refer Texture %s ;\n" % transname +
"    use_map_alpha True ;\n" +
"    use_map_color_diffuse False ;\n" +
"    invert True ;\n" +
"    use_stencil True ;\n" +
"    use_rgb_to_intensity True ;\n" +
"    uv_layer '%s' ;\n" % uvlayer +
"  end MTex\n")
        slot += 1        
        
    if nMasks > 0 or alpha < 0.99:
        fp.write(
"  use_transparency True ;\n" +
"  transparency_method 'Z_TRANSPARENCY' ;\n" +
"  alpha %3.f ;\n" % alpha +
"  specular_alpha %.3f ;\n" % alpha)
    if mat.mtexSettings == []:
        fp.write(
"  use_shadows True ;\n" +
"  use_transparent_shadows True ;\n")
    fp.write(
"  Property MhxDriven True ;\n" +
"end Material\n\n")

def writeProxyMaterialSettings(fp, settings):
    for (key, value) in settings:        
        if type(value) == list:
            fp.write("  %s Array %.4f %.4f %.4f ;\n" % (key, value[0], value[1], value[2]))
        elif type(value) == float:
            fp.write("  %s %.4f ;\n" % (key, value))
        elif type(value) == int:
            fp.write("  %s %d ;\n" % (key, value))
        else:
            fp.write("  %s '%s' ;\n" % (key, value))

def addProxyMaskMTexs(fp, mat, proxy, prxList, tex):
    n = 0  
    m = len(prxList)
    for (zdepth, prx) in prxList:
        m -= 1
        if zdepth > proxy.z_depth:
            n = addMaskMTex(fp, prx.mask, proxy, 'MULTIPLY', n)
    if not tex:            
        n = addMaskMTex(fp, (None,'solid'), proxy, 'MIX', n)
    return   
    
def sortedMasks(amt):
    if not amt.config.useMasks:
        return []
    prxList = []
    for prx in amt.proxies.values():
        if prx.type == 'Clothes' and prx.mask:
            prxList.append((prx.z_depth, prx))
    prxList.sort()
    return prxList
    
def countMasks(proxy, prxList):
    n = 0
    for (zdepth, prx) in prxList:
        if prx.type == 'Clothes' and zdepth > proxy.z_depth:
            n += 1
    return n            

#
#    copyVertexGroups(name, fp, proxy):
#

def getVertexGroups(name, vgroups):
    file = os.path.join("shared/mhx/vertexgroups", name + ".vgrp")
    fp = open(file, "rU")
    vgroupList = []
    for line in fp:
        words = line.split()
        if len(words) < 2:
            continue
        elif words[1] == "weights":
            name = words[2]
            try:
                vgroup = vgroups[name]
            except KeyError:
                vgroup = []
                vgroups[name] = vgroup 
            vgroupList.append((name, vgroup))
        else:
            vgroup.append((int(words[0]), float(words[1])))
    fp.close()            
    return vgroupList            


def copyVertexGroups(name, fp, proxy):
    vgroupList = getVertexGroups(name, {})
    if not proxy:
        for (name, weights) in vgroupList:
            fp.write("  VertexGroup %s\n" % name)
            for (v,wt) in weights:
                fp.write("    wv %d %.4g ;\n" % (v,wt))
            fp.write("  end VertexGroup\n\n")
    else:
        for (name, weights) in vgroupList:
            pgroup = []
            for (v,wt) in weights:
                try:
                    vlist = proxy.vertWeights[v]
                except:
                    vlist = []
                for (pv, w) in vlist:
                    pw = w*wt
                    if pw > 1e-4:
                        pgroup.append((pv, pw))
            if pgroup:
                fp.write("  VertexGroup %s\n" % name)
                printProxyVGroup(fp, pgroup)
                fp.write("  end VertexGroup\n\n")
    
#
#    printProxyVGroup(fp, vgroups):
#

def printProxyVGroup(fp, vgroups):
    vgroups.sort()
    pv = -1
    while vgroups:
        (pv0, wt0) = vgroups.pop()
        if pv0 == pv:
            wt += wt0
        else:
            if pv >= 0 and wt > 1e-4:
                fp.write("    wv %d %.4f ;\n" % (pv, wt))
            (pv, wt) = (pv0, wt0)
    if pv >= 0 and wt > 1e-4:
        fp.write("    wv %d %.4f ;\n" % (pv, wt))
    return



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
        for (skey, val, string, min, max) in  amt.config.customProps:
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
            

def proxyShapes(typ, test, amt, fp):
    fp.write("#if toggle&%s\n" % test)
    for proxy in amt.proxies.values():
        if proxy.name and proxy.type == typ:
            writeShapeKeys(fp, amt, amt.name+proxy.name+"Mesh", proxy)
    fp.write("#endif\n")
        
#
#   writeMultiMaterials(uvset, amt, fp):
#
      
TX_SCALE = 1
TX_BW = 2

TexInfo = {
    "diffuse" :     ("COLOR", "use_map_color_diffuse", "diffuse_color_factor", 0),
    "specular" :    ("SPECULAR", "use_map_specular", "specular_factor", TX_BW),
    "alpha" :       ("ALPHA", "use_map_alpha", "alpha_factor", TX_BW),
    "translucency": ("TRANSLUCENCY", "use_map_translucency", "translucency_factor", TX_BW),
    "bump" :        ("NORMAL", "use_map_normal", "normal_factor", TX_SCALE|TX_BW),
    "displacement": ("DISPLACEMENT", "use_map_displacement", "displacement_factor", TX_SCALE|TX_BW),
}    

def writeMultiMaterials(amt, fp):
    uvset = amt.human.uvset
    folder = os.path.dirname(uvset.filename)
    log.debug("Folder %s", folder)
    for mat in uvset.materials:
        for tex in mat.textures:
            name = os.path.basename(tex.file)
            fp.write("Image %s\n" % name)
            #file = amt.config.getTexturePath(tex, "data/textures", True, amt.human)
            file = amt.config.getTexturePath(name, folder, True, amt.human)
            fp.write(
                "  Filename %s ;\n" % file +
#                "  alpha_mode 'PREMUL' ;\n" +
                "end Image\n\n" +
                "Texture %s IMAGE\n" % name +
                "  Image %s ;\n" % name +
                "end Texture\n\n")
            
        fp.write("Material %s_%s\n" % (amt.name, mat.name))
        alpha = False
        for (key, value) in mat.settings:
            if key == "alpha":
                alpha = True
                fp.write(
                "  use_transparency True ;\n" +
                "  use_raytrace False ;\n" +
                "  use_shadows False ;\n" +
                "  use_transparent_shadows False ;\n" +
                "  alpha %s ;\n" % value)
            elif key in ["diffuse_color", "specular_color"]:
                fp.write("  %s Array %s %s %s ;\n" % (key, value[0], value[1], value[2]))
            elif key in ["diffuse_intensity", "specular_intensity"]:
                fp.write("  %s %s ;\n" % (key, value))
        if not alpha:
            fp.write("  use_transparent_shadows True ;\n")
                
        n = 0
        for tex in mat.textures:
            name = os.path.basename(tex.file)
            if len(tex.types) > 0:
                (key, value) = tex.types[0]
            else:
                (key, value) = ("diffuse", "1")
            (type, use, factor, flags) = TexInfo[key]
            diffuse = False
            fp.write(
                "  MTex %d %s UV %s\n" % (n, name, type) +
                "    texture Refer Texture %s ;\n" % name)            
            for (key, value) in tex.types:
                (type, use, factor, flags) = TexInfo[key]
                if flags & TX_SCALE:
                    scale = "*theScale"
                else:
                    scale = ""
                fp.write(
                "    %s True ;\n" % use +
                "    %s %s%s ;\n" % (factor, value, scale))
                if flags & TX_BW:
                    fp.write("    use_rgb_to_intensity True ;\n")
                if key == "diffuse":
                    diffuse = True
            if not diffuse:
                fp.write("    use_map_color_diffuse False ;\n")
            fp.write("  end MTex\n")
            n += 1
        fp.write("end Material\n\n")
    
#
#    writeRigWeights(fp, weights):
#

def writeRigWeights(fp, weights):
    for grp in weights.keys():
        fp.write("\n  VertexGroup %s\n" % grp)
        for (v,w) in weights[grp]:
            fp.write("    wv %d %.4f ;\n" % (v,w))
        fp.write("  end VertexGroup\n")
    return
    


#-------------------------------------------------------------------------------        
#   Setup custom shapes
#-------------------------------------------------------------------------------        

def setupCircle(fp, name, r):
    """
    Write circle object to the MHX file. Circles are used as custom shapes.
    
    fp:
        *File*: Output file pointer. 
    name:
        *string*: Object name.
    r:
        *float*: Radius.
    """

    fp.write("\n"+
        "Mesh %s %s \n" % (name, name) +
        "  Verts\n")
    for n in range(16):
        v = n*pi/8
        y = 0.5 + 0.02*sin(4*v)
        fp.write("    v %.3f %.3f %.3f ;\n" % (r*math.cos(v), y, r*math.sin(v)))
    fp.write(
        "  end Verts\n" +
        "  Edges\n")
    for n in range(15):
        fp.write("    e %d %d ;\n" % (n, n+1))
    fp.write(
        "    e 15 0 ;\n" +
        "  end Edges\n"+
        "end Mesh\n")
        
    fp.write(
        "Object %s MESH %s\n" % (name, name) +
        "  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n"+
        "  parent Refer Object CustomShapes ;\n"+
        "end Object\n")


def setupCube(fp, name, r, offs):
    """
    Write cube object to the MHX file. Cubes are used as custom shapes.
    
    fp:
        *File*: Output file pointer. 
    name:
        *string*: Object name.
    r:
        *float* or *float triple*: Side(s) of cube.
    offs:
        *float* or *float triple*: Y offset or offsets from origin.
    """
    
    try:
        (rx,ry,rz) = r
    except:
        (rx,ry,rz) = (r,r,r)
    try:
        (dx,dy,dz) = offs
    except:
        (dx,dy,dz) = (0,offs,0)

    fp.write("\n"+
        "Mesh %s %s \n" % (name, name) +
        "  Verts\n")
    for x in [-rx,rx]:
        for y in [-ry,ry]:
            for z in [-rz,rz]:
                fp.write("    v %.2f %.2f %.2f ;\n" % (x+dx,y+dy,z+dz))
    fp.write(
        "  end Verts\n" +
        "  Faces\n" +
        "    f 0 1 3 2 ;\n" +
        "    f 4 6 7 5 ;\n" +
        "    f 0 2 6 4 ;\n" +
        "    f 1 5 7 3 ;\n" +
        "    f 1 0 4 5 ;\n" +
        "    f 2 3 7 6 ;\n" +
        "  end Faces\n" +
        "end Mesh\n")

    fp.write(
        "Object %s MESH %s\n" % (name, name) +
        "  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n" +
        "  parent Refer Object CustomShapes ;\n" +
        "end Object\n")


def setupCustomShapes(fp):
    """
    Write simple custom shapes to the MHX file. Additional custom shapes are defined in 
    mhx files in mhx/templates.
    
    fp:
        *File*: Output file pointer. 
    """
    
    setupCircle(fp, "MHCircle01", 0.1)
    setupCircle(fp, "MHCircle025", 0.25)
    setupCircle(fp, "MHCircle05", 0.5)
    setupCircle(fp, "MHCircle10", 1.0)
    setupCircle(fp, "MHCircle15", 1.5)
    setupCircle(fp, "MHCircle20", 2.0)
    setupCube(fp, "MHCube01", 0.1, 0)
    setupCube(fp, "MHCube025", 0.25, 0)
    setupCube(fp, "MHCube05", 0.5, 0)
    setupCube(fp, "MHEndCube01", 0.1, 1)
    setupCube(fp, "MHChest", (0.7,0.25,0.5), (0,0.5,0.35))
    setupCube(fp, "MHRoot", (1.25,0.5,1.0), 1)
    return

#-------------------------------------------------------------------------------        
#   Armature used for export
#-------------------------------------------------------------------------------        

class ExportArmature(CArmature):

    def __init__(self, name, human, config):    
        CArmature. __init__(self, name, human, config)
        self.customShapeFiles = []
        self.customShapes = {}
        self.poseInfo = {}
        self.gizmoFiles = []


    def scanProxies(self):
        self.proxies = {}
        for pfile in self.config.getProxyList():
            if pfile.file:
                print("Scan", pfile, pfile.type)
                proxy = mh2proxy.readProxyFile(self.mesh, pfile, True)
                if proxy:
                    self.proxies[proxy.name] = proxy        


    def setup(self):
        if self.config.facepanel:            
            self.joints += rig_panel_25.PanelJoints
            self.headsTails += rig_panel_25.PanelHeadsTails
            self.boneDefs += rig_panel_25.PanelArmature

        amtpkg.rigdefs.CArmature.setup(self)
        
        if self.config.clothesRig:
            for proxy in self.proxies.values():
                if proxy.rig:
                    coord = []
                    for refVert in proxy.refVerts:
                        coord.append(refVert.getCoord())
                    (locations, boneList, weights) = exportutils.rig.readRigFile(proxy.rig, amt.mesh, coord=coord) 
                    proxy.weights = self.prefixWeights(weights, proxy.name)
                    appendRigBones(boneList, proxy.name, L_CLO, body, amt)
        

    def setupCustomShapes(self, fp):
        if self.gizmoFiles:
            for fname in self.gizmoFiles:
                copyFile25(fname, fp, None, self)    
            setupCustomShapes(fp)
        else:        
            for (name, data) in self.customShapes.items():
                (typ, r) = data
                if typ == "-circ":
                    setupCircle(fp, name, 0.1*r)
                elif typ == "-box":
                    setupCube(fp, name, 0.1*r, (0,0,0))
                else:
                    halt

        if self.config.facepanel:
            setupCube(fp, "MHCube025", 0.25, 0)
            setupCube(fp, "MHCube05", 0.5, 0)
            copyFile25("shared/mhx/templates/panel_gizmo25.mhx", fp, None, self)    
        

    def writeArmature(self, fp):        
        for data in self.boneDefs:
            (bone, roll, parent, flags, layers, bbone) = data
            print(data)
            conn = (flags & F_CON != 0)
            deform = (flags & F_DEF != 0)
            restr = (flags & F_RES != 0)
            wire = (flags & F_WIR != 0)
            lloc = (flags & F_NOLOC == 0)
            lock = (flags & F_LOCK != 0)
            cyc = (flags & F_NOCYC == 0)
        
            scale = self.config.scale
    
            fp.write("\n  Bone %s %s\n" % (bone, True))
            (x, y, z) = scale*self.rigHeads[bone]
            fp.write("    head  %.6g %.6g %.6g  ;\n" % (x,-z,y))
            (x, y, z) = scale*self.rigTails[bone]
            fp.write("    tail %.6g %.6g %.6g  ;\n" % (x,-z,y))
            if type(parent) == tuple:
                (soft, hard) = parent
                if hard:
                    fp.write(
                        "#if toggle&T_HardParents\n" +
                        "    parent Refer Bone %s ;\n" % hard +
                        "#endif\n")
                if soft:
                    fp.write(
                        "#if toggle&T_HardParents==0\n" +
                        "    parent Refer Bone %s ;\n" % soft +
                        "#endif\n")
            elif parent:
                fp.write("    parent Refer Bone %s ; \n" % (parent))
            fp.write(
                "    roll %.6g ; \n" % (roll)+
                "    use_connect %s ; \n" % (conn) +
                "    use_deform %s ; \n" % (deform) +
                "    show_wire %s ; \n" % (wire))
    
            if 1 and (flags & F_HID):
                fp.write("    hide True ; \n")
    
            if bbone:
                (bin, bout, bseg) = bbone
                fp.write(
                    "    bbone_in %d ; \n" % (bin) +
                    "    bbone_out %d ; \n" % (bout) +
                    "    bbone_segments %d ; \n" % (bseg))
    
            if flags & F_NOROT:
                fp.write("    use_inherit_rotation False ; \n")
            if flags & F_SCALE:
                fp.write("    use_inherit_scale True ; \n")
            else:
                fp.write("    use_inherit_scale False ; \n")
            fp.write("    layers Array ")
    
            bit = 1
            for n in range(32):
                if layers & bit:
                    fp.write("1 ")
                else:
                    fp.write("0 ")
                bit = bit << 1
    
            fp.write(" ; \n" +
                "    use_local_location %s ; \n" % lloc +
                "    lock %s ; \n" % lock +
                "    use_envelope_multiply False ; \n"+
                "    hide_select %s ; \n" % (restr) +
                "  end Bone \n")


    def writeBoneGroups(self, fp):    
        if not fp:
            return
        for (name, color) in self.boneGroups:
            fp.write(
                "    BoneGroup %s\n" % name +
                "      name '%s' ;\n" % name +
                "      color_set '%s' ;\n" % color +
                "    end BoneGroup\n")
        return


    def writeControlPoses(self, fp):
        if self.config.facepanel:
            rig_panel_25.PanelControlPoses(fp, self)
            
        for (bone, cinfo) in self.poseInfo.items():
            cs = None
            constraints = []
            for (key, value) in cinfo:
                if key == "CS":
                    cs = value
                elif key == "IK":
                    goal = value[0]
                    n = int(value[1])
                    inf = float(value[2])
                    pt = value[3]
                    if pt:
                        log.debug("%s %s %s %s", goal, n, inf, pt)
                        subtar = pt[0]
                        poleAngle = float(pt[1])
                        pt = (poleAngle, subtar)
                    constraints =  [('IK', 0, inf, ['IK', goal, n, pt, (True,False,True)])]
            posebone.addPoseBone(fp, self, bone, cs, None, (0,0,0), (0,0,0), (1,1,1), (1,1,1), 0, constraints)       


    def writeProperties(self, fp, typ):
        if typ != 'Object':
            return
        for (key, val) in self.objectProps:
            fp.write("  Property %s %s ;\n" % (key, val))
        for (key, val, string, min, max) in self.config.customProps:
            fp.write('  DefProp Float Mha%s %.2f %s min=-%.2f,max=%.2f ;\n' % (key, val, string, min, max) )
    
        if self.config.expressions:
            fp.write("#if toggle&T_Shapekeys\n")
            for skey in exportutils.shapekeys.ExpressionUnits:
                fp.write("  DefProp Float Mhs%s 0.0 %s min=-1.0,max=2.0 ;\n" % (skey, skey))
            fp.write("#endif\n")   

#-------------------------------------------------------------------------------        
#   MHX armature
#-------------------------------------------------------------------------------        

class MhxArmature(ExportArmature):

    def __init__(self, name, human, config):    
        ExportArmature. __init__(self, name, human, config)
        self.rigtype = 'mhx'

        self.boneGroups = [
            ('Master', 'THEME13'),
            ('Spine', 'THEME05'),
            ('FK_L', 'THEME09'),
            ('FK_R', 'THEME02'),
            ('IK_L', 'THEME03'),
            ('IK_R', 'THEME04'),
        ]
        self.recalcRoll = "['Foot_L','Toe_L','Foot_R','Toe_R','DfmFoot_L','DfmToe_L','DfmFoot_R','DfmToe_R']"
        self.gizmoFiles = ["./shared/mhx/templates/custom-shapes25.mhx", 
                      "./shared/mhx/templates/panel_gizmo25.mhx",
                      "./shared/mhx/templates/gizmos25.mhx"]

        self.objectProps = [("MhxRig", '"MHX"')]
        self.armatureProps = []
        self.headName = 'Head'
        self.preservevolume = False
        
        self.vertexGroupFiles = ["head", "bones", "palm", "tight"]
        if config.skirtRig == "own":
            self.vertexGroupFiles.append("skirt-rigged")    
        elif config.skirtRig == "inh":
            self.vertexGroupFiles.append("skirt")    

        if config.maleRig:
            self.vertexGroupFiles.append( "male" )
                                                        
        self.joints = (
            amtpkg.joints.DeformJoints +
            rig_body_25.BodyJoints +
            amtpkg.joints.FloorJoints +
            rig_arm_25.ArmJoints +
            rig_shoulder_25.ShoulderJoints +
            rig_finger_25.FingerJoints +
            rig_leg_25.LegJoints +
            #rig_toe_25.ToeJoints +
            rig_face_25.FaceJoints
        )            
        
        self.headsTails = (
            rig_body_25.BodyHeadsTails +
            rig_shoulder_25.ShoulderHeadsTails +
            rig_arm_25.ArmHeadsTails +
            rig_finger_25.FingerHeadsTails +
            rig_leg_25.LegHeadsTails +
            #rig_toe_25.ToeHeadsTails +
            rig_face_25.FaceHeadsTails
        )

        self.boneDefs = list(rig_body_25.BodyArmature1)
        if config.advancedSpine:
            self.boneDefs += rig_body_25.BodyArmature2Advanced
        else:
            self.boneDefs += rig_body_25.BodyArmature2Simple
        self.boneDefs += rig_body_25.BodyArmature3
        if config.advancedSpine:
            self.boneDefs += rig_body_25.BodyArmature4Advanced
        else:
            self.boneDefs += rig_body_25.BodyArmature4Simple
        self.boneDefs += rig_body_25.BodyArmature5

        self.boneDefs += (
            rig_shoulder_25.ShoulderArmature1 +
            rig_shoulder_25.ShoulderArmature2 +
            rig_arm_25.ArmArmature +            
            rig_finger_25.FingerArmature +
            rig_leg_25.LegArmature +
            #rig_toe_25.ToeArmature +
            rig_face_25.FaceArmature
        )
        
        if config.skirtRig == "own":
            self.joints += rig_skirt_25.SkirtJoints
            self.headsTails += rig_skirt_25.SkirtHeadsTails
            self.boneDefs += rig_skirt_25.SkirtArmature        

        if config.maleRig:
            self.boneDefs += rig_body_25.MaleArmature        

        if False and config.custom:
            (custJoints, custHeadsTails, custArmature, config.customProps) = exportutils.custom.setupCustomRig(config)
            self.joints += custJoints
            self.headsTails += custHeadsTails
            self.boneDefs += custArmature
        

    def dynamicLocations(self):
        rig_body_25.BodyDynamicLocations()
        

    def writeControlPoses(self, fp):
        self.writeBoneGroups(fp)
        rig_body_25.BodyControlPoses(fp, self)
        rig_shoulder_25.ShoulderControlPoses(fp, self)
        rig_arm_25.ArmControlPoses(fp, self)
        rig_finger_25.FingerControlPoses(fp, self)
        rig_leg_25.LegControlPoses(fp, self)
        #rig_toe_25.ToeControlPoses(fp, self)
        rig_face_25.FaceControlPoses(fp, self)
        if self.config.maleRig:
            rig_body_25.MaleControlPoses(fp, self)
        if self.config.skirtRig == "own":
            rig_skirt_25.SkirtControlPoses(fp, self)            
        ExportArmature.writeControlPoses(self, fp)


    def writeDrivers(self, fp):
        driverList = (
            amtpkg.drivers.writePropDrivers(fp, self, rig_arm_25.ArmPropDrivers, "", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_arm_25.ArmPropLRDrivers, "_L", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_arm_25.ArmPropLRDrivers, "_R", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_arm_25.SoftArmPropLRDrivers, "_L", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_arm_25.SoftArmPropLRDrivers, "_R", "Mha") +
            #writeScriptedBoneDrivers(fp, rig_leg_25.LegBoneDrivers) +
            amtpkg.drivers.writePropDrivers(fp, self, rig_leg_25.LegPropDrivers, "", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_leg_25.LegPropLRDrivers, "_L", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_leg_25.LegPropLRDrivers, "_R", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_leg_25.SoftLegPropLRDrivers, "_L", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_leg_25.SoftLegPropLRDrivers, "_R", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_body_25.BodyPropDrivers, "", "Mha")
        )
        if self.config.advancedSpine:
            driverList += amtpkg.drivers.writePropDrivers(fp, self, rig_body_25.BodyPropDriversAdvanced, "", "Mha") 
        driverList += (
            amtpkg.drivers.writePropDrivers(fp, self, rig_face_25.FacePropDrivers, "", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, rig_face_25.SoftFacePropDrivers, "", "Mha")
        )
        fingDrivers = rig_finger_25.getFingerPropDrivers()
        driverList += (
            amtpkg.drivers.writePropDrivers(fp, self, fingDrivers, "_L", "Mha") +
            amtpkg.drivers.writePropDrivers(fp, self, fingDrivers, "_R", "Mha") +
            #rig_panel_25.FingerControlDrivers(fp)
            amtpkg.drivers.writeMuscleDrivers(fp, rig_shoulder_25.ShoulderDeformDrivers, self.name) +
            amtpkg.drivers.writeMuscleDrivers(fp, rig_arm_25.ArmDeformDrivers, self.name) +
            amtpkg.drivers.writeMuscleDrivers(fp, rig_leg_25.LegDeformDrivers, self.name)
        )
        faceDrivers = rig_face_25.FaceDeformDrivers(fp, self)
        driverList += amtpkg.drivers.writeDrivers(fp, True, faceDrivers)
        return driverList
    
    def writeActions(self, fp):
        #rig_arm_25.ArmWriteActions(fp)
        #rig_leg_25.LegWriteActions(fp)
        #rig_finger_25.FingerWriteActions(fp)
        return

#-------------------------------------------------------------------------------        
#   Rigify armature
#-------------------------------------------------------------------------------        

class RigifyArmature(ExportArmature):

    def __init__(self, name, human, config):    
        ExportArmature. __init__(self, name, human, config)
        self.rigtype = 'rigify'

        self.vertexGroupFiles = ["head", "rigify"]
        self.gizmoFiles = ["./shared/mhx/templates/panel_gizmo25.mhx",
                          "./shared/mhx/templates/rigify_gizmo25.mhx"]
        self.headName = 'head'
        self.preservevolume = True
        faceArmature = swapParentNames(rig_face_25.FaceArmature, 
                           {'Head' : 'head', 'MasterFloor' : None} )
            
        self.joints = (
            amtpkg.joints.DeformJoints +
            rig_body_25.BodyJoints +
            amtpkg.joints.FloorJoints +
            rigify_rig.RigifyJoints +
            rig_face_25.FaceJoints
        )
        
        self.headsTails = (
            rigify_rig.RigifyHeadsTails +
            rig_face_25.FaceHeadsTails
        )

        self.boneDefs = (
            rigify_rig.RigifyArmature +
            faceArmature
        )

        self.objectProps = rigify_rig.RigifyObjectProps + [("MhxRig", '"Rigify"')]
        self.armatureProps = rigify_rig.RigifyArmatureProps


    def writeDrivers(self, fp):
        rig_face_25.FaceDeformDrivers(fp, self)        
        amtpkg.drivers.writePropDrivers(fp, self, rig_face_25.FacePropDrivers, "", "Mha")
        amtpkg.drivers.writePropDrivers(fp, self, rig_face_25.SoftFacePropDrivers, "", "Mha")
        return []


    def writeControlPoses(self, fp):
        rigify_rig.RigifyWritePoses(fp, self)
        rig_face_25.FaceControlPoses(fp, self)
        ExportArmature.writeControlPoses(self, fp)


def swapParentNames(bones, changes):
    nbones = []
    for bone in bones:
        (name, roll, par, flags, level, bb) = bone
        try:
            nbones.append( (name, roll, changes[par], flags, level, bb) )
        except KeyError:
            nbones.append(bone)
    return nbones


