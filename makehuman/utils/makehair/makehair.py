"""
===========================  ===============================================================
Project Name:                **MakeHuman**
Product Home Page:           http://www.makehuman.org/
Google Home Page:            http://code.google.com/p/makehuman/
Authors:                     Manuel Bastioni
Copyright(c):                MakeHuman Team 2001-2009
Licensing:                   GPL3 (see also http://makehuman.wiki.sourceforge.net/Licensing)
Coding Standards:            See http://sites.google.com/site/makehumandocs/developers-guide
===========================  ===============================================================
"""



import Blender
import string
import os
import sys
import math
import random
mainPath = Blender.sys.dirname(Blender.Get('filename'))
sys.path.append(mainPath)
from Blender.Draw import *
from Blender.BGL import *
from Blender import Scene
from Blender import Types
from Blender.Scene import Render
from Blender import Window
from Blender import Group
from Blender import Curve

import subprocess
import hairgenerator

humanMesh = Blender.Object.Get("Base")

hairsClass = hairgenerator.Hairgenerator()

hairDiameterClump = Create(hairsClass.hairDiameterClump)
hairDiameterMultiStrand = Create(hairsClass.hairDiameterMultiStrand)

numberOfHairsClump= Create(hairsClass.numberOfHairsClump)
numberOfHairsMultiStrand= Create(hairsClass.numberOfHairsMultiStrand)

randomFactClump= Create(hairsClass.randomFactClump)
randomFactMultiStrand= Create(hairsClass.randomFactMultiStrand)

sizeClump= Create(hairsClass.sizeClump)
sizeMultiStrand= Create(hairsClass.sizeMultiStrand)

rootColor= Create(hairsClass.rootColor[0],hairsClass.rootColor[1],hairsClass.rootColor[2])
tipColor= Create(hairsClass.tipColor[0],hairsClass.tipColor[1],hairsClass.tipColor[2])

randomPercentage = Create(hairsClass.randomPercentage)
blendDistance = Create(hairsClass.blendDistance)

tipMagnet = Create(hairsClass.tipMagnet)

def convertCoords(obj):

    #print "NAME: ",obj.getName()
    R2D = 57.2957 #Radiant to degree
    objLoc = obj.getLocation()
    objRot = obj.getEuler()
    objSize = obj.getSize()

    LocX =  objLoc[0]
    LocY =  objLoc[1]
    LocZ =  objLoc[2]

    RotX = objRot[0]*R2D
    RotY = objRot[1]*R2D
    RotZ = objRot[2]*R2D

    SizeX = objSize[0]
    SizeY = objSize[1]
    SizeZ = objSize[2]

    #Convert Blender Coords in Renderman Coords
    #rightHandled in leftHandled

    locX = LocX
    locY = LocY
    locZ = -LocZ

    rotX = -RotX
    rotY = -RotY
    rotZ = RotZ

    sizeX = SizeX
    sizeY = SizeY
    sizeZ = SizeZ

    return (locX,locY,locZ,rotX,rotY,rotZ,sizeX,sizeY,sizeZ)




def writeHeader(ribfile,imgFile):

    #ribfile.write('Option "searchpath" "texture" ["%s"]\n'%(texturesdir + ":" + shadowdir))

    display = Scene.GetCurrent()
    context = display.getRenderingContext()
    yResolution = context.imageSizeY()
    xResolution = context.imageSizeX()
    if xResolution >= yResolution:
        factor = yResolution / float(xResolution)
    else:
        factor = xResolution / float(yResolution)

    scene = Blender.Scene.GetCurrent()
    camobj = scene.getCurrentCamera()
    (locX,locY,locZ,rotX,rotY,rotZ,sizeX,sizeY,sizeZ) = convertCoords(camobj)
    camera = Blender.Camera.Get(camobj.getData().name)

    ribfile.write('Option "statistics" "endofframe" [1]\n')
    #ribfile.write("Option \"searchpath\" \"shader\" \"data/shaders/renderman:&\"\n")
    ribfile.write('Projection "perspective" "fov" [%s]\n'%(360.0 * math.atan(factor * 16.0 / camera.lens) /math.pi))
    ribfile.write('Format %s %s 1\n' % (xResolution, yResolution))
    ribfile.write("Clipping %s %s\n" % (camera.clipStart, camera.clipEnd))
    ribfile.write('PixelSamples %s %s\n'%(2, 2))
    ribfile.write('Sides 2\n')
    ribfile.write('Display "00001.tif" "framebuffer" "rgb"\n')
    ribfile.write('Display "+%s" "file" "rgba"\n' % imgFile)

    ribfile.write("\t\tRotate %s 1 0 0\n" %(-rotX))
    ribfile.write("\t\tRotate %s 0 1 0\n" %(-rotY))
    ribfile.write("\t\tRotate %s 0 0 1\n" %(-rotZ))
    ribfile.write("\t\tTranslate %s %s %s\n" %(-locX, -locY, -locZ))

    ribfile.write('WorldBegin\n')


