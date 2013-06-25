"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         GPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
Project to proxy

"""

import bpy
import os

#

#
#    class CProxy
#

class CProxy:
    def __init__(self):
        self.refVerts = []
        self.firstVert = 0
        return

    def setWeights(self, verts, grp):
        rlen = len(self.refVerts)
        mlen = len(verts)
        first = self.firstVert
        #if (first+rlen) != mlen:
        #    raise NameError( "Bug: %d refVerts != %d meshVerts" % (first+rlen, mlen) )
        gn = grp.index
        for n in range(rlen):
            vert = verts[n+first]
            refVert = self.refVerts[n]
            if type(refVert) == tuple:
                (rv0, rv1, rv2, w0, w1, w2, d0, d1, d2) = refVert
                vw0 = CProxy.getWeight(verts[rv0], gn)
                vw1 = CProxy.getWeight(verts[rv1], gn)
                vw2 = CProxy.getWeight(verts[rv2], gn)
                vw = w0*vw0 + w1*vw1 + w2*vw2
            else:
                vw = CProxy.getWeight(verts[refVert], gn)
            grp.add([vert.index], vw, 'REPLACE')
        return

    def cornerWeights(self, vn):
        n = vn - self.firstVert
        refVert = self.refVerts[n]
        if type(refVert) == tuple:
            (rv0, rv1, rv2, w0, w1, w2, d0, d1, d2) = refVert
            return [(w0,rv0), (w1,rv1), (w2,rv2)]
        else:
            return [(1,refVert)]

    def getWeight(vert, gn):
        for grp in vert.groups:
            if grp.group == gn:
                return grp.weight
        return 0

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

#
#   class VIEW3D_OT_ProjectMaterialsButton(bpy.types.Operator):
#

from random import random

class VIEW3D_OT_ProjectMaterialsButton(bpy.types.Operator):
    bl_idname = "mhw.project_materials"
    bl_label = "Project materials from proxy"

    def execute(self, context):
        ob = context.object
        proxy = CProxy()
        proxy.read(os.path.join(the3dobjFolder, "base.mhclo"))
        grps = baseFileGroups()
        grpList = set(grps.values())
        grpIndices = {}
        grpNames = {}
        n = 0
        for grp in grpList:
            mat = bpy.data.materials.new(grp)
            ob.data.materials.append(mat)
            mat.diffuse_color = (random(), random(), random())
            grpIndices[grp] = n
            grpNames[n] = grp
            n += 1

        vertFaces = {}
        for v in ob.data.vertices:
            vertFaces[v.index] = []

        for f in ob.data.polygons:
            for vn in f.vertices:
                vertFaces[vn].append(f)
                if vn >= proxy.firstVert:
                    grp = None
                    continue
                grp = grps[f.index]
            if grp:
                f.material_index = grpIndices[grp]

        for f in ob.data.polygons:
            if f.vertices[0] >= proxy.firstVert:
                cwts = []
                for vn in f.vertices:
                    cwts += proxy.cornerWeights(vn)
                cwts.sort()
                cwts.reverse()
                (w,vn) = cwts[0]
                for f1 in vertFaces[vn]:
                    mn = f1.material_index
                    f.material_index = f1.material_index
                    continue

        print("Material projected from proxy")
        return{'FINISHED'}

#
#   class VIEW3D_OT_ProjectWeightsButton(bpy.types.Operator):
#

class VIEW3D_OT_ProjectWeightsButton(bpy.types.Operator):
    bl_idname = "mhw.project_weights"
    bl_label = "Project weights from proxy"

    def execute(self, context):
        ob = context.object
        proxy = CProxy()
        filepath = os.path.join(os.path.dirname(__file__), "../maketarget/data/a8_v69_clothes.mhclo")
        proxy.read(filepath)
        for grp in ob.vertex_groups:
            print(grp.name)
            proxy.setWeights(ob.data.vertices, grp)
        print("Weights projected from proxy")
        return{'FINISHED'}

#
#   exportObjFile(context):
#   setupTexVerts(ob, scn):
#

def exportObjFile(context):
    fp = open(os.path.join(the3dobjFolder, "base3.obj"), "w")
    scn = context.scene
    me = context.object.data
    for v in me.vertices:
        fp.write("v %.4f %.4f %.4f\n" % (v.co[0], v.co[2], -v.co[1]))

    for v in me.vertices:
        fp.write("vn %.4f %.4f %.4f\n" % (v.normal[0], v.normal[2], -v.normal[1]))

    if me.uv_textures:
        (uvFaceVerts, texVerts, nTexVerts) = setupTexVerts(me, scn)
        for vtn in range(nTexVerts):
            vt = texVerts[vtn]
            fp.write("vt %.4f %.4f\n" % (vt[0], vt[1]))
        n = 1
        mn = -1
        for f in me.polygons:
            if f.material_index != mn:
                mn = f.material_index
                fp.write("g %s\n" % me.materials[mn].name)
            uvVerts = uvFaceVerts[f.index]
            fp.write("f ")
            for n,v in enumerate(f.vertices):
                (vt, uv) = uvVerts[n]
                fp.write("%d/%d " % (v+1, vt+1))
            fp.write("\n")
    else:
        for f in me.polygons:
            fp.write("f ")
            for vn in f.vertices:
                fp.write("%d " % (vn+1))
            fp.write("\n")

    fp.close()
    print("base3.obj written")
    return

def setupTexVerts(me, scn):
    vertEdges = {}
    vertFaces = {}
    for v in me.vertices:
        vertEdges[v.index] = []
        vertFaces[v.index] = []
    for e in me.edges:
        for vn in e.vertices:
            vertEdges[vn].append(e)
    for f in me.polygons:
        for vn in f.vertices:
            vertFaces[vn].append(f)

    edgeFaces = {}
    for e in me.edges:
        edgeFaces[e.index] = []
    faceEdges = {}
    for f in me.polygons:
        faceEdges[f.index] = []
    for f in me.polygons:
        for vn in f.vertices:
            for e in vertEdges[vn]:
                v0 = e.vertices[0]
                v1 = e.vertices[1]
                if (v0 in f.vertices) and (v1 in f.vertices):
                    if f not in edgeFaces[e.index]:
                        edgeFaces[e.index].append(f)
                    if e not in faceEdges[f.index]:
                        faceEdges[f.index].append(e)

    faceNeighbors = {}
    uvFaceVerts = {}
    for f in me.polygons:
        faceNeighbors[f.index] = []
        uvFaceVerts[f.index] = []
    for f in me.polygons:
        for e in faceEdges[f.index]:
            for f1 in edgeFaces[e.index]:
                if f1 != f:
                    faceNeighbors[f.index].append((e,f1))

    uvtex = me.uv_textures[0]
    vtn = 0
    texVerts = {}
    for f in me.polygons:
        uvf = uvtex.data[f.index]
        vtn = findTexVert(uvf.uv1, vtn, f, faceNeighbors, uvFaceVerts, texVerts, scn)
        vtn = findTexVert(uvf.uv2, vtn, f, faceNeighbors, uvFaceVerts, texVerts, scn)
        vtn = findTexVert(uvf.uv3, vtn, f, faceNeighbors, uvFaceVerts, texVerts, scn)
        if len(f.vertices) > 3:
            vtn = findTexVert(uvf.uv4, vtn, f, faceNeighbors, uvFaceVerts, texVerts, scn)
    return (uvFaceVerts, texVerts, vtn)

def findTexVert(uv, vtn, f, faceNeighbors, uvFaceVerts, texVerts, scn):
    for (e,f1) in faceNeighbors[f.index]:
        for (vtn1,uv1) in uvFaceVerts[f1.index]:
            vec = uv - uv1
            if vec.length < scn.MhxEpsilon:
                uvFaceVerts[f.index].append((vtn1,uv))
                return vtn
    uvFaceVerts[f.index].append((vtn,uv))
    texVerts[vtn] = uv
    return vtn+1

class VIEW3D_OT_ExportBaseObjButton(bpy.types.Operator):
    bl_idname = "mhw.export_base_obj"
    bl_label = "Export base3.obj"

    def execute(self, context):
        exportObjFile(context)
        return{'FINISHED'}
