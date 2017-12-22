#!/usr/bin/env python3

###
# imports
# <<<1

# misc functions
import copy
import getopt
import sys
import os
import os.path
from itertools import product
import re
import json
from ast import literal_eval

# math
from cmath import exp
from math import sqrt, pi, sin, cos, asin, atan2, ceil
from random import randrange, uniform, shuffle, seed

# multiprocessing
from multiprocessing import Process, Queue
import queue

# Tkinter for GUI
from tkinter import *
from tkinter.ttk import Combobox, Notebook, Style
import tkinter.font
from tkinter import filedialog, messagebox

# vectorized arrays
import numpy as np
import numexpr as ne

# image manipulation (Pillow)
import PIL
from PIL import ImageDraw
import PIL.ImageTk
from PIL.ImageColor import getrgb

# >>>1

###
# default configuration options
# <<<1
# colorwheel
COLOR_GEOMETRY = (-1, 1, -1, 1)
DEFAULT_COLOR = "black"

# output
OUTPUT_GEOMETRY = (-1.5, 1.5, -1.5, 1.5)
SPHERE_ROTATIONS = (15, 0, 0)
TRANSLATION_INVERSION_DELTA = 0.1
TRANSLATION_DELTA = 0.1
ROTATION_DELTA = 1
ZOOM_FACTOR = 2**(1/4)
INVERSION_CENTER = complex(-1/2, sqrt(3)/2)
OUTPUT_SIZE = (800, 800)
FILENAME_TEMPLATE = "output-{type:}-{name:}.{nb:}"

###
# misc options

# color of background for sphere / hyperbolic patterns
DEFAULT_BACKGROUND = "#000066"

# color of random pixels ("stars") for sphere patterns
STAR_COLOR = "#FFC"
NB_STARS = 500
FADE_COEFF = 200

# misc GUI options
COLOR_SIZE = 180            # size of colorwheel image in GUI
PREVIEW_SIZE = 400          # size of preview image in GUI
STRETCH_DISPLAY_RADIUS = 5  # how much of the "stretched" colorwheel to display
UNDO_SIZE = 100             # size of undo stack

# process images using blocks of that many pixels (0 => process everything at
# once)
BLOCK_SIZE = 2000

# keep a random seed to display random pixels in sphere images. The pixels
# should always be at the same place during a run of the program to prevent
# "jumps" during translatiosn / rotations of the image
RANDOM_SEED = uniform(0, 1)
# >>>1

