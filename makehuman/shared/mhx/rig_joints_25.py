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

Deform joint definitions
"""

DeformJoints = [
	# Spine
	('pelvis',			'j', 'pelvis'),
	('spine4',			'j', 'spine4'),
	('spine3',			'j', 'spine3'),
	('spine2',			'j', 'spine2'),
	('spine1',			'j', 'spine1'),
	('neck',			'j', 'neck'),
	('head',			'j', 'head'),
	('head2',			'j', 'head2'),

	# Head

	('mouth',			'j', 'mouth'),
	('jaw',				'j', 'jaw'),
	
	('tongue-1',			'j', 'tongue-1'),
	('tongue-2',			'j', 'tongue-2'),
	('tongue-3',			'j', 'tongue-3'),
	('tongue-4',			'j', 'tongue-4'),

	('l-eye',			'j', 'l-eye'),
	('r-eye',			'j', 'r-eye'),
	('l-eye-target',		'j', 'l-eye-target'),
	('r-eye-target',		'j', 'r-eye-target'),
	('l-upperlid',			'j', 'l-upperlid'),
	('l-lowerlid',			'j', 'l-lowerlid'),
	('r-upperlid',			'j', 'r-upperlid'),
	('r-lowerlid',			'j', 'r-lowerlid'),

	# Legs
	('r-upper-leg',			'j', 'r-upper-leg'),
	('r-knee-raw',			'j', 'r-knee'),
	('r-ankle',			'j', 'r-ankle'),
	('r-foot-1',			'j', 'r-foot-1'),
	('r-foot-2',			'vz', (15306, 'r-foot-1')),

	('l-upper-leg',			'j', 'l-upper-leg'),
	('l-knee-raw',			'j', 'l-knee'),
	('l-ankle',			'j', 'l-ankle'),
	('l-foot-1',			'j', 'l-foot-1'),
	('l-foot-2',			'vz', (15091, 'l-foot-1')),

	# Arms
	('r-clavicle',			'j', 'r-clavicle'),
	('r-shoulder',			'j', 'r-shoulder'),
	('r-scapula',			'j', 'r-scapula'),
	('r-elbow-raw',			'j', 'r-elbow'),
	('r-hand',			'j', 'r-hand'),

	('l-clavicle',			'j', 'l-clavicle'),
	('l-shoulder',			'j', 'l-shoulder'),
	('l-scapula',			'j', 'l-scapula'),
	('l-elbow-raw',			'j', 'l-elbow'),
	('l-hand',			'j', 'l-hand'),

	# Fingers
	('r-finger-1-1',	'j', 'r-finger-1-1'),
	('r-finger-1-2',	'j', 'r-finger-1-2'),
	('r-finger-1-3',	'j', 'r-finger-1-3'),
	('r-finger-1-4',	'j', 'r-finger-1-4'),
	('r-finger-2-1',	'j', 'r-finger-2-1'),
	('r-finger-2-2',	'j', 'r-finger-2-2'),
	('r-finger-2-3',	'j', 'r-finger-2-3'),
	('r-finger-2-4',	'j', 'r-finger-2-4'),
	('r-finger-3-1',	'j', 'r-finger-3-1'),
	('r-finger-3-2',	'j', 'r-finger-3-2'),
	('r-finger-3-3',	'j', 'r-finger-3-3'),
	('r-finger-3-4',	'j', 'r-finger-3-4'),
	('r-finger-4-1',	'j', 'r-finger-4-1'),
	('r-finger-4-2',	'j', 'r-finger-4-2'),
	('r-finger-4-3',	'j', 'r-finger-4-3'),
	('r-finger-4-4',	'j', 'r-finger-4-4'),
	('r-finger-5-1',	'j', 'r-finger-5-1'),
	('r-finger-5-2',	'j', 'r-finger-5-2'),
	('r-finger-5-3',	'j', 'r-finger-5-3'),
	('r-finger-5-4',	'j', 'r-finger-5-4'),

	('l-finger-1-1',	'j', 'l-finger-1-1'),
	('l-finger-1-2',	'j', 'l-finger-1-2'),
	('l-finger-1-3',	'j', 'l-finger-1-3'),
	('l-finger-1-4',	'j', 'l-finger-1-4'),
	('l-finger-2-1',	'j', 'l-finger-2-1'),
	('l-finger-2-2',	'j', 'l-finger-2-2'),
	('l-finger-2-3',	'j', 'l-finger-2-3'),
	('l-finger-2-4',	'j', 'l-finger-2-4'),
	('l-finger-3-1',	'j', 'l-finger-3-1'),
	('l-finger-3-2',	'j', 'l-finger-3-2'),
	('l-finger-3-3',	'j', 'l-finger-3-3'),
	('l-finger-3-4',	'j', 'l-finger-3-4'),
	('l-finger-4-1',	'j', 'l-finger-4-1'),
	('l-finger-4-2',	'j', 'l-finger-4-2'),
	('l-finger-4-3',	'j', 'l-finger-4-3'),
	('l-finger-4-4',	'j', 'l-finger-4-4'),
	('l-finger-5-1',	'j', 'l-finger-5-1'),
	('l-finger-5-2',	'j', 'l-finger-5-2'),
	('l-finger-5-3',	'j', 'l-finger-5-3'),
	('l-finger-5-4',	'j', 'l-finger-5-4'),

	# Toes
	('r-toe-1-1',			'j', 'r-toe-1-1'),
	('r-toe-1-2',			'j', 'r-toe-1-2'),
	('r-toe-2-1',			'j', 'r-toe-2-1'),
	('r-toe-2-2',			'j', 'r-toe-2-2'),
	('r-toe-2-3',			'j', 'r-toe-2-3'),
	('r-toe-3-1',			'j', 'r-toe-3-1'),
	('r-toe-3-2',			'j', 'r-toe-3-2'),
	('r-toe-3-3',			'j', 'r-toe-3-3'),
	('r-toe-4-1',			'j', 'r-toe-4-1'),
	('r-toe-4-2',			'j', 'r-toe-4-2'),
	('r-toe-4-3',			'j', 'r-toe-4-3'),
	('r-toe-5-1',			'j', 'r-toe-5-1'),
	('r-toe-5-2',			'j', 'r-toe-5-2'),
	('r-toe-5-3',			'j', 'r-toe-5-3'),

	('l-toe-1-1',			'j', 'l-toe-1-1'),
	('l-toe-1-2',			'j', 'l-toe-1-2'),
	('l-toe-2-1',			'j', 'l-toe-2-1'),
	('l-toe-2-2',			'j', 'l-toe-2-2'),
	('l-toe-2-3',			'j', 'l-toe-2-3'),
	('l-toe-3-1',			'j', 'l-toe-3-1'),
	('l-toe-3-2',			'j', 'l-toe-3-2'),
	('l-toe-3-3',			'j', 'l-toe-3-3'),
	('l-toe-4-1',			'j', 'l-toe-4-1'),
	('l-toe-4-2',			'j', 'l-toe-4-2'),
	('l-toe-4-3',			'j', 'l-toe-4-3'),
	('l-toe-5-1',			'j', 'l-toe-5-1'),
	('l-toe-5-2',			'j', 'l-toe-5-2'),
	('l-toe-5-3',			'j', 'l-toe-5-3'),

]

FloorJoints = [
    ('r-toe-1-1',      'j', 'r-toe-1-1'),
    ('l-toe-1-1',      'j', 'l-toe-1-1'),
    ('mid-feet',       'l', ((0.5, 'l-toe-1-1'), (0.5, 'r-toe-1-1'))),
    ('floor',          'o', ('mid-feet', [0,-0.3,0])),
]

