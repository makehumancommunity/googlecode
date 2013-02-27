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

import armature as amtpkg

#-------------------------------------------------------------------------------        
#   
#-------------------------------------------------------------------------------        

def writeMaterials(fp, amt):
    
    if amt.human.uvset:
        writeMultiMaterials(fp, amt)
        return
    
    fp.write("""    
# --------------- Images and textures ----------------------------- # 
 
Image texture.png
""")

    filename = amt.config.getTexturePath("texture.png", "data/textures", True, amt.human)
    fp.write("  Filename %s ;" % filename)

    fp.write("""
  use_premultiply True ;
end Image

Image texture_ref.png
""")

    filename = amt.config.getTexturePath("texture_ref.png", "data/textures", True, amt.human)
    fp.write("  Filename %s ;" % filename)

    fp.write("""
  use_premultiply True ;
end Image

Texture diffuse IMAGE
  Image texture.png ;
end Texture

Texture specularity IMAGE
  Image texture_ref.png ;
end Texture


Texture solid IMAGE
end Texture

# --------------- Materials ----------------------------- # 
""")

    nMasks = writeSkinStart(fp, None, amt)

    fp.write("  MTex %d diffuse UV COLOR\n" % nMasks)

    fp.write("""
    texture Refer Texture diffuse ;
    use_map_color_diffuse True ;
    use_map_alpha True ;
    use_map_color_emission True ;
    use_map_density True ;
    alpha_factor 1 ;
    ambient_factor 1 ;
    blend_type 'MIX' ;
    color Array 1.0 0.0 1.0  ;
    diffuse_color_factor 0.945272 ;
    emission_color_factor 0.945272 ;
    reflection_color_factor 0.945272 ;
    specular_color_factor 0.945272 ;
    transmission_color_factor 0.945272 ;
    default_value 1 ;
    density_factor 1 ;
    diffuse_factor 1 ;
    displacement_factor 0.2 ;
    emission_factor 1 ;
    emit_factor 1 ;
    use_from_dupli False ;
    use_from_original False ;
    hardness_factor 1 ;
    mapping 'FLAT' ;
    mirror_factor 0.945272 ;
    invert False ;
    normal_factor 0.5 ;
    normal_map_space 'TANGENT' ;
    raymir_factor 1 ;
    reflection_factor 1 ;
    use_rgb_to_intensity False ;
    scattering_factor 1 ;
    scale (1,1,1) ;
    specular_factor 1 ;
    use_stencil False ;
    translucency_factor 1 ;
    warp_factor 0 ;
    mapping_x 'X' ;
    mapping_y 'Y' ;
    mapping_z 'Z' ;
  end MTex
""")

    fp.write("  MTex %d specularity UV SPECULAR_COLOR\n" % (1+nMasks))
  
    fp.write("""
    texture Refer Texture specularity ;
    use_map_color_diffuse False ;
    use_map_specular True ;
    use_map_reflect True ;
    alpha_factor 1 ;
    ambient_factor 1 ;
    blend_type 'ADD' ;
    color Array 1.0 0.0 1.0  ;
    diffuse_color_factor 1 ;
    emission_color_factor 1 ;
    reflection_color_factor 1 ;
    specular_color_factor 1 ;
    transmission_color_factor 1 ;
    default_value 0.15 ;
    density_factor 1 ;
    diffuse_factor 1 ;
    displacement_factor 0.2 ;
    emission_factor 1 ;
    emit_factor 1 ;
    use True ;
    use_from_dupli False ;
    use_from_original False ;
    hardness_factor 1 ;
    mapping 'FLAT' ;
    mirror_factor 1 ;
    invert False ;
    normal_factor 0.5 ;
    normal_map_space 'TANGENT' ;
    raymir_factor 1 ;
    reflection_factor 1 ;
    use_rgb_to_intensity False ;
    scattering_factor 1 ;
    scale (1,1,1) ;
    specular_factor 1 ;
    use_stencil False ;
    translucency_factor 1 ;
    warp_factor 0 ;
    mapping_x 'X' ;
    mapping_y 'Y' ;
    mapping_z 'Z' ;
  end MTex

  diffuse_color Array 1.0 1.0 1.0  ;
  diffuse_shader 'LAMBERT' ;
  diffuse_intensity 0.93 ;
  specular_color Array 1.0 1.0 1.0  ;
  specular_shader 'PHONG' ;
  specular_intensity 0 ;
  Ramp diffuse_ramp
    Element (0.569697,0.0276216,0.0473347,0.449231) 0.0666667 ;
    Element (1,0.990444,0.961778,1) 0.525252 ;
  end Ramp
  Ramp specular_ramp
    Element (0.468774,0.306093,0.187666,0.2) 0.2 ;
    Element (1,0.925912,0.843177,0.5) 0.8 ;
  end Ramp
  SSS
    use True ;
    back 2 ;
    color Array 0.782026708126 0.717113316059 0.717113316059  ;
    color_factor 0.750324 ;
    error_threshold 0.15 ;
    front 1 ;
    ior 1.3 ;
    radius Array 4.82147502899 1.69369900227 1.08997094631  ;
    scale 0.008*theScale ;
    texture_factor 0 ;
  end SSS
  alpha 0 ;
  ambient 1 ;
  use_cast_approximate True ;
  use_cast_buffer_shadows True ;
  use_cast_shadows_only False ;
  use_cubic False ;
  darkness 1 ;
  diffuse_fresnel 0.1 ;
  diffuse_fresnel_factor 1 ;
  diffuse_ramp_blend 'ADD' ;
  diffuse_ramp_factor 0.3 ;
  diffuse_ramp_input 'SHADER' ;
  diffuse_toon_size 1 ;
  diffuse_toon_smooth 0.1 ;
  emit 0 ;
  use_face_texture True ;
  use_face_texture_alpha False ;
  use_full_oversampling False ;
  invert_z False ;
  use_light_group_exclusive False ;
  mirror_color Array 1.0 1.0 1.0  ;
  use_object_color False ;
  use_only_shadow False ;
  preview_render_type 'FLAT' ;
  use_ray_shadow_bias True ;
  use_transparent_shadows True ;
  roughness 0.5 ;
  use_shadeless False ;
  shadow_buffer_bias 0 ;
  shadow_cast_alpha 1 ;
  shadow_ray_bias 0 ;
  use_shadows True ;
  specular_alpha 1 ;
  specular_hardness 10 ;
  specular_ior 4 ;
  specular_ramp_blend 'MIX' ;
  specular_ramp_factor 1 ;
  specular_ramp_input 'SHADER' ;
  specular_slope 0.1 ;
  specular_toon_size 0.5 ;
  specular_toon_smooth 0.1 ;
  use_tangent_shading False ;
  use_raytrace True ;
  translucency 0 ;
  use_transparency True ;
  transparency_method 'Z_TRANSPARENCY' ;
  use_nodes False ;
  use_sky False ;
  use_textures Array 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1  ;
  use_vertex_color_light False ;
  use_vertex_color_paint False ;
  offset_z 0 ;
  Property MhxDriven True ;
""")

    fp.write("  use_textures Array")
    for n in range(nMasks):
        fp.write(" 1")
    for n in range(3):
        fp.write(" 1")
    fp.write(" ;\n")
    fp.write("  AnimationData %sMesh True\n" % amt.name)
    #amtpkg.drivers.writeTextureDrivers(fp, rig_panel_25.BodyLanguageTextureDrivers)
    writeMaskDrivers(fp, amt)
    fp.write("""
  end AnimationData
end Material
""")

    fp.write("Material %sMouth\n" % amt.name)

    fp.write("""
  MTex 0 diffuse UV COLOR
    texture Refer Texture diffuse ;
    use_map_density True ;
    use_map_color_emission True ;
    use_map_color_diffuse True ;
    use_map_alpha True ;
    alpha_factor 1 ;
    ambient_factor 1 ;
    blend_type 'MIX' ;
    color Array 1.0 0.0 1.0  ;
    emission_color_factor 0.945272 ;
    diffuse_color_factor 0.945272 ;
    mirror_factor 0.945272 ;
    normal_factor 0.5 ;
    reflection_color_factor 0.945272 ;
    specular_color_factor 0.945272 ;
    transmission_color_factor 0.945272 ;
  end MTex

  MTex 1 specularity UV SPECULAR_COLOR
    texture Refer Texture specularity ;
    use_map_color_diffuse False ;
    use_map_reflect True ;
    use_map_specular True ;
    use_map_color_spec True ;
    use_map_color_reflection True ;
    blend_type 'ADD' ;
    color Array 1.0 0.0 1.0  ;
    default_value 0.15 ;
  end MTex

  diffuse_color Array 1.0 1.0 1.0  ;
  diffuse_shader 'LAMBERT' ;
  diffuse_intensity 0.93 ;
  specular_color Array 1.0 1.0 1.0  ;
  specular_shader 'PHONG' ;
  specular_intensity 0.32973 ;
  active_texture Refer Texture diffuse ;
  active_texture_index 0 ;
  alpha 0 ;
  ambient 1 ;
  darkness 1 ;
  diffuse_fresnel 0.1 ;
  diffuse_fresnel_factor 1 ;
  diffuse_ramp_blend 'ADD' ;
  emit 0 ;
  invert_z False ;
  mirror_color Array 1.0 1.0 1.0  ;
  offset_z 0 ;
  preview_render_type 'FLAT' ;
  roughness 0.5 ;
  shadow_buffer_bias 0 ;
  shadow_cast_alpha 1 ;
  shadow_ray_bias 0 ;
  specular_alpha 1 ;
  specular_hardness 369 ;
  specular_ior 4 ;
  specular_ramp_blend 'MIX' ;
  specular_ramp_factor 1 ;
  specular_ramp_input 'SHADER' ;
  specular_slope 0.1 ;
  specular_toon_size 0.5 ;
  specular_toon_smooth 0.1 ;
  translucency 0 ;
  transparency_method 'Z_TRANSPARENCY' ;
  use_cast_approximate True ;
  use_cast_buffer_shadows True ;
  use_cast_shadows_only False ;
  use_cubic False ;
  use_face_texture True ;
  use_face_texture_alpha False ;
  use_nodes False ;
  use_ray_shadow_bias True ;
  use_raytrace True ;
  use_shadows True ;
  use_transparency True ;
  use_transparent_shadows True ;
end Material
""")

    fp.write("Material %sEye\n" % amt.name)

    fp.write("""
  MTex 0 diffuse UV COLOR
    texture Refer Texture diffuse ;
    use_map_density True ;
    use_map_color_emission True ;
    use_map_color_diffuse True ;
    use_map_alpha True ;
    alpha_factor 1 ;
    ambient_factor 1 ;
    blend_type 'MIX' ;
    color Array 1.0 0.0 1.0  ;
    emission_color_factor 0.945272 ;
    diffuse_color_factor 0.945272 ;
    mirror_factor 0.945272 ;
    normal_factor 0.5 ;
    reflection_color_factor 0.945272 ;
    specular_color_factor 0.945272 ;
    transmission_color_factor 0.945272 ;
  end MTex

  MTex 1 specularity UV SPECULAR_COLOR
    texture Refer Texture specularity ;
    use_map_color_diffuse False ;
    use_map_reflect True ;
    use_map_specular True ;
    use_map_color_spec True ;
    use_map_color_reflection True ;
    blend_type 'ADD' ;
    color Array 1.0 0.0 1.0  ;
    default_value 0.15 ;
  end MTex

  diffuse_color Array 1.0 1.0 1.0  ;
  diffuse_shader 'LAMBERT' ;
  diffuse_intensity 0.93 ;
  specular_color Array 1.0 1.0 1.0  ;
  specular_shader 'PHONG' ;
  specular_intensity 0.32973 ;
  active_texture Refer Texture diffuse ;
  active_texture_index 0 ;
  alpha 0 ;
  ambient 1 ;
  darkness 1 ;
  diffuse_fresnel 0.1 ;
  diffuse_fresnel_factor 1 ;
  emit 0 ;
  invert_z False ;
  mirror_color Array 1.0 1.0 1.0  ;
  offset_z 0 ;
  preview_render_type 'FLAT' ;
  roughness 0.5 ;
  shadow_buffer_bias 0 ;
  shadow_cast_alpha 1 ;
  shadow_ray_bias 0 ;
  specular_alpha 0 ;
  specular_hardness 369 ;
  specular_ior 4 ;
  specular_ramp_blend 'MIX' ;
  specular_ramp_factor 1 ;
  specular_ramp_input 'SHADER' ;
  specular_slope 0.1 ;
  translucency 0 ;
  transparency_method 'Z_TRANSPARENCY' ;
  use_cast_buffer_shadows False ;
  use_cast_shadows_only False ;
  use_cubic False ;
  use_face_texture True ;
  use_face_texture_alpha False ;
  use_ray_shadow_bias False ;
  use_raytrace False ;
  use_shadows True ;
  use_sky False ;
  use_tangent_shading False ;
  use_transparency True ;
  use_transparent_shadows True ;
end Material
""")

    fp.write("Material %sBrows\n" % amt.name)


    fp.write("""
  MTex 0 diffuse UV COLOR
    texture Refer Texture diffuse ;
    use_map_density True ;
    use_map_color_emission True ;
    use_map_color_diffuse True ;
    use_map_alpha True ;
    alpha_factor 1 ;
    ambient_factor 1 ;
    blend_type 'MIX' ;
    color Array 1.0 0.0 1.0  ;
    emission_color_factor 0.945272 ;
    diffuse_color_factor 0.945272 ;
    mirror_factor 0.945272 ;
    normal_factor 0.5 ;
    reflection_color_factor 0.945272 ;
    specular_color_factor 0.945272 ;
    transmission_color_factor 0.945272 ;
  end MTex

  MTex 1 specularity UV SPECULAR_COLOR
    texture Refer Texture specularity ;
    use_map_color_diffuse False ;
    use_map_reflect True ;
    use_map_specular True ;
    use_map_color_spec True ;
    use_map_color_reflection True ;
    blend_type 'ADD' ;
    color Array 1.0 0.0 1.0  ;
    default_value 0.15 ;
  end MTex

  diffuse_color Array 1.0 1.0 1.0  ;
  diffuse_shader 'LAMBERT' ;
  diffuse_intensity 0.93 ;
  specular_color Array 1.0 1.0 1.0  ;
  specular_shader 'PHONG' ;
  specular_intensity 0.32973 ;
  active_texture Refer Texture diffuse ;
  active_texture_index 0 ;
  alpha 0 ;
  ambient 1 ;
  darkness 1 ;
  emit 0 ;
  invert_z False ;
  mirror_color Array 1.0 1.0 1.0  ;
  offset_z 0 ;
  preview_render_type 'FLAT' ;
  roughness 0.5 ;
  shadow_buffer_bias 0 ;
  shadow_cast_alpha 1 ;
  shadow_ray_bias 0 ;
  specular_alpha 0 ;
  specular_hardness 369 ;
  specular_ior 4 ;
  specular_ramp_blend 'MIX' ;
  specular_ramp_factor 1 ;
  specular_ramp_input 'SHADER' ;
  specular_slope 0.1 ;
  translucency 0 ;
  transparency_method 'Z_TRANSPARENCY' ;
  use_cast_approximate False ;
  use_cast_buffer_shadows False ;
  use_cast_shadows_only False ;
  use_cubic False ;
  use_face_texture True ;
  use_face_texture_alpha False ;
  use_ray_shadow_bias False ;
  use_raytrace False ;
  use_shadows True ;
  use_transparency True ;
  use_transparent_shadows False ;
end Material
""")

    fp.write("Material %sInvisio\n" % amt.name)

    fp.write("""
  diffuse_color Array 1.0 1.0 1.0  ;
  diffuse_shader 'LAMBERT' ;
  specular_color Array 1.0 1.0 1.0  ;
  specular_shader 'COOKTORR' ;
  active_texture_index 0 ;
  alpha 0 ;
  ambient 1 ;
  use_cast_approximate False ;
  use_cast_buffer_shadows False ;
  use_cast_shadows_only False ;
  use_cubic False ;
  darkness 1 ;
  diffuse_fresnel 0.1 ;
  diffuse_fresnel_factor 0.5 ;
  diffuse_intensity 0.8 ;
  diffuse_ramp_blend 'MIX' ;
  diffuse_ramp_factor 1 ;
  diffuse_ramp_input 'SHADER' ;
  diffuse_toon_size 0.5 ;
  diffuse_toon_smooth 0.1 ;
  emit 0 ;
  use_face_texture False ;
  use_face_texture_alpha False ;
  use_full_oversampling False ;
  invert_z False ;
  use_light_group_exclusive False ;
  mirror_color Array 1.0 1.0 1.0  ;
  use_object_color False ;
  use_only_shadow False ;
  preview_render_type 'SPHERE' ;
  use_ray_shadow_bias True ;
  use_transparent_shadows False ;
  roughness 0.5 ;
  use_shadeless True ;
  shadow_buffer_bias 0 ;
  shadow_cast_alpha 1 ;
  shadow_ray_bias 0 ;
  use_shadows False ;
  specular_alpha 0 ;
  specular_hardness 168 ;
  specular_intensity 0.5 ;
  specular_ior 4 ;
  specular_ramp_blend 'MIX' ;
  specular_ramp_factor 1 ;
  specular_ramp_input 'SHADER' ;
  specular_slope 0.1 ;
  specular_toon_size 0.5 ;
  specular_toon_smooth 0.1 ;
  use_tangent_shading False ;
  use_shadows False ;
  use_raytrace False ;
  translucency 0 ;
  use_transparency True ;
  transparency_method 'Z_TRANSPARENCY' ;
  use_diffuse_ramp False ;
  use_nodes False ;
  use_sky False ;
  use_specular_ramp False ;
  use_textures Array 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1  ;
  use_vertex_color_light False ;
  use_vertex_color_paint False ;
  offset_z 0 ;
end Material
""")

    writeSimpleMaterial(fp, "Red", amt, (1,0,0))
    writeSimpleMaterial(fp, "Green", amt, (0,1,0))
    writeSimpleMaterial(fp, "Blue", amt, (0,0,1))
    return
    
