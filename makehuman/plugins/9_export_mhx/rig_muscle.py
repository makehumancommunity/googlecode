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

PlatysmaLength  = 0.9
LatDorsiLength  = 0.5
BicepsLength    = 0.25
BracLength  = 0.5
FemorisLength   = 0.5
FemorisGoal     = 0.162
SoleusLength    = 0.4

Joints = [
    ('plexus',              'v', 4070),
    ('l-pect-1',            'v', 10730),
    ('r-pect-1',            'v', 4078),
    
    ('l-plat-1',            'v', 7587),
    ('r-plat-1',            'v', 885),
    ('l-plat-2',            'l', ((1-PlatysmaLength, 'l-plat-1'), (PlatysmaLength, 'l-clavicle'))),
    ('r-plat-2',            'l', ((1-PlatysmaLength, 'r-plat-1'), (PlatysmaLength, 'r-clavicle'))),
    
    ('l-trap-1',            'v', 7561),
    ('r-trap-1',            'v', 850),
    ('l-trap-2',            'v', 8232),
    ('r-trap-2',            'v', 1554),

    ('l-scapula-1',         'vl', ((0.25, 8070), (0.75, 8238))),
    ('r-scapula-1',         'vl', ((0.25, 1378), (0.75, 1560))),
    ('l-scapula-2',         'l', ((0.5, 'l-scapula-1'), (0.5, 'spine-2'))),
    ('r-scapula-2',         'l', ((0.5, 'r-scapula-1'), (0.5, 'spine-2'))),

    ('l-lat-2',             'l', ((1-LatDorsiLength, 'spine-2'), (LatDorsiLength, 'l-scapula'))),
    ('r-lat-2',             'l', ((1-LatDorsiLength, 'spine-2'), (LatDorsiLength, 'r-scapula'))),

    ('l-biceps-1',          'l', ((0.5, 'l-shoulder'), (0.5, 'l-elbow'))),
    ('r-biceps-1',          'l', ((0.5, 'r-shoulder'), (0.5, 'r-elbow'))),
    ('l-biceps-3',          'v', 8385),
    ('r-biceps-3',          'v', 1713),
    ('l-biceps-2',          'l', ((0.5, 'l-biceps-1'), (0.5, 'l-biceps-3'))),
    ('r-biceps-2',          'l', ((0.5, 'r-biceps-1'), (0.5, 'r-biceps-3'))),

    ('l-triceps-3',         'v', 8394),
    ('r-triceps-3',         'v', 1722),
    ('l-triceps-2',         'l', ((1-BicepsLength, 'l-biceps-1'), (BicepsLength, 'l-triceps-3'))),
    ('r-triceps-2',         'l', ((1-BicepsLength, 'r-biceps-1'), (BicepsLength, 'r-triceps-3'))),

    ('l-brac-1',            'vl', ((0.9, 10076), (0.1, 10543))),
    ('r-brac-1',            'vl', ((0.9, 3408), (0.1, 3878))),
    ('l-pron-1',            'vl', ((0.1, 10076), (0.9, 10543))),
    ('r-pron-1',            'vl', ((0.1, 3408), (0.9, 3878))),    
    ('l-brac-3',            'vl', ((0.6, 10554), (0.4, 10220))),
    ('r-brac-3',            'vl', ((0.6, 3889), (0.4, 3552))),
    ('l-pron-2',            'vl', ((0.4, 10554), (0.6, 10220))),
    ('r-pron-2',            'vl', ((0.4, 3889), (0.6, 3552))),
    ('l-brac-2',            'l', ((1-BracLength, 'l-brac-1'), (BracLength, 'l-brac-3'))),
    ('r-brac-2',            'l', ((1-BracLength, 'r-brac-1'), (BracLength, 'r-brac-3'))),

    ('pubis',               'vl', ((0.9, 4341), (0.1, 4250))),
    ('l-hipside',           'vl', ((0.9, 10909), (0.1, 4279))),
    ('r-hipside',           'vl', ((0.1, 10909), (0.9, 4279))),
    ('l-hip',               'vl', ((0.9, 10778), (0.1, 4135))),
    ('r-hip',               'vl', ((0.1, 10778), (0.9, 4135))),
    ('l-gluteus',           'v', 10867),
    ('r-gluteus',           'v', 4233),

    ('l-quadriceps',        'vl', ((0.75, 11135), (0.25, 11130))),
    ('r-quadriceps',        'vl', ((0.75, 4517), (0.25, 4512))),

    ('l-fem-1',             'vl', ((0.2, 11033), (0.8, 11020))),
    ('r-fem-1',             'vl', ((0.2, 4415), (0.8, 4402))),
    ('l-fem-3',             'l', ((1-FemorisGoal, 'l-knee'), (FemorisGoal, 'l-ankle'))),
    ('r-fem-3',             'l', ((1-FemorisGoal, 'r-knee'), (FemorisGoal, 'r-ankle'))),
    ('l-fem-2',             'l', ((1-FemorisLength, 'l-fem-1'), (FemorisLength, 'l-fem-3'))),
    ('r-fem-2',             'l', ((1-FemorisLength, 'r-fem-1'), (FemorisLength, 'r-fem-3'))),

    ('l-knee-1',            'vl', ((0.8, 11116), (0.2, 11111))),
    ('r-knee-1',            'vl', ((0.8, 4498), (0.2, 4493))),
    ('l-knee-2',            'vl', ((0.8, 11135), (0.2, 11130))),
    ('r-knee-2',            'vl', ((0.8, 4517), (0.2, 4512))),

    ('l-soleus-1',          'vl', ((0.5, 11293), (0.5, 11302))),
    ('r-soleus-1',          'vl', ((0.5, 4675), (0.5, 4684))),
    ('l-soleus-2',          'l', ((1-SoleusLength, 'l-soleus-1'), (SoleusLength, 'l-heel'))),
    ('r-soleus-2',          'l', ((1-SoleusLength, 'r-soleus-1'), (SoleusLength, 'r-heel'))),
]

