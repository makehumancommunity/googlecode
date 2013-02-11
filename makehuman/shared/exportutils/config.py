#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import os
import mh
import shutil
import log

#
#   class Config
#

class Config:

    def __init__(self):
        self.useTexFolder       = False
        self.relPaths           = True
        self.eyebrows           = True
        self.lashes             = True
        self.helpers            = False
        self.hidden             = True
        self.scale,self.unit    = 1.0, "decimeter"
        self.subdivide          = False

        self.exporting          = True
        self.feetOnGround       = False
        self.skirtRig           = None
        self.rigtype            = None
        self.cage               = False
        self.texFolder          = None
        self.proxyList          = []


    def selectedOptions(self, exporter):
        self.useTexFolder       = exporter.useTexFolder.selected
        self.relPaths           = exporter.useRelPaths.selected
        self.eyebrows           = exporter.eyebrows.selected
        self.lashes             = exporter.lashes.selected
        self.helpers            = exporter.helpers.selected
        self.hidden             = exporter.hidden.selected
        self.scale,self.unit    = exporter.getScale(exporter.scales)
        self.subdivide          = exporter.smooth.selected
        
        return self
    
    
    def addObjects(self, human):
    
        if human.hairProxy:
            words = human.hairObj.mesh.name.split('.')
            pfile = CProxyFile()
            pfile.set('Hair', 2)
            name = self.goodName(words[0])
            pfile.file = human.hairProxy.file
            self.proxyList.append(pfile)
    
        for (key,clo) in human.clothesObjs.items():
            if clo:
                name = self.goodName(key)
                pfile = CProxyFile()
                pfile.set('Clothes', 3)            
                proxy = human.clothesProxies[key]
                pfile.file = proxy.file
                self.proxyList.append(pfile)
                
        if human.proxy:
            name = self.goodName(human.proxy.name)
            pfile = CProxyFile()
            pfile.set('Proxy', 4)
            pfile.file = human.proxy.file
            self.proxyList.append(pfile)    
    
        if self.cage:
            pfile = CProxyFile()
            pfile.set('Cage', 4)
            pfile.file = os.path.realpath("./data/cages/cage/cage.mhclo")
            self.proxyList.append(pfile)  
            
        print(self.proxyList)
        return self


    def setupTexFolder(self, filepath):
        (fname, ext) = os.path.splitext(filepath)
        fname = self.goodName(os.path.basename(fname))
        self.outFolder = os.path.realpath(os.path.dirname(filepath))
        self.filename = os.path.basename(filepath)
        if self.useTexFolder:
            self.texFolder = self.getSubFolder(self.outFolder, "textures")
            self.copiedFiles = {}
    
    
    def getSubFolder(self, path, name):
        folder = os.path.join(path, name)
        print "Using folder", folder
        if not os.path.exists(folder):
            log.message("Creating folder %s", folder)
            try:
                os.mkdir(folder)
            except:
                log.error("Unable to create separate folder:", exc_info=True)
                return None
        return folder        
        
        
    def getTexturePath(self, filePath, fromDir, isTexture, human):
        srcDir = os.path.realpath(os.path.expanduser(fromDir))
        filename = os.path.basename(filePath)

        if human and (filename == "texture.png"):
            fromPath = human.getTexture()
            fileDir = os.path.dirname(fromPath)         
            filename = os.path.basename(fromPath)
            #print(filePath, fromDir, fileDir, fromPath)
            if fileDir == fromDir:
                fromPath = os.path.join(srcDir, filename)
        else:
            fromPath = os.path.join(srcDir, filename)

        if self.useTexFolder:
            if isTexture:
                toPath = os.path.join(self.texFolder, filename)
            else:
                toPath = os.path.join(self.outFolder, filename)
            try:
                self.copiedFiles[fromPath]
                done = True
            except:
                done = False
            if not done:
                if 0 and human:
                    img = mh.Image(human.getTexture())
                    log.debug("%s", dir(img))
                    img.save(toPath)
                    halt
                try:
                    shutil.copyfile(fromPath, toPath)
                except:
                    pass    
                self.copiedFiles[fromPath] = True
            texPath = toPath
        else:
            texPath = os.path.abspath(fromPath)
            
        if not self.relPaths:
            return texPath
        else:
            return str(os.path.normpath(os.path.relpath(texPath, self.outFolder)))
            
            
    def goodName(self, name):
        return name.replace(" ", "_").replace("-","_").lower()

#
#   class CProxyFile:
#

class CProxyFile:
    def __init__(self):
        self.type = 'Clothes'
        self.layer = 0
        self.file = ""
        
    def set(self, type, layer):
        self.type = type
        self.layer = layer
        
    def __repr__(self):
        return ("<CProxyFile %s %d \"%s\">" % (self.type, self.layer, self.file))
        
#
#
#
        
def getExistingProxyFile(path, uuid, category):
    if not uuid:
        if not os.path.exists(os.path.realpath(path)):
            return None
        log.message("Found %s", path)
        return path
    else:
        file = os.path.basename(path)
        paths = []
        folder = os.path.join(mh.getPath(''), 'data', category)
        addProxyFiles(file, folder, paths, 6)
        folder = os.path.join('data', category)
        addProxyFiles(file, folder, paths, 6)
        for path in paths:        
            uuid1 = scanFileForUuid(path)
            if uuid1 == uuid:
                log.message("Found %s %s", path, uuid)
                return path
        return None                


def addProxyFiles(file, folder, paths, depth):
    if depth < 0:
        return None
    try:
        files = os.listdir(folder)        
    except OSError:
        return None
    for pname in files:
        path = os.path.join(folder, pname)
        if pname == file:
            paths.append(path)
        elif os.path.isdir(path):
            addProxyFiles(file, path, paths, depth-1)
    return            


def scanFileForUuid(path):           
    fp = open(path)
    for line in fp:
        words = line.split()
        if len(words) == 0:
            break
        elif words[0] == '#':
            if words[1] == "uuid":
                fp.close()
                return words[2]
        else:
            break
    fp.close()
    return None
                       
    

