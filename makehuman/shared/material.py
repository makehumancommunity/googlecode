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
import log

class Color(object):
    def __init__(self, r=0.00, g=0.00, b=0.00):
        self.setValues(r,g,b)

    def setValues(self, r, g, b):
        self.setR(r)
        self.setG(g)
        self.setB(b)

    def getValues(self):
        return [self.r, self.g, self.b]

    values = property(getValues, setValues)

    def setR(self, r):
        self.r = min(0.0, max(1.0, float(r)))

    def setG(self, g):
        self.g = min(0.0, max(1.0, float(g)))

    def setB(self, b):
        self.b = min(0.0, max(1.0, float(b)))

    def __repr__(self):
        return "Color(%s %s %s)" % (self.r,self.g,self.b)

    def copyFrom(self, color):
        if isinstance(color, Color):
            self.setValues(color.r, color.g, color.b)
        else:
            r = color[0]
            g = color[1]
            b = color[2]
            self.setValues(r, g, b)

        return self


class Material(object):
    """
    Material definition.
    Defines the visual appearance of an object when it is rendered (when it is
    set to solid).

    NOTE: Use one material per object! You can use copyFrom() to duplicate
    materials.
    """

    def __init__(self, name="UnnamedMaterial", performConfig=True):
        self.name = name

        self._ambientColor = Color(1.0, 1.0, 1.0)
        self._diffuseColor = Color()
        self._diffuseIntensity = 1.0    # TODO is this useful?
        self._specularColor = Color()
        self._specularIntensity = 0.5   # TODO is this useful?
        self._specularHardness = 0.2
        self._emissiveColor = Color()

        self._opacity = 1.0
        self._translucency = 0.0

        self._diffuseTexture = None
        self._bumpMapTexture = None
        self._bumpMapIntensity = 1.0
        self._normalMapTexture = None
        self._normalMapIntensity = 1.0
        self._displacementMapTexture = None
        self._displacementMapIntensity = 1.0
        self._specularMapTexture = None
        self._specularMapIntensity = 1.0 # TODO do we need this AND specularIntensity?

        self._shader = None
        self._shaderConfig = {}
        self._shaderParameters = {}
        self._shaderDefines = []
        self.shaderChanged = True

        if performConfig:
            self.configureShading()

        self.uvMap = None

    def copyFrom(self, material):
        self.name = material.name

        self._ambientColor.copyFrom(material.ambientColor)
        self._diffuseColor.copyFrom(material.diffuseColor)
        self._diffuseIntensity = material.diffuseIntensity
        self._specularColor.copyFrom(material.specularColor)
        self._specularIntensity = material.specularIntensity
        self._specularHardness = material.specularHardness
        self._emissiveColor.copyFrom(material.emissiveColor)

        self._opacity = material.opacity
        self._translucency = material.translucency

        self._diffuseTexture = material.diffuseTexture
        self._bumpMapTexture = material.bumpMapTexture
        self._bumpMapIntensity = material.bumpMapIntensity
        self._normalMapTexture = material.normalMapTexture
        self._normalMapIntensity = material.normalMapIntensity
        self._displacementMapTexture = material.displacementMapTexture
        self._displacementMapIntensity = material.displacementMapIntensity
        self._specularMapTexture = material.specularMapTexture
        self._specularMapIntensity = material.specularMapIntensity

        self._shader = material.shader
        self._shaderConfig = dict(material._shaderConfig)
        self._shaderParameters = dict(material.shaderParameters)
        self._shaderDefines = list(material.shaderDefines)
        self._shaderChanged = True

        self.uvMap = material.uvMap

        return self

    def fromFile(self, filename):
        """
        Parse .mhmat file and set as the properties of this material.
        """
        try:
            f = open(filename, "rU")
        except:
            f = None
        if f == None:
            log.error("Failed to load material from file %s.", filename)
            return

        for line in f:
            words = line.split()
            if len(words) == 0:
                continue
            if words[0] in ["#", "//"]:
                continue

            shaderConfig_diffuse = True
            shaderConfig_bump = True
            shaderConfig_normal = True
            shaderConfig_displacement = True
            shaderConfig_spec = True
            shaderConfig_vertexColors = True

            if words[0] == "name":
                self.name = words[1]
            if words[0] == "ambientColor":
                self._ambientColor.copyFrom([float(w) for w in words[1:4]])
            if words[0] == "diffuseColor":
                self._diffuseColor.copyFrom([float(w) for w in words[1:4]])
            if words[0] == "diffuseIntensity":
                self._diffuseIntensity = max(0.0, min(1.0, float(words[1])))
            if words[0] == "specularColor":
                self._specularColor.copyFrom([float(w) for w in words[1:4]])
            if words[0] == "specularIntensity":
                self._specularIntensity = max(0.0, min(1.0, float(words[1])))
            if words[0] == "specularHardness":
                self._specularHardness = max(0.0, min(1.0, float(words[1])))
            if words[0] == "emissiveColor":
                self._emissiveColor.copyFrom([float(w) for w in words[1:4]])
            if words[0] == "opacity":
                self._opacity = max(0.0, min(1.0, float(words[1])))
            if words[0] == "translucency":
                self._translucency = max(0.0, min(1.0, float(words[1])))
            if words[0] == "diffuseTexture":
                self._diffuseTexture = words[1]
            if words[0] == "bumpmapTexture":
                self._bumpMapTexture = words[1]
            if words[0] == "bumpmapIntensity":
                self._bumpMapIntensity = max(0.0, min(1.0, float(words[1])))
            if words[0] == "normalmapTexture":
                self._normalMapTexture = words[1]
            if words[0] == "normalmapIntensity":
                self._normalMapIntensity = max(0.0, min(1.0, float(words[1])))
            if words[0] == "displacementmapTexture":
                self._displacementMapTexture = words[1]
            if words[0] == "displacementmapIntensity":
                self._displacementMapIntensity = max(0.0, min(1.0, float(words[1])))
            if words[0] == "specularmapTexture":
                self._specularMapTexture = words[1]
            if words[0] == "specularmapIntensity":
                self._specularMapIntensity = max(0.0, min(1.0, float(words[1])))
            if words[0] == "shader":
                self._shader = words[1]
            if words[0] == "uvMap":
                self.uvMap = words[1]
            if words[0] == "shaderParam":
                if len(words) > 3:
                    self.setShaderParameter(words[1], words[2:])
                else:
                    self.setShaderParameter(words[1], words[2])
            if words[0] == "shaderDefine":
                self.addShaderDefine(words[1])
            if words[0] == "shaderConfig":
                if words[1] == "diffuse":
                    shaderConfig_diffuse = words[2].lower() in ["yes", "enabled", "true"]
                if words[1] == "bump":
                    shaderConfig_bump = words[2].lower() in ["yes", "enabled", "true"]
                if words[1] == "normal":
                    shaderConfig_normal = words[2].lower() in ["yes", "enabled", "true"]
                if words[1] == "displacement":
                    shaderConfig_displacement = words[2].lower() in ["yes", "enabled", "true"]
                if words[1] == "spec":
                    shaderConfig_spec = words[2].lower() in ["yes", "enabled", "true"]
                if words[1] == "vertexColors":
                    shaderConfig_vertexColors = words[2].lower() in ["yes", "enabled", "true"]

        self.configureShading(diffuse=shaderConfig_diffuse, bump=shaderConfig_bump, normal=shaderConfig_normal, displacement=shaderConfig_displacement, spec=shaderConfig_spec, vertexColors=shaderConfig_vertexColors)


    def getAmbientColor(self):
        #return self._ambientColor.values
        return self._ambientColor

    def setAmbientColor(self, color):
        self._ambientColor.copyFrom(color)

    ambientColor = property(getAmbientColor, setAmbientColor)


    def getDiffuseColor(self):
        #return self._diffuseColor.values
        # return self._diffuseColor * self._diffuseIntensity
        return self._diffuseColor

    def setDiffuseColor(self, color):
        self._diffuseColor.copyFrom(color)

    diffuseColor = property(getDiffuseColor, setDiffuseColor)


    def getDiffuseIntensity(self):
        return self._diffuseIntensity

    def setDiffuseIntensity(self, intensity):
        self._diffuseIntensity = min(1.0, max(0.0, intensity))

    diffuseIntensity = property(getDiffuseIntensity, setDiffuseIntensity)


    def getSpecularColor(self):
        #return self._specularColor.values
        return self._specularColor

    def setSpecularColor(self, color):
        self._specularColor.copyFrom(color)

    specularColor = property(getSpecularColor, setSpecularColor)


    def getSpecularIntensity(self):
        return self._specularIntensity

    def setSpecularIntensity(self, intensity):
        self._specularIntensity = min(1.0, max(0.0, intensity))

    specularIntensity = property(getSpecularIntensity, setSpecularIntensity)


    def getSpecularHardness(self):
        """
        The specular hardness or shinyness.
        """
        return self._specularHardness

    def setSpecularHardness(self, hardness):
        """
        Sets the specular hardness or shinyness.
        """
        self._specularHardness = max(0.0, hardness)

    specularHardness = property(getSpecularHardness, setSpecularHardness)


    def getEmissiveColor(self):
        #return self._emissiveColor.values
        return self._emissiveColor

    def setEmissiveColor(self, color):
        self._emissiveColor.copyFrom(color)

    emissiveColor = property(getEmissiveColor, setEmissiveColor)


    def getOpacity(self):
        return self._opacity

    def setOpacity(self, opacity):
        self._opacity = min(1.0, max(0.0, opacity))

    opacity = property(getOpacity, setOpacity)


    def getTranslucency(self):
        return self._translucency

    def setTranslucency(self, translucency):
        self._translucency = min(1.0, max(0.0, translucency))

    translucency = property(getTranslucency, setTranslucency)


    def supportsDiffuse(self):
        return self.diffuseTexture != None

    def supportsBump(self):
        return self.bumpMapTexture != None

    def supportsDisplacement(self):
        return self.displacementMapTexture != None

    def supportsNormal(self):
        return self.normalMapTexture != None

    def supportsSpecular(self):
        return self.specularMapTexture != None

    
    def configureShading(self, diffuse=True, bump = True, normal=True, displacement=True, spec = True, vertexColors = True):
        """
        Configure shading options and set the necessary properties based on
        the material configuration of this object. This configuration applies
        for shaders only (depending on whether the selected shader supports the
        chosen options), so only has effect when a shader is set.
        This method can be invoked even when no shader is set, the chosen
        options will remain effective when another shader is set.
        """
        self._shaderConfig['diffuse'] = diffuse
        self._shaderConfig['bump'] = bump
        self._shaderConfig['normal'] = normal
        self._shaderConfig['displacement'] = displacement
        self._shaderConfig['spec'] = spec
        self._shaderConfig['vertexColors'] = vertexColors

        self._updateShaderConfig()

    def _updateShaderConfig(self):
        import numpy as np

        if not self.shader:
            return

        self.setShaderParameter('ambient', self.ambientColor.values)
        self.setShaderParameter('diffuse', list(np.asarray(self.diffuseColor.values, dtype=np.float32) * self.diffuseIntensity) + [self.opacity])
        self.setShaderParameter('specular', list(np.asarray(self.specularColor.values, dtype=np.float32) * self.specularIntensity) + [self.specularHardness])
        self.setShaderParameter('emissive', self.emissiveColor)

        #self.clearShaderDefines()
        # Don't remove custom defines
        self.removeShaderDefine('DIFFUSE')
        self.removeShaderDefine('BUMPMAP')
        self.removeShaderDefine('NORMALMAP')
        self.removeShaderDefine('DISPLACEMENT')
        self.removeShaderDefine('SPECULARMAP')
        self.removeShaderDefine('VERTEX_COLOR')

        if self._shaderConfig['vertexColors']:
            log.debug("Enabling vertex colors.")
            self.addShaderDefine('VERTEX_COLOR')
        if self._shaderConfig['diffuse'] and self.supportsDiffuse():
            log.debug("Enabling diffuse texturing.")
            self.addShaderDefine('DIFFUSE')
            self.setShaderParameter('diffuseTexture', self.diffuseTexture)
        bump = self._shaderConfig['bump'] and self.supportsBump()
        normal = self._shaderConfig['normal'] and self.supportsNormal()
        if bump and not normal:
            log.debug("Enabling bump mapping.")
            self.addShaderDefine('BUMPMAP')
            self.setShaderParameter('bumpmapTexture', self.bumpMapTexture)
            self.setShaderParameter('bumpmapIntensity', self.bumpMapIntensity)
        if normal:
            log.debug("Enabling normal mapping.")
            self.addShaderDefine('NORMALMAP')
            self.setShaderParameter('normalmapTexture', self.normalMapTexture)
            self.setShaderParameter('normalmapIntensity', self.normalMapIntensity)
        if self._shaderConfig['displacement'] and self.supportsDisplacement():
            log.debug("Enabling displacement mapping.")
            self.addShaderDefine('DISPLACEMENT')
            self.setShaderParameter('displacementmapTexture', self.displacementMapTexture)
            self.setShaderParameter('displacementmapIntensity', self.displacementMapIntensity)
        if self._shaderConfig['spec'] and self.supportsSpecular():
            log.debug("Enabling specular mapping.")
            self.addShaderDefine('SPECULARMAP')
            self.setShaderParameter('specularmapTexture', self.specularMapTexture)
            self.setShaderParameter('specularmapIntensity', self._specularMapIntensity)


    def setShader(self, shader):
        self._shader = shader
        #self.shaderParameters = {}
        #self.clearShaderDefines()
        self._updateShaderConfig()
        self.shaderChanged = True

    def getShader(self):
        return self._shader

    shader = property(getShader, setShader)


    @property
    def shaderParameters(self):
        return self._shaderParameters

    def setShaderParameter(self, name, value):
        # TODO protect against setting parameters defined from material properties?
        self._shaderParameters[name] = value


    @property
    def shaderDefines(self):
        return self._shaderDefines

    def addShaderDefine(self, defineStr):
        if defineStr in self.shaderDefines:
            return
        self._shaderDefines.append(defineStr)
        self._shaderDefines.sort()   # This is important for shader caching

        self.shaderChanged = True

    def removeShaderDefine(self, defineStr):
        try:
            self._shaderDefines.remove(defineStr)
        except:
            pass

        self.shaderChanged = True

    def clearShaderDefines(self):
        self._shaderDefines = []

        self.shaderChanged = True


    def getDiffuseTexture(self):
        return self._diffuseTexture

    def setDiffuseTexture(self, texture):
        self._diffuseTexture = texture
        self._updateShaderConfig()

    diffuseTexture = property(getDiffuseTexture, setDiffuseTexture)


    def getBumpMapTexture(self):
        return self._bumpMapTexture

    def setBumpMapTexture(self, texture):
        self._bumpMapTexture = texture
        self._updateShaderConfig()

    bumpMapTexture = property(getBumpMapTexture, setBumpMapTexture)


    def getBumpMapIntensity(self):
        return self._bumpMapIntensity

    def setBumpMapIntensity(self, intensity):
        self._bumpMapIntensity = intensity
        self._updateShaderConfig()

    bumpMapIntensity = property(getBumpMapIntensity, setBumpMapIntensity)


    def getNormalMapTexture(self):
        return self._normalMapTexture

    def setNormalMapTexture(self, texture):
        self._normalMapTexture = texture
        self._updateShaderConfig()

    normalMapTexture = property(getNormalMapTexture, setNormalMapTexture)


    def getNormalMapIntensity(self):
        return self._normalMapIntensity

    def setNormalMapIntensity(self, intensity):
        self._normalMapIntensity = intensity
        self._updateShaderConfig()

    normalMapIntensity = property(getNormalMapIntensity, setNormalMapIntensity)


    def getDisplacementMapTexture(self):
        return self._displacementMapTexture

    def setDisplacementMapTexture(self, texture):
        self._displacementMapTexture = texture
        self._updateShaderConfig()

    displacementMapTexture = property(getDisplacementMapTexture, setDisplacementMapTexture)


    def getDisplacementMapIntensity(self):
        return self._displacementMapIntensity

    def setDisplacementMapIntensity(self, intensity):
        self._displacementMapIntensity = intensity
        self._updateShaderConfig()

    displacementMapIntensity = property(getDisplacementMapIntensity, setDisplacementMapIntensity)


    def getSpecularMapTexture(self):
        """
        The specular or reflectivity map texture.
        """
        return self._specularMapTexture

    def setSpecularMapTexture(self, texture):
        """
        Set the specular or reflectivity map texture.
        """
        self._specularMapTexture = texture
        self._updateShaderConfig()

    specularMapTexture = property(getSpecularMapTexture, setSpecularMapTexture)


    def getSpecularMapIntensity(self):
        return self._specularMapIntensity

    def setSpecularMapIntensity(self, intensity):
        self._specularMapIntensity = intensity
        self._updateShaderConfig()

    specularMapIntensity = property(getSpecularMapIntensity, setSpecularMapIntensity)


