""" 
**Project Name:**	  MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**	http://code.google.com/p/makehuman/

**Authors:**		   Thomas Larsson

**Copyright(c):**	  MakeHuman Team 2001-2010

**Licensing:**		 GPL3 (see also http://sites.google.com/site/makehumandocs/licensing)

**Coding Standards:**  See http://sites.google.com/site/makehumandocs/developers-guide

Abstract
Lipsync for the MHX rig and Blender 2.5x.
Version 0.3

"""

bl_info = {
	'name': 'MakeHuman pose tool',
	'author': 'Thomas Larsson',
	'version': '0.6',
	'blender': (2, 5, 6),
	"api": 34076,
	"location": "View3D > UI panel > MHX Lipsync, MHX Expressions, MHX Pose",
	"description": "Lipsync, expression, pose tool for the MHX rig",
	"warning": "",
	"category": "3D View"}

"""
Run from text window. 
Access from UI panel (N-key) when MHX rig is active.
"""

MAJOR_VERSION = 0
MINOR_VERSION = 5
BLENDER_VERSION = (2, 56, 0)

import bpy, os, mathutils
from mathutils import *
from bpy.props import *

theRig = None
theMesh = None

###################################################################################	
#
#	Lipsync panel
#
###################################################################################	

#
#	visemes
#

stopStaringVisemes = ({
	'Rest' : [
		('PMouth', (0,0)), 
		('PUpLip', (0,-0.1)), 
		('PLoLip', (0,0.1)), 
		('PJaw', (0,0.05)), 
		('PTongue', (0,0.0))], 
	'Etc' : [
		('PMouth', (0,0)),
		('PUpLip', (0,-0.1)),
		('PLoLip', (0,0.1)),
		('PJaw', (0,0.15)),
		('PTongue', (0,0.0))], 
	'MBP' : [('PMouth', (-0.3,0)),
		('PUpLip', (0,1)),
		('PLoLip', (0,0)),
		('PJaw', (0,0.1)),
		('PTongue', (0,0.0))], 
	'OO' : [('PMouth', (-1.5,0)),
		('PUpLip', (0,0)),
		('PLoLip', (0,0)),
		('PJaw', (0,0.2)),
		('PTongue', (0,0.0))], 
	'O' : [('PMouth', (-1.1,0)),
		('PUpLip', (0,0)),
		('PLoLip', (0,0)),
		('PJaw', (0,0.5)),
		('PTongue', (0,0.0))], 
	'R' : [('PMouth', (-0.9,0)),
		('PUpLip', (0,-0.2)),
		('PLoLip', (0,0.2)),
		('PJaw', (0,0.2)),
		('PTongue', (0,0.0))], 
	'FV' : [('PMouth', (0,0)),
		('PUpLip', (0,0)),
		('PLoLip', (0,-0.8)),
		('PJaw', (0,0.1)),
		('PTongue', (0,0.0))], 
	'S' : [('PMouth', (0,0)),
		('PUpLip', (0,-0.2)),
		('PLoLip', (0,0.2)),
		('PJaw', (0,0.05)),
		('PTongue', (0,0.0))], 
	'SH' : [('PMouth', (-0.6,0)),
		('PUpLip', (0,-0.5)),
		('PLoLip', (0,0.5)),
		('PJaw', (0,0)),
		('PTongue', (0,0.0))], 
	'EE' : [('PMouth', (0.3,0)),
		('PUpLip', (0,-0.3)),
		('PLoLip', (0,0.3)),
		('PJaw', (0,0.025)),
		('PTongue', (0,0.0))], 
	'AH' : [('PMouth', (-0.1,0)),
		('PUpLip', (0,-0.4)),
		('PLoLip', (0,0)),
		('PJaw', (0,0.35)),
		('PTongue', (0,0.0))], 
	'EH' : [('PMouth', (0.1,0)),
		('PUpLip', (0,-0.2)),
		('PLoLip', (0,0.2)),
		('PJaw', (0,0.2)),
		('PTongue', (0,0.0))], 
	'TH' : [('PMouth', (0,0)),
		('PUpLip', (0,-0.5)),
		('PLoLip', (0,0.5)),
		('PJaw', (-0.2,0.1)),
		('PTongue', (0,-0.6))], 
	'L' : [('PMouth', (0,0)),
		('PUpLip', (0,-0.2)),
		('PLoLip', (0,0.2)),
		('PJaw', (0.2,0.2)),
		('PTongue', (0,-0.8))], 
	'G' : [('PMouth', (0,0)),
		('PUpLip', (0,-0.1)),
		('PLoLip', (0,0.1)),
		('PJaw', (-0.3,0.1)),
		('PTongue', (0,-0.6))], 

	'Blink' : [('PUpLid', (0,1.0)), ('PLoLid', (0,-1.0))], 
	'UnBlink' : [('PUpLid', (0,0)), ('PLoLid', (0,0))], 
})

