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

import os
import gui3d
import mh
import download
import files3d
import mh2proxy
import exportutils
import gui
import filechooser as fc
import log
import numpy as np

KnownTags = [
    "shoes",
    "dress",
    "tshirt",
    "stockings",
    "trousers",
    "shirt",
    "underwearbottom",
    "underweartop",
    "hat"
]

class ClothesAction(gui3d.Action):
    def __init__(self, name, human, library, mhcloFile):
        super(ClothesAction, self).__init__(name)
        self.human = human
        self.library = library
        self.mhclo = mhcloFile

    def do(self):
        self.library.setClothes(self.human, self.mhclo)

    def undo(self):
        self.library.setClothes(self.human, self.mhclo)

#
#   Clothes
#

class ClothesTaskView(gui3d.TaskView):
    
    def __init__(self, category):

        self.systemClothes = os.path.join('data', 'clothes')
        self.userClothes = os.path.join(mh.getPath(''), 'data', 'clothes')

        self.taggedClothes = {}
        self.clothesList = []
        
        gui3d.TaskView.__init__(self, category, 'Clothes')
        if not os.path.exists(self.userClothes):
            os.makedirs(self.userClothes)
        self.filechooser = self.addTopWidget(fc.FileChooser([self.systemClothes, self.userClothes], 'mhclo', 'thumb', 'data/clothes/notfound.thumb'))
        self.addLeftWidget(self.filechooser.sortBox)
        self.update = self.filechooser.sortBox.addWidget(gui.Button('Check for updates'))
        self.mediaSync = None

        self.originalHumanMask = gui3d.app.selectedHuman.meshData.getFaceMask().copy()

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            gui3d.app.do(ClothesAction("Change clothing piece",
                gui3d.app.selectedHuman,
                self,
                filename))
            if gui3d.app.settings.get('jumpToModelling', True):
                mh.changeCategory('Modelling')

        @self.update.mhEvent
        def onClicked(event):
            self.syncMedia()

        
    def setClothes(self, human, filepath):
        if os.path.basename(filepath) == "clear.mhclo":
            for name,clo in human.clothesObjs.items():
                gui3d.app.removeObject(clo)
                del human.clothesObjs[name]
            human.clothesProxies = []
            self.clothesList = []
            human.activeClothing = None
            self.updateFaceMasks()
            return

        proxy = mh2proxy.readProxyFile(human.meshData, filepath, False)
        proxy.type = 'Clothes'
        
        if not proxy:
            return

        uuid = proxy.getUuid()
        
        # For loading costumes (sets of individual clothes)
        if proxy.clothings:
            t = 0
            dt = 1.0/len(proxy.clothings)
            for (pieceName, uuid) in proxy.clothings:
                gui3d.app.progress(t, text="Loading %s" % pieceName)
                t += dt
                mhclo = exportutils.config.getExistingProxyFile(pieceName+".mhclo", uuid, "clothes")
                if mhclo:
                    self.setClothes(human, mhclo)
                else:
                    log.warning("Could not load clothing %s", pieceName)
            gui3d.app.progress(1, text="%s loaded" % proxy.name)
            # Load custom textures
            for (uuid, texPath) in proxy.textures:
                if not uuid in human.clothesObjs.keys():
                    log.warning("Cannot override texture for clothing piece with uuid %s!" % uuid)
                    continue
                pieceProxy = human.clothesProxies[uuid]
                if not os.path.dirname(texPath):
                    pieceProxy = human.clothesProxies[uuid]
                    clothesPath = os.path.dirname(pieceProxy.file)
                    texPath = os.path.join(clothesPath, texPath)
                log.debug("Overriding texture for clothpiece %s to %s", uuid, texPath)
                clo = human.clothesObjs[uuid]
                clo.mesh.setTexture(texPath)
            # Apply overridden transparency setting to pieces of a costume
            for (uuid, isTransparent) in proxy.transparencies.items():
                if not uuid in human.clothesProxies.keys():
                    log.warning("Could not override transparency for object with uuid %s!" % uuid)
                    continue
                clo = human.clothesObjs[uuid]
                log.debug("Overriding transparency setting for clothpiece %s to %s", uuid, bool(proxy.transparencies[uuid]))
                if proxy.transparencies[uuid]:
                    clo.mesh.setTransparentPrimitives(len(clo.mesh.faces))
                else:
                    clo.mesh.setTransparentPrimitives(0)
            return
            
        #folder = os.path.dirname(filepath)
        (folder, name) = proxy.obj_file
        obj = os.path.join(folder, name)

        try:
            clo = human.clothesObjs[uuid]
        except:
            clo = None
        if clo:
            gui3d.app.removeObject(clo)
            del human.clothesObjs[uuid]
            self.clothesList.remove(uuid)
            if human.activeClothing == uuid:
                human.activeClothing = None
            proxy = human.clothesProxies[uuid]
            del human.clothesProxies[uuid]
            self.updateFaceMasks()
            log.message("Removed clothing %s %s", proxy.name, uuid)
            return

        mesh = files3d.loadMesh(obj)
        if not mesh:
            log.error("Could not load mesh for clothing object %s", proxy.name)
            return
        if proxy.texture:
            (dir, name) = proxy.texture
            tex = os.path.join(folder, name)
            if not os.path.exists(tex):
                tex = os.path.join(self.systemClothes, "textures", name)
            mesh.setTexture(tex)
        else:
            pass
        
        clo = gui3d.app.addObject(gui3d.Object(human.getPosition(), mesh))
        clo.setRotation(human.getRotation())
        clo.mesh.setCameraProjection(0)
        clo.mesh.setSolid(human.mesh.solid)
        if proxy.cull:
            clo.mesh.setCull(1)
        else:
            clo.mesh.setCull(None)
        if proxy.transparent:
            clo.mesh.setTransparentPrimitives(len(clo.mesh.faces))
        else:
            clo.mesh.setTransparentPrimitives(0)
        clo.mesh.priority = 10
        human.clothesObjs[uuid] = clo        
        human.clothesProxies[uuid] = proxy
        human.activeClothing = uuid
        self.clothesList.append(uuid)
        
        for tag in proxy.tags:
            tag = tag.lower()
            # Allow only one piece of clothing per known tag
            if tag in KnownTags:
                try:
                    oldUuids = self.taggedClothes[tag]
                except KeyError:
                    oldUuids = []
                newUuids = []
                for oldUuid in oldUuids:
                    if oldUuid == uuid:
                        pass
                    elif True:  # TODO use parameter here
                        try:
                            oldClo = human.clothesObjs[oldUuid]
                        except KeyError:
                            continue
                        gui3d.app.removeObject(oldClo)
                        del human.clothesObjs[oldUuid]
                        self.clothesList.remove(oldUuid)
                        if human.activeClothing == oldUuid:
                            human.activeClothing = None
                        log.message("Removed clothing %s with known tag %s", oldUuid, tag)
                    else:
                        log.message("Kept clothing %s with known tag %s", oldUuid, tag)
                        newUuids.append(oldUuid)
                newUuids.append(uuid)
                self.taggedClothes[tag] = newUuids

        self.adaptClothesToHuman(human)
        clo.setSubdivided(human.isSubdivided())
        
        #self.clothesButton.setTexture(obj.replace('.obj', '.png'))
        self.updateFaceMasks()

    def updateFaceMasks(self):
        """
        Apply facemask (deleteVerts) defined on clothes to body and lower layers
        of clothing.
        """
        human = gui3d.app.selectedHuman
        vertsMask = np.ones(human.meshData.getVertexCount(), dtype=bool)
        log.debug("masked verts %s", np.count_nonzero(~vertsMask))
        for uuid in reversed(self.clothesList):
            proxy = human.clothesProxies[uuid]
            obj = human.clothesObjs[uuid]

            # Convert basemesh vertex mask to local mask for proxy vertices
            proxyVertMask = np.ones(len(proxy.refVerts), dtype=bool)
            for idx,vs in enumerate(proxy.refVerts):
                # Body verts to which proxy vertex with idx is mapped
                (v1,v2,v3) = vs[:3]
                # Hide proxy vert if any of its referenced body verts are hidden (most agressive)
                #proxyVertMask[idx] = vertsMask[v1] and vertsMask[v2] and vertsMask[v3]
                # Alternative1: only hide if at least two referenced body verts are hidden (best result)
                proxyVertMask[idx] = np.count_nonzero(vertsMask[[v1, v2, v3]]) > 1
                # Alternative2: Only hide proxy vert if all of its referenced body verts are hidden (least agressive)
                #proxyVertMask[idx] = vertsMask[v1] or vertsMask[v2] or vertsMask[v3]
                
            proxyKeepVerts = np.argwhere(proxyVertMask)[...,0]
            proxyFaceMask = obj.mesh.getFaceMaskForVertices(proxyKeepVerts)

            # Apply accumulated mask from previous clothes layers on this clothing piece
            obj.mesh.changeFaceMask(proxyFaceMask)
            obj.mesh.updateIndexBufferFaces()
            log.debug("%s faces masked for %s", np.count_nonzero(~proxyFaceMask), proxy.name)

            if proxy.deleteVerts != None and len(proxy.deleteVerts > 0):
                log.debug("Loaded %s deleted verts (%s faces) from %s", np.count_nonzero(proxy.deleteVerts), len(human.meshData.getFacesForVertices(np.argwhere(proxy.deleteVerts)[...,0])),proxy.name)

                # Modify accumulated (basemesh) verts mask
                verts = np.argwhere(proxy.deleteVerts)[...,0]
                print "hidden verts: %s" % verts
                vertsMask[verts] = False
            log.debug("masked verts %s", np.count_nonzero(~vertsMask))

        basemeshMask = human.meshData.getFaceMaskForVertices(np.argwhere(vertsMask)[...,0])
        human.meshData.changeFaceMask(np.logical_and(basemeshMask, self.originalHumanMask))
        human.meshData.updateIndexBufferFaces()
        log.debug("%s faces masked for basemesh", np.count_nonzero(~basemeshMask))

    def adaptClothesToHuman(self, human):

        for (uuid,clo) in human.clothesObjs.items():            
            if clo:
                mesh = clo.getSeedMesh()
                human.clothesProxies[uuid].update(mesh, human.meshData)
                mesh.update()
                if clo.isSubdivided():
                    clo.getSubdivisionMesh()

    def onShow(self, event):
        # When the task gets shown, set the focus to the file chooser
        gui3d.app.selectedHuman.hide()
        gui3d.TaskView.onShow(self, event)
        self.filechooser.setFocus()
        
        #if not os.path.isdir(self.userClothes) or not len([filename for filename in os.listdir(self.userClothes) if filename.lower().endswith('mhclo')]):    
        #    gui3d.app.prompt('No user clothes found', 'You don\'t seem to have any user clothes, download them from the makehuman media repository?\nNote: this can take some time depending on your connection speed.', 'Yes', 'No', self.syncMedia)

    def onHide(self, event):
        gui3d.app.selectedHuman.show()
        gui3d.TaskView.onHide(self, event)
        
    def onHumanChanging(self, event):
        
        human = event.human
        if event.change == 'reset':
            log.message("deleting clothes")
            for (uuid,clo) in human.clothesObjs.items():
                if clo:
                    gui3d.app.removeObject(clo)
                del human.clothesObjs[uuid]
                del human.clothesProxies[uuid]
            self.clothesList = []
            human.activeClothing = None
            self.updateFaceMasks()
            # self.clothesButton.setTexture('data/clothes/clear.png')

    def onHumanChanged(self, event):
        
        human = event.human
        self.adaptClothesToHuman(human)

    def loadHandler(self, human, values):

        if len(values) >= 3:
            mhclo = exportutils.config.getExistingProxyFile(values[1], values[2], "clothes")
        else:
            mhclo = exportutils.config.getExistingProxyFile(values[1], None, "clothes")
        if not mhclo:
            log.notice("%s does not exist. Skipping.", values[1])
        else:            
            self.setClothes(human, mhclo)
        
    def saveHandler(self, human, file):
        
        for name in self.clothesList:
            clo = human.clothesObjs[name]
            if clo:
                proxy = human.clothesProxies[name]
                file.write('clothes %s %s\n' % (os.path.basename(proxy.file), proxy.getUuid()))
                
    def syncMedia(self):
        
        if self.mediaSync:
            return
        if not os.path.isdir(self.userClothes):
            os.makedirs(self.userClothes)
        self.mediaSync = download.MediaSync(gui3d.app, self.userClothes, 'http://download.tuxfamily.org/makehuman/clothes/', self.syncMediaFinished)
        self.mediaSync.start()
        
    def syncMediaFinished(self):
        
        self.mediaSync = None


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Library')
    taskview = category.addTask(ClothesTaskView(category))

    app.addLoadHandler('clothes', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass

