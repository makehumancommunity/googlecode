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

    def writePose(self, fp):
        amt = self.armature
        config = self.config

        fp.write("""
    # --------------- Shapekeys ----------------------------- #
    """)

        self.proxyShapes('Cage', 'T_Cage', fp)
        self.proxyShapes('Proxy', 'T_Proxy', fp)
        self.proxyShapes('Clothes', 'T_Clothes', fp)
        self.proxyShapes('Hair', 'T_Clothes', fp)
        self.proxyShapes('Eyes', 'T_Clothes', fp)
        self.proxyShapes('Genitals', 'T_Clothes', fp)

        fp.write("#if toggle&T_Mesh\n")
        self.writeShapeKeys(fp, "%sMesh" % self.name, None)

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
                self.writeShapeKeys(fp, self.name+proxy.name+"Mesh", proxy)
        fp.write("#endif\n")


    def writeCorrectives(self, fp, drivers, folder, landmarks, proxy, t0, t1, callback):
        amt = self.armature
        empties = []
        try:
            shapeList = amt.loadedShapes[folder]
        except KeyError:
            shapeList = None
        if shapeList is None:
            shapeList = exportutils.shapekeys.readCorrectives(drivers, self.human, folder, landmarks, t0, t1, callback)
            amt.loadedShapes[folder] = shapeList
        for (shape, pose, lr) in shapeList:
            empty = self.writeShape(fp, pose, lr, shape, 0, 1, proxy, self.config.scale)
            if empty:
                empties.append(pose)
        return empties


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


    def writeShapeKeys(self, fp, name, proxy):
        amt = self.armature
        config = self.config
        scale = config.scale

        isHuman = ((not proxy) or proxy.type == 'Proxy')
        isHair = (proxy and proxy.type in ['Hair','Eyes', 'Genitals'])
        useCorrectives = (
            False and
            config.bodyShapes and
            amt.options.rigtype == "mhx" and
            ((not proxy) or (proxy.type in ['Proxy', 'Clothes']))
        )

        fp.write(
    "#if toggle&T_Shapekeys\n" +
    "ShapeKeys %s\n" % name +
    "  ShapeKey Basis Sym True\n" +
    "  end ShapeKey\n")

        if isHuman and amt.options.facepanel:
            shapeList = exportutils.shapekeys.readFaceShapes(self.human, rig_panel.BodyLanguageShapeDrivers, 0.6, 0.7)
            for (pose, shape, lr, min, max) in shapeList:
                self.writeShape(fp, pose, lr, shape, min, max, proxy, scale)

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

        if useCorrectives:
            shoulder = self.writeCorrectives(fp, rig_mhx.ShoulderTargetDrivers, "shoulder", "shoulder", proxy, 0.88, 0.90)
            hips = self.writeCorrectives(fp, rig_mhx.HipTargetDrivers, "hips", "hips", proxy, 0.90, 0.92)
            elbow = self.writeCorrectives(fp, rig_mhx.ElbowTargetDrivers, "elbow", "body", proxy, 0.92, 0.94)
            knee = self.writeCorrectives(fp, rig_mhx.KneeTargetDrivers, "knee", "knee", proxy, 0.94, 0.96)

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

        fp.write("  AnimationData None (toggle&T_Symm==0)\n")

        if useCorrectives:
            mhx_drivers.writeTargetDrivers(fp, rig_mhx.ShoulderTargetDrivers, self.name, shoulder)
            mhx_drivers.writeTargetDrivers(fp, rig_mhx.HipTargetDrivers, self.name, hips)
            mhx_drivers.writeTargetDrivers(fp, rig_mhx.ElbowTargetDrivers, self.name, elbow)
            mhx_drivers.writeTargetDrivers(fp, rig_mhx.KneeTargetDrivers, self.name, knee)

            mhx_drivers.writeRotDiffDrivers(fp, rig_mhx.ArmShapeDrivers, proxy)
            mhx_drivers.writeRotDiffDrivers(fp, rig_mhx.LegShapeDrivers, proxy)
            #mhx_drivers.writeShapePropDrivers(fp, amt, rig_mhx.bodyShapes, proxy, "Mha", callback)

        fp.write("#if toggle&T_ShapeDrivers\n")

        if isHuman:
            for path,name in self.customTargetFiles:
                mhx_drivers.writeShapePropDrivers(fp, amt, [name], proxy, "Mhc", callback)

            if config.expressions:
                mhx_drivers.writeShapePropDrivers(fp, amt, exportutils.shapekeys.ExpressionUnits, proxy, "Mhs", callback)

            if amt.options.facepanel and amt.options.rigtype=='mhx':
                mhx_drivers.writeShapeDrivers(fp, amt, rig_panel.BodyLanguageShapeDrivers, proxy)

            skeys = []
            for (skey, val, string, min, max) in  self.customProps:
                skeys.append(skey)
            mhx_drivers.writeShapePropDrivers(fp, amt, skeys, proxy, "Mha", callback)
        fp.write("#endif\n")

        fp.write("  end AnimationData\n\n")

        if config.expressions and not proxy:
            exprList = exportutils.shapekeys.readExpressionMhm(mh.getSysDataPath("expressions"))
            self.writeExpressions(fp, exprList, "Expression")
            visemeList = exportutils.shapekeys.readExpressionMhm(mh.getSysDataPath("visemes"))
            self.writeExpressions(fp, visemeList, "Viseme")

        fp.write(
            "  end ShapeKeys\n" +
            "#endif\n")
        return


    def writeExpressions(self, fp, exprList, label):
        for (name, units) in exprList:
            fp.write("  %s %s\n" % (label, name))
            for (unit, value) in units:
                fp.write("    %s %s ;\n" % (unit, value))
            fp.write("  end\n")

