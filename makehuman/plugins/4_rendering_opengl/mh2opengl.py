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
            # Bilinear filtered resize for anti-aliasing
            qtImg = qtImg.scaled(width/2, height/2, transformMode = gui.QtCore.Qt.SmoothTransformation)
            img = image.Image(qtImg)    # Convert back to MH image

    # TODO restore scene object visibility

    path = mh.getPath('render/opengl_render.png')
    img.save(path)

    gui3d.app.getCategory('Rendering').getTaskByName('Viewer').setImage(path)
    mh.changeTask('Rendering', 'Viewer')
    gui3d.app.statusPersist('Rendering complete. Output path: %s' % path)

