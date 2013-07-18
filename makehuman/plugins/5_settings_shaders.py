#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Manuel Bastioni, Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import os
import gui3d
import gui
import log
import shader
import numpy as np

class ShaderTaskView(gui3d.TaskView):
    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Shading')

        self.human = gui3d.app.selectedHuman

        shaderBox = self.addLeftWidget(gui.GroupBox('Shader'))
        self.shaderList = shaderBox.addWidget(gui.ListView())
        self.shaderList.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)

        self.shaderConfBox = self.addLeftWidget(gui.GroupBox('Shader config'))
        shaderConfig = self.human.material.shaderConfig
        for name in shaderConfig:
            chkBox = gui.CheckBox(name, shaderConfig[name])
            self.shaderConfBox.addWidget(chkBox)
            @chkBox.mhEvent
            def onClicked(event):
                shaderConfig = dict()
                for child in self.shaderConfBox.children:
                    shaderConfig[str(child.text())] = child.isChecked()
                self.human.mesh.configureShading(**shaderConfig)

        if not shader.Shader.supported():
            log.notice('Shaders not supported')
            self.shaderList.setEnabled(False)

        self.paramBox = self.addRightWidget(gui.GroupBox('Parameters'))

        materialBox = self.addRightWidget(gui.GroupBox('Material settings'))

        @self.shaderList.mhEvent
        def onClicked(item):
            self.setShader(unicode(item.getUserData()))

    def listShaders(self, dir = 'data/shaders/glsl'):
        shaders = set()
        for name in os.listdir(dir):
            path = os.path.join(dir, name)
            if not os.path.isfile(path):
                continue
            if not name.endswith('_shader.txt'):
                continue
            # TODO clean up
            name, type = name[:-11].rsplit('_',1)
            if type not in ['vertex', 'geometry', 'fragment']:
                continue
            shaders.add(name)

        self.shaderList.clear()
        firstItem = self.shaderList.addItem('[None]', data = '')
        if self.human.mesh.shader:
            shaderName = os.path.basename(self.human.mesh.shader)
        else:
            shaderName = None
            firstItem.setChecked(True)

        for name in sorted(shaders):
            item = self.shaderList.addItem(name, data = os.path.join(dir, name))
            if shaderName and unicode(shaderName) == item.text:
                item.setChecked(True) # TODO does not have the desired effect
                path = unicode(item.getUserData())
                self.listUniforms(path, self.human.mesh.material)

    def setShader(self, path):
        self.human.mesh.setShader(path)
        self.listUniforms(path, self.human.mesh.material)

    def listUniforms(self, path, material):
        for child in self.paramBox.children[:]:
            self.paramBox.removeWidget(child)

        if not path:
            return

        sh = shader.getShader(path)
        uniforms = sh.getUniforms()
        for index, uniform in enumerate(uniforms):
            if uniform.name.startswith('gl_'):
                continue
            self.paramBox.addWidget(UniformValue(uniform, material), index)

    def onShow(self, arg):
        super(ShaderTaskView, self).onShow(arg)
        self.listShaders()
        if self.human.material.shader:
            self.human.material.shader
        if not shader.Shader.supported():
            gui3d.app.statusPersist('Shaders not supported by OpenGL')

        shaderConfig = self.human.material.shaderConfig
        for child in self.shaderConfBox.children:
            name = str(child.text())
            child.setChecked( shaderConfig[name] )
            if name == 'diffuse':
                child.setEnabled(self.human.material.supportsDiffuse())
            if name == 'bump':
                # TODO disable bump if normal enabled
                child.setEnabled(self.human.material.supportsBump())
            if name == 'normal':
                child.setEnabled(self.human.material.supportsNormal())
            if name == 'displacement':
                child.setEnabled(self.human.material.supportsDisplacement())
            if name == 'spec':
                child.setEnabled(self.human.material.supportsSpecular())

    def onHide(self, arg):
        gui3d.app.statusPersist('')
        super(ShaderTaskView, self).onHide(arg)

class UniformValue(gui.GroupBox):
    def __init__(self, uniform, material = None):
        super(UniformValue, self).__init__(uniform.name)
        self.uniform = uniform
        self.material = material
        self.widgets = None
        self.create()

    def create(self):
        values = None
        if self.material:
            # Material params have precedence over declarations in shader code
            params = self.material.shaderParameters
            values = params.get(self.uniform.name)
        if values is None:
            values = np.atleast_2d(self.uniform.values)
        else:
            values = np.atleast_2d(values)
        rows, cols = values.shape
        self.widgets = []
        for row in xrange(rows):
            widgets = []
            for col in xrange(cols):
                child = self.createWidget(values[row,col], row)
                self.addWidget(child, row, col)
                widgets.append(child)
            self.widgets.append(widgets)

    def createWidget(self, value, row):
        type = self.uniform.pytype
        if type == int:
            return IntValue(self, value)
        if type == float:
            return FloatValue(self, value)
        if type == str:
            # TODO account for tex idx
            return TextureValue(self, value)
        if type == bool:
            return BooleanValue(self, value)
        return TextView('???')

    def onActivate(self, arg=None):
        values = [[widget.value
                   for widget in widgets]
                  for widgets in self.widgets]
        if len(self.uniform.dims) == 1:
            values = values[0]
            if self.uniform.dims == (1,) and self.uniform.pytype == str:
                values = values[0]
                if not os.path.isfile(values):
                    return
        gui3d.app.selectedHuman.mesh.setShaderParameter(self.uniform.name, values)

class NumberValue(gui.TextEdit):
    def __init__(self, parent, value):
        super(NumberValue, self).__init__(str(value), self._validator)
        self.parent = parent

    def sizeHint(self):
        size = self.minimumSizeHint()
        size.width = size.width() * 3
        return size

    def onActivate(self, arg=None):
        self.parent.callEvent('onActivate', self.value)

class IntValue(NumberValue):
    _validator = gui.intValidator

    @property
    def value(self):
        return int(self.text)

class FloatValue(NumberValue):
    _validator = gui.floatValidator

    @property
    def value(self):
        return float(self.text)

class BooleanValue(gui.CheckBox):
    def __init__(self, parent, value):
        super(BooleanValue, self).__init__()
        self.parent = parent
        self.setSelected(value)

    def onClicked(self, arg=None):
        self.parent.callEvent('onActivate', self.value)

    @property
    def value(self):
        return self.selected

class TextureValue(gui.QtGui.QWidget, gui.Widget):
    def __init__(self, parent, value):
        super(TextureValue, self).__init__()
        self.parent = parent
        self._path = value

        self.layout = gui.QtGui.QGridLayout(self)
        self.imageView = gui.ImageView()
        self.browseBtn = gui.BrowseButton()
        @self.browseBtn.mhEvent
        def onClicked(event):
            if self.browseBtn._path:
                self._path = self.browseBtn._path
                self.imageView.setImage(self.value)
                self.parent.callEvent('onActivate', self.value)

        if value:
            self.imageView.setImage(value)
            if isinstance(value, basestring): self.browseBtn.setPath(value)
        else:
            self.imageView.setImage('data/notfound.thumb')

        self.layout.addWidget(self.imageView)
        self.layout.addWidget(self.browseBtn)

    @property
    def value(self):
        return self._path

def load(app):
    category = app.getCategory('Settings')
    taskview = category.addTask(ShaderTaskView(category))

def unload(app):
    pass


