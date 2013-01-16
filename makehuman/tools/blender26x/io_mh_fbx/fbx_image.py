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

import bpy
import os

from . import fbx
from .fbx_basic import *
from .fbx_props import *
from .fbx_model import *

#------------------------------------------------------------------
#   Image
#------------------------------------------------------------------

class CImage(CConnection):
    propertyTemplate = (         
"""
        PropertyTemplate: "KFbxVideo" {
            Properties70:  {
                P: "ImageSequence", "bool", "", "",0
                P: "ImageSequenceOffset", "int", "Integer", "",0
                P: "FrameRate", "double", "Number", "",0
                P: "LastFrame", "int", "Integer", "",0
                P: "Width", "int", "Integer", "",0
                P: "Height", "int", "Integer", "",0
                P: "Path", "KString", "XRefUrl", "", ""
                P: "StartFrame", "int", "Integer", "",0
                P: "StopFrame", "int", "Integer", "",0
                P: "PlaySpeed", "double", "Number", "",0
                P: "Offset", "KTime", "Time", "",0
                P: "InterlaceMode", "enum", "", "",0
                P: "FreeRunning", "bool", "", "",0
                P: "Loop", "bool", "", "",0
                P: "AccessMode", "enum", "", "",0
            }
        }
""")        

    def __init__(self, subtype=''):
        CConnection.__init__(self, 'Video', subtype, 'IMAGE')        
        self.parseTemplate('Video', CImage.propertyTemplate)
        self.isModel = True    
        self.image = None


    def make(self, img):
        CConnection.make(self, img)
        self.struct["Filename"] = os.path.basename(img.filepath)
        self.struct["RelativeFilename"] = os.path.basename(img.filepath)
        self.struct["Type"] = "Clip"
        self.struct["UseMipMap"] = 0

        self.setProps([
            ("Path", self.struct["Filename"])
        ])
        return self
    

    def build(self):
        path = os.path.join(fbx.activeFolder, self.struct["RelativeFilename"]) 
        print("Loading", path)
        self.image = bpy.data.images.load(path)
        fbx.data[self.id] = self.image
        return self.image
