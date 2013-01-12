#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Python compatibility layer replacing the old C functions of MakeHuman.
"""

import json

from core import G
from getpath import getPath
import glmodule as gl

import qtui as ui

from image import Image
from texture import Texture
from object3d import Object3D
from camera import Camera

from qtui import getKeyModifiers, addTimer, removeTimer, callAsync
from glmodule import createVertexShader, createFragmentShader, createShader
from glmodule import updatePickingBuffer, grabScreen, hasRenderSkin, renderSkin

cameras = G.cameras

Keys = ui.Keys
Buttons = ui.Buttons
Modifiers = ui.Modifiers

def getColorPicked():
    return G.color_picked

def setClearColor(r, g, b, a):
    G.clearColor = (r, g, b, a)

Application = ui.Application

def setCaption(caption):
    G.app.mainwin.setWindowTitle(caption)

def removeWidget(edge, widget):
    return G.app.mainwin.removeWidget(edge, widget)

def changeCategory(category):
    G.app.mainwin.tabs.changeTab(category)

def changeTask(category, task):
    changeCategory(category)
    G.app.mainwin.tabs.findTab(category).child.changeTab(task)

def refreshLayout():
    G.app.mainwin.refreshLayout()

def addPanels():
    return G.app.mainwin.addPanels()

def showPanels(left, right):
    return G.app.mainwin.showPanels(left, right)

def addPanelBottomLeft():
    return G.app.mainwin.addPanelBottomLeft()

def showPanelBottomLeft(panel):
    return G.app.mainwin.showPanelBottomLeft(panel)

def getPanelBottomRight():
    return G.app.mainwin.getPanelBottomRight()

def addTopWidget(widget, *args, **kwargs):
    return G.app.mainwin.addTopWidget(widget, *args, **kwargs)

def removeTopWidget(widget):
    return G.app.mainwin.removeTopWidget(widget)

def addObject(obj):
    G.world.append(obj)

def removeObject(obj):
    G.world.remove(obj)

def setShortcut(modifier, key, method):
    G.app.mainwin.setShortcut(modifier, key, method)

def parse_ini(s):
    try:
        return dict([(str(key), str(val) if isinstance(val, unicode) else val)
                     for key, val in json.loads(s).iteritems()])
    except ValueError:
        s = s.replace("'",'"').replace(": True",": true").replace(": False",": false").replace(": None",": null")
        return dict([(str(key), str(val) if isinstance(val, unicode) else val)
                     for key, val in json.loads(s).iteritems()])

def format_ini(d):
    return json.dumps(d, indent=4, ensure_ascii=True, encoding='iso-8859-1') + '\n'
