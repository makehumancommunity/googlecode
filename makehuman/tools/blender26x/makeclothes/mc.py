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


from mh_utils import mh

class CSettings(mh.CSettings):
    
    def __init__(self, version):
        mh.CSettings.__init__(self, version)

        if version == "alpha7":                    
            self.topOfSkirt1    = range(16691,16707)
            
            self.bodyPartVerts = {
                "Head" : ((4302, 8697), (8208, 8220), (8223, 6827)), 
                "Torso" : ((3464, 10305), (6930, 7245), (14022, 14040)),
                "Arm" : ((14058, 14158), (4550, 4555), (4543, 4544)), 
                "Hand" : ((14058, 15248), (3214, 3264), (4629, 5836)),
                "Leg" : ((3936, 3972), (3840, 3957), (14165, 14175)), 
                "Foot" : ((4909, 4943), (5728, 12226), (4684, 5732)), 
                "Eye" : ((142, 197), (76, 141), (169, 225)), 
            }                               

        elif version == "alpha8":
        
            self.topOfSkirt1    = []
            self.bodyPartVerts = {}


settings = {
    "alpha7" : CSettings("alpha7"),
    "alpha8" : CSettings("alpha8"),
    "None"   : None
}