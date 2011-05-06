import os.path
#!/usr/bin/python
# -*- coding: utf-8 -*-
# We need this for gui controls

import gui3d
import math
from aljabr import * #todo: import the necessities only
from skeleton import Skeleton
from mh2obj import exportObj
from mh import getPath
from linalg import *
from copy import deepcopy
print 'Pose2 plugin imported'

exportPath = getPath('exports')

#torso comes after clavicle because of getJointZones :P
jointZones = ('l-eye','r-eye', 'jaw', 'nose', 'mouth', 'head', 'neck',  
'r-torso-clavicle', 'l-torso-clavicle', 'torso', 'hip', 'pelvis', 
'r-upperarm', 'l-upperarm', 'r-lowerarm', 'l-lowerarm', 'l-hand', 'r-hand', 'r-upperleg', 'l-upperleg', 'r-lowerleg', 'l-lowerleg', 'l-foot', 'r-foot')

zonesToJointsMapping = {
    'pelvis':'joint-pelvis',
    'hip':'joint-spine2',
    'torso':'joint-spine1',
    'neck':'joint-neck',
    'head':'joint-head',
    'r-eye':'joint-r-eye',
    'l-eye':'joint-l-eye',
    'l-torso-clavicle':'joint-l-clavicle',
    'l-upperarm':'joint-l-shoulder',
    'l-lowerarm':'joint-l-elbow',
    'l-hand':'joint-l-hand',
    'r-torso-clavicle':'joint-r-clavicle',
    'r-upperarm':'joint-r-shoulder',
    'r-lowerarm':'joint-r-elbow',
    'r-hand':'joint-r-hand',
    'l-upperleg':'joint-l-upper-leg',
    'l-lowerleg':'joint-l-knee',
    'l-foot':'joint-l-ankle',
    'r-upperleg':'joint-r-upper-leg',
    'r-lowerleg':'joint-r-knee',
    'r-foot':'joint-r-ankle'
}

class PoseTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Pose')      

        self.jointSelected = False
        self.zone = ""
        self.skeleton = Skeleton()
        self.selectedGroups = []
        self.joint = None
                
        self.box = gui3d.GroupBox(self, [10, 80, 9.0], 'Rotation', gui3d.GroupBoxStyle._replace(height=25+36*3+4+24*3+6))

        self.Xslider = gui3d.Slider(self.box, value = 0.0, min = -180.0, max = 180.0, label = "RotX: %d")
        self.Yslider = gui3d.Slider(self.box, value = 0.0, min = -180.0, max = 180.0, label = "RotY: %d")
        self.Zslider = gui3d.Slider(self.box, value = 0.0, min = -180.0, max = 180.0, label = "RotZ: %d")

        self.resetPoseButton = gui3d.Button(self.box, "Reset")
        self.savePoseButton = gui3d.Button(self.box, "Save")
        self.testButton = gui3d.Button(self.box, "Test")

        @self.testButton.event
        def onClicked(event):
            self.mvcTest()
        
        @self.savePoseButton.event
        def onClicked(event):
            exportObj(self.app.selectedHuman.meshData, os.path.join(exportPath, "posed.obj"))

        @self.resetPoseButton.event
        def onClicked(event):
            self.reset()

        @self.Xslider.event
        def onChange(value):
            if self.joint:
                rotation = [value - self.joint.rotation[0], 0.0, 0.0]
                self.joint.rotation[0] = value
                self.rotateJoint(self.joint, self.joint.position, rotation)
                self.app.selectedHuman.meshData.calcNormals()
                self.app.selectedHuman.meshData.update()
            
        @self.Xslider.event
        def onChanging(value):
            pass
            
        @self.Yslider.event
        def onChange(value):
            if self.joint:
                rotation = [0.0, value - self.joint.rotation[1], 0.0]
                self.joint.rotation[1] = value
                self.rotateJoint(self.joint, self.joint.position, rotation)
                self.app.selectedHuman.meshData.calcNormals()
                self.app.selectedHuman.meshData.update()
            
        @self.Yslider.event
        def onChanging(value):
            pass

        @self.Zslider.event
        def onChange(value):
            if self.joint:
                rotation = [0.0, 0.0, value - self.joint.rotation[2]]
                self.joint.rotation[2] = value
                self.rotateJoint(self.joint, self.joint.position,rotation)
                self.app.selectedHuman.meshData.calcNormals()
                self.app.selectedHuman.meshData.update()
            
        @self.Zslider.event
        def onChanging(value):
            pass
            
    def onMouseMoved(self, event):
        if not (self.joint): #(self.jointSelected):
          human = self.app.selectedHuman
          groups = []
          self.zone = self.getJointZones(event.group.name)

          if self.zone:
              for g in human.mesh.faceGroups:
                  if self.zone != "torso":
                    if self.zone in g.name:
                        groups.append(g)
                  elif (self.zone in g.name) and not g.name.endswith("clavicle"):
                    groups.append(g)

              for g in self.selectedGroups:
                  if g not in groups:
                      g.setColor([255, 255, 255, 255])

              for g in groups:
                  if g not in self.selectedGroups:
                      g.setColor([0, 169, 184, 255])
                    
              self.selectedGroups = groups
              self.app.redraw()
    
    def onMouseUp(self, event):
        if self.joint: 
            #self.jointSelected = False
            self.joint = None
        else:
            self.joint = self.skeleton.getJoint(zonesToJointsMapping.get(self.zone))
            self.Xslider.setValue(self.joint.rotation[0])
            self.Yslider.setValue(self.joint.rotation[1])
            self.Zslider.setValue(self.joint.rotation[2])
            #self.jointSelected = True
    
    def onShow(self, event):
        self.app.selectedHuman.storeMesh()
        self.skeleton.update(self.app.selectedHuman.meshData)
        gui3d.TaskView.onShow(self, event)

    def onHide(self, event):
        self.app.selectedHuman.restoreMesh()
        self.app.selectedHuman.meshData.update()
        gui3d.TaskView.onHide(self, event)
        
    def getJointZones(self, groupName):
        for k in jointZones:
            if k in groupName:
              return k
        return None
    
    def mvcTest(self):
        
        angle = 45*degree2rad
        joint = self.skeleton.getJoint('joint-r-shoulder')
        center = joint.position
        
        #get bindings for r-shoulder-joint
        f = open("utils/makepose/r-shoulder-joint.txt")
        jointVerts = [];
        while (1): 
            line = f.readline()
            if not line: break 
            jointVerts.append(int(line));
        f.close()      
        
        #get bindings for r-shoulder-link
        f = open("utils/makepose/r-shoulder-link.txt")
        linkVerts = [];
        while (1): 
            line = f.readline()
            if not line: break 
            linkVerts.append(int(line));
        f.close()
        
        #compute bounding box
        bboxj = calcBBox(self.app.selectedHuman.meshData.verts,  jointVerts)
        bboxl = calcBBox(self.app.selectedHuman.meshData.verts,  linkVerts)   
        
        #recompute bounding box z and y values so they will be connected by 4 vertices in between them
        minY = min(bboxj[0][1], bboxl[0][1])
        maxY = max(bboxj[1][1], bboxl[1][1])
        minZ = min(bboxj[0][2], bboxl[0][2])
        maxZ = max(bboxj[1][2], bboxl[1][2])
        x = (bboxj[1][0] + bboxl[0][0]) /2
        
        #z-y plane
        #y
        bboxj[0][1] = minY - 0.01 # 1cm offset
        bboxl[0][1] = minY - 0.01 # 1cm offset
        bboxj[1][1] = maxY + 0.01 # 1cm offset
        bboxl[1][1] = maxY + 0.01 # 1cm offset
        
        #z
        bboxj[0][2] = minZ - 0.01 # 1cm offset
        bboxl[0][2] = minZ - 0.01 # 1cm offset
        bboxj[1][2] = maxZ + 0.01 # 1cm offset
        bboxl[1][2] = maxZ + 0.01 # 1cm offset
        
        #x that connects
        bboxj[1][0] = x
        bboxl[0][0] = x
        
        tets =  box2Tetrahedrons(bboxj)
        tets2 = deformTets(tets, center, angle) #temporarily rotate about z axis 
        
        #compute mvc weights for each vertex in the bindings of r-shoulder
        for v in jointVerts:
          i,w = computeWeights(v,tets)
        #1. extract the triangular face from bbox for each vertex
        #2. compute mvc weights using the triangle formula
 
        #rotate bbox
        #use mvc algorithm to deform the vertices
    
    def rotateJoint(self, joint, center, rotation, transform=None):                
        #src = self.app.selectedHuman.meshStored
        dst = self.app.selectedHuman.meshData.verts
        if not transform:
            transform = euler2matrix(vmul(rotation,degree2rad), "sxyz")
        else:
            joint.position = vadd(mtransform(transform, vsub(joint.position, center)),center)

        for i in joint.bindedVects:
            dst[i].co = vadd(mtransform(transform, vsub(dst[i].co, center)),center)
        for child in joint.children:
            self.rotateJoint(child, center, rotation, transform)
    
    def reset(self):
        self.Xslider.setValue(0.0)
        self.Yslider.setValue(0.0)
        self.Zslider.setValue(0.0)
        self.app.redraw()
        

