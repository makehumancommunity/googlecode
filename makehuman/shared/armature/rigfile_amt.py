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
import mh2proxy

from .flags import *
from .base_amt import BaseArmature

class RigfileArmature(BaseArmature):     
    
    def __init__(self, name, human, config):
        self.filepath = "data/rigs/%s.rig" % config.rigtype
        BaseArmature.__init__(self, name, human, config)
    
    
    def setup(self):
        self.fromRigfile(self.filepath, self.human.meshData)
    
    
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
        status = 0
    
        bones = {}
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
                    self.vertexWeights[words[2]] = wts
            elif status == doWeights:
                wts.append((int(words[0]), float(words[1])))
            elif status == doLocations:
                self.setupRigJoint (words, obj, coord)
            elif status == doBones:
                bone = words[0]
                self.heads[bone] = self.locations[words[1]] - self.origin
                self.tails[bone] = self.locations[words[2]] - self.origin
                roll = self.rolls[bone] = float(words[3])
                parent = words[4]
                if parent == "-":
                    parent = None  
                    self.root = bone
                self.parents[bone] = parent       
                self.layers[bone] = L_MAIN
                
                key = None
                value = []
                flags = F_DEF|F_CON
                for word in words[5:]:
                    if isinstance(word, float):
                        value.append(word)
                    elif word[0] == '-':
                        flags = self.setOption(bone, key, value, flags)
                        key = word[0]
                        value = []
                    else:
                        value.append(word)
                if key:
                    flags = self.setOption(bone, key, value, flags) 
                self.flags[bone] = flags
                bones[bone] = (roll, parent, flags, L_MAIN)
            else:
                raise NameError("Unknown status %d" % status)

        self.sortBones(bones)    
        fp.close()
        

    def getHeadTail(self, bone):
        return self.heads[bone], self,tails[bone]
        
    def setHeadTail(self, bone, head, tail):
        self.heads[bone] = head 
        self,tails[bone] = tail
        
        
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
            vn = int(words[2])
            x = float(words[3])
            y = float(words[4])
            z = float(words[5])
            self.locations[key] = self.locations[vn] + np.array((x,y,z))
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
    
    
    def setOption(self, bone, key, value, flags):
        if key == "-nc":
            flags &= ~F_CON
        elif key == "-nd":
            flags &= ~F_DEF
        elif key == "-res":
            flags |= F_RES
        elif key == "-circ":
            name = "Circ"+value[0]
            self.customShapes[name] = (key, int(value[0]))
            self.addPoseInfo(bone, ("CS", name))
            flags |= F_WIR
        elif key == "-box":
            name = "Box" + value[0]
            self.customShapes[name] = (key, int(value[0]))
            self.addPoseInfo(bone, ("CS", name))
            flags |= F_WIR
        elif key == "-ik":
            try:
                pt = options["-pt"]
            except KeyError:
                pt = None
            log.debug("%s %s", value, pt)
            value.append(pt)
            self.addPoseInfo(bone, ("IK", value))
        elif key == "-ik":
            pass
        return flags
        

    def addPoseInfo(self, bone, info):
        try:
            self.poseInfo[bone]
        except KeyError:
            self.poseInfo[bone] = []
        self.poseInfo[bone].append(info)