HeadsTails = [
    ('ribcage.L',           'plexus', 'l-pect-1'),
    ('ribcage.R',           'plexus', 'r-pect-1'),
    ('pectoralis.L',        'l-pect-1', 'l-scapula'),
    ('pectoralis.R',        'r-pect-1', 'r-scapula'),
    ('platysma.L',          'l-plat-1', 'l-plat-2'),
    ('platysma.R',          'r-plat-1', 'r-plat-2'),
    ('trapezius.L',         'l-trap-1', 'l-trap-2'),
    ('trapezius.R',         'r-trap-1', 'r-trap-2'),
    ('trap_goal.L',         'l-shoulder', 'l-trap-2'),
    ('trap_goal.R',         'r-shoulder', 'r-trap-2'),
    ('scapula.L',           'l-scapula-1', 'l-scapula-2'),
    ('scapula.R',           'r-scapula-1', 'r-scapula-2'),
    ('lat_dorsi.L',         'spine-2', 'l-lat-2'),
    ('lat_dorsi.R',         'spine-2', 'r-lat-2'),
    ('deltoid.L',           'l-scapula', 'l-shoulder'),
    ('deltoid.R',           'r-scapula', 'r-shoulder'),

    ('biceps.L',            'l-biceps-1', 'l-biceps-2'),
    ('biceps.R',            'r-biceps-1', 'r-biceps-2'),
    ('triceps.L',           'l-elbow', 'l-triceps-2'),
    ('triceps.R',           'r-elbow', 'r-triceps-2'),

    ('trg_elbow.L',         'l-elbow', 'l-brac-1'),
    ('trg_elbow.R',         'r-elbow', 'r-brac-1'),
    ('pronator.L',          'l-brac-1', 'l-brac-2'),
    ('pronator.R',          'r-brac-1', 'r-brac-2'),
    ('brachioradialis.L',   'l-pron-1', 'l-pron-2'),
    ('brachioradialis.R',   'r-pron-1', 'r-pron-2'),
    ('forearmhook.L',       'l-brac-3', 'l-pron-2'),
    ('forearmhook.R',       'r-brac-3', 'r-pron-2'),
    
    ('tail',                'pelvis', 'pubis'),
    ('hipside.L',           'pubis', 'l-hipside'),
    ('hip.L',               'pelvis', 'l-hip'),
    ('hipside.R',           'pubis', 'r-hipside'),
    ('hip.R',               'pelvis', 'r-hip'),
    ('gluteus.L',           'l-upperleg', 'l-gluteus'),
    ('gluteus.R',           'r-upperleg', 'r-gluteus'),
    
    ('quadriceps.L',        'l-quadriceps', 'l-hipside'),
    ('quadriceps.R',        'r-quadriceps', 'r-hipside'),
    ('femoris.L',           'l-fem-1', 'l-fem-2'),
    ('femoris.R',           'r-fem-1', 'r-fem-2'),
    ('trg_knee.L',          'l-knee-1', 'l-knee-2'),
    ('trg_knee.R',          'r-knee-1', 'r-knee-2'),
    ('soleus.L',            'l-soleus-1', 'l-soleus-2'),
    ('soleus.R',            'r-soleus-1', 'r-soleus-2'),
    ('sole.L',              'l-foot-1', 'l-heel'),
    ('sole.R',              'r-foot-1', 'r-heel'),
]


