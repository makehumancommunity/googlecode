
#ifndef (%%name%%_Material)

#declare %%name%%_Texture =
    texture {
        pigment {rgb 1}
        finish {
            specular 0
            roughness 1
            phong 0 phong_size 0
            ambient rgb %%ambience%%
            diffuse 1
        }
    }
    texture {
        pigment {rgbf 1}
        %%normal%%
        finish {
            specular %%edss%%
            roughness 2*%%rough%%
            phong 0 phong_size 0
            ambient 0
            diffuse 0
        }
    }
    texture {
        %%diffusef1%%
        %%normal%%
        finish { 
            specular %%spec%%
            roughness %%rough%%
            phong 0 phong_size 0
            ambient 0
            diffuse 0
            reflection {0}
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

                                                                            