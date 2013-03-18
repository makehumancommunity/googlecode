#!/usr/bin/python
# -*- coding: utf-8 -*-

import mh
import gui
import gui3d

import os
import scene

class SceneItem(object):
    def __init__(self, sceneview):
        self.sceneview = sceneview
        self.widgets = []

    def showProps(self, propsWidgets):
        self.widgetList = propsWidgets
    
    def hideProps(self):
        for widget in self.widgetList:
            self.sceneview.removeRightWidget(widget)
        del self.sceneview.activePropsWidgets[:]
        self.sceneview.activeItem = None
        

class HumanSceneItem(SceneItem):
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview)
        self.widgets = ['Human rendering options']


class OutputSceneItem(SceneItem):
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview)
        self.widgets = ['Resolution']

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

    def showProps(self, propsWidgets):
        SceneItem.showProps(self, propsWidgets)
        self.widthBox = self.widgetList[0].addWidget(gui.SpinBox(self.resWidth), 0, 0)
        self.heightBox = self.widgetList[0].addWidget(gui.SpinBox(self.resHeight), 0, 1)

        @self.widthBox.mhEvent
        def onChange(value):
            self.resWidth = value

        @self.heightBox.mhEvent
        def onChange(value):
            self.resHeight = value


class SceneItemAdder(SceneItem):
    # Virtual scene item for adding scene items.
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview)
        self.widgets = ['Add Item']

    def showProps(self, propsWidgets):
        SceneItem.showProps(self, propsWidgets)
        self.lightbtn = self.widgetList[0].addWidget(gui.Button('Add light'))

        @self.lightbtn.mhEvent
        def onClicked(event):
            self.sceneview.scene.addLight()
            self.sceneview.readScene()


class CameraSceneItem(SceneItem):
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview)
        self.widgets = ['Camera properties']
        self.camera = sceneview.scene.camera


class LightSceneItem(SceneItem):
    def __init__(self, sceneview, light, lid):
        SceneItem.__init__(self, sceneview)
        self.widgets = ['Light ' + str(lid) + ' properties']
        self.lightid = lid
        self.light = light

    def showProps(self, propsWidgets):
        SceneItem.showProps(self, propsWidgets)
        self.removebtn = self.widgetList[0].addWidget(
            gui.Button('Remove light ' + str(self.lightid)))

        @self.removebtn.mhEvent
        def onClicked(event):
            self.sceneview.scene.removeLight(self.light)
            self.sceneview.readScene()
            SceneItem.hideProps(self)

    
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

        self.activePropsWidgets = []
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
            self.displayProperties(
                self.items[str(self.itemList.selectedItems()[0].text())])

        @self.addButton.mhEvent
        def onClicked(event):
            self.displayProperties(self.adder)

    def readScene(self):
        self.items = {'Human': HumanSceneItem(self),
                      'Camera': CameraSceneItem(self)}
        i = 0
        for light in self.scene.lights:
            i += 1
            self.items['Light ' + str(i)] = LightSceneItem(self, light, i)
        self.items['Output'] = OutputSceneItem(self)
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

    def displayProperties(self, sceneitem):
        if self.activeItem:
            self.activeItem.hideProps()
        self.activeItem = sceneitem
        for widgetname in sceneitem.widgets:
            self.activePropsWidgets.append(
                self.addRightWidget(gui.GroupBox(widgetname)))
        sceneitem.showProps(self.activePropsWidgets)
        
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
