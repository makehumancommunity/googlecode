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

"""
Abstract

Convert targets

"""

import bpy
import os
from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper

from mh_utils import globvars as the
from mh_utils import utils
from mh_utils import proxy
from mh_utils import import_obj


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

class VIEW3D_OT_SetBaseButton(bpy.types.Operator):
    bl_idname = "mh.set_base_mhclo"
    bl_label = "Set Base File"
    bl_options = {'UNDO'}

    filename_ext = ".mhclo"
    filter_glob = StringProperty(default="*.mhclo", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for base mhclo", 
        maxlen= 1024, default= "")

    def execute(self, context):
        global theProxy
        context.scene.CTBase = self.filepath
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

    if not theProxy:
        if scn.CTBase:
            print("Reading %s" % scn.CTBase)
            theProxy = proxy.CProxy()
            theProxy.read(scn.CTBase)
        else:
            raise NameError("No mhclo path selected")
            
    srcFile = scn.CTSourceTarget
    trgFile = os.path.join(scn.CTTargetDir, os.path.basename(srcFile))
    
    print("Proxy", theProxy)
    print("Source", srcFile)
    print("Target", trgFile)
    
    srcVerts = readTarget(srcFile)
    trgVerts = makeVerts(len(theProxy.verts))    
    theProxy.update(srcVerts, trgVerts)
    writeTarget(trgFile, trgVerts)


def readTarget(filepath):
    fp = open(filepath, "rU")
    verts = {}
    for line in fp:
        words = line.split()
        if len(words) == 4:
            x,y,z = float(words[1]), float(words[2]), float(words[3])
            verts[int(words[0])] = CVertex(x,y,z)
    fp.close()            
    return verts            


def makeVerts(nVerts):
    
    for n in range(nVerts)    



theProxy = None

#----------------------------------------------------------
#   Init
#----------------------------------------------------------

def init():
    global theProxy
    theProxy = None

    bpy.types.Scene.CTBase = StringProperty()
    bpy.types.Scene.CTSourceTarget = StringProperty()
    bpy.types.Scene.CTTargetDir = StringProperty()
