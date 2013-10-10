#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import math
import numpy as np

import events3d
from core import G
import glmodule as gl
import matrix

class Camera(events3d.EventHandler):
    """
    Old camera. Works by moving human mesh instead of changing its own orientation.
    """
    def __init__(self):
        super(Camera, self).__init__()

        self.changedPending = False

        self._fovAngle = 25.0
        self._nearPlane = 0.1
        self._farPlane = 100.0
        self._projection = 1
        self._stereoMode = 0
        self._eyeX = 0.0
        self._eyeY = 0.0
        self._eyeZ = 60.0
        self._focusX = 0.0
        self._focusY = 0.0
        self._focusZ = 0.0
        self._upX = 0.0
        self._upY = 1.0
        self._upZ = 0.0

        self.eyeSeparation = 1.0

        self.updated = False

    def changed(self):
        self.callEvent('onChanged', self)
        self.changedPending = False

    def getProjection(self):
        return self._projection

    def setProjection(self, value):
        self._projection = value
        self.changed()

    projection = property(getProjection, setProjection)

    def getFovAngle(self):
        return self._fovAngle

    def setFovAngle(self, value):
        self._fovAngle = value
        self.changed()

    fovAngle = property(getFovAngle, setFovAngle)

    def getNearPlane(self):
        return self._nearPlane

    def setNearPlane(self, value):
        self._nearPlane = value
        self.changed()

    nearPlane = property(getNearPlane, setNearPlane)

    def getFarPlane(self):
        return self._farPlane

    def setFarPlane(self, value):
        self._farPlane = value
        self.changed()

    farPlane = property(getFarPlane, setFarPlane)

    def getEyeX(self):
        return self._eyeX

    def setEyeX(self, value):
        self._eyeX = value
        self.changed()

    eyeX = property(getEyeX, setEyeX)

    def getEyeY(self):
        return self._eyeY

    def setEyeY(self, value):
        self._eyeY = value
        self.changed()

    eyeY = property(getEyeY, setEyeY)

    def getEyeZ(self):
        return self._eyeZ

    def setEyeZ(self, value):
        self._eyeZ = value
        self.changed()

    eyeZ = property(getEyeZ, setEyeZ)

    def getEye(self):
        return (self.eyeX, self.eyeY, self.eyeZ)

    def setEye(self, xyz):
        (self._eyeX, self._eyeY, self._eyeZ) = xyz
        self.changed()

    eye = property(getEye, setEye)

    def getFocusX(self):
        return self._focusX

    def setFocusX(self, value):
        self._focusX = value
        self.changed()

    focusX = property(getFocusX, setFocusX)

    def getFocusY(self):
        return self._focusY

    def setFocusY(self, value):
        self._focusY = value
        self.changed()

    focusY = property(getFocusY, setFocusY)

    def getFocusZ(self):
        return self._focusZ

    def setFocusZ(self, value):
        self._focusZ = value
        self.changed()

    focusZ = property(getFocusZ, setFocusZ)

    def getFocus(self):
        return (self.focusX, self.focusY, self.focusZ)

    def setFocus(self, xyz):
        (self._focusX, self._focusY, self._focusZ) = xyz
        self.changed()

    focus = property(getFocus, setFocus)

    def getUpX(self):
        return self._upX

    def setUpX(self, value):
        self._upX = value
        self.changed()

    upX = property(getUpX, setUpX)

    def getUpY(self):
        return self._upY

    def setUpY(self, value):
        self._upY = value
        self.changed()

    upY = property(getUpY, setUpY)

    def getUpZ(self):
        return self._upZ

    def setUpZ(self, value):
        self._upZ = value
        self.changed()

    upZ = property(getUpZ, setUpZ)

    def getUp(self):
        return (self._upX, self._upY, self._upZ)

    def setUp(self, xyz):
        (self._upX, self._upY, self._upZ) = xyz
        self.changed()

    up = property(getUp, setUp)

    def getScale(self):
        fov = math.tan(self.fovAngle * 0.5 * math.pi / 180.0)
        delta = np.array(self.eye) - np.array(self.focus)
        scale = math.sqrt(np.sum(delta ** 2)) * fov
        return scale

    scale = property(getScale)

    def getStereoMode(self):
        return self._stereoMode

    def setStereoMode(self, value):
        self._stereoMode = value
        self.changed()

    stereoMode = property(getStereoMode, setStereoMode)

    def switchToOrtho(self):
        self._projection = 0
        self._nearPlane = -100.0
        self.changed()

    def switchToPerspective(self):
        self._projection = 1
        self._nearPlane = 0.1
        self.changed()

    def getMatrices(self, eye):
        def lookat(ex, ey, ez, tx, ty, tz, ux, uy, uz):
            e = np.array([ex, ey, ez])
            t = np.array([tx, ty, tz])
            u = np.array([ux, uy, uz])
            return matrix.lookat(e, t, u)

        stereoMode = 0
        if eye:
            stereoMode = self.stereoMode

        aspect = float(max(1, G.windowWidth)) / float(max(1, G.windowHeight))

        if stereoMode == 0:
            # No stereo
            if self.projection:
                proj = matrix.perspective(self.fovAngle, aspect, self.nearPlane, self.farPlane)
            else:
                height = self.scale
                width = self.scale * aspect
                proj = matrix.ortho(-width, width, -height, height, self.nearPlane, self.farPlane)

            mv = lookat(self.eyeX, self.eyeY, self.eyeZ,       # Eye
                        self.focusX, self.focusY, self.focusZ, # Focus
                        self.upX, self.upY, self.upZ)          # Up
        elif stereoMode == 1:
            # Toe-in method, uses different eye positions, same focus point and projection
            proj = matrix.perspective(self.fovAngle, aspect, self.nearPlane, self.farPlane)

            if eye == 1:
                mv = lookat(self.eyeX - 0.5 * self.eyeSeparation, self.eyeY, self.eyeZ, # Eye
                            self.focusX, self.focusY, self.focusZ,                      # Focus
                            self.upX, self.upY, self.upZ)                               # Up
            elif eye == 2:
                mv = lookat(self.eyeX + 0.5 * self.eyeSeparation, self.eyeY, self.eyeZ, # Eye
                            self.focusX, self.focusY, self.focusZ,                      # Focus
                            self.upX, self.upY, self.upZ)                               # Up
        elif stereoMode == 2:
            # Off-axis method, uses different eye positions, focus points and projections
            widthdiv2 = math.tan(math.radians(self.fovAngle) / 2) * self.nearPlane
            left  = - aspect * widthdiv2
            right = aspect * widthdiv2
            top = widthdiv2
            bottom = -widthdiv2

            if eye == 1:        # Left
                eyePosition = -0.5 * self.eyeSeparation
            elif eye == 2:      # Right
                eyePosition = 0.5 * self.eyeSeparation
            else:
                eyePosition = 0.0

            left -= eyePosition * self.nearPlane / self.eyeZ
            right -= eyePosition * self.nearPlane / self.eyeZ

            # Left frustum is moved right, right frustum moved left
            proj = matrix.frustum(left, right, bottom, top, self.nearPlane, self.farPlane)

            # Left camera is moved left, right camera moved right
            mv = lookat(self.eyeX + eyePosition, self.eyeY, self.eyeZ,       # Eye
                        self.focusX + eyePosition, self.focusY, self.focusZ, # Focus
                        self.upX, self.upY, self.upZ)                        # Up

        return proj, mv

    def getTransform(self):
        _, mv = self.getMatrices(0)
        return tuple(np.asarray(mv).flat)

    transform = property(getTransform, None, None, "The transform of the camera.")

    @staticmethod
    def getFlipMatrix():
        t = matrix.translate((0, G.windowHeight, 0))
        s = matrix.scale((1,-1,1))
        return t * s

    def getConvertToScreenMatrix(self, obj = None):
        viewport = matrix.viewport(0, 0, G.windowWidth, G.windowHeight)
        projection, modelview = self.getMatrices(0)
        m = viewport * projection * modelview
        if obj:
            m = m * self.getModelMatrix(obj)
        return self.getFlipMatrix() * m

    def convertToScreen(self, x, y, z, obj = None):
        "Convert 3D OpenGL world coordinates to screen coordinates."
        m = self.getConvertToScreenMatrix(obj)
        sx, sy, sz = matrix.transform3(m, [x, y, z])
        return [sx, sy, sz]

    def convertToWorld2D(self, sx, sy, obj = None):
        "Convert 2D (x, y) screen coordinates to OpenGL world coordinates."
        sz = gl.queryDepth(sx, sy)
        return self.convertToWorld3D(sx, sy, sz, obj)

    def convertToWorld3D(self, sx, sy, sz, obj = None):
        "Convert 3D (x, y, depth) screen coordinates to 3D OpenGL world coordinates."
        m = self.getConvertToScreenMatrix(obj)
        x, y, z = matrix.transform3(m.I, [sx, sy, sz])
        return [x, y, z]

    def getModelMatrix(self, obj):
        return obj.transform

    def updateCamera(self):
        pass

    def setRotation(self, rot):
        human = G.app.selectedHuman
        human.setRotation(rot)
        self.changed()

    def getRotation(self):
        human = G.app.selectedHuman
        return human.getRotation()

    def addRotation(self, axis, amount):
        human = G.app.selectedHuman
        rot = human.getRotation()
        rot[axis] += amount
        human.setRotation(rot)
        self.changed()

    def addTranslation(self, axis, amount):
        human = G.app.selectedHuman
        trans = human.getPosition()
        trans[axis] += amount
        human.setPosition(trans)
        self.changed()

    def addXYTranslation(self, deltaX, deltaY):
        (amountX, amountY, _) = self.convertToWorld3D(deltaX, deltaY, 0.0)
        human = G.app.selectedHuman
        trans = human.getPosition()
        trans[0] += amountX
        trans[1] += amountY
        human.setPosition(trans)
        self.changed()

    def addZoom(self, amount):
        self.eyeZ += amount
        self.changed()

    def getMousePickHuman(self, mouseX, mouseY):
        pass


