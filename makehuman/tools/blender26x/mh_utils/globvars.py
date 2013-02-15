# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165


#----------------------------------------------------------
#   Global variables
#----------------------------------------------------------

# Distance below which translations are ignored (in mm)
Epsilon = 1e-3

# Number of verts which are body, not clothes
NBodyVerts = 15340
FirstSkirtVert = 15340
FirstTightsVert = 16096
NTotalVerts = 18528

Proxy = None

BMeshAware = False

Confirm = None
ConfirmString = "" 
ConfirmString2 = ""


VertexNumbers = {}

VertexNumbers["alpha8a"] = {
    "Tongue"    : (0,226),
    "Body"      : (226, 13606),
    "Hair"      : (13606, 14034),
    "Skirt"     : (14034, 14754),
    "Tights"    : (14754, 17428),
    "Penis"     : (17428, 17628),
    "EyeLashes" : (17628, 17878),
    "Eyes"      : (17878, 18022),
    "LoTeeth"   : (18022, 18090),
    "UpTeeth"   : (18090, 18158),
    "Joints"     : (18158, 19166)
}        

VertexNumbers["alpha8b"] = {
    "Body"      : (0, 13380),
    "Tongue"    : (13380, 13606),
    "Joints"    : (13606, 14614),
    "Eyes"      : (14614, 14758),
    "EyeLashes" : (14758, 15008),
    "LoTeeth"   : (15008, 15076),
    "UpTeeth"   : (15076, 15144),
    "Penis"     : (15144, 15344),
    "Tights"    : (15344, 18018),
    "Skirt"     : (18018, 18738),
    "Hair"      : (18738, 19166),
}
        