def ambientLight(ribfile):
    if Blender.World.Get() != []:
        world = Blender.World.Get()[0]
        aR = world.amb[0]
        aG = world.amb[1]
        aB = world.amb[2]
        ribfile.write('\tLightSource "ambientlight" 998 "intensity" [1] "color lightcolor" [%s %s %s]\n\n'%(aR, aG, aB))

def writePolyObj(fileObj, mesh):

    objFile = file(fileObj,'w')
    index = 0
    facenum = len(mesh.faces)

    if mesh.hasFaceUV() == 1:
            objFile.write('Declare "st" "facevarying float[2]"\n')

    objFile.write("PointsPolygons [");
    for face in mesh.faces:
        objFile.write('%s '%(len(face.v)))
        index = index + 1

    objFile.write("] ")
    objFile.write("[ ")
    for face in mesh.faces:
        num = len(face.v)
        verticesIdx = []
        for vert in face.v:
            verticesIdx.append(vert)
        verticesIdx.reverse()
        if num == 3 or num == 4:
            for vert in verticesIdx:
                objFile.write('%s ' % vert.index)
    objFile.write("]")
    objFile.write('\n"P" [')
    for vert in mesh.verts:
        objFile.write("%s %s %s " % (vert.co[0], vert.co[1], -vert.co[2]))
    objFile.write('] ')
    #if mesh.faces[0].smooth:
        #objFile.write(' "N" [')
        #for vert in mesh.verts:
            #objFile.write("%s %s %s " % (-vert.no[0], +vert.no[1], -vert.no[2]))
        #objFile.write(']')
    #if mesh.hasVertexColours() == 1:
        #vertexcol = range(len(mesh.verts))
        #objFile.write('\n"Cs" [')
        #for face in mesh.faces:
            #num = len(face.v)
            #if num == 3 or num == 4:
                #for vi in range(len(face.v)):
                    #vertexcol[face.v[vi].index] = face.col[vi]
        #for vc in vertexcol:
            #objFile.write('%s %s %s ' % (vc.r/256.0, vc.g/256.0, vc.b/256.0))
        #objFile.write(']')

    if mesh.hasFaceUV() == 1:
        objFile.write('\n"st" [')
        for face in mesh.faces:
            num = len(face.v)
            if num == 3 or num == 4:
                for vi in range(len(face.v)):
                    objFile.write('%s %s ' % (face.uv[vi][0], 1.0 - face.uv[vi][1]))
        objFile.write(']')
    objFile.write('\n')
    objFile.close()


def writeSubdividedObj(ribPath, mesh):

    objFile = open(ribPath,'w')
    if mesh.hasFaceUV() == 1:
        objFile.write('Declare "st" "facevarying float[2]"\n')
    objFile.write('SubdivisionMesh "catmull-clark" [')
    for face in mesh.faces:
        num = len(face.v)
        objFile.write('%s '%(num))
    objFile.write(']\n[')
    for face in mesh.faces:
        for vert in face.v:
            objFile.write('%s ' % vert.index)
    objFile.write(']\n["interpolateboundary"] [0 0] [] []\n"P" [')
    for vert in mesh.verts:
        objFile.write("%s %s %s " % (vert.co[0], vert.co[1], -vert.co[2]))
    objFile.write(']')

    if mesh.hasFaceUV() == 1:
        objFile.write('\n"st" [')
        for face in mesh.faces:
            num = len(face.v)
            if num == 3 or num == 4:
                for vi in range(len(face.v)):
                    objFile.write('%s %s ' % (face.uv[vi][0], 1.0 - face.uv[vi][1]))
        objFile.write(']')
    if mesh.hasVertexColours() == 1:
        vertexcol = range(len(mesh.verts))
        objFile.write('\n"Cs" [')
        for face in mesh.faces:
            num = len(face.v)
            if num == 3 or num == 4:
                for vi in range(len(face.v)):
                    vertexcol[face.v[vi].index] = face.col[vi]
        for vc in vertexcol:
            objFile.write('%s %s %s ' % (vc.r/256.0, vc.g/256.0, vc.b/256.0))
        objFile.write(']')
    objFile.write('\n')


