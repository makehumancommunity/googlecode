
import math
import numpy as np
import events3d
import gui3d
import mh
import gui
import log
import module3d

class ValueConverter(object):
    def dataToDisplay(self, value):
        return 2 ** value

    def displayToData(self, value):
        return math.log(value, 2)

class EditingTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Proportional editing', label='Edit')

        self.radius = 1.0
        self.start = None
        self.center = None
        self.depth = None
        self.morph = None
        self.original = None
        self.weights = None
        self.verts = None
        self.faces = None

        self.converter = ValueConverter()
        value = self.converter.displayToData(self.radius)
        self.radiusSlider = self.addLeftWidget(gui.Slider(value, min=-5.0, max=3.0, label="Radius",
                                                          valueConverter=self.converter))
        self.modeBox = self.addLeftWidget(gui.GroupBox("Mode"))
        modes = []
        self.grab = self.modeBox.addWidget(gui.RadioButton(modes, "Grab", selected=True))
        self.norm = self.modeBox.addWidget(gui.RadioButton(modes, "Normal"))
        self.scalex = self.modeBox.addWidget(gui.RadioButton(modes, "Scale X"))
        self.scaley = self.modeBox.addWidget(gui.RadioButton(modes, "Scale Y"))
        self.scalez = self.modeBox.addWidget(gui.RadioButton(modes, "Scale Z"))

        self.buildCircle()
        self.updateRadius()

        self.circle = self.addObject(gui3d.Object([0, 0, 0], self.circleMesh))

        @self.radiusSlider.mhEvent
        def onChanging(value):
            self.radius = self.converter.dataToDisplay(value)
            self.updateRadius()

        @self.radiusSlider.mhEvent
        def onChange(value):
            self.radius = self.converter.dataToDisplay(value)
            self.updateRadius()

    def buildCircle(self):
        self.circleMesh = module3d.Object3D('circle', 2)
        fg = self.circleMesh.createFaceGroup('circle')

        self.circleMesh.setCoords(np.zeros((180, 3), dtype=np.float32))
        self.circleMesh.setUVs(np.zeros((1, 2), dtype=np.float32))
        ix = np.arange(180)
        faces = np.vstack((ix, np.roll(ix,-1))).transpose()
        self.circleMesh.setFaces(faces)

        self.circleMesh.setCameraProjection(0)
        self.circleMesh.setShadeless(True)
        self.circleMesh.setDepthless(True)
        self.circleMesh.setColor([0, 255, 255, 255])
        self.circleMesh.setPickable(0)
        self.circleMesh.updateIndexBuffer()
        self.circleMesh.priority = 50

    def updateRadius(self):
        angle = np.arange(0,360,2) * np.pi / 180
        coord = np.vstack((np.cos(angle), np.sin(angle), np.zeros_like(angle))).transpose()
        coord *= self.radius
        self.circleMesh.changeCoords(coord)
        self.circleMesh.update()

    def updatePosition(self, x, y):
        pos = gui3d.app.modelCamera.convertToWorld2D(x, y)
        self.circle.setPosition(pos)

    def onMouseDown(self, event):
        if gui3d.app.getSelectedFaceGroupAndObject() is None:
            return
        if event.button != mh.Buttons.LEFT:
            return

        human = gui3d.app.selectedHuman

        x, y, z = gui3d.app.modelCamera.convertToWorld2D(event.x, event.y, human.mesh)
        center = np.array([x, y, z])
        _, _, depth = gui3d.app.modelCamera.convertToScreen(x, y, z, human.mesh)

        distance2 = np.sum((human.meshData.coord - center[None,:]) ** 2, axis=-1)
        verts = np.argwhere(distance2 < (self.radius ** 2))
        if not len(verts):
            return

        self.start = (event.x, event.y)
        self.center = center
        self.depth = depth
        self.verts = verts[:,0]
        self.weights = self.falloff(np.sqrt(distance2[self.verts]) / self.radius)
        self.original = human.meshData.coord[self.verts]
        self.normals = human.meshData.vnorm[self.verts]
        self.faces = human.meshData.getFacesForVertices(self.verts)

    @staticmethod
    def falloff(x):
        return (2 * x - 3) * x ** 2 + 1

    def onMouseMoved(self, event):
        self.updatePosition(event.x, event.y)
        human = gui3d.app.selectedHuman
        x, y, z = gui3d.app.modelCamera.convertToWorld2D(event.x, event.y, human.mesh)

    def scale(self, vector, factor):
        vector = np.array(vector, dtype=np.float32)
        ones = 1 - vector
        scale = 2 ** (factor * self.weights[:,None])
        return self.center + (ones + vector * scale) * (self.original - self.center)

    def onMouseDragged(self, event):
        self.updatePosition(event.x, event.y)

        if self.start is None or self.center is None or self.depth is None:
            return

        human = gui3d.app.selectedHuman

        dist = (event.x - self.start[0]) / 100.0

        if self.norm.selected:
            coord = self.original + dist * self.weights[:,None] * self.normals
        elif self.scalex.selected:
            coord = self.scale([1, 0, 0], dist)
        elif self.scaley.selected:
            coord = self.scale([0, 1, 0], dist)
        elif self.scalez.selected:
            coord = self.scale([0, 0, 1], dist)
        else:
            x, y, z = gui3d.app.modelCamera.convertToWorld3D(event.x, event.y, self.depth, human.mesh)
            pos = np.array([x, y, z])
            delta = pos - self.center
            coord = self.original + delta[None,:] * self.weights[:,None]

        human.meshData.changeCoords(coord, self.verts)
        human.meshData.calcNormals(True, True, self.verts, self.faces)
        human.meshData.update()
        mh.redraw()

    def onMouseUp(self, event):
        if self.start is None or self.center is None or self.depth is None:
            return

        human = gui3d.app.selectedHuman
        self.morph = human.meshData.coord[self.verts] - self.original

        self.start = None
        self.center = None
        self.depth = None
        self.original = None
        self.weights = None

def load(app):
    category = app.getCategory('Modelling')
    taskview = category.addTask(EditingTaskView(category))

def unload(app):
    pass