Armature = OrderedDict([
    ('ribcage.L',           (0, 'chest', F_DEF, L_MSCL, NoBB)),
    ('pectoralis.L',        (173*D, 'ribcage.L', F_DEF+F_CON, L_MSCL, NoBB)),
    ('platysma.L',          (-153*D, 'neck', F_DEF, L_MSCL, NoBB)),
    ('trapezius.L',         (176*D, 'chest', F_DEF+F_CON, L_MSCL, NoBB)),
    ('trap_goal.L',         (0, 'shoulder.L', F_CON, L_MSCL, NoBB)),
    ('lat_dorsi.L',         (74*D, 'chest', F_DEF, L_MSCL, NoBB)),
    ('deltoid.L',           (0, 'shoulder.L', F_CON+F_DEF, L_MSCL, NoBB)),
    ('scapula.L',           (-24*D, 'shoulder.L', F_DEF, L_MSCL, NoBB)),

    ('ribcage.R',           (0, 'chest', F_DEF, L_MSCL, NoBB)),
    ('pectoralis.R',        (-173*D, 'ribcage.R', F_DEF+F_CON, L_MSCL, NoBB)),
    ('platysma.R',          (153*D, 'neck', F_DEF, L_MSCL, NoBB)),
    ('trapezius.R',         (-176*D, 'chest', F_DEF+F_CON, L_MSCL, NoBB)),
    ('trap_goal.R',         (0, 'shoulder.R', F_CON, L_MSCL, NoBB)),
    ('lat_dorsi.R',         (-74*D, 'chest', F_DEF, L_MSCL, NoBB)),
    ('deltoid.R',           (0, 'shoulder.R', F_CON+F_DEF, L_MSCL, NoBB)),
    ('scapula.R',           (24*D, 'shoulder.R', F_DEF, L_MSCL, NoBB)),

    ('biceps.L',            (91*D, 'upper_arm.L', F_DEF, L_MSCL, NoBB)),
    ('triceps.L',           (-101*D, 'upper_arm.L', F_DEF, L_MSCL, NoBB)),
    ('trg_elbow.L',         (-105*D, 'upper_arm.L', F_DEF+F_CON, L_MSCL, NoBB)),
    ('pronator.L',          (10*D, 'trg_elbow.L', F_DEF+F_CON, L_MSCL, NoBB)),
    ('brachioradialis.L',   (74*D, 'forearm.L', F_DEF, L_MSCL, NoBB)),
    ('forearmhook.L',       (0, 'hand.L',0, L_MSCL, NoBB)),
    
    ('biceps.R',            (-91*D, 'upper_arm.R', F_DEF, L_MSCL, NoBB)),
    ('triceps.R',           (101*D, 'upper_arm.R', F_DEF, L_MSCL, NoBB)),
    ('trg_elbow.R',         (105*D, 'upper_arm.R', F_DEF+F_CON, L_MSCL, NoBB)),
    ('pronator.R',          (-10*D, 'trg_elbow.R', F_DEF+F_CON, L_MSCL, NoBB)),
    ('brachioradialis.R',   (-74*D, 'forearm.R', F_DEF, L_MSCL, NoBB)),
    ('forearmhook.R',       (0, 'hand.R',0, L_MSCL, NoBB)),
    
    ('tail',                (0, 'hips', F_DEF, L_MSCL, NoBB)),
    ('hipside.L',           (0, 'tail', F_DEF+F_CON, L_MSCL, NoBB)),
    ('hip.L',               (0, 'tail', F_DEF, L_MSCL, NoBB)),
    ('gluteus.L',           (0, 'hips', F_DEF, L_MSCL, NoBB)),
    ('hipside.R',           (0, 'tail', F_DEF+F_CON, L_MSCL, NoBB)),
    ('hip.R',               (0, 'tail', F_DEF, L_MSCL, NoBB)),
    ('gluteus.R',           (0, 'hips', F_DEF, L_MSCL, NoBB)),
    
    ('quadriceps.L',        (-8*D, 'thigh.L', F_DEF, L_MSCL, NoBB)),
    ('femoris.L',           (-177*D, 'thigh.L', F_DEF, L_MSCL, NoBB)),
    ('trg_knee.L',          (-179*D, 'thigh.L', F_DEF, L_MSCL, NoBB)),
    ('soleus.L',            (168*D, 'shin.L', F_DEF, L_MSCL, NoBB)),
    ('sole.L',              (0, 'foot.L', 0, L_MSCL, NoBB)),

    ('quadriceps.R',        (8*D, 'thigh.R', F_DEF, L_MSCL, NoBB)),
    ('femoris.R',           (177*D, 'thigh.R', F_DEF, L_MSCL, NoBB)),
    ('trg_knee.R',          (179*D, 'thigh.R', F_DEF, L_MSCL, NoBB)),
    ('soleus.R',            (-168*D  , 'shin.R', F_DEF, L_MSCL, NoBB)),
    ('sole.R',              (0, 'foot.R', 0, L_MSCL, NoBB)),

])

