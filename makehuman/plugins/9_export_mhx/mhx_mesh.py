#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makeinfo.human.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makeinfo.human.org/node/318)

**Coding Standards:**  See http://www.makeinfo.human.org/node/165

Abstract
--------

Mesh
"""

import numpy
import os
import log
from . import mhx_drivers

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

def writeMesh(fp, mesh, env):
    config = env.config
    scale = config.scale

    fp.write("""
# ----------------------------- MESH --------------------- #
""")

    fp.write("Mesh %sMesh %sMesh\n  Verts\n" % (env.name, env.name))
    amt = env.armature
    ox = amt.origin[0]
    oy = amt.origin[1]
    oz = amt.origin[2]
    fp.write( "".join(["  v %.4f %.4f %.4f ;\n" % (scale*(co[0]-ox), scale*(-co[2]+oz), scale*(co[1]-oy)) for co in mesh.coord] ))

    fp.write("""
  end Verts

  Faces
""")
    fp.write( "".join(["    f %d %d %d %d ;\n" % tuple(fv) for fv in mesh.fvert] ))

    writeFaceNumbers(fp, env)

    fp.write("""
  end Faces

  MeshTextureFaceLayer UVTex
    Data
""")

    if env.human.uvset:
        uvs = env.human.uvset.uvs
        fuvs = env.human.uvset.fuvs
    else:
        uvs = mesh.texco
        fuvs = mesh.fuvs
    for fuv in fuvs:
        fp.write( "    vt" + "".join([" %.4g %.4g" %(tuple(uvs[vt])) for vt in fuv]) + " ;\n")

    fp.write("""
    end Data
    active True ;
    active_clone True ;
    active_render True ;
  end MeshTextureFaceLayer
""")

    writeBaseMaterials(fp, env)
    writeVertexGroups(fp, env, None)

    fp.write(
"""
end Mesh
""" +
"Object %sMesh MESH %sMesh\n"  % (env.name, env.name) +
"  Property MhxOffsetX %.4f ;\n" % ox +
"  Property MhxOffsetY %.4f ;\n" % oy +
"  Property MhxOffsetZ %.4f ;\n" % oz +
"""
  layers Array 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0  ;
#if toggle&T_Armature
""")

    writeArmatureModifier(fp, env, None)

    fp.write(
"  parent Refer Object %s ;" % env.name +
"""
  parent_type 'OBJECT' ;
#endif
  color Array 1.0 1.0 1.0 1.0  ;
  select True ;
  lock_location Array 1 1 1 ;
  lock_rotation Array 1 1 1 ;
  lock_scale Array 1 1 1  ;
  Property MhxScale theScale ;
  Property MhxMesh True ;
  Modifier SubSurf SUBSURF
    levels 0 ;
    render_levels 1 ;
  end Modifier
end Object
""")

    writeHideAnimationData(fp, amt, "", env.name)
    return


#-------------------------------------------------------------------------------
#   Armature modifier.
#-------------------------------------------------------------------------------

def writeArmatureModifier(fp, env, proxy):
    amt = env.armature
    config = env.config

    if (config.cage and
        not (proxy and proxy.cage)):

        fp.write(
"""
  #if toggle&T_Cage
    Modifier MeshDeform MESH_DEFORM
      invert_vertex_group False ;
""" +
"  object Refer Object %sCageMesh ;" % env.name +
"""
      precision 6 ;
      use_dynamic_bind True ;
    end Modifier
    Modifier Armature ARMATURE
      invert_vertex_group False ;
""" +
"  object Refer Object %s ;" % env.name +
"""
      use_bone_envelopes False ;
      use_multi_modifier True ;
      use_vertex_groups True ;
      vertex_group 'Cage' ;
    end Modifier
  #else
    Modifier Armature ARMATURE
""" +
"  object Refer Object %s ;" % env.name +
"""
      use_bone_envelopes False ;
      use_vertex_groups True ;
    end Modifier
  #endif
""")

    else:

        fp.write(
"""
    Modifier Armature ARMATURE
