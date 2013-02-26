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

Functions shared by all rigs 

Limit angles from http://hippydrome.com/
"""

import math
import numpy
import os
import sys
import mh2proxy
import exportutils
import log

#-------------------------------------------------------------------------------        
#
#-------------------------------------------------------------------------------        

def writeAction(fp, cond, name, action, lr, ikfk):
    """
    Write actions to the MHX file. This function is currently not in use, but may be
    reintroduced later.
    """
    fp.write("Action %s %s\n" % (name,cond))
    if ikfk:
        iklist = ["IK", "FK"]
    else:
        iklist = [""]
    if lr:
        for (bone, quats) in action:
            rquats = []
            for (t,x,y,z,w) in rquats:
                rquats.append((t,x,y,-z,-w))
            for ik in iklist:
                writeFCurves(fp, "%s%s_L" % (bone, ik), quats)
                writeFCurves(fp, "%s%s_R" % (bone, ik), rquats)
    else:
        for (bone, quats) in action:
            for ik in iklist:
                writeFCurves(fp, "%s%s" % (bone, ik), quats)
    fp.write("end Action\n\n")
    return


def writeFCurves(fp, name, quats):
    """
    Write actions to the MHX file. This function is only used by writeAction, and thus
    currently not in use, but may be reintroduced later.
    """
    n = len(quats)
    for index in range(4):
        fp.write("\n" +
            "  FCurve pose.bones[\"%s\"].rotation_quaternion %d\n" % (name, index))
        for m in range(n):
            t = quats[m][0]
            x = quats[m][index+1]
            fp.write("    kp %d %.4g ;\n" % (t,x))
        fp.write(
            "    extrapolation 'CONSTANT' ;\n" +
            "  end FCurve \n")
    return
    
