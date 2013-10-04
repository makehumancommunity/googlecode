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
Tool for loading bvh files onto the MHX rig in Blender 2.5x

Place the script in the .blender/scripts/addons dir
Activate the script in the "Add-Ons" tab (user preferences).
Access from UI panel (N-key) when MHX rig is active.

Alternatively, run the script in the script editor (Alt-P), and access from UI panel.
"""

bl_info = {
    "name": "MakeWalk",
    "author": "Thomas Larsson",
    "version": "0.917",
    "blender": (2, 6, 8),
    "location": "View3D > Tools > MakeWalk",
    "description": "Mocap tool for MakeHuman character",
    "warning": "",
    'wiki_url': "http://www.makehuman.org/doc/node/makewalk_user_interface.html",
    "category": "MakeHuman"}

# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    print("Reloading MakeWalk")
    import imp
    imp.reload(utils)
    imp.reload(io_json)
    imp.reload(mcp)
    imp.reload(props)
    imp.reload(t_pose)
    imp.reload(armature)
    imp.reload(source)
    imp.reload(target)
    imp.reload(load)
    imp.reload(retarget)
    imp.reload(fkik)
    imp.reload(toggle)
    imp.reload(simplify)
    imp.reload(action)
    imp.reload(loop)
    imp.reload(edit)
    imp.reload(floor)
else:
    print("Loading MakeWalk")
    import bpy, os
    from bpy_extras.io_utils import ImportHelper
    from bpy.props import *

    from . import utils
    from . import io_json
    from . import mcp
    from . import props
    from . import t_pose
    from . import armature
    from . import source
    from . import target
    from . import load
    from . import retarget
    from . import fkik
    from . import toggle
    from . import simplify
    from . import action
    from . import loop
    from . import edit
    from . import floor


def inset(layout):
    split = layout.split(0.05)
    split.label("")
    return split.column()

########################################################################
#
#   class MainPanel(bpy.types.Panel):
#

class MainPanel(bpy.types.Panel):
    bl_label = "MakeWalk v %s: Main" % bl_info["version"]
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        layout = self.layout
        ob = context.object
        scn = context.scene
        if ob and ob.type == 'ARMATURE':
            layout.operator("mcp.load_and_retarget")
            layout.separator()
            layout.prop(scn, "McpStartFrame")
            layout.prop(scn, "McpEndFrame")
            layout.separator()
            layout.prop(scn, "McpShowDetailSteps")
            if scn.McpShowDetailSteps:
                ins = inset(layout)
                ins.operator("mcp.load_bvh")
                ins.operator("mcp.rename_bvh")
                ins.operator("mcp.load_and_rename_bvh")

                ins.separator()
                ins.operator("mcp.retarget_mhx")

                ins.separator()
                ins.operator("mcp.simplify_fcurves")
                ins.operator("mcp.rescale_fcurves")

        else:
            layout.operator("mcp.load_bvh")
            layout.separator()
            layout.prop(scn, "McpStartFrame")
            layout.prop(scn, "McpEndFrame")

########################################################################
#
#   class OptionsPanel(bpy.types.Panel):
#

class OptionsPanel(bpy.types.Panel):
    bl_label = "MakeWalk: Options"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'ARMATURE':
            return True

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        ob = context.object

        layout.label("SubSample and Rescale")
        layout.prop(scn, "McpDefaultSS")
        if not scn.McpDefaultSS:
            layout.prop(scn, "McpSubsample")
            layout.prop(scn, "McpSSFactor")
        layout.prop(scn, "McpRescale")
        layout.prop(scn, "McpRescaleFactor")

        layout.separator()
        layout.prop(scn, "McpAutoScale")
        layout.prop(scn, "McpBvhScale")
        layout.prop(scn, "McpMakeHumanTPose")
        layout.prop(scn, 'McpAutoSourceRig')
        layout.prop(scn, 'McpAutoTargetRig')

        layout.separator()
        layout.label("Simplification")
        layout.prop(scn, "McpDoSimplify")
        layout.prop(scn, "McpErrorLoc")
        layout.prop(scn, "McpErrorRot")
        layout.prop(scn, "McpSimplifyVisible")
        layout.prop(scn, "McpSimplifyMarkers")



        return

        layout.separator()
        layout.label("Toggle constraints")
        row = layout.row()
        row.label("Limit constraints")
        if ob.McpLimitsOn:
            row.operator("mcp.toggle_limits", text="ON").mute=True
        else:
            row.operator("mcp.toggle_limits", text="OFF").mute=False
        row = layout.row()
        row.label("Child-of constraints")
        if ob.McpChildOfsOn:
            row.operator("mcp.toggle_childofs", text="ON").mute=True
        else:
            row.operator("mcp.toggle_childofs", text="OFF").mute=False


########################################################################
#
#   class EditPanel(bpy.types.Panel):
#

class EditPanel(bpy.types.Panel):
    bl_label = "MakeWalk: Edit Actions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'ARMATURE':
            return True

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        ob = context.object

        if mcp.editConfirm:
            confirmPanel(layout, mcp.editConfirm, mcp.editString)
            return

        layout.label("Inverse Kinematics")
        row = layout.row()
        row.prop(scn, "McpFkIkArms")
        row.prop(scn, "McpFkIkLegs")
        layout.operator("mcp.transfer_to_ik")
        layout.operator("mcp.transfer_to_fk")
        layout.operator("mcp.clear_animation", text="Clear IK Animation").type = "IK"
        layout.operator("mcp.clear_animation", text="Clear FK Animation").type = "FK"
        #layout.operator("mcp.print_hands")

        layout.separator()
        layout.label("Global Edit")
        layout.operator("mcp.shift_bone")
        row = layout.row()
        row.prop(scn, "McpFixX")
        row.prop(scn, "McpFixY")
        row.prop(scn, "McpFixZ")
        layout.operator("mcp.fix_bone")
        layout.prop(scn, "McpRescaleFactor")
        layout.operator("mcp.rescale_fcurves")

        layout.separator()
        layout.label("Displace Animation")
        layout.operator("mcp.start_edit")
        layout.operator("mcp.undo_edit").answer=""
        row = layout.row()
        row.operator("mcp.insert_loc")
        row.operator("mcp.insert_rot")
        row.operator("mcp.insert_locrot")
        layout.operator("mcp.confirm_edit")

        layout.separator()
        layout.label("Floor")
        row = layout.row()
        row.prop(scn, "McpFloorLeft")
        row.prop(scn, "McpFloorRight")
        row.prop(scn, "McpFloorHips")
        layout.operator("mcp.floor_foot")

        layout.separator()
        layout.label("Loop Animation")
        layout.prop(scn, "McpLoopBlendRange")
        row = layout.row()
        row.prop(scn, "McpLoopLoc")
        row.prop(scn, "McpLoopRot")
        layout.prop(scn, "McpLoopInPlace")
        if scn.McpLoopInPlace:
            layout.prop(scn, "McpLoopZInPlace")
        layout.operator("mcp.loop_fcurves")

        layout.separator()
        layout.label("Repeat Animation")
        layout.prop(scn, "McpRepeatNumber")
        layout.operator("mcp.repeat_fcurves")

        layout.separator()
        layout.label("Stitch Animations")
        layout.operator("mcp.update_action_list")
        layout.prop(scn, "McpFirstAction")
        row = layout.row()
        row.prop(scn, "McpFirstEndFrame")
        row.operator("mcp.set_current_action").prop = "McpFirstAction"
        layout.prop(scn, "McpSecondAction")
        row = layout.row()
        row.prop(scn, "McpSecondStartFrame")
        row.operator("mcp.set_current_action").prop = "McpSecondAction"
        layout.prop(scn, "McpLoopBlendRange")
        layout.prop(scn, "McpActionTarget")
        layout.prop(scn, "McpOutputActionName")
        layout.operator("mcp.stitch_actions")

########################################################################
#
#    class MhxSourceBonesPanel(bpy.types.Panel):
#

class MhxSourceBonesPanel(bpy.types.Panel):
    bl_label = "MakeWalk: Source armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        rig = context.object

        if not source.isSourceInited(scn):
            layout.operator("mcp.init_sources", text="Init Source Panel")
            return
        layout.operator("mcp.init_sources", text="Reinit Source Panel")
        layout.prop(scn, 'McpAutoSourceRig')
        layout.prop(scn, "McpSourceRig")

        if scn.McpSourceRig:
            amt = mcp.sourceArmatures[scn.McpSourceRig]
            if amt:
                bones = amt.boneNames
                box = layout.box()
                for boneText in target.TargetBoneNames:
                    if not boneText:
                        box.separator()
                        continue
                    (mhx, text) = boneText
                    bone = source.findSourceKey(mhx, bones)
                    if bone:
                        row = box.row()
                        row.label(text)
                        row.label(bone)

########################################################################
#
#    class MhxTargetBonesPanel(bpy.types.Panel):
#

class MhxTargetBonesPanel(bpy.types.Panel):
    bl_label = "MakeWalk: Target armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE')

    def draw(self, context):
        layout = self.layout
        rig = context.object
        scn = context.scene

        if not target.isTargetInited(scn):
            layout.operator("mcp.init_targets", text="Init Target Panel")
            return
        layout.operator("mcp.init_targets", text="Reinit Target Panel")
        layout.separator()
        layout.prop(scn, "McpTargetRig")
        layout.prop(scn, 'McpAutoTargetRig')
        layout.prop(rig, "MhReverseHip")
        layout.separator()
        layout.operator("mcp.get_target_rig")
        layout.operator("mcp.set_t_pose")
        layout.separator()
        layout.prop(scn, "McpSaveTargetTPose")
        layout.operator("mcp.save_target_file")
        layout.separator()

        if scn.McpTargetRig:
            (bones, ikBones, tpose) = mcp.targetInfo[scn.McpTargetRig]

            layout.label("FK bones")
            box = layout.box()
            for boneText in target.TargetBoneNames:
                if not boneText:
                    box.separator()
                    continue
                (mhx, text) = boneText
                bone = target.findTargetKey(mhx, bones)
                row = box.row()
                row.label(text)
                if bone:
                    row.label(bone)
                else:
                    row.label("-")

            if ikBones:
                row = layout.row()
                row.label("IK bone")
                row.label("FK bone")
                box = layout.box()
                for (ikBone, fkBone) in ikBones:
                    row = box.row()
                    row.label(ikBone)
                    row.label(fkBone)
        return

########################################################################
#
#   class UtilityPanel(bpy.types.Panel):
#

class UtilityPanel(bpy.types.Panel):
    bl_label = "MakeWalk: Utilities"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'ARMATURE':
            return True

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        ob = context.object

        if mcp.utilityConfirm:
            confirmPanel(layout, mcp.utilityConfirm, mcp.utilityString)
            return

        layout.label("Default Settings")
        #layout.operator("mcp.init_interface")
        layout.operator("mcp.save_defaults")
        layout.operator("mcp.load_defaults")

        layout.separator()
        layout.label("Manage Actions")
        layout.prop_menu_enum(context.scene, "McpActions")
        layout.prop(scn, 'McpFilterActions')
        layout.operator("mcp.update_action_list")
        layout.operator("mcp.set_current_action").prop = 'McpActions'
        #layout.prop(scn, "McpReallyDelete")
        layout.operator("mcp.delete").answer=""
        layout.operator("mcp.delete_hash")

        layout.separator()
        layout.operator("mcp.clear_temp_props")

        layout.separator()
        layout.label("T-pose")
        layout.operator("mcp.set_t_pose")
        layout.operator("mcp.clear_t_pose")
        layout.operator("mcp.load_t_pose")
        layout.operator("mcp.save_t_pose")

        layout.separator()
        layout.label("Rest Pose")
        layout.operator("mcp.rest_current_pose")
        layout.operator("mcp.rest_t_pose")
        layout.operator("mcp.rest_default_pose")

        return
        layout.operator("mcp.copy_angles_fk_ik")

        layout.separator()
        layout.label("Batch conversion")
        layout.prop(scn, "McpDirectory")
        layout.prop(scn, "McpPrefix")
        layout.operator("mcp.batch")

#
#    Confirm
#

mcp.editConfirm = None
mcp.editString = "?"
mcp.utilityConfirm = None
mcp.utilityString = "?"

def confirmPanel(layout, confirm, string):
    layout.label(string)
    layout.operator(confirm, text="yes").answer="yes"
    layout.operator(confirm, text="no").answer="no"
    return


#
#    init
#

props.initInterface(bpy.context)

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()


