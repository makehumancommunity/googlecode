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
import aljabr
import gui3d
import os
import time
import numpy
import log

#import cProfile

import mh2proxy
import exportutils
import armature
import warpmodifier
import posemode
import exportutils


from . import mhx_rig
from . import mhx_24
from . import rig_panel_25
from . import rig_shoulder_25
from . import rig_arm_25
from . import rig_leg_25
from . import rig_body_25



class CInfo:
    def __init__(self, name, human, config):
        self.name = name
        self.human = human
        self.mesh = human.meshData
        self.config = config
        self.proxies = {}
        self.locations = {}
        self.rigHeads = {}
        self.rigTails = {}
        self.origin = [0,0,0]
        self.loadedShapes = {}
        
        
    def scanProxies(self):
        self.proxies = {}
        for pfile in self.config.proxyList:
            if pfile.file:
                print("Scan", pfile, pfile.type)
                proxy = mh2proxy.readProxyFile(self.mesh, pfile, True)
                if proxy:
                    self.proxies[proxy.name] = proxy        


#
#    exportMhx(human, filepath, config):
#

def exportMhx(human, filepath, config):  
    time1 = time.clock()
    posemode.exitPoseMode()        
    posemode.enterPoseMode()
    
    config.addObjects(human)
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
        info = CInfo(name, human, config)
        exportMhx_25(info, fp)
        fp.close()
        time2 = time.clock()
        log.message("Wrote MHX file in %g s: %s", time2-time1, filepath)

    posemode.exitPoseMode()        
    return        


def exportMhx_25(info, fp):
    gui3d.app.progress(0, text="Exporting MHX")
    log.message("Export MHX")
    
    fp.write(
"# MakeHuman exported MHX\n" +
"# www.makeinfo.human.org\n" +
"MHX %d %d ;\n" % (MAJOR_VERSION, MINOR_VERSION) +
"#if Blender24\n" +
"  error 'This file can only be read with Blender 2.5' ;\n" +
"#endif\n")

    info.scanProxies()
    mhx_rig.setupRig(info)
    
    if not info.config.cage:
        fp.write(
    "#if toggle&T_Cage\n" +
    "  error 'This MHX file does not contain a cage. Unselect the Cage import option.' ;\n" +
    "#endif\n")

    fp.write(
"NoScale True ;\n" +
"Object CustomShapes EMPTY None\n" +
"  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n" +
"end Object\n\n")

    if info.config.rigtype in ['mhx', 'rigify', 'blenrig']:
        for fname in info.config.gizmoFiles:
            copyFile25(fname, fp, None, info)    
        mhx_rig.setupCircles(fp)
    else:
        for (name, data) in info.config.customShapes.items():
            (typ, r) = data
            if typ == "-circ":
                mhx_rig.setupCircle(fp, name, 0.1*r)
            elif typ == "-box":
                mhx_rig.setupCube(fp, name, 0.1*r, (0,0,0))
            else:
                halt
        """                
        if info.config.facepanel:
            mhx_rig.setupCube(fp, "MHCube025", 0.25, 0)
            mhx_rig.setupCube(fp, "MHCube05", 0.5, 0)
            copyFile25("shared/mhx/templates/panel_gizmo25.mhx", fp, None, info)    
        """            
        
    gui3d.app.progress(0.1, text="Exporting armature")
    copyFile25("shared/mhx/templates/rig-armature25.mhx", fp, None, info)    
    
    gui3d.app.progress(0.15, text="Exporting materials")    
    fp.write("\nNoScale False ;\n\n")
    if info.human.uvset:
        writeMultiMaterials(info, fp)
    else:
        copyFile25("shared/mhx/templates/materials25.mhx", fp, None, info)    

    if info.config.cage:
        proxyCopy('Cage', 'T_Cage', info, fp, 0.2, 0.25)
    
    gui3d.app.progress(0.25, text="Exporting main mesh")    
    fp.write("#if toggle&T_Mesh\n")
    copyFile25("shared/mhx/templates/meshes25.mhx", fp, None, info)    
    fp.write("#endif\n")

    proxyCopy('Proxy', 'T_Proxy', info, fp, 0.35, 0.4)
    proxyCopy('Clothes', 'T_Clothes', info, fp, 0.4, 0.55)
    proxyCopy('Hair', 'T_Clothes', info, fp, 0.55, 0.6)

    copyFile25("shared/mhx/templates/rig-poses25.mhx", fp, None, info) 

    if info.config.rigtype == 'rigify':
        fp.write("Rigify %s ;\n" % info.name)

    gui3d.app.progress(1.0)
    return
    

