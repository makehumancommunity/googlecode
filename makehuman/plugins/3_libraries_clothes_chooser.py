#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers, Jonas Hauquier, Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Clothes library.
"""

import proxychooser

import os
import gui3d
import mh
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


#
#   Clothes
#

class ClothesTaskView(proxychooser.ProxyChooserTaskView):

    def __init__(self, category):
        super(ClothesTaskView, self).__init__(category, 'clothes', multiProxy = True)

        self.taggedClothes = {}
        self.clothesList = []
        self.highlightedPiece = None

        self.cache = {}
        self.meshCache = {}

        # TODO self.filechooser.setFileLoadHandler(fc.MhcloFileLoader())

        self.addLeftWidget(self.filechooser.createTagFilter())

        self.originalHumanMask = gui3d.app.selectedHuman.meshData.getFaceMask().copy()
        self.faceHidingTggl = self.optionsBox.addWidget(gui.ToggleButton("Hide faces under clothes"))
        @self.faceHidingTggl.mhEvent
        def onClicked(event):
            self.updateFaceMasks(self.faceHidingTggl.selected)
        self.faceHidingTggl.setSelected(True)

    def createFileChooser(self):
        self.optionsBox = self.addLeftWidget(gui.GroupBox('Options'))
        super(ClothesTaskView, self).createFileChooser()

    def getObjectLayer(self):
        return 10

    def proxySelected(self, proxy, obj):
        # TODO check for and prevent double use of same UUID
        uuid = proxy.getUuid()

        '''
        # TODO
        try:
            clo = human.clothesObjs[uuid]
        except KeyError:
            clo = None
        if clo:
            gui3d.app.removeObject(clo)
            del human.clothesObjs[uuid]
            self.clothesList.remove(uuid)
            proxy = human.clothesProxies[uuid]
            del human.clothesProxies[uuid]
            self.updateFaceMasks(self.faceHidingTggl.selected)
            self.filechooser.deselectItem(proxy.file)
            log.message("Removed clothing %s %s", proxy.name, uuid)
            return
        '''


        # TODO handle UUIDs in proxychooser baseclass?
        self.human.clothesObjs[uuid] = obj
        self.human.clothesProxies[uuid] = proxy
        self.clothesList.append(uuid)


        # TODO Disabled until conflict with new filechooser is sorted out
        '''
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
                        log.message("Removed clothing %s with known tag %s", oldUuid, tag)
                    else:
                        log.message("Kept clothing %s with known tag %s", oldUuid, tag)
                        newUuids.append(oldUuid)
                newUuids.append(uuid)
                self.taggedClothes[tag] = newUuids
        '''

        self.orderRenderQueue()
        self.updateFaceMasks(self.faceHidingTggl.selected)

    def proxyDeselected(self, proxy, obj, suppressSignals = False):
        # TODO 
        if not suppressSignals:
            self.updateFaceMasks(self.faceHidingTggl.selected)

    def resetSelection(self):
        super(ClothesTaskView, self).resetSelection()
        self.updateFaceMasks(self.faceHidingTggl.selected)


    def orderRenderQueue(self):
        """
        Sort clothes on proxy.z_depth parameter, both in self.clothesList and
        in the render component.
        """
        human = gui3d.app.selectedHuman
        decoratedClothesList = [(human.clothesProxies[uuid].z_depth, uuid) for uuid in self.clothesList]
        decoratedClothesList.sort()
        self.clothesList = [uuid for (_, uuid) in decoratedClothesList]

        '''
        # Remove and re-add clothes in z_depth order to renderer
        for uuid in self.clothesList:
            try:
                gui3d.app.removeObject(human.clothesObjs[uuid])
            except:
                pass
        for uuid in self.clothesList:
            gui3d.app.addObject(human.clothesObjs[uuid])
        '''
        # Use priority for this instead:
        priority = 50
        for uuid in self.clothesList:
            human.clothesObjs[uuid].mesh.priority = priority
            priority += 1

    def updateFaceMasks(self, enableFaceHiding = True):
        """
        Apply facemask (deleteVerts) defined on clothes to body and lower layers
        of clothing. Uses order as defined in self.clothesList.
        """
        human = gui3d.app.selectedHuman
        if not enableFaceHiding:
            human.meshData.changeFaceMask(self.originalHumanMask)
            human.meshData.updateIndexBufferFaces()
            for uuid in self.clothesList:
                obj = human.clothesObjs[uuid]
                faceMask = np.ones(obj.mesh.getFaceCount(), dtype=bool)
                obj.mesh.changeFaceMask(faceMask)
                obj.mesh.updateIndexBufferFaces()
            return

        vertsMask = np.ones(human.meshData.getVertexCount(), dtype=bool)
        log.debug("masked verts %s", np.count_nonzero(~vertsMask))
        for uuid in reversed(self.clothesList):
            proxy = human.clothesProxies[uuid]
            obj = human.clothesObjs[uuid]

            # Convert basemesh vertex mask to local mask for proxy vertices
            proxyVertMask = np.ones(len(proxy.refVerts), dtype=bool)
            for idx,vs in enumerate(proxy.refVerts):
                # Body verts to which proxy vertex with idx is mapped
                (v1,v2,v3) = vs.getHumanVerts()
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
                vertsMask[verts] = False
            log.debug("masked verts %s", np.count_nonzero(~vertsMask))

        basemeshMask = human.meshData.getFaceMaskForVertices(np.argwhere(vertsMask)[...,0])
        human.meshData.changeFaceMask(np.logical_and(basemeshMask, self.originalHumanMask))
        human.meshData.updateIndexBufferFaces()
        log.debug("%s faces masked for basemesh", np.count_nonzero(~basemeshMask))


    def onShow(self, event):
        super(ClothesTaskView, self).onShow(event)
        if gui3d.app.settings.get('cameraAutoZoom', True):
            gui3d.app.setGlobalCamera()

    def loadHandler(self, human, values):
        # Do this manually because we don't reuse proxychooser.loadHandler()
        if self._proxyFileCache is None:
            self.loadProxyFileCache()

        if values[0] == 'clothesHideFaces':
            enabled = values[1].lower() in ['true', 'yes']
            self.faceHidingTggl.setChecked(enabled)
            self.updateFaceMasks(enabled)
            return

        if len(values) >= 3:
            mhclo = exportutils.config.getExistingProxyFile(values[1], values[2], "clothes")
        else:
            mhclo = exportutils.config.getExistingProxyFile(values[1], None, "clothes")
        if not mhclo:
            log.notice("%s does not exist. Skipping.", values[1])
        else:
            self.selectProxy(mhclo)

    def saveHandler(self, human, file):
        file.write('clothesHideFaces %s\n' % self.faceHidingTggl.selected)
        for name in self.clothesList:
            clo = human.clothesObjs[name]
            if clo:
                proxy = human.clothesProxies[name]
                file.write('clothes %s %s\n' % (os.path.basename(proxy.file), proxy.getUuid()))

    def registerLoadSaveHandlers(self):
        super(ClothesTaskView, self).registerLoadSaveHandlers()
        gui3d.app.addLoadHandler('clothesHideFaces', self.loadHandler)


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements

taskview = None

def load(app):
    global taskview

    category = app.getCategory('Geometries')
    taskview = ClothesTaskView(category)
    taskview.sortOrder = 0
    category.addTask(taskview)

    taskview.registerLoadSaveHandlers()

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    taskview.onUnload()