class OrbitalCamera(Camera):
    """
    Orbital camera.
    A camera that rotates on a sphere that completely encapsulates the human mesh
    (its bounding box) and that has a zoom factor relative to the sphere radius.
    Camera is rotated, instead of the meshes as is the case in the old model.
    """
    def __init__(self):
        super(OrbitalCamera, self).__init__()
        self.center = [0.0, 0.0, 0.0]
        self.radius = 1.0
        self._fovAngle = 90.0

        self.fixedRadius = False
        self.scaleTranslations = True  # Enable to make translations depend on zoom factor (only work when zoomed in)

        # Ortho mode
        self._projection = 0    # TODO properly test with projection mode as well

        self._horizontalRotation = 0.0
        self._verticalInclination = 0.0

        self.zoomFactor = 1.0
        self.translation = [0.0, 0.0, 0.0]

        self.debug = False

    def getHorizontalRotation(self):
        return self._horizontalRotation

    def setHorizontalRotation(self, rot):
        self._horizontalRotation = (rot % 360.0)

    horizontalRotation = property(getHorizontalRotation, setHorizontalRotation)


    def getVerticalInclination(self):
        return self._verticalInclination

    def setVerticalInclination(self, rot):
        self._verticalInclination = (rot % 360.0)

    verticalInclination = property(getVerticalInclination, setVerticalInclination)


    def getModelMatrix(self, obj):
        """
        Calculate model view matrix for this orbital camera
        Currently ignores the actual model transformation
        Note that matrix is constructed in reverse order (using post-multiplication)
        """
        # Note: matrix is constructed with post-multiplication in reverse order

        if obj:
            m = obj.transform   # Apply object transform as last
        else:
            m = np.matrix(np.identity(4))
        # First translate to camera center, then rotate around that center
        m = m * matrix.translate(self.center)   # Move mesh to original position again
        if self.verticalInclination != 0:
            m = m * matrix.rotx(self.verticalInclination)
        if self.horizontalRotation != 0:
            m = m * matrix.roty(self.horizontalRotation)
        # Ignore scale (bounding boxes ignore scale as well, anyway)
        #if any(x != 1 for x in self.scale):
        #    m = m * matrix.scale(self.scale)
        center = [-self.center[0], -self.center[1], -self.center[2]]
        m = m * matrix.translate(center)   # Move mesh to its rotation center to apply rotation

        return m

    def updateCamera(self):
        human = G.app.selectedHuman
        # Set camera to human y center to compensate for varying human height
        bbox = human.getSeedMesh().calcBBox()
        # Note that BB does not take into account human translation, scale or rotation
        humanHalfHeight = (bbox[1][1] - bbox[0][1]) / 2.0
        humanHalfWidth = (bbox[1][0] - bbox[0][0]) / 2.0
        humanHalfDepth = (bbox[1][2] - bbox[0][2]) / 2.0
        hCenter = bbox[0][0] + humanHalfWidth
        vCenter = bbox[0][1] + humanHalfHeight
        zCenter = bbox[0][2] + humanHalfDepth
        if self.scaleTranslations:
            tScale = min(1.0, max(0.0, (math.sqrt(self.zoomFactor)-1))) # clipped linear scale
        else:
            tScale = 1.0
        self.center = [hCenter + self.translation[0] * humanHalfWidth * tScale,
                       vCenter + self.translation[1] * humanHalfHeight * tScale,
                       zCenter + self.translation[2] * humanHalfDepth * tScale]

        if self.fixedRadius:
            # Set fixed radius to avoid auto scaling
            self.radius = 15.0  # bounding sphere of 3m to fit all human sizes
            return

        # Determine radius of camera sphere based on distance from center to
        # furthest human bounding box vertex so that the sphere with arbitrary
        # center completely encloses human bounding box.
        # Get all bounding box vertices
        verts = []
        for x in [0, 1]:
            for y in [0, 1]:
                for z in [0, 1]:
                    verts.append( [bbox[x][0], bbox[y][1], bbox[z][2]] )

        # Calculate all squared distances
        verts = np.asarray(verts, dtype=np.float32)
        verts[:] = verts[:] - self.center
        distances = -np.sum(verts ** 2 , axis=-1)
        maxDistance = math.sqrt( -distances[ np.argsort(distances)[0] ] )

        # Set radius as max distance from bounding box
        self.radius = maxDistance + 1

        if self.debug:
            import log
            log.debug("OrbitalCamera radius: %s", self.radius)

    def addRotation(self, axis, amount):
        if axis == 0:
            self.verticalInclination += amount
        elif axis == 1:
            self.horizontalRotation += amount
        else:
            import log
            log.warning('Orbital camera does not support rotating along Z axis.')
        self.changed()

    def setRotation(self, rot):
        self.verticalInclination = rot[0]
        self.horizontalRotation = rot[1]
        self.changed()

    def getRotation(self):
        return [self.verticalInclination, self.horizontalRotation, 0.0]

    def addTranslation(self, axis, amount):
        # TODO handle movement using keys differently
        self.translation[axis] += (amount)
        if self.translation[axis] < -1.0:
            self.translation[axis] = -1.0
        if self.translation[axis] > 1.0:
            self.translation[axis] = 1.0
        self.changed()

    def addXYTranslation(self, deltaX, deltaY):
        # Get matrix to transform camera X and Y direction into world space
        m = np.matrix(np.identity(4))
        if self.verticalInclination != 0:
            m = m * matrix.rotx(self.verticalInclination)
        if self.horizontalRotation != 0:
            m = m * matrix.roty(self.horizontalRotation)
        xDirection = matrix.transform3(m, [1.0, 0.0, 0.0])
        yDirection = matrix.transform3(m, [0.0, 1.0, 0.0])
        
        # Translation speed is scaled with zoomFactor
        deltaX = (-deltaX/50.0) / self.zoomFactor
        deltaY = (deltaY/50.0) / self.zoomFactor

        offset = (deltaX * xDirection) + (deltaY * yDirection)
        offset[2] = -offset[2]  # Invert Z direction

        self.addTranslation(0, offset[0])
        self.addTranslation(1, offset[1])
        self.addTranslation(2, offset[2])

    def addZoom(self, amount):
        self.zoomFactor += (-amount/4.0)
        if self.zoomFactor < 0.25:
            self.zoomFactor = 0.25
        if self.zoomFactor > 10.0:
            self.zoomFactor = 10.0
        if self.debug:
            import log
            log.debug("OrbitalCamera zoom: %s", self.zoomFactor)

    def getMatrices(self, eye=None):
        # Ignores eye parameter

        #proj, _ = super(OrbitalCamera, self).getMatrices(eye)
        #mv = ..

        def lookat(ex, ey, ez, tx, ty, tz, ux, uy, uz):
            e = np.array([ex, ey, ez])
            t = np.array([tx, ty, tz])
            u = np.array([ux, uy, uz])
            return matrix.lookat(e, t, u)

        aspect = self.getAspect()

        if self.projection:
            # Perspective mode
            proj = matrix.perspective(self.fovAngle, aspect, self.nearPlane, self.farPlane)
        else:
            # Ortho mode
            height = self.getScale() 
            width = height * aspect
            # Camera position around world origin
            proj = matrix.ortho(-width, width, -height, height, self.nearPlane, self.farPlane)

        """
        mv = lookat(self.eyeX, self.eyeY, self.eyeZ,       # Eye
                    self.focusX, self.focusY, self.focusZ, # Focus point (target)
                    self.upX, self.upY, self.upZ)          # Up
        """

        mv = lookat(self.center[0], self.center[1], self.center[2] + self.radius,       # Eye
                    self.center[0], self.center[1], self.center[2], # Focus point (target)
                    self.upX, self.upY, self.upZ)          # Up

        return proj, mv

    def getAspect(self):
        return float(max(1, G.windowWidth)) / float(max(1, G.windowHeight))

    def getScale(self):
        #return self.fovAngle / 30.0     # TODO
        fov = math.tan(self.fovAngle * 0.5 * math.pi / 180.0)
        delta = np.array(self.getEye()) - np.array(self.focus)
        scale = math.sqrt(np.sum(delta ** 2)) * fov
        if self.zoomFactor < 1.0:
            scale = scale / math.sqrt(self.zoomFactor)
        else:
            scale = scale / ( 2*self.zoomFactor - 1)
        if self.debug:
            import log
            log.debug("OrbitalCamera scale: %s", scale)
        return scale

    def getEye(self):
        return [self.center[0], self.center[1], self.center[2] + self.radius]

    def getEyeX(self):
        return self.center[0]

    def getEyeY(self):
        return self.center[1]

    def getEyeZ(self):
        return self.center[2] + self.radius

    # TODO setters

    def getFocusX(self):
        return self.center[0]

    def getFocusY(self):
        return self.center[1]

    def getFocusZ(self):
        return self.center[2]

    def getMousePickHuman(self, mouseX, mouseY):
        self.pickedPos = None

        if G.app.getSelectedFaceGroupAndObject() is None:
            return

        human = G.app.selectedHuman

        self.pickedPos = self.convertToWorld2D(mouseX, mouseY, human.mesh)
        # Transfer this position to transformations relative to bounding box
        # center
        bBox = human.mesh.calcBBox()

        humanHalfWidth = (bBox[1][0] - bBox[0][0]) / 2.0
        hCenter = bBox[0][0] + humanHalfWidth
        self.translation[0] = (self.pickedPos[0] - hCenter) / humanHalfWidth

        humanHalfHeight = (bBox[1][1] - bBox[0][1]) / 2.0
        vCenter = bBox[0][1] + humanHalfHeight
        self.translation[1] = (self.pickedPos[1] - vCenter) / humanHalfHeight

        humanHalfDepth = (bBox[1][2] - bBox[0][2]) / 2.0
        zCenter = bBox[0][2] + humanHalfDepth
        self.translation[2] = (self.pickedPos[2] - zCenter) / humanHalfDepth

        self.changed()
        