def proxyCopy(type, test, info, fp, t0, t1):
    n = 0
    for proxy in info.proxies.values():
        if proxy.type == type:
            n += 1
    if n == 0:
        return
        
    dt = (t1-t0)/n
    t = t0
    for proxy in info.proxies.values():
        if proxy.type == type:
            gui3d.app.progress(t, text="Exporting %s" % proxy.name)
            fp.write("#if toggle&%s\n" % test)
            copyFile25("shared/mhx/templates/proxy25.mhx", fp, proxy, info)    
            fp.write("#endif\n")
            t += dt
        
#
#    copyFile25(tmplName, fp, proxy, info):
#

def copyFile25(tmplName, fp, proxy, info):
    tmpl = open(tmplName)
    if tmpl == None:
        log.error("*** Cannot open %s", tmplName)
        return

    bone = None
    config = info.config
    #faces = loadFacesIndices(info.mesh)
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
                fp.write("    %s Refer Object %s%s ;\n" % (words[2], info.name, suffix))

            elif key == 'rig-bones':
                fp.write("Armature %s %s   Normal \n" % (info.name, info.name))
                mhx_rig.writeArmature(fp, info, info.config.armatureBones)

            elif key == 'human-object':
                if words[2] == 'Mesh':
                    fp.write(
                        "Object %sMesh MESH %sMesh\n"  % (info.name, info.name) +
                        "  Property MhxOffsetX %.4f ;\n" % info.origin[0] +
                        "  Property MhxOffsetY %.4f ;\n" % info.origin[1] +
                        "  Property MhxOffsetZ %.4f ;\n" % info.origin[2])
                elif words[2] == 'ControlRig':
                    fp.write(
                        "Object %s ARMATURE %s\n"  % (info.name, info.name) +
                        "  Property MhxVersion %d ;\n" % MINOR_VERSION)

            elif key == 'rig-poses':
                fp.write("Pose %s\n" % info.name)
                mhx_rig.writeControlPoses(fp, info)
                fp.write("  ik_solver 'LEGACY' ;\nend Pose\n")

            elif key == 'rig-actions':
                fp.write("Pose %s\nend Pose\n" % info.name)
                mhx_rig.writeAllActions(fp, info)

            elif key == 'if-true':
                value = eval(words[2])
                log.debug("if %s %s", words[2], value)
                fp.write("#if %s\n" % value)

            elif key == 'rig-drivers':
                if info.config.rigtype == "mhx":
                    fp.write("AnimationData %s True\n" % info.name)
                    mhx_rig.writeAllDrivers(fp, info)
                    rigDriversEnd(fp)

            elif key == 'rig-correct':
                fp.write("CorrectRig %s ;\n" % info.name)

            elif key == 'recalc-roll':
                if info.config.rigtype == "mhx":
                    fp.write("  RecalcRoll %s ;\n" % info.config.recalcRoll)

            elif key == 'ProxyMesh':
                writeProxyMesh(fp, info, proxy)

            elif key == 'ProxyObject':
                writeProxyObject(fp, info, proxy)

            elif key == 'ProxyLayers':
                fp.write("layers Array ")
                for n in range(20):
                    if n == proxy.layer:
                        fp.write("1 ")
                    else:
                        fp.write("0 ")
                fp.write(";\n")

            elif key == 'MeshAnimationData':
                writeHideAnimationData(fp, info, "", info.name)

            elif key == 'ProxyAnimationData':
                writeHideAnimationData(fp, info, info.name, proxy.name)

            elif key == 'toggleCage':
                if proxy and proxy.cage:
                    fp.write(
                    "  draw_type 'WIRE' ;\n" +
                    "  #if False\n")
                elif info.config.cage:                    
                    fp.write("  #if toggle&T_Cage\n")
                else:
                    fp.write("  #if False\n")

            elif key == 'ProxyVerts':
                ox = info.origin[0]
                oy = info.origin[1]
                oz = info.origin[2]
                for bary in proxy.realVerts:
                    (x,y,z) = mh2proxy.proxyCoord(bary)
                    fp.write("  v %.4f %.4f %.4f ;\n" % (x-ox, -z+oz, y-oy))

            elif key == 'Verts':
                proxy = None
                fp.write("Mesh %sMesh %sMesh\n  Verts\n" % (info.name, info.name))
                ox = info.origin[0]
                oy = info.origin[1]
                oz = info.origin[2]
                for v in info.mesh.verts:
                    fp.write("  v %.4f %.4f %.4f ;\n" % (v.co[0]-ox, -v.co[2]+oz, v.co[1]-oy))

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
                for f in info.mesh.faces:
                    fv = f.verts
                    if f.isTriangle():
                        fp.write("    f %d %d %d ;\n" % (fv[0].idx, fv[1].idx, fv[2].idx))
                    else:
                        fp.write("    f %d %d %d %d ;\n" % (fv[0].idx, fv[1].idx, fv[2].idx, fv[3].idx))
                fp.write("#if False\n")

            elif key == 'EndFaces':
                writeFaceNumbers(fp, info)

            elif key == 'FTTriangles':
                for f in info.mesh.faces:
                    if f.isTriangle():
                        fp.write("    mn %d 1 ;\n" % f.idx)

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
                if info.human.uvset:
                    for ft in info.human.uvset.texFaces:
                        fp.write("    vt")
                        for vt in ft:
                            uv = info.human.uvset.texVerts[vt]
                            fp.write(" %.4g %.4g" %(uv[0], uv[1]))
                        fp.write(" ;\n")
                else:
                    for f in info.mesh.faces:
                        uv0 = info.mesh.texco[f.uv[0]]
                        uv1 = info.mesh.texco[f.uv[1]]
                        uv2 = info.mesh.texco[f.uv[2]]
                        if f.isTriangle():
                            fp.write("    vt %.4g %.4g %.4g %.4g %.4g %.4g ;\n" % (uv0[0], uv0[1], uv1[0], uv1[1], uv2[0], uv2[1]))
                        else:
                            uv3 = info.mesh.texco[f.uv[3]]
                            fp.write("    vt %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g ;\n" % (uv0[0], uv0[1], uv1[0], uv1[1], uv2[0], uv2[1], uv3[0], uv3[1]))

            elif key == 'Material':
                fp.write("Material %s%s\n" % (info.name, words[2]))

            elif key == 'Materials':
                writeBaseMaterials(fp, info)

            elif key == 'ProxyMaterials':
                if proxy.useBaseMaterials:
                    writeBaseMaterials(fp, info)
                elif proxy.material:
                    fp.write("  Material %s%s ;\n" % (info.name, proxy.material.name))

            elif key == 'VertexGroup':
                writeVertexGroups(fp, info, proxy)

            elif key == 'group':
                writeGroups(fp, info)

            elif key == 'mesh-shapeKey':
                writeShapeKeys(fp, info, "%sMesh" % info.name, None)

            elif key == 'proxy-shapeKey':
                proxyShapes('Cage', 'T_Cage', info, fp)
                proxyShapes('Proxy', 'T_Proxy', info, fp)
                proxyShapes('Clothes', 'T_Clothes', info, fp)
                proxyShapes('Hair', 'T_Clothes', info, fp)

            elif key == 'ProxyModifiers':
                writeProxyModifiers(fp, info, proxy)

            elif key == 'MTex':
                n = nMasks + int(words[2])
                fp.write("  MTex %d %s %s %s\n" % (n, words[3], words[4], words[5]))

            elif key == 'SkinStart':
                nMasks = writeSkinStart(fp, proxy, info)

            elif key == 'curves':
                mhx_rig.writeAllCurves(fp, info)

            elif key == 'properties':
                mhx_rig.writeAllProperties(fp, words[2], info)
                writeHideProp(fp, info.name)
                for proxy in info.proxies.values():
                    writeHideProp(fp, proxy.name)
                if info.config.useCustomShapes: 
                    exportutils.custom.listCustomFiles(info.config)                            
                for path,name in info.config.customShapeFiles:
                    fp.write("  DefProp Float %s 0 %s  min=-1.0,max=2.0 ;\n" % (name, name[3:]))

            elif key == 'material-drivers':
                fp.write("  use_textures Array")
                for n in range(nMasks):
                    fp.write(" 1")
                for n in range(3):
                    fp.write(" 1")
                fp.write(" ;\n")
                fp.write("  AnimationData %sMesh True\n" % info.name)
                #armature.drivers.writeTextureDrivers(fp, rig_panel_25.BodyLanguageTextureDrivers)
                writeMaskDrivers(fp, info)
                fp.write("  end AnimationData\n")

            elif key == 'Filename':
                file = info.config.getTexturePath(words[2], words[3], True, info.human)
                fp.write("  Filename %s ;\n" % file)

            else:
                raise NameError("Unknown *** %s" % words[1])
        else:
            fp.write(line)

    log.message("    %s copied", tmplName)
    tmpl.close()

    return

