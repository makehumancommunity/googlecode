#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Export to id Software's MD5 format.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module implements a plugin to export MakeHuman mesh and skeleton data to id Software's MD5 format.
See http://www.modwiki.net/wiki/MD5MESH_(file_format) for information on the format.

Requires:

- base modules

"""

__docformat__ = 'restructuredtext'

import os
import numpy as np
import numpy.linalg as la
import aljabr
import exportutils
import skeleton

scale = 1

def exportMd5(human, filepath, config):
    """
    This function exports MakeHuman mesh and skeleton data to id Software's MD5 format. 
    
    Parameters
    ----------
   
    human:     
      *Human*.  The object whose information is to be used for the export.
    filepath:     
      *string*.  The filepath of the file to export the object to.
    config:
      *Config*.  Export configuration.
    """

    obj = human.meshData
    config.setHuman(human)
    config.feetOnGround = True    # TODO translate skeleton with feet-on-ground offset too
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    stuffs = exportutils.collect.setupObjects(
        name, 
        human,
        config=config,
        helpers=config.helpers, 
        hidden=config.hidden, 
        eyebrows=config.eyebrows, 
        lashes=config.lashes,
        subdivide=config.subdivide)

    if human.getSkeleton():
        numJoints = human.getSkeleton().getBoneCount() +1 # Amount of joints + the hardcoded origin below
    else:
        numJoints = 1

    f = open(filepath, 'w')
    f.write('MD5Version 10\n')
    f.write('commandline ""\n\n')
    f.write('numJoints %d\n' % numJoints) 
    f.write('numMeshes %d\n\n' % (len(stuffs)))
    
    f.write('joints {\n')
    # Hardcoded root joint
    f.write('\t"%s" %d ( %f %f %f ) ( %f %f %f )\n' % ('origin', -1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    if human.getSkeleton():
        for bone in human.getSkeleton().getBones():
            writeBone(f, bone)
    f.write('}\n\n')

    for stuffIdx, stuff in enumerate(stuffs):
        # stuff.type: None is human, "Proxy" is human proxy, "Clothes" for clothing and "Hair" for hair
        obj = stuff.meshInfo.object

        obj.calcFaceNormals()
        obj.calcVertexNormals()
        obj.updateIndexBuffer()

        numVerts = len(obj.r_coord)
        if obj.vertsPerPrimitive == 4:
            # Quads
            numFaces = len(obj.r_faces) * 2
        else:
            # Tris
            numFaces = len(obj.r_faces)

        f.write('mesh {\n')
        if stuff.texture:
            texfolder,texname = stuff.texture
            f.write('\tshader "%s"\n' % (texname)) # TODO: create the shader file

        f.write('\n\tnumverts %d\n' % numVerts)

        # Collect vertex weights
        if human.getSkeleton():
            bodyWeights = human.getVertexWeights()

            if stuff.type:
                # Determine vertex weights for proxy
                weights = skeleton.getProxyWeights(stuff.proxy, bodyWeights, obj)
            else:
                # Use vertex weights for human body
                weights = bodyWeights
                # Account for vertices that are filtered out
                if stuff.meshInfo.vertexMapping != None:
                    filteredVIdxMap = stuff.meshInfo.vertexMapping
                    weights2 = {}
                    for (boneName, (verts,ws)) in weights.items():
                        verts2 = []
                        ws2 = []
                        for i, vIdx in enumerate(verts):
                            if vIdx in filteredVIdxMap:
                                verts2.append(filteredVIdxMap[vIdx])
                                ws2.append(ws[i])
                        weights2[boneName] = (verts2, ws2)
                    weights = weights2

            # Remap vertex weights to the unwelded vertices of the object (obj.coord to obj.r_coord)
            originalToUnweldedMap = {}
            for unweldedIdx, originalIdx in enumerate(obj.vmap):
                if originalIdx not in originalToUnweldedMap.keys():
                    originalToUnweldedMap[originalIdx] = []
                originalToUnweldedMap[originalIdx].append(unweldedIdx)

            # Build a weights list indexed per vertex
            jointIndexes = {}
            jointIndexes['origin'] = 0
            joints = [None] + human.getSkeleton().getBones() # origin joint is None
            for idx,bone in enumerate(joints):
                if bone:
                    jointIndexes[bone.name] = idx
            vertWeights = {}    # = dict( vertIdx: [ (jointIdx1, weight1), ...])
            for (jointName, (verts,ws)) in weights.items():
                jointIdx = jointIndexes[jointName]
                for idx,v in enumerate(verts):
                    try:
                        for r_vIdx in originalToUnweldedMap[v]:
                            if r_vIdx not in vertWeights.keys():
                                vertWeights[r_vIdx] = []
                            vertWeights[r_vIdx].append((jointIdx, ws[idx]))
                    except:
                        # unused coord
                        pass
            for vert in xrange(numVerts):
                if vert not in vertWeights.keys():
                    # Weight vertex completely to origin joint
                    vertWeights[vert] = [(0, 1.0)]
        else:
            vertWeights = None

        # Write vertices
        wCount = 0
        for vert in xrange(numVerts):
            if obj.has_uv:
                u, v = obj.r_texco[vert]
            else:
                u, v = 0, 0
            if vertWeights == None:
                numWeights = 1
            else:
                numWeights = len(vertWeights[vert])
            # vert [vertIndex] ( [texU] [texV] ) [weightIndex] [weightElem]
            f.write('\tvert %d ( %f %f ) %d %d\n' % (vert, u, 1.0-v, wCount, numWeights))
            wCount = wCount + numWeights

        # Write faces
        # TODO account for masked faces
        f.write('\n\tnumtris %d\n' % numFaces)
        fn = 0
        for fv in obj.r_faces:
            # tri [triIndex] [vertIndex1] [vertIndex2] [vertIndex3]
            f.write('\ttri %d %d %d %d\n' % (fn, fv[2], fv[1], fv[0]))
            fn += 1
            if fv[0] != fv[3]:
                f.write('\ttri %d %d %d %d\n' % (fn, fv[0], fv[3], fv[2]))
                fn += 1

        # Write bone weighting
        if human.getSkeleton():
            f.write('\n\tnumweights %d\n' % wCount)
            wCount = 0
            for idx,co in enumerate(obj.r_coord):
                for (jointIdx, jointWght) in vertWeights[idx]:
                    # Get vertex position in bone space
                    if joints[jointIdx]:
                        invbonematrix = joints[jointIdx].matRestGlobal.copy()
                        invbonematrix[:3,3] *= scale
                        invbonematrix = la.inv(invbonematrix)
                        relPos = np.ones(4, dtype=np.float32)
                        relPos[:3] = co[:3]
                        relPos = np.dot(relPos, invbonematrix)
                        #relPos[:3] -= joints[jointIdx].getRestHeadPos()


                        #toBoneSpace = la.inv(joints[jointIdx].matRestGlobal)
                        #coor[:3] = co[:3]
                        #relPos = np.dot(toBoneSpace, coor.transpose())
                        #relPos = relPos * scale


                        #q = np.asarray( joints[jointIdx].getRestOrientationQuat() )
                        #q1 = -q
                        #q1[3] = q[3]
                        #c = co - joints[jointIdx].getRestHeadPos()
                        #relPos = np.asarray(aljabr.quaternionVectorTransform(q1, c), dtype=np.float32)
                        #relPos = relPos * scale
                    else:
                        relPos = co[:3] * scale
                    # weight [weightIndex] [jointIndex] [weightValue] ( [xPos] [yPos] [zPos] )
                    f.write('\tweight %d %d %f ( %f %f %f )\n' % (wCount, jointIdx, jointWght, relPos[0], relPos[1], relPos[2]))
                    wCount = wCount +1
        else:
            # No skeleton selected: Attach all vertices to the root with weight 1.0
            f.write('\n\tnumweights %d\n' % (numVerts))
            for idx,co in enumerate(obj.r_coord):
                # weight [weightIndex] [jointIndex] [weightValue] ( [xPos] [yPos] [zPos] )
                co = co.copy() * scale
                f.write('\tweight %d %d %f ( %f %f %f )\n' % (idx, 0, 1.0, co[0], co[1], co[2]))
                # Note: MD5 has a z-up coordinate system
        f.write('}\n\n')
    f.close()

def writeBone(f, bone):
    """
  This function writes out information describing one joint in MD5 format. 
  
  Parameters
  ----------
  
  f:     
    *file handle*.  The handle of the file being written to.
  joint:     
    *Bone object*.  The bone object to be processed by this function call.
  """
    if bone.parent:
        parentIndex = bone.parent.index + 1
    else:
        parentIndex = 0 # Refers to the hard-coded root joint
    # "[boneName]"   [parentIndex] ( [xPos] [yPos] [zPos] ) ( [xOrient] [yOrient] [zOrient] )
    pos = bone.getRestHeadPos() * scale
    orientationQuat = bone.getRestOrientationQuat() # TODO transform global rest mat when using z-up coordinates
    qx = orientationQuat[0]
    qy = orientationQuat[1]
    qz = orientationQuat[2]
    w = orientationQuat[3]
    #if w > 0:
    #    qx = -qx
    #    qy = -qy
    #    qz = -qz
    #orientationQuat = [0.0, 0.0, 0.0, 1.0]

    f.write('\t"%s" %d ( %f %f %f ) ( %f %f %f )\n' % (bone.name, parentIndex,
        pos[0], pos[1], pos[2],
        qx, qy, qz))
