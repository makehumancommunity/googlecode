# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165

import bpy
import os
import math

from . import globvars as the

#
#    class CProxy
#

class CProxy:
    def __init__(self):
        self.name = None
        self.obj_file = None
        self.refVerts = []
        self.firstVert = 0
        self.rScale = None
        self.xScale = None
        self.yScale = None
        self.zScale = None
        self.nVerts = the.NTotalVerts
        return
        
    def __repr__(self):
        return ("<CProxy %s %d\n  %s\n  w %s\n x %s\n  y %s\n  z %s>" % 
            (self.name, self.firstVert, self.obj_file, self.rScale, self.xScale, self.yScale, self.zScale))
        
    def update(self, srcVerts, trgVerts, useManualScale=False, manualScale=1.0, skipBefore=0, skipAfter=100000):
        rlen = len(self.refVerts)
        mlen = len(trgVerts)
        first = self.firstVert
        if (first+rlen) != mlen:
            raise NameError( "Bug: %d refVerts != %d meshVerts" % (first+rlen, mlen) )

        if useManualScale:
            s0 = s1 = s2 = manualScale
        elif self.rScale:
            s0 = s1 = s2 = getScale(self.rScale, srcVerts, -1)
        else:
            s0 = getScale(self.xScale, srcVerts, 0)
            s1 = getScale(self.yScale, srcVerts, 2)
            s2 = getScale(self.zScale, srcVerts, 1)
        print("Scales", s0, s1, s2)

        for n in range(rlen):
            if n < skipBefore or n >= skipAfter:
                continue
            trgVert = trgVerts[n+first]
            refVert = self.refVerts[n]
            if type(refVert) == tuple:
                (rv0, rv1, rv2, w0, w1, w2, d0, d1, d2) = refVert
                v0 = srcVerts[rv0]
                v1 = srcVerts[rv1]
                v2 = srcVerts[rv2]
                trgVert.co[0] = w0*v0.co[0] + w1*v1.co[0] + w2*v2.co[0] + d0*s0
                trgVert.co[1] = w0*v0.co[1] + w1*v1.co[1] + w2*v2.co[1] - d2*s2
                trgVert.co[2] = w0*v0.co[2] + w1*v1.co[2] + w2*v2.co[2] + d1*s1
                #bverts[n+first].select = (bverts[rv0].select or bverts[rv1].select or bverts[rv2].select)
                """
                if n == 940:
                    print("V0", v0.co)
                    print("V1", v1.co)
                    print("V2", v2.co)
                    print("w", w0,w1,w2)
                    print("s", s0,s1,s2)
                    print("d", d0,d1,d2)
                    print("t", trgVert.co)
                """
            else:
                v0 = srcVerts[refVert]
                trgVert.co = v0.co
                #bvert[n+first].select = bverts[rv0].select
        return s0

    def read(self, filepath):
        realpath = os.path.realpath(os.path.expanduser(filepath))
        folder = os.path.dirname(realpath)
        try:
            tmpl = open(filepath, "rU")
        except:
            tmpl = None
        if tmpl == None:
            print("*** Cannot open %s" % realpath)
            return None

        status = 0
        doVerts = 1
        vn = 0
        for line in tmpl:
            words= line.split()
            if len(words) == 0:
                pass
            elif words[0] == '#':
                status = 0
                if len(words) == 1:
                    pass
                elif words[1] == 'verts':
                    if len(words) > 2:
                        self.firstVert = int(words[2])                    
                    status = doVerts
                elif words[1] == 'name':
                    self.name = words[2]
                elif words[1] == 'r_scale':
                    self.rScale = scaleInfo(words)
                elif words[1] == 'x_scale':
                    self.xScale = scaleInfo(words)
                elif words[1] == 'y_scale':
                    self.yScale = scaleInfo(words)
                elif words[1] == 'z_scale':
                    self.zScale = scaleInfo(words)                
                elif words[1] == 'obj_file':
                    self.obj_file = os.path.join(folder, words[2])
                else:
                    pass
            elif status == doVerts:
                if len(words) == 1:
                    v = int(words[0])
                    self.refVerts.append(v)
                else:                
                    v0 = int(words[0])
                    v1 = int(words[1])
                    v2 = int(words[2])
                    w0 = float(words[3])
                    w1 = float(words[4])
                    w2 = float(words[5])            
                    d0 = float(words[6])
                    d1 = float(words[7])
                    d2 = float(words[8])
                    self.refVerts.append( (v0,v1,v2,w0,w1,w2,d0,d1,d2) )
        return


def scaleInfo(words):                
    v1 = int(words[2])
    v2 = int(words[3])
    den = float(words[4])
    return (v1, v2, den)


def getScale(info, verts, index):
    if info is None:
        return 1.0
    (vn1, vn2, den) = info
    if index > 0:
        num = abs(verts[vn1].co[index] - verts[vn2].co[index])
    else:
        v1 = verts[vn1].co
        v2 = verts[vn2].co
        dx = v1[0]-v2[0]
        dy = v1[1]-v2[1]
        dz = v1[2]-v2[2]
        num = math.sqrt(dx*dx + dy*dy + dz*dz)
    return num/den
    