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

Simple download script to fetch additional assets from ftp.
"""

import os
import sys
import shutil
from ftplib import FTP

sys.path = ["./lib"] + sys.path
from getpath import getSysDataPath, isSubPath, getSysPath

def downloadFromFTP(ftp, filePath, destination):
    fileSize = ftp.size(filePath)
    downloaded = [0]    # Is a list so we can pass and change it in an inner func
    f = open(destination, 'wb')
    def writeChunk(data):
        f.write(data)

        downloaded[0] += len(data)
        percentage = 100 * float(downloaded[0]) / fileSize
        sys.stdout.write("  Downloaded %d%% of %d bytes\r" % (percentage, fileSize))

        if percentage >= 100:
            sys.stdout.write('\n')

    ftp.retrbinary('RETR '+filePath, writeChunk)
    f.close()


def downloadFile(ftp, filePath, destination, fileProgress):
    filePath = filePath.replace('\\', '/')
    destination = destination.replace('\\', '/')
    if os.path.dirname(destination) and not os.path.isdir(os.path.dirname(destination)):
        os.makedirs(os.path.dirname(destination))

    #print "[%d%% done] Downloading file %s to %s" % (fileProgress, url, filename)
    print "[%d%% done] Downloading file %s" % (fileProgress, os.path.basename(destination))
    print "             %s ==> %s" % (filePath, destination)
    downloadFromFTP(ftp, filePath, destination)

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
        try:
            contents[c[0]] = long(c[1])
        except:
            contents[c[0]] = 0
    f.close()
    return contents

def writeContentsFile(filename, contents):
    f = open(filename, 'w')
    for fPath, mtime in contents.items():
        f.write("%s %s\n" % (fPath, mtime))
    f.close()

def getNewFiles(oldContents, newContents, destinationFolder):
    result = []
    for (filename, newTime) in newContents.items():
        destFile = os.path.join(destinationFolder, filename.lstrip('/'))
        if not os.path.isfile(destFile):
            result.append(filename)
        elif filename in oldContents:
            oldTime = oldContents[filename]
            if newTime > oldTime:
                result.append(filename)
        else:
            result.append(filename)
    return result

def getRemovedFiles(oldContents, newContents, destinationFolder):
    toRemove = []
    for filename in oldContents.keys():
        if filename not in newContents:
            destFile = os.path.join(destinationFolder, filename.lstrip('/'))
            if os.path.isfile(destFile):
                toRemove.append(filename)
    return toRemove

def getFTPContents(ftp):
    def walkFTP(ftp):
        path = ftp.pwd()    # TODO relpath to root path
        contentsList = []
        directories = []
        s = ftp.retrlines('LIST', contentsList.append)

        for line in contentsList:
            if line.startswith('d'): # is a folder
                directories.append(line.split()[8])

        filesList = [f for f in ftp.nlst() if f not in directories]
        result = []
        for fname in filesList:
            mtime = ftp.sendcmd('MDTM %s' % fname)
            mtime = int(mtime[3:].strip())
            #mtime = int(time.mktime(time.strptime(mtime[3:].strip(), '%Y%m%d%H%M%S')))
            fpath = os.path.join(path, fname)
            result.append( (fpath, mtime) )

        for dir_ in directories:
            ftp.cwd(dir_.replace('\\', '/'))
            result.extend( walkFTP(ftp) )
            ftp.cwd('..')

        return result

    rootPath = ftp.pwd()
    contentsList = walkFTP(ftp)
    result = {}
    # make paths relative to rootpath
    for (p, mtime) in contentsList:
        result[os.path.relpath(p, rootPath)] = mtime

    return result


if __name__ == '__main__':
    ftpUrl = "download.tuxfamily.org"
    ftpPath = "/makehuman/a8/base"

    ftpPath = os.path.normpath(ftpPath)
    ## Use simple sync mechanism, maybe in the future we can use rsync over http?
    # Download contents list
    baseName = os.path.basename(ftpPath)
    contentsFile = getSysPath(baseName+'_contents.txt')
    if os.path.isfile(contentsFile):
        # Parse previous contents file
        oldContents = parseContentsFile(contentsFile)
        if len(oldContents) > 0 and len(str(oldContents[oldContents.keys()[0]])) < 5:
            # Ignore old style contents file
            oldContents = {}
    else:
        oldContents = {}

    # Setup FTP connection
    ftp = FTP(ftpUrl)
    ftp.login()
    ftp.cwd(ftpPath.replace('\\', '/'))

    # Get contents from FTP
    newContents = getFTPContents(ftp)

    destinationFolder = getSysDataPath()
    toDownload = getNewFiles(oldContents, newContents, destinationFolder)
    toRemove = getRemovedFiles(oldContents, newContents, destinationFolder)

    # Remove files removed on FTP
    for filePath in toRemove:
        filename = os.path.join(destinationFolder, filePath.lstrip('/'))

        if not isSubPath(filename, destinationFolder):
            raise RuntimeError("ERROR: File destinations are jailed inside the sys data path (%s), destination path (%s) tries to escape!" % (destinationFolder, filename))

        print "Removing file %s (removed from FTP)" % filename
        os.remove(filename)

    TOTAL_FILES = len(toDownload)

    fIdx = 0
    for filePath in toDownload:
        filename = os.path.join(destinationFolder, filePath.lstrip('/'))

        if not isSubPath(filename, destinationFolder):
            raise RuntimeError("ERROR: File destinations are jailed inside the sys data path (%s), destination path (%s) tries to escape!" % (destinationFolder, filename))

        fileProgress = round(100 * float(fIdx)/TOTAL_FILES, 2)
        downloadFile(ftp, filePath, filename, fileProgress)
        fIdx += 1

    ftp.close()

    writeContentsFile(contentsFile, newContents)

    print "All done."

