#!/usr/bin/python
# -*- coding: utf-8 -*-
# We need this for gui controls

import gui3d, random, humanmodifier
class RandomTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Random')
        
        toolbox = gui3d.GroupBox(self, [10, 80, 9.0], 'Tools', gui3d.GroupBoxStyle._replace(height=25+24*4+6))
        self.macro = gui3d.CheckBox(toolbox, "Macro", True)
        self.height = gui3d.CheckBox(toolbox, "Height")
        self.create = gui3d.Button(toolbox, "Create new")
        self.modify = gui3d.Button(toolbox, "Modify current")
        
        @self.create.event
        def onClicked(event):
            human = self.app.selectedHuman
            human.resetMeshValues()
            
            if self.macro.selected:
                human.setGender(random.random())
                human.setAge(random.random())
                human.setMuscle(random.random())
                human.setWeight(random.random())
                
            if self.height.selected:
                modifier = humanmodifier.Modifier(human, 'data/targets/macrodetails/universal-stature-dwarf.target',
                                                      'data/targets/macrodetails/universal-stature-giant.target')
                modifier.setValue(random.random() * 2 - 1, 0)
            
            human.applyAllTargets(self.app.progress)
            
        @self.modify.event
        def onClicked(event):
            human = self.app.selectedHuman
            
            if self.macro.selected:
                human.setGender(human.getGender() + random.random() - 0.5)
                human.setAge(human.getAge() + random.random() - 0.5)
                human.setMuscle(human.getMuscle() + random.random() - 0.5)
                human.setWeight(human.getWeight() + random.random() - 0.5)
                
            if self.height.selected:
                modifier = humanmodifier.Modifier(human, 'data/targets/macrodetails/universal-stature-dwarf.target',
                                                      'data/targets/macrodetails/universal-stature-giant.target')
                modifier.setValue(modifier.getValue() + random.random() - 0.5, 0)
                
            human.applyAllTargets(self.app.progress)

def load(app):
    category = app.getCategory('Experiments')
    taskview = RandomTaskView(category)
    print 'Random imported'

def unload(app):
    pass


