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
import mh2proxy

class ClothesTaskView(gui3d.TaskView):
    
    def __init__(self, category):
        
        gui3d.TaskView.__init__(self, category, 'Clothes')
        self.filechooser = gui3d.FileChooser(self, 'data/clothes', 'mhclo', 'png', 'notfound.png')

        @self.filechooser.event
        def onFileSelected(filename):
            
            self.setClothes(gui3d.app.selectedHuman, filename)

            gui3d.app.switchCategory('Modelling')
        
    def setClothes(self, human, mhclo):

        print("Clothes file", mhclo)
        proxy = mh2proxy.readProxyFile(human.meshData, mhclo, False)
        #folder = os.path.dirname(mhclo)
        (folder, name) = proxy.obj_file
        obj = os.path.join(folder, name)

        try:
            clo = human.clothesObjs[proxy.name]
        except:
            clo = None
        if clo:
            gui3d.app.scene3d.delete(clo.mesh)
            del human.clothesObjs[proxy.name]
            return

        mesh = files3d.loadMesh(gui3d.app.scene3d, obj)
        if proxy.texture:
            (dir, name) = proxy.texture
            tif = os.path.join(folder, name)
            mesh.setTexture(tif)
        else:
            pass
        
        clo = gui3d.app.addObject(gui3d.Object(human.getPosition(), mesh))
        clo.setRotation(human.getRotation())
        clo.mesh.setCameraProjection(0)
        clo.mesh.setSolid(human.mesh.solid)
        clo.mesh.setTransparentPrimitives(len(clo.mesh.faces))
        clo.mesh.originalClothesVerts = [v.co[:] for v in clo.mesh.verts]
        human.clothesObjs[proxy.name] = clo
        
        human.clothesProxies[proxy.name] = proxy

        gui3d.app.scene3d.update()
        self.adaptClothesToHuman(human)
        clo.setSubdivided(human.isSubdivided())
        
        #self.clothesButton.setTexture(obj.replace('.obj', '.png'))
    
    def adaptClothesToHuman(self, human):

        for (name,clo) in human.clothesObjs.items():            
            if clo:
                mesh = clo.getSeedMesh()
                human.clothesProxies[name].update(mesh, human.meshData)
                mesh.update()
                if clo.isSubdivided():
                    clo.getSubdivisionMesh()

    def onShow(self, event):
        # When the task gets shown, set the focus to the file chooser
        gui3d.app.selectedHuman.hide()
        gui3d.TaskView.onShow(self, event)
        self.filechooser.setFocus()

    def onHide(self, event):
        gui3d.app.selectedHuman.show()
        gui3d.TaskView.onHide(self, event)
        
    def onResized(self, event):
        self.filechooser.onResized(event)
        
    def onHumanChanging(self, event):
        
        human = event.human
        if event.change == 'reset':
            print 'deleting clothes'
            for (name,clo) in human.clothesObjs.items():
                if clo:
                    gui3d.app.scene3d.delete(clo.mesh)
                del human.clothesObjs[name]
                del human.clothesProxies[name]
            # self.clothesButton.setTexture('data/clothes/clear.png')

    def onHumanChanged(self, event):
        
        human = event.human
        self.adaptClothesToHuman(human)

    def loadHandler(self, human, values):
        
        self.setClothes(human, os.path.join('data/clothes', values[1].replace('.obj', ''), values[1].replace('.obj', '.mhclo')))
        
    def saveHandler(self, human, file):
        
        for clo in human.clothesObjs.values():
            if clo:
                file.write('clothes %s\n' % clo.mesh.name)

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Library')
    taskview = ClothesTaskView(category)

    app.addLoadHandler('clothes', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass

