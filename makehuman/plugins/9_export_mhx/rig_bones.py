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

Bone definitions for Rigify rig
"""

from collections import OrderedDict
from .flags import *
from .rig_joints import *
from . import posebone
from posebone import addPoseBone

Joints = [
    ('l-heel',              'v', 12820),
    ('r-heel',              'v', 6223),
    ('l-ball-1',            'vo', (12889, -0.5, 0, 0)),
    ('l-ball-2',            'vo', (12889, 0.5, 0, 0)),
    ('r-ball-1',            'vo', (6292, 0.5, 0, 0)),
    ('r-ball-2',            'vo', (6292, -0.5, 0, 0)),

    ('l-hand-end',          'j', 'l-finger-3-1'),
    ('r-hand-end',          'j', 'r-finger-3-1'),
]


HeadsTails = [
    ('hips',                'pelvis', 'spine-1'),
    ('spine',               'spine-1', 'spine-2'),
    ('spine-1',             'spine-2', 'spine-3'),
    ('chest',               'spine-3', 'neck'),
    ('neck',                'neck', 'head'),
    ('head',                'head', 'head-2'),

    ('shoulder.L',          'l-clavicle', 'l-scapula'),
    ('upper_arm.L',         'l-shoulder', 'l-elbow'),
    ('forearm.L',           'l-elbow', 'l-hand'),
    ('hand.L',              'l-hand', 'l-hand-end'),

    ('shoulder.R',          'r-clavicle', 'r-scapula'),
    ('upper_arm.R',         'r-shoulder', 'r-elbow'),
    ('forearm.R',           'r-elbow', 'r-hand'),
    ('hand.R',              'r-hand', 'r-hand-end'),

    ('thumb.01.L',          'l-finger-1-1', 'l-finger-1-2'),
    ('thumb.02.L',          'l-finger-1-2', 'l-finger-1-3'),
    ('thumb.03.L',          'l-finger-1-3', 'l-finger-1-4'),

    ('thumb.01.R',          'r-finger-1-1', 'r-finger-1-2'),
    ('thumb.02.R',          'r-finger-1-2', 'r-finger-1-3'),
    ('thumb.03.R',          'r-finger-1-3', 'r-finger-1-4'),

    ('palm.01.L',           'l-hand-3', 'l-finger-2-1'),
    ('f_index.01.L',        'l-finger-2-1', 'l-finger-2-2'),
    ('f_index.02.L',        'l-finger-2-2', 'l-finger-2-3'),
    ('f_index.03.L',        'l-finger-2-3', 'l-finger-2-4'),

    ('palm.01.R',           'r-hand-3', 'r-finger-2-1'),
    ('f_index.01.R',        'r-finger-2-1', 'r-finger-2-2'),
    ('f_index.02.R',        'r-finger-2-2', 'r-finger-2-3'),
    ('f_index.03.R',        'r-finger-2-3', 'r-finger-2-4'),

    ('palm.02.L',           'l-hand-3', 'l-finger-3-1'),
    ('f_middle.01.L',       'l-finger-3-1', 'l-finger-3-2'),
    ('f_middle.02.L',       'l-finger-3-2', 'l-finger-3-3'),
    ('f_middle.03.L',       'l-finger-3-3', 'l-finger-3-4'),

    ('palm.02.R',           'r-hand-3', 'r-finger-3-1'),
    ('f_middle.01.R',       'r-finger-3-1', 'r-finger-3-2'),
    ('f_middle.02.R',       'r-finger-3-2', 'r-finger-3-3'),
    ('f_middle.03.R',       'r-finger-3-3', 'r-finger-3-4'),

    ('palm.03.L',           'l-hand-2', 'l-finger-4-1'),
    ('f_ring.01.L',         'l-finger-4-1', 'l-finger-4-2'),
    ('f_ring.02.L',         'l-finger-4-2', 'l-finger-4-3'),
    ('f_ring.03.L',         'l-finger-4-3', 'l-finger-4-4'),

    ('palm.03.R',           'r-hand-2', 'r-finger-4-1'),
    ('f_ring.01.R',         'r-finger-4-1', 'r-finger-4-2'),
    ('f_ring.02.R',         'r-finger-4-2', 'r-finger-4-3'),
    ('f_ring.03.R',         'r-finger-4-3', 'r-finger-4-4'),

    ('palm.04.L',           'l-hand-2', 'l-finger-5-1'),
    ('f_pinky.01.L',        'l-finger-5-1', 'l-finger-5-2'),
    ('f_pinky.02.L',        'l-finger-5-2', 'l-finger-5-3'),
    ('f_pinky.03.L',        'l-finger-5-3', 'l-finger-5-4'),

    ('palm.04.R',           'r-hand-2', 'r-finger-5-1'),
    ('f_pinky.01.R',        'r-finger-5-1', 'r-finger-5-2'),
    ('f_pinky.02.R',        'r-finger-5-2', 'r-finger-5-3'),
    ('f_pinky.03.R',        'r-finger-5-3', 'r-finger-5-4'),

    ('thigh.L',             'l-upperleg', 'l-knee'),
    ('shin.L',              'l-knee', 'l-ankle'),
    ('foot.L',              'l-ankle', 'l-foot-1'),
    ('toe.L',               'l-foot-1', 'l-foot-2'),
    ('heel.L',              'l-ankle', 'l-heel'),
    ('heel.02.L',           'l-ball-1', 'l-ball-2'),

    ('thigh.R',             'r-upperleg', 'r-knee'),
    ('shin.R',              'r-knee', 'r-ankle'),
    ('foot.R',              'r-ankle', 'r-foot-1'),
    ('toe.R',               'r-foot-1', 'r-foot-2'),
    ('heel.R',              'r-ankle', 'r-heel'),
    ('heel.02.R',           'r-ball-1', 'r-ball-2'),

]

Armature = OrderedDict([
    ('hips',                (0, None, F_DEF, L_UPSPNFK, NoBB)),
    ('spine',               (0, 'hips', F_DEF+F_CON, L_UPSPNFK, NoBB)),
    ('spine-1',             (0, 'spine', F_DEF+F_CON, L_UPSPNFK, NoBB)),
    ('chest',               (0, 'spine-1', F_DEF+F_CON, L_UPSPNFK, NoBB)),
    ('neck',                (0, 'chest', F_DEF+F_CON, L_UPSPNFK, NoBB)),
    ('head',                (0, 'neck', F_DEF+F_CON, L_UPSPNFK, NoBB)),

    ('shoulder.L',          (0, 'chest', F_DEF, L_LARMFK, NoBB)),
    ('upper_arm.L',         (45*D, 'shoulder.L', F_DEF, L_LARMFK, NoBB)),
    ('forearm.L',           (131*D, 'upper_arm.L', F_DEF+F_CON, L_LARMFK, NoBB)),
    ('hand.L',              (-120*D, 'forearm.L', F_CON, L_LARMFK, NoBB)),

    ('shoulder.R',          (0, 'chest', F_DEF, L_RARMFK, NoBB)),
    ('upper_arm.R',         (-45*D, 'shoulder.R', F_DEF, L_RARMFK, NoBB)),
    ('forearm.R',           (-131*D, 'upper_arm.R', F_DEF+F_CON, L_RARMFK, NoBB)),
    ('hand.R',              (120*D, 'forearm.R', F_CON, L_RARMFK, NoBB)),

    ('palm.01.L',           (-143*D, 'hand.L', F_DEF, L_LPALM, NoBB)),
    ('f_index.01.L',        (-82*D, 'palm.01.L', F_DEF+F_CON, L_LHANDFK, NoBB)),
    ('f_index.02.L',        (-65*D, 'f_index.01.L', F_DEF+F_CON, L_LHANDFK, NoBB)),
    ('f_index.03.L',        (-56*D, 'f_index.02.L', F_DEF+F_CON, L_LHANDFK, NoBB)),

    ('palm.01.R',           (143*D, 'hand.R', F_DEF, L_RPALM, NoBB)),
    ('f_index.01.R',        (82*D, 'palm.01.R', F_DEF+F_CON, L_RHANDFK, NoBB)),
    ('f_index.02.R',        (65*D, 'f_index.01.R', F_DEF+F_CON, L_RHANDFK, NoBB)),
    ('f_index.03.R',        (56*D, 'f_index.02.R', F_DEF+F_CON, L_RHANDFK, NoBB)),

    ('thumb.01.L',          (154*D, 'palm.01.L', F_DEF, L_LPALM, NoBB)),
    ('thumb.02.L',          (70*D, 'thumb.01.L', F_DEF+F_CON, L_LHANDFK, NoBB)),
    ('thumb.03.L',          (55*D, 'thumb.02.L', F_DEF+F_CON, L_LHANDFK, NoBB)),

    ('thumb.01.R',          (-154*D, 'palm.01.R', F_DEF, L_RPALM, NoBB)),
    ('thumb.02.R',          (-70*D, 'thumb.01.R', F_DEF+F_CON, L_RHANDFK, NoBB)),
    ('thumb.03.R',          (-55*D, 'thumb.02.R', F_DEF+F_CON, L_RHANDFK, NoBB)),

    ('palm.02.L',           (-153*D, 'hand.L', F_DEF, L_LPALM, NoBB)),
    ('f_middle.01.L',       (-110*D, 'palm.02.L', F_DEF+F_CON, L_LHANDFK, NoBB)),
    ('f_middle.02.L',       (-93*D, 'f_middle.01.L', F_DEF+F_CON, L_LHANDFK, NoBB)),
    ('f_middle.03.L',       (-89*D, 'f_middle.02.L', F_DEF+F_CON, L_LHANDFK, NoBB)),
    
    ('palm.02.R',           (153*D, 'hand.R', F_DEF, L_RPALM, NoBB)),
    ('f_middle.01.R',       (110*D, 'palm.02.R', F_DEF+F_CON, L_RHANDFK, NoBB)),
    ('f_middle.02.R',       (93*D, 'f_middle.01.R', F_DEF+F_CON, L_RHANDFK, NoBB)),
    ('f_middle.03.R',       (89*D, 'f_middle.02.R', F_DEF+F_CON, L_RHANDFK, NoBB)),
    
    ('palm.03.L',           (-161*D, 'hand.L', F_DEF, L_LPALM, NoBB)),
    ('f_ring.01.L',         (-107*D, 'palm.03.L', F_DEF+F_CON, L_LHANDFK, NoBB)),
    ('f_ring.02.L',         (-98*D, 'f_ring.01.L', F_DEF+F_CON, L_LHANDFK, NoBB)),
    ('f_ring.03.L',         (-83*D, 'f_ring.02.L', F_DEF+F_CON, L_LHANDFK, NoBB)),
    
    ('palm.03.R',           (161*D, 'hand.R', F_DEF, L_RPALM, NoBB)),
    ('f_ring.01.R',         (107*D, 'palm.03.R', F_DEF+F_CON, L_RHANDFK, NoBB)),
    ('f_ring.02.R',         (98*D, 'f_ring.01.R', F_DEF+F_CON, L_RHANDFK, NoBB)),
    ('f_ring.03.R',         (83*D, 'f_ring.02.R', F_DEF+F_CON, L_RHANDFK, NoBB)),
    
    ('palm.04.L',           (-144*D, 'hand.L', F_DEF, L_LPALM, NoBB)),
    ('f_pinky.01.L',        (-103*D, 'palm.04.L', F_DEF+F_CON, L_LHANDFK, NoBB)),
    ('f_pinky.02.L',        (-99*D, 'f_pinky.01.L', F_DEF+F_CON, L_LHANDFK, NoBB)),
    ('f_pinky.03.L',        (-90*D, 'f_pinky.02.L', F_DEF+F_CON, L_LHANDFK, NoBB)),

    ('palm.04.R',           (144*D, 'hand.R', F_DEF, L_RPALM, NoBB)),
    ('f_pinky.01.R',        (103*D, 'palm.04.R', F_DEF+F_CON, L_RHANDFK, NoBB)),
    ('f_pinky.02.R',        (99*D, 'f_pinky.01.R', F_DEF+F_CON, L_RHANDFK, NoBB)),
    ('f_pinky.03.R',        (90*D, 'f_pinky.02.R', F_DEF+F_CON, L_RHANDFK, NoBB)),

    ('thigh.L',             (-10*D, 'hips', F_DEF, L_LLEGFK, NoBB)),
    ('shin.L',              (-7*D, 'thigh.L', F_DEF+F_CON, L_LLEGFK, NoBB)),
    ('foot.L',              (-31*D, 'shin.L', F_DEF+F_CON, L_LLEGFK, NoBB)),
    ('toe.L',               (-36*D, 'foot.L', F_DEF+F_CON, L_LLEGFK, NoBB)),
    ('heel.L',              (180*D, 'shin.L', F_CON, L_HELP2, NoBB)),
    ('heel.02.L',           (0, 'heel.L', 0, L_HELP2, NoBB)),

    ('thigh.R',             (10*D, 'hips', F_DEF, L_RLEGFK, NoBB)),
    ('shin.R',              (7*D, 'thigh.R', F_DEF+F_CON, L_RLEGFK, NoBB)),
    ('foot.R',              (31*D, 'shin.R', F_DEF+F_CON, L_RLEGFK, NoBB)),
    ('toe.R',               (36*D, 'foot.R', F_DEF+F_CON, L_RLEGFK, NoBB)),
    ('heel.R',              (180*D, 'shin.R', F_CON, L_HELP2, NoBB)),
    ('heel.02.R',           (0, 'heel.R', 0, L_HELP2, NoBB)),
])

RotationLimits = {
    'hips' :            (-50*D,40*D, -45*D,45*D, -16*D,16*D),
    'spine' :           (-60*D,90*D, -60*D,60*D, -60*D,60*D),
    'spine-1' :         (-90*D,70*D, -20*D,20*D, -50*D,50*D),
    'chest' :           (-20*D,20*D, 0,0, -20*D,20*D),
    'neck' :            (-60*D,40*D, -45*D,45*D, -60*D,60*D),

    'thigh.L' :         (-160*D,120*D, -90*D,90*D, -170*D,80*D),
    'thigh.R' :         (-160*D,120*D, -90*D,90*D, -80*D,170*D),
    'shin.L' :          (-20*D,170*D,-40*D,40*D, 0,0),
    'shin.R' :          (-20*D,170*D,-40*D,40*D, 0,0),
    'foot.L' :          (-90*D,45*D, -30*D,15*D, 0,0),
    'foot.R' :          (-90*D,45*D, -15*D,30*D, 0,0),
    'toe.L' :           (-20*D,60*D, 0,0, 0,0),
    'toe.R' :           (-20*D,60*D, 0,0, 0,0),

    'shoulder.L' :      (-16*D,40*D, -40*D,40*D,  -45*D,45*D),
    'shoulder.L' :      (-16*D,40*D,  -40*D,40*D,  -45*D,45*D),
    'upper_arm.L' :     (-135*D,135*D, -60*D,60*D, -135*D,135*D),
    'upper_arm.R' :     (-135*D,135*D, -60*D,60*D, -135*D,135*D),
    'forearm.L' :       (-10*D,100*D, -178*D,150*D, -175*D,10*D),
    'forearm.R' :       (-10*D,100*D, -150*D,178*D, -10*D,175*D),
    'hand.L' :          (-90*D,70*D, -10*D,10*D, -20*D,20*D),
    'hand.R' :          (-90*D,70*D, -10*D,10*D, -20*D,20*D),
}

CustomShapes = {
    'hips' :            'GZM_Crown',
    'spine' :           'GZM_CircleSpine',
    'spine-1' :         'GZM_CircleSpine',
    'chest' :           'GZM_CircleChest',
    'neck' :            'GZM_Neck',
    'head' :            'GZM_Head',
    
    'thigh.L' :         'GZM_Circle025',
    'thigh.R' :         'GZM_Circle025',
    'shin.L' :          'GZM_Circle025',
    'shin.R' :          'GZM_Circle025',
    'foot.L' :          'GZM_Foot',
    'foot.R' :          'GZM_Foot',
    'toe.L' :           'GZM_Toe_L',
    'toe.R' :           'GZM_Toe_R',

    'shoulder.L' :      'GZM_Shoulder',
    'shoulder.R' :      'GZM_Shoulder',
    'upper_arm.L' :     'GZM_Circle025',
    'upper_arm.R' :     'GZM_Circle025',
    'forearm.L' :       'GZM_Circle025',
    'forearm.R' :       'GZM_Circle025',
    'hand.L' :          'GZM_Hand',
    'hand.R' :          'GZM_Hand',
}

Constraints = {}
    

ObjectProps = [
]


ArmatureProps = [
    ('MhxScale', 1.000),
    ('MhxRig', '"Control"'),
    ('MhxVisemeSet', '"BodyLanguage"'),
]

