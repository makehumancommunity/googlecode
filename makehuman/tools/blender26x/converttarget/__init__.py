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

bl_info = {
    "name": "Convert Target",
    "author": "Thomas Larsson",
    "version": "0.1",
    "blender": (2, 6, 5),
    "location": "View3D > Properties > Make Target",
    "description": "Convert MakeHuman Target To New Mesh",
    "warning": "",
    'wiki_url': "http://www.makehuman.org/node/223",
    "category": "MakeHuman"}

if "bpy" in locals():
    print("Reloading converttarget")
    import imp    
    imp.reload(mh_utils)
    imp.reload(proxy)
    imp.reload(convert)
else:
    print("Loading converttarget")
    import bpy
    import os
    from bpy.props import *
    from bpy_extras.io_utils import ImportHelper, ExportHelper

    import mh_utils
    from mh_utils import proxy
    from . import convert
            
#----------------------------------------------------------
#   class ConvertTargetPanel(bpy.types.Panel):
#----------------------------------------------------------

class ConvertTargetPanel(bpy.types.Panel):
    bl_label = "Convert Target"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        
        layout.operator("mh.set_base_obj")
        layout.prop(scn, "CTBaseObj", text="")

        layout.separator()
        layout.operator("mh.set_convert_mhclo")
        layout.prop(scn, "CTConvertMhclo", text="")

        layout.separator()
        layout.operator("mh.set_target_dir")
        layout.prop(scn, "CTTargetDir", text="")

        layout.separator()
        layout.operator("mh.set_source_target")
        layout.prop(scn, "CTSourceTarget", text="")

        layout.separator()
        layout.operator("mh.convert_target")


#----------------------------------------------------------
#   Register
#----------------------------------------------------------
 
def register():
    mh_utils.init()
    convert.init()
    bpy.utils.register_module(__name__)
  
def unregister():
    bpy.utils.unregister_module(__name__)
 
if __name__ == "__main__":
    register()
