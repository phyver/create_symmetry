#!/usr/bin/env python3

###
# imports
# <<<1

# image manipulation (Pillow)
import PIL
from PIL import ImageDraw
import PIL.ImageTk
from PIL.ImageColor import getrgb

# vectorized arrays
import numpy as np

# Tkinter for GUI
from tkinter import *
from tkinter.ttk import Combobox, Notebook, Style
import tkinter.font
from tkinter import filedialog

# misc functions
import copy
import getopt
import sys
import os.path
from itertools import product
import re
import json
import time
from ast import literal_eval

# math
from cmath import exp
from math import sqrt, pi, sin, cos, asin, acos, atan2
from random import randrange, uniform, shuffle, seed

# multiprocessing
from multiprocessing import Process, Queue
from threading import Thread
import queue
# >>>1

PREVIEW_SIZE = 500
STRETCH_DISPLAY_RADIUS = 5
OUTPUT_WIDTH = 1280
OUTPUT_HEIGHT = 960
COLOR_SIZE = 200
COLOR_GEOMETRY = (-1, 1, -1, 1)
WORLD_GEOMETRY = (-2, 2, -2, 2)
DEFAULT_COLOR = "black"
FILENAME_TEMPLATE = "output-{type:}-{name:}~{nb:}"
UNDO_SIZE = 100
DEFAULT_SPHERE_BACKGROUND = "#000066"
STAR_COLOR = "#FFC"

RANDOM_SEED = uniform(0, 1)

PATTERN = {     # <<<1
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
    },
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
    },
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
        # OK (the axis of symmetry are the same, only the size of the basic tile changes
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
    },
    }

# transform all the cyclic sphere groups into frieze groups
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
# >>>1