###
# recipes and related informations
# <<<1
PATTERN = {         # <<<2
    # the 17 wallpaper groups   <<<3
    'o': {
        "alt_name": "p1",
        "recipe": "",
        "parity": "",
        "type": "plane group",
        "description": "general lattice",
        # OK
    },
    '2222': {
        "alt_name": "p2",
        "recipe": "n,m = -n, -m",
        "parity": "",
        "type": "plane group",
        "description": "general lattice",
        # OK
    },
    '*×': {
        "alt_name": "cm",
        "recipe": "n,m = m,n",
        "parity": "",
        "type": "plane group",
        "description": "rhombic lattice",
        # OK
    },
    '2*22': {
        "alt_name": "cmm",
        "recipe": "n,m = m,n = -n,-m = -m,-n",
        "parity": "",
        "type": "plane group",
        "description": "rhombic lattice",
        # OK
    },
    '**': {
        "alt_name": "pm",
        "recipe": "n,m = n,-m",
        "parity": "",
        "type": "plane group",
        "description": "rectangular lattice",
        # OK
    },
    '××': {
        "alt_name": "pg",
        "recipe": "n,m = -{n}(n,-m)",
        "parity": "",
        "type": "plane group",
        "description": "rectangular lattice",
        # OK
    },
    '*2222': {
        "alt_name": "pmm",
        "recipe": "n,m = -n,-m = -n,m = n,-m",
        "parity": "",
        "type": "plane group",
        "description": "rectangular lattice",
        # OK
    },
    '22*': {
        "alt_name": "pmg",
        "recipe": "n,m = -n,-m = -{n}(n,-m) = -{n}(-n,m)",
        "parity": "",
        "type": "plane group",
        "description": "rectangular lattice",
        # OK
    },
    '22×': {
        "alt_name": "pgg",
        "recipe": "n,m = -n,-m = -{n+m}(n,-m) = -{n+m}(-n,m)",
        "parity": "",
        "type": "plane group",
        "description": "rectangular lattice",
        # OK
    },
    '442': {
        "alt_name": "p4",
        "recipe": "n,m = m,-n = -n,-m = -m,n",
        "parity": "",
        "type": "plane group",
        "description": "square lattice",
        # OK
    },
    '*442': {
        "alt_name": "p4m",
        "recipe": "n,m = m,-n = -n,-m = -m,n ; n,m = m,n",
        "parity": "",
        "type": "plane group",
        "description": "square lattice",
        # OK
    },
    '4*2': {
        "alt_name": "p4g",
        "recipe": "n,m = m,-n = -n,-m = -m,n ; n,m = -{n+m}(m,n)",
        "parity": "",
        "type": "plane group",
        "description": "square lattice",
        # OK
    },
    '333': {
        "alt_name": "p3",
        "recipe": "n,m = m,-n-m = -n-m,n",
        "parity": "",
        "type": "plane group",
        "description": "hexagonal lattice",
        # OK
    },
    '3*3': {
        "alt_name": "p31m",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = m,n",
        "parity": "",
        "type": "plane group",
        "description": "hexagonal lattice",
        # OK
    },
    '*333': {
        "alt_name": "p3m1",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -m,-n",
        "parity": "",
        "type": "plane group",
        "description": "hexagonal lattice",
        # OK
    },
    '632': {
        "alt_name": "p6",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -n,-m",
        "parity": "",
        "type": "plane group",
        "description": "hexagonal lattice",
        # OK
    },
    '*632': {
        "alt_name": "p6m",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = m,n = -n,-m = -m,-n",
        "parity": "",
        "type": "plane group",
        "description": "hexagonal lattice",
        # OK
    },      # >>>3

    # the 47 color reversing wallpaper groups       <<<3
    ('o', 'o'): {
        "alt_name": "",
        "recipe": "",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "general lattice",
        # OK
    },
    ('2222', 'o'): {
        "alt_name": "",
        "recipe": "n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "general lattice",
        # OK
    },
    ('*×', 'o'): {
        "alt_name": "",
        "recipe": "n,m = -(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rhombic lattice",
        # OK
    },
    ('**', 'o'): {
        "alt_name": "",
        "recipe": "n,m = -(n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK
    },
    ('××', 'o'): {
        "alt_name": "",
        "recipe": "n,m = -{n+1}(n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK
    },
    ('2222', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -n,-m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "general lattice",
        # OK
    },
    ('2*22', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -(m,n) ; n,m = -n,-m",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rhombic lattice",
        # OK
    },
    ('*2222', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -(-n,m) ; n,m = -n,-m",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rectangular lattice with positive half turn",
        # OK
    },
    ('22*', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -{m+1}(-n,m) ; n,m = -n,-m",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rectangular lattice with positive half turn",
        # OK        NOTE: there is a typo in Farris' book
    },
    ('22×', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -{1+n+m}(-n, m) ; n,m = -n,-m",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rectangular lattice with positive half turn",
        # OK        NOTE: there is a typo in Farris' book
    },
    ('442', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -(-m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "square lattice with negating center",
        # OK
    },
    ('2*22', '*×'): {
        "alt_name": "",
        "recipe": "n,m = -(m,n) ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rhombic lattice",
        # OK
    },
    ('**', '*×'): {
        "alt_name": "",
        "recipe": "n,m = m,n",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rhombic lattice",
        # OK
    },
    ('*2222', '2*22'): {
        "alt_name": "",
        "recipe": "n,m = m,n ; n,m = -n,-m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rhombic lattice",
        # OK
    },
    ('*442', '2*22'): {
        "alt_name": "",
        "recipe": "n,m = -(-m,n) ; n,m = m,n",
        "parity": "",
        "type": "color reversing plane group",
        "description": "square lattice with negating center",
        # OK
    },
    ('4*2', '2*22'): {
        "alt_name": "",
        "recipe": "n,m = -(-m,n) ; n,m = -{n+m}(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "square lattice with negative center",
        # OK
    },
    ('*×', '**'): {
        "alt_name": "",
        "recipe": "n,m = n,-m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK
    },
    ('**₁', '**'): {
        "alt_name": "",
        "recipe": "n,m = n,-m",
        "parity": "m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK
    },
    ('**₂', '**'): {
        "alt_name": "",
        "recipe": "n,m = -n,m",
        "parity": "m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK (the axis of symmetry are the same, only the size of the basic
        # tile changes
    },
    ('*2222', '**'): {
        "alt_name": "",
        "recipe": "n,m = n,-m ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK
    },
    ('22*', '**'): {
        "alt_name": "",
        "recipe": "n,m = -{m+1}(-n,m) ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK
    },
    ('*×', '××'): {
        "alt_name": "",
        "recipe": "n,m = -{n}(n,-m)",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK
    },
    ('**', '××'): {
        "alt_name": "",
        "recipe": "n,m = -{n}(n,-m)",
        "parity": "n = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK
    },
    ('××', '××'): {
        "alt_name": "",
        "recipe": "n,m = -{m}(-n,m)",
        "parity": "n = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK
    },
    ('22*', '××'): {
        "alt_name": "",
        "recipe": "n,m = -{n}(n,-m) ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK
    },
    ('22×', '××'): {
        "alt_name": "",
        "recipe": "n,m = -{n+m}(-n,m) ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "rectangular lattice without positive half turn",
        # OK
    },
    ('2*22', '*2222'): {
        "alt_name": "",
        "recipe": "n,m = -n,m ; n,m = -n,-m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice with positive half turn",
        # OK
    },
    ('*2222', '*2222'): {
        "alt_name": "",
        "recipe": "n,m = -n,m ; n,m = -n,-m",
        "parity": "n = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice with positive half turn",
        # OK
    },
    ('*442', '*2222'): {
        "alt_name": "",
        "recipe": "n,m = -(-m,n) ; n,m = -(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "square lattice with negating center",
        # OK
    },
    ('2*22', '22*'): {
        "alt_name": "",
        "recipe": "n,m = -{n}(n,-m) ; n,m = -n,-m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice with positive half turn",
        # OK
    },
    ('*2222', '22*'): {
        "alt_name": "",
        "recipe": "n,m = -{n}(n,-m) ; n,m = -n,-m",
        "parity": "n = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice with positive half turn",
        # OK
    },
    ('22*', '22*'): {
        "alt_name": "",
        "recipe": "n,m = -{n}(n,-m) ; n,m = -n,-m",
        "parity": "m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice with positive half turn",
        # OK
    },
    ('2*22', '22×'): {
        "alt_name": "",
        "recipe": "n,m = -{n+m}(-n,m) ; n,m = -n,-m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice with positive half turn",
        # OK
    },
    ('22*', '22×'): {
        "alt_name": "",
        "recipe": "n,m = -{n+m}(-n,m) ; n,m = -n,-m",
        "parity": "n = 1 mod 2",
        "type": "color reversing plane group",
        "description": "rectangular lattice with positive half turn",
        # OK
    },
    ('4*2', '22×'): {
        "alt_name": "",
        "recipe": "n,m = -(-m,n) ; n,m = -{1+n+m}(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "square lattice with negative center",
        # OK
    },
    ('442', '442'): {
        "alt_name": "",
        "recipe": "n,m = -m,n",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "square lattice with positive center",
        # OK
    },
    ('*442', '442'): {
        "alt_name": "",
        "recipe": "n,m = -m,n ; n,m = -(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "square lattice with positive center",
        # OK
    },
    ('4*2', '442'): {
        "alt_name": "",
        "recipe": "n,m = -m,n ; n,m = -{n+m+1}(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "square lattice with positive center",
        # OK
    },
    ('*442', '*442'): {
        "alt_name": "",
        "recipe": "n,m = -m,n ; n,m = m,n",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "square lattice with positive center",
        # OK
    },
    ('*442', '4*2'): {
        "alt_name": "",
        "recipe": "n,m = -m,n ; n,m = -{n+m}(m,n)",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "square lattice with positive center",
        # OK
    },
    ('3*3', '333'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "hexagonal lattice, 3-fold symmetry",
        # OK
    },
    ('*333', '333'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -(-m,-n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "hexagonal lattice, 3-fold symmetry",
        # OK
    },
    ('632', '333'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "hexagonal lattice, 3-fold symmetry",
        # OK
    },
    ('*632', '3*3'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = m,n ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "hexagonal lattice, 6-fold symmetry",
        # OK
    },
    ('*632', '*333'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -m,-n ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "hexagonal lattice, 6-fold symmetry",
        # OK
    },
    ('*632', '632'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -n,-m ; n,m = -(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "hexagonal lattice, 6-fold symmetry",
        # OK
    },          # >>>3

    # the 14 spherical symmetry groups      <<<3
    '332': {
        "alt_name": "T",
        "recipe": "n,m = -n,-m",
        "parity": "n-m = 0 mod 2",
        "type": "sphere group",
        "description": "tetrahedral symmetry",
    },
    '432': {
        "alt_name": "O",
        "recipe": "n,m = -n,-m",
        "parity": "n-m = 0 mod 4",
        "type": "sphere group",
        "description": "octahedral symmetry",
    },
    '532': {
        "alt_name": "I",
        "recipe": "n,m = -n,-m",
        "parity": "n-m = 0 mod 2",
        "type": "sphere group",
        "description": "icosahedral symmetry",
    },
    '3*2': {
        "alt_name": "Th",
        "recipe": "n,m = -n,-m ; n,m = -m,-n",
        "parity": "n-m = 0 mod 2",
        "type": "sphere group",
        "description": "tetrahedral symmetry",
    },
    '*332': {
        "alt_name": "Td",
        "recipe": "n,m = -n,-m ; n,m = i{n-m}(m,n)",
        "parity": "n-m = 0 mod 2",
        "type": "sphere group",
        "description": "tetrahedral symmetry",
    },
    '*432': {
        "alt_name": "Oh",
        "recipe": "n,m = -n,-m ; n,m = -m,-n",
        "parity": "n-m = 0 mod 4",
        "type": "sphere group",
        "description": "octahedral symmetry",
    },
    '*532': {
        "alt_name": "Ih",
        "recipe": "n,m = -n,-m ; n,m = -m,-n",
        "parity": "n-m = 0 mod 2",
        "type": "sphere group",
        "description": "icosahedral symmetry",
    },
    'NN': {
        "alt_name": "CN p111",
        "recipe": "",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "cyclic symmetry",
    },
    '22N': {
        "alt_name": "DN p211",
        "recipe": "n,m = -n,-m",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "dihedral symmetry",
    },
    '*NN': {
        "alt_name": "CNv p1m1",
        "recipe": "n,m = m,n",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "cyclic symmetry",
    },
    'N*': {
        "alt_name": "CNh p11m",
        "recipe": "n,m = -m,-n",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "cyclic symmetry",
    },
    '*22N': {
        "alt_name": "DNh p2mm",
        "recipe": "n,m = m,n = -n,-m = -m,-n",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "dihedral symmetry",
    },
    'N×': {
        "alt_name": "S2N p11g",
        "recipe": "n,m = -{n+m}(-m,-n)",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "cyclic symmetry",
    },
    '2*N': {
        "alt_name": "DNd p2mg",
        "recipe": "n,m = -n,-m = -{n+m}(-m,-n) = -{n+m}(m,n)",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "dihedral symmetry",
    },      # >>>3

    # the 7 frieze groups are generated from the corresponding cyclic spherical
    # groups
}

# transform all the appropriate cyclic sphere groups into frieze groups
_F = {}
for p in PATTERN:
    if PATTERN[p]["type"] == "sphere group" and "N" in p:
        fp = p.replace("N", "∞")
        _F[fp] = copy.deepcopy(PATTERN[p])
        _F[fp]["type"] = "frieze"
        _F[fp]["description"] = ""
        alt_name1, alt_name2 = PATTERN[p]["alt_name"].split()
        _F[fp]["alt_name"] = alt_name2
        PATTERN[p]["alt_name"] = alt_name1
PATTERN.update(_F)
del _F
# >>>2

# order of the groups in menus
NAMES = [       # <<<2
    # wallpaper groups
    "o",        # general lattice
    "2222",
    "*×",       # rhombic lattice
    "2*22",
    "**",       # rectangular lattice
    "××",
    "*2222",
    "22*",
    "22×",
    "442",      # square lattice
    "*442",
    "4*2",
    "333",      # hexagonal lattice
    "3*3",
    "*333",
    "632",
    "*632",
    # spherical groups
    "332",
    "*332",
    "3*2",
    "432",
    "*432",
    "532",
    "*532",
    "NN",
    "*NN",
    "N*",
    "N×",
    "22N",
    "*22N",
    "2*N",
]

# add names for frieze patterns
NAMES = NAMES + [p.replace("N", "∞") for p in NAMES if "N" in p]

# full names, with alternative names, for wallpaper groups
W_NAMES = ["{} ({})".format(p, PATTERN[p]["alt_name"])
           for p in NAMES
           if PATTERN[p]["type"] == "plane group"]
_t = None
for i in range(len(W_NAMES)):
    p = W_NAMES[i].split()[0]
    t = PATTERN[p]["description"].split()[0]
    if _t != t:
        W_NAMES[i] += "         -- {}".format(t)
    _t = t
del p

# full names, with alternative names, for sphere groups
S_NAMES = ["{} ({})".format(p, PATTERN[p]["alt_name"])
           for p in NAMES
           if PATTERN[p]["type"] == "sphere group"]
_t = None
for i in range(len(S_NAMES)):
    p = S_NAMES[i].split()[0]
    t = PATTERN[p]["description"].split()[0]
    if _t != t:
        S_NAMES[i] += "     -- {}".format(t)
    _t = t
del p
del _t

# full names, with alternative names, for frieze groups
F_NAMES = ["{} ({})".format(p, PATTERN[p]["alt_name"])
           for p in NAMES
           if PATTERN[p]["type"] == "frieze"]


# full names, with alternative names, for color reversing groups, as a function
# of the symmetry groups
def C_NAMES(s):
    r = []
    # we need to deal with the two groups for **/**
    names = copy.deepcopy(NAMES)
    k = NAMES.index("**")
    names.insert(k+1, "**₁")
    names.insert(k+2, "**₂")
    for p in names:
        if (p, s) in PATTERN:
            if p in ["**₁", "**₂"]:
                q = p[2]
                p = p[:2]
            else:
                q = ""
            r.append("{}{} ({}{})".format(p, q, PATTERN[p]["alt_name"], q))
    return r
# >>>2
# >>>1


###
# utility functions
# <<<1
class Error(Exception):     # <<<2
    """generic class for errors"""
    pass
# >>>2


def error(*args, **kwargs):     # <<<2
    """print message on stderr"""
    print("***", *args, file=sys.stderr, **kwargs)
# >>>2


def message(*args, **kwargs):       # <<<2
    """print message if verbosity is greater than 1"""
    print(*args, **kwargs)
# >>>2


def sequence(*fs):      # <<<2
    """return a function calling all the argument functions in sequence
    useful for running several functions in a callback
    """
    def res(*args):
        r = []
        for f in fs:
            r.append(f())
        if "break" in r:
            return "break"
    return res
# >>>2


def invert22(M):        # <<<2
    """invert a 2x2 matrix"""
    d = M[0][0] * M[1][1] - M[1][0] * M[0][1]
    I = [[M[1][1]/d, -M[0][1]/d],
         [-M[1][0]/d, M[0][0]/d]]
    return I
# >>>2


def matrix_mult(M1, M2):     # <<<2
    """matrix multiplication"""
    assert len(M1[0]) == len(M2)
    R = [[0]*len(M2[0]) for i in range(len(M1))]
    for i in range(len(M1)):
        for j in range(len(M2[0])):
            for k in range(len(M2)):
                R[i][j] += M1[i][k] * M2[k][j]
    return R
# >>>2


def rotation_matrix(x, y, z):       # <<<2
    """rotation matrix corresponding to the Euler-Tait angles
    ("yaw", "pitch" and "roll")
    see https://en.wikipedia.org/wiki/Euler_angles#Rotation_matrix
    """
    a = cos(x)*cos(y)
    b = cos(x)*sin(y)*sin(z) - cos(z)*sin(x)
    c = sin(x)*sin(z) + cos(x)*cos(z)*sin(y)
    d = cos(y)*sin(x)
    e = cos(x)*cos(z) + sin(x)*sin(y)*sin(z)
    f = cos(z)*sin(x)*sin(y) - cos(x)*sin(z)
    g = -sin(y)
    h = cos(y)*sin(z)
    i = cos(y)*cos(z)
    return [[a, b, c], [d, e, f], [g, h, i]]
# >>>2


def tait_angle(R):                  # <<<2
    """compute the Euler-Tait angles from a rotation matrix
    see http://stackoverflow.com/questions/18433801/converting-a-3x3-matrix-to-euler-tait-bryan-angles-pitch-yaw-roll
    """
    theta_z = atan2(R[2][1], R[2][2])
    theta_y = -asin(R[2][0])
    theta_x = atan2(R[1][0], R[0][0])
    return theta_x, theta_y, theta_z
# >>>2


def str_to_floats(s):       # <<<2
    """transform a string into a list of floats"""
    try:
        if s.strip() == "":
            return []
        else:
            s = re.sub("[,;]", " ", s)
            return list(map(float, s.split()))
    except:
        raise ValueError("str_to_floats: '{}' is not a list of floats"
                         .format(s))
# >>>2


def float_to_str(x):       # <<<2
    """transform a float into a string, removing trailing decimal 0s
    and decimal points if possible
    """
    s = str(x)
    if "." in s:
        s = re.sub("0*\s*$", "", s)
    s = s.rstrip(".")
    if s == "":
        s = "0"
    return s
# >>>2


def floats_to_str(l):       # <<<2
    """transform a list of floats into a string"""
    return ", ".join(map(float_to_str, l))
# >>>2


def str_to_complex(s):      # <<<2
    """transform a string into a complex number"""
    s = re.sub("\s*", "", s)
    s = s.replace("i", "j")
    return complex(s)
# >>>2


def complex_to_str(z, precision=16):    # <<<2
    """transform a complex number into a string"""
    if z == 0:
        return "0"
    elif z == z.real:
        x = "{x:.{prec:}f}".format(x=z.real, prec=precision)
        x = float_to_str(x)
        return x
    elif z == z - z.real:
        y = "{y:.{prec:}f}".format(y=z.imag, prec=precision)
        y = float_to_str(y)
        y = "" if y == "1" else y
        return y + "i"
    else:
        sign = "+" if z.imag > 0 else "-"
        x = "{x:.{prec:}f}".format(x=z.real, prec=precision)
        x = float_to_str(x)
        # x = x.rjust(precision + 3)
        y = "{y:.{prec:}f}".format(y=abs(z.imag), prec=precision)
        y = float_to_str(y)
        y = "" if y == "1" else y
        return "{} {} {}i".format(x, sign, y)
# >>>2


def matrix_to_list(M):      # <<<2
    """transform a "matrix" (ie a dictionnary with pairs of integers as keys
    and complex numbers as values) into a list of pairs of pairs:
        - the pair of integers of the key
        - the real and imaginary parts of the value
    This is used as preprocessing before transforming the matrix to JSON.
    """
    try:
        return [((n, m), (z.real, z.imag)) for (n, m), z in M.items()]
    except:
        return M
# >>>2


def list_to_matrix(L):      # <<<2
    """transform a list of pairs of pairs into a matrix:
        - the first pairs are integers
        - the second pairs are floats (real and imaginary parts)
    This is used as postprocessing after getting the matrix from JSON.
    """
    try:
        return dict([((n, m), complex(x, y)) for ((n, m), (x, y)) in L])
    except:
        return L
# >>>2


def parse_matrix(s):        # <<<2
    """parse a string and return the corresponding matrix"""
    # ugly, but works
    s = s.strip(" {}")
    tmp = re.split("\s*(?:[,;:]|(?:[-=]>))\s*", s)
    M = {}
    for i in range(0, len(tmp), 3):
        n, m, e = tmp[i:i+3]
        n = n.strip(" ()")
        m = m.strip(" ()")
        M[(int(n), int(m))] = complex(e)
    return M
# >>>2


def is_rgb(s):  # <<<2
    """check if a string is a color"""
    try:
        getrgb(s)
        return True
    except:
        return False
# >>>2


def random_matrix(nb_coeffs, min_degre=-3, max_degre=3, modulus=1):    # <<<2
    """generate a random complex matrix"""
    coeffs = list(product(range(min_degre, max_degre+1),
                          range(min_degre, max_degre+1)))
    shuffle(coeffs)
    coeffs = coeffs[:nb_coeffs]
    M = {}
    for (n, m) in coeffs:
        mod = uniform(0, modulus) / nb_coeffs
        angle = uniform(0, 2*pi)
        M[(n, m)] = mod * complex(cos(angle), sin(angle))
    return M
# >>>2


def eqn_indices(eq, n, m):        # <<<2
    """return a list of (s, (j, k))
        - eq is a string representing a list of equations involving "n" and "m"
        - n and m are integers
    for eq = "n,m = -n,m = -{n+m}(m,n)" and n = 7 and m = 4, the result will be
    [ (1, (7, 4)), (1, (-7, 4)), (-1, (4, 7)) ]
    """
    eq = eq.strip()

    if eq == "":
        return [(1, (n, m))]

    try:
        res = []
        l = map(lambda s: s.strip(), eq.split("="))

        for snm in l:
            if re.match("^[-nm, ]*$", snm):
                nm = snm.replace("n", str(n)).replace("m", str(m))
                res.append((1, literal_eval(nm)))
            else:
                # print("snm", snm)
                _r = re.match("^([-i])([-{n+m1} ]*)(\(.*\))$", snm)
                s = _r.group(1)
                # print("s = '{}'".format(s))
                e = _r.group(2)
                # print("e = '{}'".format(e))
                e = e.replace("{", "").replace("}", "")
                e = e.replace("n", str(n)).replace("m", str(m))
                nm = _r.group(3)
                # print("nm = '{}'".format(nm))
                nm = nm.replace("n", str(n)).replace("m", str(m))
                if s == "-":
                    s = -1
                elif s == "i":
                    s = 1j
                if e == "":
                    e = "1"
                e = s**(literal_eval(e))
                res.append((e, literal_eval(nm)))
    except Exception as e:
        raise Error("cannot compute indices for recipe '{}': {}"
                    .format(eq, e))

    # print("for {}, {}, {} got {}".format(eq, n, m, res))
    return res
# >>>2


def recipe_all_indices(recipe, n, m):   # <<<2
    """BFS like algorithm to compute all the related indices to n and m
        - recipe is a string containing a list of equations, like
            "n,m = -n,m  ; n,m = -m,-n = -{n}(n, m)"
    the result will contain all the related indices, removing any indices that
    leads to a contradiction
    """
    R = {}
    todo = set([(1, (n, m))])
    bad = set([])
    while todo:
        s, (n, m) = todo.pop()
        if (n, m) in bad:
            continue
        if (n, m) in R:
            if R[n, m] != s:
                bad.add((n, m))
            else:
                continue
        R[(n, m)] = s
        for eq in recipe.split(";"):
            for t, (j, k) in eqn_indices(eq, n, m):
                todo.add((s*t, (j, k)))
    L = []
    for n, m in R:
        if (n, m) not in bad:
            L.append((R[(n, m)], (n, m)))
    return L
# >>>2


def check_matrix_recipe(M, recipe):     # <<<2
    """check if a matrix agrees with a recipe"""
    for eq in map(lambda s: s.strip(), recipe.split(";")):
        for n, m in M:
            coeff = None
            for s, (j, k) in eqn_indices(eq, n, m):
                if coeff is None:
                    coeff = s * M[(j, k)]
                else:
                    if M.get((j, k)) != coeff / s:
                        print("PROBLEM: matrix doesn't obey recipe '{}'"
                              .format(recipe))
                        print("         got {} for ({},{}), expected {}"
                              .format(M.get((j, k)), j, k, coeff/s))
                        return False
    return True
# >>>2


def apply_parity(parity, M):    # <<<2
    """remove all entries of the matrix that do not agree with the parity rule
        - parity is a string of the form "n+m = 3 mod 7"
    """
    parity = parity.strip()
    if parity == "":
        return M

    r = re.match("^([-+nm ()0-9]*)\s*==?\s*([0-9]+)\s*mod\s*([0-9]+)",
                 parity)
    if r:
        modulo = int(r.group(3))
        equal = int(r.group(2))
        parity = r.group(1)
    elif re.match("^[-+nm 0-9]*$", parity):
        modulo = 2
        equal = 1
    else:
        assert False

    R = {}
    for (n, m) in M.keys():
        s = parity.replace("n", str(n)) .replace("m", str(m))
        if literal_eval(s) % modulo == equal:
            R[n, m] = M[n, m]
    return R
# >>>2


def add_symmetries(M, recipe, parity=""):      # <<<2
    """return a matrix computed from M by adding symmetries given by recipe
    recipe can be of the form "n,m = -n,-m = -(m,n) ; n,m = -{n+m}(n,m)"...
    """
    M = apply_parity(parity, M)

    R = {}
    for n, m in M:
        if (n, m) in R:
            continue
        indices = recipe_all_indices(recipe, n, m)
        coeffs = [M[nm]/s for (s, nm) in indices if nm in M]
        if len(coeffs) != 0:
            coeff = sum(coeffs) / len(indices)
            # coeff = sum(coeffs) / len(coeffs)
            if coeff != 0:
                for s, nm in indices:
                    R[nm] = s * coeff

    assert R == apply_parity(parity, R)

    assert check_matrix_recipe(R, recipe)

    return R
# >>>2


def basis(pattern, *params):        # <<<2
    """return the matrix for the basis of the wallpaper pattern, using
    arguments from params if necessary (see Farris)"""
    if pattern == "hyperbolic":
        return None
    lattice = PATTERN[pattern]["description"].split()[0]
    if lattice == "general":
        try:
            return [[params[0], params[1]], [params[2], params[3]]]
        except:
            # FIXME: warning message
            return [[1, 1], [1, 0]]
    elif lattice == "rhombic":
        try:
            return [[1/2, params[0]/2], [1/2, -params[0]/2]]
        except:
            # FIXME: warning message
            return [[1/2, 1], [1/2, -1]]
    elif lattice == "rectangular":
        try:
            return [[1, 0], [0, 1/params[0]]]
        except:
            # FIXME: warning message
            return [[1, 0], [0, 1/2]]
    elif lattice == "square":
        return [[1, 0], [0, 1]]
    elif lattice == "hexagonal":
        return [[1, 0], [-1/2, sqrt(3)/2]]
    else:
        return None
# >>>2


def bezout(a, b):       # <<<2
    """Compute Bezout numbers,
    ie (u, v, p) st a*u + b*v = p and p = gcd(a, b)"""
    if a == 0 and b == 0:
        return (0, 0, 0)
    if b == 0:
        return (a//abs(a), 0, abs(a))
    (u, v, p) = bezout(b, a % b)
    return (v, (u - v*(a//b)), p)
# >>>2


def normalize_path(path):       # <<<2
    """normalize a path so that $HOME is portable across computers"""
    home = os.path.expanduser("~")
    path = os.path.expanduser(path)
    path = path.replace(home, "~")
    # print()
    return path
# >>>2


def fourrier_identity(degre):       # <<<2
    """Fourrier approximation of the identity function,
    with period (1,0) / (0,1)"""
    M = {}
    for n in range(1, degre+1):
        M[(n, 0)] = (-1)**(n+1) * -1j/abs(n*pi)
        M[(-n, 0)] = (-1)**(n+1) * 1j/abs(n*pi)
    for n in range(1, degre+1):
        M[(0, n)] = (-1)**(n+1) * 1/abs(n*pi)
        M[(0, -n)] = (-1)**(n+1) * -1/abs(n*pi)
    return M
# >>>2
# >>>1


###
# making an image from a transformation and a colorwheel
# <<<1
def make_coordinates_array(         # <<<2
        size=OUTPUT_SIZE,
        geometry=OUTPUT_GEOMETRY,
        modulus=1,
        angle=0,
        ):
    """compute the array of floating point numbers associated to each pixel"""
    rho = modulus * complex(cos(angle*pi/180), sin(angle*pi/180))

    x_min, x_max, y_min, y_max = geometry
    width, height = size
    delta_x = (x_max-x_min) / (width-1)
    delta_y = (y_max-y_min) / (height-1)

    xs = np.arange(width, dtype='float')
    ne.evaluate("delta_x*xs + x_min", out=xs)

    ys = np.arange(height, dtype='float')
    ne.evaluate("delta_y*ys - y_max", out=ys)

    zs = xs[:, None] + 1j*ys
    zs = ne.evaluate("zs / rho", out=zs)

    return zs
# >>>2


def plane_coordinates_to_sphere(zs, rotations=(0, 0, 0)):       # <<<2
    """transform an array of pixel values into an array of pixel values on the
    sphere
    the original array is taken as the stereographic projection of a sphere of
    radius 1 centered at the origin"""
    x = zs.real
    y = zs.imag
    with np.errstate(invalid='ignore'):
        z = np.sqrt(1 - x**2 - y**2)

    theta_x, theta_y, theta_z = rotations
    theta_x = theta_x * pi / 180
    theta_y = theta_y * pi / 180
    theta_z = theta_z * pi / 180
    R = rotation_matrix(theta_x, theta_y, theta_z)

    _x = R[0][0]*x + R[0][1]*y + R[0][2]*z
    _y = R[1][0]*x + R[1][1]*y + R[1][2]*z
    _z = R[2][0]*x + R[2][1]*y + R[2][2]*z

    zs = _x/(1-_z) + 1j*_y/(1-_z)
    return zs
# >>>2


def apply_color(                    # <<<2
        res,                        # the complex values
        filename,                   # image for the colorwheel image
        geometry=COLOR_GEOMETRY,    # coordinates of the colorwheel
        modulus="1",                # transformation to apply to the colorwheel
        angle="0",
        stretch=False,              # should we stretch the colorwheel
        color="black",              # default color if value is outside image
        morph_angle=False,          # should the result morph
        morph_start_angle=0,        # from one angle transformation
        morph_end_angle=180,        # to another
        morph_stable=20,            # and if so, how big (%) should the
        **_):                       # constant parts of the result be
    """replace each complex value in the array res by the color taken from an
    image in filename
    the resulting image is returned"""

    if isinstance(color, str):
        color = getrgb(color)

    if stretch:
        ne.evaluate("res / (sqrt(1 + res.real**2 * res.imag**2))", out=res)

    rho = modulus * complex(cos(angle*pi/180), sin(angle*pi/180))
    x_min, x_max, y_min, y_max = geometry

    tmp = PIL.Image.open(os.path.expanduser(filename))
    color_width, color_height = tmp.size
    delta_x = (x_max-x_min) / (color_width-1)
    delta_y = (y_max-y_min) / (color_height-1)

    # morphing
    if morph_angle:
        # print("morph from {} to {} ({}%)"
        #       .format(morph_start_angle, morph_end_angle, morph_stable))
        width = res.shape[0]
        morph = np.arange(0, width, dtype="complex128")

        if morph_stable >= 50:
            morph_stable = 50 - 1e-10
        x = 100*morph_stable / ((100-2*morph_stable)*width)
        ne.evaluate("-x + morph * (1+2*x) / width", out=morph)
        np.place(morph, morph < 0, 0)
        np.place(morph, morph > 1, 1)

        a1 = morph_start_angle
        a2 = morph_end_angle
        hundred_eighty = complex(180, 0)
        ne.evaluate("exp((a1 + morph * (a2 - a1))*1j*pi/hundred_eighty)", out=morph)
        np.multiply(morph[:, None], res, out=res)

    # we add a one pixel border to the top / right of the color image, using
    # the default color
    color_im = PIL.Image.new("RGB",
                             (color_width+1,
                              color_height+1),
                             color=color)
    color_im.paste(tmp, box=(1, 1))

    # TODO when hyperbolic pattern, ComplexWarning: Casting complex values to
    # real discards the imaginary part ???
    ne.evaluate("res/rho", out=res)

    # convert the ``res`` array into pixel coordinates
    xs = np.rint((res.real - x_min) / delta_x).astype(int)
    ys = np.rint((y_max - res.imag) / delta_y).astype(int)

    # increase all coordinates by 1: 0 will be used for pixels in the border
    # with ``color``
    ne.evaluate("xs+1", out=xs)
    ne.evaluate("ys+1", out=ys)

    # replace too big / too small values with 0, to get the ``color``
    np.place(xs, xs < 0, [0])
    np.place(xs, xs >= color_width, [0])
    np.place(ys, ys < 0, [0])
    np.place(ys, ys >= color_height, [0])

    res = np.dstack([xs, ys])

    # get array of pixels colors, and reshape the array to be 3 dimensional
    color = np.asarray(color_im).reshape(color_height+1, color_width+1, 3)

    # apply color to the pixel coordinates and convert to appropriate type
    # transpose the first two dimensions because images have [y][x] and arrays
    # have [x][y] coordinates
    res = color.transpose(1, 0, 2)[xs, ys].transpose(1, 0, 2)
    return PIL.Image.fromarray(np.array(res, dtype=np.uint8), "RGB")
# >>>2


def make_wallpaper_image(   # <<<2
        zs,                 # input coordinates
        matrix,             # transformation matrix
        pattern,            # name of pattern
        basis,              # additional parameters for basis
        N=1,                # additional forced symmetry
        color_pattern="",   # color reversing symmetry pattern
        message_queue=None,
        nb_blocks=1,
        nb_block=0):
    """use the given matrix to make an image for the given pattern
    the ``N`` parameter is used to enforce rotational symmetry around the
    origin but will usually destroy periodicity

    (the basis could be infered from the pattern in most cases)

    ``color_pattern`` is used to create color reversing wallpaper (the
    colorwheel file should then be symmetric)

    ``message_queue`` is used to keep track of progress
    """

    matrix = add_symmetries(
            matrix,
            PATTERN[pattern]["recipe"],
            parity=PATTERN[pattern]["parity"])

    B = invert22(basis)

    res = np.zeros(zs.shape, complex)

    w1, w2 = 1, len(matrix)*N
    for (n, m) in matrix:
        ZS = np.zeros(zs.shape, dtype="complex128")

        for k in range(0, N):
            rho = complex(cos(2*pi*k/N),
                          sin(2*pi*k/N))
            a, b = B[0][0], B[1][0]
            c, d = B[0][1], B[1][1]
            ne.evaluate("exp((n*(a*(rho*zs).real + b*(rho*zs).imag) +"
                        "     m*(c*(rho*zs).real + d*(rho*zs).imag))"
                        "    * 2j*pi) +"
                        "ZS", out=ZS)
            if message_queue is not None:
                message_queue.put(nb_block/nb_blocks+w1/(w2*nb_blocks))
            w1 += 1
        coeff = matrix[n, m]
        ne.evaluate("res + (ZS/N) * coeff", out=res)
    return res
# >>>2


def make_hyperbolic_image(      # <<<2
        zs,                     # input coordinates
        matrix=None,            # transformation matrix
        nb_steps=200,           # number of approximations steps to perform
        message_queue=None,
        s=5,                    # exponent for imaginary part (should have real part > 1)
        nb_blocks=1,
        nb_block=0):

    # ks = list(matrix.keys())
    # for n, m in ks:
    #     if m != 0:
    #         matrix[n, 0] = matrix[n, m]
    #         del matrix[n, m]
    # for n, m in ks:
    #     if n != 0:
    #         matrix[0, m] = matrix[n, m]
    #         del matrix[n, m]

    def PSL2():
        """generator for elements of the PSL2(Z),
        ie, quadruples (a, b, c, d) such that ad - bc = 1
        They are generated in order
            c+d = 1
            c+d = 2
            c+d = 3
            ...
        """
        total = 0
        c = 0
        while True:
            if c == total:
                c = 0
                total += 1
            else:
                c = c + 1
            d = total - c
            b, a, p = bezout(c, d)
            if p == 1:
                yield a, -b, c, d
                yield a, b, -c, d

    done = set([])
    res = np.zeros(zs.shape, dtype="complex128")
    c, d = 0, 0
    w1, w2 = 0, nb_steps*len(matrix)

    # A = np.zeros(res.shape, dtype="complex128")
    # B = np.zeros(res.shape, dtype="complex128")
    ZS = np.zeros(res.shape, dtype="complex128")
    for a, b, c, d in PSL2():
        if len(done) >= nb_steps:
            break
        if (c, d) in done or (-c, -d) in done:
            continue
        assert a*d - b*c == 1
        done.add((c, d))

        ne.evaluate("(a*zs + b) / (c*zs + d)", out=ZS)

        for n, m in matrix:
            coeff = matrix[n, m]
            ne.evaluate("res +"
                        "ZS.imag**s * coeff *"
                        "exp(2j*pi*(n*ZS.real + m*ZS.imag))",
                        out=res)
            w1 += 1
            if message_queue is not None:
                message_queue.put(nb_block/nb_blocks+w1/(w2*nb_blocks))
    return res
# >>>2


def make_sphere_image(      # <<<2
        zs,                 # input coordinates
        matrix,             # transformation matrix
        pattern,            # name of group
        N=5,                # parameter for cyclic groups
        unwind=False,       # should the result be in stereographic projection?
        message_queue=None,
        nb_blocks=1,
        nb_block=0):
    """use the given matrix to make an image for the given spherical pattern

    the ``N`` parameter is used for cyclic groups

    ``unwind`` is used to transform cyclic groups into frieze patterns

    ``message_queue`` is used to keep track of progress
    """

    recipe = PATTERN[pattern]["recipe"]
    parity = PATTERN[pattern]["parity"].replace("N", str(N))
    matrix = add_symmetries(matrix, recipe, parity)

    if unwind:
        ne.evaluate("exp(zs*1j)", out=zs)

    # choose the elements (rotations) on which to average
    if "T" in PATTERN[pattern]["alt_name"]:
        average = [([[1, 0], [0, 1]], 1), ([[1, 1j], [1, -1j]], 3)]
    elif "O" in PATTERN[pattern]["alt_name"]:
        average = [([[1, 0], [0, 1]], 1), ([[1, 1j], [1, -1j]], 3)]
    elif "I" in PATTERN[pattern]["alt_name"]:
        phi = (1 + sqrt(5)) / 2
        average = [([[1, 1j], [1, -1j]], 3),
                   ([[phi*(1-phi*1j), 1+2j],
                     [sqrt(5), phi*(1-phi*1j)]], 5)]
    else:
        average = [([[1, 0], [0, 1]], 1), ([[1, 0], [0, 1]], 1)]

    res = np.zeros(zs.shape, complex)
    [a, b], [c, d] = average[0][0]
    [e, f], [g, h] = average[1][0]
    w1, w2 = 0, average[0][1]*average[1][1]*len(matrix)
    for i in range(average[1][1]):
        for j in range(average[0][1]):
            zsc = np.conj(zs)
            for (n, m) in matrix:
                coeff = matrix[n, m]
                ne.evaluate("res + coeff * zs**n * zsc**m", out=res)
                if message_queue is not None:
                    message_queue.put(nb_block/nb_blocks+w1/(w2*nb_blocks))
                w1 += 1
            ne.evaluate("(a*zs + b) / (c*zs + d)", out=zs)
        ne.evaluate("(e*zs + f) / (g*zs + h)", out=zs)

    a = average[0][1] * average[1][1]
    ne.evaluate("res/a", out=res)
    return res
# >>>2


def make_sphere_background(     # <<<2
        geometry,
        modulus,
        angle,
        img,                    # the sphere image
        background="back.jpg",  # background: either a colorname or a filename
        fade=128,               # fade the background
        stars=0):               # how many random "stars" (pixels) to add
    """compute the background for a sphere
        - background can either be a color, or a filename containing an image
          to display
        - fade is used to fade the background (0: no fading, 255: black
          background)
        - stars is the number of random "stars" (pixels) to add to the
          background
      """
    zs = make_coordinates_array(img.size, geometry, modulus, angle)
    try:
        background_img = PIL.Image.open(background)
        background_img = background_img.resize((width, height))
    except Exception as e:
        try:
            color = getrgb(background)
            background_img = PIL.Image.new(
                mode="RGB",
                size=img.size,
                color=color
            )
            width, height = img.size
            for i in range(int(stars)):
                background_img.putpixel(
                    (randrange(0, width),
                     randrange(0, height)),
                    getrgb(STAR_COLOR)
                )
            rest = stars - int(stars)
            if uniform(0, 1) < rest:
                background_img.putpixel(
                    (randrange(0, width),
                     randrange(0, height)),
                    getrgb(STAR_COLOR)
                )

        except ValueError:
            background_img = PIL.Image.new(
                mode="RGB",
                size=(width, height),
                color=DEFAULT_BACKGROUND
            )

    mask = (zs.real**2 + zs.imag**2 > 1).astype(int).transpose(1, 0)

    mask_background = PIL.Image.fromarray(
        np.array(mask*fade, dtype=np.uint8),
        "L"
    )
    background_img.paste(0, mask=mask_background)

    mask_sphere = PIL.Image.fromarray(
        np.array(mask*255, dtype=np.uint8),
        "L"
    )
    img.paste(background_img, mask=mask_sphere)
    return img
# >>>2


def save_image(         # <<<2
        message_queue=None,
        image=None,
        **config
        ):
    """save an image to a file, and construct a shell script to invoke the
    program with the exact same parameters
    ``config`` should contain the whole configuration of the program
    """
    save_directory = config["output"]["save_directory"]
    filename_template = config["output"]["filename_template"]

    colorwheel = config["colorwheel"]
    output = config["output"]
    function = config["function"]

    if function["pattern_type"] == "wallpaper":
        if function["wallpaper_color_pattern"]:
            pattern = (function["wallpaper_color_pattern"],
                       function["wallpaper_pattern"])
        else:
            pattern = function["wallpaper_pattern"]
    elif function["pattern_type"] == "sphere":
        pattern = function["sphere_pattern"]
    elif function["pattern_type"] == "hyperbolic":
        pattern = "hyperbolic"

    # put the tile and / or orbifold into the image
    if ((output["draw_tile"] or output["draw_orbifold"]) and
            PATTERN[pattern]["type"] in ["plane group",
                                         "color reversing plane group"] and
            output["display_mode"] == "plain" and
            not output["morph"]):
        tile = make_tile(
            output["geometry"],
            (output["modulus"], output["angle"]),
            pattern,
            basis(pattern, *function["lattice_parameters"]),
            image.size,
            draw_tile=output["draw_tile"],
            draw_orbifold=output["draw_orbifold"],
            color_tile=output["draw_color_tile"],
            draw_mirrors=output["draw_mirrors"]
        )
        image.paste(tile, mask=tile)

    # build the filename
    function = config["function"]
    info = {"type": "", "name": "", "alt_name": ""}
    if function["pattern_type"] == "wallpaper":
        info["type"] = "planar"
        info["name"] = function["wallpaper_pattern"]
        info["alt_name"] = PATTERN[info["name"]]["alt_name"]
        cp = function["wallpaper_color_pattern"]
        if cp:
            info["name"] = cp + "_" + info["name"]
            info["alt_name"] = (PATTERN[cp]["alt_name"] +
                                "_" +
                                info["alt_name"])
    elif function["pattern_type"] == "sphere":
        info["type"] = "spherical"
        p = function["sphere_pattern"]
        N = function["sphere_N"]
        info["name"] = p.replace("N", str(N))
        info["alt_name"] = PATTERN[p]["alt_name"]
        info["alt_name"] = info["alt_name"].replace("N", str(N))
    elif function["pattern_type"] == "hyperbolic":
        info["type"] = "hyperbolic"
        info["name"] = "--"
        info["alt_name"] = "--"
    else:
        assert False
    info["nb"] = 1

    _filename = None
    while True:
        filename = filename_template.format(**info)
        filename = os.path.join(save_directory, filename)
        if (not os.path.exists(filename+".jpg") and
                not os.path.exists(filename+".sh")):
            break
        if filename == _filename:
            break
        _filename = filename
        info["nb"] += 1
    image.save(filename + ".jpg")
    if message_queue is not None:
        message_queue.put("saved file {}".format(filename+".jpg"))

    cfg = {
        "colorwheel": config["colorwheel"],
        "output": config["output"],
        "function": config["function"],
        "preview": True
    }
    config_file = open(filename + ".ct", mode="w")
    if "matrix" in cfg["function"]:
        cfg["function"]["matrix"] = matrix_to_list(cfg["function"]["matrix"])
    if "hyper_s" in cfg["function"]:
        cfg["function"]["hyper_s"] = str(cfg["function"]["hyper_s"])
    if "inversion_center" in cfg["output"]:
        cfg["output"]["inversion_center"] = complex_to_str(
            cfg["output"]["inversion_center"]
        )

    json.dump(cfg, config_file, indent=2)
    config_file.close()
# >>>2


def background_output(     # <<<2
        message_queue=None,
        output_message_queue=None,
        **config):
    """compute an image from the configuration in config, and save it to a file
    used by the GUI for output jobs"""

    # print("PID background_output", os.getpid())

    colorwheel = config["colorwheel"]
    output = config["output"]
    function = config["function"]

    image = make_image(
        color=colorwheel,
        output=output,
        function=function,
        message_queue=output_message_queue
    )

    if output["fade"]:
        image = fade_image(image)

    save_image(
        message_queue=message_queue,
        image=image,
        **config
    )
# >>>2


def make_image(     # <<<2
        color=None,             # configuration of colorwheel
        output=None,             # configuration of output
        function=None,          # configuration for function
        message_queue=None,
        block_size=BLOCK_SIZE):
    """compute an image for a pattern, cutting the output image into subimages
    if necessary"""

    seed(RANDOM_SEED)

    if block_size <= 0:
        return make_image_single_block(
            color=color,
            output=output,
            function=function,
            message_queue=message_queue,
            nb_blocks=1,
            nb_block=0)

    x_min, x_max, y_min, y_max = output["geometry"]
    delta_x = x_max - x_min
    delta_y = y_max - y_min

    width, height = output["size"]

    # print("{}x{} from ({},{}) to ({},{}), block size={}"
    #       .format(width, height,
    #               x_min, y_min, x_max, y_max,
    #               block_size))
    images = {}
    nb_blocks = ceil(height/block_size) * ceil(width/block_size)
    nb = 0
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            i = x//block_size
            j = y//block_size

            local_width = min(block_size, width-i*block_size)
            local_height = min(block_size, height-j*block_size)

            local_x_min = x_min + i * delta_x * block_size / width
            local_y_max = y_max - j * delta_y * block_size / height

            local_x_max = min(
                x_min + (i+1) * delta_x * block_size / width,
                x_max
            )
            local_y_min = max(
                y_max - (j+1) * delta_y * block_size / height,
                y_min
            )

            # print("bloc {}/{}: {},{}: {}x{} from ({},{}) to ({},{})"
            #       .format(nb, nb_blocks,
            #               i, j,
            #               local_width, local_height,
            #               local_x_min, local_y_min,
            #               local_x_max, local_y_max))

            local_output = copy.deepcopy(output)
            local_color = copy.deepcopy(color)
            local_function = copy.deepcopy(function)
            local_output["geometry"] = (local_x_min, local_x_max,
                                        local_y_min, local_y_max)
            local_output["size"] = (local_width, local_height)
            local_output["sphere_stars"] /= nb_blocks

            images[i, j] = make_image_single_block(
                color=local_color,
                output=local_output,
                function=local_function,
                message_queue=message_queue,
                nb_blocks=nb_blocks,
                nb_block=nb)
            nb += 1
    # print()

    img = PIL.Image.new("RGBA", (width, height), (255, 0, 0, 0))
    for i, j in images:
        img.paste(images[i, j], (i*block_size, j*block_size))

    seed()
    return img
# >>>2


def make_image_single_block(                 # <<<2
        color=None,             # configuration of colorwheel
        output=None,             # configuration of output
        function=None,          # configuration for function
        message_queue=None,
        nb_blocks=1,
        nb_block=0):
    """compute a subimage for a pattern"""

    if function["pattern_type"] == "wallpaper":
        if function["wallpaper_color_pattern"]:
            pattern = (function["wallpaper_color_pattern"],
                       function["wallpaper_pattern"])
        else:
            pattern = function["wallpaper_pattern"]
    elif function["pattern_type"] == "sphere":
        pattern = function["sphere_pattern"]
    elif function["pattern_type"] == "hyperbolic":
        pattern = "hyperbolic"

    zs = make_coordinates_array(
        output["size"],
        output["geometry"],
        output["modulus"],
        output["angle"]
    )

    if output["display_mode"] == "sphere":
        zs = plane_coordinates_to_sphere(zs, output["sphere_rotations"])
    elif output["display_mode"] == "inversion":
        x = output["inversion_center"].real
        y = -output["inversion_center"].imag

        # cf p 317 and 125 in Needlam (pdf 337 and 145)
        # zs = np.conj(zs)
        # zs = 2 / (zs + 1j) + 1j
        two = complex(2,0)
        ne.evaluate("(1j + two/(zs+1j) - x) * y", out=zs)

    if pattern == "hyperbolic":
        res = make_hyperbolic_image(
            zs,
            function["matrix"],
            nb_steps=function["hyper_nb_steps"],
            s=function["hyper_s"],
            message_queue=message_queue,
            nb_blocks=nb_blocks,
            nb_block=nb_block
        )
    elif PATTERN[pattern]["type"] in ["plane group",
                                      "color reversing plane group"]:
        res = make_wallpaper_image(
            zs,
            function["matrix"],
            pattern,
            basis(pattern, *function["lattice_parameters"]),
            N=function["wallpaper_N"],
            message_queue=message_queue,
            nb_blocks=nb_blocks,
            nb_block=nb_block
        )
    elif PATTERN[pattern]["type"] in ["sphere group", "frieze", "rosette"]:
        res = make_sphere_image(
            zs,
            function["matrix"],
            pattern,
            N=function["sphere_N"],
            unwind=function["sphere_mode"] == "frieze",
            message_queue=message_queue,
            nb_blocks=nb_blocks,
            nb_block=nb_block
        )
    else:
        # print(PATTERN[pattern]["type"])
        assert False

    img = apply_color(
        res, color["filename"],
        geometry=color["geometry"],
        modulus=color["modulus"],
        angle=color["angle"],
        stretch=color["stretch"],
        color=color["default_color"],
        morph_angle=output["morph"],
        morph_start_angle=output["morph_start"],
        morph_end_angle=output["morph_end"],
        morph_stable=output["morph_stable_coeff"],
    )

    if (output["display_mode"] in ["sphere", "inversion"]):
        return make_sphere_background(
            output["geometry"],
            output["modulus"],
            output["angle"],
            img,
            background=output["sphere_background"],
            fade=output["sphere_background_fading"],
            stars=output["sphere_stars"]
        )
    else:
        return img
# >>>2


# TODO: name all arguments???
def make_tile(geometry,         # <<<2
              transformation,
              pattern,
              basis,
              size,
              draw_tile=True,
              draw_orbifold=True,
              color_tile=False,
              draw_mirrors=False):
    """compute a transparent image with a tile and orbifold information
    this image can be added on top of a wallpaper image"""

    coeff = 4       # draw bigger tile and resize with antialiasing
    width = size[0]*coeff
    height = size[1]*coeff

    # translation of tile, necessary for some color-reversing tiles that are
    # not on the origin
    tile_translation = [0, 0]

    if isinstance(pattern, tuple):
        C = [[1, 0], [0, 1]]        # change of base matrix

        if pattern in [('o', 'o'), ('2222', '2222')]:
            if color_tile:
                C = [[1, 0], [1/2, 1/2]]
        elif pattern in [('2*22', '*×')]:
            if not color_tile:
                C = [[1, 0], [0, -1]]
        elif pattern in [('**', '*×'), ('*2222', '2*22'), ('2*22', '*2222'),
                         ('*×', '**'), ('2*22', '22×'),
                         ('442', '442'), ('*442', '*442'),
                         ('*442', '4*2')]:
            if color_tile:
                C = [[1/2, -1/2], [1/2, 1/2]]
        elif pattern in [('4*2', '2*22')]:
            if not color_tile:
                tile_translation = [-1/2, 0]
        elif pattern in [('**₁', '**')]:
            pattern = ('**', '**')
            if color_tile:
                C = [[1, 0], [0, 1/2]]
        elif pattern in [('**₂', '**')]:
            pattern = ('**', '**')
            if color_tile:
                C = [[0, 1/2], [1, 0]]
            else:
                C = [[0, 1], [1, 0]]
        elif pattern in [('22*', '**')]:
            if color_tile:
                C = [[0, 1], [1, 0]]
            else:
                tile_translation = [0, -1/2]
        elif pattern in [('*×', '××')]:
            if color_tile:
                C = [[1/2, 1/2], [1/2, -1/2]]
                tile_translation = [0, 1/2]
        elif pattern in [('*2222', '*2222')]:
            if color_tile:
                C = [[1/2, 0], [0, 1]]
        elif pattern in [('2*22', '22*')]:
            if color_tile:
                C = [[1/2, 1/2], [1/2, -1/2]]
                tile_translation = [1/4, 1/2]
        elif pattern in [('*2222', '22*')]:
            if color_tile:
                C = [[1/2, 0], [0, 1]]
        elif pattern in [('22*', '22×')]:
            if color_tile:
                C = [[0, 1], [1/2, 0]]
        elif pattern in [('22×', '××')]:
            if not color_tile:
                C = [[0, 1], [1, 0]]
                tile_translation = [-1/4, 0]
        elif pattern in [('××', '××')]:
            if color_tile:
                C = [[0, 1], [1/2, 0]]
            else:
                C = [[0, 1], [1, 0]]
        elif pattern in [('22*', '22*')]:
            if color_tile:
                C = [[1, 0], [0, 1/2]]
        elif pattern in [('22*', '2222')]:
            if color_tile:
                C = [[0, 1], [1, 0]]

        basis = matrix_mult(C, basis)

        if color_tile:
            pattern = pattern[0]
        else:
            pattern = pattern[1]

    img = PIL.Image.new("RGBA", (width, height), (255, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    modulus, angle = transformation
    angle = angle * pi / 180

    x_min, x_max, y_min, y_max = geometry

    def xy_to_pixel(x, y):
        z = modulus * complex(cos(angle), sin(angle)) * complex(x, y)
        x = z.real
        y = z.imag
        delta_x = (x_max - x_min) / (width-1)
        delta_y = (y_max - y_min) / (height-1)
        px = (x-x_min) / delta_x
        py = (y_max-y) / delta_y
        return px, py

    def XY_to_pixel(X, Y):
        [a, b], [c, d] = basis
        x = a*X + c*Y + tile_translation[0]
        y = b*X + d*Y + tile_translation[1]
        return xy_to_pixel(x, y)

    def disks(*coord, color="white"):
        R = 5*coeff
        for i in range(0, len(coord), 2):
            x, y = XY_to_pixel(coord[i], coord[i+1])
            draw.ellipse((x-R, y-R, x+R, y+R), fill=color)

    def line(*coord, color="white", width=1, caps=False):
        R = 5*coeff
        for i in range(2, len(coord), 2):
            x1, y1 = XY_to_pixel(coord[i-2], coord[i-1])
            x2, y2 = XY_to_pixel(coord[i], coord[i+1])
            draw.line((x1, y1, x2, y2), fill=color, width=width*coeff)
            if caps:
                draw.ellipse([x1-R, y1-R, x1+R, y1+R], fill=color)
                draw.ellipse([x2-R, y2-R, x2+R, y2+R], fill=color)

    def mirror(X0, Y0, X1, Y1, order, pixels=50):

        # if order > 1:
        disks(X0, Y0, color="red")

        if not draw_mirrors:
            return

        x0, y0 = XY_to_pixel(X0, Y0)
        x1, y1 = XY_to_pixel(X1, Y1)
        p = complex(x1-x0, y1-y0)
        p = p / abs(p) / 2 * coeff

        for i in range(order):
            q = p * exp(i*pi*1j/order) * pixels
            x2, y2 = q.real, q.imag
            x3, y3 = -x2, -y2
            draw.line((x2+x0, y2+y0, x3+x0, y3+y0), width=3*coeff, fill="red")

    # tile
    if draw_tile:
        line(0, 0, 0, 1, 1, 1, 1, 0, 0, 0, color="black", width=1)

    if draw_orbifold:
        if pattern == "o":
            line(1, 0, 0, 0, 0, 1, color="green", width=3)
        elif pattern == "2222":
            disks(0, 0, 0, 1/2, 1/2, 0, 1/2, 1/2, color="blue")
        elif pattern == "442":
            disks(0, 0, 1/2, 0, 1/2, 1/2, color="blue")
        elif pattern == "333":
            disks(0, 0, 1/3, 2/3, 2/3, 1/3, color="blue")
        elif pattern == "632":
            disks(0, 0, 1/2, 0, 2/3, 1/3, color="blue")
        elif pattern == "*2222":
            line(0, 0, 0, 1/2, 1/2, 1/2, 1/2, 0, 0, 0, color="red", width=3)
            mirror(0, 0, 1/2, 0, 2)
            mirror(1/2, 0, 0, 0, 2)
            mirror(0, 1/2, 0, 0, 2)
            mirror(1/2, 1/2, 0, 1/2, 2)
        elif pattern == "*442":
            line(0, 0, 1/2, 0, 1/2, 1/2, 0, 0, color="red", width=3)
            mirror(0, 0, 0, 1, 4)
            mirror(1/2, 1/2, 0, 1, 4)
            mirror(1/2, 0, 1/2, 1/2, 2)
        elif pattern == "*333":
            line(0, 0, 1/3, 2/3, 2/3, 1/3, 0, 0, color="red", width=3)
            mirror(0, 0, 1/3, 2/3, 3)
            mirror(1/3, 2/3, 0, 0, 3)
            mirror(2/3, 1/3, 0, 0, 3)
        elif pattern == "*632":
            line(0, 0, 1/2, 0, 2/3, 1/3, 0, 0, color="red", width=3)
            mirror(0, 0, 1/2, 0, 6)
            mirror(1/2, 0, 0, 0, 2)
            mirror(2/3, 1/3, 0, 0, 3)
        elif pattern == "4*2":
            disks(0, 0, color="blue")
            mirror(1/2, 0, 0, 1/2, 2)
        elif pattern == "2*22":
            disks(0, 1/2, color="blue")
            mirror(0, 0, 1/2, 1/2, 2)
            mirror(1/2, 1/2, 0, 0, 2)
        elif pattern == "3*3":
            disks(2/3, 1/3, color="blue")
            mirror(0, 0, 1/2, 0, 3)
        elif pattern == "**":
            mirror(1/2, 0, 0, 0, 1)
            mirror(1/2, 1/2, 0, 1/2, 1)
        elif pattern == "22×":
            disks(0, 0, 1/2, 0, color="blue")
            line(0, 1/4, 1/2, 1/4, color="lightgreen", width=3, caps=True)
        elif pattern == "22*":
            disks(0, 1/2, 1/2, 0, color="blue")
            mirror(1/4, 0, 1/4, 1/2, 1)
        elif pattern == "*×":
            mirror(1/2, 1/2, 0, 0, 1)
            line(1/2, 0, 1, 1/2, color="lightgreen", width=3, caps=True)
        elif pattern == "××":
            line(1/4, 0, 3/4, 0, color="lightgreen", width=3, caps=True)
            line(1/4, 1/2, 3/4, 1/2, color="lightgreen", width=3, caps=True)

    img = img.resize(size, PIL.Image.ANTIALIAS)

    return img
# >>>2


def fade_image(image, coeff=100):       # <<<2
    """return a faded version of the image"""
    # TODO allow fading to black and use in make_sphere_background
    mask = PIL.Image.new("L", image.size, coeff)
    white = PIL.Image.new("RGB", image.size, (255, 255, 255))
    white.paste(image, mask=mask)
    return white
# >>>2
# >>>1


###
# GUI
# <<<1

# tooltip objet (see http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml)
# <<<2
class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.bcolor = self.widget.cget("highlightbackground")
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 20
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
        self.widget.config(highlightbackground="green")

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
        self.widget.config(highlightbackground=self.bcolor)


def createToolTip(widget, text):
    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
# >>>2


class LabelEntry(Frame):  # <<<2
    """
    An Entry widget with a label on its left.
    """
    entry_widget = None  # the Entry widget
    label_widget = None  # the Label widget
    content = None       # the corresponding StringVar
    convert = None       # the conversion function used for validation

    def __init__(self, parent, label, on_click=None,  # <<<3
                 value="",
                 convert=None,
                 state=NORMAL,
                 orientation="H", **kwargs):
        Frame.__init__(self, parent)

        self.convert = convert

        if orientation == "H":
            side = LEFT
            padx = (0, 5)
            pady = 0
        elif orientation == "V":
            side = TOP
            padx = 0
            pady = 0
        if label:
            self.label_widget = Label(self, text=label)
            self.label_widget.pack(side=side, padx=padx, pady=pady)

        self.content = StringVar("")
        self.content.set(value)
        self.entry_widget = Entry(self, textvar=self.content,
                                  exportselection=0,
                                  state=state, **kwargs)
        self.entry_widget.pack(side=side)

        for method in ["config", "configure", "bind", "focus_set", "xview"]:
            setattr(self, method, getattr(self.entry_widget, method))

        if self.convert is not None:
            self.bind("<Return>", self.validate)
            self.bind("<FocusOut>", self.validate)
    # >>>3

    def validate(self, *args):     # <<<3
        if self.convert is None:
            return True
        else:
            try:
                self.convert(self.content.get())
                self.entry_widget.config(foreground="black")
                return True
            except Exception as e:
                self.entry_widget.config(foreground="red")
                return False
    # >>>3

    def set(self, s):  # <<<3
        if s is None:
            self.content.set("")
        else:
            self.content.set(s)
            self.entry_widget.select_clear()
            if self.convert is not None:
                self.validate()
    # >>>3

    def get(self):  # <<<3
        if self.convert is not None:
            try:
                return self.convert(self.content.get())
            except Exception as e:
                raise Error("{}: cannot convert value of field '{}': {}"
                            .format(self.label_widget.cget("text"),
                                    self.content.get(), e))
        else:
            return self.content.get()
    # >>>3

    def delete(self):  # <<<3
        self.content.set("")
    # >>>3

    def disable(self):  # <<<3
        self.entry_widget.config(state=DISABLED)
        if self.label_widget is not None:
            self.label_widget.config(state=DISABLED)
    # >>>3

    def enable(self):  # <<<3
        self.entry_widget.config(state=NORMAL)
        if self.label_widget is not None:
            self.label_widget.config(state=NORMAL)
    # >>>3

    def toggle(self):  # <<<3
        if self.entry_widget.cget("state") == NORMAL:
            self.disable()
        else:
            self.enable()
    # >>>3
# >>>2


class ColorWheel(LabelFrame):   # <<<2

    # getter / setters <<<3
    @property
    def geometry(self):     # <<<4
        x_min = self._x_min.get()
        x_max = self._x_max.get()
        y_min = self._y_min.get()
        y_max = self._y_max.get()
        return x_min, x_max, y_min, y_max
    # >>>4

    @geometry.setter
    def geometry(self, geometry):     # <<<4
        x_min, x_max, y_min, y_max = geometry
        self._x_min.set(float_to_str(x_min))
        self._x_max.set(float_to_str(x_max))
        self._y_min.set(float_to_str(y_min))
        self._y_max.set(float_to_str(y_max))
    # >>>4

    @property
    def modulus(self):  # <<<4
        return self._modulus.get()
    # >>>4

    @modulus.setter
    def modulus(self, modulus):  # <<<4
        self._modulus.set(float_to_str(modulus))
    # >>>4

    @property
    def angle(self):    # <<<4
        return self._angle.get()
    # >>>4

    @angle.setter
    def angle(self, angle):    # <<<4
        self._angle.set(float_to_str(angle))
    # >>>4

    @property
    def rgb_color(self):    # <<<4
        return self._default_color.get()
    # >>>4

    @rgb_color.setter
    def rgb_color(self, color):    # <<<4
        self._default_color.set("#{:02x}{:02x}{:02x}"
                                .format(color[0], color[1], color[2]))
    # >>>4

    @property
    def default_color(self):    # <<<4
        return self._default_color.entry_widget.get()
    # >>>4

    @default_color.setter
    def default_color(self, color):    # <<<4
        self._default_color.set(color)
    # >>>4

    @property
    def stretch(self):    # <<<4
        return self._stretch_color.get()
    # >>>4

    @stretch.setter
    def stretch(self, b):    # <<<4
        self._stretch_color.set(b)
    # >>>4

    @property
    def filename(self):     # <<<4
        try:
            return normalize_path(self._filename)
        except AttributeError:
            return None
    # >>>4

    @filename.setter
    def filename(self, filename):   # <<<4
        if filename is not None:
            filename = normalize_path(filename)
        try:
            if self._filename != filename:
                self._alt_filename = self._filename
                self._filename = filename
        except AttributeError:
            self._filename = filename
    # >>>4

    @property
    def alt_filename(self):     # <<<4
        try:
            return self._alt_filename
        except AttributeError:
            return None
    # >>>4

    @alt_filename.setter
    def alt_filename(self, filename):   # <<<4
        if filename is not None:
            if os.path.isfile(os.path.expanduser(filename)):
                self._alt_filename = filename
                self._alt_filename_label.config(
                    text="alt:" + os.path.basename(filename)
                )
    # >>>4
    # >>>3

    def __init__(self, root):        # <<<3

        self.root = root

        LabelFrame.__init__(self, root)
        self.configure(text="Colorwheel")

        self._default_color = LabelEntry(
            self,
            label="default color",
            value=DEFAULT_COLOR,
            width=10,
            convert=getrgb
        )
        self._default_color.pack(padx=5, pady=5)
        self._default_color.bind("<Return>", self.update_default_color)
        self._default_color.bind("<FocusOut>", self.update_default_color)

        self._stretch_color = BooleanVar()
        self._stretch_color.set(False)
        self._stretch_color.trace(
            "w",
            lambda *_: self.change_colorwheel(self.filename, reset_geometry=False)
        )
        # Checkbutton(self, text="stretch unit disk",
        #             variable=self._stretch_color,
        #             onvalue=True, offvalue=False,
        #             command=lambda: self.change_colorwheel(self.filename, reset_geometry=False),
        #             indicatoron=False
        #             ).pack(padx=5, pady=0)

        self._canvas = Canvas(
            self,
            width=COLOR_SIZE,
            height=COLOR_SIZE,
            bg="white",
            cursor="tcross"
        )
        self._canvas.pack(padx=5, pady=5)
        for i in range(5, COLOR_SIZE, 10):
            for j in range(5, COLOR_SIZE, 10):
                self._canvas.create_line(i-1, j, i+2, j, fill="gray")
                self._canvas.create_line(i, j-1, i, j+2, fill="gray")
        self._colorwheel_id = None
        self._canvas.bind("<Button-3>", self.set_origin)
        self._canvas.bind("<Double-Button-1>", self.switch_colorwheel)

        self._filename_button = Button(
            self,
            text="choose file",
            command=self.choose_colorwheel
        )
        self._filename_button.pack(padx=5, pady=0)

        self._alt_filename_label = Label(self, text="alt: ", font="TkNormal 8")
        self._alt_filename_label.pack(padx=5, pady=(0, 5))

        self._coord_frame = LabelFrame(self, text="coordinates")
        self._coord_frame.pack(fill=X, padx=5, pady=5)
        self._coord_frame.columnconfigure(0, weight=1)
        self._coord_frame.columnconfigure(1, weight=1)

        self._x_min = LabelEntry(self._coord_frame, label="x min",
                                 value=COLOR_GEOMETRY[0],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._x_min.grid(row=0, column=0, padx=5, pady=5)

        self._x_max = LabelEntry(self._coord_frame, label="x max",
                                 value=COLOR_GEOMETRY[1],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._x_max.grid(row=0, column=1, padx=5, pady=5)

        self._y_min = LabelEntry(self._coord_frame, label="y min",
                                 value=COLOR_GEOMETRY[2],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._y_min.grid(row=1, column=0, padx=5, pady=5)

        self._y_max = LabelEntry(self._coord_frame, label="y max",
                                 value=COLOR_GEOMETRY[3],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._y_max.grid(row=1, column=1, padx=5, pady=5)

        transformation_frame = LabelFrame(self, text="transformation")
        transformation_frame.pack(fill=X, padx=5, pady=5)
        tmp_frame = Frame(transformation_frame)
        tmp_frame.pack()
        self._modulus = LabelEntry(
            tmp_frame,
            label="modulus",
            value=1,
            convert=float,
            width=6
        )
        self._modulus.grid(row=0, column=0, sticky=E, padx=5, pady=(5, 2))
        self._modulus.bind(
            "<Return>",
            lambda _: self.change_colorwheel(self.filename, reset_geometry=False),
            add="+"
        )
        self._modulus.bind(
            "<FocusOut>",
            lambda _: self.change_colorwheel(self.filename, reset_geometry=False),
            add="+"
        )

        self._angle = LabelEntry(
            tmp_frame, label="angle (°)",
            value=0,
            convert=float,
            width=4
        )
        self._angle.grid(row=1, column=0, sticky=E, padx=5, pady=(2, 5))
        self._angle.bind(
            "<Return>",
            lambda _: self.change_colorwheel(self.filename, reset_geometry=False),
            add="+"
        )
        self._angle.bind(
            "<FocusOut>",
            lambda _: self.change_colorwheel(self.filename, reset_geometry=False),
            add="+"
        )

        self.update_default_color()

        if os.path.exists("./colorwheel.jpg"):
            self.change_colorwheel("colorwheel.jpg", reset_geometry=True)
        else:
            self.filename = None
    # >>>3

    def update_default_color(self, *args):     # <<<3
        if self._default_color.validate():
            self._canvas.config(bg="#{:02x}{:02x}{:02x}"
                                .format(*self.rgb_color))
    # >>>3

    def change_colorwheel(self, filename, reset_geometry=True):  # <<<3
        if filename is None:
            return
        try:
            filename = os.path.expanduser(filename)
            if self.stretch:
                self._coord_frame.config(foreground="#a3a3a3")
                self._x_min.disable()
                self._x_max.disable()
                self._y_min.disable()
                self._y_max.disable()
                # self._modulus.disable()
                # self._angle.disable()
                zs = make_coordinates_array(
                        size=(PREVIEW_SIZE, PREVIEW_SIZE),
                        geometry=(-STRETCH_DISPLAY_RADIUS,
                                  STRETCH_DISPLAY_RADIUS,
                                  -STRETCH_DISPLAY_RADIUS,
                                  STRETCH_DISPLAY_RADIUS))
                ne.evaluate("zs / (sqrt(1+zs.real**2 + zs.imag**2))", out=zs)
                img = apply_color(
                    zs,
                    filename,
                    geometry=self.geometry,
                    modulus=self.modulus,
                    angle=self.angle,
                    stretch=self.stretch,
                    color=self.rgb_color
                )
            else:
                self._coord_frame.config(foreground="black")
                self._x_min.enable()
                self._x_max.enable()
                self._y_min.enable()
                self._y_max.enable()
                self._modulus.enable()
                self._angle.enable()
                # self._reset_button.configure(state=NORMAL)
                img = PIL.Image.open(filename)
                img.thumbnail(
                    (COLOR_SIZE+1, COLOR_SIZE+1),
                    PIL.Image.ANTIALIAS
                )
                if reset_geometry:
                    width, height = img.size
                    ratio = width / height
                    if ratio < 1:
                        self.geometry = (COLOR_GEOMETRY[0],
                                         COLOR_GEOMETRY[1],
                                         COLOR_GEOMETRY[2]/ratio,
                                         COLOR_GEOMETRY[3]/ratio)
                    else:
                        self.geometry = (COLOR_GEOMETRY[0]*ratio,
                                         COLOR_GEOMETRY[1]*ratio,
                                         COLOR_GEOMETRY[2],
                                         COLOR_GEOMETRY[3])

            self._image = img
            tk_img = PIL.ImageTk.PhotoImage(img)
            self._tk_image = tk_img     # prevent garbage collection
            self._canvas.delete("colorwheel")
            self._canvas.create_image(
                (COLOR_SIZE//2, COLOR_SIZE//2),
                image=tk_img,
                tag="colorwheel"
            )
            self.filename = filename
            self._filename_button.config(text=os.path.basename(filename))
            try:
                alt_filename = self.alt_filename
                self._alt_filename_label.config(
                    text="alt:" + os.path.basename(alt_filename)
                )
            except:
                pass

            self.draw_axes()

        except Exception as e:
            error("problem while loading {} for color image: {}"
                  .format(filename, e))
    # >>>3

    def switch_colorwheel(self, *args):     # <<<3
        try:
            self.change_colorwheel(self._alt_filename, reset_geometry=False)
            return "break"
        except AttributeError:
            pass
    # >>>3

    def draw_axes(self, *args):      # <<<3
        self._canvas.delete("axes")

        if self.stretch:
            x_min = -STRETCH_DISPLAY_RADIUS
            x_max = STRETCH_DISPLAY_RADIUS
            y_min = -STRETCH_DISPLAY_RADIUS
            y_max = STRETCH_DISPLAY_RADIUS
        else:
            x_min, x_max, y_min, y_max = self.geometry

        delta_x = COLOR_SIZE / (x_max - x_min)
        delta_y = COLOR_SIZE / (y_max - y_min)
        x0 = - delta_x * x_min
        y0 = delta_y * y_max
        r = delta_x / self.modulus
        self._unit_circle = self._canvas.create_oval(
            x0-r+1, y0-r+1,
            x0+r, y0+r,
            width=1,
            outline="lightgray",
            tag="axes"
        )

        alpha = ((self.angle % 360) + 360) % 360
        beta = (alpha % 90)
        beta = beta * pi / 180 if beta < 45 else (beta-90) * pi / 180

        a, b = cos(beta), sin(beta)
        d = a*x0 + b*y0
        p_top = int(d/a)
        p_bottom = int((d-b*COLOR_SIZE)/a)

        a, b = b, -a
        d = a*x0 + b*y0
        p_left = int(d/b)
        p_right = int((d-a*COLOR_SIZE)/b)

        if 0 <= alpha < 45 or 315 <= alpha < 360:
            l_plus = [p_top, 0, x0, y0, COLOR_SIZE, p_right]
            l_minus = [p_bottom, COLOR_SIZE, x0, y0, 0, p_left]
        elif 45 <= alpha < 135:
            l_plus = [COLOR_SIZE, p_right, x0, y0, p_bottom, COLOR_SIZE]
            l_minus = [0, p_left, x0, y0, p_top, 0]
        elif 135 <= alpha < 225:
            l_plus = [p_bottom, COLOR_SIZE, x0, y0, 0, p_left]
            l_minus = [p_top, 0, x0, y0, COLOR_SIZE, p_right]
        elif 225 <= alpha < 315:
            l_plus = [0, p_left, x0, y0, p_top, 0]
            l_minus = [COLOR_SIZE, p_right, x0, y0, p_bottom, COLOR_SIZE]
        else:
            assert False

        self._canvas.create_line(
            *l_plus,
            fill="lightgray",
            width=2,
            tags=("axes", "colorwheel")
        )
        self._canvas.create_line(
            *l_minus,
            fill="lightgray",
            width=1,
            tags=("axes", "colorwheel")
        )
    # >>>3

    def choose_colorwheel(self, *args):    # <<<3
        if self.filename and os.path.isfile(os.path.expanduser(self.filename)):
            initialdir = os.path.dirname(os.path.expanduser(self.filename))
        else:
            initialdir = "./"
        filename = filedialog.askopenfilename(
            parent=self,
            title="Create Symmetry: choose color wheel image",
            initialdir=initialdir,
            filetypes=[("images", "*.jpg *.jpeg *.png"), ("all", "*.*")]
        )
        if filename:
            self.change_colorwheel(filename, reset_geometry=True)
    # >>>3

    def set_origin(self, event):        # <<<3
        if self.stretch:
            return
        x, y = event.x, event.y
        x_min, x_max, y_min, y_max = self.geometry
        delta_x = x_max - x_min
        delta_y = y_max - y_min

        x_min = -x/COLOR_SIZE * delta_x
        x_max = x_min + delta_x
        y_max = y/COLOR_SIZE * delta_y
        y_min = y_max - delta_y
        self.geometry = x_min, x_max, y_min, y_max

        self.draw_axes()
    # >>>3

    def reset_geometry(self, *args):        # <<<3
        # if self.stretch:
        #     return
        self.modulus = 1
        self.angle = 0
        self.stretch = False
        self.geometry = COLOR_GEOMETRY
        if self.filename is not None:
            self.change_colorwheel(self.filename, reset_geometry=True)
    # >>>3

    @property
    def config(self):           # <<<3
        cfg = {}
        for k in ["filename", "alt_filename", "default_color", "geometry",
                  "modulus", "angle", "stretch"]:
            cfg[k] = getattr(self, k)
        return cfg
    # >>>3

    @config.setter
    def config(self, cfg):      # <<<3
        for k in ["default_color", "geometry", "modulus",
                  "angle", "stretch"]:
            if k in cfg:
                setattr(self, k, cfg[k])
        if "filename" in cfg:
            self.change_colorwheel(cfg["filename"], reset_geometry=False)
        if "alt_filename" in cfg:
            self.alt_filename = cfg["alt_filename"]
        if "default_color" in cfg:
            self.update_default_color()
    # >>>3
# >>>2


class Output(LabelFrame):     # <<<2

    # getters and setters   <<<3
    @property
    def filename_template(self):    # <<<4
        return self._filename_template.get()
    # >>>4

    @filename_template.setter
    def filename_template(self, template):    # <<<4
        self._filename_template.set(template)
    # >>>4

    @property
    def save_directory(self):   # <<<4
        return os.path.expanduser(self._save_directory)
    # >>>4

    @save_directory.setter
    def save_directory(self, dir):   # <<<4
        self._save_directory = normalize_path(dir)
        if len(dir) > 30:
            dir = "..." + dir[-27:]
        self._save_directory_button.configure(text=dir)
    # >>>4

    @property
    def geometry(self):     # <<<4
        x_min = self._x_min.get()
        x_max = self._x_max.get()
        y_min = self._y_min.get()
        y_max = self._y_max.get()
        return x_min, x_max, y_min, y_max
    # >>>4

    @geometry.setter
    def geometry(self, geometry):     # <<<4
        x_min, x_max, y_min, y_max = geometry
        self._x_min.set(float_to_str(x_min))
        self._x_max.set(float_to_str(x_max))
        self._y_min.set(float_to_str(y_min))
        self._y_max.set(float_to_str(y_max))
    # >>>4

    @property
    def modulus(self):  # <<<4
        return self._modulus.get()
    # >>>4

    @modulus.setter
    def modulus(self, modulus):  # <<<4
        self._modulus.set(float_to_str(modulus))
    # >>>4

    @property
    def angle(self):    # <<<4
        return self._angle.get()
    # >>>4

    @angle.setter
    def angle(self, angle):    # <<<4
        self._angle.set(float_to_str(angle))
    # >>>4

    @property
    def size(self):    # <<<4
        return self._size.get()
    # >>>4

    @size.setter
    def size(self, size):    # <<<4
        w, h = size
        self._size.set("{} x {}".format(w, h))
    # >>>4

    @property
    def width(self):    # <<<4
        return self.size[0]
    # >>>4

    @width.setter
    def width(self, width):    # <<<4
        h = self.height
        self.size = width, h
    # >>>4

    @property
    def height(self):    # <<<4
        return self.size[1]
    # >>>4

    @height.setter
    def height(self, height):    # <<<4
        w = self.width
        self.size = w, height
    # >>>4

    @property
    def display_mode(self):    # <<<4
        return self._display_mode.get()
    # >>>4

    @display_mode.setter
    def display_mode(self, m):    # <<<4
        self._display_mode.set(m)
    # >>>4

    @property
    def sphere_rotations(self):    # <<<4
        return self._rotations.get()
    # >>>4

    @sphere_rotations.setter
    def sphere_rotations(self, rotations):    # <<<4
        self._rotations.set(floats_to_str(rotations))
    # >>>4

    @property
    def inversion_center(self):    # <<<4
        return self._inversion_center.get()
    # >>>4

    @inversion_center.setter
    def inversion_center(self, z):    # <<<4
        if isinstance(z, str):
            z = str_to_complex(z)
        z = complex(z)
        self._inversion_center.set(complex_to_str(z, precision=3))
    # >>>4

    @property
    def sphere_background(self):    # <<<4
        s = self._sphere_background.get()
        if is_rgb(s):
            return s
        elif os.path.isfile(
            os.path.expanduser(
                self._sphere_background_full_filename
            )
        ):
            return self._sphere_background_full_filename
        else:
            return s
    # >>>4

    @sphere_background.setter
    def sphere_background(self, s):    # <<<4
        if is_rgb(s):
            self._sphere_background_full_filename = ""
            self._sphere_background.set(s)
        elif os.path.isfile(os.path.expanduser(s)):
            self._sphere_background_full_filename = os.path.expanduser(s)
            self._sphere_background.set(os.path.basename(s))
        else:
            self._sphere_background_full_filename = ""
            self._sphere_background.set(s)
    # >>>4

    @property
    def sphere_background_fading(self):    # <<<4
        return self._sphere_background_fading.get()
    # >>>4

    @sphere_background_fading.setter
    def sphere_background_fading(self, n):    # <<<4
        self._sphere_background_fading.set(n)
    # >>>4

    @property
    def sphere_stars(self):    # <<<4
        return self._sphere_stars.get()
    # >>>4

    @sphere_stars.setter
    def sphere_stars(self, n):    # <<<4
        self._sphere_stars.set(n)
    # >>>4

    @property
    def geometry_tab(self):     # <<<4
        if "mode" in self._geometry_tabs.tab(
                self._geometry_tabs.select(),
                "text"):
            return "mode"
        elif "geometry" in self._geometry_tabs.tab(
                self._geometry_tabs.select(),
                "text"):
            return "geometry"
        elif "morph" in self._geometry_tabs.tab(
                self._geometry_tabs.select(),
                "text"):
            return "morph"
        else:
            assert False
    # >>>4

    @geometry_tab.setter
    def geometry_tab(self, tab):     # <<<4
        tab = tab.lower().strip()
        if tab == "mode":
            self._geometry_tabs.select(self._geometry_display_tab)
        elif tab == "geometry":
            self._geometry_tabs.select(self._geometry_geometry_tab)
        elif tab == "morph":
            self._geometry_tabs.select(self._geometry_morph_tab)
    # >>>4

    @property
    def draw_tile(self):    # <<<4
        return self._draw_tile.get()
    # >>>4

    @draw_tile.setter
    def draw_tile(self, b):    # <<<4
        self._draw_tile.set(b)
    # >>>4

    @property
    def draw_orbifold(self):    # <<<4
        return self._draw_orbifold.get()
    # >>>4

    @draw_orbifold.setter
    def draw_orbifold(self, b):    # <<<4
        self._draw_orbifold.set(b)
    # >>>4

    @property
    def draw_color_tile(self):    # <<<4
        return self._draw_color_tile.get()
    # >>>4

    @draw_color_tile.setter
    def draw_color_tile(self, b):    # <<<4
        self._draw_color_tile.set(b)
    # >>>4

    @property
    def draw_mirrors(self):    # <<<4
        return self._draw_mirrors.get()
    # >>>4

    @draw_mirrors.setter
    def draw_mirrors(self, b):    # <<<4
        self._draw_mirrors.set(b)
    # >>>4

    @property
    def fade(self):    # <<<4
        return self._fade.get()
    # >>>4

    @fade.setter
    def fade(self, b):    # <<<4
        self._fade.set(b)
    # >>>4

    @property
    def fade_coeff(self):    # <<<4
        return self._fade_coeff.get()
    # >>>4

    @fade_coeff.setter
    def fade_coeff(self, b):    # <<<4
        self._fade_coeff.set(b)
    # >>>4

    @property
    def preview_size(self):     # <<<4
        return min(PREVIEW_SIZE, self._preview_size.get())
    # >>>4

    @preview_size.setter
    def preview_size(self, n):      # <<<4
        self._preview_size.set(min(PREVIEW_SIZE, n))
    # >>>4

    @property
    def morph(self):    # <<<4
        return (self._morph_button.cget("state") != DISABLED and
                self._morph.get())
    # >>>4

    @morph.setter
    def morph(self, b):     # <<<4
        self._morph.set(b)
    # >>>4

    @property
    def morph_start(self):    # <<<4
        return self._morph_start.get()
    # >>>4

    @morph_start.setter
    def morph_start(self, b):     # <<<4
        self._morph_start.set(b)
    # >>>4

    @property
    def morph_end(self):    # <<<4
        return self._morph_end.get()
    # >>>4

    @morph_end.setter
    def morph_end(self, b):     # <<<4
        self._morph_end.set(b)
    # >>>4

    @property
    def morph_stable_coeff(self):    # <<<4
        return self._morph_stable_coeff.get()
    # >>>4

    @morph_stable_coeff.setter
    def morph_stable_coeff(self, c):     # <<<4
        self._morph_stable_coeff.set(float_to_str(c))
    # >>>4
    # >>>3

    def __init__(self, root):       # <<<3

        self.root = root

        LabelFrame.__init__(self, root)
        self.configure(text="Output")

        # the preview image     <<<4
        canvas_frame = Frame(
            self,
            borderwidth=2,
            relief=GROOVE
        )
        canvas_frame.grid(row=0, column=0, rowspan=4, padx=5, pady=5)

        self._canvas = Canvas(
            canvas_frame,
            width=PREVIEW_SIZE,
            height=PREVIEW_SIZE,
            bg="light gray",
            cursor="tcross"
        )
        for i in range(5, PREVIEW_SIZE, 10):
            for j in range(5, PREVIEW_SIZE, 10):
                self._canvas.create_line(i-1, j, i+2, j, fill="gray")
                self._canvas.create_line(i, j-1, i, j+2, fill="gray")
        self._canvas.pack(padx=5, pady=5)

        self._draw_color_tile = BooleanVar()
        self._draw_color_tile_button = Checkbutton(
            canvas_frame,
            variable=self._draw_color_tile,
            text=""
        )
        self._draw_color_tile_button.pack(side=LEFT, padx=0, pady=0)
        createToolTip(self._draw_color_tile_button, "show tile for color symmetry\n(instead of plain symmetry)")

        self._draw_tile = BooleanVar()
        self._draw_tile_button = Checkbutton(
            canvas_frame,
            variable=self._draw_tile,
            text="tile",
            indicatoron=False
        )
        self._draw_tile_button.pack(side=LEFT, padx=5, pady=5)

        self._draw_orbifold = BooleanVar()
        self._draw_orbifold_button = Checkbutton(
            canvas_frame,
            variable=self._draw_orbifold,
            text="orbifold",
            indicatoron=False
        )
        self._draw_orbifold_button.pack(side=LEFT, padx=5, pady=5)

        self._draw_mirrors = BooleanVar()
        self._draw_mirrors_button = Checkbutton(
            canvas_frame,
            variable=self._draw_mirrors,
            text="mirrors",
            indicatoron=False
        )
        self._draw_mirrors_button.pack(side=LEFT, padx=5, pady=5)

        self._fade = BooleanVar()
        self._fade_button = Checkbutton(
            canvas_frame,
            variable=self._fade,
            text="fade",
            indicatoron=False
        )
        self._fade_button.pack(side=LEFT, padx=(5, 0), pady=5)

        self._fade_coeff = LabelEntry(
            canvas_frame,
            convert=int,
            width=3,
            label=""
        )
        self._fade_coeff.pack(side=LEFT, padx=(0, 5), pady=5)

        self._preview_size = LabelEntry(
            canvas_frame,
            convert=int,
            width=3,
            label="preview size"
        )
        self._preview_size.pack(side=RIGHT, padx=5, pady=5)
        self._preview_size.set(PREVIEW_SIZE)

        self._draw_tile.trace("w", self.update)
        self._draw_tile.set(False)
        self._draw_orbifold.trace("w", self.update)
        self._draw_orbifold.set(False)
        self._draw_color_tile.trace("w", self.update)
        self._draw_color_tile.set(False)
        self._draw_mirrors.trace("w", self.update)
        self._draw_mirrors.set(False)
        self._fade.trace("w", self.update)
        self._fade.set(False)
        self._fade_coeff.set(100)
        # >>>4

        # geometry of result    <<<4
        self._geometry_tabs = Notebook(self)
        self._geometry_tabs.grid(row=0, column=1, sticky=E+W, padx=5, pady=5)
        # prevent arrows from changing tab
        self._geometry_tabs.bind_all(
            "<<NotebookTabChanged>>",
            lambda _: self.focus_set()
        )

        self._geometry_geometry_tab = Frame(self._geometry_tabs)
        self._geometry_tabs.add(self._geometry_geometry_tab, text="geometry")

        self._geometry_display_tab = Frame(self._geometry_tabs)
        self._geometry_tabs.add(self._geometry_display_tab, text="mode")

        self._geometry_morph_tab = Frame(self._geometry_tabs)
        self._geometry_tabs.add(self._geometry_morph_tab, text="morph")

        # geometry tab ###4
        coord_frame = LabelFrame(
            self._geometry_geometry_tab,
            text="coordinates"
        )
        coord_frame.pack(padx=5, pady=5)
        # coord_frame.grid(row=0, column=1, sticky=E+W, padx=5, pady=5)
        coord_frame.columnconfigure(0, weight=1)
        coord_frame.columnconfigure(1, weight=1)

        self._x_min = LabelEntry(
            coord_frame,
            label="x min",
            value=OUTPUT_GEOMETRY[0],
            convert=float,
            width=4, justify=RIGHT
        )
        self._x_min.grid(row=0, column=0, padx=5, pady=5)

        self._x_max = LabelEntry(
            coord_frame,
            label="x max",
            value=OUTPUT_GEOMETRY[1],
            convert=float,
            width=4, justify=RIGHT
        )
        self._x_max.grid(row=0, column=1, padx=5, pady=5)

        self._y_min = LabelEntry(
            coord_frame,
            label="y min",
            value=OUTPUT_GEOMETRY[2],
            convert=float,
            width=4, justify=RIGHT
        )
        self._y_min.grid(row=1, column=0, padx=5, pady=5)

        self._y_max = LabelEntry(
            coord_frame,
            label="y max",
            value=OUTPUT_GEOMETRY[3],
            convert=float,
            width=4, justify=RIGHT
        )
        self._y_max.grid(row=1, column=1, padx=5, pady=5)

        transformation_frame = LabelFrame(
            self._geometry_geometry_tab,
            text="transformation"
        )
        transformation_frame.pack(padx=5, pady=5, fill=BOTH)
        tmp_frame = Frame(transformation_frame)
        tmp_frame.pack()
        self._modulus = LabelEntry(
            tmp_frame,
            label="modulus",
            value=1,
            convert=float,
            width=6
        )
        self._modulus.grid(row=0, column=0, sticky=E, padx=5, pady=(5, 2))

        self._angle = LabelEntry(
            tmp_frame,
            label="angle (°)",
            value=0,
            convert=float,
            width=4
        )
        self._angle.grid(row=1, column=0, sticky=E, padx=5, pady=(2, 5))

        Button(
            transformation_frame,
            text="zoom -",
            command=self.zoom(1/ZOOM_FACTOR)
        ).pack(side=LEFT, padx=5, pady=5)
        Button(
            transformation_frame,
            text="zoom +",
            command=self.zoom(ZOOM_FACTOR)
        ).pack(side=RIGHT, padx=5, pady=5)
        # >>>4

        # sphere parameters     <<<4
        self._geometry_tabs.bind(
            "<Triple-Button-1>",
            sequence(self.enable_mode_tab,
                     self.enable_geometry_morph_tab)
        )

        self._display_mode = StringVar()

        tmp = Frame(self._geometry_display_tab)
        tmp.grid(row=0)

        plain_button = Radiobutton(
            tmp,
            text="plain",
            variable=self._display_mode,
            value="plain",
            indicatoron=False,
        )
        plain_button.pack(side=LEFT, padx=5, pady=10)

        sphere_button = Radiobutton(
            tmp,
            text="sphere",
            variable=self._display_mode,
            value="sphere",
            indicatoron=False,
        )
        sphere_button.pack(side=LEFT, padx=5, pady=10)

        inversion_button = Radiobutton(
            tmp,
            text="inversion",
            variable=self._display_mode,
            value="inversion",
            indicatoron=False,
        )
        inversion_button.pack(side=LEFT, padx=5, pady=10)

        self._rotations = LabelEntry(
            self._geometry_display_tab,
            label="rotations x, y, z (°)",
            orientation="V",
            value=SPHERE_ROTATIONS,
            convert=str_to_floats,
            width=15
        )
        self._rotations.grid(row=2, padx=5, pady=10)

        self._inversion_center = LabelEntry(
            self._geometry_display_tab,
            label="inversion center",
            orientation="V",
            value="i",
            convert=str_to_complex,
            width=10
        )
        self._inversion_center.grid(row=2, padx=5, pady=10)

        background_frame = Frame(self._geometry_display_tab)
        background_frame.grid(row=3, padx=5, pady=5)

        self._sphere_background_full_filename = ""
        self._sphere_background = StringVar()

        background_button = Button(
            background_frame,
            text="background",
            command=self.choose_sphere_background,
            padx=1, pady=1
        )
        background_button.grid(row=0, column=0, sticky=E)
        background_entry = Entry(
            background_frame,
            textvar=self._sphere_background,
            width=10
        )
        background_entry.grid(row=0, column=1, padx=5, pady=10, sticky=E)
        self.sphere_background = DEFAULT_BACKGROUND

        self._sphere_background_fading = LabelEntry(
            background_frame,
            label="fade background",
            value=100,
            width=5,
            convert=int
        )
        self._sphere_background_fading.grid(
            row=1, column=0, columnspan=2,
            padx=5, pady=5,
            sticky=E
        )

        self._sphere_stars = LabelEntry(
            background_frame,
            label="random stars",
            value=500,
            width=5,
            convert=int
        )
        self._sphere_stars.grid(
            row=2, column=0, columnspan=2,
            padx=5, pady=5,
            sticky=E
        )

        def update_tab(*args):
            s = self._display_mode.get()
            if s == "plain":
                self._sphere_stars.disable()
                self._sphere_background_fading.disable()
                self._inversion_center.grid_forget()
                self._rotations.grid_forget()
                background_button.config(state=DISABLED)
                background_entry.config(state=DISABLED)
            elif s == "sphere":
                self._sphere_stars.enable()
                self._sphere_background_fading.enable()
                self._inversion_center.grid_forget()
                self._rotations.grid(row=2, padx=5, pady=10)
                background_button.config(state=NORMAL)
                background_entry.config(state=NORMAL)
            elif s == "inversion":
                self._sphere_stars.enable()
                self._sphere_background_fading.enable()
                self._inversion_center.grid(row=2, padx=5, pady=10)
                self._rotations.grid_forget()
                background_button.config(state=NORMAL)
                background_entry.config(state=NORMAL)
            else:
                assert False

        self._display_mode.trace("w", callback=update_tab)
        self._display_mode.set("plain")
        # >>>4

        # morph parameters      ###4
        self._morph = BooleanVar()
        self._morph.set(False)
        self._morph_button = Checkbutton(
            self._geometry_morph_tab,
            variable=self._morph,
            text="morph",
            indicatoron=False
        )
        self._morph_button.pack(padx=5, pady=10)

        tmp_frame = Frame(self._geometry_morph_tab)
        tmp_frame.pack()
        self._morph_start = LabelEntry(
            tmp_frame,
            label="from (°)",
            convert=int,
            width=3
        )
        self._morph_start.grid(row=0, sticky=E, padx=5, pady=5)
        self._morph_start.set(0)

        self._morph_end = LabelEntry(
            tmp_frame,
            label="to (°)",
            convert=int,
            width=3
        )
        self._morph_end.grid(row=1, sticky=E, padx=5, pady=5)
        self._morph_end.set(180)

        self._morph_stable_coeff = LabelEntry(
            tmp_frame,
            label="stable (%)",
            value=20,
            convert=float,
            width=3
        )
        self._morph_stable_coeff.grid(row=2, sticky=E, padx=5, pady=5)
        # >>>4

        # result settings       <<<4
        settings_frame = LabelFrame(self, text="output")
        settings_frame.grid(row=2, column=1, sticky=E+W, padx=5, pady=5)

        def convert_size(s):
            try:
                s = re.sub("[,;x]", " ", s)
                w, h = s.split()
                w = int(w.strip())
                h = int(h.strip())
                return w, h
            except:
                raise ValueError
        self._size = LabelEntry(
            settings_frame,
            label="size",
            value="{} x {}".format(*OUTPUT_SIZE),
            convert=convert_size,
            width=12
        )
        self._size.pack(padx=5, pady=(5, 0))

        Label(settings_frame, text="save directory").pack(padx=5, pady=(5, 2))
        self._save_directory = "./"
        self._save_directory_button = Button(
            settings_frame,
            text=self._save_directory,
            font="TkNormal 8",
            padx=2, pady=0,
            command=self.change_save_dir
        )
        self._save_directory_button.pack(padx=5, pady=(0, 5))

        self._filename_template = LabelEntry(
            settings_frame,
            label="filename template",
            orientation="V",
            value=FILENAME_TEMPLATE,
            font="TkNormal 8",
            width=24
        )
        self._filename_template.pack(padx=5, pady=5)
        # >>>4

        # preview button    <<<4
        self._preview_button = Button(self, text="preview", command=None)
        self._preview_button.grid(row=3, column=1, padx=5, pady=5)
        # >>>4

        self._canvas.bind(
            "<Motion>",
            lambda e: self.update_pointer_coordinates(e.x, e.y)
        )
        self._canvas.bind(
            "<Leave>",
            lambda e: self._canvas.itemconfig(
                self._canvas._pointer_coords,
                text=""
            )
        )

        # this binding is overridden in CreateSymmetry to add make_preview
        self._canvas.bind("<Button-1>", self.start_apply_zoom_rectangle)
        self._canvas.bind("<Button-3>", self.cancel_zoom_rectangle)
        self._canvas.bind("<Motion>", self.update_zoom_rectangle, add="+")

        self.adjust_geometry()
    # >>>3

    def change_save_dir(self):  # <<<3
        if os.path.isdir(self.save_directory):
            initialdir = self.save_directory
        else:
            initialdir = "./"
        dir = filedialog.askdirectory(
            parent=self,
            title="Create Symmetry: save directory",
            initialdir=initialdir
        )
        if dir:
            self.save_directory = dir
    # >>>3

    def disable_mode_tab(self, *args):  # <<<3
        self.display_mode = "plain"
        self._geometry_tabs.tab(self._geometry_display_tab, state=DISABLED)
    # >>>3

    def disable_geometry_morph_tab(self, *args):  # <<<3
        self.morph = False
        self._geometry_tabs.tab(self._geometry_morph_tab, state=DISABLED)
    # >>>3

    def enable_mode_tab(self, *args):   # <<<3
        self._geometry_tabs.tab(self._geometry_display_tab, state=NORMAL)
    # >>>3

    def enable_geometry_morph_tab(self, *args):   # <<<3
        self._geometry_tabs.tab(self._geometry_morph_tab, state=NORMAL)
    # >>>3

    def reset_geometry(self, *args):        # <<<3
        self.geometry = OUTPUT_GEOMETRY
        self.sphere_rotations = SPHERE_ROTATIONS
        self.inversion_center = INVERSION_CENTER
        self.adjust_geometry()
        self.angle = 0
        self.modulus = 1
        self.rotations = 0, 0, 0
    # >>>3

    def zoom(self, alpha):      # <<<3
        def zoom_tmp(*args):
            x_min, x_max, y_min, y_max = self.geometry
            x_c, y_c = (x_min + x_max) / 2, (y_min + y_max) / 2
            delta_x, delta_y = (x_max - x_min) / alpha, (y_max - y_min) / alpha
            x_min, x_max = x_c - delta_x/2, x_c + delta_x/2
            y_min, y_max = y_c - delta_y/2, y_c + delta_y/2
            self.geometry = x_min, x_max, y_min, y_max
        return zoom_tmp
    # >>>3

    def translate(self, dx, dy):    # <<<3
        x_min, x_max, y_min, y_max = self.geometry
        delta_x = x_max - x_min
        delta_y = y_max - y_min
        self.geometry = (x_min + dx*delta_x,
                         x_max + dx*delta_x,
                         y_min + dy*delta_y,
                         y_max + dy*delta_y)
    # >>>3

    def rotate(self, dx, dy, dz=0):   # <<<3
            theta_x, theta_y, theta_z = self.sphere_rotations

            theta_x = theta_x*pi/180
            theta_y = theta_y*pi/180
            theta_z = theta_z*pi/180
            R1 = rotation_matrix(theta_x, theta_y, theta_z)

            R2 = rotation_matrix(10*dz*pi/180, 10*dx*pi/180, -10*dy*pi/180)

            R = matrix_mult(R1, R2)
            theta_x, theta_y, theta_z = tait_angle(R)

            theta_x = round(theta_x * 180 / pi)
            theta_y = round(theta_y * 180 / pi)
            theta_z = round(theta_z * 180 / pi)

            if theta_x < 0:
                theta_x += 360
            if theta_y < 0:
                theta_y += 360
            if theta_z < 0:
                theta_z += 360

            self.sphere_rotations = theta_x, theta_y, theta_z
    # >>>3

    def choose_sphere_background(self, *args):    # <<<3
        filename = filedialog.askopenfilename(
            parent=self,
            title="Create Symmetry: choose background image",
            initialdir="./",
            filetypes=[("images", "*.jpg *.jpeg *.png"), ("all", "*.*")]
        )
        if filename:
            self.sphere_background = filename
    # >>>3

    def update(self, *args):   # <<<3
        if self.draw_orbifold:
            self._draw_mirrors_button.config(state=NORMAL)
        else:
            self._draw_mirrors_button.config(state=DISABLED)

        if self.fade:
            self._fade_coeff.enable()
        else:
            self._fade_coeff.disable()
    # >>>3

    def adjust_geometry(self, *args):       # <<<3
        ratio = self.width / self.height
        x_min, x_max, y_min, y_max = self.geometry
        delta_x = x_max - x_min
        delta_y = y_max - y_min
        if ratio > delta_x/delta_y:
            delta_y = y_max - y_min
            delta_x = delta_y * ratio
            middle_x = (x_min+x_max) / 2
            self.geometry = (middle_x - delta_x/2,
                             middle_x + delta_x/2,
                             y_min,
                             y_max)
        else:
            delta_x = x_max - x_min
            delta_y = delta_x / ratio
            middle_y = (y_min+y_max) / 2
            self.geometry = (x_min,
                             x_max,
                             middle_y - delta_y/2,
                             middle_y + delta_y/2)
    # >>>3

    def pixel_to_xy(self, px, py):      # <<<3
        x_min, x_max, y_min, y_max = self.geometry
        try:
            width, height = self._canvas._image.size
            delta_x = (x_max - x_min) / width
            delta_y = (y_max - y_min) / height
            px_center, py_center = self._canvas.coords(
                self._canvas._image_id
            )
            x_center = (x_max + x_min) / 2
            y_center = (y_max + y_min) / 2
        except AttributeError:
            return
        x = x_center + (px - px_center) * delta_x
        y = y_center + (py_center - py) * delta_y
        return x, y
    # >>>3

    def update_pointer_coordinates(self, px, py):       # <<<3
        if not hasattr(self._canvas, "_pointer_coords"):
            self._canvas._pointer_coords = self._canvas.create_text(
                PREVIEW_SIZE, PREVIEW_SIZE,
                anchor=SE,
                fill="white",
                text=""
            )
        else:
            try:
                x, y = self.pixel_to_xy(px, py)
                self._canvas.itemconfig(
                    self._canvas._pointer_coords,
                    text="{:6.4f} , {:6.4f}".format(x, y)
                )
                self._canvas.tag_raise(self._canvas._pointer_coords)
            except TypeError:       # when self.pixel_to_xy returns None
                pass
    # >>>3

    def start_apply_zoom_rectangle(self, event):   # <<<3
        """the return value is True on the second clic: it means we can perform
        the zoom operation"""
        if not hasattr(self._canvas, "_image_id"):
            return False

        if hasattr(self, "rect"):
            self._canvas.delete(self.rect)
            del self.rect
            x1, y1 = self.pixel_to_xy(self.start_x, self.start_y)
            x2, y2 = self.pixel_to_xy(self.curX, self.curY)
            del self.start_x, self.start_y, self.curX, self.curY
            x_min, x_max = min(x1, x2), max(x1, x2)
            y_min, y_max = min(y1, y2), max(y1, y2)
            self.geometry = x_min, x_max, y_min, y_max
            return True
        else:
            self.start_x = event.x
            self.start_y = event.y
            self.rect = self._canvas.create_rectangle(
                self.start_x,
                self.start_y,
                self.start_x,
                self.start_y,
                width=2,
                outline="white"
            )
            return False
    # >>>3

    def update_zoom_rectangle(self, event):     # <<<3
        if not hasattr(self, "rect"):
            return
        curX, curY = (event.x, event.y)
        ratio = self.width / self.height
        sx = -1 if curX < self.start_x else 1
        sy = -1 if curY < self.start_y else 1
        if curX == self.start_x or curY == self.start_y:
            curX = self.start_x
            curY = self.start_y
        elif ratio > abs(curX-self.start_x) / abs(curY-self.start_y):
            curX = self.start_x + sx * abs(curY-self.start_y) * ratio
        else:
            curY = self.start_y + sy * abs(curX-self.start_x) / ratio
        self._canvas.coords(
            self.rect,
            self.start_x, self.start_y,
            curX, curY
        )
        self.curX = curX
        self.curY = curY
        self.update_pointer_coordinates(curX, curY)
    # >>>3

    def cancel_zoom_rectangle(self, event):     # <<<3
        if hasattr(self, "rect"):
            self._canvas.delete(self.rect)
            del self.rect
        else:
            return
    # >>>3

    @property
    def config(self):           # <<<3
        cfg = {}
        for k in ["geometry_tab",
                  "geometry", "modulus", "angle",
                  "size", "filename_template", "save_directory",
                  "preview_size",
                  "draw_tile", "draw_orbifold", "draw_color_tile",
                  "draw_mirrors", "fade", "fade_coeff",
                  "display_mode", "sphere_rotations", "inversion_center",
                  "sphere_background", "sphere_background_fading",
                  "sphere_stars",
                  "morph", "morph_start", "morph_end", "morph_stable_coeff"]:
            cfg[k] = getattr(self, k)
        return cfg
    # >>>3

    @config.setter
    def config(self, cfg):      # <<<3
        for k in ["geometry_tab",
                  "geometry", "modulus", "angle",
                  "size", "filename_template", "save_directory",
                  "preview_size",
                  "draw_tile", "draw_orbifold", "draw_color_tile",
                  "draw_mirrors", "fade", "fade_coeff",
                  "display_mode", "sphere_rotations", "inversion_center",
                  "sphere_background", "sphere_background_fading",
                  "sphere_stars",
                  "morph", "morph_start", "morph_end", "morph_stable_coeff"]:
            if k in cfg:
                setattr(self, k, cfg[k])
    # >>>3
# >>>2


class Function(LabelFrame):     # <<<2

    # setters and getters <<<3
    @property
    def pattern_type(self):      # <<<4
        if ("plane" in self._tabs.tab(self._tabs.select(), "text")):
            return "wallpaper"
        elif ("sphere" in self._tabs.tab(self._tabs.select(), "text")):
            return "sphere"
        elif ("hyper" in self._tabs.tab(self._tabs.select(), "text")):
            return "hyperbolic"
        else:
            assert False
    # >>>4

    @pattern_type.setter
    def pattern_type(self, tab):      # <<<4
        tab = tab.lower().strip()
        if tab == "plane":
            self._tabs.select(self._wallpaper_tab)
        elif tab == "sphere":
            self._tabs.select(self._sphere_tab)
        elif tab == "hyperbolic":
            self._tabs.select(self._hyper_tab)
    # >>>4

    @property
    def random_nb_coeffs(self):     # <<<4
        return self._random_nb_coeffs.get()
    # >>>4

    @random_nb_coeffs.setter
    def random_nb_coeffs(self, d):     # <<<4
        self._random_nb_coeffs.set(d)
    # >>>4

    @property
    def random_min_degre(self):     # <<<4
        return self._random_min_degre.get()
    # >>>4

    @random_min_degre.setter
    def random_min_degre(self, d):     # <<<4
        self._random_min_degre.set(d)
    # >>>4

    @property
    def random_max_degre(self):     # <<<4
        return self._random_max_degre.get()
    # >>>4

    @random_max_degre.setter
    def random_max_degre(self, d):     # <<<4
        self._random_max_degre.set(d)
    # >>>4

    @property
    def random_modulus(self):     # <<<4
        return self._random_modulus.get()
    # >>>4

    @random_modulus.setter
    def random_modulus(self, d):     # <<<4
        self._random_modulus.set(d)
    # >>>4

    @property
    def random_noise(self):     # <<<4
        return self._random_noise.get()
    # >>>4

    @random_noise.setter
    def random_noise(self, d):     # <<<4
        self._random_noise.set(d)
    # >>>4

    @property
    def sphere_N(self):     # <<<4
        return self._sphere_N.get()
    # >>>4

    @sphere_N.setter
    def sphere_N(self, N):     # <<<4
        self._sphere_N.set(N)
    # >>>4

    @property
    def sphere_mode(self):     # <<<4
        return self._sphere_mode.get()
    # >>>4

    @sphere_mode.setter
    def sphere_mode(self, b):     # <<<4
        self._sphere_mode.set(b)
    # >>>4

    @property
    def change_entry(self):     # <<<4
        return self._change_entry.get().strip()
    # >>>4

    @change_entry.setter
    def change_entry(self, s):     # <<<4
        self._change_entry.set(s)
    # >>>4

    @property
    def wallpaper_pattern(self):    # <<<4
        return self._wallpaper_pattern.get().split()[0]
    # >>>4

    @wallpaper_pattern.setter
    def wallpaper_pattern(self, p):    # <<<4
        values = self._wallpaper_combo["values"]
        for i in range(len(values)):
            tmp = values[i]
            tmp = re.sub("--.*$", "", tmp)
            tmp = tmp.replace("(", " ").replace(")", " ")
            tmp = tmp.split()
            if p in tmp:
                self._wallpaper_combo.current(i)
                return
        self._wallpaper_combo.current(0)
    # >>>4

    @property
    def wallpaper_color_pattern(self):    # <<<4
        p = self._wallpaper_color_pattern.get().split()[0]
        if p == "--":
            return ""
        else:
            return p
    # >>>4

    @wallpaper_color_pattern.setter
    def wallpaper_color_pattern(self, p):    # <<<4
        values = self._wallpaper_color_combo["values"]
        for i in range(len(values)):
            tmp = values[i]
            tmp = re.sub("--.*$", "", tmp)
            tmp = tmp.replace("(", " ").replace(")", " ")
            tmp = tmp.split()
            if p in tmp:
                self._wallpaper_color_combo.current(i)
                return
        self._wallpaper_color_combo.current(0)
    # >>>4

    @property
    def wallpaper_N(self):     # <<<4
        return self._wallpaper_N.get()
    # >>>4

    @wallpaper_N.setter
    def wallpaper_N(self, N):     # <<<4
        self._wallpaper_N.set(N)
    # >>>4

    @property
    def sphere_pattern(self):    # <<<4
        return self._sphere_pattern.get().split()[0]
    # >>>4

    @sphere_pattern.setter
    def sphere_pattern(self, p):    # <<<4
        if self.sphere_mode in ["frieze", "rosette"]:
            patterns = F_NAMES
        else:
            patterns = S_NAMES
        for i in range(len(patterns)):
            tmp = patterns[i]
            tmp = tmp.replace("(", " ").replace(")", " ")
            tmp = tmp.split()
            if p in tmp:
                self._sphere_combo.current(i)
                return
        self._sphere_combo.current(0)
    # >>>4

    @property
    def full_wallpaper_pattern(self):          # <<<4
        color_pattern = self.wallpaper_color_pattern
        if color_pattern:
            return (color_pattern, self.wallpaper_pattern)
        else:
            return self.wallpaper_pattern
        return self.wallpaper_pattern
    # >>>4

    @property
    def lattice_parameters(self):
        return self._lattice_parameters.get()
    # >>>4

    @lattice_parameters.setter
    def lattice_parameters(self, l):
        self._lattice_parameters.set(floats_to_str(l))
    # >>>4

    @property
    def hyper_nb_steps(self):       # <<<4
        return self._hyper_nb_steps.get()
    # >>>4

    @hyper_nb_steps.setter          # <<<4
    def hyper_nb_steps(self, n):
        self._hyper_nb_steps.set(n)
    # >>>4

    @property
    def hyper_s(self):       # <<<4
        return self._hyper_s.get()
    # >>>4

    @hyper_s.setter          # <<<4
    def hyper_s(self, s):
        z = complex(s)
        s = complex_to_str(z)
        self._hyper_s.set(s)
    # >>>4
    # >>>3

    def __init__(self, root):      # <<<3
        self.root = root
        LabelFrame.__init__(self, root)
        self.configure(text="Pattern")

        # tabs for the different kinds of functions / symmetries  <<<4
        self._tabs = Notebook(self)
        self._tabs.grid(row=0, column=0, rowspan=2, sticky=N+S, padx=5, pady=5)
        # prevent arrows from changing tab
        self._tabs.bind_all(
            "<<NotebookTabChanged>>",
            lambda _: self.focus_set()
        )

        self._wallpaper_tab = Frame(self._tabs)
        self._tabs.add(self._wallpaper_tab, text="plane")

        self._sphere_tab = Frame(self._tabs)
        self._tabs.add(self._sphere_tab, text="sphere")

        self._hyper_tab = Frame(self._tabs)
        self._tabs.add(self._hyper_tab, text="hyperbolic")
        # >>>4

        # wallpaper tab      <<<4
        Label(
            self._wallpaper_tab,
            text="symmetry group"
        ).pack(padx=5, pady=(20, 0))
        self._wallpaper_pattern = StringVar()
        self._wallpaper_combo = Combobox(
            self._wallpaper_tab, width=24, exportselection=0,
            textvariable=self._wallpaper_pattern,
            state="readonly",
            values=W_NAMES
        )
        self._wallpaper_combo.pack(padx=5, pady=5)
        self._wallpaper_combo.current(0)
        self._wallpaper_combo.bind(
            "<<ComboboxSelected>>",
            self.update
        )
        # remove focus to prevent Ctrl-Down from displaying the dropdown menu
        self._wallpaper_combo.bind(
            "<FocusIn>",
            lambda _: self.focus_set()
        )

        Label(
            self._wallpaper_tab,
            text="color symmetry group"
        ).pack(padx=5, pady=(5, 0))
        self._wallpaper_color_pattern = StringVar()
        self._wallpaper_color_combo = Combobox(
            self._wallpaper_tab, width=20, exportselection=0,
            textvariable=self._wallpaper_color_pattern,
            state="readonly",
            values=["--"]
        )
        self._wallpaper_color_combo.pack(padx=5, pady=5)
        self._wallpaper_color_combo.current(0)
        self._wallpaper_color_combo.bind(
            "<<ComboboxSelected>>",
            self.update
        )
        # remove focus to prevent Ctrl-Down from displaying the dropdown menu
        self._wallpaper_color_combo.bind(
            "<FocusIn>",
            lambda _: self.focus_set()
        )

        self._lattice_parameters = LabelEntry(
            self._wallpaper_tab,
            orientation="V",
            label="lattice parameters",
            value="",
            convert=str_to_floats,
            width=10
        )
        self._lattice_parameters.pack(padx=5, pady=5)

        self._wallpaper_N = LabelEntry(
            self._wallpaper_tab,
            orientation="V",
            label="forced rotational symmetry",
            value=1,
            convert=int,
            width=3
        )
        self._wallpaper_N.pack(padx=5, pady=5)
        self._wallpaper_N.disable()
        self._wallpaper_N.bind(
            "<Double-Button-1>",
            sequence(self._wallpaper_N.toggle)
        )
        # # >>>4

        # sphere tab        <<<4
        Label(
            self._sphere_tab,
            text="symmetry group"
        ).pack(padx=5, pady=(20, 0))
        self._sphere_pattern = StringVar()
        self._sphere_combo = Combobox(
            self._sphere_tab,
            width=20,
            exportselection=0,
            textvariable=self._sphere_pattern,
            state="readonly",
            values=S_NAMES
        )
        self._sphere_combo.pack(padx=5, pady=5)
        self._sphere_combo.current(0)
        self._sphere_combo.bind(
            "<<ComboboxSelected>>",
            self.update
        )

        self._sphere_N = LabelEntry(
            self._sphere_tab,
            label="N",
            value=7,
            convert=int,
            width=2
        )
        self._sphere_N.pack(padx=5, pady=5)

        radio_frame = Frame(self._sphere_tab)
        radio_frame.pack(padx=5, pady=(10, 5))
        self._sphere_mode = StringVar()
        self._sphere_mode.set("sphere")
        Radiobutton(
            radio_frame,
            indicatoron=0,
            text="sphere",
            variable=self._sphere_mode,
            value="sphere",
            command=self.update
        ).grid(row=0, column=0, padx=5, pady=5)
        Radiobutton(
            radio_frame,
            indicatoron=0,
            text="rosette",
            variable=self._sphere_mode,
            value="rosette",
            command=self.update
        ).grid(row=0, column=1, padx=5, pady=5)
        Radiobutton(
            radio_frame,
            indicatoron=0,
            text="frieze",
            variable=self._sphere_mode,
            value="frieze",
            command=self.update
        ).grid(row=0, column=2, padx=5, pady=5)
        # >>>4

        # hyperbolic tab        <<<4
        Label(self._hyper_tab, text="modular group").pack(padx=5, pady=(20, 5))

        self._hyper_nb_steps = LabelEntry(
            self._hyper_tab,
            label="averaging steps",
            width=5,
            convert=int,
            value=25
        )
        self._hyper_nb_steps.pack(padx=5, pady=5)

        self._hyper_s = LabelEntry(
            self._hyper_tab,
            label="s",
            convert=str_to_complex,
            value=3,
            width=6,
        )
        self._hyper_s.pack(padx=5, pady=5)
        # >>>4

        # display matrix    <<<4
        main_matrix_frame = LabelFrame(self, text="matrix")
        main_matrix_frame.grid(
            row=0, column=1,
            sticky=N+S+E+W,
            padx=5, pady=5
        )

        scroll_matrix_frame = Frame(main_matrix_frame)
        scroll_matrix_frame.pack()
        self._display_matrix = Listbox(
            scroll_matrix_frame,
            selectmode=MULTIPLE,
            font="TkFixedFont",
            width=26, height=8
        )
        self._display_matrix.pack(side=LEFT)

        scrollbar = Scrollbar(scroll_matrix_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        self._display_matrix.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self._display_matrix.yview)

        self._display_matrix.bind("<BackSpace>", self.remove_entries)
        self._display_matrix.bind("<Delete>", self.remove_entries)

        self.change_matrix({})
        # >>>4

        # change entries <<<4
        self._change_entry = LabelEntry(
            main_matrix_frame,
            label="change entry",
            value="",
            width=15,
            font="TkFixedFont"
        )
        self._change_entry.pack(padx=5, pady=5)
        self._change_entry.bind("<Return>", self.add_entry)

        Button(
            main_matrix_frame, text="make matrix",
            command=self.make_matrix
        ).pack(side=LEFT, padx=5, pady=10)

        Button(
            main_matrix_frame,
            text="reset",
            command=lambda *_: self.change_matrix({})
        ).pack(side=RIGHT, padx=5, pady=5)
        # >>>4

        # random matrix     <<<4
        random_frame = LabelFrame(self, text="random matrix")
        random_frame.grid(row=0, column=2, sticky=N+S, padx=5, pady=5)

        self._random_nb_coeffs = LabelEntry(
            random_frame,
            label="nb entries",
            value=3,
            convert=int,
            width=4
        )
        self._random_nb_coeffs.pack(padx=5, pady=5)

        self._random_min_degre = LabelEntry(
            random_frame, label="min degre",
            value=-3,
            convert=int,
            width=4
        )
        self._random_min_degre.pack(padx=5, pady=5)

        self._random_max_degre = LabelEntry(
            random_frame,
            label="max degre",
            value=3,
            convert=int,
            width=4
        )
        self._random_max_degre.pack(padx=5, pady=5)

        self._random_modulus = LabelEntry(
            random_frame,
            label="modulus",
            value=1,
            convert=float,
            width=4
        )
        self._random_modulus.pack(padx=5, pady=5)

        generate = Button(
            random_frame,
            text="generate",
            command=self.new_random_matrix
        )
        generate.pack(padx=5, pady=5)
        # >>>4

        # add noise <<<4
        self._random_noise = LabelEntry(
            random_frame,
            label="",
            value=25,
            convert=float,
            width=3)
        self._random_noise.pack(side=RIGHT, padx=5, pady=5)
        self._random_noise.bind("<Return>", self.add_noise)

        random_noise = Button(
            random_frame,
            text="noise (%)",
            command=self.add_noise
        )
        random_noise.pack(side=LEFT, padx=5, pady=5)
        # >>>4

        # make sure the layout reflects the selected options    <<<4
        self.update()
        # >>>4
    # >>>3

    def change_matrix(self, M=None):    # <<<3
        if M is None:
            M = self.matrix
        else:
            self.matrix = dict(M)
        self._display_matrix.delete(0, END)
        keys = list(M.keys())
        keys.sort()

        for (n, m) in keys:
            self._display_matrix.insert(
                    END,
                    "{:2}, {:2} : {}"
                    .format(n, m, complex_to_str(M[(n, m)], precision=3)))
    # >>>3

    def new_random_matrix(self, *args):     # <<<3
        M = random_matrix(
            self.random_nb_coeffs,
            self.random_min_degre,
            self.random_max_degre,
            self.random_modulus
        )
        # M = self.add_symmetries(M)
        self.change_matrix(M)
    # >>>3

    def add_entry(self, *args):     # <<<3
        e = self.change_entry
        if e == "":
            return
        try:
            tmp = re.split("\s*(?:[,;:]|(?:[-=]>))\s*", e)
            n, m, z = tmp
            n = n.strip(" ()")
            m = m.strip(" ()")
            n = int(n)
            m = int(m)
            z = str_to_complex(z)
            if z == 0:
                if (n, m) in self.matrix:
                    del self.matrix[n, m]
            else:
                self.matrix[(n, m)] = z
            self.change_matrix()
            self.change_entry = ""
        except Exception as err:
            error("cannot parse matrix entry '{}': {}".format(e, err))
        # >>>3

    def remove_entries(self, *args):        # <<<3
        entries = self._display_matrix.curselection()
        p = 0
        for e in entries:
            tmp = self._display_matrix.get(e-p)
            n, m, _ = re.split("\s*(?:[,;:]|(?:[-=]>))\s*", tmp)
            self.matrix.pop((int(n), int(m)))
            self._display_matrix.delete(e-p, e-p)
            p += 1
    # >>>3

    def add_noise(self, *args):     # <<<3
        try:
            e = self.random_noise/100
        except:
            e = 0.2
        M = self.matrix
        for n, m in M:
            z = M[(n, m)]
            modulus = abs(z) * uniform(0, e)
            angle = uniform(0, 2*pi)
            M[(n, m)] = z + modulus * complex(cos(angle), sin(angle))
        self.change_matrix()
    # >>>3

    def make_matrix(self):       # <<<3
        M = self.matrix
        self.change_matrix(self.add_symmetries(M))
    # >>>3

    def add_symmetries(self, M):        # <<<3

        if self.pattern_type == "wallpaper":
            pattern = self.wallpaper_pattern
            color_pattern = self.wallpaper_color_pattern
            if color_pattern:
                M = add_symmetries(
                    M,
                    PATTERN[color_pattern, pattern]["recipe"],
                    PATTERN[color_pattern, pattern]["parity"]
                )
            else:
                M = add_symmetries(M, PATTERN[pattern]["recipe"])
        elif self.pattern_type == "sphere":
            M = add_symmetries(
                M,
                PATTERN[self.sphere_pattern]["recipe"],
                PATTERN[self.sphere_pattern]["parity"]
                .replace("N", str(self.sphere_N))
            )
        elif self.pattern_type == "hyperbolic":
            pass
        else:
            assert False
        return M
    # >>>3

    @property
    def config(self):           # <<<3
        cfg = {}
        for k in ["matrix",
                  "random_nb_coeffs", "random_min_degre",
                  "random_max_degre", "random_modulus", "random_noise",
                  "pattern_type",
                  "wallpaper_pattern", "lattice_parameters",
                  "wallpaper_color_pattern", "wallpaper_N",
                  "sphere_pattern", "sphere_N", "sphere_mode",
                  "hyper_nb_steps", "hyper_s"]:
            cfg[k] = getattr(self, k)
        return cfg
    # >>>3

    @config.setter
    def config(self, cfg):      # <<<3
        for k in ["random_nb_coeffs", "random_min_degre",
                  "random_max_degre", "random_modulus", "random_noise",
                  "pattern_type",
                  "wallpaper_pattern",  "wallpaper_N",  # "lattice_parameters",
                  # "wallpaper_color_pattern",
                  "sphere_pattern", "sphere_N", "sphere_mode",
                  "hyper_nb_steps", "hyper_s"]:
            if k in cfg:
                setattr(self, k, cfg[k])
        self.update()
        # FIXME: not very nice
        # we need to set wallpaper_color_pattern after the combobox has been
        # updated with actual color patterns
        if "wallpaper_color_pattern" in cfg:
            self.wallpaper_color_pattern = cfg["wallpaper_color_pattern"]
        # we need to update again to configure the lattice parameters correctly
        self.update()
        # we can now set the lattice_parameters
        if "lattice_parameters" in cfg and cfg["lattice_parameters"]:
            self.lattice_parameters = cfg["lattice_parameters"]

        if "matrix" in cfg:
            cfg["matrix"] = list_to_matrix(cfg["matrix"])
            self.change_matrix(cfg["matrix"])
    # >>>3

    def update(self, *args):     # <<<3
        # sphere tab  <<<4
        pattern = self.sphere_pattern
        if self.sphere_mode in ["frieze", "rosette"]:
            self._sphere_combo["values"] = F_NAMES
            pattern = pattern.replace("N", "∞")
            self.sphere_pattern = pattern
            self._sphere_N.label_widget.configure(text="period")
            self._sphere_N.enable()
        elif self.sphere_mode == "sphere":
            pattern = pattern.replace("∞", "N")
            self._sphere_combo["values"] = S_NAMES
            self.sphere_pattern = pattern
            self._sphere_N.label_widget.configure(text="N")
            if "N" in self.sphere_pattern:
                self._sphere_N.enable()
            else:
                self._sphere_N.disable()
        # >>>4

        # wallpaper tab     <<<4
        color_pattern = self.wallpaper_color_pattern
        try:
            lattice_parameters = self.lattice_parameters
        except:
            lattice_parameters = None

        # color reversing combo
        self._wallpaper_color_combo.configure(
            values=["--"] + C_NAMES(self.wallpaper_pattern)
        )
        self.wallpaper_color_pattern = color_pattern

        if lattice_parameters is not None:
            try:
                self._lattice_parameters.convert(lattice_parameters)
                self.lattice_parameters = lattice_parameters
            except:
                pass

        if self.wallpaper_color_pattern:
            pattern = self.wallpaper_color_pattern, self.wallpaper_pattern
        else:
            pattern = self.wallpaper_pattern

        lattice = PATTERN[pattern]["description"]
        lattice0 = lattice.split()[0]

        def not_zero(s):
            x = float(s)
            assert x != 0
            return [x]

        def det_not_null(s):
            xs = str_to_floats(s)
            assert len(xs) == 4
            assert xs[0]*xs[3] - xs[1]*xs[2] != 0
            return xs

        if lattice0 == "general":
            self._lattice_parameters.enable()
            self._lattice_parameters.label_widget.config(
                text=lattice0 + ": x1,y1,x2,y2"
            )
            self._lattice_parameters.convert = det_not_null
            self.lattice_parameters = [1, 0, 1, 1]
        elif lattice0 == "rhombic":
            self._lattice_parameters.enable()
            self._lattice_parameters.label_widget.config(
                text=lattice0 + ": b"
            )
            self._lattice_parameters.convert = not_zero
            self.lattice_parameters = [.5]
        elif lattice0 == "rectangular":
            self._lattice_parameters.enable()
            self._lattice_parameters.convert = not_zero
            self.lattice_parameters = [.5]
            self._lattice_parameters.label_widget.config(
                text=lattice0 + ": H"
            )
        elif lattice0 == "square":
            self._lattice_parameters.convert = None
            self.lattice_parameters = []
            self._lattice_parameters.label_widget.config(text=lattice0)
            self._lattice_parameters.disable()
        elif lattice0 == "hexagonal":
            self._lattice_parameters.convert = None
            self.lattice_parameters = []
            self._lattice_parameters.label_widget.config(text=lattice0)
            self._lattice_parameters.disable()
        else:
            assert False
        # >>>4
    # >>>3
# >>>2


class CreateSymmetry(Tk):      # <<<2

    # getters and setters <<<3
    @property
    def config(self):       # <<<4
        return {"colorwheel": self.colorwheel.config,
                "function": self.function.config,
                "output": self.output.config,
                "working_directory": normalize_path(os.getcwd())}
    # >>>4

    @config.setter
    def config(self, cfg):      # <<<4
        if "working_directory" in cfg:
            os.chdir(os.path.expanduser(cfg["working_directory"]))
        self.colorwheel.config = cfg.get("colorwheel", {})
        self.output.config = cfg.get("output", {})
        self.function.config = cfg.get("function", {})
    # >>>4

    @property
    def pending_preview(self):
        try:
            return self.preview_process.is_alive()
        except AttributeError:
            return False
    # >>>3

    @property
    def pending_outputs(self):
        try:
            return self.output_process.is_alive()
        except AttributeError:
            return False
    # >>>3

    def __init__(self):     # <<<3

        # tk interface
        Tk.__init__(self)
        self.resizable(width=False, height=False)
        # self.geometry("1200x600")
        self.title("Create Symmetry")

        s = Style()
        s.configure("*TCombobox*Listbox*Font", "TkFixedFont")
        fixed_font = tkinter.font.nametofont("TkFixedFont")
        fixed_font.configure(size=8)

        # components    <<<4
        self.colorwheel = ColorWheel(self)

        self.output = Output(self)

        self.function = Function(self)

        self.colorwheel.grid(row=0, column=0, sticky=N+S, padx=10, pady=10)
        self.output.grid(row=0, column=1, sticky=N+S, padx=10, pady=10)
        self.function.grid(row=1, column=1, sticky=E+W, padx=10, pady=10)

        console_frame = Frame(self)
        console_frame.grid(row=1, column=0, padx=0, pady=0)

        self._console = Text(
            console_frame,
            width=28, height=15,
            background="black", foreground="white",
            font="TkFixedFont",
            borderwidth=3,
            relief=RIDGE
        )
        self._console.grid(
            row=1, column=0,
            sticky=E+W+N+S,
            padx=10, pady=(10, 0)
        )
        self._console.config(state=DISABLED)

        self._preview_console = Text(
            console_frame, width=10, height=1,
            background="black", foreground="white",
            font="TkFixedFont",
            borderwidth=3,
            relief=RIDGE
        )
        self._preview_console.grid(
            row=2, column=0,
            sticky=E+W,
            padx=10, pady=0
        )
        self._preview_console.config(state=DISABLED)

        self._output_console = Text(
            console_frame,
            width=10, height=1,
            background="black", foreground="white",
            font="TkFixedFont",
            borderwidth=3,
            relief=RIDGE
        )
        self._output_console.grid(
            row=3, column=0,
            sticky=E+W,
            padx=10, pady=(0, 10)
        )
        self._output_console.config(state=DISABLED)
        # >>>4

        # attach appropriate actions to buttons     <<<4
        self.output._preview_button.config(command=sequence(self.make_preview))
        # >>>4

        # keybindings       <<<4
        self.bind("<Control-h>", sequence(self.display_help))
        self.bind("?", sequence(self.display_help))
        self.bind("<F1>", sequence(self.display_help))

        self.bind("<Control-q>", sequence(self.quit))

        self.bind("<Control-p>", sequence(self.make_preview))
        self.bind("<Control-s>", sequence(self.make_output))
        self.bind("<Control-S>", sequence(self.save_preview))

        self.bind("<Control-n>", sequence(self.function.add_noise))
        self.bind("<Control-N>", sequence(self.function.add_noise,
                                          self.make_preview))

        self.bind("<Control-g>", sequence(self.function.new_random_matrix))
        self.bind("<Control-G>", sequence(self.new_random_preview))

        self.bind(
            "<Control-Key-minus>",
            sequence(
                self.output.zoom(1/ZOOM_FACTOR),
                self.make_preview
            )
        )
        self.bind(
            "<Control-Key-plus>",
            sequence(
                self.output.zoom(ZOOM_FACTOR),
                self.make_preview
            )
        )

        self.bind("<Control-Key-Left>", sequence(self.translate_rotate(1, 0),
                                                 self.make_preview))
        self.bind("<Control-Key-Right>", sequence(self.translate_rotate(-1, 0),
                                                  self.make_preview))
        self.bind("<Control-Key-Up>", sequence(self.translate_rotate(0, -1),
                                               self.make_preview))
        self.bind("<Control-Key-Down>", sequence(self.translate_rotate(0, 1),
                                                 self.make_preview))
        self.bind("<Control-z>", sequence(self.translate_rotate(0, 0, -1),
                                          self.make_preview))
        self.bind("<Control-Z>", sequence(self.translate_rotate(0, 0, 1),
                                          self.make_preview))
        self.bind("<Control-0>", sequence(self.output.reset_geometry,
                                          self.make_preview))

        self.bind("<Control-u>", sequence(self.undo))
        self.bind("<Control-r>", sequence(self.redo))
        self.bind("<Control-U>", sequence(self.undo,
                                          self.make_preview))
        self.bind("<Control-R>", sequence(self.redo,
                                          self.make_preview))

        self.output._canvas.bind("<Double-Button-1>", self.show_bigger_preview)

        def apply_zoom(event):
            if self.output.start_apply_zoom_rectangle(event):
                self.make_preview()

        self.output._canvas.bind("<Button-1>", apply_zoom)
        # >>>4

        # menu <<<4
        menu = Menu(self)
        self.configure(menu=menu)

        file_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="file", menu=file_menu)

        file_menu.add_command(
            label="preview",
            accelerator="Ctrl-p",
            command=sequence(self.make_preview)
        )
        file_menu.add_command(
            label="save image",
            accelerator="Ctrl-s",
            command=sequence(self.make_output)
        )
        file_menu.add_command(
            label="save preview image",
            accelerator="Ctrl-S",
            command=sequence(self.save_preview)
        )
        file_menu.add_command(
            label="save config",
            command=self.save_config
        )
        file_menu.add_command(
            label="load config",
            command=self.load_config
        )
        file_menu.add_command(
            label="quit",
            accelerator="Ctrl-q",
            command=sequence(self.quit)
        )

        edit_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="edit", menu=edit_menu)

        edit_menu.add_command(
            label="undo",
            accelerator="Ctrl-u",
            command=sequence(self.undo)
        )
        edit_menu.add_command(
            label="redo",
            accelerator="Ctrl-r",
            command=sequence(self.redo)
        )

        color_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="colorwheel", menu=color_menu)

        color_menu.add_command(
            label="choose colorwheel",
            command=sequence(self.colorwheel.choose_colorwheel)
        )
        color_menu.add_command(
            label="switch to alt. colorwheel",
            command=sequence(self.colorwheel.switch_colorwheel),
            # accelerator="Double-clic"
        )
        color_menu.add_command(
            label="reset geometry",
            command=sequence(self.colorwheel.reset_geometry)
        )
        color_menu.add_checkbutton(
            label="stretch unit disk",
            onvalue=True, offvalue=False,
            variable=self.colorwheel._stretch_color
        )

        output_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="output", menu=output_menu)

        output_menu.add_command(
            label="zoom -",
            accelerator="Ctrl--",
            command=sequence(
                self.output.zoom(1/ZOOM_FACTOR),
                self.make_preview
            )
        )
        output_menu.add_command(
            label="zoom +",
            accelerator="Ctrl-+",
            command=sequence(self.output.zoom(ZOOM_FACTOR), self.make_preview)
        )
        output_menu.add_command(
            label="reset output",
            accelerator="Ctrl-0",
            command=sequence(self.output.reset_geometry)
        )
        output_menu.add_command(
            label="change save dir",
            command=sequence(self.output.change_save_dir)
        )

        # function_menu = Menu(menu, tearoff=False)
        # menu.add_cascade(label="function", menu=function_menu)

        about_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label="about", menu=about_menu)

        about_menu.add_command(
            label="help",
            accelerator="Ctrl-h",
            command=sequence(self.display_help)
        )

        about_menu.add_command(
            label="about",
            command=sequence(self.display_about)
        )
        # >>>4

        # updating events <<<4
        self.function._tabs.bind(
            "<<NotebookTabChanged>>",
            self.update
        )
        self.function._sphere_mode.trace(
            "w",
            callback=self.update
        )

        # update settings (checkbutton for showing orbifold for color pattern)
        self.function._wallpaper_combo.bind(
            "<<ComboboxSelected>>",
            self.update,
            add="+"
        )
        self.function._wallpaper_color_combo.bind(
            "<<ComboboxSelected>>",
            self.update,
            add="+"
        )

        self.output._draw_tile_button.config(
            command=self.update_output_preview
        )
        self.output._draw_orbifold_button.config(
            command=self.update_output_preview
        )
        self.output._draw_color_tile_button.config(
            command=self.update_output_preview
        )
        self.output._draw_mirrors_button.config(
            command=self.update_output_preview
        )
        self.output._fade_button.config(
            command=self.update_output_preview
        )
        self.output._fade_coeff.bind(
            "<Return>",
            self.update_output_preview
        )
        self.output._fade_coeff.bind(
            "<FocusOut>",
            self.update_output_preview
        )
        # >>>4

        # initialisations  <<<4
        # list of matrices, for UNDO
        self.undo_list = []
        self.undo_index = -1

        # queue containing parameters for pending output jobs
        self.output_params_queue = Queue()
        # are there pending output jobs?
        self.output_message_queue = Queue()

        # queue containing the preview image, computed by make_preview_job
        # the function ``update_GUI`` empties the queue
        self.preview_image_queue = Queue()
        self.preview_message_queue = Queue()

        self.message_queue = Queue()
        self.message_queue.put("""  create_symmetry.py
 Control-h for shortcuts
-------------------------
""")
        self.update_GUI()
    # >>>4
    # >>>3

    def quit(self, *args):     # <<<3
        if self.pending_outputs:
            r = messagebox.askokcancel(
                parent=self,
                title="Create Symmetry: quit",
                message="There are pending output job(s). "
                        "Kill them and quit?")
            if r:
                self.output_process.terminate()
                self.preview_process.terminate()
                self.destroy()
            else:
                return
        else:
            self.destroy()
    # >>>3

    def display_help(self):     # <<<3
        dialog = Toplevel(self)
        dialog.resizable(width=False, height=False)

        text = Text(
            dialog,
            height=40,
            background="lightgrey",
            relief=FLAT,
            font="TkFixedFont"
        )
        text.pack()
        text.insert(END, """
Keyboard shortcuts:

  Control-h     this help message
  F1            this help message
  ?             this help message

  Control-q     quit

  Control-p     compute and display preview
  Control-s     compute and save result to file
  Control-S     save current preview to file

  Control-n     add noise to matrix
  Control-N     add noise to matrix and display preview

  Control-g     generate random matrix
  Control-G     generate random matrix and display preview

  Control--     zoom out the result file and display preview
  Control-+     zoom in the result file and display preview

  Control-0     reset geometry of output and display preview

  Control-Up    translate the result and display preview
  Control-Down  (for spherical patterns, rotate instead)
  Control-Right
  Control-Left

  Control-z
  Control-Z     rotate around z-axis

  Control-u     undo: go back to previous state
  Control-r     redo
  Control-U     undo: go back to previous state and compute preview
  Control-R     redo
""")
        text.config(state=DISABLED)

        dialog.bind("<Escape>", lambda _: dialog.destroy())
        dialog.bind("<Control-q>", lambda _: dialog.destroy())
        ok = Button(
            dialog,
            text="OK",
            command=lambda: dialog.destroy()
        )
        ok.pack(padx=10, pady=10)
        ok.focus_set()
        self.wait_window(dialog)
    # >>>3

    def display_about(self):        # <<<3
        dialog = Toplevel(self)
        dialog.resizable(width=False, height=False)

        text = Text(
            dialog,
            background="lightgrey",
            height=12,
            width=60,
            relief=FLAT,
            font="TkFixedFont"
        )
        text.pack()
        text.insert(END, """
create symmetry
===============

a Python program to compute wallpaper patterns based on
Frank Farris book "creating symmetry"

author: Pierre Hyvernat
contact: Pierre.Hyvernat@univ-smb.fr
""")
        text.config(state=DISABLED)

        dialog.bind("<Escape>", lambda _: dialog.destroy())
        dialog.bind("<Control-q>", lambda _: dialog.destroy())
        ok = Button(
            dialog,
            text="OK",
            command=lambda: dialog.destroy()
        )
        ok.pack(padx=10, pady=10)
        ok.focus_set()
        self.wait_window(dialog)
    # >>>3

    def update(self, *args):       # <<<3
        if self.function.pattern_type in ["sphere"]:
            if self.function.sphere_mode == "rosette":
                self.output.enable_mode_tab()
                self.output.display_mode = "plain"
                self.output.geometry_tab = "mode"
                self.output.disable_geometry_morph_tab()
            elif self.function.sphere_mode == "frieze":
                self.output.disable_mode_tab()
                self.output.display_mode = "plain"
                self.output.geometry_tab = "geometry"
                self.output.disable_geometry_morph_tab()
            elif self.function.sphere_mode == "sphere":
                self.output.enable_mode_tab()
                self.output.display_mode = "sphere"
                self.output.geometry_tab = "mode"
                self.output.disable_geometry_morph_tab()
                self.output.sphere_stars = NB_STARS
            else:
                assert False
        elif self.function.pattern_type in ["wallpaper"]:
            self.output.disable_mode_tab()
            self.output.display_mode = "plain"
            self.output.enable_geometry_morph_tab()
        elif self.function.pattern_type in ["hyperbolic"]:
            self.output.enable_mode_tab()
            self.output.display_mode = "inversion"
            self.output.disable_geometry_morph_tab()
            self.output.sphere_stars = 0

        # enable / disable tiling / orbifold drawing buttons
        if self.function.pattern_type in ["sphere", "hyperbolic"]:
            self.output.draw_tile = False
            self.output.draw_orbifold = False
            self.output.draw_mirrors = False
            self.output.fade = False
            self.output._draw_tile_button.config(state=DISABLED)
            self.output._draw_orbifold_button.config(state=DISABLED)
            self.output._draw_color_tile_button.config(state=DISABLED)
            self.output._draw_mirrors_button.config(state=DISABLED)
            self.output._fade_button.config(state=DISABLED)
            self.output._fade_coeff.disable()
        else:
            self.output._draw_tile_button.config(state=NORMAL)
            self.output._draw_orbifold_button.config(state=NORMAL)
            self.output._draw_mirrors_button.config(state=NORMAL)
            self.output._fade_button.config(state=NORMAL)
            self.output._fade_coeff.enable()
            if self.function.wallpaper_color_pattern == "":
                self.output._draw_color_tile_button.config(state=DISABLED)
            else:
                self.output._draw_color_tile_button.config(state=NORMAL)
            self.update_output_preview()
            self.output.update()

    # >>>3

    def update_output_preview(self, *args):       # <<<3
        self.output._canvas.delete("preview")
        try:
            if self.output.fade:
                fade = fade_image(
                    self.output._canvas._image,
                    255-self.output.fade_coeff
                )
                self.output._canvas.tk_img = PIL.ImageTk.PhotoImage(fade)
            else:
                self.output._canvas.tk_img = PIL.ImageTk.PhotoImage(
                    self.output._canvas._image
                )

            self.output._canvas._image_id = self.output._canvas.create_image(
                (PREVIEW_SIZE//2, PREVIEW_SIZE//2),
                image=self.output._canvas.tk_img,
                tags="preview"
            )
        except AttributeError:
            pass

        if self.output.display_mode != "plain" or self.output.morph:
            return

        def put_tile(name):
            try:
                if isinstance(getattr(self.output._canvas, name), tuple):
                    img = make_tile(*getattr(self.output._canvas, name))
                    tk_img = PIL.ImageTk.PhotoImage(img)
                    setattr(self.output._canvas, name, img)
                    setattr(self.output._canvas, "tk" + name, tk_img)
                img_id = self.output._canvas.create_image(
                    (PREVIEW_SIZE//2, PREVIEW_SIZE//2),
                    image=getattr(self.output._canvas, "tk" + name),
                    tags="preview"
                )
                setattr(self.output._canvas, name + "_id", img_id)
            except AttributeError:
                pass

        if self.output.draw_tile:
            if self.output.draw_color_tile:
                put_tile("_color_tile_img")
            else:
                put_tile("_tile_img")

        if self.output.draw_orbifold:
            if self.output.draw_color_tile:
                put_tile("_color_orbifold_img")
            else:
                put_tile("_orbifold_img")

        if self.output.draw_orbifold and self.output.draw_mirrors:
            if self.output.draw_color_tile:
                put_tile("_color_mirrors_img")
            else:
                put_tile("_mirrors_img")

    # >>>3

    def update_GUI(self):        # <<<3

        # console messages
        self._console.config(state=NORMAL)
        while not self.message_queue.empty():
            self._console.insert(
                END,
                self.message_queue.get(block=False) + "\n"
            )
        self._console.yview(END)
        self._console.config(state=DISABLED)

        m = None
        while True:
            try:
                m = self.preview_message_queue.get(block=False)
            except queue.Empty:
                if m is not None:
                    self._preview_console.config(state=NORMAL)
                    self._preview_console.delete(0.0, END)
                    self._preview_console.insert(
                        0.0,
                        "Preview: {}%".format(int(m*100))
                    )
                    self._preview_console.config(state=DISABLED)
                elif not self.pending_preview:
                    self._preview_console.config(state=NORMAL)
                    self._preview_console.delete(0.0, END)
                    self._preview_console.config(state=DISABLED)
                break

        m = None
        while True:
            try:
                m = self.output_message_queue.get(block=False)
            except queue.Empty:
                if m is not None:
                    self._output_console.config(state=NORMAL)
                    self._output_console.delete(0.0, END)
                    self._output_console.insert(
                        0.0,
                        "output ({}): {}%"
                        .format(1+self.output_params_queue.qsize(),
                                round(m*100, 3))
                    )
                    self._output_console.config(state=DISABLED)
                elif not self.pending_outputs:
                    self._output_console.config(state=NORMAL)
                    self._output_console.delete(0.0, END)
                    self._output_console.config(state=DISABLED)
                break

        # preview image
        image = None
        while True:
            try:
                image = self.preview_image_queue.get(block=False)
            except queue.Empty:
                if image is not None:
                    # FIXME: methode change_preview in Output class

                    self.output._canvas._image = image
                    self.output._canvas.tk_img = PIL.ImageTk.PhotoImage(image)

                    self.output._canvas._image_id = self.output._canvas.create_image(
                        (PREVIEW_SIZE//2, PREVIEW_SIZE//2),
                        image=self.output._canvas.tk_img
                    )

                    if self.function.pattern_type == "wallpaper":
                        pattern = self.function.full_wallpaper_pattern

                        # name all argument of make tile and use dictionary
                        self.output._canvas._tile_img = (
                            self.output.geometry,
                            (self.output.modulus, self.output.angle),
                            pattern,
                            basis(pattern,
                                  *self.function.lattice_parameters),
                            image.size,
                            True,
                            False,
                            False,
                            False
                        )

                        self.output._canvas._orbifold_img = (
                            self.output.geometry,
                            (self.output.modulus, self.output.angle),
                            pattern,
                            basis(pattern,
                                  *self.function.lattice_parameters),
                            image.size,
                            False,
                            True,
                            False,
                            False
                        )

                        self.output._canvas._mirrors_img = (
                            self.output.geometry,
                            (self.output.modulus, self.output.angle),
                            pattern,
                            basis(pattern,
                                  *self.function.lattice_parameters),
                            image.size,
                            False,
                            True,
                            False,
                            True
                        )

                        self.output._canvas._color_tile_img = (
                            self.output.geometry,
                            (self.output.modulus, self.output.angle),
                            pattern,
                            basis(pattern,
                                  *self.function.lattice_parameters),
                            image.size,
                            True,
                            False,
                            True,
                            False
                        )

                        self.output._canvas._color_orbifold_img = (
                            self.output.geometry,
                            (self.output.modulus, self.output.angle),
                            pattern,
                            basis(pattern,
                                  *self.function.lattice_parameters),
                            image.size,
                            False,
                            True,
                            True,
                            False
                        )

                        self.output._canvas._color_mirrors_img = (
                            self.output.geometry,
                            (self.output.modulus, self.output.angle),
                            pattern,
                            basis(pattern,
                                  *self.function.lattice_parameters),
                            image.size,
                            False,
                            True,
                            True,
                            True
                        )

                    self.update_output_preview()
                break

        self.after(100, self.update_GUI)
    # >>>3

    def make_output(self, *args):      # <<<3
        self.output.adjust_geometry()
        cfg = self.config

        self.output_params_queue.put(cfg)

        def output_process():
            while True:
                try:
                    cfg = self.output_params_queue.get(timeout=0.1)
                except queue.Empty:
                    break
                cfg["message_queue"] = self.message_queue
                cfg["output_message_queue"] = self.output_message_queue
                background_output(**cfg)

        if not self.pending_outputs:
            self.output_process = Process(target=output_process)
            self.output_process.start()
    # >>>3

    def make_preview(self, *args):      # <<<3

        self.output.adjust_geometry()
        if not self.function.matrix:
            return
        ratio = self.output.width / self.output.height
        if (self.output.width < self.output.preview_size and
                self.output.height < self.output.preview_size):
            width = self.output.width
            height = self.output.height
        elif ratio > 1:
            width = self.output.preview_size
            height = round(self.output.preview_size / ratio)
        else:
            width = round(self.output.preview_size * ratio)
            height = self.output.preview_size

        def make_preview_job():
            # print("make_preview PID", os.getpid())
            cfg = self.config
            cfg["output"]["size"] = (width, height)

            image = make_image(
                color=cfg["colorwheel"],
                output=cfg["output"],
                function=cfg["function"],
                message_queue=self.preview_message_queue
            )
            self.preview_image_queue.put(image)

        try:
            self.preview_process.terminate()
            self.preview_process.join()
            # redefine queues to avoid corruption
            self.preview_message_queue = Queue()
            self.preview_image_queue = Queue()
        except AttributeError as e:
            pass

        try:
            self.preview_config = copy.deepcopy(self.config)

            self.preview_process = Process(target=make_preview_job)
            self.preview_process.start()

            if (len(self.undo_list) == 0 or
                    self.preview_config != self.undo_list[self.undo_index]):
                self.undo_list = self.undo_list[:len(self.undo_list) + self.undo_index + 1]
                self.undo_list.append(self.preview_config)
                self.undo_index = -1
            self.undo_list = self.undo_list[-UNDO_SIZE:]
        except Error as e:
            self.message_queue.put("* {}".format(e))
    # >>>3

    def full_preview_image(self):       # <<<3
        """paste the preview, tile, orbifold and mirror images together"""
        img = self.output._canvas._image
        width, height = img.size
        if self.output.fade:
            img = fade_image(img)

        def paste_tile(name):
            try:
                tile = getattr(self.output._canvas, name)
                img.paste(tile, mask=tile)
            except:
                pass

        if self.output.draw_tile:
            if self.output.draw_color_tile:
                paste_tile("_color_tile_img")
            else:
                paste_tile("_tile_img")
        if self.output.draw_orbifold:
            if self.output.draw_color_tile:
                paste_tile("_color_orbifold_img")
            else:
                paste_tile("_orbifold_img")
        if self.output.draw_mirrors:
            if self.output.draw_color_tile:
                paste_tile("_color_mirrors_img")
            else:
                paste_tile("_mirrors_img")
        return img
    # >>>3

    def show_bigger_preview(self, *args, alpha=2):       # <<<3
        try:
            img = self.full_preview_image()
            width, height = img.size
            width = alpha * width
            height = alpha * height
            big_img = img.resize(
                (width, height),
                resample=PIL.Image.ANTIALIAS
            )

            dialog = Toplevel(self)
            dialog.resizable(width=False, height=False)
            dialog.tk_img = PIL.ImageTk.PhotoImage(big_img)
            canvas = Canvas(dialog, width=width, height=height)
            canvas.pack()
            canvas.create_image((width/2, height/2), image=dialog.tk_img)
            dialog.bind("<Key>", sequence(dialog.destroy, self.deiconify))
            dialog.bind("<Button-1>", sequence(dialog.destroy, self.deiconify))
            self.withdraw()
        except AttributeError:
            pass
    # >>>3

    def save_preview(self):     # <<<3
        img = self.full_preview_image()

        save_image(
            message_queue=self.message_queue,
            image=img,
            **self.preview_config
        )
    # >>>3

    def translate_rotate(self, dx, dy, dz=0):   # <<<3
        def translate_rotate_tmp(*args):
            if (self.output.geometry_tab == "mode" and
                    self.output.display_mode == "sphere"):
                if dx != 0 or dy != 0 or dz != 0:
                    self.output.rotate(
                        dx*ROTATION_DELTA,
                        dy*ROTATION_DELTA,
                        dz*ROTATION_DELTA)
            elif (self.output.geometry_tab == "mode" and
                  self.output.display_mode == "inversion"):
                if dx != 0 or dy != 0 or dz != 0:
                    x = self.output.inversion_center.real
                    y = self.output.inversion_center.imag
                    x -= dx*TRANSLATION_INVERSION_DELTA
                    y -= dy*TRANSLATION_INVERSION_DELTA
                    self.output.inversion_center = complex(x, y)
            else:
                if dx != 0 or dy != 0:
                    self.output.translate(
                        dx*TRANSLATION_DELTA,
                        dy*TRANSLATION_DELTA
                    )
                elif dz != 0:
                    self.output.angle -= dz * ROTATION_DELTA
        return translate_rotate_tmp
    # >>>3

    def new_random_preview(self, nb_tries=100):       # <<<3
        for i in range(nb_tries):
            self.function.new_random_matrix()
            if self.function.add_symmetries(self.function.matrix):
                break
        self.make_preview()
    # >>>3

    def load_config_file(self, filename):       # <<<3
        try:
            f = open(filename, mode="r")
            cfg = json.load(f)
            try:
                os.chdir(
                    os.path.expanduser(cfg.get("working_directory", "./"))
                )
            except:
                pass
            try:
                self.colorwheel.config = cfg["colorwheel"]
            except:
                pass
            try:
                self.output.config = cfg["output"]
            except:
                pass
            try:
                self.function.config = cfg["function"]
            except:
                pass
            if cfg.get("preview", False):
                self.make_preview()
        except:
            error("could read config file '{}'".format(filename))
    # >>>3

    def load_config(self, *args):   # <<<3
        if not hasattr(self, "_config_dir"):
            self._config_dir = "./"

        filename = filedialog.askopenfilename(
            parent=self,
            title="Create Symmetry: choose configuration file",
            initialdir=self._config_dir,
            filetypes=[("ct files", "*.ct"), ("all", "*.*")]
        )
        if not filename:
            return

        self._config_dir = os.path.dirname(filename)
        self.load_config_file(filename)
    # >>>3

    def save_config(self, *args):       # <<<3
        if not hasattr(self, "_config_dir"):
            self._config_dir = "./"
        filename = filedialog.asksaveasfilename(
            parent=self,
            title="Create Symmetry: choose configuration file",
            initialdir=self._config_dir,
            filetypes=[("ct files", "*.ct"), ("all", "*.*")]
        )
        cfg = self.config
        cfg["preview"] = True

        if not filename.endswith(".ct"):
            filename = filename + ".ct"
        config_file = open(filename, mode="w")
        if "matrix" in cfg["function"]:
            cfg["function"]["matrix"] = matrix_to_list(
                cfg["function"]["matrix"]
            )
        if "hyper_s" in cfg["function"]:
            cfg["function"]["hyper_s"] = str(cfg["function"]["hyper_s"])
        if "inversion_center" in cfg["output"]:
            cfg["output"]["inversion_center"] = str(
                cfg["output"]["inversion_center"]
            )
        json.dump(cfg, config_file, indent=2)
        config_file.close()
    # >>>3

    def undo(self):     # <<<3
        # print(">>", self.undo_index, len(self.undo_list))
        if abs(self.undo_index) < len(self.undo_list):
            self.undo_index -= 1
            self.config = self.undo_list[self.undo_index]
    # >>>3

    def redo(self):     # <<<3
        # print(">>>", self.undo_index, len(self.undo_list))
        if self.undo_index < -1:
            self.undo_index += 1
            self.config = self.undo_list[self.undo_index]
    # >>>3
# >>>2
# >>>1


###
# main
def main():     # <<<1
    # TODO:
    #  --batch
    #  --raw-config=...:...
    def display_help():
        print("""Usage: {} [flags]

    -o FILE                     choose output file
    --output=FILE

    -s W,H                      choose width and height of output
    --size=W,H

    -g X,Y,X,Y                  choose geometry of output
    --geometry=X,Y,X,Y

    --modulus=...               transformation of the result
    --angle=...

    -c FILE                     choose color file
    --color=FILE

    --color-geometry=X,Y,X,Y    choose "geometry" of the color file

    --color-modulus=...         transformation of the colorwheel
    --color-angle=...

    --matrix=...                transformation matrix

    --rotation-symmetry=p       force p-fold symmetry around the origin

    --pattern=...               name of pattern

    --params=...                lattice parameters (only used when appropriate)

    --N=...                     rotations for relevant spherical patterns

    --config=...                config file

    --preview                   compute the initial preview image

    --batch                     do not run GUI

    -h  /  --help               this message
""")

    # parsing the command line arguments
    short_options = "hc:o:s:g:v"
    long_options = [
            "help",
            "color=", "color-geometry=", "color-modulus=", "color-angle=",
            "output=", "size=", "geometry=", "modulus=", "angle=",
            "matrix=", "rotation-symmetry=",
            "preview",
            "pattern=", "params=",
            "config=", "batch"]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(-1)

    config = {
        "colorwheel": {
            # "filename": None,
            "default_color": DEFAULT_COLOR,
            "geometry": COLOR_GEOMETRY,
            "modulus": 1,
            "angle": 0,
            "stretch": False,
        },
        "output": {
                "size": OUTPUT_SIZE,
                "geometry": OUTPUT_GEOMETRY,
                "modulus": 1,
                "angle": 0,
                "filename_template": FILENAME_TEMPLATE,
                "save_directory": "./",
                "draw_tile": False,
                "draw_orbifold": False,
                "draw_color_tile": False,
                "draw_mirrors": False,
                "fade": False,
                "fade_coeff": FADE_COEFF,
                "display_mode": "plain",
                "sphere_rotations": SPHERE_ROTATIONS,
                "inversion_center": INVERSION_CENTER,
                "sphere_background": DEFAULT_BACKGROUND,
                "sphere_background_fading": 100,
                "sphere_stars": NB_STARS,
                "morph": False,
                "morph_start": 0,
                "morph_end": 180,
                "morph_stable_coeff": 20,
        },
        "function": {
                "matrix": None,
                "pattern_type": "wallpaper",
                "wallpaper_pattern": "o",
                "wallpaper_color_pattern": "",
                "lattice_parameters": [],
                "sphere_pattern": "332",
                "random_nb_coeffs": 3,
                "random_min_degre": -3,
                "random_max_degre": 3,
                "random_modulus": 1,
                "random_noise": 25,
                "wallpaper_N": 1,
                "sphere_N": 5,
                "sphere_mode": "sphere",
                "hyper_nb_steps": 25,
                "hyper_s": 3,
        },
        "preview": False,
        "working_directory": "./"}
    batch = False
    config_files = []

    def get_config(file):
        nonlocal config, config_files
        try:
            config_files.append(file)
            f = open(file, mode="r")
            cfg = json.load(f)
            for d in ["colorwheel", "output", "function"]:
                for k in cfg[d]:
                    config[d][k] = cfg[d][k]
            if cfg.get("preview", False):
                config["preview"] = True
        except:
            error("problem while loading configuration from '{}'"
                  .format(file))

    for o, a in opts:
        if o in ["-h", "--help"]:
            display_help()
            sys.exit(0)
        elif o in ["-c", "--color"]:
            config["colorwheel"]["filename"] = a
        elif o in ["-o", "--output"]:
            config["output"]["filename_template"] = a
        elif o in ["-s", "--size"]:
            try:
                tmp = map(int, re.split("[,x]", a))
                width, height = tmp
                config["output"]["size"] = (width, height)
            except:
                error("problem with size '{}'".format(a))
                sys.exit(1)
        elif o in ["-g", "--geometry"]:
            try:
                x_min, x_max, y_min, y_max = str_to_floats(a)
                config["output"]["geometry"] = x_min, x_max, y_min, y_max
            except:
                error("problem with geometry '{}' for output".format(a))
                sys.exit(1)
        elif o in ["--rotation-symmetry"]:
            try:
                config["function"]["wallpaper_N"] = int(a)
            except:
                error("problem with rotational symmetry '{}'".format(a))
        elif o in ["--modulus"]:
            try:
                config["output"]["modulu"] = float(a)
            except:
                error("problem with modulus '{}'".format(a))
                sys.exit(1)
        elif o in ["--angle"]:
            try:
                config["output"]["angle"] = float(a)
            except:
                error("problem with angle '{}'".format(a))
                sys.exit(1)
        elif o in ["--color-geometry"]:
            try:
                x_min, x_max, y_min, y_max = str_to_floats(a)
                config["colorwheel"]["geometry"] = x_min, x_max, y_min, y_max
            except:
                error("problem with geometry '{}' for color image".format(a))
                sys.exit(1)
        elif o in ["--color-modulus"]:
            try:
                config["colorwheel"]["modulus"] = float(a)
            except:
                error("problem with modulus '{}'".format(a))
                sys.exit(1)
        elif o in ["--color-angle"]:
            try:
                config["colorwheel"]["angle"] = float(a)
            except:
                error("problem with angle '{}'".format(a))
                sys.exit(1)
        elif o in ["--pattern"]:
            pattern = a
            # print("pattern:", pattern)
            if "/" in pattern:
                color_pattern, pattern = pattern.split("/")
                config["function"]["pattern_type"] = "wallpaper"
                config["function"]["wallpaper_pattern"] = pattern
                config["function"]["wallpaper_color_pattern"] = color_pattern
                config["output"]["display_mode"] = "plain"
            elif pattern in W_NAMES:
                config["function"]["pattern_type"] = "wallpaper"
                config["function"]["wallpaper_pattern"] = pattern
                config["output"]["display_mode"] = "plain"
            elif pattern in S_NAMES:
                config["function"]["pattern_type"] = "sphere"
                config["function"]["sphere_pattern"] = pattern
                config["output"]["display_mode"] = "sphere"
                config["output"]["sphere_stars"] = NB_STARS
            elif pattern == "hyperbolic":
                config["function"]["pattern_type"] = "hyperbolic"
                config["output"]["display_mode"] = "inversion"
                config["output"]["sphere_stars"] = 0

        elif o in ["--params"]:
            config["function"]["lattice_parameters"] = str_to_floats(a)
        elif o in ["--N"]:
            config["function"]["sphere_N"] = int(a)
        elif o == "--preview":
            config["preview"] = True
        elif o in ["--matrix"]:
            config["function"]["matrix"] = parse_matrix(a)
        elif o == "--config":
            get_config(a)
        elif o == "--batch":
            batch = True
        elif o == "--gui":
            batch = False
        else:
            assert False

    if len(args) == 1:
        get_config(args[0])
    elif len(args) > 1:
        error("cannot give more than one argument on the command line: '{}'"
              .format(args))
        sys.exit(1)

    # print("main PID", os.getpid())
    if batch:
        if config["function"]["matrix"] is None:
            config["function"]["matrix"] = random_matrix(
                config["function"]["random_nb_coeffs"],
                config["function"]["random_min_degre"],
                config["function"]["random_max_degre"],
                config["function"]["random_modulus"],
            )

    gui = CreateSymmetry()
    gui.config = config

    if config_files == [] and os.path.isfile(".create_symmetry.ct"):
        gui.load_config_file(".create_symmetry.ct")
        # gui.function.change_matrix(fourrier_identity(20))

    if batch:
        img = make_image(
            color=config["colorwheel"],
            output=config["output"],
            function=config["function"]
        )
        if gui.output.config["fade"]:
            img = fade_image(img)
        save_image(image=img, **gui.config)
        return

    if config["preview"]:
        gui.make_preview()

    gui.mainloop()
# >>>1


if __name__ == "__main__":
    main()

# vim: textwidth=0 foldmarker=<<<,>>> foldmethod=marker foldlevel=0
