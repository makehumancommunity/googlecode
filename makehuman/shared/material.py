#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

class Color(object):
    def __init__(self, r=0.00, g=0.00, b=0.00):
        self.setR(r)
        self.setG(g)
        self.setB(b)

    def setR(self, r):
        self.r = min(0.0, max(1.0, float(r)))

    def setG(self, g):
        self.g = min(0.0, max(1.0, float(g)))

    def setB(self, b):
        self.b = min(0.0, max(1.0, float(b)))

    def __repr__(self):
        return "Color(%s %s %s)" % (self.r,self.g,self.b)

    def copyFrom(self, color):
        self.setR(color.r)
        self.setG(color.g)
        self.setB(color.b)

class Material(object):
    """
    Material definition.
    Defines the visual appearance of an object when it is rendered (when it is
    set to solid).

    NOTE: Use one material per object! You can use copyFrom() to duplicate
    materials.
    """

    def __init__(self, name="UnnamedMaterial"):
        self.name = name

        self.ambientColor = Color(1.0, 1.0, 1.0)
        self.diffuseColor = Color()
        self.diffuseIntensity = 1.0
        self.specularColor = Color()
        self.specularIntensity = 0.0
        self.specularHardness = 0.0
        self.emissiveColor = Color()

        self.opacity = 1.0
        self.translucency = 0.0

        self.diffuseTexture = None
        self.bumpTexture = None
        self.bumpMapIntensity = 1.0
        self.normalTexture = None
        self.normalMapIntensity = 1.0
        self.displacementTexture = None
        self.displacementMapIntensity = 1.0
        self.specularTexture = None
        self.specularMapIntensity = 1.0

        self.shader = None
        self.shaderParameters = {}
        self.shaderDefines = []
        self.shaderChanged = True

        self.uvMap = None

    def copyFrom(self, material):
        self.name = material.name

        self.ambientColor = Color().copyFrom(material.ambientColor)
        self.diffuseColor = Color().copyFrom(material.diffuseColor)
        self.diffuseIntensity = material.diffuseIntensity
        self.specularColor = Color().copyFrom(material.specularColor)
        self.specularIntensity = material.specularIntensity
        self.specularHardness = material.specularHardness
        self.emissiveColor = Color().copyFrom(material.emissiveColor)

        self.opacity = material.opacity
        self.translucency = material.translucency

        self.diffuseTexture = material.diffuseTexture
        self.bumpTexture = material.bumpTexture
        self.bumpMapIntensity = material.bumpMapIntensity
        self.normalTexture = material.normalTexture
        self.normalMapIntensity = material.normalMapIntensity
        self.displacementTexture = material.displacementTexture
        self.displacementMapIntensity = material.displacementMapIntensity
        self.specularTexture = material.specularTexture
        self.specularMapIntensity = material.specularMapIntensity

        self.shader = material.shader
        self.shaderParameters = dict(material.shaderParameters)
        self.shaderDefines = list(material.shaderDefines)
        self.shaderChanged = True

        self.uvMap = material.uvMap

    def fromFile(self, filename):
        """
        Parse .mhmat file and set as the properties of this material.
        """
        # TODO parse material file
        return

    def supportsDiffuse(self):
        return self.diffuseTexture != None

    def supportsBump(self):
        return self.bumpTexture != None

    def supportsDisplacement(self):
        return self.displacementTexture != None

    def supportsNormal(self):
        return self.normalTexture != None

    def supportsSpecular(self):
        return self.specularTexture != None


    def setShader(self, shader):
        self.shader = shader
        self.configureShader()
        self.shaderChanged = True

    def configureShader(self, diffuse=True, bump = True, normal=True, displacement=True, spec = True):
        """
        Configure shader options and set the necessary properties based on
        the material configuration of this object.
        """
        self.clearShaderDefines()
        # TODO clear shader parameters as well?
        if diffuse and self.supportsDiffuse():
            self.addShaderDefine('DIFFUSE')
        bump = bump and self.supportsBump()
        normal = normal and self.supportsNormal()
        if bump and not normal:
            self.addShaderDefine('BUMPMAP')
        if normal:
            self.addShaderDefine('NORMALMAP')
        if spec and self.supportsSpecular():
            self.addShaderDefine('SPECULARMAP')

        # Set variables and properties
        if diffuse:
            self.setShaderParameter('diffuseTexture', self.diffuseTexture)
        if normal:
            self.setShaderParameter('normalmapTexture', self.normalTexture)
        if bump:
            self.setShaderParameter('bumpmapTexture', self.bumpTexture)
        if spec:
            self.setShaderParameter('specularmapTexture', self.specularTexture)

    def setShaderParameter(self, name, value):
        self.shaderParameters[name] = value

    def addShaderDefine(self, defineStr):
        if defineStr in self.shaderDefines:
            return
        self.shaderDefines.append(defineStr)
        self.shaderDefines.sort()   # This is important for shader caching

        self.shaderChanged = True

    def removeShaderDefine(self, defineStr):
        self.shaderDefines.remove(defineStr)

        self.shaderChanged = True

    def clearShaderDefines(self):
        self.shaderDefines = []

        self.shaderChanged = True

def fromFile(filename):
    """
    Create a material from a .mhmat file.
    """
    mat = Material()
    mat.fromFile(filename)
    return mat
