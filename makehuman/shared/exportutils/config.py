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


def truthValue(word):
    if word.lower() in ["false", "no", "0"]:
        return False
    return True

#
#    proxyFilePtr(name):
#

def proxyFilePtr(name):
    head = os.path.normpath(mh.getPath(''))
    for path in [head, './']:
        filename = os.path.realpath( os.path.join(path, name) )
        try:
            fp = open(filename, "r")
            log.message("    Using config file %s", filename)
            return fp
        except:
            log.error("Cannot open %s", filename, exc_info=True)
    return None
    
#
#   class CProxyFile:
#

class CProxyFile:
    def __init__(self):
        self.type = 'Clothes'
        self.layer = 0
        self.file = ""
        self.name = None
        
    def set(self, type, layer):
        self.type = type
        self.layer = layer
        
    def __repr__(self):
        return (
"<CProxyFile type %s layer %d\n" % (self.type, self.layer) +
"    name %s file \"%s\">" % (self.name, self.file))
        
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
            

def exportConfig(human, config):

    if human.hairProxy:
        words = human.hairObj.mesh.name.split('.')
        pfile = CProxyFile()
        pfile.set('Hair', 2)
        name = goodName(words[0])
        pfile.file = human.hairProxy.file
        config.proxyList.append(pfile)

    for (key,clo) in human.clothesObjs.items():
        if clo:
            name = goodName(key)
            pfile = CProxyFile()
            pfile.set('Clothes', 3)            
            proxy = human.clothesProxies[key]
            pfile.file = proxy.file
            config.proxyList.append(pfile)
            
    if human.proxy:
        name = goodName(human.proxy.name)
        pfile = CProxyFile()
        pfile.set('Proxy', 4)
        pfile.file = human.proxy.file
        config.proxyList.append(pfile)    

    if config.cage:
        pfile = getCageFile("./data/cages/cage/cage.mhclo", 4)
        config.proxyList.append(pfile)    
            
    
def getCageFile(name, layer):
    pfile = CProxyFile()
    pfile.set('Cage', layer)
    name = goodName(name)
    pfile.file = os.path.realpath(os.path.expanduser(name))
    return pfile


def getOutFileFolder(filename, config):
    (fname, ext) = os.path.splitext(filename)
    fname = goodName(os.path.basename(fname))
    if config.separateFolder:
        config.outFolder = getSubFolder(os.path.dirname(filename), fname)
        if config.outFolder:
            outfile = os.path.join(config.outFolder, "%s%s" % (fname, ext)) 
        config.texFolder = getSubFolder(config.outFolder, "textures")
        config.copiedFiles = {}
    if not config.texFolder:
        outfile = filename
    return outfile


def getSubFolder(path, name):
    folder = os.path.join(path, name)
    #print "Using folder", folder
    if not os.path.exists(folder):
        log.message("Creating folder %s", folder)
        #print folder
        try:
            os.mkdir(folder)
        except:
            log.error("Unable to create separate folder:", exc_info=True)
            #print folder
            return None
    return folder        
    

def getOutFileName(filePath, fromDir, isTexture, human, config):
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
    if config.separateFolder:
        if isTexture:
            toPath = os.path.join(config.texFolder, filename)
        else:
            toPath = os.path.join(config.outFolder, filename)
        try:
            config.copiedFiles[fromPath]
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
            config.copiedFiles[fromPath] = True
        return toPath
    else:
        fromAbs = os.path.abspath(fromPath)
        str(os.path.normpath(os.path.relpath(fromAbs, ".")))
        return fromPath
        
        
def goodName(name):
    return name.replace(" ", "_").replace("-","_").lower()
