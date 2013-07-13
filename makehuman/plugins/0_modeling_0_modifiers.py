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

Generic modifiers
TODO
"""

import mh
import gui
import gui3d
import humanmodifier
import log
import targets

class GroupBoxRadioButton(gui.RadioButton):
    def __init__(self, task, group, label, groupBox, selected=False):
        super(GroupBoxRadioButton, self).__init__(group, label, selected)
        self.groupBox = groupBox
        self.task = task

    def onClicked(self, event):
        self.task.groupBox.showWidget(self.groupBox)

class ModifierTaskView(gui3d.TaskView):
    _group = None
    _label = None

    def __init__(self, category):
        super(ModifierTaskView, self).__init__(category, self._name, label=self._label)

        def resolveOptionsDict(opts, type = 'simple'):
            # Function to analyze options passed
            # with a dictionary in the features.
            if not 'cam' in opts.keys():
                opts['cam'] = 'noSetCamera'
            if not 'min' in opts.keys():
                if type == 'paired':
                    opts['min'] = -1.0
                else:
                    opts['min'] = 0.0
            if not 'max' in opts.keys():
                opts['max'] = 1.0
            if 'reverse' in opts.keys() and opts['reverse'] == True:
                temp = opts['max']
                opts['max'] = opts['min']
                opts['min'] = temp
                # More work needed for reversing - TODO SOON
                
        self.groupBoxes = []
        self.radioButtons = []
        self.sliders = []
        self.modifiers = {}

        self.categoryBox = self.addRightWidget(gui.GroupBox('Category'))
        self.groupBox = self.addLeftWidget(gui.StackedBox())

        for name, base, templates in self._features:
            title = name.capitalize()

            # Create box
            box = self.groupBox.addWidget(gui.GroupBox(title))
            self.groupBoxes.append(box)

            # Create radiobutton
            radio = self.categoryBox.addWidget(GroupBoxRadioButton(self, self.radioButtons, title, box, selected = len(self.radioButtons) == 0))

            # Create sliders
            for index, template in enumerate(templates):
                macro = len(template) == 4
                if macro:
                    tlabel, tname, tvar, opts = template
                    resolveOptionsDict(opts, 'macro')
                    modifier = humanmodifier.MacroModifier(base, tname, tvar)
                    self.modifiers[tvar] = modifier
                    slider = humanmodifier.MacroSlider(modifier, tlabel, None,
                                                       opts['cam'], opts['min'], opts['max'])
                else:
                    paired = len(template) == 5
                    if paired:
                        tlabel, tname, tleft, tright, opts = template
                        resolveOptionsDict(opts, 'paired')
                        left  = '-'.join([base, tname, tleft])
                        right = '-'.join([base, tname, tright])
                    else:
                        tlabel, tname, opts = template
                        resolveOptionsDict(opts)                       
                        left = None
                        right = '-'.join([base, tname])

                    if tlabel is None:
                        tlabel = tname.split('-')
                        if len(tlabel) > 1 and tlabel[0] == base:
                            tlabel = tlabel[1:]
                        tlabel = ' '.join([word.capitalize() for word in tlabel])

                    modifier = humanmodifier.UniversalModifier(left, right)

                    tpath = '-'.join(template[1:-1])
                    modifierName = tpath
                    clashIndex = 0
                    while modifierName in self.modifiers:
                        log.debug('modifier clash: %s', modifierName)
                        modifierName = '%s%d' % (tpath, clashIndex)
                        clashIndex += 1

                    self.modifiers[modifierName] = modifier
                    slider = humanmodifier.UniversalSlider(modifier, tlabel, '%s.png' % tpath,
                                                           opts['cam'], opts['min'], opts['max'])

                box.addWidget(slider)
                self.sliders.append(slider)

        self.updateMacro()

        self.groupBox.showWidget(self.groupBoxes[0])

    def getModifiers(self):
        return self.modifiers

    def getSymmetricModifierPairNames(self):
        return [dict(left = name, right = "l-" + name[2:])
                for name in self.modifiers
                if name.startswith("r-")]

    def getSingularModifierNames(self):
        return [name
                for name in self.modifiers
                if name[:2] not in ("r-", "l-")]

    def updateMacro(self):
        human = gui3d.app.selectedHuman
        for modifier in self.modifiers.itervalues():
            if isinstance(modifier, humanmodifier.MacroModifier):
                modifier.setValue(human, modifier.getValue(human))

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

        if gui3d.app.settings.get('cameraAutoZoom', True):
            self.setCamera()

        for slider in self.sliders:
            slider.update()

    def onHumanChanged(self, event):
        human = event.human

        for slider in self.sliders:
            slider.update()

        if event.change in ('reset', 'load', 'random'):
            self.updateMacro()

    def loadHandler(self, human, values):
        if values[0] == self._group:
            modifier = self.modifiers.get(values[1], None)
            if modifier:
                modifier.setValue(human, float(values[2]))

    def saveHandler(self, human, file):
        for name, modifier in self.modifiers.iteritems():
            if name is None:
                continue
            value = modifier.getValue(human)
            if value or isinstance(modifier, humanmodifier.MacroModifier):
                file.write('%s %s %f\n' % (self._group, name, value))

    def setCamera(self):
        pass

class FaceTaskView(ModifierTaskView):
    _name = 'Face'
    _group = 'face'
    _features = [
        ('head shape', 'head', [
            (None, 'head-oval', {'cam' : 'frontView'}),
            (None, 'head-round', {'cam' : 'frontView'}),
            (None, 'head-rectangular', {'cam' : 'frontView'}),
            (None, 'head-square', {'cam' : 'frontView'}),
            (None, 'head-triangular', {'cam' : 'frontView'}),
            (None, 'head-invertedtriangular', {'cam' : 'frontView'}),
            (None, 'head-diamond', {'cam' : 'frontView'}),
            ]),
        ('head', 'head', [
            (None, 'head-age', 'less', 'more', {'cam' : 'frontView'}),
            (None, 'head-angle', 'in', 'out', {'cam' : 'rightView'}),
            (None, 'head-scale-depth', 'less', 'more', {'cam' : 'rightView'}),
            (None, 'head-scale-horiz', 'less', 'more', {'cam' : 'frontView'}),
            (None, 'head-scale-vert', 'more', 'less', {'cam' : 'frontView'}),
            (None, 'head-trans', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'head-trans', 'down', 'up', {'cam' : 'frontView'}),
            (None, 'head-trans', 'forward', 'backward', {'cam' : 'rightView'}),
            ]),
        ('neck', 'neck', [
            (None, 'neck-scale-depth', 'less', 'more', {'cam' : 'rightView'}),
            (None, 'neck-scale-horiz', 'less', 'more', {'cam' : 'frontView'}),
            (None, 'neck-scale-vert', 'more', 'less', {'cam' : 'frontView'}),
            (None, 'neck-trans', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'neck-trans', 'down', 'up', {'cam' : 'frontView'}),
            (None, 'neck-trans', 'forward', 'backward', {'cam' : 'rightView'}),
            ]),
        ('right eye', 'eyes', [
            (None, 'r-eye-height1', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'r-eye-height2', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'r-eye-height3', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'r-eye-push1', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'r-eye-push2', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'r-eye-move', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'r-eye-move', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'r-eye', 'small', 'big', {'cam' : 'frontView'}),
            (None, 'r-eye-corner1', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'r-eye-corner2', 'up', 'down', {'cam' : 'frontView'})
            ]),
        ('left eye', 'eyes', [
            (None, 'l-eye-height1', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'l-eye-height2', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'l-eye-height3', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'l-eye-push1', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'l-eye-push2', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'l-eye-move', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'l-eye-move', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'l-eye', 'small', 'big', {'cam' : 'frontView'}),
            (None, 'l-eye-corner1', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'l-eye-corner2', 'up', 'down', {'cam' : 'frontView'}),
            ]),
        ('nose features', 'nose', [
            (None, 'nose', 'compress', 'uncompress', {'cam' : 'rightView'}),
            (None, 'nose', 'convex', 'concave', {'cam' : 'rightView'}),
            (None, 'nose', 'moregreek', 'lessgreek', {'cam' : 'rightView'}),
            (None, 'nose', 'morehump', 'lesshump', {'cam' : 'rightView'}),
            (None, 'nose', 'potato', 'point', {'cam' : 'rightView'}),
            (None, 'nose-nostrils', 'point', 'unpoint', {'cam' : 'frontView'}),
            (None, 'nose-nostrils', 'up', 'down', {'cam' : 'rightView'}),
            (None, 'nose-point', 'up', 'down', {'cam' : 'rightView'}),
            ]),
        ('nose size details', 'nose', [
            (None, 'nose-nostril-width', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'nose-height', 'min', 'max', {'cam' : 'rightView'}),
            (None, 'nose-width1', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'nose-width2', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'nose-width3', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'nose-width', 'min', 'max', {'cam' : 'frontView'}),
            ]),
        ('nose size', 'nose', [
            (None, 'nose-trans', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'nose-trans', 'forward', 'backward', {'cam' : 'rightView'}),
            (None, 'nose-trans', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'nose-scale-vert', 'incr', 'decr', {'cam' : 'frontView'}),
            (None, 'nose-scale-horiz', 'incr', 'decr', {'cam' : 'frontView'}),
            (None, 'nose-scale-depth', 'incr', 'decr', {'cam' : 'rightView'}),
            ]),
        ('mouth size', 'mouth', [
            (None, 'mouth-scale-horiz', 'incr', 'decr', {'cam' : 'frontView'}),
            (None, 'mouth-scale-vert', 'incr', 'decr', {'cam' : 'frontView'}),
            (None, 'mouth-scale-depth', 'incr', 'decr', {'cam' : 'rightView'}),
            (None, 'mouth-trans', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'mouth-trans', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'mouth-trans', 'forward', 'backward', {'cam' : 'rightView'}),
            ]),
        ('mouth size details', 'mouth', [
            (None, 'mouth-lowerlip-height', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'mouth-lowerlip-middle', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'mouth-lowerlip-width', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'mouth-upperlip-height', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'mouth-upperlip-width', 'min', 'max', {'cam' : 'frontView'}),
            ]),
        ('mouth features', 'mouth', [
            (None, 'mouth-lowerlip-ext', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'mouth-angles', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'mouth-lowerlip-middle', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'mouth-lowerlip', 'deflate', 'inflate', {'cam' : 'rightView'}),
            (None, 'mouth-philtrum', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'mouth-philtrum', 'increase', 'decrease', {'cam' : 'rightView'}),
            (None, 'mouth-upperlip', 'deflate', 'inflate', {'cam' : 'rightView'}),
            (None, 'mouth-upperlip-ext', 'up', 'down', {'cam' : 'frontView'}),
            (None, 'mouth-upperlip-middle', 'up', 'down', {'cam' : 'frontView'}),
            ]),
        ('right ear', 'ears', [
            (None, 'r-ear', 'backward', 'forward', {'cam' : 'rightView'}),
            (None, 'r-ear', 'big', 'small', {'cam' : 'rightView'}),
            (None, 'r-ear', 'down', 'up', {'cam' : 'rightView'}),
            (None, 'r-ear-height', 'min', 'max', {'cam' : 'rightView'}),
            (None, 'r-ear-lobe', 'min', 'max', {'cam' : 'rightView'}),
            (None, 'r-ear', 'pointed', 'triangle', {'cam' : 'rightView'}),
            (None, 'r-ear-rot', 'backward', 'forward', {'cam' : 'rightView'}),
            (None, 'r-ear', 'square', 'round', {'cam' : 'rightView'}),
            (None, 'r-ear-width', 'max', 'min', {'cam' : 'rightView'}),
            (None, 'r-ear-wing', 'out', 'in', {'cam' : 'frontView'}),
            (None, 'r-ear-flap', 'out', 'in', {'cam' : 'frontView'}),
            ]),
        ('left ear', 'ears', [
            (None, 'l-ear', 'backward', 'forward', {'cam' : 'leftView'}),
            (None, 'l-ear', 'big', 'small', {'cam' : 'leftView'}),
            (None, 'l-ear', 'down', 'up', {'cam' : 'leftView'}),
            (None, 'l-ear-height', 'min', 'max', {'cam' : 'leftView'}),
            (None, 'l-ear-lobe', 'min', 'max', {'cam' : 'leftView'}),
            (None, 'l-ear', 'pointed', 'triangle', {'cam' : 'leftView'}),
            (None, 'l-ear-rot', 'backward', 'forward', {'cam' : 'leftView'}),
            (None, 'l-ear', 'square', 'round', {'cam' : 'leftView'}),
            (None, 'l-ear-width', 'max', 'min', {'cam' : 'leftView'}),
            (None, 'l-ear-wing', 'out', 'in', {'cam' : 'frontView'}),
            (None, 'l-ear-flap', 'out', 'in', {'cam' : 'frontView'}),
            ]),
        ('chin', 'chin', [
            (None, 'chin', 'in', 'out', {'cam' : 'rightView'}),
            (None, 'chin-width', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'chin-height', 'min', 'max', {'cam' : 'frontView'}),
            (None, 'chin', 'squared', 'round', {'cam' : 'frontView'}),
            (None, 'chin', 'prognathism1', 'prognathism2', {'cam' : 'rightView'}),
            ]),
        ('cheek', 'cheek', [
            (None, 'l-cheek', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'l-cheek-bones', 'out', 'in', {'cam' : 'frontView'}),
            (None, 'r-cheek', 'in', 'out', {'cam' : 'frontView'}),
            (None, 'r-cheek-bones', 'out', 'in', {'cam' : 'frontView'}),
            ]),
        ]

    def setCamera(self):
        gui3d.app.setFaceCamera()

class TorsoTaskView(ModifierTaskView):
    _name = 'Torso'
    _group = 'torso'
    _features = [
        ('Torso', 'torso', [
            (None, 'torso-scale-depth', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            (None, 'torso-scale-horiz', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            (None, 'torso-scale-vert', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            (None, 'torso-trans', 'in', 'out', {'cam' : 'setGlobalCamera'}),
            (None, 'torso-trans', 'down', 'up', {'cam' : 'setGlobalCamera'}),
            (None, 'torso-trans', 'forward', 'backward', {'cam' : 'setGlobalCamera'}),
            ]),
        ('Hip', 'hip', [
            (None, 'hip-scale-depth', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            (None, 'hip-scale-horiz', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            (None, 'hip-scale-vert', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            (None, 'hip-trans', 'in', 'out', {'cam' : 'setGlobalCamera'}),
            (None, 'hip-trans', 'down', 'up', {'cam' : 'setGlobalCamera'}),
            (None, 'hip-trans', 'forward', 'backward', {'cam' : 'setGlobalCamera'}),
            ]),
        ('Stomach', 'stomach', [
            (None, 'stomach-tone', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ]),
        ('Buttocks', 'buttocks', [
            (None, 'buttocks-tone', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ]),
        ('Pelvis', 'pelvis', [
            (None, 'pelvis-tone', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ])
        ]

class ArmsLegsTaskView(ModifierTaskView):
    _name = 'Arms and Legs'
    _group = 'armslegs'
    _features = [
        ('right hand', 'armslegs', [
            (None, 'r-hand-scale-depth', 'decr', 'incr', {'cam' : 'setRightHandTopCamera'}),
            (None, 'r-hand-scale-horiz', 'decr', 'incr', {'cam' : 'setRightHandFrontCamera'}),
            (None, 'r-hand-scale-vert', 'decr', 'incr', {'cam' : 'setRightHandFrontCamera'}),
            (None, 'r-hand-trans', 'in', 'out', {'cam' : 'setRightHandFrontCamera'}),
            (None, 'r-hand-trans', 'down', 'up', {'cam' : 'setRightHandFrontCamera'}),
            (None, 'r-hand-trans', 'forward', 'backward', {'cam' : 'setRightHandTopCamera'}),
            ]),
        ('left hand', 'armslegs', [
            (None, 'l-hand-scale-depth', 'decr', 'incr', {'cam' : 'setLeftHandTopCamera'}),
            (None, 'l-hand-scale-horiz', 'decr', 'incr', {'cam' : 'setLeftHandFrontCamera'}),
            (None, 'l-hand-scale-vert', 'decr', 'incr', {'cam' : 'setLeftHandFrontCamera'}),
            (None, 'l-hand-trans', 'in', 'out', {'cam' : 'setLeftHandFrontCamera'}),
            (None, 'l-hand-trans', 'down', 'up', {'cam' : 'setLeftHandFrontCamera'}),
            (None, 'l-hand-trans', 'forward', 'backward', {'cam' : 'setLeftHandTopCamera'}),
            ]),
        ('right foot', 'armslegs', [
            (None, 'r-foot-scale-depth', 'decr', 'incr', {'cam' : 'setRightFootRightCamera'}),
            (None, 'r-foot-scale-horiz', 'decr', 'incr', {'cam' : 'setRightFootFrontCamera'}),
            (None, 'r-foot-scale-vert', 'decr', 'incr', {'cam' : 'setRightFootFrontCamera'}),
            (None, 'r-foot-trans', 'in', 'out', {'cam' : 'setRightFootFrontCamera'}),
            (None, 'r-foot-trans', 'down', 'up', {'cam' : 'setRightFootFrontCamera'}),
            (None, 'r-foot-trans', 'forward', 'backward', {'cam' : 'setRightFootRightCamera'}),
            ]),
        ('left foot', 'armslegs', [
            (None, 'l-foot-scale-depth', 'decr', 'incr', {'cam' : 'setLeftFootLeftCamera'}),
            (None, 'l-foot-scale-horiz', 'decr', 'incr', {'cam' : 'setLeftFootFrontCamera'}),
            (None, 'l-foot-scale-vert', 'decr', 'incr', {'cam' : 'setLeftFootFrontCamera'}),
            (None, 'l-foot-trans', 'in', 'out', {'cam' : 'setLeftFootFrontCamera'}),
            (None, 'l-foot-trans', 'down', 'up', {'cam' : 'setLeftFootFrontCamera'}),
            (None, 'l-foot-trans', 'forward', 'backward', {'cam' : 'setLeftFootLeftCamera'}),
            ]),
        ('left arm', 'armslegs', [
            (None, 'l-lowerarm-scale-depth', 'decr', 'incr', {'cam' : 'setLeftArmTopCamera'}),
            (None, 'l-lowerarm-scale-horiz', 'decr', 'incr', {'cam' : 'setLeftArmFrontCamera'}),
            (None, 'l-lowerarm-scale-vert', 'decr', 'incr', {'cam' : 'setLeftArmFrontCamera'}),
            (None, 'l-lowerarm-trans', 'in', 'out', {'cam' : 'setLeftArmFrontCamera'}),
            (None, 'l-lowerarm-trans', 'down', 'up', {'cam' : 'setLeftArmFrontCamera'}),
            (None, 'l-lowerarm-trans', 'forward', 'backward', {'cam' : 'setLeftArmTopCamera'}),
            (None, 'l-upperarm-scale-depth', 'decr', 'incr', {'cam' : 'setLeftArmTopCamera'}),
            (None, 'l-upperarm-scale-horiz', 'decr', 'incr', {'cam' : 'setLeftArmFrontCamera'}),
            (None, 'l-upperarm-scale-vert', 'decr', 'incr', {'cam' : 'setLeftArmFrontCamera'}),
            (None, 'l-upperarm-trans', 'in', 'out', {'cam' : 'setLeftArmFrontCamera'}),
            (None, 'l-upperarm-trans', 'down', 'up', {'cam' : 'setLeftArmFrontCamera'}),
            (None, 'l-upperarm-trans', 'forward', 'backward', {'cam' : 'setLeftArmTopCamera'}),
            ]),
        ('right arm', 'armslegs', [
            (None, 'r-lowerarm-scale-depth', 'decr', 'incr', {'cam' : 'setRightArmTopCamera'}),
            (None, 'r-lowerarm-scale-horiz', 'decr', 'incr', {'cam' : 'setRightArmFrontCamera'}),
            (None, 'r-lowerarm-scale-vert', 'decr', 'incr', {'cam' : 'setRightArmFrontCamera'}),
            (None, 'r-lowerarm-trans', 'in', 'out', {'cam' : 'setRightArmFrontCamera'}),
            (None, 'r-lowerarm-trans', 'down', 'up', {'cam' : 'setRightArmFrontCamera'}),
            (None, 'r-lowerarm-trans', 'forward', 'backward', {'cam' : 'setRightArmTopCamera'}),
            (None, 'r-upperarm-scale-depth', 'decr', 'incr', {'cam' : 'setRightArmTopCamera'}),
            (None, 'r-upperarm-scale-horiz', 'decr', 'incr', {'cam' : 'setRightArmFrontCamera'}),
            (None, 'r-upperarm-scale-vert', 'decr', 'incr', {'cam' : 'setRightArmFrontCamera'}),
            (None, 'r-upperarm-trans', 'in', 'out', {'cam' : 'setRightArmFrontCamera'}),
            (None, 'r-upperarm-trans', 'down', 'up', {'cam' : 'setRightArmFrontCamera'}),
            (None, 'r-upperarm-trans', 'forward', 'backward', {'cam' : 'setRightArmTopCamera'}),
            ]),
        ('left leg', 'armslegs', [
            (None, 'l-lowerleg-scale-depth', 'decr', 'incr', {'cam' : 'setLeftLegLeftCamera'}),
            (None, 'l-lowerleg-scale-horiz', 'decr', 'incr', {'cam' : 'setLeftLegFrontCamera'}),
            (None, 'l-lowerleg-scale-vert', 'decr', 'incr', {'cam' : 'setLeftLegFrontCamera'}),
            (None, 'l-lowerleg-trans', 'in', 'out', {'cam' : 'setLeftLegFrontCamera'}),
            (None, 'l-lowerleg-trans', 'down', 'up', {'cam' : 'setLeftLegFrontCamera'}),
            (None, 'l-lowerleg-trans', 'forward', 'backward', {'cam' : 'setLeftLegLeftCamera'}),
            (None, 'l-upperleg-scale-depth', 'decr', 'incr', {'cam' : 'setLeftLegLeftCamera'}),
            (None, 'l-upperleg-scale-horiz', 'decr', 'incr', {'cam' : 'setLeftLegFrontCamera'}),
            (None, 'l-upperleg-scale-vert', 'decr', 'incr', {'cam' : 'setLeftLegFrontCamera'}),
            (None, 'l-upperleg-trans', 'in', 'out', {'cam' : 'setLeftLegFrontCamera'}),
            (None, 'l-upperleg-trans', 'down', 'up', {'cam' : 'setLeftLegFrontCamera'}),
            (None, 'l-upperleg-trans', 'forward', 'backward', {'cam' : 'setLeftLegLeftCamera'}),
            ]),
        ('right leg', 'armslegs', [
            (None, 'r-lowerleg-scale-depth', 'decr', 'incr', {'cam' : 'setRightLegRightCamera'}),
            (None, 'r-lowerleg-scale-horiz', 'decr', 'incr', {'cam' : 'setRightLegFrontCamera'}),
            (None, 'r-lowerleg-scale-vert', 'decr', 'incr', {'cam' : 'setRightLegFrontCamera'}),
            (None, 'r-lowerleg-trans', 'in', 'out', {'cam' : 'setRightLegFrontCamera'}),
            (None, 'r-lowerleg-trans', 'down', 'up', {'cam' : 'setRightLegFrontCamera'}),
            (None, 'r-lowerleg-trans', 'forward', 'backward', {'cam' : 'setRightLegRightCamera'}),
            (None, 'r-upperleg-scale-depth', 'decr', 'incr', {'cam' : 'setRightLegRightCamera'}),
            (None, 'r-upperleg-scale-horiz', 'decr', 'incr', {'cam' : 'setRightLegFrontCamera'}),
            (None, 'r-upperleg-scale-vert', 'decr', 'incr', {'cam' : 'setRightLegFrontCamera'}),
            (None, 'r-upperleg-trans', 'in', 'out', {'cam' : 'setRightLegFrontCamera'}),
            (None, 'r-upperleg-trans', 'down', 'up', {'cam' : 'setRightLegFrontCamera'}),
            (None, 'r-upperleg-trans', 'forward', 'backward', {'cam' : 'setRightLegRightCamera'}),
            ])
        ]

class GenderTaskView(ModifierTaskView):
    _name = 'Gender'
    _group = 'gendered'
    _features = [
        ('Genitals', 'genitals', [
            (None, 'genitals', 'feminine', 'masculine', {}),
            ]),
        ('Breast', 'breast', [
            ('Breast size', None, 'BreastSize', {}),
            ('Breast firmness', None, 'BreastFirmness', {'reverse' : True}),
            (None, 'breast', 'down', 'up', {}),
            (None, 'breast-dist', 'min', 'max', {}),
            (None, 'breast-point', 'min', 'max', {}),
            ]),
        ]

class AsymmTaskView(ModifierTaskView):
    _name = 'Asymmetry'
    _group = 'asymmetry'
    _features = [
        ('brow', 'asym', [
            (None, 'asym-brown-1', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-brown-2', 'l', 'r', {'cam' : 'setFaceCamera'}),
            ]),
        ('cheek', 'asym', [
            (None, 'asym-cheek-1', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-cheek-2', 'l', 'r', {'cam' : 'setFaceCamera'}),
            ]),
        ('ear', 'asym', [
            (None, 'asym-ear-1', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-ear-2', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-ear-3', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-ear-4', 'l', 'r', {'cam' : 'setFaceCamera'}),
            ]),
        ('eye', 'asym', [
            (None, 'asym-eye-1', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-eye-2', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-eye-3', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-eye-4', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-eye-5', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-eye-6', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-eye-7', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-eye-8', 'l', 'r', {'cam' : 'setFaceCamera'}),
            ]),
        ('jaw', 'asym', [
            (None, 'asym-jaw-1', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-jaw-2', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-jaw-3', 'l', 'r', {'cam' : 'setFaceCamera'}),
            ]),
        ('mouth', 'asym', [
            (None, 'asym-mouth-1', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-mouth-2', 'l', 'r', {'cam' : 'setFaceCamera'}),
            ]),
        ('nose', 'asym', [
            (None, 'asym-nose-1', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-nose-2', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-nose-3', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-nose-4', 'l', 'r', {'cam' : 'setFaceCamera'}),
            ]),
        ('temple', 'asym', [
            (None, 'asym-temple-1', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-temple-2', 'l', 'r', {'cam' : 'setFaceCamera'}),
            ]),
        ('top', 'asym', [
            (None, 'asym-top-1', 'l', 'r', {'cam' : 'setFaceCamera'}),
            (None, 'asym-top-2', 'l', 'r', {'cam' : 'setFaceCamera'}),
            ]),
        ('body', 'asym', [
            (None, 'asymm-breast-1', 'l', 'r', {'cam' : 'setGlobalCamera'}),
            (None, 'asymm-trunk-1', 'l', 'r', {'cam' : 'setGlobalCamera'}),
            ]),
        ]

class MacroTaskView(ModifierTaskView):
    _name = 'Macro modelling'
    _group = 'macro'
    _label = 'Macro'

    _features = [
        ('Macro', 'macrodetails', [
            ('Gender', None, 'Gender', {}),
            ('Age', None, 'Age', {}),
            ('Muscle', 'universal', 'Muscle', {}),
            ('Weight', 'universal', 'Weight', {}),
            ('Height', 'universal-stature', 'Height', {}),
            ('African', None, 'African', {}),
            ('Asian', None, 'Asian', {}),
            ('Caucasian', None, 'Caucasian', {}),
            ]),
        ]

    def __init__(self, category):
        super(MacroTaskView, self).__init__(category)
        for race, modifier, slider in self.raceSliders():
            slider.setValue(1.0/3)

    def raceSliders(self):
        for slider in self.sliders:
            modifier = slider.modifier
            if not isinstance(modifier, humanmodifier.MacroModifier):
                continue
            variable = modifier.variable
            if variable in ('African', 'Asian', 'Caucasian'):
                yield (variable, modifier, slider)

    def syncStatus(self):
        human = gui3d.app.selectedHuman
        
        if human.getGender() == 0.0:
            gender = gui3d.app.getLanguageString('female')
        elif human.getGender() == 1.0:
            gender = gui3d.app.getLanguageString('male')
        elif abs(human.getGender() - 0.5) < 0.01:
            gender = gui3d.app.getLanguageString('neutral')
        else:
            gender = gui3d.app.getLanguageString('%.2f%% female, %.2f%% male') % ((1.0 - human.getGender()) * 100, human.getGender() * 100)
        
        age = human.getAgeYears()
        muscle = (human.getMuscle() * 100.0)
        weight = (50 + (150 - 50) * human.getWeight())
        coords = human.meshData.getCoords([8223,12361,13155])
        height = human.getHeightCm()
        if gui3d.app.settings['units'] == 'metric':
            units = 'cm'
        else:
            units = 'in'
            height *= 0.393700787

        self.setStatus('Gender: %s, Age: %d, Muscle: %.2f%%, Weight: %.2f%%, Height: %.2f %s', gender, age, muscle, weight, height, units)

    def syncRaceSliders(self, event):
        human = event.human
        for race, modifier, slider in self.raceSliders():
            slider.setValue(1.0/3)
            value = modifier.getValue(human)
            modifier.setValue(human, value)
            slider.setValue(value)

    def setStatus(self, format, *args):
        gui3d.app.statusPersist(format, *args)

    def onShow(self, event):
        self.syncStatus()
        super(MacroTaskView, self).onShow(event)

    def onHide(self, event):
        self.setStatus('')
        super(MacroTaskView, self).onHide(event)

    def onHumanChaging(self, event):
        super(MacroTaskView, self).onHumanChanging(event)
        if event.change in ('caucasian', 'asian', 'african'):
            self.syncRaceSliders(event)

    def onHumanChanged(self, event):
        super(MacroTaskView, self).onHumanChanged(event)
        if self.isVisible():
            self.syncStatus()
        if event.change in ('caucasian', 'asian', 'african'):
            self.syncRaceSliders(event)

def load(app):
    category = app.getCategory('Modelling')

    gui3d.app.noSetCamera = (lambda: None)

    for type in [MacroTaskView, GenderTaskView, FaceTaskView, TorsoTaskView, ArmsLegsTaskView, AsymmTaskView]:
        taskview = category.addTask(type(category))
        if taskview._group is not None:
            app.addLoadHandler(taskview._group, taskview.loadHandler)
            app.addSaveHandler(taskview.saveHandler)

def unload(app):
    pass