bodyLanguageVisemes = ({
	'Rest' : [
		('PMouth', (0,0)), 
		('PMouthMid', (0,-0.6)), 
		('PUpLipMid', (0,0)), 
		('PLoLipMid', (0,0)), 
		('PJaw', (0,0)), 
		('PTongue', (0,0))], 
	'Etc' : [
		('PMouth', (0,0)), 
		('PMouthMid', (0,-0.4)), 
		('PUpLipMid', (0,0)), 
		('PLoLipMid', (0,0)), 
		('PJaw', (0,0)), 
		('PTongue', (0,0))], 
	'MBP' : [
		('PMouth', (0,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,0)), 
		('PLoLipMid', (0,0)), 
		('PJaw', (0,0)), 
		('PTongue', (0,0))], 
	'OO' : [
		('PMouth', (-1.0,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,0)), 
		('PLoLipMid', (0,0)), 
		('PJaw', (0,0.4)), 
		('PTongue', (0,0))], 
	'O' : [
		('PMouth', (-0.9,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,0)), 
		('PLoLipMid', (0,0)), 
		('PJaw', (0,0.8)), 
		('PTongue', (0,0))], 
	'R' : [
		('PMouth', (-0.5,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,-0.2)), 
		('PLoLipMid', (0,0.2)), 
		('PJaw', (0,0)), 
		('PTongue', (0,0))], 
	'FV' : [
		('PMouth', (-0.2,0)), 
		('PMouthMid', (0,1.0)), 
		('PUpLipMid', (0,0)), 
		('PLoLipMid', (-0.6,-0.3)), 
		('PJaw', (0,0)), 
		('PTongue', (0,0))], 
	'S' : [
		('PMouth', (0,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,-0.5)), 
		('PLoLipMid', (0,0.7)), 
		('PJaw', (0,0)), 
		('PTongue', (0,0))], 
	'SH' : [
		('PMouth', (-0.8,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,-1.0)), 
		('PLoLipMid', (0,1.0)), 
		('PJaw', (0,0)), 
		('PTongue', (0,0))], 
	'EE' : [
		('PMouth', (0.2,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,-0.6)), 
		('PLoLipMid', (0,0.6)), 
		('PJaw', (0,0.05)), 
		('PTongue', (0,0))], 
	'AH' : [
		('PMouth', (0,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,-0.4)), 
		('PLoLipMid', (0,0)), 
		('PJaw', (0,0.7)), 
		('PTongue', (0,0))], 
	'EH' : [
		('PMouth', (0,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,-0.5)), 
		('PLoLipMid', (0,0.6)), 
		('PJaw', (0,0.25)), 
		('PTongue', (0,0))], 
	'TH' : [
		('PMouth', (0,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,0)), 
		('PLoLipMid', (0,0)), 
		('PJaw', (0,0.2)), 
		('PTongue', (1.0,1.0))], 
	'L' : [
		('PMouth', (0,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,-0.5)), 
		('PLoLipMid', (0,0.5)), 
		('PJaw', (0,-0.2)), 
		('PTongue', (1.0,1.0))], 
	'G' : [
		('PMouth', (0,0)), 
		('PMouthMid', (0,0)), 
		('PUpLipMid', (0,-0.5)), 
		('PLoLipMid', (0,0.5)), 
		('PJaw', (0,-0.2)), 
		('PTongue', (-1.0,0))], 

	'Blink' : [('PUpLid', (0,1.0)), ('PLoLid', (0,-1.0))], 
	'UnBlink' : [('PUpLid', (0,0)), ('PLoLid', (0,0))], 
})

#
#	mohoVisemes
#	magpieVisemes
#

mohoVisemes = dict({
	'rest' : 'Rest', 
	'etc' : 'Etc', 
	'AI' : 'AH', 
	'O' : 'O', 
	'U' : 'OO', 
	'WQ' : 'AH', 
	'L' : 'L', 
	'E' : 'EH', 
	'MBP' : 'MBP', 
	'FV' : 'FV', 
})

magpieVisemes = dict({
	"CONS" : "t,d,k,g,T,D,s,z,S,Z,h,n,N,j,r,tS", 
	"AI" : "i,&,V,aU,I,0,@,aI", 
	"E" : "eI,3,e", 
	"O" : "O,@U,oI", 
	"UW" : "U,u,w", 
	"MBP" : "m,b,p", 
	"L" : "l", 
	"FV" : "f,v", 
	"Sh" : "dZ", 
})

#
#	setViseme(context, vis, setKey, frame):
#	setBoneLocation(context, pbone, loc, mirror, setKey, frame):
#

def getVisemeSet(context):
	if context.scene['MhxBodyLanguage'] == True:
		return bodyLanguageVisemes
	else:
		return stopStaringVisemes

