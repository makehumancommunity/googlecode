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

Proxies
"""

import os
import log
import gui3d

from . import mhx_mesh
from . import mhx_materials

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

def writeProxyType(type, test, env, fp, t0, t1):
    n = 0
    for proxy in env.proxies.values():
        if proxy.type == type:
            n += 1
    if n == 0:
        return

    dt = (t1-t0)/n
    t = t0
    for proxy in env.proxies.values():
        if proxy.type == type:
            gui3d.app.progress(t, text="Exporting %s" % proxy.name)
            fp.write("#if toggle&%s\n" % test)
            writeProxy(fp, env, proxy)
            fp.write("#endif\n")
            t += dt


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

def writeProxy(fp, env, proxy):
    scale = env.config.scale

    fp.write("""
NoScale False ;
""")

    # Proxy material

    writeProxyMaterial(fp, proxy, env)

    # Proxy mesh

    name = env.name + proxy.name
    fp.write(
        "Mesh %sMesh %sMesh \n" % (name, name) +
        "  Verts\n")

    amt = env.armature
    ox = amt.origin[0]
    oy = amt.origin[1]
    oz = amt.origin[2]
    for x,y,z in proxy.getCoords():
        fp.write("  v %.4f %.4f %.4f ;\n" % (scale*(x-ox), scale*(-z+oz), scale*(y-oy)))

    fp.write("""
  end Verts
  Faces
""")

    obj = proxy.getObject()
    for fv in obj.fvert:
        fp.write("    f %d %d %d %d ;\n" % (fv[0], fv[1], fv[2], fv[3]))
    #if False and proxy.faceNumbers:
    #    for ftn in proxy.faceNumbers:
    #        fp.write(ftn)
    #else:
    fp.write("    ftall 0 1 ;\n")

    fp.write("  end Faces\n")

    # Proxy layers

    fp.write(
        "  MeshTextureFaceLayer %s\n" % "Texture" +
        "    Data \n")
    for fuv in obj.fuvs:
        fp.write("    vt")
        for vt in fuv:
            uv = obj.texco[vt]
            fp.write(" %.4g %.4g" % tuple(uv))
        fp.write(" ;\n")
    fp.write(
        "    end Data\n" +
        "  end MeshTextureFaceLayer\n")

    '''
    #Support for multiple texture layers currently disabled.

    layers = list( proxy.uvtexLayerName.keys())
    list.sort()
    for layer in layers:
        if layer == proxy.objFileLayer
            continue
        try:
            texfaces = proxy.texFacesLayers[layer]
            texverts = proxy.texVertsLayers[layer]
        except KeyError:
            continue
        fp.write(
            "  MeshTextureFaceLayer %s\n" % proxy.uvtexLayerName[layer] +
            "    Data \n")

        if layer == proxy.objFileLayer:
            for fuv in obj.fuvs:
                fp.write("    vt")
                for vt in fuv:
                    uv = obj.texco[vt]
                    fp.write(" %.4g %.4g" % (uv[0], uv[1]))
                fp.write(" ;\n")
        else:
            pass

        fp.write(
            "    end Data\n" +
            "  end MeshTextureFaceLayer\n")
    '''

    # Proxy vertex groups

    mhx_mesh.writeVertexGroups(fp, env, proxy)

    if proxy.useBaseMaterials:
        mhx_mesh.writeBaseMaterials(fp, env)
    elif proxy.material:
        fp.write("  Material %s%s ;" % (env.name, proxy.material.name))


    fp.write("""
end Mesh
""")

    # Proxy object

    name = env.name + proxy.name
    fp.write(
        "Object %sMesh MESH %sMesh \n" % (name, name) +
        "  parent Refer Object %s ;\n" % env.name +
        "  hide False ;\n" +
        "  hide_render False ;\n")
    if proxy.wire:
        fp.write("  draw_type 'WIRE' ;\n")


    # Proxy layers

    fp.write("layers Array ")
    for n in range(20):
        if n == proxy.layer:
            fp.write("1 ")
        else:
            fp.write("0 ")
    fp.write(";\n")

    fp.write("""
#if toggle&T_Armature
""")

    mhx_mesh.writeArmatureModifier(fp, env, proxy)
    writeProxyModifiers(fp, env, proxy)

    fp.write("""
  parent_type 'OBJECT' ;
#endif
  color Array 1.0 1.0 1.0 1.0  ;
  show_name True ;
  select True ;
  lock_location Array 1 1 1 ;
  lock_rotation Array 1 1 1 ;
  lock_scale Array 1 1 1  ;
  Property MhxScale theScale ;
  Property MhxProxy True ;