def fromFile(filename):
    """
    Create a material from a .mhmat file.
    """
    mat = Material(performConfig=False)
    mat.fromFile(filename)
    return mat


# TODO this is a duplicate from mh2proxy, but I hope to remove this code from mh2proxy some time. mh2proxy is too bloated
class UVMap:
    def __init__(self, name):
        self.name = name
        self.type = "UvSet"
        self.filename = None
        self.faceMaterials = None
        self.materials = []
        self.faceNumbers = []
        self.texVerts = []
        self.texFaces = []

    def read(self, mesh, filename):
        import numpy as np

        doTexVerts = 1
        doTexFaces = 2    
        doFaces = 3
        doFaceNumbers = 4
        doMaterial = 5

        try:
            fp = open(filename, "r")
        except:
            log.error("Error loading UV map from %s.", filename)
            raise NameError("Cannot open %s" % filename)
                
        status = 0
        for line in fp:
            words = line.split()
            if words == []:
                continue
            elif words[0] == '#':
                if words[1] == "name":
                    self.name = words[2]
                # TODO allow multiple materials for one mesh?
                #elif words[1] == "material":
                #    mat = Material(words[2])
                #    self.materials.append(mat)
                #    status = doMaterial
                elif words[1] == "faceNumbers":
                    status = doFaceNumbers
                elif words[1] == "texVerts":
                    status = doTexVerts
                elif words[1] == "texFaces":
                    status = doTexFaces
            #elif status == doMaterial:
            #    readMaterial(line, mat, self, True)
            elif status == doFaceNumbers:
                self.faceNumbers.append(line)
            elif status == doTexVerts:
                self.texVerts.append([float(words[0]), float(words[1])])
            elif status == doTexFaces:
                texface = [int(word) for word in words]
                self.texFaces.append(texface)
        fp.close()   
        self.filename = filename
            
        nFaces = len(mesh.fvert)                
        self.faceMaterials = np.zeros(nFaces, int)
        fn = 0
        mn = 0
        for line in self.faceNumbers:
            words = line.split()
            if len(words) < 2:
                continue
            elif words[0] == "ft":        
                self.faceMaterials[fn] = int(words[1])
                fn += 1
            elif words[0] == "ftn":
                nfaces = int(words[1])
                mn = int(words[2])
                for n in range(nfaces):
                    self.faceMaterials[fn] = mn
                    fn += 1
        while fn < nFaces:
            self.faceMaterials[fn] = mn
            fn += 1

