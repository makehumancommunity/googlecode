#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import os
import zipfile
from getpath import getSysDataPath
import log

# TODO share with algos3d
TARGETS_NPZ_PATH = getSysDataPath('targets.npz')

class Component(object):
    """
    Defines a target or target folder.
    Refers to its path either in an NPZ archive or as a file on disk.
    A Component does not actually contain target data, see algos3d.Target for
    that.
    """

    # Defines reserved value keywords and which category they map to
    # Used for specifying dependencies between targets using their filename
    _cat_data = [
       # category     values
        ('gender',   ['male', 'female']),
        ('age',      ['baby', 'child', 'young', 'old']),
        ('race',     ['caucasian', 'asian', 'african']),
        ('muscle',   ['maxmuscle', 'averagemuscle', 'minmuscle']),
        ('weight',   ['minweight', 'averageweight', 'maxweight']),
        ('height',   ['dwarf', 'giant']),
        ('cup',      ['cup1', 'cup2']),
        ('firmness', ['firmness0', 'firmness1'])
        ]

    _cat_values = dict(_cat_data)
    _categories = [cat for cat, value in _cat_data]
    _value_cat = dict([(value, cat)
                       for cat, values in _cat_data
                       for value in values])
    del cat, value, values

    def __init__(self, other = None):
        self.path = None
        if other is None:
            self.key = []   # Used for referencing this component in Targets.groups
            self.data = {}  # Dependent (macro) variables that influence the weight of this target
        else:
            self.key = other.key[:]
            self.data = other.data.copy()

    def __repr__(self):
        return repr((self.key, self.data, self.path))

    def set_data(self, category, value):
        orig = self.data.get(category)
        if orig is not None and orig != value:
            raise RuntimeError('%s already set' % category)
        self.data = self.data.copy()
        self.data[category] = value

    def add_key(self, value):
        self.key.append(value)

    def clone(self):
        return Component(self)

    def update(self, value):
        category = self._value_cat.get(value)
        if category is not None:
            self.set_data(category, value)
        elif value == 'target':
            pass
        else:
            self.add_key(value)

    def finish(self, path):
        """
        Finish component as a leaf in the tree (file).
        """
        self.path = path
        for category in self._categories:
            if category not in self.data:
                self.data[category] = None

class TargetsCrawler(object):
    """
    Recursive target finder baseclass.
    """
    def __init__(self, root, dataPath = None):
        self.root = root
        self.dataPath = dataPath

        if self.dataPath:
            if os.path.basename(os.path.normpath(self.dataPath)) != "data":
                log.warning('Data path containing targets (%s) is not called "data", this might cause problems with wrong relative target paths when trying to load from a .npz archive (which are usually compiled against data/targets relative path).', self.dataPath)

            self.relPath = os.path.normpath(os.path.join(dataPath, '..'))
        else:
            self.relPath = None

        self.rootComponent = Component()

        self.targets = []
        self.groups = {}
        self.images = {}

    def list_dir(self, path):
        raise NotImplementedError("Implement TargetsCrawler.list_dir(path)")

    def is_dir(self, path):
        raise NotImplementedError("Implement TargetsCrawler.is_dir(path)")

    def is_file(self, path):
        raise NotImplementedError("Implement TargetsCrawler.is_file(path)")

    def findTargets(self):
        if self.relPath:
            rootPath = os.path.relpath(self.root, self.relPath)
        else:
            rootPath = self.root

        self.walkTargets(rootPath, self.rootComponent)

    def real_path(self, path):
        raise NotImplementedError("Implement TargetsCrawler.real_path(path)")

    def walkTargets(self, root, base):
        dirs = self.list_dir(self.real_path(root))
        for name in sorted(dirs):
            path = self.real_path(os.path.join(root, name)).replace('\\','/')

            if self.is_file(path) and not path.lower().endswith('.target'):
                # File but not a .target file
                if path.lower().endswith('.png'):
                    # Add image
                    self.images[name.lower()] = path

            else:   # Add target or folder
                item = base.clone() # Create new Component

                # Split filename in parts
                parts = name.replace('_','-').replace('.','-').split('-')
                for part in parts:
                    item.update(part)   # Set Component.key or dependencies data

                if self.is_dir(path):
                    # Continue recursion on subfolder
                    _root = os.path.join(root, name).replace('\\','/')
                    self.walkTargets(_root, item)
                else: # File is a .target file: add Component to groups
                    item.finish(path)
                    self.targets.append(item)
                    key = tuple(item.key)
                    if key not in self.groups:
                        self.groups[key] = []
                    self.groups[key].append(item)


