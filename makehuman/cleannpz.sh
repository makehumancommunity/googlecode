#!/bin/bash

##
# Clean up any remaining .npz files.
##

find . -type f -iname \*.npz -exec rm -rf {} \;
