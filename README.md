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
- generate random (or not) patterns for the 14 spherical symmetry groups,

You cannot generate automatically the color-turning wallpaper patterns: you'll
need to input the transformation matrix and enforce the corresponding recipes
by hand.

Exemples of images for the 17 wallpaper groups and 14 spherical groups can be
seen here: http://www.lama.univ-savoie.fr/~hyvernat/symetries.php (the page is
in French, but the pictures are not...)


## System Requirements

This program is written in Python3, using the following additional libraries:

- numpy and numexpr, for efficient computation on large arrays,
- pillow, for efficient image generation.

You cannot run the program without them.

On a Debian / Ubuntu system, the following should be enough:
```console
$ sudo apt install python3 python3-tk python3-pil python3-pil.imagetk python3-numpy python3-numexpr
```
If you use ``pip`` for python packages, 
```console
$ pip3 install numpy numexpr pillow --user
```
or if you want to install them globally,
```console
$ sudo pip3 install numpy numexpr pillow
```


## Description

### Colorwheel

The "Colorwheel" frame contains a thumbnail of the current colorwheel image
file. The coordinates of the corners are given below. Axes are added to
visualize the origin, and a gray circle is added to visualize the unit circle.

If a pixel falls outside the image, the "default color" is used instead.

You can switch between the current colorwheel file and the previous one by
double clicking anywhere on the thumbnail.

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

#### Preview window

The main part of the "Output" part is the preview window, displaying a preview
of the current transformation on the current colorwheel. This preview is
updated whenever the "preview" button is pressed.

Below this preview window are some buttons that allows to display some visual
information about the current wallpaper pattern: the tile border, the
different components of the orbifold (rotation centers, symmetry centers and
glide symmetries).

It is also possible to choose a smaller preview size, which can be useful when
testing computationally expensive transformations.


#### geometry and other options

The "geometry" tab allows to choose the part of the plane to display. The
transformation frame makes it easy to rotate or zoom in / out without changing
the corners: the image is multiplied by "m (cos(alpha) + i sin(alpha))" as a
final step.


#### Output options

This is where the size, filename and save directory for final images can be
configured.



### Pattern

The "Pattern" frame contains the transformation used to generate the image.
The left part allows to chose the kind of symmetry to enforce (either planar
or spherical).

For planar symmetries, the "color symmetry group" is used to generate "color
reversing" patterns. (In this case, the colorwheel image needs to be color
reversing!) It should be left empty for "normal" patterns.

The general, rhombic and rectangular patterns are parametrized by additional
numerical parameters.

The "Matrix" part contains the matrix representation of the current
transformation. Individual entries can be input with
```
i, j : z
```
where ``i`` and ``j`` are integers, and ``z`` is a complex number.

The "make matrix" button adds the relevant symmetries (depending on the
current pattern) to the matrix.


The right side of this frame contains parameters for random generation of
matrices.


### Log and messages

The bottom left corner contains log messages and can mostly be ignored.

## Shortcuts

The following shortcuts are available:

- Control-q     quit

- Control-p     compute and display preview
- Control-s     compute and save result to file
- Control-S     save current preview to file

- Control-n     add noise to matrix
- Control-N     add noise to matrix and display preview

- Control-g     generate random matrix
- Control-G     generate random matrix and display preview

- Control--     zoom out the result file and display preview
- Control-+     zoom in the result file and display preview

- Control-0     reset geometry of output and display preview

- Control-Up    translate the result and display preview
- Control-Down  (for spherical patterns, rotate instead)
- Control-Right
- Control-Left

- Control-z     rotate around z-axis
- Control-Z     (for spherical patterns)

- Control-u     undo: go back to previous state
- Control-r     redo
- Control-U     undo: go back to previous state and compute preview
- Control-R     redo



## Contact

Pierre Hyvernat

pierre.hyvernat@univ-smb.fr

http://www.lama.univ-smb.fr/~hyvernat


## Licence

GPL3

