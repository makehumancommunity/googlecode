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

MHX bone definitions 
"""

from .flags import *
from . import posebone
from posebone import addPoseBone


Joints = [
    ('l-heel0',             'v', 12815),
    ('l-heel',              'l', ((-2.5,'l-foot-2'), (3.5,'l-foot-1'))),
    ('r-heel0',             'v', 6218),
    ('r-heel',              'l', ((-2.5,'r-foot-2'), (3.5,'r-foot-1'))),

    ('l-ankle-tip',         'o', ('l-ankle', (0,0,-1))),
    ('r-ankle-tip',         'o', ('r-ankle', (0,0,-1))),
    
    ('l-knee-pt',           'o', ('l-knee', [0,0,3])),
    ('r-knee-pt',           'o', ('r-knee', [0,0,3])),
    ('l-elbow-pt',          'o', ('l-elbow', [0,0,-3])),
    ('r-elbow-pt',          'o', ('r-elbow', [0,0,-3])),
]

HeadsTails = {
    # Leg
    
    'hip.L' :      ('l-upper-leg', ('l-upper-leg', ysmall)),
    'hip.R' :      ('r-upper-leg', ('r-upper-leg', ysmall)),
    
    'ankle.L' :         ('l-ankle', 'l-ankle-tip'),
    'ankle.ik.L' :      ('l-ankle', 'l-ankle-tip'),
    'leg.ik.L' :        ('l-heel', 'l-foot-2'),
    'toe.rev.L' :       ('l-foot-2', 'l-foot-1'),
    'foot.rev.L' :      ('l-foot-1', 'l-ankle'),

    'ankle.R' :         ('r-ankle', 'r-ankle-tip'),
    'ankle.ik.R' :      ('r-ankle', 'r-ankle-tip'),
    'leg.ik.R' :        ('r-heel', 'r-foot-2'),
    'toe.rev.R' :       ('r-foot-2', 'r-foot-1'),
    'foot.rev.R' :      ('r-foot-1', 'r-ankle'),

    # Pole Targets
    'knee.pt.ik.L' :    ('l-knee-pt', ('l-knee-pt', ysmall)),
    'knee.pt.fk.L' :    ('l-knee-pt', ('l-knee-pt', ysmall)),
    'knee.link.L' :     ('l-knee', 'l-knee-pt'),
    'FootPT.L' :        (('l-midfoot', (0,1,0.2)), ('l-midfoot', (0,1.3,0.2))),
    'ToePT.L' :         (('l-midtoe', (0,1,0)), ('l-midtoe', (0,1.3,0))),
    
    'knee.pt.ik.R' :    ('r-knee-pt', ('r-knee-pt', ysmall)),
    'knee.pt.fk.R' :    ('r-knee-pt', ('r-knee-pt', ysmall)),
    'knee.link.R' :     ('r-knee', 'r-knee-pt'),
    'FootPT.R' :        (('r-midfoot', (0,1,0.2)), ('r-midfoot', (0,1.3,0.2))),
    'ToePT.R' :         (('r-midtoe', (0,1,0)), ('r-midtoe', (0,1.3,0))),
    
    # Arm

    'arm_root.L' :      ('l-shoulder', ('l-shoulder', ysmall)),
    'arm_socket.L' :    ('l-shoulder', ('l-shoulder', ysmall)),
    'arm_hinge.L' :     ('l-shoulder', ('l-shoulder', ysmall)),

    'arm_root.R' :      ('r-shoulder', ('r-shoulder', ysmall)),
    'arm_socket.R' :    ('r-shoulder', ('r-shoulder', ysmall)),
    'arm_hinge.R' :     ('r-shoulder', ('r-shoulder', ysmall)),
    
    'wrist.ik.L' :      ('l-hand', 'l-hand-end'),
    'elbow.pt.ik.L' :   ('l-elbow-pt', ('l-elbow-pt', ysmall)),
    'elbow.pt.fk.L' :   ('l-elbow-pt', ('l-elbow-pt', ysmall)),
    'elbow.link.L' :    ('l-elbow', 'l-elbow-pt'),

    'wrist.ik.R' :      ('r-hand', 'r-hand-end'),
    'elbow.pt.ik.R' :   ('r-elbow-pt', ('r-elbow-pt', ysmall)),
    'elbow.pt.fk.R' :   ('r-elbow-pt', ('r-elbow-pt', ysmall)),
    'elbow.link.R' :    ('r-elbow', 'r-elbow-pt'),
}

"""
    # Directions    
    ('DirUpLegFwd.L' :    ('l-upper-leg', ('l-upper-leg', (0,0,1))),
    ('DirUpLegFwd.R' :    ('r-upper-leg', ('r-upper-leg', (0,0,1))),
    ('DirUpLegBack.L' :   ('l-upper-leg', ('l-upper-leg', (0,0,-1))),
    ('DirUpLegBack.R' :   ('r-upper-leg', ('r-upper-leg', (0,0,-1))),
    ('DirUpLegOut.L' :    ('l-upper-leg', ('l-upper-leg', (1,0,0))),
    ('DirUpLegOut.R' :    ('r-upper-leg', ('r-upper-leg', (-1,0,0))),

    ('DirKneeBack.L' :    ('l-knee', ('l-knee', (0,0,-1))),
    ('DirKneeBack.R' :    ('r-knee', ('r-knee', (0,0,-1))),
    ('DirKneeInv.L' :     ('l-knee', ('l-knee', (0,1,0))),
    ('DirKneeInv.R' :     ('r-knee', ('r-knee', (0,1,0))),
"""


Armature = {
    
    # Leg
    
    'hip.L' :          (0, 'hips', F_WIR, L_TWEAK),
    'leg.ik.L' :       (0, None, F_WIR, L_LLEGIK),
    'toe.rev.L' :      (0, 'leg.ik.L', F_WIR, L_LLEGIK),
    'foot.rev.L' :     (0, 'toe.rev.L', F_WIR, L_LLEGIK),
    'ankle.L' :        (0, None, F_WIR, L_LEXTRA),
    'ankle.ik.L' :     (0, 'foot.rev.L', 0, L_HELP2),

    'hip.R' :          (0, 'hips', F_WIR, L_TWEAK),
    'leg.ik.R' :       (0, None, F_WIR, L_RLEGIK),
    'toe.rev.R' :      (0, 'leg.ik.R', F_WIR, L_RLEGIK),
    'foot.rev.R' :     (0, 'toe.rev.R', F_WIR, L_RLEGIK),
    'ankle.R' :        (0, None, F_WIR, L_REXTRA),
    'ankle.ik.R' :     (0, 'foot.rev.R', 0, L_HELP2),

    'knee.pt.ik.L' :   (0, 'foot.rev.L', F_WIR, L_LLEGIK+L_LEXTRA),
    'knee.pt.fk.L' :   (0, 'thigh.L', 0, L_HELP2),
    'knee.link.L' :    (0, 'thigh.ik.L', F_RES, L_LLEGIK+L_LEXTRA),

    'knee.pt.ik.R' :   (0, 'foot.rev.R', F_WIR, L_RLEGIK+L_REXTRA),
    'knee.pt.fk.R' :   (0, 'thigh.R', 0, L_HELP2),
    'knee.link.R' :    (0, 'thigh.ik.R', F_RES, L_RLEGIK+L_REXTRA),

    # Arm
    
    'arm_root.L' :     (0, 'shoulder.L', F_WIR, L_TWEAK),
    'arm_root.R' :     (0, 'shoulder.R', F_WIR, L_TWEAK),
    'arm_socket.L' :   (0, 'hips', 0, L_HELP),
    'arm_socket.R' :   (0, 'hips', 0, L_HELP),
    'arm_hinge.L' :    (0, 'arm_socket.L', 0, L_HELP),
    'arm_hinge.R' :    (0, 'arm_socket.R', 0, L_HELP),

    'wrist.ik.L' :     (0, None, F_WIR, L_LARMIK),
    'elbow.pt.ik.L' :  (0, 'shoulder.L', F_WIR, L_LARMIK+L_LEXTRA),
    'elbow.pt.fk.L' :  (0, 'upper_arm.L', 0, L_HELP2),
    'elbow.link.L' :   (0, 'upper_arm.ik.L', F_RES, L_LARMIK+L_LEXTRA),

    'wrist.ik.R' :     (0, None, F_WIR, L_RARMIK),
    'elbow.pt.ik.R' :  (0, 'shoulder.R', F_WIR, L_RARMIK+L_REXTRA),
    'elbow.pt.fk.R' :  (0, 'upper_arm.R', 0, L_HELP2),
    'elbow.link.R' :   (0, 'upper_arm.ik.R', F_RES, L_RARMIK+L_REXTRA),
}

"""

    # Directions
    ('DirUpLegFwd.L',       180*D, 'hip.L', 0, L_HELP),
    ('DirUpLegFwd.R',       180*D, 'hip.R', 0, L_HELP),
    ('DirUpLegBack.L',      0*D, 'hip.L', 0, L_HELP),
    ('DirUpLegBack.R',      0*D, 'hip.R', 0, L_HELP),
    ('DirUpLegOut.L',       -90*D, 'hip.L', 0, L_HELP), 
    ('DirUpLegOut.R',       90*D, 'hip.R', 0, L_HELP),

    ('DirKneeBack.L',       0*D, 'thigh.L', 0, L_HELP),
    ('DirKneeBack.R',       0*D, 'thigh.R', 0, L_HELP),
    ('DirKneeInv.L',        0*D, 'thigh.L', 0, L_HELP),
    ('DirKneeInv.R',        0*D, 'thigh.R', 0, L_HELP),
"""

Parents = {
    'upper_arm.L' :     'arm_hinge.L',
    'upper_arm.R' :     'arm_hinge.R',
    'thigh.L' :         'hip.L',
    'thigh.R' :         'hip.R',    
}


RotationLimits = {
    # Leg
    
    'foot.rev.L' :   (-20*D,60*D, 0,0, 0,0),
    'foot.rev.R' :   (-20*D,60*D, 0,0, 0,0),
    'toe.rev.L' :    (-10*D,45*D, 0,0, 0,0),
    'toe.rev.R' :    (-10*D,45*D, 0,0, 0,0),
}

CustomShapes = {
    # Leg
    
    'hip.L' :           'GZM_Ball025',
    'hip.R' :           'GZM_Ball025',
    'foot.rev.L' :      'GZM_RevFoot',
    'foot.rev.R' :      'GZM_RevFoot',
    'toe.rev.L' :       'GZM_RevToe',
    'toe.rev.R' :       'GZM_RevToe',
    'ankle.L' :         'GZM_Ball025',
    'ankle.R' :         'GZM_Ball025',
    'knee.pt.ik.L' :    'GZM_Cube025',
    'knee.pt.ik.R' :    'GZM_Cube025',

    # Arm
    
    'arm_root.L' :      'GZM_Ball025',
    'arm_root.R' :      'GZM_Ball025',
    'wrist.L' :         'GZM_Ball025',
    'wrist.R' :         'GZM_Ball025',
    'elbow.pt.ik.L' :   'GZM_Cube025',
    'elbow.pt.ik.R' :   'GZM_Cube025',
}

IkChains = {
    "upper_arm" :   (L_LARMIK, "Arm"),
    "forearm" :     (2, L_LARMIK, "Arm", "wrist", "elbow.pt", 175*D, 5*D),
    "thigh" :       (L_LLEGIK, "Leg"),
    "shin" :        (2, L_LLEGIK, "Leg", "ankle", "knee.pt", -112*D, -68*D),
}        

Hint = 18*D

Constraints = {
    #Leg
    
    'shin.ik.L' :   [
        ('LimitRot', C_OW_LOCAL, 1, ['Hint', (Hint,Hint, 0,0, 0,0), (1,0,0)])
        ],
    'shin.ik.R' :   [
        ('LimitRot', C_OW_LOCAL, 1, ['Hint', (Hint,Hint, 0,0, 0,0), (1,0,0)])
        ],        
    'foot.L' : [
         ('IK', 0, 0, ['RevIK', 'foot.rev.L', 1, None, (1,0,1)]),
         ('IK', 0, 0, ['FreeIK', None, 2, None, (True, False,True)])
        ],    
    'foot.R' : [
         ('IK', 0, 0, ['RevIK', 'foot.rev.R', 1, None, (1,0,1)]),
         ('IK', 0, 0, ['FreeIK', None, 2, None, (True, False,True)])
        ],    
    'toe.L' : [
         ('IK', 0, 0, ['RevIK', 'toe.rev.L', 1, None, (1,0,1)]),
        ],
    'toe.R' : [
         ('IK', 0, 0, ['RevIK', 'toe.rev.R', 1, None, (1,0,1)]),
        ],
    'ankle.ik.L' : [
         ('CopyLoc', 0, 1, ['Foot', 'foot.rev.L', (1,1,1), (0,0,0), 1, False]),
         ('CopyLoc', 0, 0, ['Ankle', 'ankle.L', (1,1,1), (0,0,0), 0, False]) 
        ],
    'ankle.ik.R' :  [
         ('CopyLoc', 0, 1, ['Foot', 'foot.rev.R', (1,1,1), (0,0,0), 1, False]),
         ('CopyLoc', 0, 0, ['Ankle', 'ankle.R', (1,1,1), (0,0,0), 0, False]) 
        ],
    'knee.link.L' : [
         ('StretchTo', 0, 1, ['Stretch', 'knee.pt.ik.L', 0, 1, 3.0])
        ],
    'knee.link.R' : [
         ('StretchTo', 0, 1, ['Stretch', 'knee.pt.ik.R', 0, 1, 3.0])
        ],

    #Arm
    
    'arm_socket.L' : [
        ('CopyLoc', 0, 1, ['Location', 'arm_root.L', (1,1,1), (0,0,0), 0, False]),
        ('CopyTrans', 0, 0, ['Hinge', 'arm_root.L', 0])
        ],        
    'arm_socket.R' : [
        ('CopyLoc', 0, 1, ['Location', 'arm_root.R', (1,1,1), (0,0,0), 0, False]),
        ('CopyTrans', 0, 0, ['Hinge', 'arm_root.R', 0])
        ],        
    'forearm.ik.L' :   [
        ('LimitRot', C_OW_LOCAL, 1, ['Hint', (Hint,Hint, 0,0, 0,0), (1,0,0)])
        ],
    'forearm.ik.R' :   [
        ('LimitRot', C_OW_LOCAL, 1, ['Hint', (Hint,Hint, 0,0, 0,0), (1,0,0)])
        ],     
    'hand.L' : [
         ('IK', 0, 0, ['FreeIK', None, 2, None, (True, False,False)]),
         ('CopyLoc', 0, 0, ['WristLoc', 'wrist.ik.L', (1,1,1), (0,0,0), 0, False]),
         ('CopyRot', 0, 0, ['WristRot', 'wrist.ik.L', (1,1,1), (0,0,0), False])
        ],
    'hand.R' : [
         ('IK', 0, 0, ['FreeIK', None, 2, None, (True, False,False)]),
         ('CopyLoc', 0, 0, ['WristLoc', 'wrist.ik.R', (1,1,1), (0,0,0), 0, False]),
         ('CopyRot', 0, 0, ['WristRot', 'wrist.ik.R', (1,1,1), (0,0,0), False])
        ],        
    'elbow.link.L' : [
        ('StretchTo', 0, 1, ['Stretch', 'elbow.pt.ik.L', 0, 1, 3.0])
        ],
    'elbow.link.R' : [
        ('StretchTo', 0, 1, ['Stretch', 'elbow.pt.ik.R', 0, 1, 3.0])
        ],

}


#
#   PropLRDrivers
#   (Bone, Name, Props, Expr)
#

PropLRDrivers = [
    ('thigh', 'LegIK', ['LegIk'], 'x1'),
    ('thigh', 'LegFK', ['LegIk'], '1-x1'),
    ('shin', 'LegIK', ['LegIk'], 'x1'),
    ('shin', 'LegFK', ['LegIk'], '1-x1'),
    ('foot', 'RevIK', ['LegIk', 'LegIkToAnkle'], 'x1*(1-x2)'),
    #('foot', 'FreeIK', ['LegIk'], '1-x1'),
    ('toe', 'RevIK', ['LegIk', 'LegIkToAnkle'], 'x1*(1-x2)'),
    ('ankle.ik', 'Foot', ['LegIkToAnkle'], '1-x1'),
    ('ankle.ik', 'Ankle', ['LegIkToAnkle'], 'x1'),
    
    #('shoulder', 'Elbow', ['ElbowPlant'], 'x1'),
    ('arm_socket', 'Hinge', ['ArmHinge'], '1-x1'),
    ('upper_arm', 'ArmIK', ['ArmIk', 'ElbowPlant'], 'x1*(1-x2)'),
    ('upper_arm', 'ArmFK', ['ArmIk', 'ElbowPlant'], '1-x1*(1-x2)'),
    #('upper_arm', 'Elbow', ['ElbowPlant'], 'x1'),
    ('forearm', 'ArmIK', ['ArmIk', 'ElbowPlant'], 'x1*(1-x2)'),
    ('forearm', 'ArmFK', ['ArmIk', 'ElbowPlant'], '1-x1*(1-x2)'),
    #('forearm', 'Wrist', ['ArmIk', 'ElbowPlant'], 'x1*x2'),
    #('hand', 'FreeIK', ['ArmIk', 'ElbowPlant'], '(1-x1)*(1-x2)'),
    #('hand', 'WristLoc', ['ArmIk'], 'x1'),
    ('hand', 'WristRot', ['ArmIk', 'HandFollowsWrist'], 'x1*x2'),
    #('HlpLoArm', 'WristRot', ['ArmIk', 'HandFollowsWrist'], 'x1*x2'),
    
]

SoftPropLRDrivers = [
    # Leg
    
    #('KneePT', 'Foot', ['KneeFollowsFoot'], 'x1'),
    #('KneePT', 'Hip', ['KneeFollowsHip', 'KneeFollowsFoot'], 'x1*(1-x2)'),  
    
    # Arm
    
    #('ElbowPT', 'Hand', ['ElbowFollowsWrist'], 'x1'),
    #('ElbowPT', 'Shoulder', ['ElbowFollowsWrist'], '(1-x1)'),
    
]

PropDrivers = [
    # Leg
    ('thigh.L', 'LimitRot', ['RotationLimits', 'LegIk.L'], 'x1*(1-x2)'),
    ('shin.L', 'LimitRot', ['RotationLimits', 'LegIk.L'], 'x1*(1-x2)'),    
    ('foot.L', 'LimitRot', ['RotationLimits', 'LegIk.L'], 'x1*(1-x2)'),    

    ('thigh.R', 'LimitRot', ['RotationLimits', 'LegIk.R'], 'x1*(1-x2)'),
    ('shin.R', 'LimitRot', ['RotationLimits', 'LegIk.R'], 'x1*(1-x2)'),    
    ('foot.R', 'LimitRot', ['RotationLimits', 'LegIk.R'], 'x1*(1-x2)'),   

    #Arm    
    ('upper_arm.L', 'LimitRot', ['RotationLimits', 'ArmIk.L'], 'x1*(1-x2)'),
    #('LoArm.L', 'LimitRot', ['RotationLimits', 'ArmIk.L'], 'x1*(1-x2)'),    
    ('hand.L', 'LimitRot', ['RotationLimits', 'ArmIk.L', 'HandFollowsWrist.L'], 'x1*(1-x2*x3)'),

    ('upper_arm.R', 'LimitRot', ['RotationLimits', 'ArmIk.R'], 'x1*(1-x2)'),
    #('LoArm.R', 'LimitRot', ['RotationLimits', 'ArmIk.R'], 'x1*(1-x2)'),    
    ('hand.R', 'LimitRot', ['RotationLimits', 'ArmIk.R', 'HandFollowsWrist.R'], 'x1*(1-x2*x3)'),
    
]

#
#   DeformDrivers
#   Bone : (constraint, driver, rotdiff, keypoints)
#

DeformDrivers = []

#
#   ShapeDrivers
#   Shape : (driver, rotdiff, keypoints)
#

ShapeDrivers = {
}

expr90 = "%.3f*(1-%.3f*x1)" % (90.0/90.0, 2/pi)
expr70 = "%.3f*(1-%.3f*x1)" % (90.0/70.0, 2/pi)
expr60 = "%.3f*(1-%.3f*x1)" % (90.0/60.0, 2/pi)
expr45 = "%.3f*(1-%.3f*x1)" % (90.0/45.0, 2/pi)
expr90_90 = "%.3f*max(1-%.3f*x1,0)*max(1-%.3f*x2,0)" % (90.0/90.0, 2/pi, 2/pi)


HipTargetDrivers = []
"""
    ("legs-forward-90", "LR", expr90,
        [("UpLegVec", "DirUpLegFwd")]),
    ("legs-back-60", "LR", expr60,
        [("UpLegVec", "DirUpLegBack")]),
    ("legs-out-90", "LR", expr90_90,
        [("UpLegVec", "DirUpLegOut"),
         ("UpLeg", "UpLegVec")]),
    ("legs-out-90-neg-90", "LR", expr90_90,
        [("UpLegVec", "DirUpLegOut"),
         ("UpLeg", "UpLegVecNeg")]),
]
"""
KneeTargetDrivers = [
#    ("lolegs-back-90", "LR", expr90,
#        [("LoLeg", "DirKneeBack")]),
#    ("lolegs-back-135", "LR", expr45,
#        [("LoLeg", "DirKneeInv")]),
]


