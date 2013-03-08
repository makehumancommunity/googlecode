#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier, Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Various image processing operations.
"""

import numpy as np
from image import Image


def resized(img, width, height):
    sw, sh = img.size
    xmap = np.floor((np.arange(width) + 0.5) * sw / float(width)).astype(int)
    ymap = np.floor((np.arange(height) + 0.5) * sh / float(height)).astype(int)
    return Image(data = img.data[ymap,:][:,xmap])

def blurred(img, level=10):
    """
    Apply a gaussian blur on the specified image. Returns a new blurred image.
    Level is the level of blurring and should be an integer between 0 and 20

    Based on a Scipy lecture example from https://github.com/scipy-lectures/scipy-lecture-notes
    Licensed under Creative Commons Attribution 3.0 United States License
    (CC-by) http://creativecommons.org/licenses/by/3.0/us
    """
    level = int(level)
    if level > 20:
        level = 20
    elif level < 0:
        level = 0

    # prepare an 1-D Gaussian convolution kernel
    dist = 21 - level
    kernelSize = 30
    t = np.linspace(-dist, dist, kernelSize)
    bump = np.exp(-0.1*t**2)
    bump /= np.trapz(bump) # normalize the integral to 1
    padSize = int(kernelSize/2)
    paddedShape = (img.data.shape[0] + padSize, img.data.shape[1] + padSize)

    # make a 2-D kernel out of it
    kernel = bump[:,np.newaxis] * bump[np.newaxis,:]

    # padded fourier transform, with the same shape as the image
    kernel_ft = np.fft.fft2(kernel, s=paddedShape, axes=(0, 1))

    # convolve
    img_ft = np.fft.fft2(img.data, s=paddedShape, axes=(0, 1))
    img2_ft = kernel_ft[:,:,np.newaxis] * img_ft
    data = np.fft.ifft2(img2_ft, axes=(0, 1)).real

    # clip values to range
    data = np.clip(data, 0, 255)

    return Image(data = data[padSize:data.shape[0], padSize:data.shape[1], :])

def getAlpha(img):
    return Image(data = self._data[:,:,-1:])

def getChannel(img, channel):
    return Image(data = img.data[:,:,(channel-1):channel])
