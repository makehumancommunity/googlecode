#ifndef (%%name%%_Material)
#declare %%name%%_Texture =
    texture {
        %%diffuse%%
        %%normal%%
        finish {
            specular 1
            roughness 0.008
            phong 0 phong_size 0 
            ambient rgb %%ambience%%
            diffuse 1
            conserve_energy
        }
    }

#declare %%name%%_Material = material {
    texture {
        uv_mapping
        pigment_pattern {%%alpha%%}
        texture_map {
            [0 pigment {color transmit 1.0}]
            [1 %%name%%_Texture]
        }
    }
}

#end

