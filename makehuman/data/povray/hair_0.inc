#ifndef (%%name%%_Material)
#declare %%name%%_Material = material {
    texture {
        uv_mapping
        %%diffuse%%
        finish {
            specular 0
            roughness 1
            phong 0 phong_size 0 
            ambient rgb %%ambience%%
            diffuse 1
            conserve_energy
        }
    }
}
#end 
