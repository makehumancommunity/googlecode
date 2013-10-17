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
from getpath import getPath, getSysDataPath, isSubPath



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


def downloadFile(url, destinationFolder, fileProgress):
    if not os.path.isdir(destinationFolder):
        os.makedirs(destinationFolder)

    filename = os.path.basename(url)
    filename = os.path.join(destinationFolder, filename)

    if not isSubPath(filename, getSysDataPath()):
        raise RuntimeError("ERROR: File destinations are jailed inside the sys data path (%s), destination path (%s) tries to escape!" % (getSysDataPath(), filename))

    #print "[%d%% done] Downloading file %s to %s" % (fileProgress, url, filename)
    print "[%d%% done] Downloading file %s" % (fileProgress, os.path.basename(filename))
    print "             %s ==> %s" % (url, filename)
    data = download(url, progressCallback = progress)
    destFile = open(filename, 'w')
    destFile.write(''.join(data))
    destFile.close()


if __name__ == '__main__':
    baseUrl = "http://download.tuxfamily.org/makehuman/a8/base/"

    # Remove previously downloaded assets
    print "Removing old downloaded content"
    oldPaths = [getSysDataPath('hair/hairstyle01'), getSysDataPath('hair/hairstyle02')]
    for oldPath in oldPaths:
        if os.path.exists(oldPath):
            shutil.rmtree(oldPath)

    # Hardcoded for now
    TOTAL_FILES = 8
    fileUrls = ["hair/hairtype01/red-brown-3.png", 
                "hair/hairtype01/hairtype01.mhmat", 
                "hair/hairtype01/longhair01.mhclo", 
                "hair/hairtype01/longhair01.obj", 
                "hair/hairtype01/longhair01.thumb",
                "hair/hairtype01/mediumhair01.mhclo", 
                "hair/hairtype01/mediumhair01.obj", 
                "hair/hairtype01/mediumhair01.thumb"]

    fIdx = 0
    for url in fileUrls:
        url = baseUrl+url
        fileProgress = round(100 * float(fIdx)/TOTAL_FILES, 2)
        downloadFile(url, getSysDataPath('hair/hairtype01'), fileProgress)
        fIdx += 1

    print "All done."
