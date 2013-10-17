#!/usr/bin/env python
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

Simple download script to fetch additional assets from http.
"""

import os
import urllib2
import sys
import shutil

sys.path = ["./lib"] + sys.path
from getpath import getSysDataPath, isSubPath, getSysPath



def progress(percentage, totalSize):
    sys.stdout.write("  Downloaded %d%% of %d bytes\r" % (percentage, totalSize))

    if percentage >= 100:
        sys.stdout.write('\n')

def download(url, chunkSize=1024, progressCallback=None):
    u = urllib2.urlopen(url)

    totalSize = u.info().getheader('Content-Length').strip()
    totalSize = int(totalSize)
    bytesDownloaded = 0

    result = []

    while True:
        chunk = u.read(chunkSize)
        bytesDownloaded += len(chunk)

        if not chunk:
            return result
        else:
            result.append(chunk)

        if progressCallback:
            percentage = round(100* float(bytesDownloaded) / totalSize, 2)
            progressCallback(percentage, totalSize)


def downloadFile(url, destination, fileProgress):
    if os.path.dirname(destination) and not os.path.isdir(os.path.dirname(destination)):
        os.makedirs(os.path.dirname(destination))
    
    #print "[%d%% done] Downloading file %s to %s" % (fileProgress, url, filename)
    print "[%d%% done] Downloading file %s" % (fileProgress, os.path.basename(destination))
    print "             %s ==> %s" % (url, destination)
    data = download(url, progressCallback = progress)
    destFile = open(destination, 'wb')
    destFile.write(''.join(data))
    destFile.close()

def parseContentsFile(filename):
    f = open(filename)
    fileData = f.read()
    contents = {}
    for l in fileData.split('\n'):
        if not l:
            continue
        if l.startswith('#') or l.startswith('//'):
            continue
        c=l.split()
        contents[c[0]] = float(c[1])
    f.close()
    return contents

def getNewFiles(oldContents, newContents, destinationFolder):
    result = []
    for (filename, version) in newContents.items():
        destFile = os.path.join(destinationFolder, filename.lstrip('/'))
        if not os.path.isfile(destFile):
            result.append(filename)
        elif filename in oldContents:
            oldVersion = oldContents[filename]
            if version > oldVersion:
                result.append(filename)
        else:
            result.append(filename)
    return result

if __name__ == '__main__':
    baseUrl = "http://download.tuxfamily.org/makehuman/a8/base/"

    # Remove previously downloaded assets
    print "Removing old downloaded content"
    oldPaths = [getSysDataPath('hair/hairstyle01'), getSysDataPath('hair/hairstyle02')]
    for oldPath in oldPaths:
        if os.path.exists(oldPath):
            shutil.rmtree(oldPath)

    ## Use simple sync mechanism, maybe in the future we can use rsync over http?
    # Download contents list
    baseUrl = baseUrl.rstrip('/')
    baseName = os.path.basename(baseUrl)
    contentsFile = getSysPath(baseName+'_contents.txt')
    if os.path.isfile(contentsFile):
        # Parse previous contents file
        oldContents = parseContentsFile(contentsFile)
    else:
        oldContents = {}

    # Get and parse new contents file
    downloadFile(baseUrl+"/contents.txt", contentsFile, 0)
    newContents= parseContentsFile(contentsFile)

    destinationFolder = getSysDataPath()
    toDownload = getNewFiles(oldContents, newContents, destinationFolder)
    TOTAL_FILES = len(toDownload)

    fIdx = 0
    for url in toDownload:
        filename = os.path.join(destinationFolder, url.lstrip('/'))

        url = baseUrl+'/'+url.lstrip('/')

        if not isSubPath(filename, destinationFolder):
            raise RuntimeError("ERROR: File destinations are jailed inside the sys data path (%s), destination path (%s) tries to escape!" % (destinationFolder, filename))

        fileProgress = round(100 * float(fIdx)/TOTAL_FILES, 2)
        downloadFile(url, filename, fileProgress)
        fIdx += 1

    print "All done."
