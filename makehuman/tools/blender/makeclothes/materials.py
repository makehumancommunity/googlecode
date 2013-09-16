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
Utility for making clothes to MH characters.
"""

import bpy
import os
import shutil
from . import mc
from maketarget.error import MHError

'''
def checkObjectHasDiffuseTexture(ob):
    """
    An object must either lack material, or have a diffuse texture.
    """
    if ob.data.materials:
        mat = ob.data.materials[0]
        if mat is None:
            return True
        else:
            for mtex in mat.texture_slots:
                if mtex is None:
                    continue
                if mtex.use_map_color_diffuse:
                    tex = mtex.texture
                    if tex.type == 'IMAGE' and tex.image is not None:
                        return True
        return False
    else:
        return True
'''

def writeMaterial(ob, folder):
    """
    Create an mhmat file and write material settings there.
    """
    if ob.data.materials:
        mat = ob.data.materials[0]
        if mat is None:
            return None
        else:
            name = mc.goodName(mat.name)
            _,filepath = mc.getFileName(ob, folder, "mhmat")
            outdir = os.path.dirname(filepath)
            fp = mc.openOutputFile(filepath)
            matfile = writeMaterialFile(fp, mat, name, outdir)
            fp.close()
            print("%s created" % filepath)
            return os.path.basename(filepath)
    return None


def writeMaterialFile(fp, mat, name, outdir):
    """
    Write a material (.mhmat) file in the output folder.
    Also copies all textures to the output folder
    """

    fp.write(
        '# Material definition for MakeHuman benchmark clothes\n' +
        '\n' +
        'name %sMaterial\n' % name +
        '\n' +
        '// Color shading attributes\n'
        'ambientColor 1.0 1.0 1.0\n' +
        'diffuseColor  %.4g %.4g %.4g\n' % tuple(mat.diffuse_color) +
        'diffuseIntensity %.4g\n' % mat.diffuse_intensity +
        'specularColor  %.4g %.4g %.4g\n' % tuple(mat.specular_color) +
        'specularIntensity %.4g\n' % mat.specular_intensity +
        'specularHardness %.4g\n' % mat.specular_hardness +
        'opacity %.4g\n' % mat.alpha +
        '\n' +
        '// Textures and properties\n')

    useDiffuse = useSpecular = useBump = useNormal = useDisplacement = "false"
    for slotNo,mtex in enumerate(mat.texture_slots):
        if mtex is None or not mat.use_textures[slotNo]:
            continue
        tex = mtex.texture
        if tex.type != 'IMAGE' or tex.image is None:
            continue
        blenddir = os.path.dirname(bpy.data.filepath)
        relpath =  bpy.path.relpath(tex.image.filepath)     # starts with //
        filepath = os.path.join(blenddir, relpath[2:])
        texpath = os.path.basename(filepath).replace(" ","_")

        if mtex.use_map_color_diffuse:
            fp.write('diffuseTexture %s\n' % texpath)
            useDiffuse = "true"
        if mtex.use_map_alpha:
            useAlpha = "true"
        if mtex.use_map_specular:
            fp.write('specularTexture %s\n' % texpath)
            useSpecular = "true"
        if mtex.use_map_normal:
            if True:
                fp.write('bumpTexture %s\n' % texpath)
                useBump = "true"
            else:
                fp.write('normalTexture %s\n' % texpath)
                useNormal = "true"
        if mtex.use_map_displacement:
            fp.write('displacementTexture %s\n' % texpath)
            useDisplacement = "true"

        trgpath = os.path.join(outdir, texpath)
        print("Copy texture %s => %s" % (filepath, trgpath))
        shutil.copy(filepath, trgpath)

    fp.write(
        '\n' +
        '// Shader programme\n' +
        'shader data/shaders/glsl/phong\n' +
        '\n' +
        '// Configure built-in shader defines\n' +
        'shaderConfig diffuse %s\n' % useDiffuse +
        'shaderConfig bump %s\n' % useBump +
        'shaderConfig normal  %s\n' % useNormal +
        'shaderConfig displacement  %s\n' % useDisplacement +
        'shaderConfig spec  %s\n' % useSpecular +
        'shaderConfig vertexColors true\n')

