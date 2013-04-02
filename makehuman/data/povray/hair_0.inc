#ifndef (%%name%%_Material)
#declare %%name%%_Material = material {
    texture {
        uv_mapping
        pigment { image_map {%%type%% "%%name%%_texture.%%ext%%" interpolate 2}}
    }
}
#end 