def setViseme(context, vis, setKey, frame):
	global theRig
	pbones = theRig.pose.bones
	try:
		scale = pbones['PFace'].bone.length
	except:
		return
	visemes = getVisemeSet(context)
	for (b, (x, z)) in visemes[vis]:
		loc = mathutils.Vector((float(x),0,float(z)))
		try:
			pb = pbones[b]
		except:
			pb = None
			
		if pb:
			setBoneLocation(context, pb, scale, loc, False, setKey, frame)
		else:
			setBoneLocation(context, pbones[b+'_L'], scale, loc, False, setKey, frame)
			setBoneLocation(context, pbones[b+'_R'], scale, loc, True, setKey, frame)
	return

def setBoneLocation(context, pb, scale, loc, mirror, setKey, frame):
	if mirror:
		loc[0] = -loc[0]
	pb.location = loc*scale*0.2
	if setKey or context.scene['MhxSyncAutoKeyframe']:
		for n in range(3):
			pb.keyframe_insert('location', index=n, frame=frame, group=pb.name)
	return

#
#	openFile(context, filepath):
#	readMoho(context, filepath, offs):
#	readMagpie(context, filepath, offs):
#

def openFile(context, filepath):
	(path, fileName) = os.path.split(filepath)
	(name, ext) = os.path.splitext(fileName)
	return open(filepath, "rU")

def readMoho(context, filepath, offs):
	context.scene.objects.active = theRig
	bpy.ops.object.mode_set(mode='POSE')	
	fp = openFile(context, filepath)		
	for line in fp:
		words= line.split()
		if len(words) < 2:
			pass
		else:
			vis = mohoVisemes[words[1]]
			setViseme(context, vis, True, int(words[0])+offs)
	fp.close()
	setInterpolation(context.object)
	print("Moho file %s loaded" % filepath)
	return

def readMagpie(context, filepath, offs):
	context.scene.objects.active = theRig
	bpy.ops.object.mode_set(mode='POSE')	
	fp = openFile(context, filepath)		
	for line in fp: 
		words= line.split()
		if len(words) < 3:
			pass
		elif words[2] == 'X':
			vis = magpieVisemes[words[3]]
			setViseme(context, vis, True, int(words[0])+offs)
	fp.close()
	setInterpolation(context.object)
	print("Magpie file %s loaded" % filepath)
	return

#
#	setInterpolation(rig):
#

def setInterpolation(rig):
	if not rig.animation_data:
		return
	act = rig.animation_data.action
	if not act:
		return
	for fcu in act.fcurves:
		for pt in fcu.keyframe_points:
			pt.interpolation = 'LINEAR'
		fcu.extrapolation = 'CONSTANT'
	return
	
# Define viseme buttons

def defineVisemeButtons():
	visemes = bodyLanguageVisemes
	for vis in visemes.keys():
		expr = (
"class VIEW3D_OT_Mhx%sButton(bpy.types.Operator):\n" % vis +
"	bl_idname = 'mhx.pose_%s'\n" % vis.lower() +
"	bl_label = '%s'\n" % vis +	
"	def invoke(self, context, event):\n" +
"		global bpy, mathutils\n" +
"		setViseme(context, '%s', False, context.scene.frame_current)\n" % vis +
"		return{'FINISHED'}\n"
		)
		# print(expr)
		exec(expr, globals(), locals())
	return

# 
#	class VIEW3D_OT_MhxLoadMohoButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxLoadMohoButton(bpy.types.Operator):
	bl_idname = "mhx.pose_load_moho"
	bl_label = "Moho (.dat)"
	filepath = StringProperty(name="File Path", description="File path used for importing the file", maxlen= 1024, default= "")
	startFrame = IntProperty(name="Start frame", description="First frame to import", default=1)

	def execute(self, context):
		import bpy, os, mathutils
		readMoho(context, self.properties.filepath, self.properties.startFrame-1)		
		return{'FINISHED'}	

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}	

#
#	class VIEW3D_OT_MhxLoadMagpieButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxLoadMagpieButton(bpy.types.Operator):
	bl_idname = "mhx.pose_load_magpie"
	bl_label = "Magpie (.mag)"
	filepath = StringProperty(name="File Path", description="File path used for importing the file", maxlen= 1024, default= "")
	startFrame = IntProperty(name="Start frame", description="First frame to import", default=1)

	def execute(self, context):
		import bpy, os, mathutils
		readMagpie(context, self.properties.filepath, self.properties.startFrame-1)		
		return{'FINISHED'}	

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}	

#
#	class MhxLipsyncPanel(bpy.types.Panel):
#

class MhxLipsyncPanel(bpy.types.Panel):
	bl_label = "MHX Lipsync"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	@classmethod
	def poll(cls, context):
		return context.object

	def draw(self, context):
		setGlobals(context)
		layout = self.layout
		layout.operator("mhx.pose_init_interface")
		
		if theRig:
			layout.separator()
			layout.prop(context.scene, 'MhxSyncAutoKeyframe')
			layout.prop(context.scene, 'MhxBodyLanguage')
			layout.label(text="Visemes")
			row = layout.row()
			row.operator("mhx.pose_rest")
			row.operator("mhx.pose_etc")
			row.operator("mhx.pose_ah")
			row = layout.row()
			row.operator("mhx.pose_mbp")
			row.operator("mhx.pose_oo")
			row.operator("mhx.pose_o")
			row = layout.row()
			row.operator("mhx.pose_r")
			row.operator("mhx.pose_fv")
			row.operator("mhx.pose_s")
			row = layout.row()
			row.operator("mhx.pose_sh")
			row.operator("mhx.pose_ee")
			row.operator("mhx.pose_eh")
			row = layout.row()
			row.operator("mhx.pose_th")
			row.operator("mhx.pose_l")
			row.operator("mhx.pose_g")
			layout.separator()
			row = layout.row()
			row.operator("mhx.pose_blink")
			row.operator("mhx.pose_unblink")
			layout.label(text="Load file")
			row = layout.row()
			row.operator("mhx.pose_load_moho")
			row.operator("mhx.pose_load_magpie")


###################################################################################	
#
#	Expression panel
#
###################################################################################	

#
#	Expressions - the same as in read_expression.py
#

Expressions = [
	'smile',
	'hopeful',
	'innocent',
	'tender',
	'seductive',

	'grin',
	'excited',
	'ecstatic',

	'proud',
	'pleased',
	'amused',
	'laughing1',
	'laughing2',

	'so-so',
	'blue',
	'depressed',
	'sad',
	'distressed',
	'crying',
	'pain',

	'disappointed',
	'frustrated',
	'stressed',
	'worried',
	'scared',
	'terrified',

	'shy',
	'guilty',
	'embarassed',
	'relaxed',
	'peaceful',
	'refreshed',

	'lazy',
	'bored',
	'tired',
	'drained',
	'sleepy',
	'groggy',

	'curious',
	'surprised',
	'impressed',
	'puzzled',
	'shocked',
	'frown',
	'upset',
	'angry',
	'enraged',

	'skeptical',
	'vindictive',
	'pout',
	'furious',
	'grumpy',
	'arrogant',
	'sneering',
	'haughty',
	'disgusted',
]


#
#	meshHasExpressions(mesh):
#	rigHasExpressions(rig):
#
	
def meshHasExpressions(mesh):
	return ('guilty' in mesh.data.shape_keys.keys.keys())

def rigHasExpressions(rig):
	return ('Pguilty' in rig.pose.bones.keys())

#
#	class VIEW3D_OT_MhxResetExpressionsButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxResetExpressionsButton(bpy.types.Operator):
	bl_idname = "mhx.pose_reset_expressions"
	bl_label = "Reset expressions"

	def execute(self, context):
		global theMesh
		keys = theMesh.data.shape_keys
		if keys:
			for name in Expressions:
				try:
					keys.keys[name].value = 0.0
				except:
					pass
		print("Expressions reset")
		return{'FINISHED'}	

#
#	class VIEW3D_OT_MhxResetBoneExpressionsButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxResetBoneExpressionsButton(bpy.types.Operator):
	bl_idname = "mhx.pose_reset_bone_expressions"
	bl_label = "Reset expressions"

	def execute(self, context):
		global theRig
		pbones = theRig.pose.bones
		if pbones:
			for name in Expressions:
				try:
					pb = pbones['P%s' % name]
					pb.location[1] = 0.0
				except:
					pass
		print("Expressions reset")
		return{'FINISHED'}
		
#
#	createExpressionDrivers(context):	
#
#	class VIEW3D_OT_MhxCreateExpressionDriversButton(bpy.types.Operator):
#

def createExpressionDrivers(context):		
	global theMesh, theRig
	keys = theMesh.data.shape_keys
	if keys:
		context.scene.objects.active = theRig
		bpy.ops.object.mode_set(mode = 'EDIT')
		ebones = theRig.data.edit_bones		
		pface = ebones['PFace']
		layers = 32*[False]
		layers[31] = True
		
		for name in Expressions:
			eb = ebones.new("P%s" % name)
			eb.head = pface.head
			eb.tail = pface.tail
			eb.parent = pface
			eb.layers = layers

		bpy.ops.object.mode_set(mode = 'POSE')
		for name in Expressions:			
			try:
				createExpressionDriver(name, keys)
			except:
				pass
	return
				
def createExpressionDriver(name, keys):
	global theRig
	print("Create driver %s" % name)
	fcu = keys.keys[name].driver_add('value')

	drv = fcu.driver
	drv.type = 'AVERAGE'
	drv.show_debug_info = True

	var = drv.variables.new()
	var.name = 'x'
	var.type = 'TRANSFORMS'
	
	trg = var.targets[0]
	trg.id = theRig
	trg.transform_type = 'LOC_Y'
	trg.bone_target = 'P%s' % name
	trg.use_local_space_transform = True
	
	#fmod = fcu.modifiers.new('GENERATOR')
	fmod = fcu.modifiers[0]
	fmod.coefficients = (0, 1.0)
	fmod.show_expanded = True
	fmod.mode = 'POLYNOMIAL'
	fmod.mute = False
	fmod.poly_order = 1

	return
	
