#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Renderman Export functions

B{Project Name:}      MakeHuman

B{Product Home Page:} U{http://www.makehuman.org/}

B{Code Home Page:}    U{http://code.google.com/p/makehuman/}

B{Authors:}           Manuel Bastioni, Marc Flerackers

B{Copyright(c):}      MakeHuman Team 2001-2010

B{Licensing:}         GPL3 (see also U{http://sites.google.com/site/makehumandocs/licensing})

B{Coding Standards:}  See U{http://sites.google.com/site/makehumandocs/developers-guide}

Abstract
========

This module implements functions to export a human model in Renderman format and render it
using either the Aqsis or Renderman engine.

The MakeHuman data structures are transposed into renderman objects.

"""

import mh
import os
import aljabr
import files3d
import subprocess
import random
import hair
import time
import math



class MaterialParameter:

    def __init__(self, type, name, val):
        self.type = type
        self.val = val
        self.name = name



class RMRMaterial:

    def __init__(self, name):

        self.name = name
        self.type = "Surface"
        self.parameters = []

    def writeRibCode(self, file):
        file.write('\t\t%s "%s" '%(self.type,self.name))
        for p in self.parameters:
            if p.type == "float":
                file.write('"%s %s" [%f] '%(p.type, p.name, p.val))
            if p.type == "string":
                file.write('"%s %s" "%s" '%(p.type, p.name, p.val))
            if p.type == "color":
                file.write('"%s %s" [%f %f %f] '%(p.type, p.name, p.val[0],  p.val[1],  p.val[2]))
        file.write('\n')

    def setParameter(self, name, val):
        for p in self.parameters:
            if p.name == name:
                p.val = val


class RMRLight:

    lightCounter = 0

    def __init__(self, ribsPath, position = [0,0,0], lookAt = [0,0,0], intensity = 1.0, type = "pointlight", blur = 0.025):

        RMRLight.lightCounter += 1
        self.ribsPath = ribsPath
        self.position = position
        self.lookAt = lookAt
        self.type = type
        self.intensity = intensity
        self.color = [1,1,1]        
        self.counter = RMRLight.lightCounter
        self.samples = 64
        self.blur = blur
        self.AOmap = ""
        self.coneangle = 0.25
        self.roll = None              
        self.shadowMapDataFile = os.path.join(self.ribsPath,"%sshadow%d.zfile"%(self.type, self.counter)).replace('\\', '/')

    def writeRibCode(self, ribfile, n=0):
        # remember z in opengl -> -z in renderman
        if self.type == "pointlight":
             ribfile.write('\tLightSource "pointlight" %i  "from" [%f %f %f] "intensity" %f "color lightcolor" [%f %f %f]\n' % (n, self.position[0], self.position[1], self.position[2],
                      self.intensity, self.color[0], self.color[1], self.color[2]))
        if self.type == "ambient":
            ribfile.write('\tLightSource "ambientlight" %i "intensity" [%f] "color lightcolor" [%f %f %f]\n'%(n, self.intensity, self.color[0], self.color[1], self.color[2]))
        if self.type == "envlight":
            ribfile.write('\tLightSource "envlight" %i "string filename" "%s" "intensity" [%f] "float samples" [ %f ] "float blur" [ %f ]\n'%(n, self.AOmap, self.intensity, self.samples, self.blur))
        if self.type == "shadowspot":
            ribfile.write('\tLightSource "shadowspot" %i "intensity" [%f] "from" [%f %f %f] "to" [%f %f %f] "coneangle" [%f] "string shadowname" ["%s"] "float blur" [%f]\n'%(n, self.intensity,\
             self.position[0],self.position[1],self.position[2], self.lookAt[0], self.lookAt[1], self.lookAt[2],\
             self.coneangle, self.shadowMapDataFile, self.blur))



    def shadowRotate(self, ribfile, angle, x, y, z):
        """
        To place the cam for shadow map
        """
        if math.fabs(angle) > 0.001:
            ribfile.write("Rotate %0.2f %0.2f %0.2f %0.2f\n"% (angle, x, y, z))

    def shadowTranslate(self, ribfile, dx, dy, dz):
        """
        To place the cam for shadow map
        """
        ribfile.write("Translate %0.2f %0.2f %0.2f\n"%(dx, dy, dz))

    def shadowProjection(self, ribfile):
        if self.coneangle != 0.0:
            fov = self.coneangle * 360.0/math.pi
            ribfile.write("Projection \"perspective\" \"fov\" [%0.2f]\n"%(fov))

    def pointToAim(self, ribfile, direction):
        """        
        pointToAim(): rotate the world so the direction vector points in
        positive z by rotating about the y axis, then x. The cosine
        of each rotation is given by components of the normalized
        direction vector. Before the y rotation the direction vector
        might be in negative z, but not afterward.
        """

        if (direction[0]==0) and (direction[1]==0) and (direction[2]==0):
            return

        #The initial rotation about the y axis is given by the projection of
        #the direction vector onto the x,z plane: the x and z components
        #of the direction.

        xzlen = math.sqrt(direction[0]*direction[0]+direction[2]*direction[2]);
        if xzlen == 0:
            if direction[1] < 0:
                yrot = 180
            else:
                yrot = 0
        else:
            yrot = 180*math.acos(direction[2]/xzlen)/math.pi;

        #The second rotation, about the x axis, is given by the projection on
        #the y,z plane of the y-rotated direction vector: the original y
        #component, and the rotated x,z vector from above.

        yzlen = math.sqrt(direction[1]*direction[1]+xzlen*xzlen);
        xrot = 180*math.acos(xzlen/yzlen)/math.pi; #yzlen should never be 0

        if direction[1] > 0:
            self.shadowRotate(ribfile, xrot, 1.0, 0.0, 0.0)
        else:
            self.shadowRotate(ribfile, -xrot, 1.0, 0.0, 0.0)

        #The last rotation declared gets performed first
        if direction[0] > 0:
            self.shadowRotate(ribfile, -yrot, 0.0, 1.0, 0.0)
        else:
            self.shadowRotate(ribfile, yrot, 0.0, 1.0, 0.0)

    def placeShadowCamera(self, ribfile):
        direction = aljabr.vsub(self.lookAt, self.position)
        print "VIEW",self.lookAt, self.position
        print "DIRECTION: ", direction
        self.shadowProjection(ribfile)
        if self.roll:
            self.shadowRotate(ribfile,-self.roll, 0.0, 0.0, 1.0);
        self.pointToAim(ribfile, direction);
        self.shadowTranslate(ribfile, -self.position[0], -self.position[1], -self.position[2])




class RMRHairs:

    def __init__(self, human, hairsClass,ribRepository):

        self.hairsClass = hairsClass
        self.humanToGrowHairs = human
        hair.adjustHair(human.human, self.hairsClass)
        self.hairFilePath = os.path.join(ribRepository, 'hairs.rib')


    def writeCurvesRibCode(self):


        # Write the full hairstyle

        totalNumberOfHairs = 0
        self.hairsClass.humanVerts = self.humanToGrowHairs.meshData.verts

        hairs = self.hairsClass.generateHairToRender()
        print 'Writing hairs'

        hairFile = open(self.hairFilePath, 'w')

        hairFile.write('\t\tBasis "b-spline" 1 "b-spline" 1\n')
        for strands in hairs:

            hDiameter = self.hairsClass.hairDiameterMultiStrand * random.uniform(0.5, 1)
            totalNumberOfHairs += 1
            hairFile.write('Curves "cubic" [%i] "nonperiodic" "P" ['% len(strands))

            #renderman engine understand cubic spline not connected to endpoints, whilest makehuman and blender hair particle connect endpoints
            hairFile.write('%s %s %s ' % (strands[0][0], strands[0][1], -strands[0][2]))  # z * -1 blender  to renderman coords

            for cP in strands:
                hairFile.write('%s %s %s ' % (cP[0], cP[1], -cP[2]))  # z * -1 blender  to renderman coords

            #renderman engine understand cubic spline not connected to endpoints, whilest makehuman and blender hair particle connect endpoints
            hairFile.write('%s %s %s ' % (strands[len(strands)-1][0], strands[len(strands)-1][1],\
            -strands[len(strands)-1][2]))  # z * -1 blender  to renderman coords

            #if random.randint(0, 3) >= 1:
            #    hairFile.write(']\n"N" [')
            #    for cP in strands:
            #            hairFile.write('0 1 0 ')  # arbitrary normals
            hairFile.write(']  "constantwidth" [%s]\n' % hDiameter)

        hairFile.close()
        print 'Totals hairs written: ', totalNumberOfHairs
        #print 'Number of tufts', len(hairs)

    def writeRibCode(self, file):
        archivePath = self.hairFilePath.replace('\\', '/')
        file.write('\t\tReadArchive "%s" '%(archivePath))



class RMNObject:

    def __init__(self, name, obj = None):

        self.groupsDict = {}
        self.facesGroup = None
        self.vertsColorSSS = None
        self.material = None
        self.name = name
        self.facesIndices = []


        if obj:
            self.meshData = obj
            self.name = obj.name
            self.wavefrontPath = os.path.join('data','3dobjs',obj.name)
            self.facesIndices = files3d.loadFacesIndices(self.wavefrontPath, True)
            self.facesUVvalues = obj.uvValues

            #create a dictionary for all facesgroups
            currentGroup = "Empty"
            indices = []
            for faceIdx in self.facesIndices:
                if type(faceIdx) == type("abc"):
                    self.groupsDict[currentGroup]=indices
                    indices = []
                    currentGroup = faceIdx
                else:
                    indices.append(faceIdx)
                self.groupsDict[currentGroup]=indices #add latest group


    def writeRibCode(self, ribPath ):


        facesUVvalues = self.meshData.uvValues #TODO usa direttamente self.

        ribObjFile = file(ribPath, 'w')
        ribObjFile.write('Declare "st" "facevarying float[2]"\n')
        ribObjFile.write('Declare "Cs" "facevarying color"\n')
        ribObjFile.write('SubdivisionMesh "catmull-clark" [')
        for faceIdx in self.facesIndices:
            ribObjFile.write('%i ' % len(faceIdx))
        ribObjFile.write('] ')

        ribObjFile.write('[')
        for faceIdx in self.facesIndices:
            faceIdx.reverse()
            if len(faceIdx) == 3:
                ribObjFile.write('%i %i %i ' % (faceIdx[0][0], faceIdx[1][0], faceIdx[2][0]))
            if len(faceIdx) == 4:
                ribObjFile.write('%i %i %i %i ' % (faceIdx[0][0], faceIdx[1][0], faceIdx[2][0], faceIdx[3][0]))
        ribObjFile.write(']')

        ribObjFile.write('''["interpolateboundary"] [0 0] [] []"P" [''')
        for vert in self.meshData.verts:
            ribObjFile.write('%f %f %f ' % (vert.co[0], vert.co[1], -vert.co[2]))
        ribObjFile.write('] ')

        ribObjFile.write('\n"st" [')
        for faceIdx in self.facesIndices:
            for idx in faceIdx:
                uvIdx = idx[1]
                uvValue = facesUVvalues[uvIdx]
                ribObjFile.write('%s %s ' % (uvValue[0], 1 - uvValue[1]))
        ribObjFile.write(']')
        ribObjFile.close()


    def joinGroupIndices(self):
        for g in self.facesGroup:
            gIndices = self.groupsDict[g]
            self.facesIndices.extend(gIndices)



class RMRHuman(RMNObject):

    def __init__(self, human, name, obj):

        RMNObject.__init__(self, name, obj)

        self.subObjects = []
        self.human = human

        #materials
        self.skinMat = RMRMaterial("skin")
        self.skinMat.parameters.append(MaterialParameter("string", "skintexture", "texture.texture"))
        self.skinMat.parameters.append(MaterialParameter("string", "refltexture", "texture_ref.texture"))
        self.skinMat.parameters.append(MaterialParameter("float", "Ks", 1.5))
        self.skinMat.parameters.append(MaterialParameter("float", "Value", 2.0))


        self.hairMat = RMRMaterial("hair")
        self.hairMat.parameters.append(MaterialParameter("float", "Kd", .5)) 
        self.hairMat.parameters.append(MaterialParameter("float", "Ks", 5)) 
        self.hairMat.parameters.append(MaterialParameter("float", "roughness", 0.08))
        self.hairMat.parameters.append(MaterialParameter("color", "rootcolor", self.human.hairColor))
        self.hairMat.parameters.append(MaterialParameter("color", "tipcolor", self.human.hairColor))

    def subObjectsInit(self):

        #SubObjects
        self.rEyeBall = RMNObject(name = "right_eye_ball")
        self.rEyeBall.groupsDict = self.groupsDict
        self.rEyeBall.meshData = self.meshData
        self.rEyeBall.vertsColorSSS = self.vertsColorSSS
        self.rEyeBall.facesGroup = set(['r-eye-ball'])
        self.rEyeBall.material = self.skinMat
        self.rEyeBall.joinGroupIndices()

        self.lEyeBall = RMNObject(name = "left_eye_ball")
        self.lEyeBall.groupsDict = self.groupsDict
        self.lEyeBall.meshData = self.meshData
        self.lEyeBall.vertsColorSSS = self.vertsColorSSS
        self.lEyeBall.facesGroup = set(['l-eye-ball'])
        self.lEyeBall.material = self.skinMat
        self.lEyeBall.joinGroupIndices()

        self.rCornea = RMNObject(name = "right_cornea")
        self.rCornea.groupsDict = self.groupsDict
        self.rCornea.meshData = self.meshData
        self.rCornea.vertsColorSSS = self.vertsColorSSS
        self.rCornea.facesGroup = set(['r-eye-cornea'])
        self.rCornea.material = self.skinMat
        self.rCornea.joinGroupIndices()

        self.lCornea = RMNObject(name = "left_cornea")
        self.lCornea.groupsDict = self.groupsDict
        self.lCornea.meshData = self.meshData
        self.lCornea.vertsColorSSS = self.vertsColorSSS
        self.lCornea.facesGroup = set(['l-eye-cornea'])
        self.lCornea.material = self.skinMat
        self.lCornea.joinGroupIndices()

        teethGr = set()
        allGr = set()
        nailsGr = set()
        toSubtract = set()
        for f in self.meshData.facesGroups:
            if 'joint' not in f.name:
                allGr.add(f.name)
            if 'teeth' in f.name:
                teethGr.add(f.name)
            if 'nail' in f.name:
                nailsGr.add(f.name)

        self.teeth = RMNObject(name = "teeth")
        self.teeth.groupsDict = self.groupsDict
        self.teeth.meshData = self.meshData
        self.teeth.vertsColorSSS = self.vertsColorSSS
        self.teeth.facesGroup = teethGr
        self.teeth.material = self.skinMat
        self.teeth.joinGroupIndices()

        self.nails = RMNObject(name = "nails")
        self.nails.groupsDict = self.groupsDict
        self.nails.meshData = self.meshData
        self.nails.vertsColorSSS = self.vertsColorSSS
        self.nails.facesGroup = nailsGr
        self.nails.material = self.skinMat
        self.nails.joinGroupIndices()

        for s in [self.rEyeBall,self.lEyeBall,self.rCornea,\
            self.lCornea,self.teeth,self.nails]:
            toSubtract = toSubtract.union(s.facesGroup)

        self.skin = RMNObject(name = "skin")
        self.skin.groupsDict = self.groupsDict
        self.skin.meshData = self.meshData
        self.skin.vertsColorSSS = self.vertsColorSSS
        self.skin.facesGroup = allGr.difference(toSubtract)
        self.skin.material = self.skinMat
        self.skin.joinGroupIndices()

        #parts to render with different material
        self.subObjects = [self.skin,self.rEyeBall,self.lEyeBall,
                        self.rCornea,self.lCornea,self.nails]

    def getObjPosition(self):
        return (self.human.getPosition()[0], self.human.getPosition()[1],\
                self.human.getRotation()[0], self.human.getRotation()[1])


    def __str__(self):
        return "Human Character"


class RMRTexture:

    def __init__(self, picturename, appTexturePath, usrTexturePath):

        self.picturename = os.path.join(appTexturePath, picturename).replace('\\', '/')
        self.texturename = os.path.join(usrTexturePath,os.path.splitext(picturename)[0]+".texture").replace('\\', '/')
        self.swrap = "periodic"
        self.twrap = "periodic"
        self.filterfunc = "box"
        self.swidth = 1
        self.twidth = 1

    def writeRibCode(self, ribfile):
        ribfile.write('MakeTexture "%s" "%s" "%s" "%s" "%s" %d %d\n' %\
                        (self.picturename,self.texturename,self.swrap,self.twrap,\
                        self.filterfunc,self.swidth,self.twidth))


class RMRScene:

    #def __init__(self, MHscene, camera):
    def __init__(self, app):
        MHscene = app.scene3d
        camera = app.modelCamera

        self.app = app       


        #Human in the scene
        self.humanCharacter = RMRHuman(MHscene.selectedHuman, "base.obj", MHscene.getObject("base.obj"))

        self.hairsClass = MHscene.selectedHuman.hairs

        #resources paths
        self.renderPath = mh.getPath('render')
        self.ribsPath = os.path.join(self.renderPath, 'ribFiles')
        self.usrShaderPath = os.path.join(self.ribsPath, 'shaders')
        self.usrTexturePath = os.path.join(self.ribsPath, 'textures')
        self.applicationPath = os.getcwd()  # TODO: this may not always return the app folder
        self.appTexturePath = os.path.join(self.applicationPath, 'data', 'textures')
        self.appObjectPath = os.path.join(self.applicationPath, 'data', '3dobjs')        
        self.worldFileName = os.path.join(self.ribsPath,"world.rib").replace('\\', '/')
        
        #Ambient Occlusion paths
        self.ambientOcclusionFileName = os.path.join(self.ribsPath, "occlmap.rib").replace('\\', '/')
        self.ambientOcclusionData = os.path.join(self.ribsPath,"occlmap.sm" ).replace('\\', '/')
        
        #Shadow path        
        self.shadowFileName = os.path.join(self.ribsPath,"shadow.rib").replace('\\', '/')


        #default lights
        self.light1 = RMRLight(self.ribsPath,[20, 20, 20],intensity = 500, type = "shadowspot", blur = 0.005)
        self.light2 = RMRLight(self.ribsPath,[-20, 20, -20],intensity = 800, type = "shadowspot",  blur = 0.005)
        
        
        #Ambient Occlusion
        #self.light3 = RMRLight([0, 0, 0],intensity = 0.2, type = "ambient")
        self.light3 = RMRLight(self.ribsPath,[0, 0, 0],intensity = 0.2, type = "envlight")
        self.light3.AOmap = self.ambientOcclusionData
        
        #Lights list
        self.lights = [self.light1,self.light2,self.light3]
        

        #creating resources folders
        if not os.path.isdir(self.renderPath):
            os.makedirs(self.renderPath)
        if not os.path.isdir(self.ribsPath):
            os.makedirs(self.ribsPath)
        if not os.path.isdir(self.usrTexturePath):
            os.makedirs(self.usrTexturePath)
        if not os.path.isdir(self.usrShaderPath):
            os.makedirs(self.usrShaderPath)

        #rendering properties
        self.camera = camera

        #textures used in the scene
        texture1 = RMRTexture("texture.tif", self.appTexturePath, self.usrTexturePath)
        texture2 = RMRTexture("texture_ref.tif", self.appTexturePath, self.usrTexturePath)
        self.textures = [texture1,texture2]

    def __str__(self):
        return "Renderman Scene"
        
        
    def writeWorldRibFile(self, fName, shadowMode = None):
        """

        """
        
        #Init and write rib code for hairs
        humanHairs = RMRHairs(self.humanCharacter, self.hairsClass, self.ribsPath)
        self.humanCharacter.subObjectsInit()
        humanHairs.writeCurvesRibCode()
        
        if len(self.humanCharacter.subObjects) < 1:
            print "Warning: AO calculation on 0 objects"
        ribfile = file(fName, 'w')
        for subObj in self.humanCharacter.subObjects:
            print "rendering....", subObj.name
            ribPath = os.path.join(self.ribsPath, subObj.name + '.rib')            
            ribfile.write('\tAttributeBegin\n')
            subObj.writeRibCode(ribPath)
            if shadowMode:
                ribfile.write('\tSurface "null"\n')
            else:
                subObj.material.writeRibCode(ribfile)
            ribfile.write('\t\tReadArchive "%s"\n' % ribPath.replace('\\', '/'))
            ribfile.write('\tAttributeEnd\n')
        ribfile.write('\tAttributeBegin\n')
        self.humanCharacter.hairMat.writeRibCode(ribfile)
        humanHairs.writeRibCode(ribfile)
        ribfile.write('\tAttributeEnd\n')
        ribfile.close()


    def writeRibFile(self, fName):
        """
        This function creates the frame definition for a Renderman scene.
        """

        #Getting global settings
        self.xResolution, self.yResolution = self.app.settings.get('rendering_width', 800), self.app.settings.get('rendering_height', 600)
        self.pixelSamples = [self.app.settings.get('rendering_aqsis_samples', 2),self.app.settings.get('rendering_aqsis_samples', 2)]
        self.shadingRate = self.app.settings.get('rendering_aqsis_shadingrate', 2)
        self.humanCharacter.skinMat.setParameter("Ks", self.app.settings.get('rendering_aqsis_oil', 0.25))

        self.humanCharacter.subObjectsInit()
        pos = self.humanCharacter.getObjPosition()
        imgFile = str(time.time())+".tif"
        ribfile = file(fName, 'w')        

        #Write rib code for textures
        for t in self.textures:
            t.writeRibCode(ribfile)

        #Write headers
        ribfile.write('ScreenWindow -1.333 1.333 -1 1\n')
        ribfile.write('Option "statistics" "endofframe" [1]\n')
        ribfile.write('Option "searchpath" "shader" "%s:&"\n' % self.usrShaderPath.replace('\\', '/'))
        ribfile.write('Option "searchpath" "texture" "%s:&"\n' % self.usrTexturePath.replace('\\', '/'))
        ribfile.write('Projection "perspective" "fov" %f\n' % self.camera.fovAngle)
        ribfile.write('Format %s %s 1\n' % (self.xResolution, self.yResolution))
        ribfile.write('Clipping 0.1 100\n')
        ribfile.write('PixelSamples %s %s\n' % (self.pixelSamples[0], self.pixelSamples[1]))
        ribfile.write('ShadingRate %s \n' % self.shadingRate)
        ribfile.write('Declare "refltexture" "string"\n')
        ribfile.write('Declare "skintexture" "string"\n')
        ribfile.write('Declare "bumptexture" "string"\n')
        ribfile.write('Display "Rendering" "framebuffer" "rgb"\n')
        ribfile.write('Display "+%s" "file" "rgba"\n' % os.path.join(self.ribsPath, imgFile).replace('\\', '/'))
        ribfile.write('\tTranslate %f %f %f\n' % (self.camera.eyeX, -self.camera.eyeY, self.camera.eyeZ)) # Camera
        ribfile.write('\tTranslate %f %f %f\n' % (pos[0], pos[1], 0.0)) # Model
        ribfile.write('\tRotate %f 1 0 0\n' % -pos[2])
        ribfile.write('\tRotate %f 0 1 0\n' % -pos[3])
        ribfile.write('WorldBegin\n')

        for l in self.lights:
            l.writeRibCode(ribfile, l.counter)
        self.writeWorldRibFile(self.worldFileName)
        ribfile.write('\tReadArchive "%s"\n'%(self.worldFileName))        
        ribfile.write('WorldEnd\n')
        ribfile.close()

    def writeShadowFile(self):
        """
        This function creates the frame definition for a Renderman scene.
        """

        ribfile = file(self.shadowFileName, 'w')

        #Write headers
        ribfile.write('Option "limits" "bucketsize" [32 32]\n')
        ribfile.write('Option "limits" "eyesplits" [10]\n')
        ribfile.write('Declare "bias" "float"\n')
        ribfile.write('Hider "hidden" "depthfilter" "midpoint"\n')
        ribfile.write('Clipping 0.01 1000\n')
        ribfile.write('Sides 2\n')
        ribfile.write('Format 1024 1024 1\n')
        ribfile.write('PixelFilter "box" 1 1\n')
        ribfile.write('PixelSamples 1 1\n')
        ribfile.write('ShadingRate 2\n')
        ribfile.write('Hider "hidden" "depthfilter" "midpoint"\n')
        ribfile.write('Option "searchpath" "shader" "%s:&"\n' % self.usrShaderPath.replace('\\', '/'))
        ribfile.write('Option "searchpath" "texture" "%s:&"\n' % self.usrTexturePath.replace('\\', '/'))
        self.writeWorldRibFile(self.worldFileName, 1)

        for l in self.lights:
            if l.type == "shadowspot":
                ribfile.write('FrameBegin %d\n'%(l.counter))
                ribfile.write('Display "%s" "zfile" "z"\n'%(l.shadowMapDataFile))
                l.placeShadowCamera(ribfile)
                ribfile.write('WorldBegin\n')
                ribfile.write('\tSurface "null"\n')
                ribfile.write('\tReadArchive "%s"\n'%(self.worldFileName))
                ribfile.write('WorldEnd\n') 
                ribfile.write('FrameEnd\n') 
                shadowMapDataFileFinal = l.shadowMapDataFile.replace("zfile","shad")                
                ribfile.write('MakeShadow "%s" "%s"\n'%(l.shadowMapDataFile,shadowMapDataFileFinal))
            
        ribfile.close()  
        
    
        




    def copyAOfile(self, src, dst, oldString1, newString1, oldString2, newString2):

        i = open(src)
        o = i.read()
        o = o.replace(oldString1, newString1)
        o = o.replace(oldString2, newString2)
        i.close()

        f = open(dst, 'w')
        f.write(o)
        f.close()
        
    def renderShadow(self):
        self.writeShadowFile()
        command = '%s "%s"' % ('aqsis -progress', self.shadowFileName)
        subprocess.Popen(command, shell=True)
            

    def renderAOdata(self):
        self.writeWorldRibFile(self.worldFileName, 1)
        self.copyAOfile("data/shaders/aqsis/occlmap.rib",\
                        self.ambientOcclusionFileName,\
                        "%DATAPATH%",self.ambientOcclusionData,\
                        "%WORLDPATH%",self.worldFileName)
        command = '%s "%s"' % ('aqsis -progress', self.ambientOcclusionFileName)
        subprocess.Popen(command, shell=True)


    def render(self, ribFileName):
        self.writeShadowFile()
        sceneFileName = os.path.join(self.ribsPath, ribFileName)
        self.writeRibFile(sceneFileName)
        command = '%s "%s"' % ('aqsis -progress', sceneFileName)
        subprocess.Popen(command, shell=True)







