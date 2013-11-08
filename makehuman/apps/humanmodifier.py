#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

__docformat__ = 'restructuredtext'

import algos3d
import guicommon
from core import G
import events3d
import operator
import numpy as np
import log
import targets


# Gender
# -
# female          1.0  0.5  1.0
# male            0.0  0.5  1.0

# Age
# -
# baby            1.0  0.0  0.0  0.0
# child           0.0  1.0  0.0  0.0
# young           0.0  0.0  1.0  0.0
# old             0.0  0.0  0.0  1.0

# Weight
# -
# light           1.0  0.0  0.0
# averageWeight   0.0  1.0  0.0
# heavy           0.0  0.0  1.0

# Muscle
# -
# flaccid         1.0  0.0  0.0
# averageTone     0.0  1.0  0.0
# muscle          0.0  0.0  1.0

# Height
# -
# dwarf           1.0  0.0  0.0
# giant           0.0  0.0  1.0

# BreastFirmness
# -
# firmness0       1.0  0.5  1.0
# firmness1       0.0  0.5  1.0

# BreastSize
# -
# cup1            1.0  0.0  0.0
# cup2            0.0  0.0  1.0

# African

# Asian

# Caucasian

class DetailAction(guicommon.Action):
    def __init__(self, human, before, after, update=True):
        super(DetailAction, self).__init__('Change detail')
        self.human = human
        self.before = before
        self.after = after
        self.update = update

    def do(self):
        for (target, value) in self.after.iteritems():
            self.human.setDetail(target, value)
        self.human.applyAllTargets(G.app.progress, update=self.update)
        return True

    def undo(self):
        for (target, value) in self.before.iteritems():
            self.human.setDetail(target, value)
        self.human.applyAllTargets()
        return True

class ModifierAction(guicommon.Action):
    def __init__(self, human, modifier, before, after, postAction):
        super(ModifierAction, self).__init__('Change modifier')
        self.human = human
        self.modifier = modifier
        self.before = before
        self.after = after
        self.postAction = postAction

    def do(self):
        self.modifier.setValue(self.human, self.after)
        self.human.applyAllTargets(G.app.progress)
        self.postAction()
        return True

    def undo(self):
        self.modifier.setValue(self.human, self.before)
        self.human.applyAllTargets(G.app.progress)
        self.postAction()
        return True

class BaseModifier(object):

    def __init__(self):
        self.verts = None
        self.faces = None
        self.eventType = 'modifier'
        self.targets = []

        self.macroVariable = None
        self.macroDependencies = []
        G.app.selectedHuman.modifiers.append(self)

    def setValue(self, human, value):
        value = self.clampValue(value)
        factors = self.getFactors(human, value)

        for target in self.targets:
            human.setDetail(target[0], value * reduce(operator.mul, [factors[factor] for factor in target[1]]))

    def clampValue(self, value):
        raise NotImplementedError()

    def getFactors(self, human, value):
        raise NotImplementedError()

    def getValue(self, human):
        return sum([human.getDetail(target[0]) for target in self.targets])

    def buildLists(self):
        human = G.app.selectedHuman
        # Collect vertex and face indices if we didn't yet
        if self.verts is None and self.faces is None:
            # Collect verts
            vmask = np.zeros(human.meshData.getVertexCount(), dtype=bool)
            for target in self.targets:
                t = algos3d.getTarget(human.meshData, target[0])
                vmask[t.verts] = True
            self.verts = np.argwhere(vmask)[...,0]
            del vmask

            # collect faces
            self.faces = human.meshData.getFacesForVertices(self.verts)

    def updateValue(self, human, value, updateNormals=1):
        if self.verts is None and self.faces is None:
            self.buildLists()

        # Update detail state
        old_detail = [human.getDetail(target[0]) for target in self.targets]
        self.setValue(human, value)
        new_detail = [human.getDetail(target[0]) for target in self.targets]

        # Apply changes
        for target, old, new in zip(self.targets, old_detail, new_detail):
            if new == old:
                continue
            algos3d.loadTranslationTarget(human.meshData, target[0], new - old, None, 0, 0)

        # Update vertices
        if updateNormals:
            human.meshData.calcNormals(1, 1, self.verts, self.faces)
        human.meshData.update()
        event = events3d.HumanEvent(human, self.eventType)
        #print 'onChanging %s' % event
        event.modifier = self.name
        #print self.name
        human.callEvent('onChanging', event)