class VIEW3D_OT_MhxCreateExpressionDriversButton(bpy.types.Operator):
	bl_idname = "mhx.pose_create_drivers"
	bl_label = "Create drivers"

	def execute(self, context):
		createExpressionDrivers(context)
		print("ExpressionDrivers created")
		return{'FINISHED'}	

#
#	removeExpressionDrivers(context):		
#	class VIEW3D_OT_MhxRemoveExpressionDriversButton(bpy.types.Operator):
#

def removeExpressionDrivers(context):		
	global theMesh, theRig
	keys = theMesh.data.shape_keys
	if keys:
		context.scene.objects.active = theRig
		bpy.ops.object.mode_set(mode = 'EDIT')
		ebones = theRig.data.edit_bones				
		for name in Expressions:
			try:
				ebones.remove(ebones["P%s" % name])
			except:
				pass
		bpy.ops.object.mode_set(mode = 'POSE')
		for name in Expressions:			
			try:
				keys.keys[name].driver_remove('value')
				print("Removed driver %s" % name)
			except:
				pass
	return

class VIEW3D_OT_MhxRemoveExpressionDriversButton(bpy.types.Operator):
	bl_idname = "mhx.pose_remove_drivers"
	bl_label = "Remove drivers"

	def execute(self, context):
		removeExpressionDrivers(context)
		print("ExpressionDrivers removed")
		return{'FINISHED'}	

#
#	class MhxExpressionsPanel(bpy.types.Panel):
#

class MhxExpressionsPanel(bpy.types.Panel):
	bl_label = "MHX Expressions"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	@classmethod
	def poll(cls, context):
		return context.object

	def draw(self, context):
		setGlobals(context)
		layout = self.layout
		layout.operator("mhx.pose_init_interface")
		
		if theRig and rigHasExpressions(theRig):
			layout.separator()
			layout.label(text="Expressions (driven)")
			layout.operator("mhx.pose_reset_bone_expressions")
			layout.operator("mhx.pose_remove_drivers")
			layout.separator()
			pbones = theRig.pose.bones
			for name in Expressions:
				try:
					pb = pbones['P%s' % name]
					layout.prop(pb, 'location', index=1, text=name)
				except:
					pass
		
		elif theMesh and meshHasExpressions(theMesh):	
			layout.separator()
			layout.label(text="Expressions")
			layout.operator("mhx.pose_reset_expressions")
			layout.operator("mhx.pose_create_drivers")
			layout.separator()
			keys = theMesh.data.shape_keys
			if keys:
				for name in Expressions:
					try:
						datum = keys.keys[name]
						layout.prop(datum, 'value', text=name)
					except:
						pass
		return

###################################################################################	
#
#	Posing panel
#
###################################################################################	

# Property types
D_ENUM = 1
D_INT = 2
D_FLOAT = 3
D_BOOL = 4
D_BOOLINV = 5
D_MULTIVAR = 6

PropTypeName = ['', 'Enum', 'Int', 'Float', 'Bool', 'Bool', '']

#	Parenting
ParentProperties = [
	('RootParent', D_ENUM, ["Floor","Hips","Neck"], 'name="Master", description=""' ),
	('GazeParent', D_ENUM, ['Head','World'], 'name="Gaze", description=""' ),
]

MasterDrivers = [('Floor', 'x==0'), ('Hips', 'x==1'), ('Neck', 'x==2')]

ParentPropDrivers = [
	('Root', 'RootParent', D_ENUM, MasterDrivers),
	('ElbowIK_L', 'RootParent', D_ENUM, MasterDrivers),
	('ElbowIK_R', 'RootParent', D_ENUM, MasterDrivers),
	('WristIK_L', 'RootParent', D_ENUM, MasterDrivers),
	('WristIK_R', 'RootParent', D_ENUM, MasterDrivers),
	('LegIK_L', 'RootParent', D_ENUM, MasterDrivers),
	('LegIK_R', 'RootParent', D_ENUM, MasterDrivers),

	('Gaze', 'GazeParent', D_ENUM, [('Head', 'x==0'), ('World', 'x==1')]),
]

#	Body
BodyProperties = [
	('SpineIK', D_BOOL, False, 'name="Spine IK"'),
]

BodyPropDrivers = [
	('DefSpine3', 'SpineIK', D_BOOL, ['SplineIK']),
	('DefSpine1', 'SpineIK', D_BOOLINV, ['Rot']),
	('DefSpine2', 'SpineIK', D_BOOLINV, ['Rot']),
	('DefSpine3', 'SpineIK', D_BOOLINV, ['Rot']),
]

#	Arm