CustomShapes = {}

RotationLimits = {}

Constraints = {
    'pectoralis.L' : [
        ('StretchTo', C_VOLXZ, 1, 
            ['Stretch_To', 'shoulder.L', 1, 1, ('l-pect-1', 'l-scapula')])
        ],

    'platysma.L' : [
        ('StretchTo', C_VOLXZ, 1, 
            ['Stretch_To', 'shoulder.L', 0, 1, ('l-plat-1', 'l-clavicle')])
        ],

    'trapezius.L' : [
        ('StretchTo', C_VOLZ, 1, 
            ['Stretch_To', 'trap_goal.L', 1, 1])
        ],

    'scapula.L' : [
        ('TrackTo', C_LOCAL, 1, 
            ['Track_To', 'chest', 1, 'TRACK_Y', 'UP_Z', False])
        ],

    'lat_dorsi.L' : [
        ('StretchTo', C_VOLXZ, 1, 
            ['Stretch_To', 'shoulder.L', 1, 1, ('spine-2', 'l-scapula')])
        ],

    'deltoid.L' : [
        ('StretchTo', C_VOLXZ, 1, 
            ['Stretch_To', 'upper_arm.L', 0, 1, ('l-scapula', 'l-shoulder')])
        ],

    'biceps.L' : [
        ('Transform', C_LOCAL, 1, 
            ['Transform', 'forearm.L', 
                'ROTATION', (0,0,0), (90,0,0), 
                ('X','X','X'),
                'SCALE', (1,1,1), (1.3,1.4,1.3)])
        ],

    'triceps.L' : [
        ('Transform', C_LOCAL, 1, 
            ['Transform', 'forearm.L', 
                'ROTATION', (0,0,0), (90,0,0), 
                ('X','X','X'),
                'SCALE', (1,1,1), (1.3,0.8,1.3)])
        ],

    'trg_elbow.L' : [
        ('Transform', C_LOCAL, 1, 
            ['Transform', 'forearm.L', 
                'ROTATION', (0,0,0), (90,0,0), 
                ('X','X','X'),
                'ROTATION', (0,0,0), (29,0,0)])
        ],

    'pronator.L' : [
        ('StretchTo', C_VOLXZ, 1, 
            ['Stretch_To', 'forearmhook.L', 0, 1, ('l-brac-1', 'l-brac-3')])
        ],

    'brachioradialis.L' : [
        ('StretchTo', C_VOLXZ, 1, 
            ['Stretch_To', 'forearmhook.L', 1, 1])
        ],

    'quadriceps.L' : [
        ('StretchTo', C_VOLXZ, 1, 
            ['Stretch_To', 'hipside.L', 1, 5, ('l-quadriceps', 'l-hipside')])
        ],

    'femoris.L' : [
        ('StretchTo', C_VOLXZ, 1, 
            ['Stretch_To', 'shin.L', FemorisGoal, 1, ('l-fem-1', 'l-fem-3')])
        ],

    'trg_knee.L' : [
        ('Transform', C_LOCAL, 1, 
            ['Transform', 'shin.L', 
                'ROTATION', (0,0,0), (90,0,0), 
                ('X','X','X'),
                'SCALE', (1,1,1), (1.3,1.4,1.3)])
        ],

    'soleus.L' : [
        ('StretchTo', C_VOLX, 1, 
            ['Stretch_To', 'sole.L', 1, 1, ('l-soleus-1', 'l-heel')])
        ],
}
