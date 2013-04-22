#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import os
import numpy as np

import gui3d
import mh
import gui
import algos3d
from core import G
import log

class ViewerTaskView(gui3d.TaskView):
    def __init__(self, category):
        super(ViewerTaskView, self).__init__(category, 'Viewer')
        self.image = self.addTopWidget(gui.ImageView())

    def setImage(self, path):
        self.image.setImage(path)

def load(app):
    category = app.getCategory('Rendering')
    taskview = category.addTask(ViewerTaskView(category))

def unload(app):
    pass