def writeHairs(ribRepository):

    global rootColor,tipColor,hairDiameter,preview,hairsClass
    totalNumberOfHairs = 0

    for hSet in hairsClass.hairStyle:

        if "clump" in hSet.name:
            hDiameter = hairsClass.hairDiameterClump*random.uniform(0.5,1)
        else:
            hDiameter = hairsClass.hairDiameterMultiStrand*random.uniform(0.5,1)

        hairName = "%s/%s.rib"%(ribRepository,hSet.name)
        hairFile = open(hairName,'w')
        hairFile.write('\t\tDeclare "rootcolor" "color"\n')
        hairFile.write('\t\tDeclare "tipcolor" "color"\n')
        hairFile.write('\t\tSurface "hair" "rootcolor" [%s %s %s] "tipcolor" [%s %s %s]'%(rootColor.val[0],\
                    rootColor.val[1],rootColor.val[2],\
                    tipColor.val[0],tipColor.val[1],tipColor.val[2]))
        #hairFile.write('\t\tSurface "matte" ')
        hairFile.write('\t\tBasis "b-spline" 1 "b-spline" 1  ')
        hairFile.write('Curves "cubic" [')
        for hair in hSet.hairs:
            totalNumberOfHairs += 1
            hairFile.write('%i ' % len(hair.controlPoints))
        hairFile.write('] "nonperiodic" "P" [')
        for hair in hSet.hairs:
            for cP in hair.controlPoints:
                hairFile.write("%s %s %s " % (cP[0],cP[1],cP[2]))
        hairFile.write(']  "constantwidth" [%s]' % (hDiameter))
        hairFile.close()
    print "TOTAL HAIRS WRITTEN: ",totalNumberOfHairs
    print "NUMBER OF TUFTS",len(hairsClass.hairStyle)



def writeLamps(ribfile):
    ribfile.write('\tLightSource "ambientlight" 998 "intensity" [.05] "color lightcolor" [1 1 1]')
    numLamp = 0
    for obj in Blender.Object.Get():
        if obj.getType() == "Lamp":
            lamp = obj.getData()
            intensity = lamp.getEnergy()*10
            numLamp += 1
            (locX,locY,locZ,rotX,rotY,rotZ,sizeX,sizeY,sizeZ) = convertCoords(obj)
            ribfile.write('\tLightSource "pointlight" %s "from" [%s %s %s] "intensity" %s  "lightcolor" [%s %s %s] \n' %(numLamp,locX, locY, locZ, intensity, lamp.col[0], lamp.col[1], lamp.col[2]))


def writeHuman(ribRepository):

    global humanMesh
    meshData = humanMesh.getData()
    ribPath = "%s/base.obj.rib"%(ribRepository)
    writePolyObj(ribPath, meshData)

def writeFooter(ribfile):
    ribfile.write("\tAttributeBegin\n")
    #ribfile.write("\t\tRotate -90 1 0 0\n")
    ribfile.write("\t\tSurface \"matte\"\n")
    ribfile.write("\t\tReadArchive \"ribObjs/base.obj.rib\"\n")
    ribfile.write("\tAttributeEnd\n")
    ribfile.write("WorldEnd\n")


def writeBody(ribfile, ribRepository):
    global nHairs,alpha
    print "Calling create objects"

    for hSet in hairsClass.hairStyle:
        ribObj = "%s/%s.rib"%(ribRepository,hSet.name)
        print "RIBOBJ",ribObj
        ribfile.write('\tAttributeBegin\n')
        ribfile.write('\t\tReadArchive "%s"\n' %(ribObj))
        ribfile.write('\tAttributeEnd\n')


def applyTransform(vec, matrix):
	x, y, z = vec
	xloc, yloc, zloc = matrix[3][0], matrix[3][1], matrix[3][2]
	return	x*matrix[0][0] + y*matrix[1][0] + z*matrix[2][0] + xloc,\
			x*matrix[0][1] + y*matrix[1][1] + z*matrix[2][1] + yloc,\
			x*matrix[0][2] + y*matrix[1][2] + z*matrix[2][2] + zloc

def updateHumanVerts():
    for v in humanMesh.getData().verts:
        v1 = [v.co[0],v.co[1],-v.co[2]] #-1 +z to convert in renderman coord
        hairsClass.humanVerts.append(v1)