#
#   writeFaceNumbers(fp, info):
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
    
def writeFaceNumbers(fp, info):
    fp.write("#else\n")
    if info.human.uvset:
        for ftn in info.human.uvset.faceNumbers:
            fp.write(ftn)
    else:            
        info.mesh = info.human.meshData
        fmats = {}
        print(info.mesh.materials.items)
        for fn,mtl in info.mesh.materials.items():
            fmats[fn] = MaterialNumbers[mtl]
            
        if info.config.hidden:
            deleteVerts = None
            deleteGroups = []
        else:
            deleteGroups = []
            deleteVerts = numpy.zeros(len(info.mesh.verts), bool)
            for proxy in info.proxies.values():
                deleteGroups += proxy.deleteGroups
                deleteVerts = deleteVerts | proxy.deleteVerts
                    
        for fg in info.mesh.faceGroups: 
            if mh2proxy.deleteGroup(fg.name, deleteGroups):
                for f in fg.faces:
                    fmats[f.idx] = 6
            elif "joint" in fg.name:
                for f in fg.faces:
                    fmats[f.idx] = 4
            elif fg.name == "helper-tights":                    
                for f in fg.faces:
                    fmats[f.idx] = 5
            elif fg.name == "helper-skirt":                    
                for f in fg.faces:
                    fmats[f.idx] = 7
            elif ("tongue" in fg.name):
                for f in fg.faces:
                    fmats[f.idx] = 1
            elif ("eyebrown" in fg.name) or ("lash" in fg.name):
                for f in fg.faces:
                    fmats[f.idx] = 3   
                    
        if deleteVerts != None:
            for f in info.mesh.faces:
                v = f.verts[0]
                if deleteVerts[v.idx]:
                    fmats[f.idx] = 6                        
                
        mn = -1
        fn = 0
        f0 = 0
        for f in info.mesh.faces:
            if fmats[fn] != mn:
                if fn != f0:
                    fp.write("  ftn %d %d 1 ;\n" % (fn-f0, mn))
                mn = fmats[fn]
                f0 = fn
            fn += 1
        if fn != f0:
            fp.write("  ftn %d %d 1 ;\n" % (fn-f0, mn))
    fp.write("#endif\n")

