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

// Create the skin material.
// This texture implements a SubSurface Scattering method
// using premade lightmaps.  
#ifndef (%%name%%_Material)                            

#declare TEXTURE = 
    texture { // Apply high blur to red channel.
        pigment { image_map {png "%%name%%_sss_redlmap.png" interpolate 2} }
        normal  {%%rednormal%%}
        finish { 
            specular 0
            roughness 0.01
            phong 0 phong_size 0
            ambient 0
            diffuse 3
            reflection {0}
            conserve_energy
        }
    }
    texture { // Apply medium blur to green channel.
        pigment { image_map {png "%%name%%_sss_greenlmap.png" interpolate 2 transmit all 1/2} }
        normal  {%%greennormal%%}
        finish { 
            specular 3*%%edss%%
            roughness 2*%%rough%%
            phong 0 phong_size 0
            ambient 0
            diffuse 3
            reflection {0}
            conserve_energy
        }
    }
    texture { // Apply no blur to blue channel.
        pigment { image_map {png "%%name%%_sss_bluelmap.png" interpolate 2 transmit all 2/3} }
        normal  {%%bluenormal%%}
        finish { 
            specular 0
            roughness 0.01
            phong 0 phong_size 0
            ambient 0
            diffuse 3
            reflection {0}
            conserve_energy
        }
    }
    texture {
        pigment { image_map {png "%%name%%_texture.png" filter all 1} }
        normal  {%%normal%%}
        finish { 
            specular %%spec%%
            roughness %%rough%%
            phong 0 phong_size 0
            ambient %%ambience%%
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

                                                                            