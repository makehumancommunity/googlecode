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

MHX materials
"""

import os
import log

from . import mhx_writer
from . import mhx_drivers

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

class Writer(mhx_writer.Writer):

    def writeTexture(self, fp, filepath, prefix, channel):
        texname = prefix+"_"+channel
        imgname = os.path.basename(filepath)
        newpath = self.config.copyTextureToNewLocation(filepath)
        newpath = newpath.replace("\\","/")
        fp.write(
            "Image %s\n" % imgname +
            "  Filename %s ;\n" % newpath +
            "  use_premultiply True ;\n" +
            "end Image\n\n"+
            "Texture %s IMAGE\n" % texname +
            "  Image %s ;\n" % imgname)
        if channel == "normal":
            fp.write("    use_normal_map True ;\n")
        fp.write(
            "end Texture\n\n")
        return texname


    def writeTextures(self, fp, mat, prefix):
        prefix = prefix.replace(" ", "_")
        diffuse,spec,bump,normal,disp = None,None,None,None,None
        if mat.diffuseTexture:
            diffuse = self.writeTexture(fp, mat.diffuseTexture, prefix, "diffuse")
        if mat.specularMapTexture:
            spec = self.writeTexture(fp, mat.specularMapTexture, prefix, "spec")
        if mat.bumpMapTexture:
            bump = self.writeTexture(fp, mat.bumpMapTexture, prefix, "bump")
        if mat.normalMapTexture:
            normal = self.writeTexture(fp, mat.normalMapTexture, prefix, "normal")
        if mat.displacementMapTexture:
            disp = self.writeTexture(fp, mat.displacementMapTexture, prefix, "disp")
        return diffuse,spec,bump,normal,disp


    def writeMTexes(self, fp, texnames, mat, slot):
        diffuse,spec,bump,normal,disp = texnames
        scale = self.config.scale

        if diffuse:
            fp.write(
                "  MTex %d %s UV COLOR\n" % (slot, diffuse) +
                "    texture Refer Texture %s ;" % diffuse +
    """
        use_map_color_diffuse True ;
        use_map_translucency True ;
        use_map_alpha True ;
        alpha_factor 1 ;
        diffuse_color_factor 1.0 ;
        translucency_factor 1.0 ;
      end MTex

    """)
            slot += 1

        if spec:
            fp.write(
                "  MTex %d %s UV SPECULAR_COLOR\n" % (slot, spec) +
                "    texture Refer Texture %s ;\n" % spec +
                "    specular_factor %.4g ;" % (0.1*mat.specularIntensity) +
    """
        use_map_color_diffuse False ;
        use_map_specular True ;
        use_map_reflect True ;
        reflection_factor 1 ;
      end MTex

    """)
            slot += 1

        if bump:
            fp.write(
                "  MTex %d %s UV NORMAL\n" % (slot, bump) +
                "    texture Refer Texture %s ;\n" % bump +
                "    normal_factor %.4g*theScale ;" % (0.1*scale*mat.bumpMapIntensity) +
    """
        use_map_color_diffuse False ;
        use_map_normal True ;
        use_rgb_to_intensity True ;
        end MTex
    """)
            slot += 1

        if normal:
            fp.write(
                "  MTex %d %s UV NORMAL\n" % (slot, normal) +
                "    texture Refer Texture %s ;\n" % normal +
                "    normal_factor %.4g*theScale ;" % (0.1*scale*mat.normalMapIntensity) +
    """
        use_map_color_diffuse False ;
        use_map_normal True ;
        use_rgb_to_intensity True ;
        end MTex
    """)
            slot += 1

        if disp:
            fp.write(
                "  MTex %d %s UV DISPLACEMENT\n" % (slot, disp) +
                "    texture Refer Texture %s ;\n" % disp +
                "    displacement_factor %.4g*theScale ;" % (0.1*scale*mat.displacementMapIntensity) +
    """
        use_map_color_diffuse False ;
        use_map_normal True ;
        use_rgb_to_intensity True ;
        end MTex
    """)
            slot += 1


    def writeMaterialSettings(self, fp, mat, alpha):
        log.debug("%s %s %s" % (mat.specularColor, mat.specularIntensity, mat.specularHardness))
        fp.write(
            "  diffuse_color Array %.4g %.4g %.4g  ;\n" % mat.diffuseColor.asTuple() +
            "  diffuse_shader 'LAMBERT' ;\n" +
            "  diffuse_intensity %.4g ;\n" % mat.diffuseIntensity +
            "  specular_color Array %.4g %.4g %.4g ;\n" % mat.specularColor.asTuple() +
            "  specular_shader 'PHONG' ;\n" +
            "  specular_intensity %.4g ;\n" % (0.1*mat.specularIntensity) +
            "  specular_hardness %.4g ;\n" % mat.specularHardness)

        if alpha < 0.99:
            fp.write(
                "  use_transparency True ;\n" +
                "  transparency_method 'Z_TRANSPARENCY' ;\n" +
                "  alpha %3.f ;\n" % alpha +
                "  specular_alpha %.3f ;\n" % alpha)

        fp.write(
    """
      use_cast_approximate True ;
      use_cast_buffer_shadows True ;
      use_cast_shadows_only False ;
      use_ray_shadow_bias True ;
      use_shadows True ;
      use_transparent_shadows True ;
      use_raytrace True ;
    """)


    def writeMaterials(self, fp):
        config = self.config
        human = self.human
        mat = human.material

        texnames = self.writeTextures(fp, mat, self.name)

        fp.write(
    """
    Texture solid IMAGE
    end Texture

    """)
        if config.useMasks:
            prxList = list(self.proxies.values())
            for prx in prxList:
                if prx.mask:
                    self.addMaskImage(fp, prx.mask)

        fp.write(
            "# --------------- Materials ----------------------------- #\n\n" +
            "Material %sSkin\n" % self.name)

        nMasks = self.writeMaskMTexs(fp)
        self.writeMTexes(fp, texnames, mat, nMasks)
        self.writeMaterialSettings(fp, mat, 0)

        fp.write(
    """
      SSS
        use True ;
        back 2 ;
        color Array 0.782026708126 0.717113316059 0.717113316059  ;
        color_factor 0.750324 ;
        error_threshold 0.15 ;
        front 1 ;
        ior 1.3 ;
        radius Array 4.82147502899 1.69369900227 1.08997094631  ;
    """ +
    "    scale %.4g*theScale ;" % (0.01*config.scale) +
    """
        texture_factor 0 ;
      end SSS
      Property MhxDriven True ;
    """)

        self.writeMaterialAnimationData(fp, nMasks, 2)
        fp.write("end Material\n\n")

        fp.write("Material %sShiny\n" % self.name)
        nMasks = self.writeMaskMTexs(fp)
        shinyTexnames = texnames[0],None,None,None,None
        self.writeMTexes(fp, shinyTexnames, mat, nMasks)

        fp.write(
    """
      diffuse_color Array 1.0 1.0 1.0  ;
      diffuse_shader 'LAMBERT' ;
      diffuse_intensity 1.0 ;
      specular_color Array 1.0 1.0 1.0  ;
      specular_shader 'PHONG' ;
      specular_intensity 1.0 ;
      alpha 0 ;
      specular_alpha 0 ;
      specular_hardness 369 ;
      specular_ior 4 ;
      specular_slope 0.1 ;
      transparency_method 'Z_TRANSPARENCY' ;
      use_cast_buffer_shadows False ;
      use_cast_shadows_only False ;
      use_raytrace True ;
      use_shadows True ;
      use_transparency True ;
      use_transparent_shadows True ;
    """)

        self.writeMaterialAnimationData(fp, nMasks, 1)
        fp.write("end Material\n\n")

        self.writeSimpleMaterial(fp, "Invisio", (1,1,1))
        self.writeSimpleMaterial(fp, "Red", (1,0,0))
        self.writeSimpleMaterial(fp, "Green", (0,1,0))
        self.writeSimpleMaterial(fp, "Blue", (0,0,1))
        self.writeSimpleMaterial(fp, "Yellow", (1,1,0))
        return

    #-------------------------------------------------------------------------------
    #   Simple materials: red, green, blue
    #-------------------------------------------------------------------------------

    def writeSimpleMaterial(self, fp, name, color):
        fp.write(
            "Material %s%s\n" % (self.name, name) +
            "  diffuse_color Array %s %s %s  ;" % (color[0], color[1], color[2]))

        fp.write(
    """
      use_shadeless True ;
      use_shadows False ;
      use_cast_buffer_shadows False ;
      use_raytrace False ;
      use_transparency True ;
      transparency_method 'Z_TRANSPARENCY' ;
      alpha 0 ;
      specular_alpha 0 ;
    end Material
    """)

    #-------------------------------------------------------------------------------
    #
    #-------------------------------------------------------------------------------

    def writeMaterialAnimationData(self, fp, nMasks, nTextures):
        fp.write("  use_textures Array")
        for n in range(nMasks):
            fp.write(" 1")
        for n in range(nTextures):
            fp.write(" 1")
        fp.write(" ;\n")
        fp.write("  AnimationData %sMesh True\n" % self.name)
        #mhx_drivers.writeTextureDrivers(fp, rig_panel.BodyLanguageTextureDrivers)
        self.writeMaskDrivers(fp)
        fp.write("  end AnimationData\n")


    def writeMaskMTexs(self, fp):
        nMasks = 0
        if self.config.useMasks:
            prxList = list(self.proxies.values())
            for prx in prxList:
                if prx.mask:
                    nMasks = addMaskMTex(fp, prx.mask, None, 'MULTIPLY', nMasks)
        return nMasks


    def writeMaskDrivers(self, fp):
        if not self.config.useMasks:
            return
        fp.write("#if toggle&T_Clothes\n")
        n = 0
        for prx in self.proxies.values():
            if prx.type == 'Clothes' and prx.mask:
                (dir, file) = prx.mask
                mhx_drivers.writePropDriver(fp, ["Mhh%s" % prx.name], "1-x1", 'use_textures', n)
                n += 1
        fp.write("#endif\n")
        return

    #-------------------------------------------------------------------------------
    #   Masking
    #-------------------------------------------------------------------------------

    def addMaskImage(self, fp, filepath):
        newpath = self.config.copyTextureToNewLocation(filepath)
        filename = os.path.basename(filepath)
        fp.write(
            "Image %s\n" % filename +
            "  Filename %s ;\n" % newpath +
            #"  alpha_mode 'PREMUL' ;\n" +
            "end Image\n\n" +
            "Texture %s IMAGE\n" % filename  +
            "  Image %s ;\n" % filename +
            "end Texture\n\n"
        )


    def addMaskMTex(self, fp, filepath, proxy, blendtype, n):
        if proxy:
            try:
                uvLayer = proxy.uvtexLayerName[proxy.maskLayer]
            except KeyError:
                return n

        filename = os.path.basename(filepath)
        fp.write(
            "  MTex %d %s UV ALPHA\n" % (n, filename) +
            "    texture Refer Texture %s ;\n" % filename +
            "    use_map_alpha True ;\n" +
            "    use_map_color_diffuse False ;\n" +
            "    alpha_factor 1 ;\n" +
            "    blend_type '%s' ;\n" % blendtype +
            "    mapping 'FLAT' ;\n" +
            "    invert True ;\n" +
            "    use_stencil True ;\n" +
            "    use_rgb_to_intensity True ;\n")
        if proxy:
            fp.write("    uv_layer '%s' ;\n" %  uvLayer)
        fp.write("  end MTex\n")
        return n+1