end Object
""")

    mhx_mesh.writeHideAnimationData(fp, env, env.name, proxy.name)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

def writeProxyModifiers(fp, env, proxy):
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
                "      target Refer Object %sMesh ;\n" % env.name +
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



def copyProxyMaterialFile(fp, pair, mat, proxy, env):
    prxList = sortedMasks(env)
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
            words[1] = env.name + words[1]
            for word in words:
                fp.write("%s " % word)
            fp.write("\n")
            tex = os.path.join(folder,words[1])
        elif words[0] == 'Material':
            words[1] = env.name + words[1]
            for word in words:
                fp.write("%s " % word)
            fp.write("\n")
            addProxyMaskMTexs(fp, mat, proxy, prxList)
        elif words[0] == 'MTex':
            words[2] = env.name + words[2]
            for word in words:
                fp.write("%s " % word)
            fp.write("\n")
        elif words[0] == 'Filename':
            filepath = os.path.join(folder, words[1])
            newpath = env.config.copyTextureToNewLocation(filepath)
            fp.write("  Filename %s ;\n" % newpath)
        else:
            fp.write(line)
    tmpl.close()
    return


def writeProxyTexture(fp, filepath, mat, extra, env):
    config = env.config

    texname = getTextureName(filepath, env)
    newpath = config.copyTextureToNewLocation(filepath)
    fp.write(
        "Image %s\n" % texname +
        "  Filename %s ;\n" % newpath +
#        "  alpha_mode 'PREMUL' ;\n" +
        "end Image\n\n" +
        "Texture %s IMAGE\n" % texname +
        "  Image %s ;\n" % texname)
    #writeProxyMaterialSettings(fp, mat.textureSettings)
    fp.write(extra)
    fp.write("end Texture\n\n")
    return newpath


def getTextureName(filepath, env):
    return (env.name + os.path.basename(filepath).replace(" ","_"))


def writeProxyMaterial(fp, proxy, env):
    mat = proxy.material
    alpha = 1 - mat.transparencyIntensity

    # Write images and textures

    if mat.diffuseTexture:
        uuid = proxy.getUuid()
        if uuid in env.human.clothesObjs.keys() and env.human.clothesObjs[uuid]:
            # Apply custom texture
            clothesObj = env.human.clothesObjs[uuid]
            texture = clothesObj.mesh.texture
            diffpath = writeProxyTexture(fp, texture, mat, "", env)
        else:
            diffpath = writeProxyTexture(fp, mat.diffuseTexture, mat, "", env)
    else:
        diffpath = None

    if mat.normalMapTexture or mat.bumpMapTexture:
        if mat.normalMapTexture:
            bumppath = writeProxyTexture(fp, mat.normalMapTexture, mat,
                ("    use_normal_map True ;\n"),
                env)
            bumpIsnormal = True
            bumpfactor = mat.normalMapIntensity
        else:
            bumppath = writeProxyTexture(fp, mat.bumpMapTexture, mat, "", env)
            bumpIsnormal = False
            factor = mat.bumpMapIntensity
    else:
        bumppath = None

    if mat.displacementMapTexture:
        disppath = writeProxyTexture(fp, mat.displacementMapTexture, mat, "", env)
    else:
        disppath = None

    if mat.transparencyMapTexture:
        transpath = writeProxyTexture(fp, mat.transparencyMapTexture, mat, "", env)
    else:
        transpath = None

    # Write materials

    prxList = sortedMasks(env)
    nMasks = countMasks(proxy, prxList)
    slot = nMasks

    fp.write("Material %s%s \n" % (env.name, mat.name))
    addProxyMaskMTexs(fp, mat, proxy, prxList)
    #writeProxyMaterialSettings(fp, mat.settings)
    #uvlayer = proxy.uvtexLayerName[proxy.textureLayer]
    uvlayer = "Texture"

    if diffpath:
        texname = getTextureName(diffpath, env)
        fp.write(
            "  MTex %d %s UV COLOR\n" % (slot, texname) +
            "    texture Refer Texture %s ;\n" % texname +
            "    use_map_alpha True ;\n" +
            "    diffuse_color_factor %.3f ;\n" % mat.diffuseIntensity +
            "    uv_layer '%s' ;\n" % uvlayer)
        #writeProxyMaterialSettings(fp, proxy.mtexSettings)
        fp.write("  end MTex\n")
        slot += 1
        alpha = 0

    if bumppath:
        texname = getTextureName(bumppath, env)
        fp.write(
            "  MTex %d %s UV NORMAL\n" % (slot, texname) +
            "    texture Refer Texture %s ;\n" % texname +
            "    use_map_normal %s ;\n" % bumpIsnormal +
            "    use_map_color_diffuse False ;\n" +
            "    normal_factor %.3f ;\n" % bumpfactor +
            "    use_rgb_to_intensity True ;\n" +
            "    uv_layer '%s' ;\n" % uvlayer +
            "  end MTex\n")
        slot += 1

    if disppath:
        texname = getTextureName(disppath, env)
        fp.write(
            "  MTex %d %s UV DISPLACEMENT\n" % (slot, texname) +
            "    texture Refer Texture %s ;\n" % texname +
            "    use_map_displacement True ;\n" +
            "    use_map_color_diffuse False ;\n" +
            "    displacement_factor %.3f ;\n" % proxy.displacementMapIntensity +
            "    use_rgb_to_intensity True ;\n" +
            "    uv_layer '%s' ;\n" % uvlayer +
            "  end MTex\n")
        slot += 1

    if transpath:
        texname = getTextureName(transpath, env)
        fp.write(
            "  MTex %d %s UV ALPHA\n" % (slot, texname) +
            "    texture Refer Texture %s ;\n" % texname +
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

    if True or mat.mtexSettings == []:
        fp.write(
            "  use_shadows True ;\n" +
            "  use_transparent_shadows True ;\n")

    fp.write(
        "  Property MhxDriven True ;\n" +
        "end Material\n\n")

"""
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
"""

def addProxyMaskMTexs(fp, mat, proxy, prxList):
    if proxy.maskLayer < 0:
        return
    n = 0
    m = len(prxList)
    for (zdepth, prx) in prxList:
        m -= 1
        if zdepth > proxy.z_depth:
            n = mhx_materials.addMaskMTex(fp, prx.mask, proxy, 'MULTIPLY', n)
    if True or not tex:
        n = mhx_materials.addMaskMTex(fp, 'solid', proxy, 'MIX', n)


def sortedMasks(env):
    if not env.config.useMasks:
        return []
    prxList = []
    for prx in env.proxies.values():
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


