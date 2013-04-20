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

    def update(self):
        pass

    def __del__(self):
        self.widget.destroy()
        

class HumanSceneItem(SceneItem):
    def __init__(self, sceneview):
        self.human = sceneview.scene.human
        SceneItem.__init__(self, sceneview)

    def makeProps(self):
        SceneItem.makeProps(self)
        
        self.widget.addWidget(gui.TextView("Position"))
        self.posbox = self.widget.addWidget(gui.TextEdit(
            ", ".join([str(x) for x in self.human.position])))
        
        self.widget.addWidget(gui.TextView("Rotation"))
        self.rotbox = self.widget.addWidget(gui.TextEdit(
            ", ".join([str(x) for x in self.human.rotation])))

        @self.posbox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.human.position = tuple([float(x) for x in value.split(",")])
            except: # The user hasn't typed the value correctly yet.
                pass

        @self.rotbox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.human.rotation = tuple([float(x) for x in value.split(",")])
            except:
                pass

    def update(self):
        self.posbox.setText(", ".join([str(x) for x in self.human.position]))
        self.rotbox.setText(", ".join([str(x) for x in self.human.rotation]))


class OutputSceneItem(SceneItem):
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview)

    @property
    def resWidth(self):
        return gui3d.app.settings.get('rendering_width', 800)

    @property
    def resHeight(self):
        return gui3d.app.settings.get('rendering_height', 600)

    @property
    def AA(self):
        return gui3d.app.settings.get('rendering_AA', 0.5)

    @resWidth.setter
    def resWidth(self, value = None):
        gui3d.app.settings['rendering_width'] = 0 if not value else int(value)

    @resHeight.setter
    def resHeight(self, value = None):
        gui3d.app.settings['rendering_height'] = 0 if not value else int(value)

    @AA.setter
    def AA(self, value = None):
        gui3d.app.settings['rendering_AA'] = 0.5 if not value else float(value)

    def makeProps(self):
        SceneItem.makeProps(self)
        self.widget.addWidget(gui.TextView("Resolution"))
        self.resBox = self.widget.addWidget(gui.TextEdit(
            "x".join([str(self.resWidth), str(self.resHeight)])))
        self.AAslider = self.widget.addWidget(gui.Slider(
            value=self.AA, label="AntiAliasing"))

        @self.resBox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                res = [int(x) for x in value.split("x")]
                self.resWidth = res[0]
                self.resHeight = res[1]
            except: # The user hasn't typed the value correctly yet.
                pass

        @self.AAslider.mhEvent
        def onChange(value):
            self.AA = value

            
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

    def makeProps(self):
        SceneItem.makeProps(self)

        self.widget.addWidget(gui.TextView("Position"))
        self.posbox = self.widget.addWidget(gui.TextEdit(
            ", ".join([str(x) for x in self.camera.eye])))
        
        self.widget.addWidget(gui.TextView("Focus"))
        self.focbox = self.widget.addWidget(gui.TextEdit(
            ", ".join([str(x) for x in self.camera.focus])))
        
        self.widget.addWidget(gui.TextView("Field Of View"))
        self.fov = self.widget.addWidget(gui.TextEdit(str(self.camera.fovAngle)))

        @self.posbox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.camera.eye = tuple([float(x) for x in value.split(",")])
            except: # The user hasn't typed the value correctly yet.
                pass

        @self.focbox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.camera.focus = tuple([float(x) for x in value.split(",")])
            except:
                pass

        @self.fov.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.camera.fovAngle = float(value)
            except:
                pass

    def update(self):
        self.posbox.setText(", ".join([str(x) for x in self.camera.eye]))
        self.focbox.setText(", ".join([str(x) for x in self.camera.focus]))
        self.fov.setText(str(self.camera.fovAngle))


class EnvironmentSceneItem(SceneItem):
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview)

    def makeProps(self):
        SceneItem.makeProps(self)

        self.widget.addWidget(gui.TextView("Ambience"))
        self.colbox = self.widget.addWidget(gui.TextEdit(
            ", ".join([str(x) for x in self.sceneview.scene.ambience])))

        @self.colbox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.sceneview.scene.ambience = tuple([float(x) for x in value.split(",")])
            except:
                pass
            
     
class LightSceneItem(SceneItem):
    def __init__(self, sceneview, light, lid):
        self.lightid = lid
        self.light = light
        SceneItem.__init__(self, sceneview)

    def makeProps(self):
        SceneItem.makeProps(self)
        
        self.widget.addWidget(gui.TextView("Position"))
        self.posbox = self.widget.addWidget(gui.TextEdit(
            ", ".join([str(x) for x in self.light.position])))
        
        self.widget.addWidget(gui.TextView("Focus"))
        self.focbox = self.widget.addWidget(gui.TextEdit(
            ", ".join([str(x) for x in self.light.focus])))
        
        self.widget.addWidget(gui.TextView("Color"))
        self.colbox = self.widget.addWidget(gui.TextEdit(
            ", ".join([str(x) for x in self.light.color])))
        
        self.widget.addWidget(gui.TextView("Spot angle"))
        self.fov = self.widget.addWidget(gui.TextEdit(str(self.light.fov)))

        self.widget.addWidget(gui.TextView("Attenuation"))
        self.att = self.widget.addWidget(gui.TextEdit(str(self.light.attenuation)))

        self.removebtn = self.widget.addWidget(
            gui.Button('Remove light ' + str(self.lightid)))

        @self.posbox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.light.position = tuple([float(x) for x in value.split(",")])
            except: # The user hasn't typed the value correctly yet.
                pass

        @self.focbox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.light.focus = tuple([float(x) for x in value.split(",")])
            except:
                pass

        @self.colbox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.light.color = tuple([float(x) for x in value.split(",")])
            except:
                pass

        @self.fov.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.light.fov = float(value)
            except:
                pass

        @self.att.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                self.light.attenuation = float(value)
            except:
                pass

        @self.removebtn.mhEvent
        def onClicked(event):
            self.sceneview.scene.removeLight(self.light)
            self.sceneview.readScene()


class SceneTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Scene')
        sceneBox = self.addLeftWidget(gui.GroupBox('Scene'))
        self.fnlbl = sceneBox.addWidget(gui.TextView('<New scene>'))
        self.saveButton = sceneBox.addWidget(gui.Button('Save'), 1, 0)
        self.loadButton = sceneBox.addWidget(gui.Button('Load ...'), 1, 1)
        self.saveAsButton = sceneBox.addWidget(gui.Button('Save As...'), 2, 0)
        self.closeButton = sceneBox.addWidget(gui.Button('Close'), 2, 1)

        self.dontRefresh = True
        self.isShown = False

        itemBox = self.addLeftWidget(gui.GroupBox('Items'))
        self.itemList = itemBox.addWidget(gui.ListView())
        self.itemList.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)

        self.propsBox = gui.StackedBox()
        self.addRightWidget(self.propsBox)

        self.addButton = itemBox.addWidget(gui.Button('Add...'))
        self.adder = SceneItemAdder(self)
        self.propsBox.addWidget(self.adder.widget)

        self.items = {}
        self.activeItem = None
        self.scene = scene.Scene()
        self.readScene()

        def doLoad():
            filename = mh.getOpenFileName(mh.getPath("scenes"), 'MakeHuman scene (*.mhscene);;All files (*.*)')
            if filename:
                self.scene.load(filename)
                self.readScene()

        @self.scene.mhEvent
        def onChanged(scene):
            self.refreshScene()

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
        def onClicked(event):
            self.items[self.itemList.getSelectedItem()].showProps()

        @self.addButton.mhEvent
        def onClicked(event):
            self.adder.showProps()

    def readScene(self):
        self.adder.showProps()
        self.items.clear()
        self.items = {'Human': HumanSceneItem(self),
                      'Camera': CameraSceneItem(self),
                      'Environment': EnvironmentSceneItem(self)}
        i = 0
        for light in self.scene.lights:
            i += 1
            self.items['Light ' + str(i)] = LightSceneItem(self, light, i)
        self.items['Output'] = OutputSceneItem(self)
        for item in self.items.values():
            self.propsBox.addWidget(item.widget)
        self.itemList.setData(self.items.keys()[::-1])
        self.refreshScene()

    def refreshScene(self):
        if (self.dontRefresh):
            return
        self.storeCamera(self.scene.camera, gui3d.app.modelCamera)
        gui3d.app.selectedHuman.setPosition(self.scene.human.position)
        gui3d.app.selectedHuman.setRotation(self.scene.human.rotation)
        self.updateFileTitle()

    def update(self):
        if (self.isShown):
            self.dontRefresh = True
            self.storeCamera(gui3d.app.modelCamera, self.scene.camera)
            self.scene.human.position = gui3d.app.selectedHuman.getPosition()
            self.scene.human.rotation = gui3d.app.selectedHuman.getRotation()
            self.updateItems()
            self.dontRefresh = False
            self.updateFileTitle()
        
    def updateItems(self):
        for item in self.items.values():
            item.update()
        
    def onHumanTranslated(self, event):
        self.update()

    def onHumanRotated(self, event):
        self.update()
        
    def onMouseWheel(self, event):
        gui3d.TaskView.onMouseWheel(self, event)
        self.update()

    def onMouseDragged(self, event):
        gui3d.TaskView.onMouseDragged(self, event)
        self.update()
        
    def updateFileTitle(self):
        if self.scene.path is None:
            lbltxt = '<New scene>'
        else:
            lbltxt = os.path.basename(self.scene.path)
        if self.scene.unsaved:
            lbltxt += '*'
        self.fnlbl.setText(lbltxt)

    def storeCamera(self, fromCamera = None, toCamera = None):
        if (fromCamera is None):    # Pop.
            toCamera.eye = self.storedCamEye
            toCamera.focus = self.storedCamFocus
            toCamera.fovAngle = self.storedCamFov
        elif (toCamera is None):    # Push.
            self.storedCamEye = fromCamera.eye
            self.storedCamFocus = fromCamera.focus
            self.storedCamFov = fromCamera.fovAngle
        else:
            toCamera.eye = fromCamera.eye
            toCamera.focus = fromCamera.focus
            toCamera.fovAngle = fromCamera.fovAngle        
        
    def storeHuman(self, human):
        self.storedHumanPos = human.getPosition()
        self.storedHumanRot = human.getRotation()
        
    def restoreHuman(self, human):
        human.setPosition(self.storedHumanPos)
        human.setRotation(self.storedHumanRot)

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        self.dontRefresh = False
        gui3d.app.status('Scene Editor')
        self.storeCamera(gui3d.app.modelCamera)
        self.storeHuman(gui3d.app.selectedHuman)
        self.refreshScene()
        self.isShown = True     # Do this last.

    def onHide(self, event):
        self.isShown = False    # Do this first.
        self.dontRefresh = True
        gui3d.TaskView.onHide(self, event)
        self.storeCamera(None, gui3d.app.modelCamera)
        self.restoreHuman(gui3d.app.selectedHuman)
        gui3d.app.saveSettings()
        gui3d.app.statusPersist('')


def load(app):
    category = app.getCategory('Rendering')
    taskview = category.addTask(SceneTaskView(category))

def unload(app):
    pass