def blenderCurves2MHData():
    global hairsClass

    hairsClass.resetHairs()
    hairCounter = 0
    groups = Group.Get()
    for group in groups:
        g = hairsClass.addGuideGroup(group.name)
        for obj in list(group.objects):
            data = obj.getData()
            name = obj.getName()
            if type(data) == Types.CurveType:
                matr = obj.getMatrix()
                controlPoints = []
                for curnurb in data:
                    for p in curnurb:
                        p1 = [p[0],p[1],p[2]]
                        worldP = applyTransform(p1,matr) #convert the point in absolute coords
                        p2 = [worldP[0],worldP[1],-worldP[2]] #convert from Blender coord to Renderman coords
                        controlPoints.append(p2)
                    hairsClass.addHairGuide(controlPoints, name, g)
                    hairCounter += 1

def MHData2BlenderCurves():
    global hairsClass
    for group in hairsClass.guideGroups:
        for guide in group.guides:
            guide = Blender.Object.Get(guide.name)
            data = guide.getData()
            curnurb = data[0] #we assume each curve has only one nurbs
            for p in curnurb:
                print p





def adjustGuides(path):
    """

    """
    global hairsClass
    humanMeshVerts = Blender.Object.Get("Base").getData().verts
    try:
        fileDescriptor = open(path)
    except:
        print "Impossible to load %s"%(path)
        return

    #Guides and Deltas have the same name, so it's
    #easy to associate them. Anyway we must a dd a check to
    #be sure the hairs to adjust are the same as saved in
    #the file. 
    deltaGuides = {}
    for data in fileDescriptor:
        datalist = data.split()
        if datalist[0] == "delta":
            name = datalist[1]
            guidesDelta = datalist[2:]
            deltaGuides[name] = hairsClass.extractSubList(guidesDelta,4)

    for group in hairsClass.guideGroups:
        for g in group.guides:
            guide = Blender.Object.Get(g.name)
            curvsDelta = deltaGuides[g.name]
            data = guide.getData()
            curnurb = data[0] #we assume each curve has only one nurbs
            for i in range(len(curvsDelta)):
                cpDelta = curvsDelta[i]
                parentVertIndex = int(cpDelta[0])
                v = humanMeshVerts[parentVertIndex]
                cPoint = [0,0,0,1]
                cPoint[0] = v.co[0] + float(cpDelta[1])
                cPoint[1] = v.co[1] + float(cpDelta[2])
                cPoint[2] = v.co[2] - float(cpDelta[3]) # mul -1 to convert from renderman to Blender
                data.setControlPoint(0, i, cPoint)
                data.update()


def generateHairs():
    global hairsClass
    blenderCurves2MHData()
    hairsClass.generateHairStyle1()
    hairsClass.generateHairStyle2()





def saveRib(fName):
    global hairsClass
    engine = "aqsis"

    #d0 is [path,filename]
    #d1 is [name,extension]

    d0 = os.path.split(fName)
    d1 = os.path.splitext(d0[1])

    imageName = d1[0]+'.tif'
    fName = d1[0]+'.rib'

    print "Saved rib in ",  fName
    print "Saved image in ", imageName
    objectsDirectory = 'ribObjs'
    generateHairs()
    if not os.path.isdir(objectsDirectory):
        os.mkdir(objectsDirectory)
    theFile = open(fName,'w')
    writeHuman(objectsDirectory)
    writeHeader(theFile,imageName)
    writeLamps(theFile)
    writeBody(theFile,objectsDirectory)
    writeFooter(theFile)
    writeHairs(objectsDirectory)
    theFile.close()

    hairsClass.resetHairs()

    command = '%s %s'%('cd', mainPath) #To avoid spaces in path problem
    subprocess.Popen(command, shell=True) #We move into current dir

    if engine == "aqsis":
        subprocess.Popen("aqsl hair.sl -o hair.slx", shell=True)
        command = '%s %s'%('aqsis', fName)
    if engine == "pixie":
        subprocess.Popen("sdrc hair.sl -o hair.sdr", shell=True)
        command = '%s %s'%('rndr', fName)
    subprocess.Popen(command, shell=True)

def saveHairsFile(path):
    updateHumanVerts()
    blenderCurves2MHData()
    hairsClass.saveHairs(path)

def loadHairsFile(path):
    hairsClass.loadHairs(path)

    scn = Scene.GetCurrent()
    for group in hairsClass.guideGroups:
        grp= Group.New(group.name)
        for guide in group.guides:
            startP = guide.controlPoints[0]
            cu = Curve.New()
            #Note: hairs are stored using renderman coords system, so
            #z is multiplied for -1 to conver renderman coords to Blender coord
            cu.appendNurb([startP[0],startP[1],-startP[2],1])
            cu_nurb= cu[0]
            for cP in guide.controlPoints[1:]:
                cu_nurb.append([cP[0],cP[1],-cP[2],1])
            ob = scn.objects.new(cu)
            grp.objects.link(ob)
    Window.RedrawAll()




###############################INTERFACE#####################################

