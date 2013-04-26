#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
POV-Ray Export functions.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Chris Bartlett, Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module implements functions to export a human model in POV-Ray format. POV-Ray is a 
Raytracing application (a renderer) that is free to download and use. The generated text 
file contains POV-Ray Scene Description Language (SDL), which consists of human-readable 
instructions for building 3D scenes. 

This module supports the export of a simple mesh2 object or the export of arrays of data
with accompanying macros to assemble POV-Ray objects. Both formats include some handy 
variable and texture definitions that are written into a POV-Ray include file. A POV-Ray 
scene file is also written to the output directory containing a range of examples 
illustrating the use of the include file.

The content of the generated files follows naming conventions intended to make it simple
to adjust to be compliant with the standards for the POV-Ray Object Collection. All 
identifiers start with 'MakeHuman\_'. You can easily perform a global change on this
prefix so that you end up with your own unique prefix.

"""

import os
import string
import shutil
import projection
import random
import mh
import log
import image_operations as imgop
import gui3d
from exportutils import collect
import subprocess

def downloadPovRay():
    import webbrowser
    webbrowser.open('http://www.povray.org/download/')

def povrayExport(app, settings):
    """
    This function exports data in a format that can be used to reconstruct all
    renderable MakeHuman objects in POV-Ray.

    Parameters
    ----------

    app:
      *MHApplication*. MakeHuman's main app class.
    settings:
      *Dictionary*. Options passed from the Povray exporter GUI.
    """

    settings['name'] = string.replace(getHumanName(), " ", "_")
    log.message('POV-Ray Export of object: %s', settings['name'])
  
    camera = app.modelCamera
    resW = app.settings.get('rendering_width', 800)
    resH = app.settings.get('rendering_height', 600)
    resolution = (resW,resH)
  
    path = os.path.join(mh.getPath('render'),
                        app.settings.get('povray_render_dir', 'pov_output'),
                        "%s.inc" % settings['name'])
    
    # The format option defines whether a simple mesh2 object is to be generated
    # or the more flexible but slower array and macro combo is to be generated.
    if settings['format'] == 'array':
        povrayExportArray(app.selectedHuman.mesh, camera, resolution, path, settings)
    if settings['format'] == 'mesh2':
        povrayExportMesh2(app.selectedHuman.mesh, camera, resolution, path, settings)

    outputDirectory = os.path.dirname(path)
    log.debug('out folder: %s', outputDirectory)

    povray_bin = (app.settings.get('povray_bin', ''))
   
    # try to use the appropriate binary 
    if os.path.exists(povray_bin):
        exetype = settings['bintype']
        if exetype == 'win64':
            povray_bin += '/pvengine64.exe'
        elif exetype == 'win32sse2':
            povray_bin += '/pvengine-sse2.exe'
        elif exetype == 'win32':
            povray_bin += '/pvengine.exe'
        elif exetype == 'linux':
            povray_bin += '/povray'
        log.debug('Povray path: %s', povray_bin)


    povwatchApp = None
    povwatchPath = ""
    povwatchTimer = 0
    def povwatch():
        if povwatchApp.poll() is not None:
            mh.changeTask('Rendering', 'Viewer')
            gui3d.app.getCategory('Rendering').getTaskByName('Viewer').setImage(povwatchPath)
            gui3d.app.statusPersist('Rendering complete')
            mh.removeTimer(povwatchTimer)

    if settings['action'] == 'render':
        if os.path.isfile(povray_bin):
            # Prepare command line.
            if os.name == 'nt':
                cmdLine = (povray_bin, 'MHRENDER', '/EXIT')
            else:
                cmdLine = (povray_bin, 'MHRENDER')
                
            # Pass parameters by writing an .ini file.
            iniFD = open(os.path.join(outputDirectory, 'MHRENDER.ini'), 'w')
            iniFD.write('Input_File_Name="%s.pov"\n' % settings['name'] +
                        '+W%d +H%d +a%s +am2\n' % (resW, resH, settings['AA']))
            iniFD.close()

            povwatchApp = subprocess.Popen(cmdLine, cwd = os.path.dirname(path))
            gui3d.app.statusPersist('POV - Ray is rendering.')
            povwatchPath = path.replace('.inc','.png')
            povwatchTimer = mh.addTimer(1000, lambda: povwatch())

        else:
            app.prompt('POV-Ray not found',
                       'You don\'t seem to have POV-Ray installed or the path is incorrect.',
                       'Download', 'Cancel', downloadPovRay)        

def povrayExportArray(obj, camera, resolution, path, settings):
    """
  This function exports data in the form of arrays of data the can be used to 
  reconstruct a humanoid object using some very simple POV-Ray macros. These macros 
  can build this data into a variety of different POV-Ray objects, including a
  mesh2 object that represents the human figure much as it was displayed in MakeHuman. 

  These macros can also generate a union of spheres at the vertices and a union of 
  cylinders that follow the edges of the mesh. A parameter on the mesh2 macro can be 
  used to generate a slightly inflated or deflated mesh. 

  The generated output file always starts with a standard header, is followed by a set 
  of array definitions containing the object data and is ended by a standard set of 
  POV-Ray object definitions. 
  
  Parameters
  ----------
  
  obj:
      *3D object*. The object to export. This should be the humanoid object with
      uv-mapping data and Face Groups defined.
  
  camera:
      *Camera object*. The camera to render from. 
  
  path:
      *string*. The file system path to the output files that need to be generated. 
  """

  # Certain files and blocks of SDL are mostly static and can be copied directly
  # from reference files into the generated output directories or files.

    headerFile = 'data/povray/headercontent.inc'
    staticFile = 'data/povray/staticcontent.inc'
    sceneFile = 'data/povray/makehuman.pov'
    groupingsFile = 'data/povray/makehuman_groupings.inc'
    pigmentMap = gui3d.app.selectedHuman.mesh.texture

  # Define some additional file related strings

    outputSceneFile = path.replace('.inc', '.pov')
    baseName = os.path.basename(path)
    nameOnly = string.replace(baseName, '.inc', '')
    underScores = ''.ljust(len(baseName), '-')
    outputDirectory = os.path.dirname(path)

  # Make sure the directory exists

    if not os.path.isdir(outputDirectory):
        try:
            os.makedirs(outputDirectory)
        except:
            log.error('Error creating export directory.')
            return 0

  # Open the output file in Write mode

    try:
        outputFileDescriptor = open(path, 'w')
    except:
        log.error('Error opening file to write data.')
        return 0

  # Write the file name into the top of the comment block that starts the file.

    outputFileDescriptor.write('// %s\n' % baseName)
    outputFileDescriptor.write('// %s\n' % underScores)

  # Copy the header file SDL straight across to the output file

    try:
        headerFileDescriptor = open(headerFile, 'r')
    except:
        log.error('Error opening file to read standard headers.')
        return 0
    headerLines = headerFileDescriptor.read()
    outputFileDescriptor.write(headerLines)
    outputFileDescriptor.write('''

''')
    headerFileDescriptor.close()

  # Declare POV_Ray variables containing the current makehuman camera.

    povrayCameraData(camera, resolution, outputFileDescriptor)
    
    outputFileDescriptor.write('#declare MakeHuman_TranslateX      = %s;\n' % -obj.x)
    outputFileDescriptor.write('#declare MakeHuman_TranslateY      = %s;\n' % obj.y)
    outputFileDescriptor.write('#declare MakeHuman_TranslateZ      = %s;\n\n' % obj.z)
    
    outputFileDescriptor.write('#declare MakeHuman_RotateX         = %s;\n' % obj.rx)
    outputFileDescriptor.write('#declare MakeHuman_RotateY         = %s;\n' % -obj.ry)
    outputFileDescriptor.write('#declare MakeHuman_RotateZ         = %s;\n\n' % obj.rz)

  # Calculate some useful values and add them to the output as POV-Ray variable
  # declarations so they can be readily accessed from a POV-Ray scene file.

    povraySizeData(obj, outputFileDescriptor)

    # Collect and prepare all objects.
    stuffs = collect.setupObjects(settings['name'], gui3d.app.selectedHuman, helpers=False, hidden=False,
                                            eyebrows=False, lashes=False, subdivide = settings['subdivide'])

    # Write array data for the object.
    povrayWriteArray(outputFileDescriptor, stuffs)

  # Copy macro and texture definitions straight across to the output file.

    try:
        staticContentFileDescriptor = open(staticFile, 'r')
    except:
        log.error('Error opening file to read static content.')
        return 0
    staticContentLines = staticContentFileDescriptor.read()
    outputFileDescriptor.write(staticContentLines)
    outputFileDescriptor.write('\n')
    staticContentFileDescriptor.close()

  # The POV-Ray include file is complete

    outputFileDescriptor.close()
    log.message("POV-Ray '#include' file generated.")

  # Copy a sample scene file across to the output directory

    try:
        sceneFileDescriptor = open(sceneFile, 'r')
    except:
        log.error('Error opening file to read standard scene file.')
        return 0
    try:
        outputSceneFileDescriptor = open(outputSceneFile, 'w')
    except:
        log.error('Error opening file to write standard scene file.')
        return 0
    sceneLines = sceneFileDescriptor.read()
    sceneLines = string.replace(sceneLines, 'xxFileNamexx', nameOnly)
    sceneLines = string.replace(sceneLines, 'xxUnderScoresxx', underScores)
    sceneLines = string.replace(sceneLines, 'xxLowercaseFileNamexx', nameOnly.lower())
    outputSceneFileDescriptor.write(sceneLines)

    # Copy the skin texture file into the output directory
    collect.copy(pigmentMap, os.path.join(outputDirectory, "texture.png"))


  # Copy the makehuman_groupings.inc file into the output directory

    try:
        shutil.copy(groupingsFile, outputDirectory)
    except (IOError, os.error), why:
        log.error("Can't copy %s" % str(why))

  # Job done

    outputSceneFileDescriptor.close()
    sceneFileDescriptor.close()
    log.message('Sample POV-Ray scene file generated.')

def povrayWriteCamera(camera, hfile):
    hfile.write("camera {\n  perspective\n")
    hfile.write("  location <%f,%f,%f>\n" % invx(camera.eye))
    hfile.write("  look_at <%f,%f,%f>\n" % invx(camera.focus))
    hfile.write("  angle %f\n}\n\n" % camera.fovAngle)

def povrayWriteLights(scene, hfile):
    hflig = open('data/povray/lights.inc','r')
    for light in scene.lights:
        liglines = hflig.read()
        liglines = string.replace(liglines, '%%pos%%', '<%f,%f,%f>' % invx(light.position))
        liglines = string.replace(liglines, '%%color%%', '<%f,%f,%f>' % light.color)
        liglines = string.replace(liglines, '%%focus%%', '<%f,%f,%f>' % invx(light.focus))
        liglines = string.replace(liglines, '%%fov%%', str(light.fov))
        liglines = string.replace(liglines, '%%att%%', str(light.attenuation))
        hfile.write(liglines)
    hflig.close()

def povrayWriteScene(stuffs, file):
    hfile = open(file, 'w')
    hfile.write('#include "%s.inc"\n\n' % stuffs[0].name)
    humanRot = gui3d.app.selectedHuman.getRotation()
    for stuff in stuffs:
        hfile.write(
            "object { \n" +
            "   %s_Mesh2Object \n" % stuff.name +
            "   rotate <0,0,%f> \n" % humanRot[2] +
            "   rotate <0,%f,0> \n" % -humanRot[1] +
            "   rotate <%f,0,0> \n" % humanRot[0] +
            "   translate <%f,%f,%f> \n" % invx(gui3d.app.selectedHuman.getPosition()) +
            "   material {%s_Material} \n}\n" % stuff.name)
    hfile.close()

def povraySizeData(obj, hfile):
    """
  This function outputs standard object dimension data common to all POV-Ray 
  format exports. 

  Parameters
  ----------
  
  obj:
      *3D object*. The object to export. This should be the humanoid object with
      uv-mapping data and Face Groups defined.
  
  hfile:
      *file descriptor*. The file to which the camera settings need to be written. 
  """

    maxX = 0
    maxY = 0
    maxZ = 0
    minX = 0
    minY = 0
    minZ = 0
    for co in obj.coord:
        maxX = max(maxX, co[0])
        maxY = max(maxY, co[1])
        maxZ = max(maxZ, co[2])
        minX = min(minX, co[0])
        minY = min(minY, co[1])
        minZ = min(minZ, co[2])
    hfile.write('// Figure Dimensions. \n')
    hfile.write('#declare MakeHuman_MaxExtent = < %s, %s, %s>;\n' % (maxX, maxY, maxZ))
    hfile.write('#declare MakeHuman_MinExtent = < %s, %s, %s>;\n' % (minX, minY, minZ))
    hfile.write('#declare MakeHuman_Center    = < %s, %s, %s>;\n' % ((maxX + minX) / 2, (maxY + minY) / 2, (maxZ + minZ) / 2))
    hfile.write('#declare MakeHuman_Width     = %s;\n' % (maxX - minX))
    hfile.write('#declare MakeHuman_Height    = %s;\n' % (maxY - minY))
    hfile.write('#declare MakeHuman_Depth     = %s;\n' % (maxZ - minZ))
    hfile.write('''

''')


def povrayExportMesh2(obj, camera, resolution, path, settings, progressCallback = None):
    """
    This function exports data in the form of a mesh2 humanoid object. The POV-Ray 
    file generated is fairly inflexible, but is highly efficient. 

    Parameters
    ----------

    obj:
      *3D object*. The object to export. This should be the humanoid object with
      uv-mapping data and Face Groups defined.

    camera:
      *Camera object*. The camera to render from. 

    path:
      *string*. The file system path to the output files that need to be generated.

    settings:
      *dictionary*. Settings passed from the GUI.
    """

    progbase = 0
    def progress (prog, desc):
        if progressCallback == None:
            gui3d.app.progress(prog, desc)
        else:
            progressCallback(prog, desc)

    # Certain blocks of SDL are mostly static and can be copied directly from reference
    # files into the output files.
    nextpb = 0.6 - 0.4 * bool(settings['SSS'])
    progress (progbase,"Parsing data")
    staticFile = 'data/povray/staticcontent_mesh2only_fsss.inc' if settings['SSS'] else 'data/povray/staticcontent_mesh2only_tl.inc'

    # Define some additional file locations
    outputSceneFile = path.replace('.inc', '.pov')
    baseName = os.path.basename(path)
    underScores = ''.ljust(len(baseName), '-')
    outputDirectory = os.path.dirname(path)

    # Make sure the directory exists
    if not os.path.isdir(outputDirectory):
        try:
            os.makedirs(outputDirectory)
        except:
            log.error('Error creating export directory.')
            return 0
    
    # Open the output file in Write mode
    try:
        outputFileDescriptor = open(path, 'w')
    except:
        log.error('Error opening file to write data: %s', path)
        return 0

    # Write sizes to make size ratios available.
    povraySizeData(obj, outputFileDescriptor)

    # Collect and prepare all objects.
    stuffs = collect.setupObjects(settings['name'], gui3d.app.selectedHuman, helpers=False, hidden=False,
                                            eyebrows=False, lashes=False, subdivide = settings['subdivide'],
                                            progressCallback = lambda p: progress(progbase+p*(nextpb-progbase),"Analyzing objects"))
    progbase = nextpb

    # If SSS is enabled, render the lightmaps.
    if settings['SSS'] == True:
        povrayProcessSSS(stuffs, outputDirectory, settings, lambda p: progress(progbase+p*(0.6-progbase),"Processing Subsurface Scattering"))
        progbase = 0.6

    # Write mesh data for the object.
    povrayWriteMesh2(outputFileDescriptor, stuffs, lambda p: progress(progbase+p*(0.9-progbase),"Writing Objects"))
    progbase = 0.9
                                            
    # Copy texture definitions to the output file.
    progress(progbase,"Writing Materials")
    povrayWriteCamera(gui3d.app.modelCamera, outputFileDescriptor)
    povrayWriteLights(settings['scene'], outputFileDescriptor)
    try:
        staticContentFileDescriptor = open(staticFile, 'r')
    except:
        log.error('Error opening file to read static content.')
        return 0
    staticContentLines = staticContentFileDescriptor.read()
    staticContentLines = string.replace(staticContentLines, '%%spec%%', str(settings['skinoil']*settings['moist']))    
    staticContentLines = string.replace(staticContentLines, '%%edss%%', str(settings['skinoil']*(1-settings['moist'])))
    staticContentLines = string.replace(staticContentLines, '%%rough%%', str(settings['rough']))
    if settings['usebump']:
        _, imgtype = getChannelData(stuffs[0].bump)
        staticContentLines = string.replace(staticContentLines, '%%normal%%',
                                            'bump_map {%s "%s_bump.%s" bump_size %s interpolate 2}' % (
                                                imgtype, stuffs[0].name,(stuffs[0].bump[1].split("."))[1],str(
                                                    settings['wrinkles'])))         
        if settings['SSS']:
            staticContentLines = string.replace(staticContentLines, '%%bluenormal%%',
                                                'bump_map {%s "%s_bump.%s" bump_size 3*%s interpolate 2}' % (
                                                    imgtype, stuffs[0].name,(stuffs[0].bump[1].split("."))[1],str(settings['wrinkles'])))         
            staticContentLines = string.replace(staticContentLines, '%%greennormal%%',
                                                'bump_map {png "%s_sss_greenbump.png" bump_size 3*%s interpolate 2}' % (
                                                    stuffs[0].name, str(settings['wrinkles'])))         
            staticContentLines = string.replace(staticContentLines, '%%rednormal%%',
                                                'bump_map {png "%s_sss_redbump.png" bump_size 3*%s interpolate 2}' % (
                                                    stuffs[0].name, str(settings['wrinkles'])))         
    else:
        grainstr = 'wrinkles %s scale 0.0002' % str(settings['wrinkles'])
        staticContentLines = string.replace(staticContentLines, '%%normal%%',
                                            'wrinkles %s scale 0.0002' % str(settings['wrinkles']))         
        if settings['SSS']:
            staticContentLines = string.replace(staticContentLines, '%%bluenormal%%',
                                                'wrinkles 3*%s scale 0.0002' % str(settings['wrinkles']))         
            staticContentLines = string.replace(staticContentLines, '%%greennormal%%',
                                                'wrinkles 1.5*%s scale 0.0004' % str(settings['wrinkles']))         
            staticContentLines = string.replace(staticContentLines, '%%rednormal%%',
                                                'wrinkles 0.75*%s scale 0.0006' % str(settings['wrinkles']))
    staticContentLines = string.replace(staticContentLines, '%%name%%', stuffs[0].name)    
    staticContentLines = string.replace(staticContentLines, '%%ambience%%',
                                        'rgb <%f,%f,%f>' % settings['scene'].environment.ambience)
    outputFileDescriptor.write(staticContentLines)
    outputFileDescriptor.write('\n')
    staticContentFileDescriptor.close()
    
    progress(progbase+0.2*(1-progbase),"Writing Materials")
    writeItemsMaterials(outputFileDescriptor, stuffs, settings, outputDirectory)
    outputFileDescriptor.close()

    progress(0.95,"Writing Scene file")
    povrayWriteScene(stuffs, outputSceneFile)

    progress(0.95,"Writing textures")
    for stuff in stuffs:
        if stuff.textureImage:
            stuff.textureImage.save(os.path.join(outputDirectory,
                                                 "%s_texture.png" % stuff.name))
        elif stuff.texture:
            collect.copy(stuff.texture, os.path.join(outputDirectory,
                                                     "%s_texture.%s" % (stuff.name,
                                                                        (stuff.texture[1].split("."))[1])))
        if stuff.bump:
            collect.copy(stuff.bump, os.path.join(outputDirectory,
                                                  "%s_bump.%s" % (stuff.name,
                                                                  (stuff.bump[1].split("."))[1])))
            
    progress(1,"Finished. Pov-Ray project exported successfully at %s" % outputDirectory)

def writeItemsMaterials(outputFileDescriptor, stuffs, settings, outDir):
    for stuff in stuffs[1:]:
        texdata = getChannelData(stuff.texture)
        bumpdata = getChannelData(stuff.bump)
        if stuff.type == 'Hair':
            if settings['hairShine']:
                # Export transparency map.
                hairtex = mh.Image(path = os.path.join(stuff.texture[0],stuff.texture[1]))
                hairalpha = imgop.getAlpha(hairtex)
                hairalpha.save(path = os.path.join(outDir,"%s_alpha.png" % stuff.name))
                hhairfile = open ("data/povray/hair_2.inc",'r')
                hairlines = hhairfile.read()
                hairlines = hairlines.replace ("%%spec%%",str(settings['hairSpec']))
                hairlines = hairlines.replace ("%%hard%%",str(settings['hairHard']))
                hairlines = hairlines.replace ("%%rough%%",str(settings['hairRough']))
            else:
                hhairfile = open ("data/povray/hair_0.inc",'r')
                hairlines = hhairfile.read()
            hhairfile.close()
            hairlines = hairlines.replace (
                "%%ambience%%", 'rgb <%f,%f,%f>' %
                settings['scene'].environment.ambience)
            hairlines = hairlines.replace ("%%name%%",stuff.name)
            hairlines = hairlines.replace (
                "%%texture%%", '%s "%s_texture.%s"' %
                (texdata[1], stuff.name, stuff.texture[1].split(".")[1]))
            if bumpdata:
                hairlines = hairlines.replace (
                    "%%bumpmap%%", '%s "%s_bump.%s"' %
                    (bumpdata[1], stuff.name, stuff.bump[1].split(".")[1]))
            elif settings['hairSpec']:
                hairlines = hairlines.replace (
                    "%%bumpmap%%", 'png "%s_alpha.png"' % stuff.name)
            outputFileDescriptor.write(hairlines)
        else:            
            outputFileDescriptor.write("#ifndef (%s_Material)\n" % stuff.name +
                                       "#declare %s_Texture =\n" % stuff.name +
                                       "    texture {\n")                        
            if texdata:                
                outputFileDescriptor.write(
                        '        pigment { image_map {%s "%s_texture.%s" interpolate 2} }\n' % (
                            texdata[1], stuff.name, (stuff.texture[1].split("."))[1]))
            else:
                outputFileDescriptor.write(
                        '        pigment { rgb <1,1,1> }\n')
            if bumpdata:
               outputFileDescriptor.write(
                        '        normal { bump_map {%s "%s_bump.%s" interpolate 2} }\n' % (
                            bumpdata[1], stuff.name, (stuff.bump[1].split("."))[1]))
            else:
                outputFileDescriptor.write(
                        '        normal { wrinkles 0.2 scale 0.0001 }\n')
            outputFileDescriptor.write ("        finish {\n" +
                                "            specular 0.05\n" +
                                "            roughness 0.2\n" +
                                "            phong 0 phong_size 0 \n" +
                                "            ambient 0.1\n" +
                                "            diffuse 0.9\n" +
                                "            conserve_energy\n" +
                                "        }\n" +
                                "    }\n\n" +
                                "#declare %s_Material = material {\n" % stuff.name +
                                "    texture {\n" +
                                "        uv_mapping\n" +
                                "        %s_Texture\n" % stuff.name +
                                "    }\n" +
                                "}\n\n" +
                                "#end\n")


def writeChannel(outputFileDescriptor, var, channel, stuff, data):
    (path, type) = data
    outputFileDescriptor.write(
            "    #declare %s_%s = %s { \n" % (var, stuff.name, channel) +
            '       image_map { %s "%s" interpolate 2} \n' % (type, path) +
            "    } \n" +
            "     \n")            


def getChannelData(value):
    if value:
        (folder, file) = value
        (fname, ext) = os.path.splitext(file)
        ext = ext.lower()
        if ext == ".tif":
            type = "tiff"
        elif ext == ".jpg":
            type = "jpeg"
        else:
            type = ext[1:]
        return file,type
    else:
        return None
                
def povrayWriteMesh2(hfile, stuffs, progressCallback = None):

    def progress(prog):
        if progressCallback == None:
            gui3d.app.progress(prog)
        else:
            progressCallback(prog)
    progress(0)
        
    stuffnum = float(len(stuffs))
    i = 0.0
    for stuff in stuffs:
        obj = stuff.meshInfo.object

        hfile.write('// Mesh2 object definition\n')
        hfile.write('#declare %s_Mesh2Object = mesh2 {\n' % stuff.name)

        # Vertices
        hfile.write('  vertex_vectors {\n      %s\n  ' % len(obj.coord))
        for co in obj.coord:
            hfile.write('<%s,%s,%s>' % (-co[0],co[1],co[2]))
        hfile.write('\n  }\n\n')
        progress((i+0.142)/stuffnum)

        # Normals
        hfile.write('  normal_vectors {\n      %s\n  ' % len(obj.vnorm))
        for no in obj.vnorm:
            hfile.write('<%s,%s,%s>' % (-no[0],no[1],no[2]))
        hfile.write('\n  }\n\n')
        progress((i+0.286)/stuffnum)
    
        # UV Vectors
        hfile.write('  uv_vectors {\n      %s\n  ' % len(obj.texco))
        for uv in obj.texco:
            hfile.write('<%s,%s>' % tuple(uv))        
        hfile.write('\n  }\n\n')
        progress((i+0.428)/stuffnum)
        
        nTriangles = 2*len(obj.fvert) # MH faces are quads.

        hfile.write('  face_indices {\n      %s\n  ' % nTriangles)
        for fverts in obj.fvert:
            hfile.write('<%s,%s,%s>' % (fverts[0], fverts[1], fverts[2]))
            hfile.write('<%s,%s,%s>' % (fverts[2], fverts[3], fverts[0]))
        hfile.write('\n  }\n\n')
        progress((i+0.714)/stuffnum)


        # UV Indices for each face
        hfile.write('  uv_indices {\n      %s\n  ' % nTriangles)
        for fuv in obj.fuvs:
            hfile.write('<%s,%s,%s>' % (fuv[0], fuv[1], fuv[2]))
            hfile.write('<%s,%s,%s>' % (fuv[2], fuv[3], fuv[0]))
        hfile.write('\n  }\n')

        # Write the end squiggly bracket for the mesh2 object declaration
        hfile.write('\n      uv_mapping\n}\n\n')
        
        i += 1.0
        progress(i/stuffnum)

def povrayWriteArray(hfile, stuffs, progressCallback = None):

    def progress(prog):
        if progressCallback == None:
            gui3d.app.progress(prog)
        else:
            progressCallback(prog)
    progress(0)

    obj = stuffs[0].object
    
    # Vertices
    hfile.write('#declare MakeHuman_VertexArray = array[%s] {\n  ' % len(obj.coord))
    for co in obj.coord:
        hfile.write('<%s,%s,%s>' % (co[0], co[1], co[2]))
    hfile.write("\n}\n\n")

    # Normals
    hfile.write('#declare MakeHuman_NormalArray = array[%s] {\n  ' % len(obj.vnorm))
    for no in obj.vnorm:
        hfile.write('<%s,%s,%s>' % (no[0], no[1], no[2]))
    hfile.write("\n}\n\n")

    faces = [f for f in obj.faces if not 'joint-' in f.group.name]

    # UV Vectors
    hfile.write('#declare MakeHuman_UVArray = array[%s] {\n  ' % len(obj.texco))
    for uv in obj.texco:
        
        hfile.write('<%s,%s>' % (uv[0], uv[1]))

    # hfile.write("\n")
    hfile.write("\n}\n\n")

    # Faces
    hfile.write('#declare MakeHuman_FaceArray = array[%s][3] {\n  ' % (len(faces) * 2))
    for f in faces:
        hfile.write('{%s,%s,%s}' % (f.verts[0].idx, f.verts[1].idx, f.verts[2].idx))
        hfile.write('{%s,%s,%s}' % (f.verts[2].idx, f.verts[3].idx, f.verts[0].idx))
    hfile.write("\n}\n\n")

    # FaceGroups - Write a POV-Ray array to the output stream and build a list of indices
    # that can be used to cross-reference faces to the Face Groups that they're part of.
    hfile.write('#declare MakeHuman_FaceGroupArray = array[%s] {\n  ' % obj.faceGroupCount)
    fgIndex = 0
    faceGroupIndex = {}
    for fg in obj.faceGroups:
        faceGroupIndex[fg.name] = fgIndex
        hfile.write('  "%s",\n' % fg.name)
        fgIndex += 1
    hfile.write("}\n\n")

    # FaceGroupIndex
    hfile.write('#declare MakeHuman_FaceGroupIndexArray = array[%s] {\n  ' % len(faces))
    for f in faces:
        hfile.write('%s,' % faceGroupIndex[f.group.name])
    hfile.write("\n}\n\n")

    # UV Indices for each face
    hfile.write('#declare MakeHuman_UVIndexArray = array[%s][3] {\n  ' % (len(faces) * 2))
    for f in faces:
        hfile.write('{%s,%s,%s}' % (f.uv[0], f.uv[1], f.uv[2]))
        hfile.write('{%s,%s,%s}' % (f.uv[2], f.uv[3], f.uv[0]))
    hfile.write("\n}\n\n")

    # Joint Positions
    faceGroupExtents = {}
    for f in obj.faces:
        if 'joint-' in f.group.name:

      # Compare the components of each vertex to find the min and max values for this faceGroup

            if f.group.name in faceGroupExtents:
                maxX = max([f.verts[0].co[0], f.verts[1].co[0], f.verts[2].co[0], f.verts[3].co[0], faceGroupExtents[f.group.name][3]])
                maxY = max([f.verts[0].co[1], f.verts[1].co[1], f.verts[2].co[1], f.verts[3].co[1], faceGroupExtents[f.group.name][4]])
                maxZ = max([f.verts[0].co[2], f.verts[1].co[2], f.verts[2].co[2], f.verts[3].co[2], faceGroupExtents[f.group.name][5]])
                minX = min([f.verts[0].co[0], f.verts[1].co[0], f.verts[2].co[0], f.verts[3].co[0], faceGroupExtents[f.group.name][0]])
                minY = min([f.verts[0].co[1], f.verts[1].co[1], f.verts[2].co[1], f.verts[3].co[1], faceGroupExtents[f.group.name][1]])
                minZ = min([f.verts[0].co[2], f.verts[1].co[2], f.verts[2].co[2], f.verts[3].co[2], faceGroupExtents[f.group.name][2]])
            else:
                maxX = max([f.verts[0].co[0], f.verts[1].co[0], f.verts[2].co[0], f.verts[3].co[0]])
                maxY = max([f.verts[0].co[1], f.verts[1].co[1], f.verts[2].co[1], f.verts[3].co[1]])
                maxZ = max([f.verts[0].co[2], f.verts[1].co[2], f.verts[2].co[2], f.verts[3].co[2]])
                minX = min([f.verts[0].co[0], f.verts[1].co[0], f.verts[2].co[0], f.verts[3].co[0]])
                minY = min([f.verts[0].co[1], f.verts[1].co[1], f.verts[2].co[1], f.verts[3].co[1]])
                minZ = min([f.verts[0].co[2], f.verts[1].co[2], f.verts[2].co[2], f.verts[3].co[2]])
            faceGroupExtents[f.group.name] = [minX, minY, minZ, maxX, maxY, maxZ]

    # Write out the centre position of each joint
    for fg in obj.faceGroups:
        if 'joint-' in fg.name:
            jointVarName = string.replace(fg.name, '-', '_')
            jointCentreX = (faceGroupExtents[fg.name][0] + faceGroupExtents[fg.name][3]) / 2
            jointCentreY = (faceGroupExtents[fg.name][1] + faceGroupExtents[fg.name][4]) / 2
            jointCentreZ = (faceGroupExtents[fg.name][2] + faceGroupExtents[fg.name][5]) / 2

      # jointCentre  = "<"+jointCentreX+","+jointCentreY+","+jointCentreZ+">"

            hfile.write('#declare MakeHuman_%s=<%s,%s,%s>;\n' % (jointVarName, jointCentreX, jointCentreY, jointCentreZ))
    hfile.write("\n\n")

    #TEMP# Write the rest using Mesh2 format.
    povrayWriteMesh2(hfile,stuffs[1:])


def povrayProcessSSS(stuffs, outDir, settings, progressCallback = None):

    def progress(prog):
        if progressCallback == None:
            gui3d.app.progress(prog)
        else:
            progressCallback(prog)
    progress(0)
        
    progbase = 0
    nextpb = 1 - 0.65*settings['usebump']
    # get lightmap
    lmap = projection.mapSceneLighting(
        settings['scene'],progressCallback = lambda p: progress(0.3*nextpb*p))
    lmap = imgop.getChannel(lmap,1)
    # prepare channels
    black = imgop.Image(data=imgop.numpy.zeros((lmap.height, lmap.width, 1), dtype=imgop.numpy.uint8))
    # calculate blur level of each cannel, according to settings
    sssa = float(settings['SSSA'])
    # blue channel
    imgop.compose([black,black,lmap]).save(
        os.path.join(outDir, '%s_sss_bluelmap.png' % stuffs[0].name))
    # green channel
    progress(0.4*nextpb)
    lmap2 = imgop.blurred(lmap, int(10*sssa),13, lambda p: progress((0.4+0.3*p)*nextpb))
    imgop.compose([black,lmap2,black]).save(
        os.path.join(outDir, '%s_sss_greenlmap.png' % stuffs[0].name))
    # red channel
    progress(0.7*nextpb)
    lmap2 = imgop.blurred(lmap2, int(20*sssa),13, lambda p: progress((0.7+0.3*p)*nextpb))
    imgop.compose([lmap2,black,black]).save(
        os.path.join(outDir, '%s_sss_redlmap.png' % stuffs[0].name))
    progbase = nextpb
    progress(progbase)
    if settings['usebump']:
        # Export blurred bump maps
        lmap = imgop.Image(os.path.join(stuffs[0].bump[0], stuffs[0].bump[1]))
        lmap = imgop.getChannel(lmap,1)
        lmap = imgop.blurred(lmap, int(float(lmap.width/1024)*5*sssa), 15,
                             lambda p: progress(progbase+0.5*p*(1-progbase)))
        progress(progbase+0.5*(1-progbase))
        lmap.save(os.path.join(outDir, '%s_sss_greenbump.png' % stuffs[0].name))
        lmap = imgop.blurred(lmap, int(float(lmap.width/1024)*10*sssa), 15,
                             lambda p: progress(progbase+(0.5+0.5*p)*(1-progbase)))
        lmap.save(os.path.join(outDir, '%s_sss_redbump.png' % stuffs[0].name))
        progress(1.0)

def getHumanName():
    sav = str(gui3d.app.categories['Files'].tasksByName['Save'].fileentry.edit.text())
    if sav == "":
        return 'Untitled'
    else:
        return (os.path.basename(sav).split("."))[0]

def invx(pos):
    return (-pos[0],pos[1],pos[2])

    
