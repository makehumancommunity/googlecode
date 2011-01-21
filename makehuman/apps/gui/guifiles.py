#!/usr/bin/python
# -*- coding: utf-8 -*-
# You may use, modify and redistribute this module under the terms of the GNU GPL.

""" 
Class for handling File mode in the GUI.

B{Project Name:}      MakeHuman

B{Product Home Page:} U{http://www.makehuman.org/}

B{Code Home Page:}    U{http://code.google.com/p/makehuman/}

B{Authors:}           Marc Flerackers

B{Copyright(c):}      MakeHuman Team 2001-2010

B{Licensing:}         GPL3 (see also U{http://sites.google.com/site/makehumandocs/licensing})

B{Coding Standards:}  See U{http://sites.google.com/site/makehumandocs/developers-guide}

Abstract
========

This module implements the 'guifiles' class structures and methods to support GUI 
File mode operations.
File mode is invoked by selecting the File mode icon from the main GUI control bar at the top of
the screen. While in this mode, user actions (keyboard and mouse events) are passed into 
this class for processing. Having processed an event this class returns control to the 
main OpenGL/SDL/Application event handling loop.  

"""

import mh
import files3d
import animation3d
import gui3d
import events3d
import os
import mh2obj
import mh2bvh
import mh2mhx
import mh2proxy
import mh2collada
import mh2md5
import mh2stl
import hair

class SaveTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Save')
        self.fileentry = gui3d.FileEntryView(self)

        @self.fileentry.event
        def onFileSelected(filename):
            modelPath = mh.getPath('models')
            if not os.path.exists(modelPath):
                os.makedirs(modelPath)

            tags = filename
            filename = filename.split()[0]

            # Save the thumbnail

            leftTop = mh.cameras[0].convertToScreen(-10, 9, 0)
            rightBottom = mh.cameras[0].convertToScreen(10, -10, 0)
            self.app.scene3d.grabScreen(int(leftTop[0]), int(leftTop[1]), int(rightBottom[0] - leftTop[0]), int(rightBottom[1] - leftTop[1]), os.path.join(modelPath, filename + '.bmp'))

            # Save the model

            human = self.app.scene3d.selectedHuman
            human.save(os.path.join(modelPath, filename + '.mhm'), tags)

            self.app.switchCategory('Modelling')
            self.app.scene3d.redraw(1)

    def onShow(self, event):

        # When the task gets shown, set the focus to the file entry

        gui3d.TaskView.onShow(self, event)
        self.fileentry.setFocus()
        self.pan = self.app.scene3d.selectedHuman.getPosition()
        self.eyeX = mh.cameras[0].eyeX
        self.eyeY = mh.cameras[0].eyeY
        self.eyeZ = mh.cameras[0].eyeZ
        self.focusX = mh.cameras[0].focusX
        self.focusY = mh.cameras[0].focusY
        self.focusZ = mh.cameras[0].focusZ
        self.rotation = self.app.scene3d.selectedHuman.getRotation()
        self.app.scene3d.selectedHuman.setPosition([0, -1, 0])
        self.app.setGlobalCamera();
        mh.cameras[0].eyeZ = 70
        self.app.scene3d.selectedHuman.setRotation([0.0, 0.0, 0.0])

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)
        self.app.scene3d.selectedHuman.setPosition(self.pan)
        mh.cameras[0].eyeX = self.eyeX
        mh.cameras[0].eyeY = self.eyeY
        mh.cameras[0].eyeZ = self.eyeZ
        mh.cameras[0].focusX = self.focusX
        mh.cameras[0].focusY = self.focusY
        mh.cameras[0].focusZ = self.focusZ
        self.app.scene3d.selectedHuman.setRotation(self.rotation)


