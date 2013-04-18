// Create a camera definition based on the MakeHuman camera settings when this 
// file was generated. We need to convert between the OpenGL vertical FOV and 
// the horizontal POV-Ray camera angle. We also need to account for the way 
// OpenGL reports its camera data, translating before rotating, which further 
// moves the camera. The x-axis is also reversed to the standard POV-Ray settings.
#declare MakeHuman_Camera = camera {
  perspective
  location <MakeHuman_EyeX, MakeHuman_EyeY, MakeHuman_EyeZ>
  look_at <MakeHuman_FocusX, MakeHuman_FocusY, MakeHuman_FocusZ>
  angle 30
}

// Create a standard light definition based on MakeHuman settings.
#declare MakeHuman_LightSource = light_source {
    <MakeHuman_LightX, MakeHuman_LightY, MakeHuman_LightZ>
    color rgb 1
    spotlight
    radius 1000
    falloff 1000
    tightness 1
    point_at < MakeHuman_TranslateX, MakeHuman_TranslateY, MakeHuman_TranslateZ>
}

// Assign default values.
// This texture uses the standard pigment map as a uv-mapped pigment and adds a
// little disruption to the surface normals.  
#ifndef (%%name%%_Material)

#declare TEXTURE =
    texture {
        pigment {rgb 1}
        finish {
            specular 0
            roughness 1
            phong 0 phong_size 0
            ambient %%ambience%%
            diffuse 1
        }
    }
    texture {
        pigment {rgbf 1}
        normal {%%normal%%}
        finish {
            specular %%edss%%
            roughness 2*%%rough%%
            phong 0 phong_size 0
            ambient 0
            diffuse 0
        }
    }
    texture {
        pigment {image_map {png "%%name%%_texture.png" filter all 1}}
        normal {%%normal%%}
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
        TEXTURE
    }
}

#end

                                                                            