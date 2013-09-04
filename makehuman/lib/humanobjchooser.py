#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Human Object Chooser widget.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

A widget for selecting the human object or any of the proxies attached to it.
"""

from PyQt4 import QtCore, QtGui

import qtgui as gui
import log


class HumanObjectSelector(gui.QtGui.QWidget, gui.Widget):
    """
    A widget for selecting the human object or any of the proxies attached to it.
    """

    def __init__(self, human):
        super(HumanObjectSelector, self).__init__()
        self.human = human
        self._selected = 'skin'

        self.layout = gui.QtGui.QGridLayout(self)

        self.objectSelector = []
        self.humanBox = gui.GroupBox('Human')
        self.layout.addWidget(self.humanBox)
        self.skinRadio = self.humanBox.addWidget(gui.RadioButton(self.objectSelector, "Skin", selected=True))
        self.hairRadio = self.humanBox.addWidget(gui.RadioButton(self.objectSelector, "Hair", selected=False))
        self.eyesRadio = self.humanBox.addWidget(gui.RadioButton(self.objectSelector, "Eyes", selected=False))
        self.genitalsRadio = self.humanBox.addWidget(gui.RadioButton(self.objectSelector, "Genitals", selected=False))

        @self.skinRadio.mhEvent
        def onClicked(event):
            if self.skinRadio.selected:
                self.selected = 'skin'
                self.callEvent('onActivate', self.selected)

        @self.hairRadio.mhEvent
        def onClicked(event):
            if self.hairRadio.selected:
                self.selected = 'hair'
                self.callEvent('onActivate', self.selected)

        @self.eyesRadio.mhEvent
        def onClicked(event):
            if self.eyesRadio.selected:
                self.selected = 'eyes'
                self.callEvent('onActivate', self.selected)

        @self.genitalsRadio.mhEvent
        def onClicked(event):
            if self.genitalsRadio.selected:
                self.selected = 'genitals'
                self.callEvent('onActivate', self.selected)

        self.clothesBox = gui.GroupBox('Clothes')
        self.layout.addWidget(self.clothesBox)
        self.clothesSelections = []

    def getSelected(self):
        if self._selected == 'eyes' and not self.human.eyesObj:
            return 'skin'

        if self._selected == 'genitals' and not self.human.genitalsObj:
            return 'skin'

        if self._selected == 'hair' and not self.human.hairObj:
            return 'skin'

        if self._selected in ['skin', 'hair', 'eyes', 'genitals'] or \
           self._selected in self.human.clothesObjs.keys():
            return self._selected
        else:
            return 'skin'

    def setSelected(self, value):
        if self._selected == 'eyes' and not self.human.eyesObj:
            self._selected = 'skin'
            return

        if self._selected == 'genitals' and not self.human.genitalsObj:
            self._selected = 'skin'
            return

        if self._selected == 'hair' and not self.human.hairObj:
            self._selected = 'skin'
            return

        if value in ['skin', 'hair', 'eyes', 'genitals'] or \
           value in self.human.clothesObjs.keys():
            self._selected = value
        else:
            self._selected = 'skin'

    selected = property(getSelected, setSelected)

    def onShow(self, event):
        selected = self.selected

        self.skinRadio.setChecked(selected == 'skin')

        if self.human.hairObj:
            self.hairRadio.setEnabled(True)
        else:
            self.hairRadio.setEnabled(False)
        self.hairRadio.setChecked(selected == 'hair')

        if self.human.eyesObj:
            self.eyesRadio.setEnabled(True)
        else:
            self.eyesRadio.setEnabled(False)
        self.eyesRadio.setChecked(selected == 'eyes')

        if self.human.genitalsObj:
            self.genitalsRadio.setEnabled(True)
        else:
            self.genitalsRadio.setEnabled(False)
        self.genitalsRadio.setChecked(selected == 'genitals')

        self._populateClothesSelector()

    def _populateClothesSelector(self):
        """
        Builds a list of all available clothes.
        """
        human = self.human
        # Only keep first 3 radio btns (human body parts)
        for radioBtn in self.objectSelector[3:]:
            radioBtn.hide()
            radioBtn.destroy()
        del self.objectSelector[3:]

        self.clothesSelections = []
        clothesList = human.clothesObjs.keys()
        selected = self.selected
        for i, uuid in enumerate(clothesList):
            radioBtn = self.clothesBox.addWidget(gui.RadioButton(self.objectSelector, human.clothesProxies[uuid].name, selected=(selected == uuid)))
            self.clothesSelections.append( (radioBtn, uuid) )

            @radioBtn.mhEvent
            def onClicked(event):
                for radio, uuid in self.clothesSelections:
                    if radio.selected:
                        self.selected = uuid
                        log.debug( 'Selected clothing "%s" (%s)' % (radio.text(), uuid) )
                        self.callEvent('onActivate', self.selected)
                        return

