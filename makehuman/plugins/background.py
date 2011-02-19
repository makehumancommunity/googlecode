#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2011

**Licensing:**         GPL3 (see also http://sites.google.com/site/makehumandocs/licensing)

**Coding Standards:**  See http://sites.google.com/site/makehumandocs/developers-guide

Abstract
--------

TO DO

"""

__docformat__ = 'restructuredtext'

import gui3d
import events3d
import mh


class BackgroundTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Background')
        self.texture = mh.Texture()
        
        mesh = gui3d.RectangleMesh(420, 420)
        self.backgroundImage = gui3d.Object(self.app.categories['Modelling'], [190, 90, 1], mesh, visible=False)
        
        modifierStyle = gui3d.ButtonStyle._replace(width=(112-4)/2.0, height=20)
        
        self.backgroundImageToggle = gui3d.ToggleButton(self.app.categories['Modelling'].viewBox, [18, 600-110+25, 9.1], 'Background',
            style=modifierStyle);
            
        @self.backgroundImageToggle.event
        def onClicked(event):
            if self.backgroundImage.isVisible():
                self.backgroundImage.hide()
                self.backgroundImageToggle.setSelected(False)
            elif self.backgroundImage.hasTexture():
                self.backgroundImage.show()
                self.backgroundImageToggle.setSelected(True)
            else:
                self.app.switchCategory('Library')
                self.app.switchTask('Background')
                
        self.filechooser = gui3d.FileChooser(self, 'backgrounds', ['bmp', 'png', 'tif', 'tiff', 'jpg', 'jpeg'], None)

        @self.filechooser.event
        def onFileSelected(filename):
            print 'Loading %s' % filename
            self.texture.loadImage('backgrounds/' + filename)

            bg = self.backgroundImage
            bg.mesh.setTexture('backgrounds/' + filename)
            group = bg.mesh.getFaceGroup('rectangle')
            group.setColor([255, 255, 255, 100])
            if self.texture.width > self.texture.height:
                bg.setScale(1.0, float(self.texture.height) / float(self.texture.width))
            else:
                bg.setScale(float(self.texture.width) / float(self.texture.height), 1.0)
            bg.mesh.setPickable(0)
            bg.show()
            self.backgroundImageToggle.setSelected(True)
            self.app.switchCategory('Modelling')
            self.app.redraw()

    def onShow(self, event):

        # When the task gets shown, set the focus to the file chooser
        gui3d.TaskView.onShow(self, event)
        self.app.selectedHuman.hide()
        self.filechooser.setFocus()

    def onHide(self, event):
        self.app.selectedHuman.show()
        gui3d.TaskView.onHide(self, event)

    def onResized(self, event):
        self.backgroundImage.mesh.resize(event[0] - 190 * 2, event[0] - 190 * 2)
        self.filechooser.onResized(event)

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Library')
    taskview = BackgroundTaskView(category)
    category = app.getCategory('Modelling')
    taskview = settingsTaskView(category, taskview)

    print 'Background chooser loaded'

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    print 'Hair chooser unloaded'
    
    
class settingsTaskView(gui3d.TaskView) :
    
    def __init__(self, category, taskview):
        
        self.backgroundImage = taskview.backgroundImage
        #gui3d.TaskView.__init__(self, category, 'Settings', category.app.getThemeResource('images', 'button_setting.png'), category.app.getThemeResource('images',
        #                        'button_setting_on.png'))
                                
        gui3d.TaskView.__init__(self, category, 'Settings', label='Settings')
                                
        #gui3d.Object(self, 'data/3dobjs/unit_square.obj', self.app.getThemeResource('images', 'group_hair_tool.png'), [10, 211, 9.0], 128,256)
        
        #############
        #SLIDERS
        #############    
        self.zoomSlider = gui3d.Slider(self, position=[10, 150, 9], value=2500, min=0.0,max=5000, label = "Zoom background")
        self.panXSlider = gui3d.Slider(self, position=[10, 200, 9], value=250, min=0.0,max=500, label = "Pan X background")
        self.panYSlider = gui3d.Slider(self, position=[10, 250, 9], value=250, min=0.0,max=500, label = "Pan Y background")
        
        @self.zoomSlider.event
        def onChanging(value):
            self.changeZoom(value)
        @self.zoomSlider.event
        def onChange(value):
            self.changeZoom(value)
        
        @self.panXSlider.event
        def onChanging(value):
            self.changePanX(value)
        @self.panXSlider.event
        def onChange(value):
            self.changePanX(value)
        
        @self.panYSlider.event
        def onChanging(value):
            self.changePanY(value)
        @self.panYSlider.event
        def onChange(value):
            self.changePanY(value)
            
        @self.backgroundImage.event
        def onMouseDragged(event):
            self.backgroundImage.setPosition([event.x, event.y, 1.0])
            
    def changeZoom(self, zoom):
        
        #bg = self.app.categories['Library'].tasksByName['Background'].backgroundImage
        self.backgroundImage.mesh.resize(zoom, zoom)
        self.backgroundImage.mesh.setPickable(1)
        self.app.redraw()
        '''if bg.hasTexture():
            bg = self.app.categories['Modelling'].tasksByName['Macro modelling'].backgroundImage
            bg.setScale(zoom, 1.0)
            self.app.scene3d.redraw(1)
            print(zoom)'''
        '''group = bg.mesh.getFaceGroup('default-dummy-group')
            group.setColor([255, 255, 255, 100])
            bg.setScale(zoom,1.0)
            bg.mesh.setPickable(0)
            self.app.scene3d.redraw(1)'''
            
    def changePanX(self,panX):
        
        #bg = self.app.categories['Library'].tasksByName['Background'].backgroundImage
        self.backgroundImage.setPosition([panX, self.backgroundImage.getPosition()[1], 1.0])
        self.app.redraw()
        
    def changePanY(self,panY):
        
        #bg = self.app.categories['Library'].tasksByName['Background'].backgroundImage
        self.backgroundImage.setPosition([self.backgroundImage.getPosition()[0], panY, 1.0])
        self.app.redraw()
