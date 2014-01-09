#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Internal OpenGL Renderer Functions.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

"""

import os
import projection
import mh
import log
import gui3d
from core import G
import gui
import image
from progress import Progress
import glmodule
import numpy as np

def Render(settings):
    # TODO hide unneeded scene objects

    if settings['lightmapSSS']:
        import image_operations as imgop
        human = G.app.selectedHuman
        lmap = projection.mapSceneLighting(settings['scene'])
        lmapG = imgop.blurred(lmap, human.material.sssGScale, 13)
        lmapR = imgop.blurred(lmap, human.material.sssRScale, 13)
        lmap = imgop.compose([lmapR, lmapG, lmap])
        lmap.sourcePath = "Internal_Renderer_Lightmap_SSS_Texture"
        human.material.diffuseTexture = lmap
        settings['oldDiffuseShaderSetting'] = human.material.shaderConfig['diffuse']
        human.mesh.configureShading(diffuse = True)
        settings['oldShadelessSetting'] = human.mesh.shadeless
        human.mesh.shadeless = True

    if not glmodule.hasRenderToRenderbuffer():
        # Limited fallback mode, read from screen buffer
        img = glmodule.grabScreen(0, 0, G.windowWidth, G.windowHeight)
        # TODO disable resolution GUI setting in fallback mode
    else:
        # Render to framebuffer object
        width, height = settings['dimensions']
        if settings['AA']:
            width = width * 2
            height = height * 2
        img = glmodule.renderToBuffer(width, height)

        if settings['AA']:
            # Resize to 50% using Qt image class
            qtImg = img.toQImage()
            del img
            # Bilinear filtered resize for anti-aliasing
            scaledImg = qtImg.scaled(width/2, height/2, transformMode = gui.QtCore.Qt.SmoothTransformation)
            del qtImg
            img = scaledImg
            #img = image.Image(scaledImg)    # Convert back to MH image
            #del scaledImg

    if settings['lightmapSSS']:
        human = G.app.selectedHuman
        human.mesh.shadeless = settings['oldShadelessSetting']
        human.mesh.configureShading(diffuse = settings['oldDiffuseShaderSetting'])

    # TODO restore scene object visibility

    gui3d.app.getCategory('Rendering').getTaskByName('Viewer').setImage(img)
    mh.changeTask('Rendering', 'Viewer')
    gui3d.app.statusPersist('Rendering complete.')