NAMES = [    # <<<1
    # order of the groups in menus
    # plane groups
    "o",       # general
    "2222",
    "*×",      # rhombic
    "2*22",
    "**",      # rectangular
    "××",
    "*2222",
    "22*",
    "22×",
    "442",     # square
    "*442",
    "4*2",
    "333",     # hexagonal
    "3*3",
    "*333",
    "632",
    "*632",
    # sphere groups
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

# names, with alternative names, for wallpaper groups
W_NAMES = ["{} ({})".format(p, PATTERN[p]["alt_name"])
           for p in NAMES
           if PATTERN[p]["type"] == "plane group"]
_t = None
for i in range(len(W_NAMES)):
    p = W_NAMES[i].split()[0]
    t = PATTERN[p]["description"].split()[0]
    if _t != t:
        W_NAMES[i] += "                   -- {}".format(t)
    _t = t

# names, with alternative names, for sphere groups
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

# names, with alternative names, for frieze groups
F_NAMES = ["{} ({})".format(p, PATTERN[p]["alt_name"])
           for p in NAMES
           if PATTERN[p]["type"] == "frieze"]
del _t


# names, with alternative names, for color reversing groups
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
        for f in fs:
            f()
    return res
# >>>2


def invert22(M):        # <<<2
    """invert a 2x2 matrix"""
    d = M[0][0] * M[1][1] - M[1][0] * M[0][1]
    I = [[M[1][1]/d, -M[0][1]/d],
         [-M[1][0]/d, M[0][0]/d]]
    return I
# >>>2


def mult_M(M1, M2):     # <<<2
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
    if s.strip() == "":
        return []
    else:
        return list(map(float, s.split(",")))
# >>>2


def float_to_str(x):       # <<<2
    """transform a float into a string, removing trailing decimal 0s,
    and decimal points if possible
    """
    s = re.sub("\.0*\s*$", "", str(x))
    if s == "":
        return "0"
    else:
        return s
# >>>2


def floats_to_str(l):       # <<<2
    """transform a list of floats into a string"""
    return ", ".join(map(float_to_str, l))
# >>>2


def complex_to_str(z, precision=4):    # <<<2
    """transform a complex number into a string"""
    if z == 0:
        return "0"
    elif z == z.real:
        x = "{:.4f}".format(z.real).rstrip("0")
        x = x.rstrip(".")
        return x
    elif z == z - z.real:
        y = "{:.4f}".format(z.imag).rstrip("0")
        y = y.rstrip(".") + "i"
        return y
    else:
        sign = "+" if z.imag > 0 else "-"
        x = "{x:.{prec:}f}".format(x=z.real, prec=precision).rstrip("0")
        y = "{y:.{prec:}f}".format(y=abs(z.imag), prec=precision).rstrip("0")
        x = x.rstrip(".").rjust(7)
        y = y.rstrip(".")
        return "{} {} {}i".format(x, sign, y)
# >>>2


def matrix_to_list(M):      # <<<2
    """transform a "matrix" (ie a dictionnary with pairs of integers as keys
    and complex numbers as values) into a list of pairs of pairs:
        - the pair of integers of the key
        - the real and imaginary parts of the value
    """
    return [((n, m), (z.real, z.imag)) for (n, m), z in M.items()]
# >>>2


def list_to_matrix(L):      # <<<2
    """transform a list of pairs of pairs into a matrix:
        - the first pairs are integers
        - the second pairs are floats (real and imaginary parts)
    """
    return dict([((n, m), complex(x, y)) for ((n, m), (x, y)) in L])
# >>>2


def parse_matrix(s):        # <<<2
    """parse a string and return the corresponding matrix"""
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
        color = getrgb(s)
        return True
    except:
        return False
# >>>2


def random_matrix(nb_coeffs, min_degre, max_degre, modulus):
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
        # return [[1, 0], [params[0], params[1]]]
        return [[params[0], params[1]], [params[2], params[3]]]
    elif lattice == "rhombic":
        return [[1/2, params[0]/2], [1/2, -params[0]/2]]
    elif lattice == "rectangular":
        return [[1, 0], [0, 1/params[0]]]
    elif lattice == "square":
        return [[1, 0], [0, 1]]
    elif lattice == "hexagonal":
        return [[1, 0], [-1/2, sqrt(3)/2]]
    else:
        return None
# >>>2


def bezout(a, b):
    """Calcule (u, v, p) tels que a*u + b*v = p et p = pgcd(a, b)"""
    if a == 0 and b == 0:
        return (0, 0, 0)
    if b == 0:
        return (a//abs(a), 0, abs(a))
    (u, v, p) = bezout(b, a % b)
    return (v, (u - v*(a//b)), p)
# >>>1


###
# making an image from a transformation and a colorwheel
# <<<1
def make_coordinates_array(         # <<<2
        size=(OUTPUT_WIDTH, OUTPUT_HEIGHT),
        geometry=WORLD_GEOMETRY,
        modulus=1,
        angle=0,
        ):
    """compute the array of floating point numbers associated to each pixel"""
    rho = modulus * complex(cos(angle*pi/180), sin(angle*pi/180))

    x_min, x_max, y_min, y_max = geometry
    width, height = size
    delta_x = (x_max-x_min) / (width-1)
    delta_y = (y_max-y_min) / (height-1)

    xs = np.arange(width, dtype='float64')
    np.multiply(delta_x, xs, out=xs)
    np.add(x_min, xs, out=xs)

    ys = np.arange(height, dtype='float64')
    np.multiply(delta_y, ys, out=ys)
    np.subtract(y_max, ys, out=ys)

    zs = xs[:, None] + 1j*ys
    np.divide(zs, rho, out=zs)

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


def apply_color(        # <<<2
        res,
        filename=None,                  # image for the colorwheel image
        geometry=COLOR_GEOMETRY,          # coordinates of the colorwheel
        modulus="1",
        angle="0",
        color="black"):
    """replace each complex value in the array res by the color taken from an
    image in filename
    the resulting image is returned"""

    if isinstance(color, str):
        color = getrgb(color)

    rho = modulus * complex(cos(angle*pi/180), sin(angle*pi/180))
    x_min, x_max, y_min, y_max = geometry

    tmp = PIL.Image.open(filename)
    width, height = tmp.size
    delta_x = (x_max-x_min) / (width-1)
    delta_y = (y_max-y_min) / (height-1)

    # we add a border to the top / right of the color image, using the default
    # color
    color_im = PIL.Image.new("RGB",
                             (width+1,
                              height+1),
                             color=color)
    color_im.paste(tmp, box=(1, 1))

    # TODO when hyperbolic pattern, ComplexWarning: Casting complex values to
    # real discards the imaginary part ???
    np.divide(res, rho, out=res)

    # convert the ``res`` array into pixel coordinates
    xs = np.rint((res.real - x_min) / delta_x).astype(int)
    ys = np.rint((y_max - res.imag) / delta_y).astype(int)

    # increase all coordinates by 1: 0 will be used for pixels in the border
    # with ``color``
    np.add(xs, 1, out=xs)
    np.add(ys, 1, out=ys)

    # replace too big / too small values with 0, to get the ``color``
    np.place(xs, xs < 0, [0])
    np.place(xs, xs >= width, [0])
    np.place(ys, ys < 0, [0])
    np.place(ys, ys >= height, [0])

    res = np.dstack([xs, ys])

    # get array of pixels colors, and reshape the array to be 3 dimensional
    color = np.asarray(color_im).reshape(height+1, width+1, 3)

    # apply color to the pixel coordinates and convert to appropriate type
    # transpose the first two dimensions because images have [y][x] and arrays
    # have [x][y] coordinates
    res = color.transpose(1, 0, 2)[xs, ys].transpose(1, 0, 2)
    return PIL.Image.fromarray(np.array(res, dtype=np.uint8), "RGB")
# >>>2


def make_wallpaper_image(zs,     # <<<2
                         matrix,
                         pattern,
                         basis,      # additional parameters
                         N=1,
                         color_pattern="",
                         message_queue=None):
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
        ZS = np.zeros(zs.shape, dtype=complex)

        for k in range(0, N):
            rho = complex(cos(2*pi*k/N),
                          sin(2*pi*k/N))
            _tmp = zs * rho
            _xs = _tmp.real
            _ys = _tmp.imag
            _tmp = (n*(B[0][0]*_xs+B[1][0]*_ys) +
                    m*(B[0][1]*_xs+B[1][1]*_ys)).astype(complex)
            np.multiply(_tmp, 2j*pi, out=_tmp)
            np.exp(_tmp, out=_tmp)
            np.add(ZS, _tmp, out=ZS)
            if message_queue is not None:
                message_queue.put(w1/w2)
            w1 += 1
        np.divide(ZS, N, out=ZS)
        np.multiply(ZS, matrix[(n, m)], out=ZS)
        np.add(res, ZS, out=res)
    return res
# >>>2


def make_hyperbolic_image(     # <<<2
        zs,
        matrix=None,
        nb_steps=200,
        color_pattern="",
        disk_model=True,
        message_queue=None):

    for n, m in matrix:
        while matrix[n, m].real <= 1:
            x, y = matrix[n, m].real, matrix[n, m].imag
            matrix[n, m] = complex(10*abs(x), y)

    done = set([])
    res = np.zeros(zs.shape, dtype=complex)
    c, d = 0, 0
    w1, w2 = 0, nb_steps*len(matrix)

    if disk_model:
        zs = 1j * (1-zs) / (1+zs)
        # y = 1-np.abs(zs)
        # x = np.angle(zs)*4/(2*pi)
        # zs = x + 1j*y

    def PSL2():
        """generator for elements of the PSL2(Z)"""
        total = 0
        c = 0
        while True:
            if c == total:
                c = 0
                total += 1
            else:
                c = c + 1
            for d in [total-c, c-total]:
                b, a, p = bezout(c, d)
                if p == 1:
                    yield a, -b, c, d

    for a, b, c, d in PSL2():
        if len(done) >= nb_steps:
            break
        if (c, d) in done:
            continue
        assert a*d - b*c == 1
        done.add((c, d))
        ZS = (a*zs + b) / (c*zs + d)

        for n, m in matrix:
            res += ZS.imag**matrix[n, m] * np.exp(2j*pi*(n*ZS.real + m*ZS.imag))
            w1 += 1
            if message_queue is not None:
                message_queue.put(w1/w2)

    # res = res / nb_steps

    return res
# >>>2


def make_sphere_image(zs,      # <<<2
                      matrix,
                      pattern,
                      N=5,
                      unwind=False,
                      message_queue=None):
    """use the given matrix to make an image for the given spherical pattern

    the ``N`` parameter is used for cyclic groups

    ``unwind`` is used to transform cyclic groups into frieze patterns

    ``message_queue`` is used to keep track of progress
    """

    recipe = PATTERN[pattern]["recipe"]
    parity = PATTERN[pattern]["parity"].replace("N", str(N))
    matrix = add_symmetries(matrix, recipe, parity)

    if unwind:
        np.multiply(1j, zs, out=zs)
        np.exp(zs, out=zs)

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
                np.add(res, matrix[(n, m)] * zs**n * zsc**m, out=res)
                if message_queue is not None:
                    message_queue.put(w1/w2)
                w1 += 1
            np.divide(a*zs + b, c*zs + d, out=zs)
        np.divide(e*zs + f, g*zs + h, out=zs)

    np.divide(res, average[0][1]*average[1][1], out=res)
    return res
# >>>2


def make_sphere_background(zs, img, background="back.jpg", fade=128, stars=0):
    """compute the background for a sphere
        - background can either be a color, or a filename containing an image
          to display
        - fade is used to fade the background (0: no fading, 255: black
          background)
        - stars is the number of random "stars" (pixels) to add to the
          background
      """
    width, height = zs.shape
    try:
        background_img = PIL.Image.open(background)
        background_img = background_img.resize((width, height))
    except Exception as e:
        try:
            color = getrgb(background)
            background_img = PIL.Image.new(mode="RGB",
                                           size=(width, height),
                                           color=color)
            seed(RANDOM_SEED)
            for i in range(stars):
                background_img.putpixel((randrange(0, width),
                                        randrange(0, height)),
                                        getrgb(STAR_COLOR))
            seed()
        except ValueError:
            background_img = PIL.Image.new(mode="RGB",
                                           size=(width, height),
                                           color=DEFAULT_SPHERE_BACKGROUND)

    mask = (zs.real**2 + zs.imag**2 > 1).astype(int).transpose(1, 0)

    mask_background = PIL.Image.fromarray(
            np.array(mask*fade, dtype=np.uint8),
            "L")
    background_img.paste(0, mask=mask_background)

    mask_sphere = PIL.Image.fromarray(
            np.array(mask*255, dtype=np.uint8),
            "L")
    img.paste(background_img, mask=mask_sphere)
    return img
# >>>2


def save_image(         # <<<2
        message_queue=None,
        image=None,
        **config
        ):
    filename_template = config["world"]["filename_template"]

    color = config["color"]
    world = config["world"]
    params = config["params"]
    pattern = config["pattern"]
    matrix = config["matrix"]

    if ((world["draw_tile"] or world["draw_orbifold"]) and
            PATTERN[pattern]["type"] in ["plane group",
                                         "color reversing plane group"]):
        tile = make_tile(
                world["geometry"],
                (world["modulus"], world["angle"]),
                pattern,
                params["lattice_basis"],
                image.size,
                draw_tile=world["draw_tile"],
                draw_orbifold=world["draw_orbifold"],
                color_tile=world["draw_color_tile"],
                draw_mirrors=world["draw_mirrors"]
                )
        image.paste(tile, mask=tile)

    function = config["function"]
    info = {"type": "", "name": "", "alt_name": ""}
    if function["current_tab"] == "wallpaper":
        info["type"] = "planar"
        info["name"] = function["wallpaper_pattern"]
        info["alt_name"] = PATTERN[info["name"]]["alt_name"]
        cp = function["wallpaper_color_pattern"]
        if cp:
            info["name"] = cp + "_" + info["name"]
            info["alt_name"] = (PATTERN[cp]["alt_name"] +
                                "_" +
                                info["alt_name"])
    elif function["current_tab"] == "sphere":
        info["type"] = "spherical"
        p = function["sphere_pattern"]
        N = function["sphere_N"]
        info["name"] = p.replace("N", str(N))
        info["alt_name"] = PATTERN[p]["alt_name"]
        info["alt_name"] = info["alt_name"].replace("N", str(N))
    elif function["current_tab"] == "hyperbolic":
        info["type"] = "hyperbolic"
        info["name"] = "--"
        info["alt_name"] = "--"
    else:
        assert False
    info["nb"] = 1

    _filename = None
    while True:
        filename = filename_template.format(**info)
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

    config["function"]["matrix"] = matrix_to_list(config["matrix"])
    cmd = ("""#!/bin/sh
CREATE_SYM={prog_path:}

$CREATE_SYM --color-config='{color_config:}' \\
        --world-config='{world_config:}' \\
        --function-config='{function_config:}' \\
        --preview \\
        $@
""".format(
       prog_path=os.path.abspath(sys.argv[0]),
       color_config=json.dumps(config["color"], separators=(",", ":")),
       world_config=json.dumps(config["world"], separators=(",", ":")),
       function_config=json.dumps(config["function"], separators=(",", ":")),
       ))

    cs = open(filename + ".sh", mode="w")
    cs.write(cmd)
    cs.close()
# >>>2


def background_output(     # <<<2
        message_queue=None,
        output_message_queue=None, **config):
    """compute an image from the configuration in config, and save it to a file
    used by the GUI for output jobs"""

    filename_template = config["world"]["filename_template"]

    color = config["color"]
    world = config["world"]
    params = config["params"]
    pattern = config["pattern"]
    matrix = config["matrix"]
    image = make_image(color=color,
                       world=world,
                       pattern=pattern,
                       matrix=matrix,
                       message_queue=output_message_queue,
                       tile=True,
                       stretch_color=color["stretch"],
                       **params)

    if world["preview_fade"]:
        image = fade_image(image)

    save_image(
            message_queue=message_queue,
            image=image,
            **config
            )


# >>>2


def make_image(color=None,     # <<<2
               world=None,
               pattern="",
               matrix=None,
               message_queue=None,
               stretch_color=False,
               **params):
    """compute an image for a pattern"""

    zs = make_coordinates_array(world["size"],
                                world["geometry"],
                                world["modulus"],
                                world["angle"])
    _zs = zs

    if not world["sphere_projection"]:
        _zs = np.copy(zs)
        zs = plane_coordinates_to_sphere(zs, world["sphere_rotations"])

    if pattern == "hyperbolic":
        res = make_hyperbolic_image(
                zs,
                matrix,
                nb_steps=params["nb_steps"],
                disk_model=params["disk_model"],
                message_queue=message_queue)
    elif PATTERN[pattern]["type"] in ["plane group",
                                      "color reversing plane group"]:
        res = make_wallpaper_image(zs,
                                   matrix,
                                   pattern,
                                   params["lattice_basis"],
                                   N=params["N"],
                                   message_queue=message_queue)
    elif PATTERN[pattern]["type"] in ["sphere group", "frieze", "rosette"]:
        res = make_sphere_image(zs,
                                matrix,
                                pattern,
                                N=params["N"],
                                unwind=params["sphere_mode"] == "frieze",
                                message_queue=message_queue)
    else:
        print(PATTERN[pattern]["type"])
        assert False

    if stretch_color:
        np.divide(res, np.sqrt(1 + res.real**2 * res.imag**2), out=res)

    img = apply_color(res,
                      color["filename"],
                      color["geometry"],
                      color["modulus"],
                      color["angle"],
                      color["color"])

    if (world["sphere_background"] and not world["sphere_projection"]):
        return make_sphere_background(_zs,
                                      img,
                                      background=world["sphere_background"],
                                      fade=world["sphere_background_fading"],
                                      stars=world["sphere_stars"])
    elif (pattern == "hyperbolic" and params["disk_model"]):
        return make_sphere_background(_zs,
                                      img,
                                      background=world["sphere_background"],
                                      fade=0,
                                      stars=0)
    else:
        return img
# >>>2


# TODO: name all arguments
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

        basis = mult_M(C, basis)

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
                draw.rectangle([x1-R, y1-R, x1+R, y1+R], fill=color)
                draw.rectangle([x2-R, y2-R, x2+R, y2+R], fill=color)

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
# >>>
# >>>1


###
# GUI
# <<<1
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
        return self._color.get()
    # >>>4

    @rgb_color.setter
    def rgb_color(self, color):    # <<<4
        self._color.set("#{:02x}{:02x}{:02x}"
                        .format(color[0], color[1], color[2]))
    # >>>4

    @property
    def color(self):    # <<<4
        return self._color.entry_widget.get()
    # >>>4

    @color.setter
    def color(self, color):    # <<<4
        self._color.set(color)
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
            return self._filename
        except AttributeError:
            return None
    # >>>4

    @filename.setter
    def filename(self, filename):   # <<<4
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
        if os.path.exists(filename):
            self._alt_filename = filename
    # >>>4
    # >>>3

    def __init__(self, root):        # <<<3

        self.root = root

        LabelFrame.__init__(self, root)
        self.configure(text="Color Wheel")

        self._color = LabelEntry(self,
                                 label="default color",
                                 value=DEFAULT_COLOR,
                                 width=10,
                                 convert=getrgb)
        self._color.grid(row=0, column=0, padx=5, pady=5)
        self._color.bind("<Return>", self.update_defaultcolor)
        self._color.bind("<FocusOut>", self.update_defaultcolor)

        self._stretch_color = BooleanVar()
        self._stretch_color.set(False)
        Checkbutton(self, text="stretch unit disk",
                    variable=self._stretch_color,
                    onvalue=True, offvalue=False,
                    command=lambda: self.change_colorwheel(self.filename),
                    indicatoron=False
                    ).grid(row=1, column=0, padx=5, pady=0)

        self._canvas = Canvas(self, width=200, height=200, bg="white")
        self._canvas.grid(row=3, column=0, padx=5, pady=5)
        for i in range(5, COLOR_SIZE, 10):
            for j in range(5, COLOR_SIZE, 10):
                self._canvas.create_line(i-1, j, i+2, j, fill="gray")
                self._canvas.create_line(i, j-1, i, j+2, fill="gray")
        self._colorwheel_id = None
        self._canvas.bind("<Button-3>", self.set_origin)
        self._canvas.bind("<Double-Button-1>", self.switch_colorwheel)

        self._filename_button = Button(self, text="choose file",
                                       command=self.choose_colorwheel)
        self._filename_button.grid(row=4, column=0, padx=5, pady=5)

        coord_frame = LabelFrame(self, text="coordinates")
        coord_frame.grid(row=5, column=0, sticky=E+W, padx=5, pady=5)
        coord_frame.columnconfigure(0, weight=1)
        coord_frame.columnconfigure(1, weight=1)

        self._x_min = LabelEntry(coord_frame, label="x min",
                                 value=COLOR_GEOMETRY[0],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._x_min.grid(row=0, column=0, padx=5, pady=5)

        self._x_max = LabelEntry(coord_frame, label="x max",
                                 value=COLOR_GEOMETRY[1],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._x_max.grid(row=0, column=1, padx=5, pady=5)

        self._y_min = LabelEntry(coord_frame, label="y min",
                                 value=COLOR_GEOMETRY[2],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._y_min.grid(row=1, column=0, padx=5, pady=5)

        self._y_max = LabelEntry(coord_frame, label="y max",
                                 value=COLOR_GEOMETRY[3],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._y_max.grid(row=1, column=1, padx=5, pady=5)

        transformation_frame = LabelFrame(self, text="transformation")
        transformation_frame.grid(row=6, column=0, sticky=E+W, padx=5, pady=5)
        self._modulus = LabelEntry(transformation_frame, label="modulus",
                                   value=1,
                                   convert=float,
                                   width=6)
        self._modulus.pack(padx=5, pady=5)
        self._modulus.bind("<Return>", self.draw_unit_circle, add="+")
        self._modulus.bind("<FocusOut>", self.draw_unit_circle, add="+")

        self._angle = LabelEntry(transformation_frame, label="angle (°)",
                                 value=0,
                                 convert=float,
                                 width=4)
        self._angle.pack(padx=5, pady=5)

        self._reset_button = Button(self, text="reset",
                                    command=self.reset_geometry)
        self._reset_button.grid(row=7, column=0,
                                padx=5, pady=(5, 10))

        self.update_defaultcolor()

        if os.path.exists("./colorwheel.jpg"):
            self.change_colorwheel("colorwheel.jpg")
        else:
            self.filename = None
    # >>>3

    def update_defaultcolor(self, *args):     # <<<3
        if self._color.validate():
            self._canvas.config(bg="#{:02x}{:02x}{:02x}".format(*self.rgb_color))
    # >>>3

    def change_colorwheel(self, filename):  # <<<3
        if filename is None:
            return
        try:
            if self.stretch:
                self._x_min.disable()
                self._x_max.disable()
                self._y_min.disable()
                self._y_max.disable()
                self._modulus.disable()
                self._angle.disable()
                self._reset_button.configure(state=DISABLED)
                zs = make_coordinates_array(
                        size=(PREVIEW_SIZE, PREVIEW_SIZE),
                        geometry=(-STRETCH_DISPLAY_RADIUS,
                                  STRETCH_DISPLAY_RADIUS,
                                  -STRETCH_DISPLAY_RADIUS,
                                  STRETCH_DISPLAY_RADIUS))
                np.divide(zs, np.sqrt(1 + zs.real**2 + zs.imag**2), out=zs)
                img = apply_color(zs,
                                  filename,
                                  self.geometry,
                                  self.modulus,
                                  self.angle,
                                  self.rgb_color)
            else:
                self._x_min.enable()
                self._x_max.enable()
                self._y_min.enable()
                self._y_max.enable()
                self._modulus.enable()
                self._angle.enable()
                self._reset_button.configure(state=NORMAL)
                img = PIL.Image.open(filename)
                img.thumbnail((COLOR_SIZE, COLOR_SIZE), PIL.Image.ANTIALIAS)
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
            self._canvas.delete(self._colorwheel_id)
            self._canvas.create_image((100, 100), image=tk_img)
            self.filename = filename
            self._filename_button.config(text=os.path.basename(filename))

            self.draw_unit_circle()

        except Exception as e:
            error("problem while loading {} for color image: {}"
                  .format(filename, e))
    # >>>3

    def switch_colorwheel(self, *args):     # <<<3
        try:
            self.change_colorwheel(self._alt_filename)
        except AttributeError:
            pass
    # >>>3

    def draw_unit_circle(self, *args):      # <<<3
        try:
            self._canvas.delete(self._unit_circle)
            self._canvas.delete(self._center)
        except:
            pass


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
        self._unit_circle = self._canvas.create_oval(x0-r, y0-r, x0+r, y0+r,
                                                     width=3,
                                                     outline="gray")
        self._center = self._canvas.create_oval(x0-5, y0-5, x0+5, y0+5,
                                                width=1,
                                                fill="gray",
                                                outline="red")
    # >>>3

    def choose_colorwheel(self, *args):    # <<<3
        filename = filedialog.askopenfilename(
                parent=self,
                title="Create Symmetry: choose color wheel image",
                initialdir="./",
                filetypes=[("images", "*.jpg *.jpeg *.png"), ("all", "*.*")])
        if filename:
            self.change_colorwheel(filename)
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

        self.draw_unit_circle()
    # >>>3

    def reset_geometry(self, *args):        # <<<3
        if self.stretch:
            return
        self.modulus = 1
        self.angle = 0
        if self.filename is not None:
            self.change_colorwheel(self.filename)
        else:
            self.geometry = COLOR_GEOMETRY
    # >>>3

    @property
    def config(self):           # <<<3
        cfg = {}
        for k in ["filename", "alt_filename", "color", "geometry", "modulus",
                  "angle", "stretch"]:
            cfg[k] = getattr(self, k)
        return cfg
    # >>>3

    @config.setter
    def config(self, cfg):      # <<<3
        for k in ["color", "geometry", "modulus",
                  "angle", "stretch"]:
            if k in cfg:
                setattr(self, k, cfg[k])
        if "filename" in cfg:
            self.change_colorwheel(cfg["filename"])
        if "alt_filename" in cfg:
            self.change_colorwheel(cfg["alt_filename"])
    # >>>3
# >>>2


class World(LabelFrame):     # <<<2

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
        return self._width.get(), self._height.get()
    # >>>4

    @size.setter
    def size(self, size):    # <<<4
        width, height = size
        self._width.set(float_to_str(width))
        self._height.set(float_to_str(height))
    # >>>4

    @property
    def width(self):    # <<<4
        return self._width.get()
    # >>>4

    @width.setter
    def width(self, width):    # <<<4
        self._width.set(float_to_str(width))
    # >>>4

    @property
    def height(self):    # <<<4
        return self._height.get()
    # >>>4

    @height.setter
    def height(self, height):    # <<<4
        self._height.set(float_to_str(height))
    # >>>4

    @property
    def sphere_projection(self):    # <<<4
        return self._sphere_projection.get()
    # >>>4

    @sphere_projection.setter
    def sphere_projection(self, b):    # <<<4
        self._sphere_projection.set(b)
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
    def sphere_background(self):    # <<<4
        s = self._sphere_background.get()
        if is_rgb(s):
            return s
        elif os.path.exists(self._sphere_background_full_filename):
            return self._sphere_background_full_filename
        else:
            return s
    # >>>4

    @sphere_background.setter
    def sphere_background(self, s):    # <<<4
        if is_rgb(s):
            self._sphere_background_full_filename = ""
            self._sphere_background.set(s)
        elif os.path.exists(s):
            self._sphere_background_full_filename = s
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
        if ("sphere" in self._geometry_tabs.tab(self._geometry_tabs.select(),
                                                "text")):
            return "sphere"
        elif ("plane" in self._geometry_tabs.tab(self._geometry_tabs.select(),
                                                 "text")):
            return "plane"
        else:
            assert False
    # >>>4

    @geometry_tab.setter
    def geometry_tab(self, tab):     # <<<4
        tab = tab.lower().strip()
        if tab == "sphere":
            self._geometry_tabs.select(self._geometry_sphere_tab)
        elif tab == "plane":
            self._geometry_tabs.select(self._geometry_plane_tab)
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
    def preview_fade(self):    # <<<4
        return self._fade.get()
    # >>>4

    @preview_fade.setter
    def preview_fade(self, b):    # <<<4
        self._fade.set(b)
    # >>>4

    @property
    def preview_fade_coeff(self):    # <<<4
        return self._preview_fade_coeff.get()
    # >>>4

    @preview_fade_coeff.setter
    def preview_fade_coeff(self, b):    # <<<4
        self._preview_fade_coeff.set(b)
    # >>>4

    @property
    def preview_size(self):     # <<<4
        return min(PREVIEW_SIZE, self._preview_size.get())
    # >>>4

    @preview_size.setter
    def preview_size(self, n):      # <<<4
        self._preview_size.set(min(PREVIEW_SIZE, n))
    # >>>4

    # >>>3

    def __init__(self, root):       # <<<3

        self.root = root

        LabelFrame.__init__(self, root)
        self.configure(text="World")

        # the preview image     <<<4
        canvas_frame = Frame(self)
        canvas_frame.grid(row=0, column=0, rowspan=4, padx=5, pady=5)

        self._canvas = Canvas(canvas_frame,
                              width=PREVIEW_SIZE, height=PREVIEW_SIZE,
                              bg="light gray")
        for i in range(5, PREVIEW_SIZE, 10):
            for j in range(5, PREVIEW_SIZE, 10):
                self._canvas.create_line(i-1, j, i+2, j, fill="gray")
                self._canvas.create_line(i, j-1, i, j+2, fill="gray")
        self._canvas.pack(padx=5, pady=5)

        self._draw_color_tile = BooleanVar()
        self._draw_color_tile_button = Checkbutton(
                canvas_frame,
                variable=self._draw_color_tile,
                text="")
        self._draw_color_tile_button.pack(side=LEFT, padx=0, pady=0)

        self._draw_tile = BooleanVar()
        self._draw_tile_button = Checkbutton(
                canvas_frame,
                variable=self._draw_tile,
                text="tile",
                indicatoron=False)
        self._draw_tile_button.pack(side=LEFT, padx=5, pady=5)

        self._draw_orbifold = BooleanVar()
        self._draw_orbifold_button = Checkbutton(
                canvas_frame,
                variable=self._draw_orbifold,
                text="orbifold",
                indicatoron=False)
        self._draw_orbifold_button.pack(side=LEFT, padx=5, pady=5)

        self._draw_mirrors = BooleanVar()
        self._draw_mirrors_button = Checkbutton(
                canvas_frame,
                variable=self._draw_mirrors,
                text="mirrors",
                indicatoron=False)
        self._draw_mirrors_button.pack(side=LEFT, padx=5, pady=5)

        self._fade = BooleanVar()
        self._fade_button = Checkbutton(
                canvas_frame,
                variable=self._fade,
                text="fade",
                indicatoron=False)
        self._fade_button.pack(side=LEFT, padx=(5, 0), pady=5)

        self._preview_fade_coeff = LabelEntry(
                canvas_frame,
                convert=int,
                width=3,
                label="")
        self._preview_fade_coeff.pack(side=LEFT, padx=(0, 5), pady=5)

        self._preview_size = LabelEntry(
                canvas_frame,
                convert=int,
                width=3,
                label="preview size")
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
        self._preview_fade_coeff.set(100)
        # >>>4

        # geometry of result    <<<4
        self._geometry_tabs = Notebook(self)
        self._geometry_tabs.grid(row=0, column=1, sticky=E+W, padx=5, pady=5)

        self._geometry_plane_tab = Frame(self._geometry_tabs)
        self._geometry_tabs.add(self._geometry_plane_tab, text="plane")

        coord_frame = LabelFrame(self._geometry_plane_tab, text="coordinates")
        coord_frame.pack(padx=5, pady=5)
        # coord_frame.grid(row=0, column=1, sticky=E+W, padx=5, pady=5)
        coord_frame.columnconfigure(0, weight=1)
        coord_frame.columnconfigure(1, weight=1)

        self._x_min = LabelEntry(coord_frame, label="x min",
                                 value=WORLD_GEOMETRY[0],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._x_min.grid(row=0, column=0, padx=5, pady=5)

        self._x_max = LabelEntry(coord_frame, label="x max",
                                 value=WORLD_GEOMETRY[1],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._x_max.grid(row=0, column=1, padx=5, pady=5)

        self._y_min = LabelEntry(coord_frame, label="y min",
                                 value=WORLD_GEOMETRY[2],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._y_min.grid(row=1, column=0, padx=5, pady=5)

        self._y_max = LabelEntry(coord_frame, label="y max",
                                 value=WORLD_GEOMETRY[3],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._y_max.grid(row=1, column=1, padx=5, pady=5)

        transformation_frame = LabelFrame(self._geometry_plane_tab,
                                          text="transformation")
        transformation_frame.pack(padx=5, pady=5, fill=BOTH)
        self._modulus = LabelEntry(transformation_frame, label="modulus",
                                   value=1,
                                   convert=float,
                                   width=6)
        self._modulus.pack(padx=5, pady=5)

        self._angle = LabelEntry(transformation_frame, label="angle (°)",
                                 value=0,
                                 convert=float,
                                 width=4)
        self._angle.pack(padx=5, pady=5)

        Button(transformation_frame, text="zoom -",
               command=self.zoom(2**.25)).pack(side=LEFT,
                                              padx=5, pady=5)
        Button(transformation_frame, text="zoom +",
               command=self.zoom(2**-.25)).pack(side=RIGHT,
                                               padx=5, pady=5)

        Button(self._geometry_plane_tab, text="reset",
               command=self.reset_geometry).pack(side=TOP,
                                                 padx=5, pady=(5, 10))

        # >>>4

        # sphere parameters     <<<4
        self._geometry_sphere_tab = Frame(self._geometry_tabs)
        self._geometry_tabs.add(self._geometry_sphere_tab, text="sphere")
        self._geometry_tabs.bind(
                "<Double-Button-1>",
                lambda _: self._geometry_tabs.tab(self._geometry_sphere_tab,
                                                  state=NORMAL))

        self._sphere_projection = BooleanVar()
        self._sphere_projection.set(True)

        sphere_projection = Checkbutton(self._geometry_sphere_tab,
                                           text="stereographic projection",
                                           variable=self._sphere_projection,
                                           onvalue=True, offvalue=False,
                                           indicatoron=False,
                                           )
        sphere_projection.pack(padx=5, pady=10)

        self._rotations = LabelEntry(self._geometry_sphere_tab,
                                     label="rotations x, y, z (°)",
                                     orientation="V",
                                     value="15, 15, 0",
                                     convert=str_to_floats,
                                     width=15)
        self._rotations.pack(padx=5, pady=10)

        background_frame = Frame(self._geometry_sphere_tab)
        background_frame.pack(padx=5, pady=5)

        self._sphere_background_full_filename = ""
        self._sphere_background = StringVar()

        Button(background_frame,
               text="background",
               command=self.choose_sphere_background,
               padx=1, pady=1
               ).pack(side=LEFT)
        Entry(background_frame,
              textvar=self._sphere_background,
              width=10).pack(side=RIGHT)
        self.sphere_background = DEFAULT_SPHERE_BACKGROUND

        self._sphere_background_fading = LabelEntry(self._geometry_sphere_tab,
                                                    label="fade background",
                                                    value=100,
                                                    width=5,
                                                    convert=int)
        self._sphere_background_fading.pack(padx=5, pady=10)

        self._sphere_stars = LabelEntry(self._geometry_sphere_tab,
                                        label="random stars",
                                        value=500,
                                        width=5,
                                        convert=int)
        self._sphere_stars.pack(padx=5, pady=10)
        # >>>4

        # result settings       <<<4
        settings_frame = LabelFrame(self, text="output")
        settings_frame.grid(row=2, column=1, sticky=E+W, padx=5, pady=5)

        self._width = LabelEntry(settings_frame,
                                 label="width", value=OUTPUT_WIDTH,
                                 convert=int,
                                 width=6, justify=RIGHT)
        self._width.pack(padx=5, pady=5)

        self._height = LabelEntry(settings_frame,
                                  label="height", value=OUTPUT_HEIGHT,
                                  convert=int,
                                  width=6, justify=RIGHT)
        self._height.pack(padx=5, pady=5)

        self._filename_template = LabelEntry(settings_frame,
                                             label="filename template",
                                             orientation="V",
                                             value=FILENAME_TEMPLATE,
                                             font="TkNormal 8",
                                             width=24)
        self._filename_template.pack(padx=5, pady=5)
        # >>>4

        # image buttons (preview / save)    <<<4
        tmp = LabelFrame(self, text="image")
        tmp.grid(row=3, column=1, sticky=E+W, padx=5, pady=5)

        self._preview_button = Button(tmp, text="preview", command=None)
        self._preview_button.pack(side=TOP, padx=10, pady=10)

        self._save_preview_button = Button(
                tmp,
                text="save preview",
                command=None
                )
        self._save_preview_button.pack(side=LEFT, padx=10, pady=10)

        self._save_button = Button(tmp, text="save", command=None)
        self._save_button.pack(side=RIGHT, padx=10, pady=10)

        # >>>4

        self.adjust_geometry()
    # >>>3

    def disable_geometry_sphere_tab(self):  # <<<3
        self.sphere_projection = True
        self._geometry_tabs.tab(self._geometry_sphere_tab, state=DISABLED)
    # >>>3

    def enable_geometry_sphere_tab(self):   # <<<3
        self._geometry_tabs.tab(self._geometry_sphere_tab, state=NORMAL)
    # >>>3

    def reset_geometry(self, *args):        # <<<3
        self.geometry = WORLD_GEOMETRY
        self.adjust_geometry()
        self.angle = 0
        self.modulus = 1
        self.rotations = 0, 0, 0
    # >>>3

    def zoom(self, alpha):      # <<<3
        def zoom_tmp(*args):
            self.modulus /= alpha
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

            R = mult_M(R1, R2)
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
                filetypes=[("images", "*.jpg *.jpeg *.png"), ("all", "*.*")])
        if filename:
            self.sphere_background = filename
    # >>>3

    def update(self, *args):   # <<<3
        if self.draw_orbifold:
            self._draw_mirrors_button.config(state=NORMAL)
        else:
            self._draw_mirrors_button.config(state=DISABLED)

        if self.preview_fade:
            self._preview_fade_coeff.enable()
        else:
            self._preview_fade_coeff.disable()
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

    @property
    def config(self):           # <<<3
        cfg = {}
        for k in ["geometry_tab",
                  "geometry", "modulus", "angle",
                  "size", "filename_template",
                  "preview_size",
                  "draw_tile", "draw_orbifold", "draw_color_tile",
                  "draw_mirrors", "preview_fade", "preview_fade_coeff",
                  "sphere_projection", "sphere_rotations",
                  "sphere_background", "sphere_background_fading",
                  "sphere_stars"]:
            cfg[k] = getattr(self, k)
        return cfg
    # >>>3

    @config.setter
    def config(self, cfg):      # <<<3
        for k in ["geometry_tab",
                  "geometry", "modulus", "angle",
                  "size", "filename_template",
                  "preview_size",
                  "draw_tile", "draw_orbifold", "draw_color_tile",
                  "draw_mirrors", "preview_fade", "preview_fade_coeff",
                  "sphere_projection", "sphere_rotations",
                  "sphere_background", "sphere_background_fading",
                  "sphere_stars"]:
            if k in cfg:
                setattr(self, k, cfg[k])
    # >>>3
# >>>2


class Function(LabelFrame):     # <<<2

    # setters and getters <<<3
    @property
    def current_tab(self):      # <<<4
        if ("wallpaper" in self._tabs.tab(self._tabs.select(), "text")):
            return "wallpaper"
        elif ("sphere" in self._tabs.tab(self._tabs.select(), "text")):
            return "sphere"
        elif ("hyper" in self._tabs.tab(self._tabs.select(), "text")):
            return "hyperbolic"
        else:
            assert False
    # >>>4

    @current_tab.setter
    def current_tab(self, tab):      # <<<4
        tab = tab.lower().strip()
        if tab == "wallpaper":
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
        for i in range(len(S_NAMES)):
            tmp = S_NAMES[i]
            tmp = tmp.replace("(", " ").replace(")", " ")
            tmp = tmp.split()
            if p in tmp:
                self._sphere_combo.current(i)
                return
        self._sphere_combo.current(0)
    # >>>4

    @property
    def current_pattern(self):          # <<<4
        if self.current_tab == "wallpaper":
            color_pattern = self.wallpaper_color_pattern
            if color_pattern:
                return (color_pattern, self.wallpaper_pattern)
            else:
                return self.wallpaper_pattern
            return self.wallpaper_pattern
        elif self.current_tab == "sphere":
            return self.sphere_pattern
        elif self.current_tab == "hyperbolic":
            return "hyperbolic"
        else:
            return ""
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
    def wallpaper_basis(self):      # <<<4
        return basis(self.current_pattern, *self.lattice_parameters)
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
    def hyper_disk_model(self):       # <<<4
        return self._hyper_disk_model.get()
    # >>>4

    @hyper_disk_model.setter          # <<<4
    def hyper_disk_model(self, b):
        self._hyper_disk_model.set(b)
    # >>>4
    # >>>3

    def __init__(self, root):      # <<<3
        self.root = root
        LabelFrame.__init__(self, root)
        self.configure(text="Function")

        # tabs for the different kinds of functions / symmetries  <<<4
        self._tabs = Notebook(self)
        self._tabs.grid(row=0, column=0, rowspan=2, sticky=N+S, padx=5, pady=5)

        self._wallpaper_tab = Frame(self._tabs)
        self._tabs.add(self._wallpaper_tab, text="wallpaper")

        self._sphere_tab = Frame(self._tabs)
        self._tabs.add(self._sphere_tab, text="sphere")

        self._hyper_tab = Frame(self._tabs)
        self._tabs.add(self._hyper_tab, text="hyperbolic")
        # >>>4

        # wallpaper tab      <<<4
        Label(self._wallpaper_tab,
              text="symmetry group").pack(padx=5, pady=(20, 0))
        self._wallpaper_pattern = StringVar()
        self._wallpaper_combo = Combobox(
                self._wallpaper_tab, width=38, exportselection=0,
                textvariable=self._wallpaper_pattern,
                state="readonly",
                values=W_NAMES
                )
        self._wallpaper_combo.pack(padx=5, pady=5)
        self._wallpaper_combo.current(0)

        self._wallpaper_combo.bind("<<ComboboxSelected>>",
                                   self.update)

        Label(self._wallpaper_tab,
              text="color symmetry group").pack(padx=5, pady=(5, 0))
        self._wallpaper_color_pattern = StringVar()
        self._wallpaper_color_combo = Combobox(
                self._wallpaper_tab, width=20, exportselection=0,
                textvariable=self._wallpaper_color_pattern,
                state="readonly",
                values=["--"]
                )
        self._wallpaper_color_combo.pack(padx=5, pady=5)
        self._wallpaper_color_combo.current(0)

        self._wallpaper_color_combo.bind("<<ComboboxSelected>>",
                                         self.update)

        self._lattice_parameters = LabelEntry(self._wallpaper_tab,
                                          orientation="V",
                                          label="lattice parameters",
                                          value="",
                                          convert=str_to_floats,
                                          width=10)
        self._lattice_parameters.pack(padx=5, pady=5)

        self._wallpaper_N = LabelEntry(self._wallpaper_tab,
                                       orientation="V",
                                       label="forced rotational symmetry",
                                       value=1,
                                       convert=int,
                                       width=3)
        self._wallpaper_N.pack(padx=5, pady=5)
        self._wallpaper_N.disable()
        self._wallpaper_N.bind(
                "<Double-Button-1>",
                sequence(self._wallpaper_N.toggle))
        # # >>>4

        # sphere tab        <<<4
        Label(self._sphere_tab,
              text="symmetry group").pack(padx=5, pady=(20, 0))
        self._sphere_pattern = StringVar()
        self._sphere_combo = Combobox(self._sphere_tab, width=20,
                                      exportselection=0,
                                      textvariable=self._sphere_pattern,
                                      state="readonly",
                                      values=S_NAMES)
        self._sphere_combo.pack(padx=5, pady=5)
        self._sphere_combo.current(0)
        self._sphere_combo.bind("<<ComboboxSelected>>",
                                self.update)

        self._sphere_N = LabelEntry(self._sphere_tab,
                                    label="N",
                                    value=7,
                                    convert=int,
                                    width=2)
        self._sphere_N.pack(padx=5, pady=5)

        radio_frame = Frame(self._sphere_tab)
        radio_frame.pack(padx=5, pady=(10, 5))
        self._sphere_mode = StringVar()
        self._sphere_mode.set("sphere")
        Radiobutton(radio_frame,
                    indicatoron=0,
                    text="sphere",
                    variable=self._sphere_mode,
                    value="sphere",
                    command=self.update
                    ).grid(row=0, column=0, padx=5, pady=5)
        Radiobutton(radio_frame,
                    indicatoron=0,
                    text="rosette",
                    variable=self._sphere_mode,
                    value="rosette",
                    command=self.update
                    ).grid(row=0, column=1, padx=5, pady=5)
        Radiobutton(radio_frame,
                    indicatoron=0,
                    text="frieze",
                    variable=self._sphere_mode,
                    value="frieze",
                    command=self.update
                    ).grid(row=0, column=2, padx=5, pady=5)
        # >>>4

        # hyperbolic tab        <<<4
        self._hyper_nb_steps = LabelEntry(
                self._hyper_tab,
                label="averaging steps",
                width=5,
                convert=int,
                value=25)
        self._hyper_nb_steps.pack(padx=5, pady=(20, 5))

        self._hyper_disk_model = BooleanVar()
        self._hyper_disk_model_button = Checkbutton(
                self._hyper_tab,
                variable=self._hyper_disk_model,
                text="disk model",
                onvalue=True, offvalue=False,
                indicatoron=False)
        self._hyper_disk_model_button.pack(padx=5, pady=(20, 5))
        self._hyper_disk_model.set(True)
        # >>>4

        # display matrix    <<<4
        main_matrix_frame = LabelFrame(self, text="matrix")
        main_matrix_frame.grid(row=0, column=1,
                               sticky=N+S+E+W,  padx=5, pady=5)

        scroll_matrix_frame = Frame(main_matrix_frame)
        scroll_matrix_frame.pack()
        self._display_matrix = Listbox(scroll_matrix_frame,
                                       selectmode=MULTIPLE,
                                       font="TkFixedFont",
                                       width=30, height=8)
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
        self._change_entry = LabelEntry(main_matrix_frame,
                                        label="change entry", value="",
                                        width=17, font="TkFixedFont")
        self._change_entry.pack(padx=5, pady=5)
        self._change_entry.bind("<Return>", self.add_entry)

        Button(main_matrix_frame, text="make matrix",
               command=self.make_matrix).pack(side=LEFT, padx=5, pady=10)

        Button(main_matrix_frame,
               text="reset",
               command=lambda *_: self.change_matrix({})
               ).pack(side=RIGHT, padx=5, pady=5)
        # >>>4

        # random matrix     <<<4
        random_frame = LabelFrame(self, text="random matrix")
        random_frame.grid(row=0, column=2, sticky=N+S, padx=5, pady=5)

        self._random_nb_coeffs = LabelEntry(random_frame, label="nb entries",
                                            value=3,
                                            convert=int,
                                            width=4)
        self._random_nb_coeffs.pack(padx=5, pady=5)

        self._random_min_degre = LabelEntry(random_frame, label="min degre",
                                            value=-3,
                                            convert=int,
                                            width=4)
        self._random_min_degre.pack(padx=5, pady=5)

        self._random_max_degre = LabelEntry(random_frame, label="max degre",
                                            value=3,
                                            convert=int,
                                            width=4)
        self._random_max_degre.pack(padx=5, pady=5)

        self._random_modulus = LabelEntry(random_frame, label="modulus",
                                          value=1,
                                          convert=float,
                                          width=4)
        self._random_modulus.pack(padx=5, pady=5)

        generate = Button(random_frame,
                          text="generate",
                          command=self.new_random_matrix)
        generate.pack(padx=5, pady=5)
        # >>>4

        # add noise <<<4
        self._random_noise = LabelEntry(random_frame, label="",
                                        value=10, convert=float,
                                        width=3)
        self._random_noise.pack(side=RIGHT, padx=5, pady=5)
        self._random_noise.bind("<Return>", self.add_noise)

        random_noise = Button(random_frame, text="noise (%)",
                              command=self.add_noise)
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
                    .format(n, m, complex_to_str(M[(n, m)])))
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
            z = re.sub("\s*", "", z)
            z = z.replace("i", "j")
            z = complex(z)
            if z == 0:
                del self.matrix[(n, m)]
            else:
                self.matrix[(n, m)] = z
            self.change_matrix()
            self_change_entry = ""
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

        if self.current_tab == "wallpaper":
            pattern = self.wallpaper_pattern
            color_pattern = self.wallpaper_color_pattern
            if color_pattern:
                sub = PATTERN[color_pattern, pattern]
                parity = sub["parity"]
                M = add_symmetries(M,
                                   PATTERN[color_pattern, pattern]["recipe"],
                                   PATTERN[color_pattern, pattern]["parity"])
            else:
                M = add_symmetries(M, PATTERN[pattern]["recipe"])
        elif self.current_tab == "sphere":
            M = add_symmetries(M,
                               PATTERN[self.sphere_pattern]["recipe"],
                               PATTERN[self.sphere_pattern]["parity"]
                               .replace("N", str(self.sphere_N)))
        elif self.current_tab == "hyperbolic":
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
                  "current_tab",
                  "wallpaper_pattern", "lattice_parameters",
                  "wallpaper_color_pattern",
                  "sphere_pattern", "sphere_N", "sphere_mode",
                  "hyper_nb_steps", "hyper_disk_model"]:
            cfg[k] = getattr(self, k)
        return cfg
    # >>>3

    @config.setter
    def config(self, cfg):      # <<<3
        for k in ["matrix",
                  "random_nb_coeffs", "random_min_degre",
                  "random_max_degre", "random_modulus", "random_noise",
                  "current_tab",
                  "wallpaper_pattern",  # "lattice_parameters",
                  # "wallpaper_color_pattern",
                  "sphere_pattern", "sphere_N", "sphere_mode",
                  "hyper_nb_steps", "hyper_disk_model"]:
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
        if "lattice_parameters" in cfg:
            self.lattice_parameters = cfg["lattice_parameters"]
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

        lattice = PATTERN[self.current_pattern]["description"]
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
            self._lattice_parameters.label_widget.config(text=lattice + ": x1,y1,x2,y2")
            self._lattice_parameters.convert = det_not_null
            self.lattice_parameters = [1, 0, 1, 1]
        elif lattice0 == "rhombic":
            self._lattice_parameters.enable()
            self._lattice_parameters.label_widget.config(text=lattice + ": b")
            self._lattice_parameters.convert = not_zero
            self.lattice_parameters = [.5]
        elif lattice0 == "rectangular":
            self._lattice_parameters.enable()
            self._lattice_parameters.convert = not_zero
            self.lattice_parameters = [.5]
            self._lattice_parameters.label_widget.config(text=lattice + ": H")
        elif lattice0 == "square":
            self._lattice_parameters.convert = None
            self.lattice_parameters = []
            self._lattice_parameters.label_widget.config(text=lattice)
            self._lattice_parameters.disable()
        elif lattice0 == "hexagonal":
            self._lattice_parameters.convert = None
            self.lattice_parameters = []
            self._lattice_parameters.label_widget.config(text=lattice)
            self._lattice_parameters.disable()
        else:
            assert False

        # >>>4
    # >>>3

    @property
    def pattern_params(self):       # <<<3
        if self.current_tab == "wallpaper":
            return {"lattice_basis": self.wallpaper_basis,
                    "color_pattern": self.wallpaper_color_pattern,
                    "N": self.wallpaper_N}
        elif self.current_tab == "sphere":
            return {"N": self.sphere_N,
                    "sphere_mode": self.sphere_mode}
        elif self.current_tab == "hyperbolic":
            return {"nb_steps": self.hyper_nb_steps,
                    "disk_model": self.hyper_disk_model}
        else:
            assert False
    # >>>3
# >>>2


class CreateSymmetry(Tk):      # <<<2

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

        self.world = World(self)

        self.function = Function(self)

        self.colorwheel.grid(row=0, column=0, sticky=N+S, padx=10, pady=10)
        self.world.grid(row=0, column=1, sticky=N+S, padx=10, pady=10)
        self.function.grid(row=1, column=1, sticky=E+W, padx=10, pady=10)

        console_frame = Frame(self)
        console_frame.grid(row=1, column=0, padx=0, pady=0)

        self._console = Text(
                console_frame, width=28, height=15,
                background="black", foreground="white",
                font="TkFixedFont",
                borderwidth=3,
                relief="ridge")
        self._console.grid(row=1, column=0,
                           sticky=E+W+N+S, padx=10, pady=(10, 0))
        self._console.config(state=DISABLED)

        self._preview_console = Text(
                console_frame, width=10, height=1,
                background="black", foreground="white",
                font="TkFixedFont",
                borderwidth=3,
                relief="ridge")
        self._preview_console.grid(row=2, column=0, sticky=E+W,
                                   padx=10, pady=0)
        self._preview_console.config(state=DISABLED)

        self._output_console = Text(
                console_frame, width=10, height=1,
                background="black", foreground="white",
                font="TkFixedFont",
                borderwidth=3,
                relief="ridge")
        self._output_console.grid(row=3, column=0, sticky=E+W,
                                  padx=10, pady=(0, 10))
        self._output_console.config(state=DISABLED)
        # >>>4

        # attach appropriate actions to buttons     <<<4
        self.world._preview_button.config(command=sequence(self.make_preview))
        self.world._save_button.config(command=sequence(self.make_output))
        self.world._save_preview_button.config(
                command=sequence(self.save_preview)
                )
        # >>>4

        # keybindings       <<<4
        self.bind("<Control-h>", sequence(self.display_help))
        self.bind("?", sequence(self.display_help))
        self.bind("<F1>", sequence(self.display_help))

        self.bind("<Control-q>", sequence(self.destroy))

        self.bind("<Control-p>", sequence(self.make_preview))
        self.bind("<Control-s>", sequence(self.make_output))
        self.bind("<Control-S>", sequence(self.save_preview))

        self.bind("<Control-n>", sequence(self.function.add_noise))
        self.bind("<Control-N>", sequence(self.function.add_noise,
                                          self.make_preview))

        self.bind("<Control-g>", sequence(self.function.new_random_matrix))
        self.bind("<Control-G>", sequence(self.new_random_preview))

        self.bind("<Control-Key-minus>", sequence(self.world.zoom(2**.25),
                                                  self.make_preview))
        self.bind("<Control-Key-plus>", sequence(self.world.zoom(2**-.25),
                                                 self.make_preview))

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
        self.bind("<Control-0>", sequence(self.world.reset_geometry,
                                          self.make_preview))

        self.bind("<Control-u>", sequence(self.undo))
        self.bind("<Control-r>", sequence(self.redo))
        self.bind("<Control-U>", sequence(self.undo,
                                          self.make_preview))
        self.bind("<Control-R>", sequence(self.redo,
                                          self.make_preview))

        self.world._canvas.bind("<Double-Button-1>", self.show_bigger_preview)

        self.world._canvas.bind("<ButtonPress-1>", self.start_zoom_rectangle)
        self.world._canvas.bind("<B1-Motion>", self.update_zoom_rectangle)
        self.world._canvas.bind("<ButtonRelease-1>", self.apply_zoom_rectangle)

        self.colorwheel._canvas.bind(
                "<Double-Button-1>",
                sequence(
                    self.colorwheel.switch_colorwheel,
                    self.make_preview
                    )
                )

        # def get_focus(event):
        #     print(event.widget)
        #     event.widget.focus()
        # self.bind_all(
        #         "<Button-1>", get_focus)
        # >>>4

        # <<<4
        self.function._tabs.bind("<<NotebookTabChanged>>",
                                 self.update_world_tab)
        self.function._sphere_mode.trace(
                "w",
                callback=self.update_world_tab)

        # update settings (checkbutton for showing orbifold for color pattern)
        self.function._wallpaper_combo.bind(
                "<<ComboboxSelected>>",
                self.update_world_tab,
                add="+"
                )
        self.function._wallpaper_color_combo.bind(
                "<<ComboboxSelected>>",
                self.update_world_tab,
                add="+"
                )

        self.world._draw_tile_button.config(
                command=self.update_world_preview
                )
        self.world._draw_orbifold_button.config(
                command=self.update_world_preview
                )
        self.world._draw_color_tile_button.config(
                command=self.update_world_preview
                )
        self.world._draw_mirrors_button.config(
                command=self.update_world_preview
                )
        self.world._fade_button.config(
                command=self.update_world_preview
                )
        self.world._preview_fade_coeff.bind("<Return>", self.update_world_preview)
        self.world._preview_fade_coeff.bind("<FocusOut>", self.update_world_preview)
        # >>>4

        # list of matrices, for UNDO
        self.undo_list = []
        self.undo_index = -1

        # queue containing parameters for pending output jobs
        self.output_params_queue = Queue()
        # are there pending output jobs?
        self.pending_output_jobs = False
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
    # >>>3

    def display_help(self):     # <<<3
        dialog = Toplevel(self)
        dialog.resizable(width=False, height=False)

        text = Text(dialog, height=35)
        text.pack(padx=10, pady=10)
        text.insert(END, """
create_symmetry.py : a Python script to experiment with
Frank Farris recipes from his book "Creating Symmetry"

Keyboard shortcuts:

  Control-h     this help message
  F1            this help message
  ?             this help message

  Control-q     quit

  Control-p     compute and display preview
  Control-s     compute and save result to file
  Control-s     save current preview to file

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
  Control-Z     for spherical pattern, rotate around z-axis

  Control-u     undo: go back to previous state
  Control-r     redo
  Control-U     undo: go back to previous state and compute preview
  Control-R     redo
""")
        text.config(state=DISABLED)

        dialog.bind("<Escape>", lambda _: dialog.destroy())
        dialog.bind("<Control-q>", lambda _: dialog.destroy())
        ok = Button(dialog, text="OK",
                    command=lambda: dialog.destroy())
        ok.pack(padx=10, pady=10)
        ok.focus_set()
        self.wait_window(dialog)
    # >>>3

    def update_world_tab(self, *args):       # <<<3
        # enable / disable sphere geometry tab
        if self.function.current_tab in ["sphere"]:
            if self.function.sphere_mode in ["rosette", "frieze"]:
                self.world.sphere_projection = True
                self.world.disable_geometry_sphere_tab()
                self.world.geometry_tab = "plane"
            elif self.function.sphere_mode == "sphere":
                self.world.enable_geometry_sphere_tab()
                self.world.sphere_projection = False
                self.world.geometry_tab = "sphere"
            else:
                assert False
        else:
            self.world.disable_geometry_sphere_tab()

        # enable / disable tiling / orbifold drawing buttons
        if self.function.current_tab in ["sphere", "hyperbolic"]:
            self.world.draw_tile = False
            self.world.draw_orbifold = False
            self.world.draw_mirrors = False
            self.world.preview_fade = False
            self.world._draw_tile_button.config(state=DISABLED)
            self.world._draw_orbifold_button.config(state=DISABLED)
            self.world._draw_color_tile_button.config(state=DISABLED)
            self.world._draw_mirrors_button.config(state=DISABLED)
            self.world._fade_button.config(state=DISABLED)
            self.world._preview_fade_coeff.disable()
        else:
            self.world._draw_tile_button.config(state=NORMAL)
            self.world._draw_orbifold_button.config(state=NORMAL)
            self.world._draw_color_tile_button.config(state=NORMAL)
            self.world._draw_mirrors_button.config(state=NORMAL)
            self.world._fade_button.config(state=NORMAL)
            self.world._preview_fade_coeff.enable()
            if self.function.wallpaper_color_pattern == "":
                self.world._draw_color_tile_button.config(state=DISABLED)
            else:
                self.world._draw_color_tile_button.config(state=NORMAL)

            self.world.update()

    # >>>3

    def start_zoom_rectangle(self, event):   # <<<3
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.world._canvas.create_rectangle(
                self.start_x,
                self.start_y,
                self.start_x,
                self.start_y,
                width=3,
                outline="white")
    # >>>3

    def update_zoom_rectangle(self, event):     # <<<3
        curX, curY = (event.x, event.y)
        ratio = self.world.width / self.world.height
        if curX <= self.start_x or curY <= self.start_y:
            curX = self.start_x
            curY = self.start_y
        elif ratio > (curX-self.start_x) / (curY-self.start_y):
            curX = self.start_x + (curY-self.start_y) * ratio
        else:
            curY = self.start_y + (curX-self.start_x) / ratio
        self.world._canvas.coords(
                self.rect,
                self.start_x,
                self.start_y,
                curX,
                curY)
    # >>>3

    def apply_zoom_rectangle(self, event):     # <<<3
        try:
            self.world._canvas.delete(self.rect)
        except AttributeError:
            pass
        curX, curY = (event.x, event.y)
        ratio = self.world.width / self.world.height
        if curX <= self.start_x or curY <= self.start_y:
            return
        elif ratio > (curX-self.start_x) / (curY-self.start_y):
            curX = self.start_x + (curY-self.start_y) * ratio
        else:
            curY = self.start_y + (curX-self.start_x) / ratio

        x_min, x_max, y_min, y_max = self.world.geometry
        try:
            delta_x = self.world._canvas._img.width / (x_max - x_min)
            delta_y = self.world._canvas._img.height / (y_max - y_min)
            px_center, py_center = self.world._canvas.coords(
                    self.world._canvas._image_id
                    )
            x_center = (x_max - x_min) / 2
            y_center = (y_max - y_min) / 2
        except AttributeError:
            return
        x1 = (self.start_x - px_center) / delta_x
        x2 = (curX - px_center) / delta_x
        y1 = -(self.start_y - py_center) / delta_y
        y2 = -(curY - py_center) / delta_y
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)
        self.world.geometry = x_min, x_max, y_min, y_max
        self.make_preview()
    # >>>3

    def update_world_preview(self, *args):       # <<<3
        try:
            self.world._canvas.delete(self.world._canvas._image_id)
        except AttributeError:
            pass
        try:
            if self.world.preview_fade:
                preview_fade = fade_image(
                        self.world._canvas._img,
                        255-self.world.preview_fade_coeff
                        )
                self.world._canvas.tk_img = PIL.ImageTk.PhotoImage(preview_fade)
            else:
                self.world._canvas.tk_img = PIL.ImageTk.PhotoImage(
                        self.world._canvas._img
                        )

            self.world._canvas._image_id = self.world._canvas.create_image(
                        (PREVIEW_SIZE//2, PREVIEW_SIZE//2),
                        image=self.world._canvas.tk_img)
        except AttributeError:
            pass

        def rm_tile(name):
            try:
                img_id = getattr(self.world._canvas, name + "_id")
                self.world._canvas.delete(img_id)
            except AttributeError:
                pass

        def put_tile(name):
            try:
                if isinstance(getattr(self.world._canvas, name), tuple):
                    img = make_tile(*getattr(self.world._canvas, name))
                    tk_img = PIL.ImageTk.PhotoImage(img)
                    setattr(self.world._canvas, name, img)
                    setattr(self.world._canvas, "tk" + name, tk_img)
                img_id = self.world._canvas.create_image(
                    (PREVIEW_SIZE//2, PREVIEW_SIZE//2),
                    image=getattr(self.world._canvas, "tk" + name)
                )
                setattr(self.world._canvas, name + "_id", img_id)
            except AttributeError:
                pass

        rm_tile("_tile_img")
        rm_tile("_color_tile_img")
        if self.world.draw_tile:
            if self.world.draw_color_tile:
                put_tile("_color_tile_img")
            else:
                put_tile("_tile_img")

        rm_tile("_orbifold_img")
        if self.world.draw_orbifold:
            if self.world.draw_color_tile:
                put_tile("_color_orbifold_img")
            else:
                put_tile("_orbifold_img")

        rm_tile("_mirrors_img")
        if self.world.draw_orbifold and self.world.draw_mirrors:
            if self.world.draw_color_tile:
                put_tile("_color_mirrors_img")
            else:
                put_tile("_mirrors_img")

    # >>>3

    def update_GUI(self):        # <<<3

        # console messages
        self._console.config(state=NORMAL)
        while not self.message_queue.empty():
            self._console.insert(END,
                                 self.message_queue.get(block=False) + "\n")
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
                            # "Preview: [{}]".format(m))
                            "Preview: {}%".format(int(m*100)))
                    self._preview_console.config(state=DISABLED)
                elif self.preview_image_queue.empty():
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
                            # "output ({}): [{}]"
                            # .format(1+self.output_params_queue.qsize(), m))
                            "output ({}): {}%"
                            .format(1+self.output_params_queue.qsize(),
                                    int(m*100)))
                    self._output_console.config(state=DISABLED)
                elif not self.pending_output_jobs:
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
                    # FIXME: methode change_preview in World class

                    self.world._canvas._img = image
                    self.world._canvas.tk_img = PIL.ImageTk.PhotoImage(image)

                    try:
                        self.world._canvas.delete(self.world._canvas._image_id)
                    except AttributeError:
                        pass

                    self.world._canvas._image_id = self.world._canvas.create_image(
                                    (PREVIEW_SIZE//2, PREVIEW_SIZE//2),
                                    image=self.world._canvas.tk_img)

                    # name all argument of make tile and use dictionary here
                    self.world._canvas._tile_img = (
                                self.world.geometry,
                                (self.world.modulus, self.world.angle),
                                self.function.current_pattern,
                                self.function.wallpaper_basis,
                                image.size,
                                True,
                                False,
                                False,
                                False
                                )

                    self.world._canvas._orbifold_img = (
                                self.world.geometry,
                                (self.world.modulus, self.world.angle),
                                self.function.current_pattern,
                                self.function.wallpaper_basis,
                                image.size,
                                False,
                                True,
                                False,
                                False
                                )

                    self.world._canvas._mirrors_img = (
                                self.world.geometry,
                                (self.world.modulus, self.world.angle),
                                self.function.current_pattern,
                                self.function.wallpaper_basis,
                                image.size,
                                False,
                                True,
                                False,
                                True
                                )

                    self.world._canvas._color_tile_img = (
                                self.world.geometry,
                                (self.world.modulus, self.world.angle),
                                self.function.current_pattern,
                                self.function.wallpaper_basis,
                                image.size,
                                True,
                                False,
                                True,
                                False
                                )

                    self.world._canvas._color_orbifold_img = (
                                self.world.geometry,
                                (self.world.modulus, self.world.angle),
                                self.function.current_pattern,
                                self.function.wallpaper_basis,
                                image.size,
                                False,
                                True,
                                True,
                                False
                                )

                    self.world._canvas._color_mirrors_img = (
                                self.world.geometry,
                                (self.world.modulus, self.world.angle),
                                self.function.current_pattern,
                                self.function.wallpaper_basis,
                                image.size,
                                False,
                                True,
                                True,
                                True
                                )

                    self.update_world_preview()
                break

        self.after(100, self.update_GUI)
    # >>>3

    def make_output(self, *args):      # <<<3
        config = {
                "color": self.colorwheel.config,
                "world": self.world.config,
                "function": self.function.config,
                "params": self.function.pattern_params,
                "pattern": self.function.current_pattern,
                "matrix": self.function.matrix,
                }
        self.output_params_queue.put(config)

        def output_thread():
            self.pending_output_jobs = True
            while True:
                try:
                    config = self.output_params_queue.get(timeout=0.1)
                except queue.Empty:
                    break
                config["message_queue"] = self.message_queue
                config["output_message_queue"] = self.output_message_queue
                p = Process(target=background_output, kwargs=config)
                p.start()
                p.join()
            self.pending_output_jobs = False

        if not self.pending_output_jobs:
            Thread(target=output_thread).start()
    # >>>3

    def make_preview(self, *args):      # <<<3

        self.world.adjust_geometry()
        ratio = self.world.width / self.world.height
        if (self.world.width < self.world.preview_size and
                self.world.height < self.world.preview_size):
            width = self.world.width
            height = self.world.height
        elif ratio > 1:
            width = self.world.preview_size
            height = round(self.world.preview_size / ratio)
        else:
            width = round(self.world.preview_size * ratio)
            height = self.world.preview_size

        def make_preview_job():
            color = self.colorwheel.config
            world = self.world.config
            world["size"] = (width, height)
            params = self.function.pattern_params

            image = make_image(color=color,
                               world=world,
                               pattern=self.function.current_pattern,
                               matrix=self.function.matrix,
                               message_queue=self.preview_message_queue,
                               stretch_color=self.colorwheel.stretch,
                               tile=False,
                               **params)
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
            self.preview_config = {
                    "color": self.colorwheel.config,
                    "world": self.world.config,
                    "function": self.function.config,
                    "params": self.function.pattern_params,
                    "pattern": self.function.current_pattern,
                    "matrix": self.function.matrix,
                    }
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
        img = self.world._canvas._img
        width, height = img.size
        if self.world.preview_fade:
            img = fade_image(img)

        def paste_tile(name):
            try:
                tile = getattr(self.world._canvas, name)
                img.paste(tile, mask=tile)
            except:
                pass

        if self.world.draw_tile:
            if self.world.draw_color_tile:
                paste_tile("_color_tile_img")
            else:
                paste_tile("_tile_img")
        if self.world.draw_orbifold:
            if self.world.draw_color_tile:
                paste_tile("_color_orbifold_img")
            else:
                paste_tile("_orbifold_img")
        if self.world.draw_mirrors:
            if self.world.draw_color_tile:
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
            if self.world.geometry_tab == "sphere":
                if dx != 0 or dy != 0 or dz != 0:
                    self.world.rotate(dx, dy, dz)
            elif self.world.geometry_tab == "plane":
                if dx != 0 or dy != 0:
                    self.world.translate(dx/10, dy/10)
                elif dz != 0:
                    self.world.angle -= dz
            else:
                assert False
        return translate_rotate_tmp
    # >>>3

    def new_random_preview(self, nb_tries=100):       # <<<3
        for i in range(nb_tries):
            self.function.new_random_matrix()
            if self.function.add_symmetries(self.function.matrix):
                break
        self.make_preview()
    # >>>3

    def undo(self):     # <<<3
        # print(">>", self.undo_index, len(self.undo_list))
        if abs(self.undo_index) < len(self.undo_list):
            self.undo_index -= 1
            config = self.undo_list[self.undo_index]
            self.world.config = config["world"]
            self.function.config = config["function"]
            self.colorwheel.config = config["color"]
    # >>>3

    def redo(self):     # <<<3
        # print(">>>", self.undo_index, len(self.undo_list))
        if self.undo_index < -1:
            self.undo_index += 1
            config = self.undo_list[self.undo_index]
            self.world.config = config["world"]
            self.function.config = config["function"]
            self.colorwheel.config = config["color"]
    # >>>3
# >>>2
# >>>1


###
# main
def main():     # <<<1
    def display_help():
        print("""Usage: {} [flags]

    -o FILE  /  --output=FILE           choose output file
    -s W,H  /  --size=W,H               choose width and height of output
    -g X,Y,X,Y  /  --geometry=X,Y,X,Y   choose "geometry of output"
    --modulus  /  --angle               transformation of the result

    -c FILE  /  --color=FILE            choose color file
    --color-geometry=X,Y,X,Y            choose "geometry" of the color file
    --color-modulus  /  --color-angle   transformation of the colorwheel

    --matrix=...                        transformation matrix
    --rotation-symmetry=P               p-fold symmetry around the origin

    --wallpaper=...                     name of wallpaper group
    --sphere=...                        name of sphere group
    --frieze=...                        name of frieze group
    --rosette=...                       name of frieze group
    --params=...                        additional parameters:
                                           basis for lattice (for wallpaper)
                                           nb of rotations for rosettes

    --color-config=...
    --world-config=...
    --function-config=...

    --preview                           compute the initial preview image

    -h  /  --help                       this message
""")

    # parsing the command line arguments
    short_options = "hc:o:s:g:v"
    long_options = [
            "help",
            "color=", "color-geometry=", "color-modulus=", "color-angle=",
            "output=", "size=", "geometry=", "modulus=", "angle=",
            "matrix=", "rotation-symmetry=",
            "preview",
            "wallpaper=", "sphere", "frieze=", "rosette=", "params=",
            "color-config=", "world-config=", "function-config="]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(-1)

    rotational_symmetry = 1
    tab = None
    pattern = None
    params = None
    color_config = {}
    world_config = {}
    function_config = {}
    make_preview = False
    for o, a in opts:
        if o in ["-h", "--help"]:
            display_help()
            sys.exit(0)
        elif o in ["-c", "--color"]:
            color_config["filename"] = a
        elif o in ["-o", "--output"]:
            world_config["filename_template"] = a
        elif o in ["-s", "--size"]:
            try:
                tmp = map(int, a.split(","))
                width, height = tmp
                world_config["size"] = (width, height)
            except:
                error("problem with size '{}'".format(a))
                sys.exit(1)
        elif o in ["-g", "--geometry"]:
            try:
                tmp = map(float, a.split(","))
                x_min, x_max, y_min, y_max = tmp
                world_config["geometry"] = x_min, x_max, y_min, y_max
            except:
                error("problem with geometry '{}' for output".format(a))
                sys.exit(1)
        elif o in ["--rotation-symmetry"]:
            try:
                rotational_symmetry = int(a)
            except:
                error("problem with rotational symmetry '{}'".format(a))
        elif o in ["--modulus"]:
            try:
                world_config["modulu"] = float(a)
            except:
                error("problem with modulus '{}'".format(a))
                sys.exit(1)
        elif o in ["--angle"]:
            try:
                angle = float(a)
                world_config["angle"] = float(a)
            except:
                error("problem with angle '{}'".format(a))
                sys.exit(1)
        elif o in ["--color-geometry"]:
            try:
                tmp = map(float, a.split(","))
                color_x_min, color_x_max, color_y_min, color_y_max = tmp
                color_config["geometry"] = x_min, x_max, y_min, y_max
            except:
                error("problem with geometry '{}' for color image".format(a))
                sys.exit(1)
        elif o in ["--color-modulus"]:
            try:
                color_config["modulu"] = float(a)
            except:
                error("problem with modulus '{}'".format(a))
                sys.exit(1)
        elif o in ["--color-angle"]:
            try:
                color_config["angle"] = float(a)
            except:
                error("problem with angle '{}'".format(a))
                sys.exit(1)
        elif o in ["--wallpaper"]:
            function_config["current_tab"] = "wallpaper"
            function_config["wallpaper_pattern"] = a
        elif o in ["--sphere"]:
            function_config["current_tab"] = "sphere"
            function_config["sphere_pattern"] = a
        elif o in ["--frieze"]:
            function_config["current_tab"] = "sphere"
            function_config["sphere_pattern"] = a
            function_config["sphere_mode"] = "frieze"
        elif o in ["--rosette"]:
            function_config["current_tab"] = "sphere"
            function_config["sphere_pattern"] = a
            function_config["sphere_mode"] = "rosette"
        elif o in ["--params"]:
            params = a
        elif o == "--preview":
            make_preview = True
        elif o in ["--matrix"]:
            function_config["matrix"] = parse_matrix(a)
        elif o == "--color-config":
            cfg = json.loads(a)
            for k in cfg:
                color_config[k] = cfg[k]
        elif o == "--world-config":
            cfg = json.loads(a)
            for k in cfg:
                world_config[k] = cfg[k]
        elif o == "--function-config":
            cfg = json.loads(a)
            if "matrix" in cfg:
                cfg["matrix"] = list_to_matrix(cfg["matrix"])
            for k in cfg:
                function_config[k] = cfg[k]
        else:
            assert False

    # the "identity" function with waves, with period (1,0) / (0,1)
    # t = 10
    # M = {}
    # for n in range(1, t+1):
    #     M[(n, 0)] = (-1)**(n+1) * -1j/abs(n*pi)
    #     M[(-n, 0)] = (-1)**(n+1) * 1j/abs(n*pi)
    # for n in range(1, t+1):
    #     M[(0, n)] = (-1)**(n+1) * 1/abs(n*pi)
    #     M[(0, -n)] = (-1)**(n+1) * -1/abs(n*pi)

    # function_config["matrix"] = M
    # color_config["modulus"] = 1.5

    # color_config["filename"] = "Images/flame-sym.jpg"
    # color_config["alt_filename"] = "Images/flame-sym-gray.jpg"
    # color_config["modulus"] = .5

    # function_config["wallpaper_pattern"] = '2222'
    # function_config["wallpaper_color_pattern"] = '22×'
    # function_config["random_nb_coeffs"] = 10

    # world_config["draw_orbifold"] = True
    # world_config["draw_tile"] = True
    # world_config["draw_mirrors"] = True
    # world_config["draw_color_tile"] = False
    # world_config["preview_fade"] = False
    # world_config["modulus"] = 1.5
    # function_config["lattice_parameters"] = [2,1,1,-1]

    # function_config["current_tab"] = "hyperbolic"
    # world_config["geometry"] = (0,1/2, 0, 1/2)
    # function_config["sphere_pattern"] = "532"

    gui = CreateSymmetry()
    gui.colorwheel.config = color_config
    gui.world.config = world_config
    gui.function.config = function_config
    if make_preview:
        gui.make_preview()
    gui.mainloop()
# >>>1


if __name__ == "__main__":
    main()

# vim: textwidth=0 foldmarker=<<<,>>> foldmethod=marker foldlevel=0
