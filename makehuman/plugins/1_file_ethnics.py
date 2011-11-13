#!/usr/bin/python
# -*- coding: utf-8 -*-
# We need this for gui controls

import gui3d, os

class EthnicsTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Ethnics')

        self.ethnicGroup = []
        y = 80
        ethnicBox = self.addView(gui3d.GroupBox([10, y, 9.0], 'Ethnic', gui3d.GroupBoxStyle._replace(height=25+24*1+6)));y+=25
        self.africa = ethnicBox.addView(gui3d.RadioButton(self.ethnicGroup, "Africa", True, gui3d.ButtonStyle));y+=24
        y+=16
        
        self.subEthnicGroup = []
        subEthnicBox = self.addView(gui3d.GroupBox([10, y, 9.0], 'Sub ethnic', gui3d.GroupBoxStyle._replace(height=25+24*7+6)));y+=25
        self.aethiopid = subEthnicBox.addView(gui3d.RadioButton(self.subEthnicGroup, "Aethiopid", True, gui3d.ButtonStyle));y+=24
        self.center = subEthnicBox.addView(gui3d.RadioButton(self.subEthnicGroup, "Center", style = gui3d.ButtonStyle));y+=24
        self.khoisan = subEthnicBox.addView(gui3d.RadioButton(self.subEthnicGroup, "Khoisan", style = gui3d.ButtonStyle));y+=24
        self.nilotid = subEthnicBox.addView(gui3d.RadioButton(self.subEthnicGroup, "Nilotid", style = gui3d.ButtonStyle));y+=24
        self.pigmy = subEthnicBox.addView(gui3d.RadioButton(self.subEthnicGroup, "Pigmy", style = gui3d.ButtonStyle));y+=24
        self.sudanid = subEthnicBox.addView(gui3d.RadioButton(self.subEthnicGroup, "Sudanid", style = gui3d.ButtonStyle));y+=24
        self.bantu = subEthnicBox.addView(gui3d.RadioButton(self.subEthnicGroup, "Bantu", style = gui3d.ButtonStyle));y+=24
        
        self.genderGroup = []
        y = 80
        self.genderBox = self.addView(gui3d.GroupBox([650, y, 9.0], 'Gender', gui3d.GroupBoxStyle._replace(height=25+24*2+6)));y+=25
        self.female = self.genderBox.addView(gui3d.RadioButton(self.genderGroup, "Female", True, gui3d.ButtonStyle));y+=24
        self.male = self.genderBox.addView(gui3d.RadioButton(self.genderGroup, "Male", style = gui3d.ButtonStyle));y+=24
        y+=16
        
        self.ageGroup = []
        self.ageBox = self.addView(gui3d.GroupBox([650, y, 9.0], 'Age', gui3d.GroupBoxStyle._replace(height=25+24*3+6)));y+=25
        self.child = self.ageBox.addView(gui3d.RadioButton(self.ageGroup, "Child", True, gui3d.ButtonStyle));y+=24
        self.young = self.ageBox.addView(gui3d.RadioButton(self.ageGroup, "Young", style = gui3d.ButtonStyle));y+=24
        self.old = self.ageBox.addView(gui3d.RadioButton(self.ageGroup, "Old", style = gui3d.ButtonStyle));y+=24
        y+=16
        
        self.loadBox = self.addView(gui3d.GroupBox([650, y, 9.0], 'Load', gui3d.GroupBoxStyle._replace(height=25+24*1+6)));y+=25
        self.load = self.loadBox.addView(gui3d.Button("Load"));y+=24
        
        @self.load.event
        def onClicked(event):
            ethnic = self.africa.getSelection().getLabel().lower()
            subEthnic = self.aethiopid.getSelection().getLabel().lower()
            gender = self.female.getSelection().getLabel().lower()
            age = self.child.getSelection().getLabel().lower()
            self.loadEthnic('%s-%s-%s-%s.mhm' % (ethnic, subEthnic, gender, age))
        
    def loadEthnic(self, filename):
        
        human = self.app.selectedHuman

        human.load(os.path.join('data/models/ethnics', filename), False, self.app.progress)
        target = os.path.join('data/models/ethnics', filename.replace('.mhm', '.target'))
        human.setDetail(target, 1.0)
        human.applyAllTargets(self.app.progress)

        del self.app.undoStack[:]
        del self.app.redoStack[:]

        self.app.categories['Files'].tasksByName['Save'].fileentry.text = filename.replace('.mhm', '')
        self.app.categories['Files'].tasksByName['Save'].fileentry.edit.setText(filename.replace('.mhm', ''))

        #self.app.switchCategory('Modelling')
        
    def onResized(self, event):
        
        self.genderBox.setPosition([event.width - 150, self.genderBox.getPosition()[1], 9.0])
        self.ageBox.setPosition([event.width - 150, self.ageBox.getPosition()[1], 9.0])
        self.loadBox.setPosition([event.width - 150, self.loadBox.getPosition()[1], 9.0])
        
    def loadHandler(self, human, values):
        
        target = '%s.target' % os.path.join('data/models/ethnics', values[1])
        print target
        human.setDetail(target, float(values[2]))
       
    def saveHandler(self, human, file):
        
        for name, value in human.targetsDetailStack.iteritems():
            if 'ethnics' in name:
                target = os.path.basename(name).replace('.target', '')
                file.write('ethnic %s %f\n' % (target, value))

def load(app):
    category = app.getCategory('Files')
    taskview = category.addView(EthnicsTaskView(category))
    
    app.addLoadHandler('ethnic', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)
    
    print 'Ethnics imported'

def unload(app):
    pass