class Modifier(BaseModifier):

    def __init__(self, left, right):
        super(Modifier, self).__init__()
        self.left = left
        self.right = right
        self.targets = [[self.left], [self.right]]

    def setValue(self, human, value, update=1):

        value = max(-1.0, min(1.0, value))

        left = -value if value < 0.0 else 0.0
        right = value if value > 0.0 else 0.0

        human.setDetail(self.left, left)
        human.setDetail(self.right, right)

    def getValue(self, human):

        value = human.getDetail(self.left)
        if value:
            return -value
        value = human.getDetail(self.right)
        if value:
            return value
        else:
            return 0.0

class SimpleModifier(BaseModifier):
    # overrides

    def __init__(self, template):
        super(SimpleModifier, self).__init__()
        self.template = template
        self.targets = self.expandTemplate([(self.template, [])])

        self.macroDependencies = []

    def expandTemplate(self, targets):

        targets = [(target[0], target[1] + ['dummy']) for target in targets]

        return targets

    def getFactors(self, human, value):
        # TODO this is useless
        factors = {
            'dummy': 1.0
        }

        return factors

    def clampValue(self, value):
        return max(0.0, min(1.0, value))

class GenericModifier(BaseModifier):
    @staticmethod
    def findTargets(path):
        """
        Retrieve a list of targets grouped under the specified target path
        (which is not directly a filesystem path but rather an abstraction
        with a path being a hierarchic string of atoms separated by a - symbol).

        The result is a list of tuples, with each tuple as: 
            (targetpath, factordependencies)
        With targetpath referencing the filepath of the .target file,
        and factordependencies a list with the names of variables or factors 
        that influence the weight with how much the target file is applied.
        The resulting weight with which a target is applied is the 
        multiplication of all the factor values declared in the 
        factorDependencies list.

        Some of these factordependencies come from predeclared macro parameters
        (such as age, race, weight, gender, ...) and are already supplied by the
        targets module which automatically extracts known parameters from the
        target path or filename.
        Additional factordependencies can be added at will to control the
        weighting of a target directly (for example to apply the value of this
        modifier to its targets).
        The other way of setting modifier values to factors to eventually set 
        the weight of targets (which is used by macro modifiers) is to make sure
        the xVal variables of the human object are updated, by calling 
        corresponding setters on the human object. getFactors() will by default
        resolve the values of known xVal variables to known factor variable 
        names.

        factordependencies can be any name and are not restricted to tokens that
        occur in the target path. Though for each factordependency, getFactors()
        will have to return a matching value.
        """
        if path is None:
            return []
        path = tuple(path.split('-'))
        result = []
        if path not in targets.getTargets().groups:
            log.debug('missing target %s', path)
        for target in targets.getTargets().groups.get(path, []):
            keys = [var
                    for var in target.data.itervalues()
                    if var is not None]
            keys.append('-'.join(target.key))
            result.append((target.path, keys))
        return result

    @staticmethod
    def findMacroDependencies(path):
        result = set()
        if path is None:
            return result
        path = tuple(path.split('-'))
        for target in targets.getTargets().groups.get(path, []):
            keys = [key
                    for key, var in target.data.iteritems()
                    if var is not None]
            result.update(keys)
        return result

    def clampValue(self, value):
        value = min(1.0, value)
        if self.left is not None:
            value = max(-1.0, value)
        else:
            value = max( 0.0, value)
        return value

    def setValue(self, human, value):
        value = self.clampValue(value)
        factors = self.getFactors(human, value)

        for tpath, tfactors in self.targets:
            human.setDetail(tpath, reduce((lambda x, y: x * y), [factors[factor] for factor in tfactors]))

    @staticmethod
    def parseTarget(target):
        return target[0].split('/')[-1].split('.')[0].split('-')

    def getValue(self, human):
        right = sum([human.getDetail(target[0]) for target in self.r_targets])
        if right:
            return right
        else:
            return -sum([human.getDetail(target[0]) for target in self.l_targets])

    _variables = targets._value_cat.keys()

    def getFactors(self, human, value):
        #print 'genericModifier: getFactors'
        return dict((name, getattr(human, name + 'Val'))
                    for name in self._variables)

