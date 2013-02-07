#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO

"""

__docformat__ = 'restructuredtext'

import os

import gui3d
import events3d
import geometry3d
import mh
import projection
import gui
import filechooser as fc
import log
from language import language

class BackgroundAction(gui3d.Action):
    def __init__(self, name, library, side, before, after):
        super(BackgroundAction, self).__init__(name)
        self.side = side
        self.library = library
        self.before = before
        self.after = after

    def do(self):
        self.library.changeBackgroundImage(self.side, self.after)
        return True

    def undo(self):
        self.library.changeBackgroundImage(self.side, self.before)
        return True

def pointInRect(point, rect):

    if point[0] < rect[0] or point[0] > rect[2] or point[1] < rect[1] or point[1] > rect[3]:
        return False
    else:
        return True

class BackgroundTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Background')

        self.backgroundsFolder = os.path.join(mh.getPath(''), 'backgrounds')
        if not os.path.exists(self.backgroundsFolder):
            os.makedirs(self.backgroundsFolder)

        self.texture = mh.Texture()

        self.sides = { 'front': [0,0,0], 
                       'back': [0,180,0], 
                       'left': [0,-90,0], 
                       'right': [0,90,0],
                       'top': [90,0,0],
                       'bottom': [-90,0,0] }

        self.filenames = {}
        for side in self.sides.keys():
            self.filenames[side] = None

        mesh = geometry3d.RectangleMesh(1, 1)
        self.backgroundImage = gui3d.app.categories['Modelling'].addObject(gui3d.Object([0, 0, 1], mesh, visible=False))
        self.opacity = 100
        mesh.setColor([255, 255, 255, self.opacity])
        mesh.setPickable(False)
        mesh.setShadeless(True)
        mesh.setDepthless(True)
        mesh.priority = -90

        self.backgroundImageToggle = gui.Action('background', 'Background', self.toggleBackground, toggle=True)
        gui3d.app.main_toolbar.addAction(self.backgroundImageToggle)

        self.filechooser = self.addTopWidget(fc.FileChooser(self.backgroundsFolder, ['bmp', 'png', 'tif', 'tiff', 'jpg', 'jpeg'], None))
        self.addLeftWidget(self.filechooser.sortBox)

        self.backgroundBox = self.addLeftWidget(gui.GroupBox('Background 2 settings'))

        self.radioButtonGroup = []
        self.bgImageFrontRadioButton  = self.backgroundBox.addWidget(gui.RadioButton(self.radioButtonGroup, label='Front', selected=True))
        self.bgImageBackRadioButton   = self.backgroundBox.addWidget(gui.RadioButton(self.radioButtonGroup, label='Back'))
        self.bgImageLeftRadioButton   = self.backgroundBox.addWidget(gui.RadioButton(self.radioButtonGroup, label='Left'))
        self.bgImageRightRadioButton  = self.backgroundBox.addWidget(gui.RadioButton(self.radioButtonGroup, label='Right'))
        self.bgImageTopRadioButton    = self.backgroundBox.addWidget(gui.RadioButton(self.radioButtonGroup, label='Top'))
        self.bgImageBottomRadioButton = self.backgroundBox.addWidget(gui.RadioButton(self.radioButtonGroup, label='Bottom'))

        @self.filechooser.mhEvent
        def onFileSelected(filename):

            if self.bgImageFrontRadioButton.selected:
                side = 'front'
            elif self.bgImageBackRadioButton.selected:
                side = 'back'
            elif self.bgImageLeftRadioButton.selected:
                side = 'left'
            elif self.bgImageRightRadioButton.selected:
                side = 'right'
            elif self.bgImageTopRadioButton.selected:
                side = 'top'
            elif self.bgImageBottomRadioButton.selected:
                side = 'bottom'

            filePath = os.path.join(self.backgroundsFolder, filename)

            if self.filenames[side]:
                oldBg = self.filenames[side][0]
            else:
                oldBg = None
            gui3d.app.do(BackgroundAction("Change background",
                self,
                side,
                oldBg,
                filename))

            gui3d.app.selectedHuman.setRotation(self.sides[side])
            mh.changeTask('Modelling', 'Background')
            mh.redraw()

    def changeBackgroundImage(self, side, texturePath):
        if not side:
            return

        if texturePath:
            # Determine aspect ratio of texture
            self.texture.loadImage(mh.Image(texturePath))
            aspect = 1.0 * self.texture.width / self.texture.height

            self.filenames[side] = (texturePath, aspect)
        else:
            self.filenames[side] = None

        if side == self.getCurrentSide():
            # Reload current texture
            self.setBackgroundImage(side)

        self.setBackgroundEnabled(self.isBackgroundSet())

    def getCurrentSide(self):
        rot = gui3d.app.selectedHuman.getRotation()
        for (side, rotation) in self.sides.items():
            if rot == rotation:
                return side
        # Indicates an arbitrary non-defined view
        return None

    def setBackgroundEnabled(self, enable):
        if enable:
            if self.isBackgroundSet():
                self.backgroundImage.show()
                # Switch to orthogonal view
                gui3d.app.modelCamera.switchToOrtho()
                self.backgroundImageToggle.setChecked(True)
                mh.redraw()
            else:
                mh.changeTask('Library', 'Background')
        else: # Disable
            self.backgroundImage.hide()
            # Switch to perspective view
            gui3d.app.modelCamera.switchToPerspective()
            self.backgroundImageToggle.setChecked(False)
            mh.redraw()

    def isBackgroundSet(self):
        for bgFile in self.filenames.values():
            if bgFile:
                return True
        return False

    def isBackgroundShowing(self):
        return self.backgroundImage.isShown()

    def isBackgroundEnabled(self):
        return self.backgroundImageToggle.isChecked()

    def toggleBackground(self):
        self.setBackgroundEnabled(self.backgroundImageToggle.isChecked())
        
    def projectBackground(self):
        if not self.backgroundImage.isVisible():
            gui3d.app.prompt("Warning", "You need to load a background before you can project it.", "OK")
            return

        mesh = gui3d.app.selectedHuman.getSeedMesh()

        # for all quads, project vertex to screen
        # if one vertex falls in bg rect, project screen quad into uv quad
        # warp image region into texture
        ((x0,y0,z0), (x1,y1,z1)) = self.backgroundImage.mesh.calcBBox()
        camera = mh.cameras[self.backgroundImage.mesh.cameraMode]
        x0, y0, _ = camera.convertToScreen(x0, y0, z0, self.backgroundImage.mesh)
        x1, y1, _ = camera.convertToScreen(x1, y1, z1, self.backgroundImage.mesh)
        leftTop = (x0, y1)
        rightBottom = (x1, y0)

        dstImg = projection.mapImage(self.backgroundImage, mesh, leftTop, rightBottom)

        dstImg.save(os.path.join(mh.getPath(''), 'data', 'skins', 'projection.png'))
        gui3d.app.selectedHuman.setTexture(os.path.join(mh.getPath(''), 'data', 'skins', 'projection.png'))

    def projectLighting(self):
        dstImg = projection.mapLighting()
        #dstImg.resize(128, 128)
        dstImg.save(os.path.join(mh.getPath(''), 'data', 'skins', 'lighting.png'))

        gui3d.app.selectedHuman.setTexture(os.path.join(mh.getPath(''), 'data', 'skins', 'lighting.png'))
        log.debug("Enabling shadeless rendering on body")
        gui3d.app.selectedHuman.mesh.setShadeless(1) # Remember to reset this when lighting projection is done.
        
    def projectUV(self):
        dstImg = projection.mapUV()
        #dstImg.resize(128, 128)
        dstImg.save(os.path.join(mh.getPath(''), 'data', 'skins', 'uvtopo.png'))

        gui3d.app.selectedHuman.setTexture(os.path.join(mh.getPath(''), 'data', 'skins', 'uvtopo.png'))
        log.debug("Enabling shadeless rendering on body")
        gui3d.app.selectedHuman.mesh.setShadeless(1) # Remember to reset this when lighting projection is done.
        
    def onShow(self, event):

        gui3d.TaskView.onShow(self, event)
        gui3d.app.selectedHuman.hide()
        gui3d.app.prompt('Info', language.getLanguageString(u'Images which are placed in %s will show up here.') % self.backgroundsFolder, 'OK', helpId='backgroundHelp')
        self.filechooser.setFocus()

    def onHide(self, event):

        gui3d.TaskView.onHide(self, event)
        gui3d.app.selectedHuman.show()
        gui3d.TaskView.onHide(self, event)

    def onHumanTranslated(self, event):
        pass

    def onHumanChanging(self, event):
        
        human = event.human
        if event.change == 'reset':
            for side in self.sides.keys():
                self.filenames[side] = None
            self.setBackgroundEnabled(False)

    def setBackgroundImage(self, side):
        if not side:
            self.backgroundImage.hide()
            return

        if self.filenames.get(side):
            (filename, aspect) = self.filenames.get(side)
        else:
            filename = aspect = None
        if filename:
            self.backgroundImage.setPosition([-aspect, -1, 0])
            self.backgroundImage.mesh.resize(2.0 * aspect, 2.0)

            self.backgroundImage.mesh.setTexture(filename)
            self.backgroundImage.show()
        else:
            self.backgroundImage.hide()

    def onHumanRotated(self, event):
        self.setBackgroundImage(self.getCurrentSide())


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Library')
    taskview = category.addTask(BackgroundTaskView(category))
    category = app.getCategory('Modelling')
    taskview = category.addTask(settingsTaskView(category, taskview))

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass


class settingsTaskView(gui3d.TaskView) :

    def __init__(self, category, taskview):

        self.backgroundImage = taskview.backgroundImage
        self.texture = taskview.texture

        gui3d.TaskView.__init__(self, category, 'Background')

        y = 80

        self.lastPos = [0, 0]

        self.backgroundBox = self.addLeftWidget(gui.GroupBox('Background settings'))

        # sliders
        self.opacitySlider = self.backgroundBox.addWidget(gui.Slider(value=taskview.opacity, min=0,max=255, label = "Opacity: %d"))

        @self.opacitySlider.mhEvent
        def onChanging(value):
            self.backgroundImage.mesh.setColor([255, 255, 255, value])
        @self.opacitySlider.mhEvent
        def onChange(value):
            taskview.opacity = value
            self.backgroundImage.mesh.setColor([255, 255, 255, value])

        @self.backgroundImage.mhEvent
        def onMouseDragged(event):

            if event.button == mh.Buttons.LEFT_MASK:
                ((x0,y0,z0),(x1,y1,z1)) = self.backgroundImage.mesh.calcBBox()
                x, y, z = gui3d.app.guiCamera.convertToScreen(x0, y0, z0, self.backgroundImage.mesh)
                x += event.dx
                y += event.dy
                x, y, z = gui3d.app.guiCamera.convertToWorld3D(x, y, z, self.backgroundImage.mesh)
                dx, dy = x - x0, y - y0
                x, y, z = self.backgroundImage.getPosition()
                self.backgroundImage.setPosition([x + dx, y + dy, z])
            elif event.button == mh.Buttons.RIGHT_MASK:
                ((x0,y0,z0),(x1,y1,z1)) = self.backgroundImage.mesh.calcBBox()
                x0, y0, z0 = gui3d.app.guiCamera.convertToScreen(x0, y0, z0, self.backgroundImage.mesh)
                x1, y1, z1 = gui3d.app.guiCamera.convertToScreen(x1, y1, z1, self.backgroundImage.mesh)
                dx, dy = x1 - x0, y0 - y1
                if abs(event.dx) > abs(event.dy):
                    dx += event.dx
                    dy = dx * self.texture.height / self.texture.width
                else:
                    dy += event.dy
                    dx = dy * self.texture.width / self.texture.height
                x1, y0 = x0 + dx, y1 + dy
                x0, y0, z0 = gui3d.app.guiCamera.convertToWorld3D(x0, y0, z0, self.backgroundImage.mesh)
                x1, y1, z1 = gui3d.app.guiCamera.convertToWorld3D(x1, y1, z1, self.backgroundImage.mesh)
                self.backgroundImage.mesh.resize(x1 - x0, y1 - y0)
                self.backgroundImage.mesh.move(x0, y0)

        self.dragButton = self.backgroundBox.addWidget(gui.ToggleButton('Move && Resize'))

        @self.dragButton.mhEvent
        def onClicked(event):
            self.backgroundImage.mesh.setPickable(self.dragButton.selected)
            mh.updatePickingBuffer()

        self.projectBackgroundButton = self.backgroundBox.addWidget(gui.Button('Project background'))

        @self.projectBackgroundButton.mhEvent
        def onClicked(event):
            taskview.projectBackground()

        self.projectLightingButton = self.backgroundBox.addWidget(gui.Button('Project lighting'))

        @self.projectLightingButton.mhEvent
        def onClicked(event):
            taskview.projectLighting()

        self.projectUVButton = self.backgroundBox.addWidget(gui.Button('Project UV topology'))

        @self.projectUVButton.mhEvent
        def onClicked(event):
            taskview.projectUV()

    def onShow(self, event):

        gui3d.TaskView.onShow(self, event)
        self.backgroundImage.mesh.setPickable(self.dragButton.selected)

    def onHide(self, event):

        gui3d.TaskView.onHide(self, event)
        self.backgroundImage.mesh.setPickable(0)
