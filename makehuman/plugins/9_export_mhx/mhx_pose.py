#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makeinfo.human.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makeinfo.human.org/node/318)

**Coding Standards:**  See http://www.makeinfo.human.org/node/165

Abstract
--------

Pose
"""

import log
import mh
import mh2proxy

import exportutils

from . import mhx_writer
from . import mhx_drivers

from core import G

def callback(progress, text=""):
    """
    Progress indicator callback
    """
    G.app.progress(progress, text)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

class Writer(mhx_writer.Writer):

    def __init__(self):
        mhx_writer.Writer.__init__(self)
        self.type == "mhx_pose"


    def writePose(self, fp):
        amt = self.armature
        config = self.config

        fp.write("""
    # --------------- Shapekeys ----------------------------- #
    """)

        self.proxyShapes('Cage', 'T_Cage', fp)
        self.proxyShapes('Proxymeshes', 'T_Proxy', fp)
        self.proxyShapes('Clothes', 'T_Clothes', fp)
        for ptype in mh2proxy.SimpleProxyTypes:
            self.proxyShapes(ptype, 'T_Clothes', fp)

        fp.write("#if toggle&T_Mesh\n")
        self.writeShapeKeysAndDrivers(fp, "%sMesh" % self.name, None)

        fp.write("""
    #endif

    # --------------- Actions ----------------------------- #

    #if toggle&T_Armature
    """)

        fp.write(
            "Pose %s\n" % self.name +
            "end Pose\n")
        #amt.writeAllActions(fp)

        fp.write("Pose %s\n" % self.name)
        amt.writeControlPoses(fp, config)
        fp.write("  ik_solver 'LEGACY' ;\nend Pose\n")
        amt.writeDrivers(fp)
        fp.write("CorrectRig %s ;\n" % self.name)
        fp.write("""
    #endif
    """)


    # *** material-drivers

    #-------------------------------------------------------------------------------
    #
    #-------------------------------------------------------------------------------

    def proxyShapes(self, typ, test, fp):
        fp.write("#if toggle&%s\n" % test)
        for proxy in self.proxies.values():
            if proxy.name and proxy.type == typ:
                self.writeShapeKeysAndDrivers(fp, self.name+proxy.name+"Mesh", proxy)
        fp.write("#endif\n")


    def writeShapeHeader(self, fp, pose, lr, min, max):
        fp.write(
            "ShapeKey %s %s True\n" % (pose, lr) +
            "  slider_min %.3g ;\n" % min +
            "  slider_max %.3g ;\n" % max)


    def writeShape(self, fp, pose, lr, shape, min, max, proxy, scale):
        if proxy:
            pshapes = proxy.getShapes([("shape",shape)], scale)
            if len(pshapes) > 0:
                name,pshape = pshapes[0]
                if len(pshape.keys()) > 0:
                    self.writeShapeHeader(fp, pose, lr, min, max)
                    fp.write("".join( ["  sv %d %.4f %.4f %.4f ;\n" %  (pv, dr[0], -dr[2], dr[1]) for (pv, dr) in pshape.items()] ))
                    fp.write("end ShapeKey\n")
                    return False
        else:
            self.writeShapeHeader(fp, pose, lr, min, max)
            s = scale
            fp.write("".join( ["  sv %d %.4f %.4f %.4f ;\n" %  (vn, s*dr[0], -s*dr[2], s*dr[1]) for (vn, dr) in shape.items()] ))
            fp.write("end ShapeKey\n")
            return False
        return True


    def writeShapeKeysAndDrivers(self, fp, name, proxy):
        fp.write(
            "#if toggle&T_Shapekeys\n" +
            "ShapeKeys %s\n" % name +
            "  ShapeKey Basis Sym True\n" +
            "  end ShapeKey\n")

        self.writeShapeKeys(fp, name, proxy)

        fp.write("  AnimationData None (toggle&T_Symm==0)\n")
        self.writeShapeKeyDrivers(fp, name, proxy)
        fp.write(
            "  end AnimationData\n\n" +
            "  end ShapeKeys\n" +
            "#endif\n")


    def writeShapeKeys(self, fp, name, proxy):
        amt = self.armature
        config = self.config
        scale = config.scale

        isHuman = ((not proxy) or proxy.type == 'Proxymeshes')

        if isHuman and config.expressions:
            try:
                shapeList = self.loadedShapes["expressions"]
            except KeyError:
                shapeList = None
            if shapeList is None:
                shapeList = exportutils.shapekeys.readExpressionUnits(self.human, 0.7, 0.9, callback)
                self.loadedShapes["expressions"] = shapeList
            for (pose, shape) in shapeList:
                self.writeShape(fp, pose, "Sym", shape, -1, 2, proxy, scale)

        if isHuman:
            for path,name in self.customTargetFiles:
                try:
                    shape = self.loadedShapes[path]
                except KeyError:
                    shape = None
                if shape is None:
                    log.message("    %s", path)
                    shape = exportutils.custom.readCustomTarget(path)
                    self.loadedShapes[path] = shape
                self.writeShape(fp, name, "Sym", shape, -1, 2, proxy, scale)

        if config.expressions and not proxy:
            exprList = exportutils.shapekeys.readExpressionMhm(mh.getSysDataPath("expressions"))
            self.writeExpressions(fp, exprList, "Expression")
            visemeList = exportutils.shapekeys.readExpressionMhm(mh.getSysDataPath("visemes"))
            self.writeExpressions(fp, visemeList, "Viseme")


    def writeShapeKeyDrivers(self, fp, name, proxy):
        isHuman = ((not proxy) or proxy.type == 'Proxymeshes')
        amt = self.armature

        fp.write("#if toggle&T_ShapeDrivers\n")

        if isHuman:
            for path,name in self.customTargetFiles:
                mhx_drivers.writeShapePropDrivers(fp, amt, [name], proxy, "Mhc", callback)

            if self.config.expressions:
                mhx_drivers.writeShapePropDrivers(fp, amt, exportutils.shapekeys.ExpressionUnits, proxy, "Mhs", callback)

            skeys = []
            for (skey, val, string, min, max) in  self.customProps:
                skeys.append(skey)
            mhx_drivers.writeShapePropDrivers(fp, amt, skeys, proxy, "Mha", callback)
        fp.write("#endif\n")


    def writeExpressions(self, fp, exprList, label):
        for (name, units) in exprList:
            fp.write("  %s %s\n" % (label, name))
            for (unit, value) in units:
                fp.write("    %s %s ;\n" % (unit, value))
            fp.write("  end\n")

