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

The filenames and object names exported are based on the human's current name,
which is the name that was used when saving the MHM model. In case it's unsaved,
the exported files use 'Untitled'.

"""

import os
import re
import projection
import mh
import log
import gui3d
from progress import Progress
from exportutils import collect
from exportutils import matanalyzer
import numpy
import subprocess

def downloadPovRay():
    import webbrowser
    webbrowser.open('http://www.povray.org/download/')

def povrayExport(settings):
    """
    This function exports data in a format that can be used to reconstruct all
    renderable MakeHuman objects in POV-Ray.
    After that, POV-Ray is run and the rendering begins.

    Parameters
    ----------
    settings:
      *Dictionary*. Options passed from the Povray exporter GUI.
    """

    povwatchApp = None
    povwatchPath = ""
    povwatchTimer = 0
    def povwatch():
        if povwatchApp.poll() is not None:
            if os.path.exists(povwatchPath):
                gui3d.app.getCategory('Rendering').getTaskByName('Viewer').setImage(povwatchPath)
                mh.changeTask('Rendering', 'Viewer')
                gui3d.app.statusPersist('Rendering complete. Output path: %s' % povwatchPath)
            else:
                log.notice("POV - Ray did not produce an output file!")
                gui3d.app.statusPersist('Rendering failed!')
            mh.removeTimer(povwatchTimer)

    settings['name'] = re.sub('[^0-9a-zA-Z]+', '_', getHumanName())
    log.message('POV-Ray Export of object: %s', settings['name'])

    settings['resw'] = gui3d.app.settings.get('rendering_width', 800)
    settings['resh'] = gui3d.app.settings.get('rendering_height', 600)

    path = os.path.join(mh.getPath('render'),
                        gui3d.app.settings.get('povray_render_dir', 'pov_output'),
                        "%s.inc" % settings['name'])

    povray_bin = (gui3d.app.settings.get('povray_bin', ''))

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

    if os.path.isfile(povray_bin):

        # Export the files.
        povrayExportMesh2(path, settings)

        outputDirectory = os.path.dirname(path)
        log.debug('out folder: %s', outputDirectory)

        # Prepare command line.
        if os.name == 'nt':
            cmdLine = (povray_bin, 'MHRENDER', '/EXIT')
        else:
            cmdLine = (povray_bin, 'MHRENDER')

        # Pass parameters by writing an .ini file.
        iniFD = open(os.path.join(outputDirectory, 'MHRENDER.ini'), 'w')
        iniFD.write('Input_File_Name="%s.pov"\n' % settings['name'] +
                    '+W%d +H%d +a%s +am2\n' %
                    (settings['resw'], settings['resh'], settings['AA']))
        iniFD.close()

        # Run POV-Ray, and observe it while it renders.
        povwatchApp = subprocess.Popen(cmdLine, cwd = os.path.dirname(path))
        gui3d.app.statusPersist('POV - Ray is rendering.')
        povwatchPath = path.replace('.inc','.png')
        if os.path.exists(povwatchPath):
            os.remove(povwatchPath)
        povwatchTimer = mh.addTimer(1000, lambda: povwatch())

    else:
        gui3d.app.prompt(
            'POV-Ray not found',
            'You don\'t seem to have POV-Ray installed or the path is incorrect.',
            'Download', 'Cancel', downloadPovRay)


def writeCamera(hfile, camera, settings):
    hfile.write("camera {\n  orthographic\n")
    hfile.write("  location <%f,%f,%f>\n" % invx(camera.eye))
    hfile.write("  up <0,1,0>\n  right <%f,0,0>\n" %
                (float(settings['resw'])/float(settings['resh'])))
    hfile.write("  angle %f\n" % camera.fovAngle)
    hfile.write("  look_at <%f,%f,%f>\n}\n\n" % invx(camera.focus))

def writeLights(scene, hfile):
    hflig = open(mh.getSysDataPath('povray/lights.inc'),'r')
    ligfilebuffer = hflig.read()
    hflig.close()
    for light in scene.lights:
        liglines = ligfilebuffer
        liglines = liglines.replace('%%pos%%', '<%f,%f,%f>' % invx(light.position))
        liglines = liglines.replace('%%color%%', '<%f,%f,%f>' % light.color)
        liglines = liglines.replace('%%focus%%', '<%f,%f,%f>' % invx(light.focus))
        liglines = liglines.replace('%%fov%%', str(light.fov))
        liglines = liglines.replace('%%att%%', str(light.attenuation))
        if light.areaLights < 2:
            liglines = liglines.replace('%%arealight%%', '')
        else:
            liglines = liglines.replace(
                '%%arealight%%', 'area_light\n    ' +
                '<{0},0,0>, <0,{0},0>, {1}, {1}\n    '.format(light.areaLightSize, light.areaLights) +
                'adaptive 1\n    jitter circular orient\n')
        hfile.write(liglines)

def writeScene(file, rmeshes, settings):
    hfile = open(file, 'w')
    hfile.write('#include "%s.inc"\n\n' % settings['name'])
    writeCamera(hfile, gui3d.app.modelCamera, settings)
    for rmesh in rmeshes:
        hfile.write(
            "object { \n" +
            "   %s_Mesh2Object \n" % rmesh.name +
            "   rotate <0,0,%s_rz> \n" % settings['name'] +
            "   rotate <0,%s_ry,0> \n" % settings['name'] +
            "   rotate <%s_rx,0,0> \n" % settings['name'] +
            "   translate <{0}_x,{0}_y,{0}_z> \n".format(settings['name']) +
            "   material {%s_Material} \n}\n" % rmesh.name)
    hfile.close()

def writeConstants(hfile, settings):
    """
    This function outputs constants of the model's position and dimensions.
    """
    human = gui3d.app.selectedHuman
    humanPos = invx(human.getPosition())
    humanRot = human.getRotation()

    hfile.write('// Figure position and rotation.\n')
    hfile.write('#declare %s_x = %f;\n' % (settings['name'], humanPos[0]))
    hfile.write('#declare %s_y = %f;\n' % (settings['name'], humanPos[1]))
    hfile.write('#declare %s_z = %f;\n' % (settings['name'], humanPos[2]))
    hfile.write('#declare %s_rx = %f;\n' % (settings['name'], humanRot[0]))
    hfile.write('#declare %s_ry = %f;\n' % (settings['name'],-humanRot[1]))
    hfile.write('#declare %s_rz = %f;\n\n' % (settings['name'], humanRot[2]))
    maxX = 0
    maxY = 0
    maxZ = 0
    minX = 0
    minY = 0
    minZ = 0
    for co in human.mesh.coord:
        maxX = max(maxX, co[0])
        maxY = max(maxY, co[1])
        maxZ = max(maxZ, co[2])
        minX = min(minX, co[0])
        minY = min(minY, co[1])
        minZ = min(minZ, co[2])
    hfile.write('// Figure Dimensions.\n')
    hfile.write('#declare MakeHuman_MaxExtent = < %s, %s, %s>;\n' % (maxX, maxY, maxZ))
    hfile.write('#declare MakeHuman_MinExtent = < %s, %s, %s>;\n' % (minX, minY, minZ))
    hfile.write('#declare MakeHuman_Center    = < %s, %s, %s>;\n' % ((maxX + minX) / 2, (maxY + minY) / 2, (maxZ + minZ) / 2))
    hfile.write('#declare MakeHuman_Width     = %s;\n' % (maxX - minX))
    hfile.write('#declare MakeHuman_Height    = %s;\n' % (maxY - minY))
    hfile.write('#declare MakeHuman_Depth     = %s;\n\n' % (maxZ - minZ))

def povrayExportMesh2(path, settings):
    """
    This function exports data in the form of a mesh2 humanoid object. The POV-Ray
    file generated is fairly inflexible, but is highly efficient.

    Parameters
    ----------

    path:
      *string*. The file system path to the output files that need to be generated.

    settings:
      *dictionary*. Settings passed from the GUI.
    """

    progress = Progress()

    progress(0, 0.01, "Parsing Data")
    # Define some additional file locations
    outputSceneFile = path.replace('.inc', '.pov')
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

    # Write position and dimension constants.
    writeConstants(outputFileDescriptor, settings)

    # Collect and prepare all objects.
    progress(0.01, 0.2, "Analyzing Objects")
    rmeshes,_amt = collect.setupObjects(settings['name'], gui3d.app.selectedHuman, useHelpers=False, hidden=False,
                                            subdivide = settings['subdivide'])

    # Analyze the materials of each richmesh to povray compatible format.
    MAfuncs = {
        'diffusedef': lambda T, S: 'pigment {image_map {%(ft)s "%(fn)s" interpolate 2%(f)s%(t)s}}' % {
            'ft': getImageFType(T.getSaveExt()),
            'fn': T.getSaveName(),
            'f': ' filter all ' + str(S['filter']) if 'filter' in S else "",
            't': ' transmit all ' + str(S['transmit']) if 'transmit' in S else ""},
        'bumpdef': lambda T, S: 'normal {bump_map {%(ft)s "%(fn)s" interpolate 2} %(bi)f}' % {
            'ft': getImageFType(T.getSaveExt()),
            'fn': T.getSaveName(),
            'bi': T.Object.rmesh.material.bumpMapIntensity if T.successfulAlternative == 0 else T.Object.rmesh.material.displacementMapIntensity},
        'alphadef': lambda T, S: 'image_map {%(ft)s "%(fn)s" interpolate 2}' % {
            'ft': getImageFType(T.getSaveExt()),
            'fn': T.getSaveName()},
        'colordef': lambda T, S: 'rgb%(bf)s%(bt)s <#color#%(f)s%(t)s>' % {
            'bf': 'f' if 'filter' in S else "",
            'bt': 't' if 'transmit' in S else "",
            'f': ',' + str(S['filter']) if 'filter' in S else "",
            't': ',' + str(S['transmit']) if 'transmit' in S else ""},
        'makecolor': lambda s, ct = (1,1,1): s.replace('#color#', '%s,%s,%s' % ct),
        'getDiffuseColor': lambda T, S: T.Object.rmesh.material.diffuseColor.asTuple(),
        'getAmbience': lambda T, S: tuple([
            (v1*v2*S['multiply'] if 'multiply' in S else v1*v2)
            for (v1, v2) in zip((1.0,1.0,1.0), #T.Object.rmesh.material.ambientColor.values,
                                settings['scene'].environment.ambience)]),
        'specular': lambda T, S: str(numpy.average(T.Object.rmesh.material.specularColor.values)),
        'roughness': lambda T, S: str(1.0 - T.Object.rmesh.material.shininess),
        'diffuseInt': lambda T, S: str(T.Object.rmesh.material.diffuseIntensity),
        'pigment': lambda s: 'pigment {%s}' % s,
        'lmap': lambda RM: projection.mapSceneLighting(settings['scene'], RM.object.object),
        'blurlev': lambda img, mult: (mult*(float(img.width)/1024)) if img else mult,
        'GBlur': lambda RM: RM.material.sssGScale,
        'RBlur': lambda RM: RM.material.sssRScale,
        'mapmask': lambda RM: projection.mapMask()}
    MAfuncs.update(matanalyzer.imgopfuncs)
    materials = matanalyzer.MaterialAnalysis(rmeshes,
                                 map = {
        'diffuse':              (['mat.diffuse'],                                                                         'diffusedef', ('pigment', ('makecolor', 'colordef', 'getDiffuseColor'))),
        'bump':                 (['mat.bump', 'mat.displacement'],                                                        'bumpdef', None),
        'alpha':                (['mat.transparency', ('getAlpha', 'diffuse')],                                           'alphadef', ('makecolor', 'colordef', ('param', (1,1,1)))),
        'lmap':                  [('getChannel', 'func.lmap', 1)],
        'bllmap':                [('blur', 'lmap', ('blurlev', 'lmap', 'func.GBlur'), 13)],
        'bl2lmap':               [('blur', 'bllmap', ('blurlev', 'lmap', 'func.RBlur'), 13)],
        'sss_bluelmap':          [('compose', ('list', 'black', 'black', 'lmap'))],
        'sss_greenlmap':         [('compose', ('list', 'black', 'bllmap', 'black'))],
        'sss_redlmap':           [('compose', ('list', 'bl2lmap', 'black', 'black'))],
        'sss_alpha':             [('blur', ('shrinkMask', 'func.mapmask', 4), 4, 13)],
        'sss_bluebump':         ([('getChannel', 'bump', 1)],                                                             'bumpdef', None),
        'sss_greenbump':        ([('blur', 'sss_bluebump', ('blurlev', 'sss_bluebump', 'func.GBlur'), 15)],               'bumpdef', None),
        'sss_redbump':          ([('blur', 'sss_greenbump', ('blurlev', 'sss_bluebump', 'func.RBlur'), 15)],              'bumpdef', None),
        'hairbump':             (['bump'],                                                                                'bumpdef', 'alpha.bumpdef'),
        'ambient':              ([None],                                                                                  ('makecolor', 'colordef', 'getAmbience')),
        'specular':             ([None],                                                                                  'specular'),
        'roughness':            ([None],                                                                                  'roughness'),
        'diffuseInt':           ([None],                                                                                  'diffuseInt'),
        'black':                 [('black', 'lmap')]},
                                 functions = MAfuncs)

    # If SSS is enabled, render the lightmaps.
    progress(0.25, 0.6, "Processing SubSurface Scattering")
    povrayProcessSSS(rmeshes, materials, outputDirectory, settings)

    # Write mesh data for the object.
    progress(0.6, 0.9, "Writing Objects")
    povrayWriteMesh2(outputFileDescriptor, rmeshes)

    progress(0.9, 0.95, "Writing Materials")
    writeLights(settings['scene'], outputFileDescriptor)
    writeMaterials(outputFileDescriptor, rmeshes, materials, settings)
    outputFileDescriptor.close()

    # Write .pov scene file.
    writeScene(outputSceneFile, rmeshes, settings)

    progress(0.95, 0.99, "Writing Textures")
    writeTextures(materials, outputDirectory)

    progress(1.0, None, "Finished. Pov-Ray project exported successfully at %s" % outputDirectory)

def writeTextures(materials, outDir):
    progress = Progress(len(materials))

    for mat in materials:
        mat.diffuse.save(outDir)
        progress.substep(0.33)
        mat.bump.save(outDir)
        progress.substep(0.67)
        mat.alpha.save(outDir)
        progress.step()

def writeMaterials(hfile, rmeshes, materials, settings):
    progress = Progress(len(rmeshes))
    for rmesh in rmeshes:
        if rmesh.type == 'Hair':
                hinfile = open (mh.getSysDataPath('povray/hair.inc'),'r')
        elif rmesh.material.sssRScale:  # Determine it has skin.
            if rmesh.material.sssEnabled:
                hinfile = open(mh.getSysDataPath('povray/sss.inc'), 'r')
            else:
                hinfile = open(mh.getSysDataPath('povray/skin.inc'), 'r')
        else:
            hinfile = open(mh.getSysDataPath('povray/object.inc'),'r')
        inlines = hinfile.read()
        hinfile.close()

        inlines = inlines.replace('%%name%%', rmesh.name)
        inlines = inlines.replace('%%pigment%%', materials[rmesh].diffuse.define())
        inlines = inlines.replace('%%pigmentf1%%', materials[rmesh].diffuse.define({'filter':1.0}))
        inlines = inlines.replace('%%alpha%%', materials[rmesh].alpha.define())
        inlines = inlines.replace('%%ambient%%', materials[rmesh].ambient.define())
        inlines = inlines.replace('%%2xambient%%', materials[rmesh].ambient.define({'multiply':2}))
        inlines = inlines.replace('%%diffuse%%', materials[rmesh].diffuseInt.define())
        inlines = inlines.replace('%%specular%%', materials[rmesh].specular.define())
        inlines = inlines.replace('%%roughness%%', materials[rmesh].roughness.define())
        inlines = inlines.replace('%%moist%%', str(settings['moist']))
        if rmesh.material.sssEnabled:
            inlines = inlines.replace(
                '%%bluenormal%%', materials[rmesh].bump.define())
            inlines = inlines.replace(
                '%%greennormal%%', materials[rmesh].sss_greenbump.define())
            inlines = inlines.replace(
                '%%rednormal%%', materials[rmesh].sss_redbump.define())
        if rmesh.type == 'Hair':
            inlines = inlines.replace('%%normal%%', materials[rmesh].hairbump.define())
        else:
            inlines = inlines.replace('%%normal%%', materials[rmesh].bump.define())
        hfile.write(inlines)
        progress.step()

def povrayWriteMesh2(hfile, rmeshes):
    progress = Progress(len(rmeshes))

    for rmesh in rmeshes:
        obj = rmesh.object

        hfile.write('// Mesh2 object definition\n')
        hfile.write('#declare %s_Mesh2Object = mesh2 {\n' % rmesh.name)

        # Vertices
        hfile.write('  vertex_vectors {\n      %s\n  ' % len(obj.coord))
        hfile.write(''.join([('<%.5f,%.5f,%.5f>' % invx(co)) for co in obj.coord]))
        hfile.write('\n  }\n\n')
        progress.substep(0.14)

        # Normals
        hfile.write('  normal_vectors {\n      %s\n  ' % len(obj.vnorm))
        hfile.write(''.join([('<%.5f,%.5f,%.5f>' % invx(no)) for no in obj.vnorm]))
        hfile.write('\n  }\n\n')
        progress.substep(0.28)

        # UV Vectors
        hfile.write('  uv_vectors {\n      %s\n  ' % len(obj.texco))
        hfile.write(''.join([('<%.5f,%.5f>' % tuple(uv)) for uv in obj.texco]))
        hfile.write('\n  }\n\n')
        progress.substep(0.43)

        nTriangles = 2*len(obj.fvert) # MH faces are quads.

        hfile.write('  face_indices {\n      %s\n  ' % nTriangles)
        for fverts in obj.fvert:
            hfile.write('<%s,%s,%s>' % (fverts[0], fverts[1], fverts[2]))
            hfile.write('<%s,%s,%s>' % (fverts[2], fverts[3], fverts[0]))
        hfile.write('\n  }\n\n')
        progress.substep(0.71)


        # UV Indices for each face
        hfile.write('  uv_indices {\n      %s\n  ' % nTriangles)
        for fuv in obj.fuvs:
            hfile.write('<%s,%s,%s>' % (fuv[0], fuv[1], fuv[2]))
            hfile.write('<%s,%s,%s>' % (fuv[2], fuv[3], fuv[0]))
        hfile.write('\n  }\n')

        # Write the end squiggly bracket for the mesh2 object declaration
        hfile.write('\n      uv_mapping\n}\n\n')

        progress.step()

def povrayProcessSSS(rmeshes, materials, outDir, settings):
    progress = Progress(len(rmeshes))

    for rmesh in rmeshes:
        if rmesh.material.sssEnabled:

            # Export blurred channels
            materials[rmesh].sss_bluelmap.save(outDir)
            progress.substep(0.25)
            materials[rmesh].sss_greenlmap.save(outDir)
            progress.substep(0.45)
            materials[rmesh].sss_redlmap.save(outDir)
            progress.substep(0.6)
            materials[rmesh].sss_alpha.save(outDir)
            progress.substep(0.7)
            # Export blurred bump maps
            materials[rmesh].sss_greenbump.save(outDir)
            progress.substep(0.85)
            materials[rmesh].sss_redbump.save(outDir)
            progress.step()

def getHumanName():
    sav = str(gui3d.app.getCategory('Files').getTaskByName('Save').fileentry.edit.text())
    if sav == "":
        return 'Untitled'
    else:
        return (os.path.basename(sav).split("."))[0]

def invx(pos):
    return (-pos[0],pos[1],pos[2])

def getImageFname(name, file, type = None, getext = False):
    out = str(name)
    if type is not None:
        out += '_' + type
    ext = os.path.splitext(file)[-1] if isinstance(file, basestring) else ".png"
    if getext:
        return (out + ext, ext.lower())
    else:
        return out + ext

def getImageDef(name, file, type = None):
    (out, ext) = getImageFname(name, file, type, True)
    ext = getImageFType(ext)
    return ext + ' "' + out + '"'

def getImageFType(ext):
    ext = ext[1:]
    if ext == "tif":
        ext = "tiff"
    elif ext == "jpg":
        ext = "jpeg"
    return ext

def copyTexture(tex, dst):
    import shutil

    if isinstance(tex, basestring):
        shutil.copy(tex, dst)
    else:
        tex.save(dst)