ArmStates = ['Arm FK', 'Arm IK', 'Elbow FK', 'Elbow IK']
ArmProperties = [
	('LeftArmState', D_ENUM, ArmStates, 'name="Left arm state", description=""' ),
	('RightArmState', D_ENUM, ArmStates, 'name="Right arm state", description=""' ),
	('LeftArmStretch', D_BOOL, False, 'name="Left arm stretch", description=""' ),
	('RightArmStretch', D_BOOL, False, 'name="Right arm stretch", description=""' ),
	('LeftHandFollowsWrist', D_BOOL, True, 'name="Left hand follows wrist", description=""' ),
	('RightHandFollowsWrist', D_BOOL, True, 'name="Right hand follows wrist", description=""' ),
]

ArmRotDrivers = [('RotFK','x==0'), ('RotIK','x>=1')]
UpArmScaleDrivers = [('ScaleIK', '((x1) and (x2==1)) or (x2>=2)')]

ArmPropDrivers = [
	('UpArm1_L', 'LeftArmState', D_ENUM, ArmRotDrivers),
	('UpArm2_L',  ['LeftArmStretch', 'LeftArmState'], D_MULTIVAR, UpArmScaleDrivers),
	('UpArm3_L',  ['LeftArmStretch', 'LeftArmState'], D_MULTIVAR, UpArmScaleDrivers),
	('UpArm3_L', 'LeftArmState', D_ENUM, ArmRotDrivers),
	('LoArm1_L', 'LeftArmState', D_ENUM, ArmRotDrivers),
	('LoArm2_L', 'LeftArmState', D_ENUM, [('ScaleIK', '(x==1) or (x==3)')]),
	('LoArm3_L', 'LeftArmState', D_ENUM, ArmRotDrivers),
	('Hand_L', 'LeftArmState', D_ENUM, ArmRotDrivers),

	('UpArm1_R', 'RightArmState', D_ENUM, ArmRotDrivers),
	('UpArm2_R',  ['RightArmStretch', 'RightArmState'], D_MULTIVAR, UpArmScaleDrivers),
	('UpArm3_R',  ['RightArmStretch', 'RightArmState'], D_MULTIVAR, UpArmScaleDrivers),
	('UpArm3_R', 'RightArmState', D_ENUM, ArmRotDrivers),
	('LoArm1_R', 'RightArmState', D_ENUM, ArmRotDrivers),
	('LoArm2_R', 'RightArmState', D_ENUM, [('ScaleIK', '(x==1) or (x==3)')]),
	('LoArm3_R', 'RightArmState', D_ENUM, ArmRotDrivers),
	('Hand_R', 'RightArmState', D_ENUM, ArmRotDrivers),

	('UpArmIK_L', 'LeftArmState', D_ENUM, [('ElbowIK', 'x>=2')]),
	('LoArmIK_L', 'LeftArmState', D_ENUM, [('ArmIK', 'x==1'), ('WristIK', 'x==3')]),
	('HandIK_L', 'LeftArmState', D_ENUM, [('WristLoc', '(x==1) or (x==3)')]),

	('UpArmIK_R', 'RightArmState', D_ENUM, [('ElbowIK', 'x>=2')]),
	('LoArmIK_R', 'RightArmState', D_ENUM, [('ArmIK', 'x==1'), ('WristIK', 'x==3')]),
	('HandIK_R', 'RightArmState', D_ENUM, [('WristLoc', '(x==1) or (x==3)')]),

	('ElbowIK_L', 'LeftArmStretch', D_BOOLINV, ['DistShoulder']),
	('WristIK_L',  ['LeftArmStretch', 'LeftArmState'], D_MULTIVAR, 
		[('DistElbow', '(not(x1)) and (x2>=2)'),
		 ('DistShoulder', '(not(x1)) and (x2==1)')]),

	('ElbowIK_R', 'RightArmStretch', D_BOOLINV, ['DistShoulder']),
	('WristIK_R',  ['RightArmStretch', 'RightArmState'], D_MULTIVAR, 
		[('DistElbow', '(not(x1)) and (x2>=2)'),
		 ('DistShoulder', '(not(x1)) and (x2==1)')]),

	('HandIK_L',  ['LeftHandFollowsWrist', 'LeftArmState'], D_MULTIVAR, 
		[('WristRot', '(x1) and (x2!=2)')]),
	('HandIK_R',  ['RightHandFollowsWrist', 'RightArmState'], D_MULTIVAR, 
		[('WristRot', '(x1) and (x2!=2)')]),

]

#	Leg

LegProperties = [
	('LeftLeg', D_ENUM, ['Leg FK', 'Leg IK'], 'name="Left leg FK/IK", description=""' ),
	('RightLeg', D_ENUM, ['Leg FK', 'Leg IK'], 'name="Right leg FK/IK", description=""' ),
]

LegRotDrivers = [('RotFK','x==0'), ('RotIK','x>=1')]
LegStretchDrivers = [('StretchFK','x==0'), ('StretchIK','x>=1')]

LegPropDrivers = [
	('UpLeg1_L', 'LeftLeg', D_ENUM, LegRotDrivers),
	('UpLeg3_L', 'LeftLeg', D_ENUM, LegRotDrivers),
	('LoLeg_L', 'LeftLeg', D_ENUM, LegRotDrivers),
	('LoLeg_L', 'LeftLeg', D_ENUM, LegStretchDrivers),
	('Foot_L', 'LeftLeg', D_ENUM, LegRotDrivers),
	('Toe_L', 'LeftLeg', D_ENUM, LegRotDrivers),

	('UpLeg1_R', 'RightLeg', D_ENUM, LegRotDrivers),
	('UpLeg3_R', 'RightLeg', D_ENUM, LegRotDrivers),
	('LoLeg_R', 'RightLeg', D_ENUM, LegRotDrivers),
	('LoLeg_R', 'RightLeg', D_ENUM, LegStretchDrivers),
	('Foot_R', 'RightLeg', D_ENUM, LegRotDrivers),
	('Toe_R', 'RightLeg', D_ENUM, LegRotDrivers),
]

#	Finger

def defineFingerPropDrivers():
	global FingerPropDrivers
	FingerPropDrivers = []
	for (suffix, side) in [('_L', 'Left'), ('_R', 'Right')]:
		for fnum in range(1,6):
			for lnum in range(1,4):
				if (lnum != 1 or fnum != 1):
					FingerPropDrivers.append( ('Finger-%d-%d%s' % (fnum,lnum,suffix), '%sFingerControl' % (side), D_BOOL, ['Rot'] )),

	return

FingerProperties = [
	('LeftFingerControl', D_BOOL, True, 'name="Controlled fingers", description=""'),
	('RightFingerControl', D_BOOL, True, 'name="Controlled fingers", description=""'),
]
defineFingerPropDrivers()

#
#	redefinePropDrivers():
#

OtherProperties = BodyProperties + ArmProperties + FingerProperties + LegProperties
OtherPropDrivers = BodyPropDrivers + ArmPropDrivers + FingerPropDrivers + LegPropDrivers

def defineProperties():
	for (prop, typ, value, options) in ParentProperties + OtherProperties:
		expr = 'bpy.types.Object.%s = %sProperty(' % (prop, PropTypeName[typ])
		if typ == D_ENUM:
			items = []
			for val in value:
				items.append( (val,val,val) )
			expr += 'items=%s, ' % items
		else:
			expr += 'default=%s, ' % value
		expr += '%s)' % options
		print(expr)
		exec(expr)
	return

defineProperties()

def redefinePropDrivers():
	global theRig

	try:
		theRig.pose.bones
	except:
		return

	for pb in theRig.pose.bones:
		for cns in pb.constraints:
			try:
				cns.driver_remove('influence', -1)
			except:
				pass
	
	for (bone, prop, typ, drivers) in ParentPropDrivers+OtherPropDrivers:
		pb = theRig.pose.bones[bone]
		for drvdata in drivers:
			if typ == D_ENUM or typ == D_MULTIVAR:
				(cnsName,expr) = drvdata
			else:
				cnsName = drvdata
				expr = None
			for cns in pb.constraints:
				if cns.name == cnsName:
					print(pb.name, cns.name, prop, expr)
					addPropDriver(cns, prop, expr)
	return

def addPropDriver(cns, prop, expr):
	global theRig
	fcu = cns.driver_add('influence', -1)
	drv = fcu.driver
	if expr:
		drv.type = 'SCRIPTED'
		drv.expression = expr
	else:
		drv.type = 'AVERAGE'
	drv.show_debug_info = True

	if type(prop) == list:
		for n,p in enumerate(prop):
			var = drv.variables.new()
			var.name = 'x%d' % (n+1)
			var.type = 'SINGLE_PROP'

			targ = var.targets[0]
			targ.id = theRig
			targ.data_path = p
	else:
		var = drv.variables.new()
		var.name = 'x'
		var.type = 'SINGLE_PROP'

		targ = var.targets[0]
		targ.id = theRig
		targ.data_path = prop

	return				

#
#	initOldProps():
#	setInverse(context):
#

def initOldProps():
	global theOldProp
	theOldProp = {}
	for (prop, typ, value, options) in ParentProperties:
		theOldProp[prop] = 0
	return

def setInverse(context):
	global theRig, theOldProp
	amt = theRig.data
	for (bone, prop, typ, drivers) in ParentPropDrivers:
		print("old", theOldProp[prop])
		print("new", theRig[prop])
		if theRig[prop] == theOldProp[prop]:
			continue
		pb = theRig.pose.bones[bone]
		for drvdata in drivers:
			if typ == D_ENUM or typ == D_MULTIVAR:
				(cnsName,expr) = drvdata
			else:
				cnsName = drvdata
			cns = pb.constraints[cnsName]
			if cns.type == 'CHILD_OF':
				amt.bones.active = pb.bone
				print("Set inverse", pb.name, amt.bones.active, cns.name)
				bpy.ops.constraint.childof_set_inverse(constraint=cns.name, owner='BONE')
		
	for (prop, typ, value, options) in ParentProperties:
		theOldProp[prop] = theRig[prop]
	return
					