""" +
"  object Refer Object %s ;" % env.name +
"""
      use_bone_envelopes False ;
      use_vertex_groups True ;
    end Modifier
""")

#-------------------------------------------------------------------------------
#   Face numbers
#-------------------------------------------------------------------------------

MaterialNumbers = {
    "nail"      : 1,
    "teeth"     : 1,
    "eye"       : 1,
    "cornea"    : 1,
    "brow"      : 1,
    "joint"     : 2,
    "red"       : 3,
    "green"     : 4,
    "blue"      : 5,
    "yellow"    : 6,
}

def writeFaceNumbers(fp, env):
    from exportutils.collect import deleteGroup

    if env.human.uvset:
        pass
    else:
        obj = env.human.meshData
        fmats = numpy.zeros(len(obj.coord), int)
        #for fn,mtl in obj.materials.items():
        #    fmats[fn] = MaterialNumbers[mtl]

        # TODO use facemask set on module3d instead (cant we reuse filterMesh from collect module?)
        deleteVerts = None
        deleteGroups = []

        for fg in obj.faceGroups:
            fmask = obj.getFaceMaskForGroups([fg.name])
            if deleteGroup(fg.name, deleteGroups):
                fmats[fmask] = 4
            elif fg.name[0:6] == "joint-":
                fmats[fmask] = 2
            elif fg.name == "helper-tights":
                fmats[fmask] = 3
            elif fg.name in ["helper-hair", "helper-genital"]:
                fmats[fmask] = 6
            elif fg.name in ["helper-skirt", "helper-l-eye", "helper-r-eye"]:
                fmats[fmask] = 5
            elif fg.name[0:7] == "helper-":
                fmats[fmask] = 1

        if deleteVerts != None:
            for fn,fverts in enumerate(obj.fvert):
                if deleteVerts[fverts[0]]:
                    fmats[fn] = 6

        mn = -1
        fn = 0
        f0 = 0
        for fverts in obj.fvert:
            if fmats[fn] != mn:
                if fn != f0:
                    fp.write("  ftn %d %d 1 ;\n" % (fn-f0, mn))
                mn = fmats[fn]
                f0 = fn
            fn += 1
        if fn != f0:
            fp.write("  ftn %d %d 1 ;\n" % (fn-f0, mn))

#-------------------------------------------------------------------------------
#   Material access
#-------------------------------------------------------------------------------

def writeBaseMaterials(fp, env):
    if env.human.uvset:
        for mat in env.human.uvset.materials:
            fp.write("  Material %s_%s ;\n" % (env.name, mat.name))
    else:
        fp.write(
"  Material %sSkin ;\n" % env.name +
"  Material %sShiny ;\n" % env.name +
"  Material %sInvisio ;\n" % env.name +
"  Material %sRed ;\n" % env.name +
"  Material %sGreen ;\n" % env.name +
"  Material %sBlue ;\n" % env.name +
"  Material %sYellow ;\n" % env.name
)


def writeHideAnimationData(fp, amt, prefix, name):
    fp.write("AnimationData %s%sMesh True\n" % (prefix, name))
    mhx_drivers.writePropDriver(fp, amt, ["Mhh%s" % name], "x1", "hide", -1)
    mhx_drivers.writePropDriver(fp, amt, ["Mhh%s" % name], "x1", "hide_render", -1)
    fp.write("end AnimationData\n")
    return

#-------------------------------------------------------------------------------
#   Vertex groups
#-------------------------------------------------------------------------------

def writeVertexGroups(fp, env, proxy):
    amt = env.armature

    if proxy and proxy.weights:
        writeRigWeights(fp, proxy.weights)
        return
    if proxy:
        weights = proxy.getWeights(amt.vertexWeights)
    else:
        weights = amt.vertexWeights
    writeRigWeights(fp, weights)


def writeRigWeights(fp, weights):
    for grp in weights.keys():
        fp.write(
            "\n  VertexGroup %s\n" % grp +
            "".join( ["    wv %d %.4g ;\n" % tuple(vw) for vw in weights[grp]] ) +
            "  end VertexGroup\n")
    return