def polarToCartesian(polar, radius = 1.0):
    """
    Convert a 2D spherical coordinate into a cartesian 3D coordinate.
    Polar coordinates are expected to be in radians.
    Polar coordinate can be of form (theta, phi), in which case the radius
    parameter is used.
    Polar coordinate can also be of form (r, theta, phi), in which case radius
    parameter is ignored.
    """
    if len(polar) >= 3:
        r = polar[0]
        theta = polar[1]
        phi = polar[2]
    else:
        r = radius
        theta = polar[0]
        phi = polar[1]

    sin_theta = math.sin(theta)

    cart = np.zeros(3, dtype=np.float32)
    cart[0] = r * math.cos(phi) * sin_theta
    cart[1] = r * math.sin(phi) * sin_theta
    cart[2] = r * math.cos(theta)

    return radius * cart

def cartesianToPolar(vect):
    """
    Convert 3D cartesian coordinate into a polar coordinate of the 
    form (r, theta, phi).
    Assumes sphere center to be at origin.
    """
    import numpy.linalg as la

    vect = np.asarray(vect, dtype=np.float32)
    r = la.norm(vect)
    unitVect = vect / r

    theta = math.acos(unitVect[2])       # polar angle
    phi = math.atan2(unit[1], unit[0])   # azimuth

    return [r, theta, phi]
