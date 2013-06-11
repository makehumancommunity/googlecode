#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Armature options

"""

import gui


class ArmatureOptions:
    def __init__(self):

        self.rigtype = "python"
        self.description = ""
        self.scale = 1.0
        self.boneMap = None

        self.useMasterBone = False
        self.useMuscles = False
        self.addConnectingBones = False

        self.mergeSpine = False
        self.mergeFingers = False
        self.mergePalms = False
        self.mergeHead = False

        self.useSplitBones = False
        self.useSplitNames = False
        self.useDeformBones = False
        self.useDeformNames = False
        self.useIkArms = False
        self.useIkLegs = False
        self.useFingers = False

        # Options set by exporters
        self.useCustomShapes = False
        self.useCorrectives = False
        self.useExpressions = False
        self.feetOnGround = False
        self.useMasks = False

        # Obsolete options once used by mhx
        self.facepanel = False
        self.advancedSpine = False
        self.clothesRig = False


    def setExportOptions(self,
            useCustomShapes = False,
            useCorrectives = False,
            useExpressions = False,
            feetOnGround = False,
            useMasks = False,
            ):
        self.useCustomShapes = useCustomShapes
        self.useCorrectives = useCorrectives
        self.useExpressions = useExpressions
        self.feetOnGround = feetOnGround
        self.useMasks = useMasks


    def __repr__(self):
        return (
            "<ArmatureOptions\n" +
            "   rigtype : %s\n" % self.rigtype +
            "   description : %s\n" % self.description +
            "   scale : %s\n" % self.scale +
            "   boneMap : %s\n" % self.boneMap +
            "   useMuscles : %s\n" % self.useMuscles +
            "   addConnectingBones : %s\n" % self.addConnectingBones +
            "   mergeSpine : %s\n" % self.mergeSpine +
            "   mergeFingers : %s\n" % self.mergeFingers +
            "   mergePalms : %s\n" % self.mergePalms +
            "   mergeHead : %s\n" % self.mergeHead +
            "   useSplitBones : %s\n" % self.useSplitBones +
            "   useSplitNames : %s\n" % self.useSplitNames +
            "   useDeformBones : %s\n" % self.useDeformBones +
            "   useDeformNames : %s\n" % self.useDeformNames +
            "   useIkArms : %s\n" % self.useIkArms +
            "   useIkLegs : %s\n" % self.useIkLegs +
            "   useFingers : %s\n" % self.useFingers +
            "   useMasterBone : %s\n" % self.useMasterBone +
            "   useCorrectives : %s\n" % self.useCorrectives +
            "   feetOnGround : %s\n" % self.feetOnGround +
            "   useMasks : %s\n" % self.useMasks +
            ">")


    def fromSelector(self, selector):
        self.useMuscles = selector.useMuscles.selected
        self.useCorrectives = selector.useCorrectives.selected
        self.addConnectingBones = selector.addConnectingBones.selected

        self.mergeSpine = selector.mergeSpine.selected
        self.mergeFingers = selector.mergeFingers.selected
        self.mergePalms = selector.mergePalms.selected
        self.mergeHead = selector.mergeHead.selected

        self.useSplitBones = selector.useSplitBones.selected
        self.useSplitNames = selector.useSplitBones.selected
        self.useIkArms = selector.useIkArms.selected
        self.useIkLegs = selector.useIkLegs.selected
        if self.useSplitBones:
            self.useDeformBones = True
            self.useDeformNames = True
        else:
            self.useDeformBones = False
            self.useDeformNames = False

        self.useMasterBone = selector.useMasterBone.selected


    def reset(self, selector):
        self.__init__()
        selector.fromOptions(self)


    def presetGame(self, selector):
        self.__init__()
        self.description = (
"""
A minimal rig intended for games.
"""
        )

        self.mergeSpine = True
        self.mergeFingers = True
        self.mergePalms = True
        self.mergeHead = True

        selector.fromOptions(self)
        return self.description


    def presetSimple(self, selector):
        self.__init__()
        self.description = (
"""
A simple rig with only bone deformation.
"""
        )

        self.mergePalms = True

        selector.fromOptions(self)
        return self.description


    def presetMedium(self, selector):
        self.__init__()
        self.description = (
"""
A medium-complicated rig.
Some features only work with mhx export.
"""
        )

        self.useSplitBones = True
        self.useDeformBones = True
        self.useMuscles = True
        self.mergePalms = True

        selector.fromOptions(self)
        return self.description


    def presetAdvanced(self, selector):
        self.__init__()
        self.description = (
"""
An advanced rig intended for rendered applications.
It has muscle bones and corrective shapekeys.
Some features only work with mhx export or not at all.
"""
        )

        self.useMasterBone = True
        self.useSplitBones = True
        self.useDeformBones = True
        self.useMuscles = True
        self.useIkArms = True
        self.useIkLegs = True
        self.useFingers = True

        selector.fromOptions(self)
        return self.description


class ArmatureSelector:

    def __init__(self, box):
        self.box = box

        self.useMuscles = box.addWidget(gui.ToggleButton("Muscle bones"))
        self.useCorrectives = box.addWidget(gui.ToggleButton("Corrective shapekeys"))
        self.addConnectingBones = box.addWidget(gui.ToggleButton("Connecting bones"))

        self.mergeSpine = box.addWidget(gui.ToggleButton("Merge spine"))
        self.mergeFingers = box.addWidget(gui.ToggleButton("Merge fingers"))
        self.mergePalms = box.addWidget(gui.ToggleButton("Merge palms"))
        self.mergeHead = box.addWidget(gui.ToggleButton("Merge head"))

        self.useSplitBones = box.addWidget(gui.ToggleButton("Split forearm"))
        self.useIkArms = box.addWidget(gui.ToggleButton("Arm IK"))
        self.useIkLegs = box.addWidget(gui.ToggleButton("Leg IK"))
        self.useFingers = box.addWidget(gui.ToggleButton("Finger controls"))

        self.useMasterBone = box.addWidget(gui.ToggleButton("Master bone"))


    def fromOptions(self, options):
        self.useMuscles.setSelected(options.useMuscles)
        self.useCorrectives.setSelected(options.useCorrectives)
        self.addConnectingBones.setSelected(options.addConnectingBones)

        self.mergeSpine.setSelected(options.mergeSpine)
        self.mergeFingers.setSelected(options.mergeFingers)
        self.mergePalms.setSelected(options.mergePalms)
        self.mergeHead.setSelected(options.mergeHead)

        self.useSplitBones.setSelected(options.useSplitBones)
        self.useIkArms.setSelected(options.useIkArms)
        self.useIkLegs.setSelected(options.useIkLegs)
        self.useFingers.setSelected(options.useFingers)

        self.useMasterBone.setSelected(options.useFingers)

        for child in self.box.children:
            child.update()