category = None
taskview = None

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Posing')
    taskview = PoseTaskView(category)
    print 'pose loaded'
            
    @taskview.event
    def onMouseDown(event):
        part = app.scene3d.getSelectedFacesGroup()
        print part.name

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements

def unload(app):
    print 'pose unloaded'
    
#rotate one side of tets along z-axis
def deformTets(tets, center, angle):
    tets2 = deepcopy(tets)
    for tet in tets2:
        for v in tet:
            if v[0] > center[0]:
                v = vadd(mtransform(makeRotation([0.0,0.0,1.0], vsub(v, center))),center)
    return tets2

#needed for making mvc or harmonic coord. cage
def box2Tetrahedrons(box):
    """
    Subdivides a cuboid into 4 tetrahedrons as shown here:
    U{http://download.tuxfamily.org/makehuman/tutorials/tetrahedron-cube.png}
    subdivision is done with front view of cube having a slice from upper left to lower right corner. Views are with respect to right-hand
    coordinate system
    
    @rtype: list of list of 4 vertices
    @return: a list containing four tetrahedrons whose union is the cuboid. The order of this list is as follows: front left, front right, back 
    right, back left.
    @type  box: list of two vertices
    @param box: two vertices representing minimum and maximum corners of the cuboid
    """
    tetrahedrons = [[],[],[],[]]
    #we traverse 2 diagonals and then the last corner of the tetrahedron whose all angles are 90 degrees
    #traversal is counterclockwise and always starts from the upper corners of the box
    
    #front left
    tet = tetrahedrons[0]
    for i in xrange(0,4):
      tet.append(box[0][:])
    #front upper left corner
    tet[0][2] = box[1][2]
    #back lower left corner
    tet[1][1] = box[1][1]
    #front lower right corner
    tet[2][0] = box[1][0]
    #front lower left corner is ok
    
    #front right
    tet1 = tetrahedrons[1]
    #front upper left corner
    tet1.append(tetrahedrons[0][0][:])
    #front lower right corner    
    tet1.append(tetrahedrons[0][2][:])
    #back upper right corner
    tet1.append(box[1][:])
    #front upper right corner    
    tet1.append(box[1][:])
    tet1[3][1] = box[0][1]
    
    #back right
    tet2 = tetrahedrons[2]
    tet2.append(box[1][:])
    tet2.append(tetrahedrons[0][1][:])
    tet2.append(tetrahedrons[0][2][:])
    tet2.append(box[1][:])
    tet2[3][2] = box[0][2]
    
    #back left
    tet3 = tetrahedrons[3]
    tet3.append(tetrahedrons[2][0][:])
    tet3.append(tetrahedrons[0][0][:])
    tet3.append(tetrahedrons[0][1][:])
    tet3.append(box[1][:])
    tet3[3][0] = box[0][0]
    
    return tetrahedrons

