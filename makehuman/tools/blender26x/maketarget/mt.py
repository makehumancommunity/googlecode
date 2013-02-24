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

from mhutils import mh

class CSettings(mh.CSettings):
    
    def __init__(self, version):
        mh.CSettings.__init__(self, version)

        if version == "alpha7":                    
            
            self.irrelevantVerts = {
               "Body" : (self.vertices["Skirt"][0], self.nTotalVerts),
               "Skirt" : (self.nTotalVerts, self.nTotalVerts),
               "Tights" : self.vertices["Skirt"],
            }

            self.affectedVerts = {
                "Body" : (0, self.vertices["Skirt"][0]),
                "Skirt" : self.vertices["Skirt"],
                "Tights" : self.vertices["Tights"][0],
            }

            self.offsetVerts = {
                "Body" : 0,
                "Skirt" : 0,
                "Tights" : self.vertices["Tights"][0] - self.vertices["Skirt"][0],
            }            

        elif version == "alpha8":

            self.irrelevantVerts = {
               "Body" : (self.vertices["Body"][0], self.nTotalVerts),
               "Skirt" : (self.vertices["Skirt"][1], self.nTotalVerts),
               "Tights" : (self.vertices["Skirt"][0], self.nTotalVerts),
            }

            self.affectedVerts = {
                "Body" : (0, self.vertices["Tights"][0]),
                "Skirt" : self.vertices["Skirt"],
                "Tights" : self.vertices["Tights"],
            }

            self.offsetVerts = {
                "Body" : 0,
                "Skirt" : self.vertices["Skirt"][0] - self.vertices["Tights"][0],
                "Tights" : 0,
            }


settings = {
    "alpha7" : CSettings("alpha7"),
    "alpha8" : CSettings("alpha8"),
    "None"   : None
}

