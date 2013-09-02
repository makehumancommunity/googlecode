#ifndef (%%name%%_Material)

#declare %%name%%_hairtex0 =
    texture {
        %%diffuse%%          
        finish {
            specular 0
            roughness 1
            phong 0 phong_size 0 
            ambient %%ambience%%
            diffuse 1 - %%spec%%
            conserve_energy
        }
    }
    

#declare %%name%%_hairtex1 =
    texture {
        pigment {rgb 1}         
        %%normal%%
        finish {
            specular %%spec%%
            roughness 2*%%rough%%
            phong 0 phong_size 0 
            ambient %%ambience%%
            diffuse 1 - %%spec%%
            conserve_energy
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
            conserve_energy
        }
    }


#declare %%name%%_Material = material {
    texture {
        uv_mapping
        pigment_pattern {%%alpha%%}
        texture_map {
            [0 %%name%%_hairtex0]
            [1 %%name%%_hairtex1]    
        }
    }
}
#end   