class FilesTargetsCrawler(TargetsCrawler):
    """
    Finds targets that are separate ASCII .target files in recursive folders.
    """
    def __init__(self, root, dataPath = None):
        super(FilesTargetsCrawler, self).__init__(root, dataPath)

    def is_dir(self, path):
        return os.path.isdir(path)

    def is_file(self, path):
        return os.path.isfile(path)

    def list_dir(self, path):
        return os.listdir(path)

    def real_path(self, path):
        if self.relPath:
            return os.path.join(self.relPath, path)
        else:
            return path


class ZippedTargetsCrawler(TargetsCrawler):
    """
    Finds targets packed in a binary .npz archive.
    """
    def __init__(self, root, dataPath = None):
        if not os.path.isfile(TARGETS_NPZ_PATH):
            raise StandardError('Could not load load targets from npz archive. Archive file %s not found.', TARGETS_NPZ_PATH)
        super(ZippedTargetsCrawler, self).__init__(root, dataPath)
        self._files = None

    def is_file(self, path):
        return self.namei(path) is None

    def is_dir(self, path):
        return isinstance(self.namei(path), dict)

    def list_dir(self, path):
        if self._files is None:
            self.buildTree()
        return self.namei(path).keys()

    def real_path(self, path):
        # Target is always relative (within npz file)
        return path

    def namei(self, path):
        if isinstance(path, basestring):
            path = list(reversed(path.split('/')))
        else:
            path = list(reversed(path))
        dir_ = self._files
        while path:
            dir_ = dir_[path.pop()]
        return dir_

    def buildTree(self):
        """
        Build file list of .target and image files from targets.npz image and
        images.list
        Targets in NPZ archive are referenced as regular target files relative
        to sys path (paths like data/targets/...).
        This method will throw an exception if npz is not found or faulty.
        """
        self._files = {}

        def add_file(dir, path):
            head, tail = path[0], path[1:]
            if not tail:
                dir[head] = None
            else:
                if head not in dir:
                    dir[head] = {}
                add_file(dir[head], tail)

        # Add targets in npz archive to file list
        with zipfile.ZipFile(TARGETS_NPZ_PATH, 'r') as npzfile:
            for file_ in npzfile.infolist():
                name = file_.filename
                if not name.endswith('.index.npy'):
                    continue
                name = name[:-len('.index.npy')] + '.target'
                path = name.split('/')
                add_file(self._files, path)

        # Add images to file list
        with open(getSysDataPath('images.list'), 'r') as imgfile:
            for line in imgfile:
                name = line.rstrip()
                if not name.endswith('.png'):
                    continue
                path = name.split('/')
                add_file(self._files, path)


class Targets(object):
    def __init__(self, root, dataPath = None):
        # TODO root is a param, but the location of the .npz file is not. This is not consistent
        self.targets = []       # List of target files
        self.groups = {}        # Target components, ordered per group
        self.images = {}        # Images list
        self.walk(root, dataPath)

    def debugKeys(self):
        """
        Debug print all keys for the targets stored in groups.
        """
        log.debug("Targets keys:\n%s", "\n".join(["-".join(k) for k in self.groups.keys()]))

    def debugTargets(self, showData = False):
        """
        Elaborately print all targets stored in this collection.
        """
        for groupKey, targets in self.groups.items():
            groupKeyStr = "-".join(groupKey)
            log.debug("\n========== Group: %s ===============\n", groupKeyStr)
            for targetComponent in targets:
                log.debug("    [target] path: %s", targetComponent.path)
                if showData:
                    log.debug("             data: %s", targetComponent.data)
                dependsOn = dict([(varName, value) 
                            for (varName, value) in targetComponent.data.items()
                            if value is not None])
                log.debug("             depends on variables: %s", dependsOn)

    def walk(self, root, dataPath = None):
        try:
            # Load cached targets from .npz file
            log.debug("Attempting to load targets from NPZ file.")
            targetFinder = ZippedTargetsCrawler(root, dataPath)
            targetFinder.findTargets()
            log.debug("%s targets loaded from NPZ file succesfully.", len(targetFinder.targets))
        except StandardError as e:
            # Load targets from .target files
            log.debug("Could not load targets from NPZ, loading individual files from %s (Error message: %s)", root, e.message)
            targetFinder = FilesTargetsCrawler(root, dataPath)
            targetFinder.findTargets()
            log.debug("%s targets loaded from .target files.", len(targetFinder.targets))

        self.targets = targetFinder.targets
        self.groups = targetFinder.groups
        self.images = targetFinder.images


_targets = None

def getTargets():
    global _targets
    if _targets is None:
        _targets = Targets(getSysDataPath('targets'), getSysDataPath())
    return _targets