def draw():
    global hairDiameterClump,hairDiameterMultiStrand,alpha
    global numberOfHairsClump,numberOfHairsMultiStrand,randomFactClump,randomFactMultiStrand
    global tipMagnet,sizeMultiStrand,sizeClump,blendDistance
    global samples,preview,randomPercentage
    global rootColor,tipColor

    glClearColor(0.5, 0.5, 0.5, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)
    buttonY = 10

    Button("Exit", 1, 210, buttonY, 100, 20)
    Button("Rendering", 2, 10, buttonY, 200, 20)

    tipMagnet= Slider("Clump tipMagnet: ", 3, 10, buttonY+40, 300, 18, tipMagnet.val, 0, 1, 0,"How much tip of guide attract generated hairs")
    randomFactClump= Slider("Clump Random: ", 3, 10, buttonY+60, 300, 18, randomFactClump.val, 0, 1, 0,"Random factor in clump hairs generation")
    numberOfHairsClump= Slider("Clump hairs num.: ", 3, 10, buttonY+80, 300, 18, numberOfHairsClump.val, 1, 100, 0, "Number of generated hair for each guide. Note that value of x mean x*x hairs")
    sizeClump= Slider("Clump size: ", 3, 10, buttonY+100, 300, 18, sizeClump.val, 0.0, 0.5, 0,"Size of clump volume")
    hairDiameterMultiStrand = Slider("Clump hair diam.: ", 0, 10, buttonY+120, 300, 20, hairDiameterMultiStrand.val, 0, 0.05, 0,"Diameter of hairs used in strand interpolation")


    blendDistance= Slider("Strand blending dist.: ", 3, 10, buttonY+160, 300, 18, blendDistance.val, 0, 2, 0)
    randomFactMultiStrand= Slider("Strand Random: ", 3, 10, buttonY+180, 300, 18, randomFactMultiStrand.val, 0, 1, 0)
    numberOfHairsMultiStrand= Slider("Strand hairs num. ", 3, 10, buttonY+200, 300, 18, numberOfHairsMultiStrand.val, 1, 1000, 0)
    sizeMultiStrand= Slider("Strand volume: ", 3, 10, buttonY+220, 300, 18, sizeMultiStrand.val, 0.0, 0.5, 0)
    hairDiameterClump = Slider("Strand hair diam.: ", 0, 10, buttonY+240, 300, 20, hairDiameterClump.val, 0, 0.05, 0,"Diameter of hairs used in clump interpolation")

    randomPercentage= Slider("Random perc.: ", 3, 10, buttonY+280, 300, 18, randomPercentage.val, 0.0, 1.0, 0)
    rootColor = ColorPicker(3, 10, buttonY+300, 150, 20, rootColor.val,"Color of root")
    tipColor = ColorPicker(3, 160, buttonY+300, 150, 20, tipColor.val,"Color of tip")
    Button("Save", 4, 10, buttonY+320, 150, 20)
    Button("Load", 5, 160, buttonY+320, 150, 20)

    glColor3f(1, 1, 1)
    glRasterPos2i(10, buttonY+360)
    Text("makeHair 1.0 beta2" )

def event(evt, val):
    if (evt== QKEY and not val): Exit()

    if (evt== TKEY and not val):
        blenderCurves2MHData()
        #MHData2BlenderCurves()

        Window.FileSelector (adjustGuides, "Load curve file")

def bevent(evt):
    global tuftSize,blendDistance
    global nHairs,tipMagnet,randomFact

    if   (evt== 1): Exit()

    elif (evt== 2):
        saveRib("hair-test.rib")

    elif (evt== 3):

        hairsClass.tipMagnet = tipMagnet.val
        hairsClass.hairDiameterClump = hairDiameterClump.val
        hairsClass.hairDiameterMultiStrand = hairDiameterMultiStrand.val
        hairsClass.numberOfHairsClump= numberOfHairsClump.val
        hairsClass.numberOfHairsMultiStrand= numberOfHairsMultiStrand.val
        hairsClass.randomFactClump= randomFactClump.val
        hairsClass.randomFactMultiStrand= randomFactMultiStrand.val
        hairsClass.randomPercentage= randomPercentage.val
        hairsClass.sizeClump= sizeClump.val
        hairsClass.sizeMultiStrand= sizeMultiStrand.val
        hairsClass.blendDistance= blendDistance.val

    elif (evt== 4):
        Window.FileSelector (saveHairsFile, "Save hair data")
    elif (evt== 5):
        Window.FileSelector (loadHairsFile, "Load hair data")

    Window.RedrawAll()

Register(draw, event, bevent)
