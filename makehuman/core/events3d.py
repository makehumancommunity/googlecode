#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
:Authors:
    Marc Flerackers

:Version: 1.0
:Copyright: MakeHuman Team 2001-2011
:License: GPL3 

This module contains classes to allow an object to handle events.
"""

class Event:
    """
    Base class for all events, does not contain information.
    """
    def __init__(self):
        pass

    def __repr__(self):
        return 'event:'


class MouseEvent(Event):
    """
    Contains information about a mouse event.
    
    :param button: the button that is pressed in case of a mousedown or mouseup event, or button flags in case of a mousemove event.
    :type button: int
    :param x: the x position of the mouse in window coordinates.
    :type x: int
    :param y: the y position of the mouse in window coordinates.
    :type y: int
    :param dx: the difference in x position in case of a mousemove event.
    :type dx: int
    :param dy: the difference in y position in case of a mousemove event.
    :type dy: int
    """
    def __init__(self, button, x, y, dx=0, dy=0):
        self.button = button
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def __repr__(self):
        return 'MouseEvent(%d, %d, %d, %d, %d)' % (self.button, self.x, self.y, self.dx, self.dy)


class MouseWheelEvent(Event):
    """
    Contains information about a mouse wheel event.
    
    :param wheelDelta: the amount and direction that the wheel was scrolled.
    :type wheelDelta: int
    """
    def __init__(self, wheelDelta):
        self.wheelDelta = wheelDelta

    def __repr__(self):
        return 'MouseWheelEvent(%d)' % self.wheelDelta


class KeyEvent(Event):
    """
    Contains information about a keyboard event.
    
    :param key: the key code of the key that was pressed or released.
    :type key: int
    :param character: the unicode character if the key represents a character.
    :type character: unicode
    :param modifiers: the modifier keys that were down at the time of pressing the key.
    :type modifiers: int
    """
    def __init__(self, key, character, modifiers):
        self.key = key
        self.character = character
        self.modifiers = modifiers

    def __repr__(self):
        return 'KeyEvent(%d, %04x %s, %d)' % (self.key, ord(self.character), self.character, self.modifiers)


class FocusEvent(Event):
    """
    Contains information about a view focus/blur event
    
    :param blurred: the view that lost the focus.
    :type blurred: guid3d.View
    :param focused: the view that gained the focus.
    :type focused: guid3d.View
    """
    def __init__(self, blurred, focused):
        self.blurred = blurred
        self.focused = focused

    def __repr__(self):
        return 'FocusEvent(%s, %s)' % (self.blurred, self.focused)


class ResizeEvent(Event):
    """
    Contains information about a resize event
    
    :param width: the new width of the window in pixels.
    :type width: int
    :param height: the new height of the window in pixels.
    :type height: int
    :param fullscreen: the new fullscreen state of the window.
    :type fullscreen: Boolean
    :param dx: the change in width of the window in pixels.
    :type dx: int
    :param dy: the change in height of the window in pixels.
    :type dy: int
    """
    def __init__(self, width, height, fullscreen, dx, dy):
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.dx = dx
        self.dy = dy

    def __repr__(self):
        return 'ResizeEvent(%d, %d, %s, %d, %d)' % (self.width, self.height, self.fullscreen, self.dx, self.dy)
        

class EventHandler(object):
    """
    Base event handler class. Derive from this class if an object needs to be able to have events attached to it.
    Currently only one event per event name can be attached. This is because we either allow a class method or
    a custom method to be attached as event handling method. Since the custom method replaces the class method,
    it is needed in some case to call the base class's method from the event handling method.
    
    There are 2 ways to attach handlers:
    
    1. Override the method. This is the most appropriate way when you want to add distinctive behaviour to many EventHandlers.
    
    ::
        
        class Widget(View):
        
            def onMouseDown(self, event):
                #Handle event
                
    2. Use the event decorator. This is the most appropriate way when you want to attach distinctive behaviour to one EventHandler.
    
    ::
        
        widget = Widget()
        
        @widget.mhEvent:
        def onMouseDown(event):
            #Handle event
            
    Note that self is not passed to the handler in this case, which should not be a problem as you can just use the variable since you are creating a closure. 
    """
    def __init__(self):
        pass

    def callEvent(self, eventType, event):

        #print("Sending %s to %s" % (eventType, self))

        if hasattr(self, eventType):
            getattr(self, eventType)(event)

    def attachEvent(self, eventName, eventMethod):
        setattr(self, eventName, eventMethod)

    def detachEvent(self, eventName):
        delattr(self, eventName)

    def mhEvent(self, eventMethod):
        self.attachEvent(eventMethod.__name__, eventMethod)