#-------------------------------------------------------------------------------        
#   Simple materials: red, green, blue   
#-------------------------------------------------------------------------------           

def writeSimpleMaterial(fp, name, amt, color):
    fp.write(
        "Material %s%s\n" % (amt.name, name) +
        "  diffuse_color Array %s %s %s  ;" % (color[0], color[1], color[2]))
        
    fp.write("""
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

def writeSkinStart(fp, proxy, amt):
    if not amt.config.useMasks:
        fp.write("Material %sSkin\n" % amt.name)
        return 0
        
    if proxy:
        fp.write("Material %s%sSkin\n" % (amt.name, proxy.name))
        return 0

    nMasks = 0
    prxList = list(amt.proxies.values())
    
    for prx in prxList:
        if prx.mask:
            addMaskImage(fp, amt, prx.mask)
            nMasks += 1
    fp.write("Material %sSkin\n" % amt.name)
             #"  MTex 0 diffuse UV COLOR\n" +
             #"    texture Refer Texture diffuse ;\n" +
             #"  end MTex\n"

    n = 0    
    for prx in prxList:
        if prx.mask:
            n = addMaskMTex(fp, prx.mask, proxy, 'MULTIPLY', n)
            
    return nMasks
               

def writeMaskDrivers(fp, amt):
    if not amt.config.useMasks:
        return
    fp.write("#if toggle&T_Clothes\n")
    n = 0
    for prx in amt.proxies.values():
        if prx.type == 'Clothes' and prx.mask:
            (dir, file) = prx.mask
            amtpkg.drivers.writePropDriver(fp, amt, ["Mhh%s" % prx.name], "1-x1", 'use_textures', n)
            n += 1            
    fp.write("#endif\n")
    return

#-------------------------------------------------------------------------------        
#   Multi materials   
#-------------------------------------------------------------------------------        
      
TX_SCALE = 1
TX_BW = 2

TexInfo = {
    "diffuse" :     ("COLOR", "use_map_color_diffuse", "diffuse_color_factor", 0),
    "specular" :    ("SPECULAR", "use_map_specular", "specular_factor", TX_BW),
    "alpha" :       ("ALPHA", "use_map_alpha", "alpha_factor", TX_BW),
    "translucency": ("TRANSLUCENCY", "use_map_translucency", "translucency_factor", TX_BW),
    "bump" :        ("NORMAL", "use_map_normal", "normal_factor", TX_SCALE|TX_BW),
    "displacement": ("DISPLACEMENT", "use_map_displacement", "displacement_factor", TX_SCALE|TX_BW),
}    

def writeMultiMaterials(fp, amt):
    uvset = amt.human.uvset
    folder = os.path.dirname(uvset.filename)
    log.debug("Folder %s", folder)
    for mat in uvset.materials:
        for tex in mat.textures:
            name = os.path.basename(tex.file)
            fp.write("Image %s\n" % name)
            #file = amt.config.getTexturePath(tex, "data/textures", True, amt.human)
            file = amt.config.getTexturePath(name, folder, True, amt.human)
            fp.write(
                "  Filename %s ;\n" % file +
#                "  alpha_mode 'PREMUL' ;\n" +
                "end Image\n\n" +
                "Texture %s IMAGE\n" % name +
                "  Image %s ;\n" % name +
                "end Texture\n\n")
            
        fp.write("Material %s_%s\n" % (amt.name, mat.name))
        alpha = False
        for (key, value) in mat.settings:
            if key == "alpha":
                alpha = True
                fp.write(
                "  use_transparency True ;\n" +
                "  use_raytrace False ;\n" +
                "  use_shadows False ;\n" +
                "  use_transparent_shadows False ;\n" +
                "  alpha %s ;\n" % value)
            elif key in ["diffuse_color", "specular_color"]:
                fp.write("  %s Array %s %s %s ;\n" % (key, value[0], value[1], value[2]))
            elif key in ["diffuse_intensity", "specular_intensity"]:
                fp.write("  %s %s ;\n" % (key, value))
        if not alpha:
            fp.write("  use_transparent_shadows True ;\n")
                
        n = 0
        for tex in mat.textures:
            name = os.path.basename(tex.file)
            if len(tex.types) > 0:
                (key, value) = tex.types[0]
            else:
                (key, value) = ("diffuse", "1")
            (type, use, factor, flags) = TexInfo[key]
            diffuse = False
            fp.write(
                "  MTex %d %s UV %s\n" % (n, name, type) +
                "    texture Refer Texture %s ;\n" % name)            
            for (key, value) in tex.types:
                (type, use, factor, flags) = TexInfo[key]
                if flags & TX_SCALE:
                    scale = "*theScale"
                else:
                    scale = ""
                fp.write(
                "    %s True ;\n" % use +
                "    %s %s%s ;\n" % (factor, value, scale))
                if flags & TX_BW:
                    fp.write("    use_rgb_to_intensity True ;\n")
                if key == "diffuse":
                    diffuse = True
            if not diffuse:
                fp.write("    use_map_color_diffuse False ;\n")
            fp.write("  end MTex\n")
            n += 1
        fp.write("end Material\n\n")
  
#-------------------------------------------------------------------------------        
#   Masking   
#-------------------------------------------------------------------------------        
  
def addMaskImage(fp, amt, mask):            
    (folder, file) = mask
    path = amt.config.getTexturePath(file, folder, True, amt.human)
    fp.write(
"Image %s\n" % file +
"  Filename %s ;\n" % path +
#"  alpha_mode 'PREMUL' ;\n" +
"end Image\n\n" +
"Texture %s IMAGE\n" % file  +
"  Image %s ;\n" % file +
"end Texture\n\n")
    return
    

def addMaskMTex(fp, mask, proxy, blendtype, n):            
    if proxy:
        try:
            uvLayer = proxy.uvtexLayerName[proxy.maskLayer]
        except KeyError:
            return n

    (dir, file) = mask
    fp.write(
"  MTex %d %s UV ALPHA\n" % (n, file) +
"    texture Refer Texture %s ;\n" % file +
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
    
  