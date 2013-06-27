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
#
# Abstract
# Utility for making clothes to MH characters.
#

bl_info = {
    "name": "Make UVs",
    "author": "Thomas Larsson",
    "version": "0.100",
    "blender": (2, 6, 7),
    "location": "View3D > Properties > Make MH UVs",
    "description": "Make UVs for MakeHuman characters",
    "warning": "",
    'wiki_url': "http://www.makehuman.org/node/228",
    "category": "MakeHuman"}


if "bpy" in locals():
    print("Reloading makeuvs v %s" % bl_info["version"])
    import imp
    imp.reload(makeclothes)
    imp.reload(makeuvs)
else:
    print("Loading makeuvs v %s" % bl_info["version"])
    import bpy
    import os
    from bpy.props import *
    import maketarget
    from maketarget.error import MHError, handleMHError
    import makeclothes
    from . import makeuvs


def inset(layout):
    split = layout.split(0.05)
    split.label("")
    return split.column()


class MakeUVsPanel(bpy.types.Panel):
    bl_label = "Make UVs v %s" % bl_info["version"]
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH')

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        layout.prop(scn, "MUVShowSettings")
        if scn.MUVShowSettings:
            maketarget.settings.drawDirectories(inset(layout), scn, "MhUvsDir")

        layout.prop(scn, "MUVShowUVProject")
        if scn.MUVShowUVProject:
            ins = inset(layout)
            ins.operator("mhuv.recover_seams")
            ins.operator("mhuv.set_seams")
            ins.operator("mhuv.project_uvs")
            ins.operator("mhuv.reexport_mhclo")
            ins.separator()

        layout.operator("mhuv.export_uvs")
        layout.operator("mhuv.export_helper_uvs")

        layout.prop(scn, "MUVShowLicense")
        if scn.MUVShowLicense:
            ins = inset(layout)
            ins.prop(scn, "MCAuthor")
            ins.prop(scn, "MCLicense")
            ins.prop(scn, "MCHomePage")

#
#    class OBJECT_OT_RecoverSeamsButton(bpy.types.Operator):
#

class OBJECT_OT_RecoverSeamsButton(bpy.types.Operator):
    bl_idname = "mhuv.recover_seams"
    bl_label = "Recover seams"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            makeuvs.recoverSeams(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}


class OBJECT_OT_SetSeamsButton(bpy.types.Operator):
    bl_idname = "mhuv.set_seams"
    bl_label = "Set seams"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            makeuvs.setSeams(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#    class OBJECT_OT_ProjectUVsButton(bpy.types.Operator):
#

class OBJECT_OT_ProjectUVsButton(bpy.types.Operator):
    bl_idname = "mhuv.project_uvs"
    bl_label = "Project UVs"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            (human, clothing) = makeuvs.getObjectPair(context)
            makeuvs.unwrapObject(clothing, context)
            makeuvs.projectUVs(human, clothing, context)
            print("UVs projected")
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#   class OBJECT_OT_ReexportMhcloButton(bpy.types.Operator):
#

class OBJECT_OT_ReexportMhcloButton(bpy.types.Operator):
    bl_idname = "mhuv.reexport_mhclo"
    bl_label = "Reexport Mhclo file"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            makeuvs.reexportMhclo(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#   class OBJECT_OT_SplitHumanButton(bpy.types.Operator):
#

class OBJECT_OT_SelectHelpersButton(bpy.types.Operator):
    bl_idname = "mhuv.select_helpers"
    bl_label = "Select Helpers"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            makeuvs.selectHelpers(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}


#
#    class OBJECT_OT_ExportUVsButton(bpy.types.Operator):
#

class OBJECT_OT_ExportUVsButton(bpy.types.Operator):
    bl_idname = "mhuv.export_uvs"
    bl_label = "Export UVs"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            makeuvs.exportUVs(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}


class OBJECT_OT_ExportHelperUVsButton(bpy.types.Operator):
    bl_idname = "mhuv.export_helper_uvs"
    bl_label = "Export Helper UVs"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            makeuvs.exportHelperUVs(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}


#
#    Init and register
#

def register():
    makeuvs.initInterface()
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

