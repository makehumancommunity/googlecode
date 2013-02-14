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
# Code Home Page:      http://code.googlem/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165

"""
Abstract

Convert targets

"""

import bpy
import os
import math
from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper

from mh_utils import proxy


#----------------------------------------------------------
#   
#----------------------------------------------------------

def round(x):
    if abs(x) < 1e-3:
        return "0"
    string = "%.3g" % x
    if len(string) > 2:
        if string[:2] == "0.":
            return string[1:5]
        elif string[:3] == "-0.":
            return "-" + string[2:6]
    return string

        
Epsilon = 1e-3

#----------------------------------------------------------
#   
#----------------------------------------------------------

class VIEW3D_OT_SetBaseObjButton(bpy.types.Operator):
    bl_idname = "mh.set_base_obj"
    bl_label = "Set New Base Obj File"
    bl_options = {'UNDO'}

    filename_ext = ".obj"
    filter_glob = StringProperty(default="*.obj", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for base obj", 
        maxlen= 1024, default= "")

    def execute(self, context):
        global theProxy
        context.scene.CTBaseObj = self.filepath
        theProxy = None
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_SetConvertMhcloButton(bpy.types.Operator):
    bl_idname = "mh.set_convert_mhclo"
    bl_label = "Set Convert Mhclo File"
    bl_options = {'UNDO'}

    filename_ext = ".mhclo"
    filter_glob = StringProperty(default="*.mhclo", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for convert mhclo", 
        maxlen= 1024, default= "")

    def execute(self, context):
        global theProxy
        context.scene.CTConvertMhclo = self.filepath
        theProxy = None
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_SetSourceTargetButton(bpy.types.Operator):
    bl_idname = "mh.set_source_target"
    bl_label = "Set Source Target File"
    bl_options = {'UNDO'}

    filename_ext = ".target"
    filter_glob = StringProperty(default="*.target", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for target", 
        maxlen= 1024, default= "")

    def execute(self, context):
        context.scene.CTSourceTarget = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_SetTargetDirButton(bpy.types.Operator):
    bl_idname = "mh.set_target_dir"
    bl_label = "Set Target Directory"
    bl_options = {'UNDO'}

    filename_ext = ".target"
    filter_glob = StringProperty(default="*.target", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for target", 
        maxlen= 1024, default= "")

    def execute(self, context):
        context.scene.CTTargetDir = os.path.dirname(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#----------------------------------------------------------
#   
#----------------------------------------------------------
 
class VIEW3D_OT_ConvertTargetButton(bpy.types.Operator):
    bl_idname = "mh.convert_target"
    bl_label = "Convert Target File"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        convertTargetFile(context)
        return {'FINISHED'}


def convertTargetFile(context):
    global theProxy
    scn = context.scene

    if not theBaseObj:
        if scn.CTBaseObj:
            print("Reading %s" % scn.CTBaseObj)
            theBaseVerts = readBaseObj(scn.CTBaseObj)
        else:
            raise NameError("No base obj path selected")
            
    if not theProxy:
        if scn.CTConvertMhclo:
            print("Reading %s" % scn.CTConvertMhclo)
            theProxy = proxy.CProxy()
            theProxy.read(scn.CTConvertMhclo)
        else:
            raise NameError("No convert mhclo path selected")
            
    srcFile = scn.CTSourceTarget
    trgFile = os.path.join(scn.CTTargetDir, os.path.basename(srcFile))
    
    print("Base verts", len(theBaseVerts))
    print("Proxy", theProxy)
    print("Source", srcFile)
    print("Target", trgFile)
    
    srcVerts = readTarget(srcFile, theBaseVerts)
    trgVerts = copyVerts(theBaseVerts)   
    theProxy.update(srcVerts, trgVerts)
    saveTarget(trgVerts, theBaseVerts, trgFile)


def readBaseObj(filepath):
    fp = open(filepath, "rU")
    verts = {}
    vn = 0
    for line in fp:
        words = line.split()
        if len(words) == 4 and words[0] == 'v':
            x,y,z = float(words[1]), float(words[2]), float(words[3])
            verts[vn] = CVertex(x,y,z)
            vn += 1
    fp.close()            
    return verts            


def readTarget(filepath, theBaseVerts):
    verts = {}
    zero = CVertex(0,0,0)
    for n in range(len(theBaseVerts)):
        verts[n] = zero

    fp = open(filepath, "rU")
    for line in fp:
        words = line.split()
        if len(words) == 4:
            x,y,z = float(words[1]), float(words[2]), float(words[3])
            verts[int(words[0])] = CVertex(x,y,z)
    fp.close()            
    return verts            


def copyVerts(verts):
    newverts = {}
    for n,v in verts.items():
        newverts[n] = v.copy()
    return newverts


def saveTarget(trgVerts, baseVerts, filepath):
    fp = open(filepath, "w")
    for vn,trgVert in trgVerts.items():
        baseVert = baseVerts[vn]
        #print(trgVert, baseVert)
        #trgVert.sub(baseVert)
        if trgVert.length() > Epsilon:
            co = trgVert.co
            fp.write("%d %s %s %s\n" % (vn, round(co[0]), round(co[1]), round(co[2])))
    fp.close()
    print("Target %s saved" % (filepath))
    

#----------------------------------------------------------
#   class CVertex:
#----------------------------------------------------------

class CVertex:

    def __init__(self, x, y, z):
        self.co = [x,y,z]
    
    def __repr__(self):
        return ("<CVertex %s %s %s>" % (round(self.co[0]), round(self.co[1]), round(self.co[2])))
        
    def copy(self):
        return CVertex(self.co[0], self.co[1], self.co[2])
                
    def sub(self, v):
        self.co[0] -= v.co[0]
        self.co[1] -= v.co[1]
        self.co[2] -= v.co[2]

    def length(self):
        co = self.co
        return math.sqrt(co[0]*co[0] + co[1]*co[1] + co[2]*co[2])
        
#----------------------------------------------------------
#   Init
#----------------------------------------------------------

theBaseObj = None
theProxy = None

def init():
    global theProxy
    theBaseObj = None
    theProxy = None

    bpy.types.Scene.CTBaseObj = StringProperty()
    bpy.types.Scene.CTConvertMhclo = StringProperty()
    bpy.types.Scene.CTSourceTarget = StringProperty()
    bpy.types.Scene.CTTargetDir = StringProperty()