def findTetrahedron(tets, v):
    """
    Given 4 tetrahedrons generated from a box (see box2Tetrahedrons) and given a point v that resides in the box. Find
    the (unique) tetrahedron in which v resides.
    
    @rtype: integer
    @return: the index of tets representing the tetrahedron that contains v
    @type  tets: list of list of 4 vertices
    @param tets:  a list containing four tetrahedrons whose union is a cuboid. The order of this list is as follows: front left, front right, 
    back right, back left.
    @type  v: list of floats
    @param v: a vertex inside a one of the tetrahedrons in tets
    """
    indices = [0,1,2,3]
    
    #front pass (x-z plane)
    diffv = vsub(v, tets[1][1])
    diffBox = vsub(tets[1][0],test[1][1])
    #check tangents
    if fabs(diffv[1]*diffBox[0]) > fabs(diffv[0]*diffBox[1]):
        #point lies about the front face diagonal (see tetrahedron image in box2Tetrahedrons link)
        indices.remove(0) #remove the below tetrahedron
    else: indices.remove(1)
    
    #back pass
    diffv = vsub(v, tets[2][1])
    diffBox = vsub(tets[2][0],test[2][1])
    if fabs(diffv[2]*diffBox[0]) > fabs(diffv[0]*diffBox[2]): #x,z tangent
        indices.remove(2)
    else: indices.remove(3)
    
    #check if we need a top/below pass or a side pass
    if (indices[1] - indices[0])== 2:
        #we need top/below pass, x-y plane
        i,j,k = 1-indices[0],2,indices[0]
        diffv = vsub(v,tets[k][i])
        diffBox = vsub(test[k][j],tets[k][i])
        if fabs(diffv[1]*diffBox[0]) > fabs(diffv[0]*diffBox[1]): #x,y tangent
          indices.remove(indices[0])
        else: indices.remove(indices[1])
    else:
        #we need a side pass, y-z plane
        i,j,k = indices[0],1+indices[0],indices[0]
        diffv = vsub(v,tets[k][i])
        diffBox = vsub(test[k][j],tets[k][i])
        if fabs(diffv[2]*diffBox[1]) > fabs(diffv[1]*diffBox[2]): #y,z tangent
          indices.remove(2*indices[0])
        else: indices.remove(indices[1]-indices[0])
    return indices[0]
    
    
def computeWeights(v,tets):
    i = findTetrahedron(tets,v)
    # w1vt1 + w2vt2 + w3vt3 + w4vt4 = v
    #w1 + w2 + w3 + w4 = 1
    y = [v[0], v[1], v[2], 1]
    A = [0]*16
    for rows in xrange(0,3):
        for cols in xrange(0,4):
          A[rows*4 + cols] = tets[cols][rows]
    w = linsolve(A,y)
    return i,w
    
"""
EVERYTHING BELOW ARE OLD TEST STUFFS!!
"""

def skinTest(self):
    #rotating the shoulders in z desu..
    theta = -45
    rotation = [0.0, 0.0, theta]
    joint = self.skeleton.getJoint('joint-r-shoulder')
    dst = self.app.selectedHuman.meshData.verts
    center = joint.position
    transform = euler2matrix(vmul(rotation,degree2rad), "sxyz")
    joint.radius = 0.6
    l = math.fabs(theta*degree2rad*joint.radius)
    
    for i in joint.bindedVects:
        v= dst[i].co
        d = math.fabs(v[0]-center[0])
        #skinning upper part of shoulder, shape should be like a sphere 
        if d < l and v[1] > center[1]:
          #print "Geronimo"
          #theta = math.fabs(v[0] - center[0])/joint.radius #in radians
          theta2 = theta*(1-bump(d, l))
          t = euler2matrix([0,0,theta2*degree2rad], "sxyz")
          #x = center[0] + joint.radius * math.sin(theta)
          #y = center[1] + joint.radius * math.cos(theta)
          #z = v[2]
          dst[i].co = vadd(mtransform(t, vsub(v, center)),center)
        else:
          dst[i].co = vadd(mtransform(transform, vsub(v, center)),center)
    for child in joint.children:
        self.rotateJoint(child, joint.position, rotation, transform)
    
    self.app.selectedHuman.meshData.calcNormals()
    self.app.selectedHuman.meshData.update()