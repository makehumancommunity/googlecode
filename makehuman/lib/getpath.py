#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Manuel Bastioni, Marc Flerackers, Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Utility module for finding the user home path.
"""

import sys
import os

__home_path = None

def getHomePath():
    """
    Find the user home path.
    Note: If you are looking for MakeHuman data, you probably want getPath()!
    """
    # Cache the home path
    global __home_path
    if __home_path is not None:
        return __home_path

    # Windows
    if sys.platform == 'win32':
        import _winreg
        keyname = r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
        #name = 'Personal'
        k = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, keyname)
        value, type_ = _winreg.QueryValueEx(k, 'Personal')
        if type_ == _winreg.REG_EXPAND_SZ:
            __home_path = _winreg.ExpandEnvironmentStrings(value)
            return __home_path
        elif type_ == _winreg.REG_SZ:
            __home_path = value
            return __home_path
        else:
            raise RuntimeError("Couldn't determine user folder")

    # Unix-based
    else:
        __home_path = os.path.expanduser('~')
        return __home_path

def getPath(type = None):
    """
    Get MakeHuman folder that contains per-user files, located in the user home
    path.
    """
    if isinstance(type, (str, unicode)):
        typeStr = str(type)
    elif type is None:
        typeStr = ""
    else:
        raise TypeError("String expected")

    path = getHomePath()

    # Windows
    if sys.platform == 'win32':
        path = os.path.join(path, "makehuman")

    # MAC OSX
    elif sys.platform.startswith("darwin"):
        path = os.path.join(path, "Documents")
        path = os.path.join(path, "MakeHuman")

    # Unix/Linux
    else:
        path = os.path.join(path, "makehuman")


    if typeStr == "exports":
        return os.path.join(path, 'exports')
    elif typeStr == "models":
        return os.path.join(path, 'models')
    elif typeStr == "grab":
        return os.path.join(path, 'grab')
    elif typeStr == "render":
        return os.path.join(path, 'render')
    elif typeStr == "scenes":
        return os.path.join(path, 'scenes')
    elif typeStr == "":
        return path
    else:
        raise ValueError("Unknown value '%s' for getPath()!" % typeStr)

def getSysDataPath(subPath = ""):
    """
    Path to the data folder that is installed with MakeHuman system-wide.
    """
    if subPath:
        return getSysPath( os.path.join("data", subPath) )
    else:
        return getSysPath("data/")

def getSysPath(subPath):
    """
    Path to the system folder where MakeHuman is installed (it is possible that 
    data is stored in another path).
    Writing to this folder or modifying this data usually requires admin rights,
    contains system-wide data (for all users).
    """
    if subPath:
        return os.path.join(subPath)
    else:
        return os.path.join(".")


def _allnamesequal(name):
    return all(n==name[0] for n in name[1:])

def commonprefix(paths, sep='/'):
    """
    Implementation of os.path.commonprefix that works as you would expect.
    
    Source: http://rosettacode.org/wiki/Find_Common_Directory_Path#Python
    """
    from itertools import takewhile
    
    bydirectorylevels = zip(*[p.split(sep) for p in paths])
    return sep.join(x[0] for x in takewhile(_allnamesequal, bydirectorylevels))

def isSubPath(subpath, path):
    """
    Verifies whether subpath is within path.
    """
    subpath = os.path.normpath(os.path.realpath(subpath))
    path = os.path.normpath(os.path.realpath(path))
    return commonprefix([subpath, path]) == path