class LoadTaskView(gui3d.TaskView):

    def __init__(self, category):
        modelPath = mh.getPath('models')
        gui3d.TaskView.__init__(self, category, 'Load', )
        self.filechooser = gui3d.FileChooser(self, modelPath, 'mhm')

        @self.filechooser.event
        def onFileSelected(filename):

            human = self.app.scene3d.selectedHuman

            human.load(os.path.join(modelPath, filename), self.app.progress)

            del self.app.undoStack[:]
            del self.app.redoStack[:]

            self.parent.tasksByName['Save'].fileentry.text = filename.replace('.mhm', '')
            self.parent.tasksByName['Save'].fileentry.edit.setText(filename.replace('.mhm', ''))

            self.app.switchCategory('Modelling')
            self.app.scene3d.redraw(1)

    def onShow(self, event):

        # When the task gets shown, set the focus to the file chooser

        self.app.scene3d.selectedHuman.hide()
        gui3d.TaskView.onShow(self, event)
        self.filechooser.setFocus()

        # HACK: otherwise the toolbar background disappears for some weird reason

        self.app.scene3d.redraw(0)

    def onHide(self, event):
        self.app.scene3d.selectedHuman.show()
        gui3d.TaskView.onHide(self, event)


class ExportTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Export')
        self.fileentry = gui3d.FileEntryView(self)

        self.exportBodyGroup = []
        self.exportHairGroup = []
        
        # Formats
        y = 80
        gui3d.GroupBox(self, [10, y, 9.0], 'Format', gui3d.GroupBoxStyle._replace(height=150));y+=25
        self.wavefrontObj = gui3d.RadioButton(self, self.exportBodyGroup, [18, y, 9.2], "Wavefront obj", True, gui3d.ButtonStyle);y+=22
        self.mhx = gui3d.RadioButton(self, self.exportBodyGroup, [18, y, 9.2], label="Blender exchange", style=gui3d.ButtonStyle);y+=22
        self.collada = gui3d.RadioButton(self, self.exportBodyGroup, [18, y, 9.2], label="Collada", style=gui3d.ButtonStyle);y+=22
        self.md5 = gui3d.RadioButton(self, self.exportBodyGroup, [18, y, 9.2], label="MD5", style=gui3d.ButtonStyle);y+=22
        self.stl = gui3d.RadioButton(self, self.exportBodyGroup, [18, y, 9.2], label="STL", style=gui3d.ButtonStyle);y+=22
            
        # OBJ options
        y = 240
        self.objOptions = gui3d.GroupBox(self, [10, y, 9.0], 'Options', gui3d.GroupBoxStyle._replace(height=150));y+=25
        self.exportDiamonds = gui3d.CheckBox(self.objOptions, [18, y, 9.2], "Diamonds", False);y+=22
        self.exportSkeleton = gui3d.CheckBox(self.objOptions, [18, y, 9.2], "Skeleton", True);y+=22
        self.exportGroups = gui3d.CheckBox(self.objOptions, [18, y, 9.2], "Groups", True);y+=22
        self.hairMesh = gui3d.RadioButton(self.objOptions, self.exportHairGroup, [18, y, 9.2], "Hair as mesh", selected=True);y+=22
        self.hairCurves = gui3d.RadioButton(self.objOptions, self.exportHairGroup, [18, y, 9.2], "Hair as curves");y+=22
        
        # MHX options
        y = 240
        self.mhxOptions = gui3d.GroupBox(self, [10, y, 9.0], 'Options', gui3d.GroupBoxStyle._replace(height=150));y+=25
        self.version24 = gui3d.CheckBox(self.mhxOptions, [18, y, 9.2], "Version 2.4", True);y+=22
        self.version25 = gui3d.CheckBox(self.mhxOptions, [18, y, 9.2], "Version 2.5", True);y+=22
        self.exportExpressions = gui3d.CheckBox(self.mhxOptions, [18, y, 9.2], "Expressions", True);y+=22
        rigs = []
        self.mhxRig = gui3d.RadioButton(self.mhxOptions, rigs, [18, y, 9.2], "Use mhx rig", True);y+=22
        self.gameRig = gui3d.RadioButton(self.mhxOptions, rigs, [18, y, 9.2], "Use game rig");y+=22
        self.mhxOptions.hide()
        
        @self.wavefrontObj.event
        def onClicked(event):
            gui3d.RadioButton.onClicked(self.wavefrontObj, event)
            self.updateGui()
            
        @self.mhx.event
        def onClicked(event):
            gui3d.RadioButton.onClicked(self.mhx, event)
            self.updateGui()
        
        @self.collada.event
        def onClicked(event):
            gui3d.RadioButton.onClicked(self.collada, event)
            self.updateGui()
        
        @self.md5.event
        def onClicked(event):
            gui3d.RadioButton.onClicked(self.md5, event)
            self.updateGui()
        
        @self.stl.event
        def onClicked(event):
            gui3d.RadioButton.onClicked(self.stl, event)
            self.updateGui()
        
        @self.fileentry.event
        def onFileSelected(filename):
            exportPath = mh.getPath('exports')
            if not os.path.exists(exportPath):
                os.makedirs(exportPath)

            if self.wavefrontObj.selected:
                mh2obj.exportObj(self.app.scene3d.selectedHuman.meshData,
                    os.path.join(exportPath, filename + ".obj"),
                    'data/3dobjs/base.obj',
                    self.exportGroups.selected,
                    None if self.exportDiamonds.selected else (lambda fg: not 'joint' in fg))
                mh2proxy.exportProxyObj(self.app.scene3d.selectedHuman.meshData, os.path.join(exportPath, filename))
                
                if self.exportSkeleton.selected:
                    mh2bvh.exportSkeleton(self.app.scene3d.selectedHuman.meshData, os.path.join(exportPath, filename + ".bvh"))
                    
                if len(filename)> 0 and self.app.scene3d.selectedHuman.hairObj and len(self.app.scene3d.selectedHuman.hairObj.verts) > 0:
                    if self.hairMesh.selected:
                        mh2obj.exportObj(self.app.scene3d.selectedHuman.hairObj, os.path.join(exportPath, "hair_" + filename+".obj"))
                    else:
                        hairsClass = self.app.scene3d.selectedHuman.hairs
                        #hairsClass = self.app.categories["Library"].tasksByName["Hair"]
                        #hair.adjustHair(self.app.scene3d.selectedHuman, hairsClass)
                        file = open(os.path.join(exportPath, "hair_" + filename + ".obj"), 'w')
                        mh2obj.exportAsCurves(file, hairsClass.guides)
                        file.close()
                  
            elif self.mhx.selected:
                mh2mhx.exportMhx(self.app.scene3d.selectedHuman.meshData, os.path.join(exportPath, filename + ".mhx"))
            elif self.collada.selected:
                mh2collada.exportCollada(self.app.scene3d.selectedHuman.meshData, os.path.join(exportPath, filename))
            elif self.md5.selected:
                mh2md5.exportMd5(self.app.scene3d.selectedHuman.meshData, os.path.join(exportPath, filename + ".md5mesh"))
            elif self.stl.selected:
                mh2stl.exportStlBinary(self.app.scene3d.selectedHuman.meshData, os.path.join(exportPath, filename + ".stl"))

            self.app.switchCategory('Modelling')
            self.app.scene3d.redraw(1)
            
    def updateGui(self):
        if self.wavefrontObj.selected:
            self.objOptions.show()
        else:
            self.objOptions.hide()
            
        if self.mhx.selected:
            self.mhxOptions.show()
        else:
            self.mhxOptions.hide()

    def onShow(self, event):

    # When the task gets shown, set the focus to the file entry

        gui3d.TaskView.onShow(self, event)
        self.fileentry.setFocus()
        self.pan = self.app.scene3d.selectedHuman.getPosition()
        self.eyeX = mh.cameras[0].eyeX
        self.eyeY = mh.cameras[0].eyeY
        self.eyeZ = mh.cameras[0].eyeZ
        self.focusX = mh.cameras[0].focusX
        self.focusY = mh.cameras[0].focusY
        self.focusZ = mh.cameras[0].focusZ
        self.rotation = self.app.scene3d.selectedHuman.getRotation()
        self.app.scene3d.selectedHuman.setPosition([0, -1, 0])
        self.app.setGlobalCamera();
        mh.cameras[0].eyeZ = 70
        self.app.scene3d.selectedHuman.setRotation([0.0, 0.0, 0.0])

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)
        self.app.scene3d.selectedHuman.setPosition(self.pan)
        mh.cameras[0].eyeX = self.eyeX
        mh.cameras[0].eyeY = self.eyeY
        mh.cameras[0].eyeZ = self.eyeZ
        mh.cameras[0].focusX = self.focusX
        mh.cameras[0].focusY = self.focusY
        mh.cameras[0].focusZ = self.focusZ
        self.app.scene3d.selectedHuman.setRotation(self.rotation)


class FilesCategory(gui3d.Category):

    def __init__(self, parent):
        gui3d.Category.__init__(self, parent, 'Files')

        SaveTaskView(self)
        LoadTaskView(self)
        ExportTaskView(self)


