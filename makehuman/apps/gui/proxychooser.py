#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Common base class for all proxy chooser libraries.
"""

import os
import gui3d
import events3d
import mh
import files3d
import mh2proxy
import filechooser as fc
import log
import getpath
import pickle


class ProxyAction(gui3d.Action):
    def __init__(self, name, library, before, after):
        super(ProxyAction, self).__init__(name)
        self.library = library
        self.before = before
        self.after = after

    def do(self):
        self.library.selectProxy(self.after)
        return True

    def undo(self):
        self.library.selectProxy(self.before)
        return True


class MultiProxyAction(gui3d.Action):
    def __init__(self, name, library, mhcloFile, add):
        super(MultiProxyAction, self).__init__(name)
        self.library = library
        self.mhclo = mhcloFile
        self.add = add

    def do(self):
        if self.add:
            self.library.selectProxy(self.mhclo)
        else:
            self.library.deselectProxy(self.mhclo)
        return True

    def undo(self):
        if self.add:
            self.library.deselectProxy(self.mhclo)
        else:
            self.library.selectProxy(self.mhclo)
        return True


class ProxyChooserTaskView(gui3d.TaskView):
    """
    Common base class for all proxy chooser libraries.
    """

    def __init__(self, category, proxyName, tabLabel = None, multiProxy = False):
        if not tabLabel:
            tabLabel = proxyName.capitalize()
        proxyName = proxyName.lower().replace(" ", "_")
        gui3d.TaskView.__init__(self, category, tabLabel)

        self.proxyName = proxyName
        self.label = tabLabel
        self.multiProxy = multiProxy

        self.homeProxyDir = getpath.getPath(os.path.join('data', proxyName))
        self.sysProxyDir = mh.getSysDataPath(proxyName)

        if not os.path.exists(self.homeProxyDir):
            os.makedirs(self.homeProxyDir)

        self.paths = [self.homeProxyDir , self.sysProxyDir]

        self.human = gui3d.app.selectedHuman

        self._proxyCache = dict()
        self._proxyFileCache = None
        self._proxyFilePerUuid = None

        self.selectedProxies = []
        self.proxyObjects = []

        self.createFileChooser()


    def createFileChooser(self):
        """
        Overwrite to do custom initialization of filechooser widget.
        """
        #self.filechooser = self.addTopWidget(fc.FileChooser(self.paths, 'mhclo', 'thumb', mh.getSysDataPath(proxyName+'/notfound.thumb')))
        notfoundIcon = self.getNotFoundIcon()
        if not os.path.isfile(notfoundIcon):
            notfoundIcon = getpath.getSysDataPath('notfound.thumb')

        if self.multiProxy:
            clearIcon = None
        else:
            clearIcon = self.getClearIcon()
            if not os.path.isfile(clearIcon):
                clearIcon = getpath.getSysDataPath('clear.thumb')
        self.filechooser = fc.IconListFileChooser(self.paths, self.getFileExtension(), 'thumb', notfoundIcon, clearIcon, name=self.label, multiSelect=self.multiProxy)
        self.addRightWidget(self.filechooser)
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(False)
        self.addLeftWidget(self.filechooser.createSortBox())

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            self.proxyFileSelected(filename)

        if self.multiProxy:
            @self.filechooser.mhEvent
            def onFileDeselected(filename):
                self.proxyFileDeselected(filename)

            @self.filechooser.mhEvent
            def onDeselectAll(value):
                self.deselectAllProxies()

    def getSaveName(self):
        """
        The name used by save and load handlers to store the proxy mesh.
        """
        return self.proxyName

    def getFileExtension(self):
        """
        The file extension for proxy files of this type.
        """
        return 'mhclo'

    def getNotFoundIcon(self):
        """
        The default icon to show when no icon is found for a proxy in this
        library.
        If this icon does not exist either, it will show the default icon in
        data/notfound.thumb
        """
        return os.path.join(self.sysProxyDir, 'notfound.thumb')

    def getClearIcon(self):
        """
        The icon to show for the "select None" entry in the filechooser of this
        library. Only applies when this is not a multiselect library (not self.multiProxy).
        If this icon does not exist, it will show the default icon in
        data/clear.thumb
        """
        return os.path.join(self.sysProxyDir, 'clear.thumb')

    def proxyFileSelected(self, filename):
        """
        Called when user selects a file from the filechooser widget.
        Creates an action that invokes selectProxy().
        """
        if self.multiProxy:
            action = MultiProxyAction("Change %s" % self.proxyName,
                                      self,
                                      filename,
                                      True)
        else:
            if self.isProxySelected():
                oldFile = self.getSelection()[0].file
            else:
                oldFile = None
            action = ProxyAction("Change %s" % self.proxyName,
                                 self,
                                 oldFile,
                                 filename)
        gui3d.app.do(action)

    def proxyFileDeselected(self, filename):
        """
        Called when user deselects a file from the filechooser widget.
        Creates an action that invokes deselectProxy().
        This method only has effect when this library allows multiple proxy
        selection.
        """
        if not self.multiProxy:
            return

        action = MultiProxyAction("Change %s" % self.proxyName,
                                  self,
                                  filename,
                                  False)
        gui3d.app.do(action)

    def getObjectLayer(self):
        """
        Returns the rendering depth order with which objects of this proxy type
        should be rendered.
        Will be used as mesh rendering priority.
        """
        # TODO remove, this is bogus
        raise NotImplementedError("Implement ProxyChooserTaskView.getObjectLayer()!")

    def proxySelected(self, proxy, obj):
        """
        Do custom work specific to this library when a proxy object was loaded.
        """
        raise NotImplementedError("Implement ProxyChooserTaskView.proxySelected()!")

    def proxyDeselected(self, proxy, obj):
        """
        Do custom work specific to this library when a proxy object was unloaded.
        """
        raise NotImplementedError("Implement ProxyChooserTaskView.proxyDeselected()!")

    def selectProxy(self, mhclofile):
        """
        Called when a new proxy has been selected.
        If this library selects only a single proxy, specifying None as 
        mhclofile parameter will deselect the current proxy and set the selection
        to "none".
        If this library allows selecting multiple proxies, specifying None as
        mhclofile will have no effect.
        """
        if not mhclofile:
            if self.multiProxy:
                return
            else:
                self.deselectProxy(None)
                return

        if not self.multiProxy and self.isProxySelected():
            # Deselect previously selected proxy
            self.deselectProxy(None, suppressSignal = True)

        human = self.human

        self.filechooser.selectItem(mhclofile)

        if mhclofile not in self._proxyCache:
            proxy = mh2proxy.readProxyFile(human.meshData, 
                                           mhclofile, 
                                           type=self.proxyName.capitalize(), 
                                           layer=self.getObjectLayer() )    # TODO remove this layer arg, is bogus
            self._proxyCache[mhclofile] = proxy
        else:
            proxy = self._proxyCache[mhclofile]

        mesh = files3d.loadMesh(proxy.obj_file)
        if not mesh:
            log.error("Failed to load %s", proxy.obj_file)
            return

        if self.multiProxy and proxy.uuid in [p.uuid for p in self.getSelection()]:
            log.warning("Proxy with UUID %s (%s) already loaded in %s library. Skipping.", proxy.uuid, proxy.file, self.proxyName)
            return

        mesh.material = proxy.material
        mesh.priority = proxy.z_depth           # Set render order
        mesh.setCameraProjection(0)             # Set to model camera
        mesh.setSolid(human.mesh.solid)    # Set to wireframe if human is in wireframe

        obj = gui3d.Object(mesh, self.human.getPosition())
        obj.setRotation(human.getRotation())
        gui3d.app.addObject(obj)

        self.adaptProxyToHuman(proxy, obj)
        obj.setSubdivided(human.isSubdivided()) # Copy subdivided state of human

        # Add to selection
        self.selectedProxies.append(proxy)
        self.proxyObjects.append(obj)

        self.filechooser.selectItem(mhclofile)

        self.proxySelected(proxy, obj)

        self.signalChange()

    def deselectProxy(self, mhclofile, suppressSignal = False):
        """
        Deselect specified proxy from library selections. If this library only
        supports selecting a single proxy, the mhclofile parameter is ignored,
        and it will just deselected the currently selected proxy.
        """
        if self.multiProxy:
            idx = self._getProxyIndex(mhclofile)
            if idx == None:
                return
        else:
            if self.isProxySelected():
                idx = 0
            else:
                return

        obj = self.proxyObjects[idx]
        proxy = self.selectedProxies[idx]
        gui3d.app.removeObject(obj)
        del self.proxyObjects[idx]
        del self.selectedProxies[idx]
        self.filechooser.deselectItem(mhclofile)

        self.proxyDeselected(proxy, obj)

        if not self.multiProxy:
            # Select None item in file list
            self.filechooser.selectItem(None)

        if not suppressSignal:
            self.signalChange()

    def deselectAllProxies(self):
        selectionsCopy = list(self.getSelection())
        for p in selectionsCopy:
            self.deselectProxy(p.file, suppressSignal = True)
        self.signalChange()

    def isProxySelected(self):
        return len(self.getSelection()) > 0

    def getSelection(self):
        """
        Return the selected proxies as a list.
        If no proxy is selected, returns empty list.
        If this is library allows selecting multiple proxies, the list can 
        contain multiple entries, if this is library allows selecting only a
        single proxy, the list is either of length 0 or 1.
        """
        return self.selectedProxies

    def getObjects(self):
        """
        Returns a list of objects beloning to the proxies returned by getSelection()
        The order corresponds with that of getSelection().
        """
        return self.proxyObjects

    def _getProxyIndex(self, mhcloFile):
        """
        Get the index of specified mhclopath within the list returned by getSelection()
        Returns None if the proxy of specified path is not in selection.
        """
        for pIdx, p in enumerate(self.getSelection()):
            if getpath.canonicalPath(p.file) == getpath.canonicalPath(mhcloFile):
                return pIdx
        return None

    def resetSelection(self):
        """
        Undo selection of all proxies.
        """
        if not self.isProxySelected():
            return

        #self.filechooser.deselectAll()
        self.deselectAllProxies()

    def adaptProxyToHuman(self, proxy, obj):
        mesh = obj.getSeedMesh()
        proxy.update(mesh)
        mesh.update()
        # Update subdivided mesh if smoothing is enabled
        if obj.isSubdivided():
            obj.getSubdivisionMesh()

    def signalChange(self):
        human = self.human
        event = events3d.HumanEvent(human, 'proxy')
        event.proxy = self.proxyName
        human.callEvent('onChanged', event)

    def onShow(self, event):
        if self._proxyFileCache is None:
            self.loadProxyFileCache()

        # When the task gets shown, set the focus to the file chooser
        gui3d.TaskView.onShow(self, event)
        self.filechooser.refresh()
        selectedProxies = self.getSelection()
        if len(selectedProxies) > 1:
            self.filechooser.setSelections( [p.file for p in selectedProxies] )
        elif len(selectedProxies) > 0:
            self.filechooser.selectItem(selectedProxies[0].file)
        elif not self.multiProxy:
            # Select "None" item in list
            self.filechooser.selectItem(None)
        self.filechooser.setFocus()

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

    def onHumanChanged(self, event):
        if event.change == 'reset':
            self.resetSelection()
        self.adaptAllProxies()

    def onHumanChanging(self, event):
        if gui3d.app.settings.get('realtimeFitting', False):
            # TODO else hide proxies?
            self.adaptAllProxies()

    def adaptAllProxies(self):
        for pIdx, proxy in enumerate(self.getSelection()):
            obj = self.getObjects()[pIdx]
            self.adaptProxyToHuman(proxy, obj)            

    def loadHandler(self, human, values):
        if self._proxyFileCache is None:
            self.loadProxyFileCache()

        mhclo = values[1]
        if not os.path.exists(mhclo):
            log.notice('Proxy %s (%s) does not exist. Skipping.', mhclo, self.proxyName)
            return
        self.selectProxy(mhclo)

    def saveHandler(self, human, file):
        for p in self.getSelection():
            file.write('%s %s\n' % (self.getSaveName(), p.file))

    def onUnload(self):
        """
        Called when this library taskview is being unloaded (usually when MH
        is exited).
        Note: make sure you connect the plugin's unload() method to this one!
        """
        self.storeProxyFileCache()

    def storeProxyFileCache(self):
        """
        Save MH cache file for the proxy files managed by this library.
        """
        if self._proxyFileCache == None or len(self._proxyFileCache) == 0:
            return
        saveDir = getpath.getPath('cache')
        if not os.path.isdir(saveDir):
            os.makedirs(saveDir)
        pickle.dump(self._proxyFileCache, open( os.path.join(saveDir, self.proxyName + '_filecache.mhc'), "wb"))

    def loadProxyFileCache(self, restoreFromFile = True):
        """
        Initialize or update the proxy file cache for this proxy library.
        Will attempt to load a previous cache from file if restoreFromFile is true.
        """
        if restoreFromFile:
            cacheFile = getpath.getPath(os.path.join('cache', self.proxyName + '_filecache.mhc'))
            if os.path.isfile(cacheFile):
                self._proxyFileCache = pickle.load( open(cacheFile, "rb") )
        self._proxyFileCache = mh2proxy.updateProxyFileCache(self.paths, self.getFileExtension(), self._proxyFileCache)

    def updateProxyFileCache(self):
        """
        Update proxy file cache to add newly added proxy files.
        """
        self.loadProxyFileCache(restoreFromFile = False)

    def findProxyByUuid(self, uuid):
        if self._proxyFileCache is None:
            self.loadProxyFileCache()

        if self._proxyFilePerUuid is None:
            self._proxyFilePerUuid = dict([ (values[1], path) for (path, values) in self._proxyFileCache.items() ])

        if uuid not in self._proxyFilePerUuid:
            log.warning('Could not find a proxy with UUID %s. Does not exist in %s library.', uuid, self.proxyName)
            return None
        return self._proxyFilePerUuid[uuid]

    def getTags(self, uuid = None, filename = None):
        """
        Get tags associated with proxies.
        When no uuid and filename are specified, returns the all the tags found
        in this collection (all proxy files managed by this library).
        Specify a filename or uuid to get all tags belonging to that proxy file.
        Always returns a set of tags (so contains no duplicates), unless no proxy
        was found upon which None is returned.
        An empty library (no proxies) or a library where no proxy file contains
        tags will always return an empty set.
        """
        if self._proxyFileCache is None:
            self.loadProxyFileCache()

        result = set()

        if uuid and filename:
            raise RuntimeWarning("getTags: Specify either uuid or filename, not both!")

        if uuid:
            proxyFile = self.findProxyByUuid(uuid)
            if not proxyFile:
                log.warning('Could not get tags for proxy with UUID %s. Does not exist in %s library.', uuid, self.proxyName)
                return result
        elif filename:
            proxyId = getpath.canonicalPath(filename)
            if proxyId not in self._proxyFileCache:
                log.warning('Could not get tags for proxy with filename %s. Does not exist in %s library.', filename, self.proxyName)
        else:
            for (path, values) in self._proxyFileCache.items():
                _, uuid, tags = values
                result.union(tags)
        return result

    def registerLoadSaveHandlers(self):
        gui3d.app.addLoadHandler(self.getSaveName(), self.loadHandler)
        gui3d.app.addSaveHandler(self.saveHandler)