def writeBaseMaterials(fp, info):      
    if info.human.uvset:
        for mat in info.human.uvset.materials:
            fp.write("  Material %s_%s ;\n" % (info.name, mat.name))
    else:
        fp.write(
"  Material %sSkin ;\n" % info.name +
"  Material %sMouth ;\n" % info.name +
"  Material %sEye ;\n" % info.name +
"  Material %sBrows ;\n" % info.name +
"  Material %sInvisio ;\n" % info.name +
"  Material %sRed ;\n" % info.name +
"  Material %sGreen ;\n" % info.name +
"  Material %sBlue ;\n" % info.name
)
    
def addMaskImage(fp, info, mask):            
    (folder, file) = mask
    path = info.config.getTexturePath(file, folder, True, info.human)
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


def writeSkinStart(fp, proxy, info):
    if not info.config.useMasks:
        fp.write("Material %sSkin\n" % info.name)
        return 0
        
    if proxy:
        fp.write("Material %s%sSkin\n" % (info.name, proxy.name))
        return 0

    nMasks = 0
    prxList = list(info.proxies.values())
    
    for prx in prxList:
        if prx.mask:
            addMaskImage(fp, info, prx.mask)
            nMasks += 1
    fp.write("Material %sSkin\n" % info.name)
             #"  MTex 0 diffuse UV COLOR\n" +
             #"    texture Refer Texture diffuse ;\n" +
             #"  end MTex\n"

    n = 0    
    for prx in prxList:
        if prx.mask:
            n = addMaskMTex(fp, prx.mask, proxy, 'MULTIPLY', n)
            
    return nMasks
               

def writeMaskDrivers(fp, info):
    if not info.config.useMasks:
        return
    fp.write("#if toggle&T_Clothes\n")
    n = 0
    for prx in info.proxies.values():
        if prx.type == 'Clothes' and prx.mask:
            (dir, file) = prx.mask
            armature.drivers.writePropDriver(fp, info, ["Mhh%s" % prx.name], "1-x1", 'use_textures', n)
            n += 1            
    fp.write("#endif\n")
    return
    

def writeVertexGroups(fp, info, proxy):                
    if proxy and proxy.weights:
        writeRigWeights(fp, proxy.weights)
        return

    if info.config.vertexWeights:
        if proxy:
            weights = mh2proxy.getProxyWeights(info.config.vertexWeights, proxy)
        else:
            weights = info.config.vertexWeights                    
        writeRigWeights(fp, weights)
    else:
        for file in info.config.vertexGroupFiles:
            copyVertexGroups(file, fp, proxy)
            
    #for path in info.config.customvertexgroups:
    #    print("    %s" % path)
    #    copyVertexGroups(path, fp, proxy)    

    if info.config.cage and not (proxy and proxy.cage):
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


def writeGroups(fp, info):                
    fp.write(
        "PostProcess %sMesh %s 0000003f 00080000 0068056b 0000c000 ;\n" % (info.name, info.name) + 
        "Group %s\n"  % info.name +
        "  Objects\n" +
        "    ob %s ;\n" % info.name +
        "#if toggle&T_Mesh\n" +
        "    ob %sMesh ;\n" % info.name +
        "#endif\n")
    groupProxy('Cage', 'T_Cage', fp, info)
    groupProxy('Proxy', 'T_Proxy', fp, info)
    groupProxy('Clothes', 'T_Clothes', fp, info)
    groupProxy('Hair', 'T_Clothes', fp, info)
    fp.write(
        "    ob CustomShapes ;\n" + 
        "  end Objects\n" +
        "  layers Array 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1  ;\n" +
        "end Group\n")
    return
    
def groupProxy(typ, test, fp, info):
    fp.write("#if toggle&%s\n" % test)
    for proxy in info.proxies.values():
        if proxy.type == typ:
            name = info.name + proxy.name
            fp.write("    ob %sMesh ;\n" % name)
    fp.write("#endif\n")
    return

def writeProxyMesh(fp, info, proxy):                
    mat = proxy.material
    if mat:
        if proxy.material_file:
            copyProxyMaterialFile(fp, proxy.material_file, mat, proxy, info)
        else:
            writeProxyMaterial(fp, mat, proxy, info)
    name = info.name + proxy.name
    fp.write("Mesh %sMesh %sMesh \n" % (name, name))
    return


def writeProxyObject(fp, info, proxy): 
    name = info.name + proxy.name
    fp.write(
        "Object %sMesh MESH %sMesh \n" % (name, name) +
        "  parent Refer Object %s ;\n" % info.name +
        "  hide False ;\n" +
        "  hide_render False ;\n")
    if proxy.wire:
        fp.write("  draw_type 'WIRE' ;\n")    
    return


def writeProxyModifiers(fp, info, proxy):
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
                "      target Refer Object %sMesh ;\n" % info.name +
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


def writeHideAnimationData(fp, info, prefix, name):
    fp.write("AnimationData %s%sMesh True\n" % (prefix, name))
    armature.drivers.writePropDriver(fp, info, ["Mhh%s" % name], "x1", "hide", -1)
    armature.drivers.writePropDriver(fp, info, ["Mhh%s" % name], "x1", "hide_render", -1)
    fp.write("end AnimationData\n")
    return    
       

def copyProxyMaterialFile(fp, pair, mat, proxy, info):
    prxList = sortedMasks(info)
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
            words[1] = info.name + words[1]
            for word in words:
                fp.write("%s " % word)
            fp.write("\n")
            tex = os.path.join(folder,words[1])
        elif words[0] == 'Material':
            words[1] = info.name + words[1]
            for word in words:
                fp.write("%s " % word)
            fp.write("\n")
            addProxyMaskMTexs(fp, mat, proxy, prxList, tex)
        elif words[0] == 'MTex':
            words[2] = info.name + words[2]
            for word in words:
                fp.write("%s " % word)
            fp.write("\n")                
        elif words[0] == 'Filename':
            file = info.config.getTexturePath(words[1], folder, True, info.human)
            fp.write("  Filename %s ;\n" % file)
        else:
            fp.write(line)
    tmpl.close()
    return
       