class UniversalModifier(GenericModifier):
    def __init__(self, left, right, center=None):
        super(UniversalModifier, self).__init__()

        self.left = left
        self.right = right
        self.center = center

        self.l_targets = self.findTargets(left)
        self.r_targets = self.findTargets(right)
        self.c_targets = self.findTargets(center)

        self.macroDependencies = self.findMacroDependencies(left)
        self.macroDependencies.update(self.findMacroDependencies(right))
        self.macroDependencies.update(self.findMacroDependencies(center))
        self.macroDependencies = list(self.macroDependencies)

        self.targets = self.l_targets + self.r_targets + self.c_targets

    def getFactors(self, human, value):
        #print "UniversalModifier factors:"
        factors = super(UniversalModifier, self).getFactors(human, value)

        if self.left is not None:
            factors[self.left] = -min(value, 0.0)
        if self.center is not None:
            factors[self.center] = 1.0 - abs(value)
        factors[self.right] = max(0.0, value)

        #print 'factors:'
        #print factors

        return factors

class MacroModifier(GenericModifier):
    def __init__(self, base, name, variable):
        # TODO name is not used! (None is passed from modeling plugin)
        super(MacroModifier, self).__init__()

        self.name = '-'.join(atom
                             for atom in (base, name)
                             if atom is not None)
        self.variable = variable
        self.setter = 'set' + self.variable
        self.getter = 'get' + self.variable

        self.targets = self.findTargets(self.name)
        if self.name == 'macrodetails':
            # Update weight/muscle modifiers when macro modifiers are updated
            self.targets.extend(self.findTargets('macrodetails-universal')) # TODO make a more generic solution to this using dependencies (while still allowing to propagate updates to a select group of depencies during slider dragging (onChanging))
        # log.debug('macro modifier %s.%s(%s): %s', base, name, variable, self.targets)

        self.macroDependencies = self.findMacroDependencies(self.name)
        var = self.getMacroVariable()
        if var:
            self.macroDependencies.remove(var)
        self.macroDependencies = list(self.macroDependencies)

        self.macroVariable = var

    def getMacroVariable(self):
        """
        The macro variable modified by this modifier.
        """
        if self.variable:
            var = self.variable.lower()
            if var in targets._categories:
                return var
            elif var in targets._value_cat:
                # necessary for caucasian, asian, african
                return targets._value_cat[var]
        return None

    def getValue(self, human):
        return getattr(human, self.getter)()

    def setValue(self, human, value):
        value = self.clampValue(value)
        getattr(human, self.setter)(value)
        super(MacroModifier, self).setValue(human, value)

    def clampValue(self, value):
        return max(0.0, min(1.0, value))

    def getFactors(self, human, value):
        factors = super(MacroModifier, self).getFactors(human, value)
        factors[self.name] = 1.0
        if self.name == 'macrodetails':
            # Update weight/muscle modifiers when macro modifiers are updated
            factors['macrodetails-universal'] = 1.0
        return factors

    def buildLists(self):
        pass

def getModifierDependencies():
    human = G.app.selectedHuman
    varMapping = dict()
    for m in human.modifiers:
        if m.macroVariable:
            if m.macroVariable in varMapping:
                # This can happen for race (maybe we only need to map the modifier.name group, not individual modifiers)
                log.error("Error, multiple modifiers setting var %s", m.macroVariable)
            else:
                varMapping[m.macroVariable] = m

    for m in human.modifiers:
        if len(m.macroDependencies) > 0:
            for var in m.macroDependencies:
                if var not in varMapping:
                    log.error("Error var %s not mapped", var)
                    continue
                depM = varMapping[var]
                if depM.name == m.name: # Beware, name is only available for macro modifiers
                    log.debug("%s depends on %s but both are in same group, ignoring dependency", m.name+"/"+m.variable, depM.name+"/"+depM.variable) # variable is only available for macro modifiers
                else:
                    log.debug("%s depends on %s", m.name+"/"+m.variable, depM.name+"/"+depM.variable)
