# create_symmetry, a Python implementation of Frank Farris' recipes

## Overview

This Python program was written to experiment with Frank Farris'
(http://math.scu.edu/~ffarris/) way of generating wallpaper patterns using
"wave functions" and an arbitrary colorwheel.

This is described in details in his book "Creating Symmetry, The Artful
Mathematics of Wallpaper Patterns", which I recommend!

With this program, you can

- generate random (or not) patterns for the 17 planar wallpaper groups
- generate random (or not) pattern for the 46 planar color-reversing wallpaper groups
- generate random (or not) patterns for the 14 spherical symmetry groups, in "3D" form or stereographic form (this includes the 7 frieze pattern types and the different rosette types),
- generate random (or not) hyperbolic patterns based on the modular group, as described in Farris' book.

You cannot generate automatically the color-turning wallpaper patterns
(because I am not so much interested by them at the moment)...


## System Requirements

This program is written in Python3, using the following additional libraries:

- numpy, for efficient computation on large arrays,
- pillow, for efficient image generation.

You cannot run the program without them.

On a Debian / Ubuntu system, the following should be enough:
```console
$ sudo apt-get install python3-pillow python3-numpy python3-tk
```

## Description




## Contact

Pierre Hyvernat

pierre.hyvernat@univ-smb.fr

http://lama.univ-savoie.fr/~hyvernat


## Licence

GPL3