def writeProxyTexture(fp, texture, mat, extra, info):        
    (folder,name) = texture
    tex = os.path.join(folder,name)
    #print(info.name)
    log.debug("Tex %s", tex)
    texname = info.name + os.path.basename(tex)
    fromDir = os.path.dirname(tex)
    texfile = info.config.getTexturePath(tex, fromDir, True, None)
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
    
    
def writeProxyMaterial(fp, mat, proxy, info):
    alpha = mat.alpha
    tex = None
    bump = None
    normal = None
    displacement = None
    transparency = None
    if proxy.texture:
        uuid = proxy.getUuid()
        if uuid in info.human.clothesObjs.keys() and info.human.clothesObjs[uuid]:
            # Apply custom texture
            clothesObj = info.human.clothesObjs[uuid]
            texture = clothesObj.mesh.texture
            texPath = (os.path.dirname(texture), os.path.basename(texture))
            (tex,texname) = writeProxyTexture(fp, texPath, mat, "", info)
        else:
            (tex,texname) = writeProxyTexture(fp, proxy.texture, mat, "", info)
    if proxy.bump:
        (bump,bumpname) = writeProxyTexture(fp, proxy.bump, mat, "", info)
    if proxy.normal:
        (normal,normalname) = writeProxyTexture(fp, proxy.normal, mat, 
            ("    use_normal_map True ;\n"),
            info)
    if proxy.displacement:
        (displacement,dispname) = writeProxyTexture(fp, proxy.displacement, mat, "", info)
    if proxy.transparency:
        (transparency,transname) = writeProxyTexture(fp, proxy.transparency, mat, "", info)
           
    prxList = sortedMasks(info)
    nMasks = countMasks(proxy, prxList)
    slot = nMasks
    
    fp.write("Material %s%s \n" % (info.name, mat.name))
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
    
def sortedMasks(info):
    if not info.config.useMasks:
        return []
    prxList = []
    for prx in info.proxies.values():
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
                    vlist = proxy.verts[v]
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



def writeCorrectives(fp, info, drivers, folder, landmarks, proxy, t0, t1):  
    try:
        shapeList = info.loadedShapes[folder]
    except KeyError:
        shapeList = None
    if shapeList is None:
        shapeList = exportutils.shapekeys.readCorrectives(drivers, info.human, folder, landmarks, t0, t1)
        info.loadedShapes[folder] = shapeList
    for (shape, pose, lr) in shapeList:
        writeShape(fp, pose, lr, shape, 0, 1, proxy)
    

def writeShape(fp, pose, lr, shape, min, max, proxy):
    fp.write(
        "ShapeKey %s %s True\n" % (pose, lr) +
        "  slider_min %.3g ;\n" % min +
        "  slider_max %.3g ;\n" % max)
    if proxy:
        pshapes = mh2proxy.getProxyShapes([("shape",shape)], proxy)
        name,pshape = pshapes[0]
        print pshape
        for (pv, dr) in pshape.items():
            (dx, dy, dz) = dr
            fp.write("  sv %d %.4f %.4f %.4f ;\n" %  (pv, dx, -dz, dy))
    else:
        for (vn, dr) in shape.items():
           fp.write("  sv %d %.4f %.4f %.4f ;\n" %  (vn, dr[0], -dr[2], dr[1]))
    fp.write("end ShapeKey\n")