class VIEW3D_OT_MhxSetInverseButton(bpy.types.Operator):
	bl_idname = "mhx.pose_set_inverse"
	bl_label = "Set inverse"

	def execute(self, context):
		setInverse(context)
		return{'FINISHED'}	
				
#
#	class MhxDriversPanel(bpy.types.Panel):
#

class MhxDriversPanel(bpy.types.Panel):
	bl_label = "MHX Drivers"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	@classmethod
	def poll(cls, context):
		return context.object

	def draw(self, context):
		setGlobals(context)
		layout = self.layout
		layout.operator("mhx.pose_init_interface")
		if theRig:
			pbones = theRig.pose.bones
			for (prop, typ, values, options) in ParentProperties:
				layout.label(prop)
				layout.prop(theRig, prop, text=prop, expand=True)
			layout.operator('mhx.pose_set_inverse')
			layout.separator()
			for (prop, typ, values, options) in OtherProperties:
				if typ == D_ENUM:
					layout.label(prop)
				layout.prop(theRig, prop, text=prop, expand=True)


###################################################################################	
#
#	Init and common functions
#
###################################################################################	
#
#	initInterface()
#

def initInterface(scn):
	bpy.types.Scene.MhxSyncAutoKeyframe = BoolProperty(
		name="Auto keyframe", 
		description="Auto keyframe",
		default=False)

	bpy.types.Scene.MhxBodyLanguage = BoolProperty(
		name="Body Language", 
		description="Use Body Language shapekey set",
		default=True)		

	if scn:
		scn['MhxSyncAutoKeyframe'] = False
		scn['MhxBodyLanguage'] = True

	defineProperties()
	redefinePropDrivers()	
	initOldProps()
	return

#
#	class VIEW3D_OT_MhxInitInterfaceButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxInitInterfaceButton(bpy.types.Operator):
	bl_idname = "mhx.pose_init_interface"
	bl_label = "Initialize"
	bl_options = {'REGISTER'}

	def execute(self, context):
		import bpy
		initInterface(context.scene)
		print("Interface initialized")
		return{'FINISHED'}	

#
#	setGlobals(context):
#

def setGlobals(context):
	global theRig, theMesh, theScale	
	if context.object.type == 'ARMATURE':
		theRig = context.object
		theMesh = None
		for child in theRig.children:
			if (child.type == 'MESH' and meshHasExpressions(child)):
				theMesh = child
				break
	elif context.object.type == 'MESH':
		if meshHasExpressions(context.object):
			theMesh = context.object
			theRig = theMesh.parent
		else:
			return
	else:
		return

	try:
		theRig.data.bones['PArmIK_L']
	except:
		theRig = None	
		
#
#	setAllFKIK(value):
#	class VIEW3D_OT_MhxSetAllFKButton(bpy.types.Operator):
#	class VIEW3D_OT_MhxSetAllIKButton(bpy.types.Operator):
#

def setAllFKIK(value):
	global theRig
	pbones = theRig.pose.bones
	for name in ['PArmIK', 'PLegIK']:
		for suffix in ['_L', '_R']:
			pbones[name+suffix].location[0] = value
	return

class VIEW3D_OT_MhxSetAllFKButton(bpy.types.Operator):
	bl_idname = "mhx.pose_set_all_fk"
	bl_label = "All FK"

	def execute(self, context):
		setAllFKIK(0.0)
		return{'FINISHED'}	

class VIEW3D_OT_MhxSetAllIKButton(bpy.types.Operator):
	bl_idname = "mhx.pose_set_all_ik"
	bl_label = "All IK"

	def execute(self, context):
		setAllFKIK(1.0)
		return{'FINISHED'}	


#
#	setAllFingers(value):
#	class VIEW3D_OT_MhxSetAllFingersOffButton(bpy.types.Operator):
#	class VIEW3D_OT_MhxSetAllFingersOnButton(bpy.types.Operator):
#

def setAllFingers(value):
	global theRig
	pbones = theRig.pose.bones
	for n in range(1,6):
		for suffix in ['_L', '_R']:
			pbones['PFinger-%d%s' % (n, suffix)].location[0] = value
	return

class VIEW3D_OT_MhxSetAllFingersOffButton(bpy.types.Operator):
	bl_idname = "mhx.pose_set_all_fingers_off"
	bl_label = "All off"

	def execute(self, context):
		setAllFingers(0.0)
		return{'FINISHED'}	

class VIEW3D_OT_MhxSetAllFingersOnButton(bpy.types.Operator):
	bl_idname = "mhx.pose_set_all_fingers_on"
	bl_label = "All on"

	def execute(self, context):
		setAllFingers(0.7)
		return{'FINISHED'}	


#
#	initialize and register
#

initInterface(bpy.context.scene)
defineVisemeButtons()

def register():
	pass

def unregister():
	pass

if __name__ == "__main__":
	register()


