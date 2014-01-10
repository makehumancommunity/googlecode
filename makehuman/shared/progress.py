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

from progress import Progress


# Standard usage.

def foo():
    progress = Progress()

    ... # do stuff #
    progress(0.7)
    ... # more stuff #
    progress(1.0)


# Usage in steps.

def bar():
    progress = Progress(42)

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
    progress = Progress(len(items))

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
    progress = Progress()

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


global current_Progress_
current_Progress_ = None


class Progress(object):
    def __init__(self, steps = 0, progressCallback = None, logging = False, timing = False):
        global current_Progress_
        
        self.progress = 0.0
        self.steps = steps
        self.stepsdone = 0
        self.description = None

        self.time = None
        self.totalTime = 0.0

        self.logging = logging
        self.timing = timing

        self.children = 0
        self.farstart = 0.0
        self.farend = 1.0
        self.nextstart = 0.0

        if steps > 0:
            self.prepared = True
            self.nextend = 1.0/steps
            self.numsubs = 1
        else:
            self.prepared = False
            self.nextend = 1.0
            self.numsubs = 0
        
        if current_Progress_ is None:
            # Generic case, where the progress bar is updated directly.
            self.parent = None
            current_Progress_ = self
            self.start = 0.0
            self.end = 1.0
        elif current_Progress_.prepared:
            # Effect a subroutine progress update handler
            # if the programmer has told us its impact.
            self.parent = current_Progress_
            current_Progress_ = self
            self.parent.childcreated()
            self.start = self.parent.nextstart
            self.end = self.parent.nextend
        else:
            # In this case the programmer doesn't care about the
            # progress updates of the current subroutine.
            self.parent = False

        # Get the callback that updates MH's progress bar.
        # Has mechanism to avoid importing gui3d, if possible.
        if self.parent is None:
            if progressCallback is None:
                import gui3d
                self.progressCallback = gui3d.app.progress
            else: # In this case the user provided us with a custom
                #   progress callback to use instead of importing gui3d.
                #   Update: They can pass False to completely avoid gui3d.
                self.progressCallback = progressCallback
        else: # In this case we need no gui3d (most of cases).
            self.progressCallback = None


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
    def update(self, amount, childDescription = None, childupdate = False):
        self.progress = amount
        if self.parent != False and not childupdate:
            amount = self.start + (self.end - self.start)*amount
        if self.parent:
            if self.description:
                self.parent.update(amount, self.description, True)
            else:
                self.parent.update(amount, childDescription, True)
        elif self.parent is None and self.progressCallback != False:
            if self.timing:
                import time
                t = time.time()
                if self.time:
                    deltaT = (t - self.time)
                    self.totalTime += deltaT
                    if self.logging:
                        import log
                        log.debug("  took %s seconds", deltaT)
                self.time = t

            if childDescription:
                desc = childDescription
            elif self.description:
                desc = self.description
            else:
                desc = ""
            self.progressCallback(amount, desc)
            if self.logging:
                import log
                log.debug("Progress %s%%: %s", amount, desc)

        if self.progress >= 0.999999: # Not using 1.0 for precision safety.
            self.finish()


    # Method to be called when a subroutine has finished,
    # either explicitly (by the user), or implicitly
    # (automatically when progress reaches 1.0).
    def finish(self):
        global current_Progress_

        if not self.parent and self.logging and self.timing:
            import log
            log.debug("Total time taken: %s seconds.", self.totalTime)

        if self.parent != False:
            current_Progress_ = self.parent


    # Method useful for smaller tasks that take a number
    # of roughly equivalent steps to complete.
    # Update: Each step may accept children Progress objects.
    def step(self, desc = None, numsubs = 1):

        if desc:
            self.description = desc
        
        if self.steps == 0:
            self.update(1.0)
        else:
            self.numsubs = numsubs

            diff = 1.0/self.steps
            self.stepsdone += 1
            self.progress = self.stepsdone*diff

            self.farstart = self.progress
            self.farend = self.progress + diff
            self.children = 0
            self.prepared = True
            
            self.update(self.progress)


    # Method useful for tasks that process data in loops,
    # where each loop is a step(), and the progress
    # inside the loop can be updated with substep().
    def substep(self, amount, desc = None):
        temp = self.progress
        self.update(temp + amount/self.steps, desc)
        self.progress = temp


    # Basic method for progress updating.
    # It overloads the () operator of the constructed object.
    # Pass None to the description to allow the child update status.
    def __call__(self, progress, end = None, desc = False, numsubs = None):

        if not (desc is False):
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


    # Class method for directly creating a master Progress object.
    # Resets all progress to zero. Use this for starting a greater MH task.
    @classmethod
    def begin(cls):
        
        global current_Progress_
        
        current_Progress_ = None
        return cls()


    ## Specialized methods follow ##


    # Method that prepares the Progress object to run in a hispeed loop
    # with high number of repetitions, which needs to progress the bar
    # while looping without adding callback overhead.
    # WARNING: ALWAYS test the overhead. Don't use this
    # in extremely fast loops or it might slow them down.
    def HighFrequency(self, interval):

        # Loop number interval between progress updates.
        self.HFI = interval

        # Replace original step method with the high frequency step.
        self.dostep = self.step
        self.step = self.HFstep

        return self


    # Replacement method to be called in a hispeed loop instead of step().
    # It is replaced internally on HighFrequency() (call step() to use it).
    def HFstep(self):

        if self.stepsdone % self.HFI > 0 and self.stepsdone < self.steps - 1:
            self.stepsdone +=1
        else:
            self.dostep()
