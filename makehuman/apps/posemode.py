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

TODO
"""

import gui3d
from armature.pose import createPoseRig
import humanmodifier
import log

def resetPoseMode():
    global _InPoseMode
    log.message("Reset pose mode")
    _InPoseMode = False
    if gui3d.app:
        human = gui3d.app.selectedHuman
        if human:
            human.restoreUnposedCoords()

resetPoseMode()


def printVert(human):
    return
    for vn in [8202]:
        x = human.meshData.coord[vn]
        if human.unposedCoords is None:
            y = (0,0,0)
        else:
            y = human.unposedCoords[vn]
        log.debug("  %d: (%.3f %.3f %.3f) (%.3f %.3f %.3f)", vn,x[0],x[1],x[2],y[0],y[1],y[2])


def enterPoseMode():
    global _InPoseMode
    if _InPoseMode:
        return
    log.message("Enter pose mode")
    _InPoseMode = True
    human = gui3d.app.selectedHuman
    human.setUnposedCoords()
    log.message("Pose mode entered")
    printVert(human)


def exitPoseMode():
    global _InPoseMode
    if not _InPoseMode:
        return
    log.message("Exit pose mode")
    human = gui3d.app.selectedHuman
    human.restoreUnposedCoords()
    _InPoseMode = False
    log.message("Pose mode exited")
    printVert(human)


def changePoseMode(event):
    human = event.human
    #log.debug("Change pose mode %s w=%s e=%s", _InPoseMode, human.warpsNeedReset, event.change)
    if human and human.warpsNeedReset:
        exitPoseMode()
    elif event.change not in ["targets", "warp"]:
        exitPoseMode()
    if event.change == "reset":
        resetPoseMode()

#----------------------------------------------------------
#   class PoseModifierSlider
#----------------------------------------------------------

class PoseModifierSlider(humanmodifier.ModifierSlider):
    def __init__(self, label, modifier):
        humanmodifier.ModifierSlider.__init__(self, label=label, modifier=modifier, warpResetNeeded=False)

    def onChanging(self, value):
        enterPoseMode()
        humanmodifier.ModifierSlider.onChanging(self, value)

    def onChange(self, value):
        enterPoseMode()
        humanmodifier.ModifierSlider.onChange(self, value)

