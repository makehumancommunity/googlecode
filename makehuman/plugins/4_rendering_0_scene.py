#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Scene editor plugin.
"""

import mh
import gui
import gui3d

import os
import scene


class SceneItem(object):
    def __init__(self, sceneview):
        # Call this last
        self.sceneview = sceneview
        self.widget = gui.GroupBox()
        self.makeProps()

    def makeProps(self):
        pass

    def showProps(self):
        self.sceneview.propsBox.showWidget(self.widget)
        self.sceneview.activeItem = self

    def __del__(self):
        self.widget.destroy()
        

class HumanSceneItem(SceneItem):
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview)


class OutputSceneItem(SceneItem):
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview)

    @property
    def resWidth(self):
        return gui3d.app.settings.get('rendering_width', 800)

    @property
    def resHeight(self):
        return gui3d.app.settings.get('rendering_height', 600)

    @resWidth.setter
    def resWidth(self, value = None):
        gui3d.app.settings['rendering_width'] = 0 if not value else int(value)

    @resHeight.setter
    def resHeight(self, value = None):
        gui3d.app.settings['rendering_height'] = 0 if not value else int(value)

    def makeProps(self):
        SceneItem.makeProps(self)
        self.widget.addWidget(gui.TextView("Resolution"))
        self.resBox = self.widget.addWidget(gui.TextEdit(
            "x".join([str(self.resWidth), str(self.resHeight)])))

        @self.resBox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                res = [int(x) for x in value.split("x")]
                self.resWidth = res[0]
                self.resHeight = res[1]
            except: # The user hasn't typed the value correctly yet.
                pass


class SceneItemAdder(SceneItem):
    # Virtual scene item for adding scene items.
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview)

    def makeProps(self):
        SceneItem.makeProps(self)
        self.lightbtn = self.widget.addWidget(gui.Button('Add light'))

        @self.lightbtn.mhEvent
        def onClicked(event):
            self.sceneview.scene.addLight()
            self.sceneview.readScene()


class CameraSceneItem(SceneItem):
    def __init__(self, sceneview):
        self.camera = sceneview.scene.camera
        SceneItem.__init__(self, sceneview)


class LightSceneItem(SceneItem):
    def __init__(self, sceneview, light, lid):
        self.lightid = lid
        self.light = light
        SceneItem.__init__(self, sceneview)

    def makeProps(self):
        SceneItem.makeProps(self)
        self.widget.addWidget(gui.TextView("Position"))
        self.posbox = self.widget.addWidget(gui.TextEdit(
            ", ".join([str(x) for x in self.light.pos])))
        self.removebtn = self.widget.addWidget(
            gui.Button('Remove light ' + str(self.lightid)))

        @self.removebtn.mhEvent
        def onClicked(event):
            self.sceneview.scene.removeLight(self.light)
            self.sceneview.readScene()

        @self.posbox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.light.pos = tuple([float(x) for x in value.split(",")])
            except: # The user hasn't typed the value correctly yet.
                pass


class SceneTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Scene')
        sceneBox = self.addLeftWidget(gui.GroupBox('Scene'))
        self.fnlbl = sceneBox.addWidget(gui.TextView('<New scene>'))
        self.saveButton = sceneBox.addWidget(gui.Button('Save'), 1, 0)
        self.loadButton = sceneBox.addWidget(gui.Button('Load ...'), 1, 1)
        self.saveAsButton = sceneBox.addWidget(gui.Button('Save As...'), 2, 0)
        self.closeButton = sceneBox.addWidget(gui.Button('Close'), 2, 1)

        itemBox = self.addLeftWidget(gui.GroupBox('Items'))
        self.itemList = itemBox.addWidget(gui.ListView())
        self.itemList.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)

        self.addButton = itemBox.addWidget(gui.Button('Add...'))
        self.adder = SceneItemAdder(self)

        self.propsBox = gui.StackedBox()
        self.addRightWidget(self.propsBox)

        self.items = {}
        self.activeItem = None
        self.scene = scene.Scene()
        self.readScene()

        def doLoad():
            filename = mh.getOpenFileName(mh.getPath("scenes"), 'MakeHuman scene (*.mhscene);;All files (*.*)')
            if filename:
                self.scene.load(filename)
                self.readScene()

        @self.loadButton.mhEvent
        def onClicked(event):
            if self.scene.unsaved:
                gui3d.app.prompt('Confirmation',
                                 'Your scene is unsaved. Are you sure you want to close it?',
                                 'Close','Cancel',doLoad())
            else:
                doLoad()

        @self.saveButton.mhEvent
        def onClicked(event):
            if self.scene.path is None:
                self.saveAsButton.callEvent('onClicked', None)
            else:
                self.scene.save()
            self.updateFileTitle()

        @self.closeButton.mhEvent
        def onClicked(event):
            if self.scene.unsaved:
                gui3d.app.prompt('Confirmation',
                                 'Your scene is unsaved. Are you sure you want to close it?',
                                 'Close','Cancel',self.scene.close())
            else:
                self.scene.close()
            self.readScene()

        @self.saveAsButton.mhEvent
        def onClicked(event):
            filename = mh.getSaveFileName(mh.getPath("scenes"), 'MakeHuman scene (*.mhscene);;All files (*.*)')
            if filename:
                self.scene.save(filename)
            self.updateFileTitle()
                
        @self.itemList.mhEvent
        def onActivate(event):
            self.items[self.itemList.getSelectedItem()].showProps()

        @self.addButton.mhEvent
        def onClicked(event):
            self.adder.showProps()

    def readScene(self):
        self.items.clear()
        self.items = {'Human': HumanSceneItem(self),
                      'Camera': CameraSceneItem(self)}
        i = 0
        for light in self.scene.lights:
            i += 1
            self.items['Light ' + str(i)] = LightSceneItem(self, light, i)
        self.items['Output'] = OutputSceneItem(self)
        for item in self.items.values():
            self.propsBox.addWidget(item.widget)
        self.itemList.setData(self.items.keys()[::-1])
        self.updateFileTitle()

    def updateFileTitle(self):
        if self.scene.path is None:
            lbltxt = '<New scene>'
        else:
            lbltxt = os.path.basename(self.scene.path)
        if self.scene.unsaved:
            lbltxt += '*'
        self.fnlbl.setText(lbltxt)
        
    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        gui3d.app.statusPersist('Scene Editor. Double - click a list item to view its properties.')

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)
        gui3d.app.saveSettings()
        gui3d.app.statusPersist('')


def load(app):
    category = app.getCategory('Rendering')
    taskview = category.addTask(SceneTaskView(category))

def unload(app):
    pass
