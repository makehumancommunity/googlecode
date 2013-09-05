#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson, Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import os
import gui3d
import mh
import files3d
import mh2proxy
import gui
import filechooser as fc
import log

class GenitalsAction(gui3d.Action):
    def __init__(self, name, human, library, before, after):
        super(GenitalsAction, self).__init__(name)
        self.human = human
        self.library = library
        self.before = before
        self.after = after

    def do(self):
        self.library.setGenitals(self.human, self.after)
        return True

    def undo(self):
        self.library.setGenitals(self.human, self.before)
        return True


class GenitalsTaskView(gui3d.TaskView):

    def __init__(self, category):

        gui3d.TaskView.__init__(self, category, 'Genitals')
        genitalsDir = os.path.join(mh.getPath(''), 'data', 'genitals')
        if not os.path.exists(genitalsDir):
            os.makedirs(genitalsDir)
        self.paths = [genitalsDir , mh.getSysDataPath('genitals')]
        #self.filechooser = self.addTopWidget(fc.FileChooser(self.paths, 'mhclo', 'thumb', mh.getSysDataPath('genitals/notfound.thumb')))
        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.paths, 'mhclo', 'thumb', mh.getSysDataPath('clothes/notfound.thumb'), 'Genitals'))
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(False)
        self.addLeftWidget(self.filechooser.createSortBox())

        self.oHeadCentroid = [0.0, 7.436, 0.03 + 0.577]
        self.oHeadBBox = [[-0.84,6.409,-0.9862],[0.84,8.463,1.046]]

        self.human = gui3d.app.selectedHuman

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            if self.human.genitalsProxy:
                oldFile = self.human.genitalsProxy.file
            else:
                oldFile = 'clear.mhclo'
            gui3d.app.do(GenitalsAction("Change genitals",
                self.human,
                self,
                oldFile,
                filename))

    def setGenitals(self, human, mhclo):
        self.filechooser.selectItem(mhclo)

        if human.genitalsObj:
            gui3d.app.removeObject(human.genitalsObj)
            human.genitalsObj = None
            human.genitalsProxy = None

        if os.path.basename(mhclo) == "clear.mhclo":
            return

        human.genitalsProxy = mh2proxy.readProxyFile(human.meshData, mhclo, type="Genitals", layer=3)
        if not human.genitalsProxy:
            log.error("Failed to load %s", mhclo)
            return

        obj = human.genitalsProxy.obj_file
        #obj = os.path.join(obj[0], obj[1])
        mesh = files3d.loadMesh(obj)
        if not mesh:
            log.error("Failed to load %s", obj)
            return

        mesh.material = human.genitalsProxy.material

        human.genitalsObj = gui3d.app.addObject(gui3d.Object(human.getPosition(), mesh))
        human.genitalsObj.setRotation(human.getRotation())
        human.genitalsObj.mesh.setCameraProjection(0)
        human.genitalsObj.mesh.setSolid(human.mesh.solid)
        if human.genitalsProxy.cull:
            human.genitalsObj.mesh.setCull(1)
        else:
            human.genitalsObj.mesh.setCull(None)
        # Enabling this causes render-que order issues so that genitals render over hair
        # Disabling it renders hi-poly genitals wrong
        if human.genitalsProxy.transparent:
            human.genitalsObj.mesh.setTransparentPrimitives(len(human.genitalsObj.mesh.fvert))
        else:
            human.genitalsObj.mesh.setTransparentPrimitives(0)
        human.genitalsObj.mesh.priority = 5

        genitalsName = human.genitalsObj.mesh.name.split('.')[0]

        self.adaptGenitalsToHuman(human)
        human.genitalsObj.setSubdivided(human.isSubdivided())

    def adaptGenitalsToHuman(self, human):

        if human.genitalsObj and human.genitalsProxy:

            mesh = human.genitalsObj.getSeedMesh()
            human.genitalsProxy.update(mesh)
            mesh.update()
            if human.genitalsObj.isSubdivided():
                human.genitalsObj.getSubdivisionMesh()

    def onShow(self, event):
        # When the task gets shown, set the focus to the file chooser
        gui3d.TaskView.onShow(self, event)
        self.filechooser.refresh()
        if self.human.genitalsProxy and self.human.genitalsProxy.file:
            self.filechooser.setHighlightedItem(self.human.genitalsProxy.file)
        self.filechooser.setFocus()
        if gui3d.app.settings.get('cameraAutoZoom', True):
            gui3d.app.setGlobalCamera()

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

    def onHumanChanging(self, event):

        human = event.human
        if event.change == 'reset':
            log.message("resetting genitals")
            if human.genitalsObj:
                gui3d.app.removeObject(human.genitalsObj)
                human.genitalsObj = None
                human.genitalsProxy = None
            self.setGenitals(human, mh.getSysDataPath("genitals/high-poly/high-poly.mhclo"))
            self.filechooser.deselectAll()
        else:
            if gui3d.app.settings.get('realtimeUpdates', False):
                self.adaptGenitalsToHuman(human)

    def onHumanChanged(self, event):

        human = event.human
        self.adaptGenitalsToHuman(human)

    def loadHandler(self, human, values):

        mhclo = values[1]
        if not os.path.exists(os.path.realpath(mhclo)):
            log.notice('GenitalsTaskView.loadHandler: %s does not exist. Skipping.', mhclo)
            return
        self.setGenitals(human, mhclo)

    def saveHandler(self, human, file):

        if human.genitalsProxy:
            file.write('genitals %s\n' % human.genitalsProxy.file)

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Geometries')
    taskview = GenitalsTaskView(category)
    taskview.sortOrder = 1
    category.addTask(taskview)

    app.addLoadHandler('genitals', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)

    # Load initial genitals
    taskview.setGenitals(gui3d.app.selectedHuman, mh.getSysDataPath("genitals/low-poly/low-poly.mhclo"))

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass

