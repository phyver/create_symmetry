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
- generate random (or not) patterns for the 14 spherical symmetry groups, in "3D" form or stereographic projection (this includes the different rosette types),
- generate random (or not) pattern for the 7 frieze pattern types,
- generate random (or not) hyperbolic patterns based on the modular group, as described in Farris' book,
- generate one kind of "morphing" wallpaper pattern.

You cannot generate automatically the color-turning wallpaper patterns...


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

### Colorwheel

The "Colorwheel" frame contains a thumbnail of the current colorwheel image
file. The coordinates of the corners are given below. Axes are added to
visualize the origin, and a gray circle is added to see the unit circle.

If a pixel falls outside the image, the "default color" is used instead.

You can switch between the current file and the previous one by double
clicking anywhere on the thumbnail.

You can also choose a different spot for the origin by right clicking on the
thumbnail.

The "transformation" frame allows to easily zoom in / out or rotate the
colorwheel.

The "colorwheel" menu has one additional item: "stretch unit disk". This
corresponds to the transformation given in Farris' book: the unit disk in the
colorwheel is stretch to infinity. Part of the corresponding colorwheel is
show in the thumbnail. (Note that it is not possible to modify the coordinates
of the corners while the colorwheel is stretched.)


### Output


### Pattern


### Log and messages



## Contact

Pierre Hyvernat

pierre.hyvernat@univ-smb.fr

http://lama.univ-savoie.fr/~hyvernat


## Licence

GPL3

