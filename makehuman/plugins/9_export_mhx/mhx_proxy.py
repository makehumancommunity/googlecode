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

Proxies
"""

import os
import log
import gui3d

from . import mhx_writer
#from . import mhx_mesh
#from . import mhx_material

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

class Writer(mhx_writer.Writer):

    def __init__(self, matWriter, meshWriter):
        mhx_writer.Writer.__init__(self)
        self.type = "mhx_proxy"
        self.matWriter = matWriter
        self.meshWriter = meshWriter


    def writeProxyType(self, type, test, layer, fp, t0, t1):
        n = 0
        for proxy in self.proxies.values():
            if proxy.type == type:
                n += 1
        if n == 0:
            return

        dt = (t1-t0)/n
        t = t0
        for proxy in self.proxies.values():
            if proxy.type == type:
                gui3d.app.progress(t, text="Exporting %s" % proxy.name)
                fp.write("#if toggle&%s\n" % test)
                self.writeProxy(fp, proxy, layer)
                fp.write("#endif\n")
                t += dt


    #-------------------------------------------------------------------------------
    #
    #-------------------------------------------------------------------------------

    def writeProxy(self, fp, proxy, layer):
        scale = self.config.scale
        ox,oy,oz = self.config.offset

        fp.write("""
    NoScale False ;
    """)

        # Proxy material

        self.writeProxyMaterial(fp, proxy)

        # Proxy mesh

        name = self.name + proxy.name
        fp.write(
            "Mesh %sMesh %sMesh \n" % (name, name) +
            "  Verts\n")

        fp.write("".join( ["  v %.4f %.4f %.4f ;\n" % (scale*(x-ox), scale*(-z+oz), scale*(y-oy)) for x,y,z in proxy.getCoords()] ))

        fp.write("""
      end Verts
      Faces
    """)

        obj = proxy.getSeedObject()
        log.debug("PROXY %s %s" % (proxy, obj))


        fp.write("".join( ["    f %d %d %d %d ;\n" % tuple(fv) for fv in obj.fvert] ))
        fp.write("    ftall 0 1 ;\n")

        fp.write("  end Faces\n")

        # Proxy layers

        fp.write(
            "  MeshTextureFaceLayer %s\n" % "Texture" +
            "    Data \n")
        uvs = obj.texco
        for fuv in obj.fuvs:
            fp.write("    vt" + "".join( [" %.4g %.4g" % tuple(uvs[vt]) for vt in fuv] ) + " ;\n")
        fp.write(
            "    end Data\n" +
            "  end MeshTextureFaceLayer\n")

        # Proxy vertex groups

        self.meshWriter.writeVertexGroups(fp, proxy)

        if proxy.material:
            fp.write("  Material %s_%s_%s ;" % (self.name, proxy.name, proxy.material.name))
        elif proxy.useBaseMaterials:
            self.meshWriter.writeBaseMaterials(fp)


        fp.write("""
    end Mesh
    """)

        # Proxy object

        name = self.name + proxy.name
        fp.write(
            "Object %sMesh MESH %sMesh \n" % (name, name) +
            "  parent Refer Object %s ;\n" % self.name +
            "  hide False ;\n" +
            "  hide_render False ;\n")
        if proxy.wire:
            fp.write("  draw_type 'WIRE' ;\n")


        # Proxy layers

        fp.write("layers Array ")
        for n in range(20):
            if n == layer:
                fp.write("1 ")
            else:
                fp.write("0 ")
        fp.write(";\n")

        fp.write("""
    #if toggle&T_Armature
    """)

        self.meshWriter.writeArmatureModifier(fp, proxy)
        self.writeProxyModifiers(fp, proxy)

        fp.write("""
      parent_type 'OBJECT' ;
    #endif
      color Array 1.0 1.0 1.0 1.0  ;
      show_name True ;
      select True ;
      lock_location Array 1 1 1 ;
      lock_rotation Array 1 1 1 ;
      lock_scale Array 1 1 1  ;
      Property MhxScale theScale ;
      Property MhxProxy True ;
    end Object
    """)

        self.meshWriter.writeHideAnimationData(fp, self.armature, self.name, proxy.name)

    #-------------------------------------------------------------------------------
    #
    #-------------------------------------------------------------------------------

    def writeProxyModifiers(self, fp, proxy):
        for mod in proxy.modifiers:
            if mod[0] == 'subsurf':
                fp.write(
                    "    Modifier SubSurf SUBSURF\n" +
                    "      levels %d ;\n" % mod[1] +
                    "      render_levels %d ;\n" % mod[2] +
                    "    end Modifier\n")
            elif mod[0] == 'shrinkwrap':
                offset = mod[1]
                fp.write(
                    "    Modifier ShrinkWrap SHRINKWRAP\n" +
                    "      target Refer Object %sMesh ;\n" % self.name +
                    "      offset %.4f ;\n" % offset +
                    "      use_keep_above_surface True ;\n" +
                    "    end Modifier\n")
            elif mod[0] == 'solidify':
                thickness = mod[1]
                offset = mod[2]
                fp.write(
                    "    Modifier Solidify SOLIDIFY\n" +
                    "      thickness %.4f ;\n" % thickness +
                    "      offset %.4f ;\n" % offset +
                    "    end Modifier\n")
        return


    def writeProxyMaterial(self, fp, proxy):
        mat = proxy.material

        if mat.diffuseTexture:
            mat.diffuseTexture = proxy.getActualTexture(self.human)
            alpha = 0
        else:
            alpha = 1 - mat.transparencyMapIntensity

        prefix = self.name+"_"+proxy.name
        texnames = self.matWriter.writeTextures(fp, mat, prefix)

        # Write materials

        fp.write("Material %s_%s_%s \n" % (self.name, proxy.name, mat.name))
        uvlayer = "Texture"
        self.matWriter.writeMTexes(fp, texnames, mat)
        self.matWriter.writeMaterialSettings(fp, mat, alpha)

        fp.write(
            "  Property MhxDriven True ;\n" +
            "end Material\n\n")


