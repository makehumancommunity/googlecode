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
Blender API mockup: bpy.types

"""

from mathutils import *
from math import *
import os
import log

from fastmath import *
import exportutils
import exportutils


#------------------------------------------------------------------
#   Blender UI
#------------------------------------------------------------------

class Panel:    
    def __init__(self):
        pass
        
class Operator:
    def __init__(self):
        pass

#------------------------------------------------------------------
#   Init
#------------------------------------------------------------------

def initialize(human, cfg):
    global RnaNames, theHuman, theConfig
    theHuman = human
    theConfig = cfg
    RnaNames = {}
    for rnaType in ['OBJECT', 'MESH', 'ARMATURE', 'MATERIAL', 'TEXTURE', 'IMAGE', 'SCENE', 'BONE', 'POSE']:
        RnaNames[rnaType] = {}


        
def safeName(name, rnaType):
    global RnaNames 
    names = RnaNames[rnaType]
    try:
        names[name]
    except KeyError:
        names[name] = name
        return name
    try:
        n = int(name[-3])
        name = name[:-3] + str(n+1)
    except:
        name = name + ".001"
    return safeName(name, rnaType)           

#------------------------------------------------------------------
#   RNA types
#------------------------------------------------------------------

class Rna:
    def __init__(self, name, rnaType):
        self.animation_data = []
        self.name = safeName(name, rnaType)
        self.rnaType = rnaType
        
    def __repr__(self):
        return ("<%s: %s>" % (self.rnaType, self.name))
        

class Camera(Rna):    
    def __init__(self, name):
        Rna.__init__(self, name, 'CAMERA')
    

class Lamp(Rna):
    def __init__(self, name):
        Rna.__init__(self, name, 'LAMP')


class Curve(Rna):
    def __init__(self, name):
        Rna.__init__(self, name, 'CURVE')


class TextCurve(Rna):
    def __init__(self, name):
        Rna.__init__(self, name, 'TEXT_CURVE')


class SurfaceCurve(Rna):
    def __init__(self, name):
        Rna.__init__(self, name, 'SURFACE')


#------------------------------------------------------------------
#   Collection
#------------------------------------------------------------------

class Collection:
    def __init__(self):
        self.data = {}
        
    def __getattr__(self, attr):
        return self.data[attr]
        
    def __setattr__(self, attr, value):
        self.data[attr] = value
        
    def __iter__(self):
        return self.data.values
        
#------------------------------------------------------------------
#   Armature
#------------------------------------------------------------------

class Armature(Rna):

    def __init__(self, name, boneInfo):
        Rna.__init__(self, name, 'ARMATURE')
        self.bones = {}
        self.boneList = []
        self.edit_bones = self.bones
        self.boneInfo = boneInfo
        self.addHierarchy(boneInfo.hier[0], None)
        

    def addHierarchy(self, hier, parent):
        (bname, children) = hier
        bone = Bone(bname)
        self.bones[bname] = bone
        self.boneList.append(bone)
        bone.head = Vector(self.boneInfo.heads[bname])
        bone.tail = Vector(self.boneInfo.tails[bname])
        bone.roll = self.boneInfo.rolls[bname]
        bone.parent = parent

        bone.matrixLocalFromBone()

        bone.children = []
        for child in children:
            bone.children.append( self.addHierarchy(child, bone) )
        return bone
        

class Bone(Rna):
    ex = Vector((1,0,0))

    def __init__(self, name):
        Rna.__init__(self, name, 'BONE')
        self.head = None
        self.tail = None
        self.parent = None
        self.roll = 0
        self.children = []
        self.matrix_local = Matrix()
        self.matrix = Matrix()
        self.constraints = []
        

    def getLength(self):
        vector = self.tail.vector - self.head.vector
        return sqrt(dot(vector, vector))
        
    def setLength(self):
        pass
  
    length = property(getLength, setLength)


    def matrixLocalFromBone(self):        
    
        u = self.tail - self.head
        length = sqrt(u.dot(u))
        if length < 1e-3:
            log.message("Zero-length bone %s. Removed" % self.name)
            self.matrix_local.matrix[:3,3] = self.head.vector
            return
        u = u/length

        xu = Bone.ex.dot(u)        
        if abs(xu) > 0.99999:
            axis = Bone.ex
            if xu > 0:
                angle = 0
            else:
                angle = pi
        else:        
            axis = Bone.ex.cross(u)
            length = sqrt(axis.dot(axis))
            axis = axis/length
            angle = acos(xu)

        mat = tm.rotation_matrix(angle,axis)
        if self.roll:
            roll = tm.rotation_matrix(self.roll, Bone.ex)
            mat = dot(mat, roll)
        self.matrix_local = Matrix(mat)
        self.matrix_local.matrix[:3,3] = self.head.vector


class Pose(Rna):
    def __init__(self, name, bones):
        Rna.__init__(self, name, 'POSE')
        self.bones = bones
        

#------------------------------------------------------------------
#   Mesh
#------------------------------------------------------------------

class Mesh(Rna):
    def __init__(self, name):
        Rna.__init__(self, name, 'MESH')
        self.vertices = []
        self.faces = []
        self.uv_layers = []
        self.materials = []
        self.shape_keys = []
        
    def fromMeshData(self, mesh):        
        self.vertices = [MeshVertex(v.idx, v.co) for v in mesh.verts]
        self.faces = [[v.idx for v in f.verts] for f in mesh.faces]

    def fromStuff(self, stuff): 
        obj = stuff.meshInfo.object
        stuff.bones = []
        exportutils.collect.setStuffSkinWeights(stuff)
        nVerts = len(obj.verts)
        nUvVerts = len(obj.fuvs)
        nNormals = nVerts
        nFaces = len(obj.faces)
        nWeights = len(stuff.skinWeights)
        nBones = len(stuff.bones)
        nShapes = len(stuff.meshInfo.shapes)

        self.vertices = [MeshVertex(v) for v in obj.verts]
        self.polygons = [MeshPolygon(f, obj.verts) for f in obj.faces]

        if obj.has_uv:
            self.uv_layers.append(UvLayer(obj))

        if stuff.hasMaterial():
            self.materials = [Material(stuff)]
        else:
            self.materials = []

        if stuff.meshInfo.shapes:
            self.shape_keys = ShapeKeys()
            keyblock = KeyBlock("Basis", {})
            self.shape_keys.key_blocks.append(keyblock)
            for (name,shape) in stuff.meshInfo.shapes:
                keyblock = KeyBlock(name, shape)
                self.shape_keys.key_blocks.append(keyblock)
                
            

class MeshVertex:
    def __init__(self, v):
        self.index = v.idx
        self.co = v.co
        self.normal = []
        self.groups = []
        
    def addToGroup(self, index, weight):
        group = MeshGroup(index, weight)
        self.groups.append(group)

        
class VertexGroup:
    def __init__(self, name, index):
        self.name = name
        self.index = index        
        

class MeshGroup:
    def __init__(self, index, weight):
        self.group = index
        self.weight = weight

        
class MeshPolygon:
    def __init__(self, face, meverts):
        self.index = face.idx
        self.vertices = [v.idx for v in face.verts]
        self.material_index = 0
        self.normal = face.no
        return
        co0 = meverts[fverts[0]]
        co1 = meverts[fverts[1]]
        co2 = meverts[fverts[2]]
        e1 = vsub3d(co1,co0)
        e2 = vsub3d(co2,co1)
        self.normal = vnorm3d(vcross3d(e1,e2))
        
        
class UvLayer:
    def __init__(self, obj):
        self.uvloop = UvLoop("UVset0", obj.texco)
        uvlist = []
        for f in obj.faces:
            uvlist.extend(list(f.uv))
        self.uvfaces = uvlist

        
class UvLoop:
    def __init__(self, name, uvValues):
        self.name = name
        self.data = uvValues

class ShapeKeys:
    def __init__(self):
        self.key_blocks = []
        self.animation_data = None
        
        
class KeyBlock:
    def __init__(self, name, shape):
        self.name = name
        self.value = 0.0
        self.data = shape
        target = list(shape.items())
        target.sort()                
        self.indexes = [t[0] for t in target]
        self.vertices = [t[1] for t in target]
        
    def __repr__(self):
        return ("<KeyBlock %s>" % self.name)

        
#------------------------------------------------------------------
#   Material and Texture
#------------------------------------------------------------------

class Material(Rna):
    def __init__(self, stuff):
        
        Rna.__init__(self, self.materialName(stuff), 'MATERIAL')  
        self.diffuse_shader = 'LAMBERT'
        
        if stuff.material:
            self.diffuse_color = stuff.material.diffuse_color
            self.diffuse_intensity = stuff.material.diffuse_intensity
            self.specular_color = stuff.material.specular_color
            self.specular_intensity = stuff.material.specular_intensity
            self.specular_hardness = stuff.material.specular_hardness
            self.transparency = stuff.material.transparency
            self.translucency = stuff.material.translucency
            self.ambient_color = stuff.material.ambient_color
            self.emit_color = stuff.material.emit_color
            self.use_transparency = stuff.material.use_transparency
            self.alpha = stuff.material.alpha
        else:
            self.diffuse_color = (0.8,0.8,0.8)
            self.diffuse_intensity = 0.8
            self.specular_color = (1,1,1)
            self.specular_intensity = 0.1
            self.specular_hardness = 25
            self.transparency = 1
            self.translucency = 0.0
            self.ambient_color = (0,0,0)
            self.emit_color = (0,0,0)
            self.use_transparency = False
            self.alpha = 1

        self.texture_slots = []
        
        if stuff.texture:
            tex = Texture(stuff.texture)
            mtex = MaterialTextureSlot(tex)
            mtex.use_map_color_diffuse = True
            self.texture_slots.append(mtex)
        
        if stuff.specular:
            tex = Texture(stuff.specular)
            mtex = MaterialTextureSlot(tex)
            mtex.use_map_color_spec = True
            self.texture_slots.append(mtex)
        
        if stuff.normal:
            tex = Texture(stuff.normal)
            mtex = MaterialTextureSlot(tex)
            mtex.use_map_normal = True
            self.texture_slots.append(mtex)
        
        if stuff.transparency:
            tex = Texture(stuff.transparency)
            mtex = MaterialTextureSlot(tex)
            mtex.use_map_alpha = True
            self.texture_slots.append(mtex)
        
        if stuff.bump:
            tex = Texture(stuff.bump)
            mtex = MaterialTextureSlot(tex)
            mtex.use_map_normal = True
            self.texture_slots.append(mtex)
        
        if stuff.displacement:
            tex = Texture(stuff.displacement)
            mtex = MaterialTextureSlot(tex)
            mtex.use_map_displacement = True
            self.texture_slots.append(mtex)


    def materialName(self, stuff):
        if stuff.material: 
            return stuff.material.name
        elif stuff.texture: 
            (folder, filename) = stuff.texture
            return os.path.splitext(filename)[0]
        else:
            return "Material"
            

class MaterialTextureSlot:

    def __init__(self, tex):
        self.use_map_diffuse = False
        self.use_map_color_diffuse = False
        self.use_map_alpha = False
        self.use_map_translucency = False

        self.use_map_specular = False
        self.use_map_color_spec = False
        self.use_map_hardness = False

        self.use_map_ambient = False
        self.use_map_emit = False
        self.use_map_mirror = False
        self.use_map_raymir = False

        self.use_map_normal = False
        self.use_map_warp = False
        self.use_map_displacement = False
        
        self.texture = tex
    

class Texture(Rna):
    def __init__(self, filepair):
        folder,filename = filepair
        Rna.__init__(self, filename, 'TEXTURE')
        self.type = 'IMAGE'
        self.image = Image(filename, folder)
        

class Image(Rna):
    def __init__(self, filename, folder):     
        global theHuman, theConfig
        Rna.__init__(self, filename, 'IMAGE')
        self.filepath = theConfig.getTexturePath(filename, folder, True, theHuman)        
        if theConfig.useTexFolder:
            self.filepath = os.path.join(theConfig.outFolder, "textures", filename)

        
#------------------------------------------------------------------
#   Object
#------------------------------------------------------------------

class Object(Rna):
    def __init__(self, name, content, stuff=None):
        Rna.__init__(self, name, 'OBJECT')
        
        self.data = content
        self.type = content.rnaType
        self.parent = None
        self.children = []
        self.matrix_world = Matrix()
        self.select = True
        self.location = Vector((0,0,0))
        self.rotation_euler = Vector((0,0,0))
        self.scale = Vector((1,1,1))
        self.modifiers = []
        
        if self.data.rnaType == 'MESH':
            self.vertex_groups = []
            if stuff.meshInfo:
                index = 0
                for name,weights in stuff.meshInfo.weights.items():
                    self.vertex_groups.append(VertexGroup(name, index))
                    for (vn,w) in weights:
                        content.vertices[vn].addToGroup(index, w)
                    index += 1
        elif self.data.rnaType == 'ARMATURE':
            self.pose = Pose(self.data.name, self.data.bones)
            pass
        
    def __repr__(self):
        return ("<%s: %s type=%s data=%s parent=%s>" % (self.rnaType, self.name, self.type, self.data, self.parent))        


class Modifier:
    def __init__(self, type, ob):
        self.type = type
        self.object = ob
        
#------------------------------------------------------------------
#   Scene and Action
#------------------------------------------------------------------

class Scene(Rna):
    def __init__(self, name="Scene"):
        Rna.__init__(self, name, 'SCENE')
        self.objects = []


class Action(Rna):           
    def __init__(self, name):
        Rna.__init__(self, name, 'ACTION')
