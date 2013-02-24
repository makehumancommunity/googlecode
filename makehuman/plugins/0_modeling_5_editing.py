
import numpy as np
import events3d
import gui3d
import mh
import gui
import log

class EditingTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Proportional editing', label='Edit')
        self.radius = 1.0
        self.center = None
        self.depth = None
        self.morph = None
        self.original = None
        self.weights = None
        self.verts = None
        self.faces = None

    def onMouseDown(self, event):
        if gui3d.app.getSelectedFaceGroupAndObject() is None:
            return

        human = gui3d.app.selectedHuman

        x, y, z = gui3d.app.modelCamera.convertToWorld2D(event.x, event.y, human.mesh)
        center = np.array([x, y, z])
        _, _, depth = gui3d.app.modelCamera.convertToScreen(x, y, z, human.mesh)

        distance2 = np.sum((human.meshData.coord - center[None,:]) ** 2, axis=-1)
        verts = np.argwhere(distance2 < (self.radius ** 2))
        if not len(verts):
            return

        self.center = center
        self.depth = depth
        self.verts = verts[:,0]
        self.weights = self.falloff(np.sqrt(distance2[self.verts]) / self.radius)
        self.original = human.meshData.coord[self.verts]
        self.faces = human.meshData.getFacesForVertices(self.verts)

    @staticmethod
    def falloff(x):
        return (2 * x - 3) * x ** 2 + 1

    def onMouseDragged(self, event):
        if self.center is None or self.depth is None:
            return

        human = gui3d.app.selectedHuman

        x, y, z = gui3d.app.modelCamera.convertToWorld3D(event.x, event.y, self.depth, human.mesh)
        pos = np.array([x, y, z])
        delta = pos - self.center

        coord = self.original + delta[None,:] * self.weights[:,None]
        human.meshData.coord[self.verts] = coord
        human.meshData.markCoords(self.verts, coor=True)
        human.meshData.calcNormals(True, True, self.verts, self.faces)
        human.meshData.update()
        mh.redraw()

    def onMouseUp(self, event):
        if self.center is None or self.depth is None:
            return

        human = gui3d.app.selectedHuman
        self.morph = human.meshData.coord[self.verts] - self.original

        self.center = None
        self.depth = None
        self.original = None
        self.weights = None

def load(app):
    category = app.getCategory('Modelling')
    taskview = category.addTask(EditingTaskView(category))

def unload(app):
    pass
