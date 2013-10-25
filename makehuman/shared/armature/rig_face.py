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

Face bone definitions
"""

from .flags import *

Joints = [
    ('head-end',        'l', ((2.0, 'head'), (-1.0, 'neck'))),

    ('m-uplip-0',       'v', 467),
    ('l-uplip-1',       'v', 7255),
    ('r-uplip-1',       'v', 506),
    ('l-uplip-2',       'v', 7253),
    ('r-uplip-2',       'v', 504),

    ('m-lolip-0',       'v', 495),
    ('l-lolip-1',       'vl', ((0.4, 7238), (0.6, 7244))),
    ('r-lolip-1',       'vl', ((0.4, 483), (0.6, 489))),
    ('l-lolip-2',       'vl', ((0.1, 7238), (0.9, 7232))),
    ('r-lolip-2',       'vl', ((0.1, 483), (0.9, 477))),

    ('l-lip-3',        'v', 7249),
    ('r-lip-3',        'v', 500),

    ('l-mouthside-1',   'v', 11770),
    ('r-mouthside-1',   'v', 5156),
    ('l-mouthside-2',   'vl', ((0.5, 11904), (0.5, 11905))),
    ('r-mouthside-2',   'vl', ((0.5, 5299), (0.5, 5300))),

    ('l-noseside-1',    'v', 11673),
    ('r-noseside-1',    'v', 5056),
    ('l-noseside-2',    'v', 11764),
    ('r-noseside-2',    'v', 5150),

    ('l-loeye-1',       'v', 6920),
    ('r-loeye-1',       'v', 142),
    ('l-loeye-2',       'v', 6917),
    ('r-loeye-2',       'v', 139),
    ('l-loeye-3',       'v', 11714),
    ('r-loeye-3',       'v', 5099),

    ('l-brow-1',        'vl', ((0.5, 6957), (0.5, 6983))),
    ('r-brow-1',        'vl', ((0.5, 181), (0.5, 208))),
    ('l-brow-2',        'v', 6979),
    ('r-brow-2',        'v', 204),
    ('l-brow-3',        'v', 6982),
    ('r-brow-3',        'v', 207),
]

eyeOffs = (0,0,0.3)
posOffs = (0,0,0.0)
negOffs = (0,0,-0.07)

HeadsTails = {
    'jaw' :             ('mouth', 'jaw'),
    'tongue_base' :     ('tongue-1', 'tongue-2'),
    'tongue_mid' :      ('tongue-2', 'tongue-3'),
    'tongue_tip' :      ('tongue-3', 'tongue-4'),

    'eye.R' :           ('r-eye', ('r-eye', eyeOffs)),
    'eye_parent.R' :    ('r-eye', ('r-eye', eyeOffs)),
    'uplid.R' :         ('r-eye', 'r-upperlid'),
    'lolid.R' :         ('r-eye', 'r-lowerlid'),

    'eye.L' :           ('l-eye', ('l-eye', eyeOffs)),
    'eye_parent.L' :    ('l-eye', ('l-eye', eyeOffs)),
    'uplid.L' :         ('l-eye', 'l-upperlid'),
    'lolid.L' :         ('l-eye', 'l-lowerlid'),

    'uplip_mid' :       (('m-uplip-0', posOffs), ('m-uplip-0', negOffs)),
    'uplip_1.L' :       (('l-uplip-1', posOffs), ('l-uplip-1', negOffs)),
    'uplip_1.R' :       (('r-uplip-1', posOffs), ('r-uplip-1', negOffs)),
    'uplip_2.L' :       (('l-uplip-2', posOffs), ('l-uplip-2', negOffs)),
    'uplip_2.R' :       (('r-uplip-2', posOffs), ('r-uplip-2', negOffs)),

    'lolip_mid' :       (('m-lolip-0', posOffs), ('m-lolip-0', negOffs)),
    'lolip_1.L' :       (('l-lolip-1', posOffs), ('l-lolip-1', negOffs)),
    'lolip_1.R' :       (('r-lolip-1', posOffs), ('r-lolip-1', negOffs)),
    'lolip_2.L' :       (('l-lolip-2', posOffs), ('l-lolip-2', negOffs)),
    'lolip_2.R' :       (('r-lolip-2', posOffs), ('r-lolip-2', negOffs)),

    'lip_3.L' :         (('l-lip-3', posOffs), ('l-lip-3', negOffs)),
    'lip_3.R' :         (('r-lip-3', posOffs), ('r-lip-3', negOffs)),
    'lip_3_jaw.L' :     (('l-lip-3', posOffs), ('l-lip-3', negOffs)),
    'lip_3_jaw.R' :     (('r-lip-3', posOffs), ('r-lip-3', negOffs)),
    'lip_3_parent.L' :  (('l-lip-3', posOffs), ('l-lip-3', negOffs)),
    'lip_3_parent.R' :  (('r-lip-3', posOffs), ('r-lip-3', negOffs)),

    'mouthside_1.L' :       (('l-mouthside-1', posOffs), ('l-mouthside-1', negOffs)),
    'mouthside_1.R' :       (('r-mouthside-1', posOffs), ('r-mouthside-1', negOffs)),
    'mouthside_1_jaw.L' :   (('l-mouthside-1', posOffs), ('l-mouthside-1', negOffs)),
    'mouthside_1_jaw.R' :   (('r-mouthside-1', posOffs), ('r-mouthside-1', negOffs)),
    'mouthside_1_parent.L' :(('l-mouthside-1', posOffs), ('l-mouthside-1', negOffs)),
    'mouthside_1_parent.R' :(('r-mouthside-1', posOffs), ('r-mouthside-1', negOffs)),

    'mouthside_2.L' :       (('l-mouthside-2', posOffs), ('l-mouthside-2', negOffs)),
    'mouthside_2.R' :       (('r-mouthside-2', posOffs), ('r-mouthside-2', negOffs)),
    'mouthside_2_jaw.L' :   (('l-mouthside-2', posOffs), ('l-mouthside-2', negOffs)),
    'mouthside_2_jaw.R' :   (('r-mouthside-2', posOffs), ('r-mouthside-2', negOffs)),
    'mouthside_2_parent.L' :(('l-mouthside-2', posOffs), ('l-mouthside-2', negOffs)),
    'mouthside_2_parent.R' :(('r-mouthside-2', posOffs), ('r-mouthside-2', negOffs)),

    'noseside_1.L' :    (('l-noseside-1', posOffs), ('l-noseside-1', negOffs)),
    'noseside_1.R' :    (('r-noseside-1', posOffs), ('r-noseside-1', negOffs)),
    'noseside_2.L' :    (('l-noseside-2', posOffs), ('l-noseside-2', negOffs)),
    'noseside_2.R' :    (('r-noseside-2', posOffs), ('r-noseside-2', negOffs)),

    'loeye_1.L' :       (('l-loeye-1', posOffs), ('l-loeye-1', negOffs)),
    'loeye_1.R' :       (('r-loeye-1', posOffs), ('r-loeye-1', negOffs)),
    'loeye_2.L' :       (('l-loeye-2', posOffs), ('l-loeye-2', negOffs)),
    'loeye_2.R' :       (('r-loeye-2', posOffs), ('r-loeye-2', negOffs)),
    'loeye_3.L' :       (('l-loeye-3', posOffs), ('l-loeye-3', negOffs)),
    'loeye_3.R' :       (('r-loeye-3', posOffs), ('r-loeye-3', negOffs)),

    'brow_1.L' :       (('l-brow-1', posOffs), ('l-brow-1', negOffs)),
    'brow_1.R' :       (('r-brow-1', posOffs), ('r-brow-1', negOffs)),
    'brow_2.L' :       (('l-brow-2', posOffs), ('l-brow-2', negOffs)),
    'brow_2.R' :       (('r-brow-2', posOffs), ('r-brow-2', negOffs)),
    'brow_3.L' :       (('l-brow-3', posOffs), ('l-brow-3', negOffs)),
    'brow_3.R' :       (('r-brow-3', posOffs), ('r-brow-3', negOffs)),
}

fflags = F_DEF|F_WIR|F_NOLOCK

Armature = {
    'jaw' :             (0, 'head', F_DEF|F_NOLOCK, L_HEAD),
    'tongue_base' :     (0, 'jaw', F_DEF, L_HEAD),
    'tongue_mid' :      (0, 'tongue_base', F_DEF, L_HEAD),
    'tongue_tip' :      (0, 'tongue_mid', F_DEF, L_HEAD),
    'eye.R' :           (0, 'head', F_DEF, L_HEAD),
    'eye.L' :           (0, 'head', F_DEF, L_HEAD),
    'uplid.R' :         (0.279253, 'head', F_DEF, L_HEAD),
    'lolid.R' :         (0, 'head', F_DEF, L_HEAD),
    'uplid.L' :         (-0.279253, 'head', F_DEF, L_HEAD),
    'lolid.L' :         (0, 'head', F_DEF, L_HEAD),

    'uplip_mid' :       (0, 'head', fflags, L_HEAD),
    'uplip_1.L' :       (0, 'head', fflags, L_HEAD),
    'uplip_1.R' :       (0, 'head', fflags, L_HEAD),
    'uplip_2.L' :       (0, 'head', fflags, L_HEAD),
    'uplip_2.R' :       (0, 'head', fflags, L_HEAD),

    'lolip_mid' :       (0, 'jaw', fflags, L_HEAD),
    'lolip_1.L' :       (0, 'jaw', fflags, L_HEAD),
    'lolip_1.R' :       (0, 'jaw', fflags, L_HEAD),
    'lolip_2.L' :       (0, 'jaw', fflags, L_HEAD),
    'lolip_2.R' :       (0, 'jaw', fflags, L_HEAD),

    'lip_3_jaw.L' :     (0, 'jaw', 0, L_HELP),
    'lip_3_jaw.R' :     (0, 'jaw', 0, L_HELP),
    'lip_3_parent.L' :  (0, 'head', 0, L_HELP),
    'lip_3_parent.R' :  (0, 'head', 0, L_HELP),
    'lip_3.L' :         (0, 'lip_3_parent.L', fflags, L_HEAD),
    'lip_3.R' :         (0, 'lip_3_parent.R', fflags, L_HEAD),

    'mouthside_1_jaw.L' :     (0, 'jaw', 0, L_HELP),
    'mouthside_1_jaw.R' :     (0, 'jaw', 0, L_HELP),
    'mouthside_1_parent.L' :  (0, 'head', 0, L_HELP),
    'mouthside_1_parent.R' :  (0, 'head', 0, L_HELP),
    'mouthside_1.L' :         (0, 'mouthside_1_parent.L', fflags, L_HEAD),
    'mouthside_1.R' :         (0, 'mouthside_1_parent.R', fflags, L_HEAD),

    'mouthside_2_jaw.L' :     (0, 'jaw', 0, L_HELP),
    'mouthside_2_jaw.R' :     (0, 'jaw', 0, L_HELP),
    'mouthside_2_parent.L' :  (0, 'head', 0, L_HELP),
    'mouthside_2_parent.R' :  (0, 'head', 0, L_HELP),
    'mouthside_2.L' :         (0, 'mouthside_2_parent.L', fflags, L_HEAD),
    'mouthside_2.R' :         (0, 'mouthside_2_parent.R', fflags, L_HEAD),

    'noseside_1.L' :    (0, 'head', fflags, L_HEAD),
    'noseside_1.R' :    (0, 'head', fflags, L_HEAD),
    'noseside_2.L' :    (0, 'head', fflags, L_HEAD),
    'noseside_2.R' :    (0, 'head', fflags, L_HEAD),

    'loeye_1.L' :       (0, 'head', fflags, L_HEAD),
    'loeye_1.R' :       (0, 'head', fflags, L_HEAD),
    'loeye_2.L' :       (0, 'head', fflags, L_HEAD),
    'loeye_2.R' :       (0, 'head', fflags, L_HEAD),
    'loeye_3.L' :       (0, 'head', fflags, L_HEAD),
    'loeye_3.R' :       (0, 'head', fflags, L_HEAD),

    'brow_1.L' :        (0, 'head', fflags, L_HEAD),
    'brow_1.R' :        (0, 'head', fflags, L_HEAD),
    'brow_2.L' :        (0, 'head', fflags, L_HEAD),
    'brow_2.R' :        (0, 'head', fflags, L_HEAD),
    'brow_3.L' :        (0, 'head', fflags, L_HEAD),
    'brow_3.R' :        (0, 'head', fflags, L_HEAD),
}


CustomShapes = {
    'jaw' :             'GZM_Jaw',
    'eye.R' :           'GZM_Circle025',
    'eye.L' :           'GZM_Circle025',

    'uplip_mid' :       'GZM_Cube025',
    'uplip_1.L' :       'GZM_Cube025',
    'uplip_1.R' :       'GZM_Cube025',
    'uplip_2.L' :       'GZM_Cube025',
    'uplip_2.R' :       'GZM_Cube025',

    'lolip_mid' :       'GZM_Cube025',
    'lolip_1.L' :       'GZM_Cube025',
    'lolip_1.R' :       'GZM_Cube025',
    'lolip_2.L' :       'GZM_Cube025',
    'lolip_2.R' :       'GZM_Cube025',

    'lip_3.L' :         'GZM_Cube025',
    'lip_3.R' :         'GZM_Cube025',

    'mouthside_1.L' :   'GZM_Cube025',
    'mouthside_1.R' :   'GZM_Cube025',
    'mouthside_2.L' :   'GZM_Cube025',
    'mouthside_2.R' :   'GZM_Cube025',

    'noseside_1.L' :   'GZM_Cube025',
    'noseside_1.R' :   'GZM_Cube025',
    'noseside_2.L' :   'GZM_Cube025',
    'noseside_2.R' :   'GZM_Cube025',

    'loeye_1.L' :       'GZM_Cube025',
    'loeye_1.R' :       'GZM_Cube025',
    'loeye_2.L' :       'GZM_Cube025',
    'loeye_2.R' :       'GZM_Cube025',
    'loeye_3.L' :       'GZM_Cube025',
    'loeye_3.R' :       'GZM_Cube025',

    'brow_1.L' :       'GZM_Cube025',
    'brow_1.R' :       'GZM_Cube025',
    'brow_2.L' :       'GZM_Cube025',
    'brow_2.R' :       'GZM_Cube025',
    'brow_3.L' :       'GZM_Cube025',
    'brow_3.R' :       'GZM_Cube025',
}

Constraints = {
     'lip_3_parent.L' : [('CopyLoc', 0, 0.5, ['Jaw', 'lip_3_jaw.L', (1,1,1), (0,0,0), 0, False])],
     'lip_3_parent.R' : [('CopyLoc', 0, 0.5, ['Jaw', 'lip_3_jaw.R', (1,1,1), (0,0,0), 0, False])],

     'mouthside_1_parent.L' : [('CopyLoc', 0, 0.5, ['Jaw', 'mouthside_1_jaw.L', (1,1,1), (0,0,0), 0, False])],
     'mouthside_1_parent.R' : [('CopyLoc', 0, 0.5, ['Jaw', 'mouthside_1_jaw.R', (1,1,1), (0,0,0), 0, False])],

     'mouthside_2_parent.L' : [('CopyLoc', 0, 0.5, ['Jaw', 'mouthside_2_jaw.L', (1,1,1), (0,0,0), 0, False])],
     'mouthside_2_parent.R' : [('CopyLoc', 0, 0.5, ['Jaw', 'mouthside_2_jaw.R', (1,1,1), (0,0,0), 0, False])],
}

RotationLimits = {
    'jaw' : (-5*D,45*D, 0,0, -20*D,20*D),
}

MaxFaceTrans = (-0.1,0.1, -0.1,0.1, -0.1,0.1)

LocationLimits = {
    'jaw' :         (-0.2,0.2, -0.2,0.2, -0.2,0.2),

    'uplip_mid' :   MaxFaceTrans,
    'uplip_1.L' :   MaxFaceTrans,
    'uplip_1.R' :   MaxFaceTrans,
    'uplip_2.L' :   MaxFaceTrans,
    'uplip_2.R' :   MaxFaceTrans,

    'lolip_mid' :   MaxFaceTrans,
    'lolip_1.L' :   MaxFaceTrans,
    'lolip_1.R' :   MaxFaceTrans,
    'lolip_2.L' :   MaxFaceTrans,
    'lolip_2.R' :   MaxFaceTrans,

    'lip_3.L' :     MaxFaceTrans,
    'lip_3.R' :     MaxFaceTrans,

    'mouthside_1.L' :   MaxFaceTrans,
    'mouthside_1.R' :   MaxFaceTrans,
    'mouthside_2.L' :   MaxFaceTrans,
    'mouthside_2.R' :   MaxFaceTrans,

    'noseside_1.L' :   MaxFaceTrans,
    'noseside_1.R' :   MaxFaceTrans,
    'noseside_2.L' :   MaxFaceTrans,
    'noseside_2.R' :   MaxFaceTrans,

    'loeye_1.L' :   MaxFaceTrans,
    'loeye_1.R' :   MaxFaceTrans,
    'loeye_2.L' :   MaxFaceTrans,
    'loeye_2.R' :   MaxFaceTrans,
    'loeye_3.L' :   MaxFaceTrans,
    'loeye_3.R' :   MaxFaceTrans,

    'brow_1.L' :    MaxFaceTrans,
    'brow_1.R' :    MaxFaceTrans,
    'brow_2.L' :    MaxFaceTrans,
    'brow_2.R' :    MaxFaceTrans,
    'brow_3.L' :    MaxFaceTrans,
    'brow_3.R' :    MaxFaceTrans,
}

#
#    DeformDrivers(fp, amt):
#

def DeformDrivers(fp, amt):
    return []
    lidBones = [
    ('DEF_uplid.L', 'PUpLid_L', (0, 40*D)),
    ('DEF_lolid.L', 'PLoLid_L', (0, 20*D)),
    ('DEF_uplid.R', 'PUpLid_R', (0, 40*D)),
    ('DEF_lolid.R', 'PLoLid_R', (0, 20*D)),
    ]

    drivers = []
    for (driven, driver, coeff) in lidBones:
        drivers.append(    (driven, 'ROTQ', 'AVERAGE', None, 1, coeff,
         [("var", 'TRANSFORMS', [('OBJECT', amt.name, driver, 'LOC_Z', C_LOC)])]) )
    return drivers

