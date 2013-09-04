#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Definition of Progress class.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

The Progress module defines the Progress class, which provides an easy
and versatile way to handle MH's progress bar.

It takes care automatically for subroutines,
so that the programmer can avoid passing progress callbacks,
and only state the subroutine's impact on the progress, out of it.

*-- Usage --*

import Progress


# Standard usage.

def foo():
    progress = Progress.Progress()

    ... # do stuff #
    progress(0.7)
    ... # more stuff #
    progress(1.0)


# Usage in steps.

def bar():
    progress = Progress.Progress(42)

    ... # step 1 #
    progress.step()
    ... # step 2 #
    progress.step()
    ....
    ....
    ... # step 42 #
    progress.step()


# Usage in loops.

def baz(items):
    progress = Progress.Progress(len(items))

    for item in items:
        ... # do stuff #
        progress.substep(0.3)
        ... # more stuff #
        progress.substep(0.6)
        ... # even more stuff #
        progress.step()


# All together!!!
# (ie. time consuming functions that include
#  subroutines in them, that may have their own progress handler.)
# [This example shows the use of descriptions too.]

def FooBarBaz():
    progress = Progress.Progress()

    progress(0, 0.3, "Getting some foo")
    somefoo = foo()

    progress(0.3, 0.7, "Getting two bars", 2)
    bar1 = bar()
    bar2 = bar()

    progress(0.7, 0.99, "Bazzing them all together")
    bazzable = [somefoo, bar1, bar2]
    baz(bazzable)

    progress(1.0, None, "I've finished bazzing. Call me bazzer.")


----

Note: Progress is newbie-proof, ie. if you tell it that you'll
      call bar() 2 times (like above) and you call it 4,
      it won't explode, but when you call the 3rd bar(), it will
      start counting progress again from the point it was before you
      called the first bar() [which actually might be useful as a hack].
      It also has no problem if you call it only 1 time, it will just do
      the half progress to the next step, then jump to 0.7 of baz().

"""


import gui3d

global current
current = None


class Progress(object):
    def __init__(self, steps = 0, desc = None):
        global current
        self.prepared = False
        self.progress = 0.0
        self.steps = steps

        self.children = 0
        self.farstart = 0.0
        self.farend = 1.0
        self.nextstart = 0.0
        self.nextend = 1.0

        if current is None:
            # Generic case, where the progress bar is updated directly.
            self.parent = None
            current = self
            self.start = 0.0
            self.end = 1.0
            if desc is None:
                self.description = ""
            else:
                self.description = desc
        elif current.prepared:
            # Effect a subroutine progress update handler
            # if the programmer has told us its impact.
            self.parent = current
            current = self
            self.parent.childcreated()
            self.start = self.parent.nextstart
            self.end = self.parent.nextend
        else:
            # In this case the programmer doesn't care about the
            # progress updates of the current subroutine.
            self.parent = False


    # Internal method to be called by subroutine progress hanlders,
    # to refresh the next start and end limits for the next object.
    def childcreated(self):

        if self.children >= self.numsubs:
            self.children = 0

        diff = (self.farend - self.farstart)/self.numsubs
        self.nextstart = self.farstart + diff*self.children
        self.children += 1
        self.nextend = self.farstart + diff*self.children


    # Internal method that is responsible for the actual
    # progress bar and parent progress handler updating.
    def update(self, amount):
        self.progress = amount
        if self.progress >= 1.0:
            self.finish()
        amount = self.start + (self.end - self.start)*amount
        if self.parent:
            self.parent.update(amount)
        elif self.parent is None:
            gui3d.app.progress(amount, self.description)


    # Method to be called when a subroutine has finished,
    # either explicitly (by the user), or implicitly
    # (automatically when progress reaches 1.0).
    def finish(self):
        global current
        # Avoid  'False' parent here.
        if self.parent or self.parent is None:
            current = self.parent


    # Method useful for smaller tasks that take a number of steps
    # to complete, which are small enough to not need progress control.
    def step(self):
        
        if self.steps == 0:
            self.update(1.0)
        else:
            self.update(self.progress + 1.0/self.steps)


    # Method useful for tasks that process data in loops,
    # where each loop is a step(), and the progress
    # inside the loop can be updated with substep().
    def substep(self, amount):

        temp = self.progress
        self.update(temp + amount/self.steps)
        self.progress = temp


    # Basic method for progress updating.
    # It overloads the () operator of the constructed object.
    def __call__(self, progress, end = None, desc = None, numsubs = None):
        
        if desc is None:
            self.description = ""
        else:
            self.description = desc
        
        if numsubs is None:
            self.numsubs = 1 if end else 0
        else:
            self.numsubs = numsubs

        if end:
            self.farstart = progress
            self.farend = end
            self.children = 0
            self.prepared = True
        else:
            self.prepared = False

        self.update(progress)