def writeShapeKeys(fp, info, name, proxy):

    isHuman = ((not proxy) or proxy.type == 'Proxy')
    isHair = (proxy and proxy.type == 'Hair')
    
    fp.write(
"#if toggle&T_Shapekeys\n" +
"ShapeKeys %s\n" % name +
"  ShapeKey Basis Sym True\n" +
"  end ShapeKey\n")

    """
    if isHuman:        
        if info.config.faceshapes:
            shapeList = exportutils.shapekeys.readFaceShapes(human, rig_panel_25.BodyLanguageShapeDrivers, 0.6, 0.7)
            for (pose, shape, lr, min, max) in shapeList:
                writeShape(fp, pose, lr, shape, min, max, proxy)
    """
    
    if isHuman and info.config.expressions:
        try:
            shapeList = info.loadedShapes["expressions"]
        except KeyError:
            shapeList = None
        if shapeList is None:
            shapeList = exportutils.shapekeys.readExpressionUnits(info.human, 0.7, 0.9)
            info.loadedShapes["expressions"] = shapeList
        for (pose, shape) in shapeList:
            writeShape(fp, pose, "Sym", shape, -1, 2, proxy)
        
    if info.config.bodyShapes and info.config.rigtype == "mhx" and not isHair:
        writeCorrectives(fp, info, rig_shoulder_25.ShoulderTargetDrivers, "shoulder", "shoulder", proxy, 0.88, 0.90)                
        writeCorrectives(fp, info, rig_leg_25.HipTargetDrivers, "hips", "hips", proxy, 0.90, 0.92)                
        writeCorrectives(fp, info, rig_arm_25.ElbowTargetDrivers, "elbow", "body", proxy, 0.92, 0.94)                
        writeCorrectives(fp, info, rig_leg_25.KneeTargetDrivers, "knee", "knee", proxy, 0.94, 0.96)                

    if isHuman:
        for path,name in info.config.customShapeFiles:
            try:
                shape = info.loadedShapes[path]
            except KeyError:
                shape = None
            if shape is None:
                log.message("    %s", path)
                shape = exportutils.custom.readCustomTarget(path)
                info.loadedShapes[path] = shapeList
            writeShape(fp, name, "Sym", shape, -1, 2, proxy)                        

    fp.write("  AnimationData None (toggle&T_Symm==0)\n")
        
    print("BSS", name, proxy, isHair)
    if info.config.bodyShapes and info.config.rigtype == "mhx" and not isHair:
        armature.drivers.writeTargetDrivers(fp, rig_shoulder_25.ShoulderTargetDrivers, info.name)
        armature.drivers.writeTargetDrivers(fp, rig_leg_25.HipTargetDrivers, info.name)
        armature.drivers.writeTargetDrivers(fp, rig_arm_25.ElbowTargetDrivers, info.name)
        armature.drivers.writeTargetDrivers(fp, rig_leg_25.KneeTargetDrivers, info.name)

        armature.drivers.writeRotDiffDrivers(fp, rig_arm_25.ArmShapeDrivers, proxy)
        armature.drivers.writeRotDiffDrivers(fp, rig_leg_25.LegShapeDrivers, proxy)
        #armature.drivers.writeShapePropDrivers(fp, info, rig_body_25.bodyShapes, proxy, "Mha")

    fp.write("#if toggle&T_ShapeDrivers\n")

    if isHuman:
        for path,name in info.config.customShapeFiles:
            armature.drivers.writeShapePropDrivers(fp, info, [name], proxy, "")    

        if info.config.expressions:
            armature.drivers.writeShapePropDrivers(fp, info, exportutils.shapekeys.ExpressionUnits, proxy, "Mhs")
            
        skeys = []
        for (skey, val, string, min, max) in  info.config.customProps:
            skeys.append(skey)
        armature.drivers.writeShapePropDrivers(fp, info, skeys, proxy, "Mha")    
    fp.write("#endif\n")
        
    fp.write("  end AnimationData\n\n")

    if info.config.expressions and not proxy:
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
            

def proxyShapes(typ, test, info, fp):
    fp.write("#if toggle&%s\n" % test)
    for proxy in info.proxies.values():
        if proxy.name and proxy.type == typ:
            writeShapeKeys(fp, info, info.name+proxy.name+"Mesh", proxy)
    fp.write("#endif\n")
        
#
#   writeMultiMaterials(uvset, info.config, fp):
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

def writeMultiMaterials(uvset, info, fp):
    folder = os.path.dirname(info.human.uvset.filename)
    log.debug("Folder %s", folder)
    for mat in uvset.materials:
        for tex in mat.textures:
            name = os.path.basename(tex.file)
            fp.write("Image %s\n" % name)
            #file = info.config.getTexturePath(tex, "data/textures", True, info.human)
            file = info.config.getTexturePath(name, folder, True, info.human)
            fp.write(
                "  Filename %s ;\n" % file +
#                "  alpha_mode 'PREMUL' ;\n" +
                "end Image\n\n" +
                "Texture %s IMAGE\n" % name +
                "  Image %s ;\n" % name +
                "end Texture\n\n")
            
        fp.write("Material %s_%s\n" % (info.name, mat.name))
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
    


