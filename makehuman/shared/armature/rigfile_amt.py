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

Global variables used by MHX package
"""

import os
import log
import numpy as np
import mh2proxy
import gui3d

from .flags import *
from .utils import *
from .armature import *
from .parser import Parser

class RigfileParser(Parser):

    def __init__(self, amt):
        Parser.__init__(self, amt)
        self.filepath = "data/rigs/%s.rig" % amt.options.rigtype
        self.heads = {}
        self.tails = {}
        self.master = None


    def setup(self):
        self.fromRigfile(self.filepath, self.armature.human.meshData)


    def fromRigfile(self, filename, obj, coord=None):
        """
        if type(filename) == tuple:
            (folder, fname) = filename
            self.filename = os.path.join(folder, fname)
        else:
            self.filename = filename
        self.filepath = os.path.realpath(os.path.expanduser(self.filename))
        """
        try:
            fp = open(filename, "rU")
        except:
            log.error("*** Cannot open %s" % filename)
            return

        doLocations = 1
        doBones = 2
        doWeights = 3
        doFileWeights = 4
        status = 0

        amt = self.armature
        boneInfos = {}
        basicNames = {}
        if not coord:
            coord = obj.coord
        for line in fp:
            words = line.split()
            if len(words) == 0:
                pass
            elif words[0] == '#':
                if words[1] == 'locations':
                    status = doLocations
                elif words[1] == 'bones':
                    status = doBones
                elif words[1] == 'weights':
                    status = doWeights
                    wts = []
                    amt.vertexWeights[words[2]] = wts
                elif words[1] == 'file-weights':
                    vgroups = {}
                    vgroupList = []
                    for word in words[2:]:
                        path = os.path.join("shared/armature/vertexgroups", word+".vgrp")
                        readVertexGroups(path, vgroups, vgroupList)
                    status = doFileWeights
            elif status == doWeights:
                wts.append((int(words[0]), float(words[1])))
            elif status == doFileWeights:
                bname = words[0]
                basicNames[bname] = basicName = words[1]
                vgroup = vgroups[basicName]
                for word in words[2:]:
                    vgroup += vgroups[word]
                if len(words) > 2:
                    amt.vertexWeights[bname] = mergeWeights(vgroup)
                else:
                    amt.vertexWeights[bname] = vgroup
            elif status == doLocations:
                self.setupRigJoint (words, obj, coord)
            elif status == doBones:
                bname = words[0]
                bone = Bone(amt, bname)
                bone.head = self.locations[words[1]] - self.origin
                bone.tail = self.locations[words[2]] - self.origin
                bone.roll = float(words[3])
                bone.parent = words[4]
                if bone.parent == "-":
                    bone.parent = None
                    self.root = bname

                key = None
                value = []
                flags = F_DEF|F_CON
                for word in words[5:]:
                    if isinstance(word, float):
                        value.append(word)
                    elif word[0] == '-':
                        flags = self.setOption(bname, key, value, flags)
                        key = word[0]
                        value = []
                    else:
                        value.append(word)
                if key:
                    flags = self.setOption(bname, key, value, flags)
                bone.setFlags(flags)
                boneInfos[bname] = bone
            else:
                raise NameError("Unknown status %d" % status)
        fp.close()

        #self.sortBones(boneInfos, amt.hierarchy)
        self.createBones(boneInfos)
        for bone in amt.bones.values():
            bone.setBone(bone.head, bone.tail)

        if True:
            basic = getBasicArmature(amt.human)
            for bone in amt.bones.values():
                try:
                    basicName = basicNames[bone.name]
                except KeyError:
                    continue
                bone.roll = basic.bones[basicName].roll

        for bone in amt.bones.values():
            bone.calcRestMatrix()


    def getHeadTail(self, bname):
        return self.heads[bname], self,tails[bname]

    def setHeadTail(self, bname, head, tail):
        self.heads[bname] = head
        self.tails[bname] = tail


    def setupRigJoint(self, words, obj, coord):
        key = words[0]
        typ = words[1]
        if typ == 'joint':
            self.locations[key] = mh2proxy.calcJointPos(obj, words[2])
        elif typ == 'vertex':
            vn = int(words[2])
            self.locations[key] = obj.coord[vn]
        elif typ == 'position':
            x = self.locations[int(words[2])]
            y = self.locations[int(words[3])]
            z = self.locations[int(words[4])]
            self.locations[key] = np.array((x[0],y[1],z[2]))
        elif typ == 'line':
            k1 = float(words[2])
            vn1 = int(words[3])
            k2 = float(words[4])
            vn2 = int(words[5])
            self.locations[key] = k1*self.locations[vn1] + k2*self.locations[vn2]
        elif typ == 'offset':
            loc = words[2]
            x = float(words[3])
            y = float(words[4])
            z = float(words[5])
            self.locations[key] = self.locations[loc] + np.array((x,y,z))
        elif typ == 'voffset':
            vn = int(words[2])
            x = float(words[3])
            y = float(words[4])
            z = float(words[5])
            try:
                loc = obj.coord[vn]
            except:
                loc = coord[vn]
            self.locations[key] = loc + np.array((x,y,z))
        elif typ == 'front':
            raw = self.locations[words[2]]
            head = self.locations[words[3]]
            tail = self.locations[words[4]]
            offs = map(float, words[5].strip().lstrip('[').rstrip(']').split(','))
            offs = np.array(offs)
            vec =  tail - head
            vraw = raw - head
            x = np.dot(vec,vraw) / np.dot(vec, vec)
            self.locations[key] = head + x*vec + offs
        else:
            raise NameError("Unknown %s" % typ)


    def setOption(self, bname, key, value, flags):
        if key == "-nc":
            flags &= ~F_CON
        elif key == "-nd":
            flags &= ~F_DEF
        elif key == "-res":
            flags |= F_RES
        elif key == "-circ":
            name = "Circ"+value[0]
            self.customShapes[name] = (key, int(value[0]))
            self.addPoseInfo(bname, ("CS", name))
            flags |= F_WIR
        elif key == "-box":
            name = "Box" + value[0]
            self.customShapes[name] = (key, int(value[0]))
            self.addPoseInfo(bname, ("CS", name))
            flags |= F_WIR
        elif key == "-ik":
            try:
                pt = options["-pt"]
            except KeyError:
                pt = None
            log.debug("%s %s", value, pt)
            value.append(pt)
            self.addPoseInfo(bname, ("IK", value))
        elif key == "-ik":
            pass
        return flags


    def addPoseInfo(self, bname, info):
        try:
            self.poseInfo[bname]
        except KeyError:
            self.poseInfo[bname] = []
        self.poseInfo[bname].append(info)



def readRigfileArmature(filename, obj, coord=None):
    amt = Armature("Global", gui3d.app.selectedHuman, RigOptions())
    amt.parser = RigfileParser(amt)
    amt.parser.fromRigfile(filename, obj, coord)
    return amt


def getBasicArmature(human):
    from .basic import BasicParser
    amt = Armature("Basic", human, RigOptions())
    amt.parser = BasicParser(amt)
    amt.parser.setupToRoll()
    return amt

