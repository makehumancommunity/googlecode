"""
B{Project Name:}      MakeHuman

B{Product Home Page:} U{http://www.makehuman.org/}

B{Code Home Page:}    U{http://code.google.com/p/makehuman/}

B{Authors:}           Manuel Bastioni, Marc Flerackers

B{Copyright(c):}      MakeHuman Team 2001-2011

B{Licensing:}         GPL3 (see also U{http://sites.google.com/site/makehumandocs/licensing})

B{Coding Standards:}  See U{http://sites.google.com/site/makehumandocs/developers-guide}

Abstract
========

TO DO

"""

import gui3d, mh, os
import files3d
from aljabr import in2pts, vadd, vsub, calcBBox
# TL: import mh2proxy for treating polygon hair as clothes
import mh2proxy

HairButtonStyle = gui3d.Style(**{
    'parent':gui3d.ViewStyle,
    'width':32,
    'height':32
})

class HairTaskView(gui3d.TaskView):
    
    def __init__(self, category):
        
        gui3d.TaskView.__init__(self, category, 'Hair')
        self.filechooser = self.addView(gui3d.FileChooser('data/hairstyles', 'obj', 'png', 'notfound.png'))
        
        self.hairButton = gui3d.app.categories['Modelling'].addView(gui3d.Button(style=HairButtonStyle._replace(left=800-216, top=600-36, zIndex=9.2, normal='data/hairstyles/clear.png')))
        
        self.oHeadCentroid = [0.0, 7.436, 0.03 + 0.577]
        self.oHeadBBox = [[-0.84,6.409,-0.9862],[0.84,8.463,1.046]]

        @self.filechooser.event
        def onFileSelected(filename):
            
            self.setHair(gui3d.app.selectedHuman, filename)
            
            gui3d.app.switchCategory('Modelling')
            
        @self.hairButton.event
        def onClicked(event):
            gui3d.app.switchCategory('Library')
            gui3d.app.switchTask("Hair")

    def setHair(self, human, filename):

        #obj = os.path.join('data/hairstyles', filename)
        #TL: path now included in filename?
        obj = filename
        tif = obj.replace('.obj', '_texture.tif')
        
        if human.hairObj:
            gui3d.app.removeObject(human.hairObj)
            human.hairObj = None
            human.hairProxy = None

        mesh = files3d.loadMesh(obj)
        if mesh:
            mesh.setTexture(tif)        
            human.hairObj = gui3d.app.addObject(gui3d.Object(human.getPosition(), mesh))
            human.hairObj.setRotation(human.getRotation())
            human.hairObj.mesh.setCameraProjection(0)
            human.hairObj.mesh.setSolid(human.mesh.solid)
            human.hairObj.mesh.setTransparentPrimitives(len(human.hairObj.mesh.faces))
            human.hairObj.mesh.originalHairVerts = [v.co[:] for v in human.hairObj.mesh.verts]
                
            hairName = human.hairObj.mesh.name.split('.')[0]
            file = "data/hairstyles/%s.mhclo" % hairName
            print("Loading clothes hair %s" % file)
            human.hairProxy = mh2proxy.readProxyFile(human.meshData, file, False)

            self.adaptHairToHuman(human)
            human.hairObj.setSubdivided(human.isSubdivided())
            
            self.hairButton.setTexture(obj.replace('.obj', '.png'))

    def adaptHairToHuman(self, human):

        if human.hairObj:
            
            mesh = human.hairObj.getSeedMesh()
            human.hairProxy.update(mesh, human.meshData)
            
            """
                headNames = [group.name for group in human.meshData.faceGroups if ("head" in group.name or "jaw" in group.name or "nose" in group.name or "mouth" in group.name or "ear" in group.name or "eye" in group.name)]
                headVertices = human.meshData.getVerticesAndFacesForGroups(headNames)[0]
                headBBox = calcBBox(headVertices)
            
                headCentroid = in2pts(headBBox[0], headBBox[1], 0.5)
                delta = vsub(headCentroid, self.oHeadCentroid)
            
                sx = (headBBox[1][0]-headBBox[0][0])/float(self.oHeadBBox[1][0]-self.oHeadBBox[0][0])
                sy = (headBBox[1][1]-headBBox[0][1])/float(self.oHeadBBox[1][1]-self.oHeadBBox[0][1])
                sz = (headBBox[1][2]-headBBox[0][2])/float(self.oHeadBBox[1][2]-self.oHeadBBox[0][2])
            
                mesh = human.hairObj.getSeedMesh()
                for i, v in enumerate(mesh.verts):
                    co = vsub(mesh.originalHairVerts[i], headCentroid)
                    co[0] *= sx
                    co[1] *= sy
                    co[2] *= sz
                    v.co = vadd(vadd(co, headCentroid), delta)
            """
            
            mesh.update()
            if human.hairObj.isSubdivided():
                human.hairObj.getSubdivisionMesh()
        
    def onShow(self, event):
        # When the task gets shown, set the focus to the file chooser
        gui3d.app.selectedHuman.hide()
        gui3d.TaskView.onShow(self, event)
        self.filechooser.setFocus()

    def onHide(self, event):
        gui3d.app.selectedHuman.show()
        gui3d.TaskView.onHide(self, event)
        
    def onResized(self, event):
        self.hairButton.setPosition([event.width-216, event.height-36, 9.2])
        self.filechooser.onResized(event)
        
    def onHumanChanging(self, event):
        
        human = event.human
        if event.change == 'reset':
            if human.hairObj:
                human.hairObj.mesh.clear()
                human.hairObj = None
                human.hairProxy = None
            self.hairButton.setTexture('data/hairstyles/clear.png')
        
    def onHumanChanged(self, event):
        
        human = event.human
        self.adaptHairToHuman(human)

    def loadHandler(self, human, values):
        
        self.setHair(human, values[1])
        
    def saveHandler(self, human, file):
        
        if human.hairObj:
            file.write('hair %s\n' % human.hairObj.mesh.name)

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Library')
    taskview = category.addView(HairTaskView(category))

    app.addLoadHandler('hair', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass

