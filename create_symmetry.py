#!/usr/bin/env python3

###
# imports
# <<<1

# image manipulation (Pillow)
import PIL
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
import multiprocessing
import threading
import queue
# >>>1

PREVIEW_SIZE = 450
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
        },
    '2222': {
        "alt_name": "p2",
        "recipe": "n,m = -n, -m",
        "parity": "",
        "type": "plane group",
        "description": "general lattice",
        },
    '*×': {
        "alt_name": "cm",
        "recipe": "n,m = m,n",
        "parity": "",
        "type": "plane group",
        "description": "rhombic lattice",
        },
    '2*22': {
        "alt_name": "cmm",
        "recipe": "n,m = m,n = -n,-m = -m,-n",
        "parity": "",
        "type": "plane group",
        "description": "rhombic lattice",
        },
    '**': {
        "alt_name": "pm",
        "recipe": "n,m = n,-m",
        "parity": "",
        "type": "plane group",
        "description": "rectangular lattice",
        },
    '××': {
        "alt_name": "pg",
        "recipe": "n,m = -{n}(n,-m)",
        "parity": "",
        "type": "plane group",
        "description": "rectangular lattice",
        },
    '*2222': {
        "alt_name": "pmm",
        "recipe": "n,m = -n,-m = -n,m = n,-m",
        "parity": "",
        "type": "plane group",
        "description": "rectangular lattice",
        },
    '22*': {
        "alt_name": "pmg",
        "recipe": "n,m = -n,-m = -{n}(n,-m) = -{n}(-n,m)",
        "parity": "",
        "type": "plane group",
        "description": "rectangular lattice",
        },
    '22×': {
        "alt_name": "pgg",
        "recipe": "n,m = -n,-m = -{n+m}(n,-m) = -{n+m}(-n,m)",
        "parity": "",
        "type": "plane group",
        "description": "rectangular lattice",
        },
    '442': {
        "alt_name": "p4",
        "recipe": "n,m = m,-n = -n,-m = -m,n",
        "parity": "",
        "type": "plane group",
        "description": "square lattice",
        },
    '*442': {
        "alt_name": "p4m",
        "recipe": "n,m = m,-n = -n,-m = -m,n ; n,m = m,n",
        "parity": "",
        "type": "plane group",
        "description": "square lattice",
        },
    '4*2': {
        "alt_name": "p4g",
        "recipe": "n,m = m,-n = -n,-m = -m,n ; n,m = -{n+m}(m,n)",
        "parity": "",
        "type": "plane group",
        "description": "square lattice",
        },
    '333': {
        "alt_name": "p3",
        "recipe": "n,m = m,-n-m = -n-m,n",
        "parity": "",
        "type": "plane group",
        "description": "hexagonal lattice",
        },
    '3*3': {
        "alt_name": "p31m",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = m,n",
        "parity": "",
        "type": "plane group",
        "description": "hexagonal lattice",
        },
    '*333': {
        "alt_name": "p3m1",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -m,-n",
        "parity": "",
        "type": "plane group",
        "description": "hexagonal lattice",
        },
    '632': {
        "alt_name": "p6",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -n,-m",
        "parity": "",
        "type": "plane group",
        "description": "hexagonal lattice",
        },
    '*632': {
        "alt_name": "p6m",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = m,n = -n,-m = -m,-n",
        "parity": "",
        "type": "plane group",
        "description": "hexagonal lattice",
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
        "alt_name": "CN",
        "recipe": "",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "cyclic symmetry",
        },
    '22N': {
        "alt_name": "DN",
        "recipe": "n,m = -n,-m",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "dihedral symmetry",
        },
    '*NN': {
        "alt_name": "CNv",
        "recipe": "n,m = m,n",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "cyclic symmetry",
        },
    'N*': {
        "alt_name": "CNh",
        "recipe": "n,m = -m,-n",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "cyclic symmetry",
        },
    '*22N': {
        "alt_name": "DNh",
        "recipe": "n,m = m,n = -n,-m = -m,-n",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "cyclic symmetry",
        },
    'N×': {
        "alt_name": "S2N",
        "recipe": "n,m = -{n+m}(-m,-n)",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "cyclic symmetry",
        },
    '2*N': {
        "alt_name": "DNd",
        "recipe": "n,m = -n,-m = -{n+m}(-m,-n) = -{n+m}(m,n)",
        "parity": "n-m = 0 mod N",
        "type": "sphere group",
        "description": "dihedral symmetry",
        },
    '∞∞': {
        "alt_name": "p111",
        "recipe": "",
        "parity": "",
        "type": "frieze",
        "description": "",
        },
    '22∞': {
        "alt_name": "p211",
        "recipe": "n,m = -n,-m",
        "parity": "",
        "type": "frieze",
        "description": "",
        },
    '*∞∞': {
        "alt_name": "p1m1",
        "recipe": "n,m = m,n",
        "parity": "",
        "type": "frieze",
        "description": "",
        },
    '∞*': {
        "alt_name": "p11m",
        "recipe": "n,m = -m,-n",
        "parity": "",
        "type": "frieze",
        "description": "",
        },
    '*22∞': {
        "alt_name": "p2mm",
        "recipe": "n,m = m,n = -n,-m = -m,-n",
        "parity": "",
        "type": "frieze",
        "description": "",
        },
    '∞×': {
        "alt_name": "p11g",
        "recipe": "n,m = -{n+m}(-m,-n)",
        "parity": "",
        "type": "frieze",
        "description": "",
        },
    '2*∞': {
        "alt_name": "p2mg",
        "recipe": "n,m = -n,-m = -{n+m}(-m,-n) = -{n+m}(m,n)",
        "parity": "",
        "type": "frieze",
        "description": "",
        },
    ('o', 'o'): {
        "alt_name": "",
        "recipe": "",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('2222', 'o'): {
        "alt_name": "",
        "recipe": "n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('2222', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -n,-m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*×', 'o'): {
        "alt_name": "",
        "recipe": "n,m = -(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*×', '**'): {
        "alt_name": "",
        "recipe": "n,m = -n,m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*×', '××'): {
        "alt_name": "",
        "recipe": "n,m = -{m}(-n,m)",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('2*22', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -(m,n) ; n,m = -n,-m",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('2*22', '*×'): {
        "alt_name": "",
        "recipe": "n,m = -(m,n) ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('2*22', '*2222'): {
        "alt_name": "",
        "recipe": "n,m = -n,m ; n,m j -n,-m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('2*22', '22*'): {
        "alt_name": "",
        "recipe": "n,m = -{m}(-n,m) ; n,m = -n,-m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('2*22', '22×'): {
        "alt_name": "",
        "recipe": "n,m = -{n+m}(-n,m) ; n,m = -n,-m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('**', 'o'): {
        "alt_name": "",
        "recipe": "n,m = -(-n,m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('**', '*×'): {
        "alt_name": "",
        "recipe": "n,m = m,n",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('**', '**'): {
        "alt_name": "",
        "recipe": "n,m = -n,m",
        "parity": "m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('**', '××'): {
        "alt_name": "",
        "recipe": "n,m = -{m}(-n,m)",
        "parity": "m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('××', 'o'): {
        "alt_name": "",
        "recipe": "n,m = -{m+1}(-n,m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('××', '××'): {
        "alt_name": "",
        "recipe": "n,m = -{m}(-n,m)",
        "parity": "n = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*2222', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -(-n,m) ; n,m = -n,-m",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*2222', '2*22'): {
        "alt_name": "",
        "recipe": "n,m = m,n ; n,m = -n,-m",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*2222', '**'): {
        "alt_name": "",
        "recipe": "n,m = -n,m ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*2222', '*2222'): {
        "alt_name": "",
        "recipe": "n,m = -n,m ; n,m = -n,-m",
        "parity": "n = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*2222', '22*'): {
        "alt_name": "",
        "recipe": "n,m = -{m}(-n,m) ; n,m = -n,-m",
        "parity": "m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('22*', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -{m+1}(m,n) ; n,m = -n,-m",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('22*', '**'): {
        "alt_name": "",
        "recipe": "n,m = -{m+1}(-n,m) ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('22*', '××'): {
        "alt_name": "",
        "recipe": "n,m = -{m}(-n,m) ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('22*', '22*'): {
        "alt_name": "",
        "recipe": "n,m = -{m}(-n,m) ; n,m = -n,-m",
        "parity": "n = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('22*', '22×'): {
        "alt_name": "",
        "recipe": "n,m = -{n+m}(-n,m) ; n,m = -n,-m",
        "parity": "n = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('22×', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -{1+n+m}(m,n) ; n,m = -n,-m",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('22×', '××'): {
        "alt_name": "",
        "recipe": "n,m = -{n+m}(-n,m) ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('442', '2222'): {
        "alt_name": "",
        "recipe": "n,m = -(-m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('442', '442'): {
        "alt_name": "",
        "recipe": "n,m = -m,n",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*442', '2*22'): {
        "alt_name": "",
        "recipe": "n,m = -(-m,n) ; n,m = m,n",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*442', '*2222'): {
        "alt_name": "",
        "recipe": "n,m = -(-m,n) ; n,m = -(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*442', '442'): {
        "alt_name": "",
        "recipe": "n,m = -m,n ; n,m = -(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*442', '*442'): {
        "alt_name": "",
        "recipe": "n,m = -m,n ; n,m = m,n",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*442', '4*2'): {
        "alt_name": "",
        "recipe": "n,m = -m,n ; n,m = -{n+m}(m,n)",
        "parity": "n+m = 1 mod 2",
        "type": "color reversing plane group",
        "description": "",
        },
    ('4*2', '2*22'): {
        "alt_name": "",
        "recipe": "n,m = -(-m,n) ; n,m = -{n+m}(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('4*2', '22×'): {
        "alt_name": "",
        "recipe": "n,m = -(-m,n) ; n,m = -{1+n+m}(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('4*2', '442'): {
        "alt_name": "",
        "recipe": "n,m = -m,n ; n,m = -{n+m+1}(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('3*3', '333'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*333', '333'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -(-m,-n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('632', '333'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*632', '3*3'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = m,n ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*632', '*333'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -m,-n ; n,m = -(-n,-m)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    ('*632', '632'): {
        "alt_name": "",
        "recipe": "n,m = m,-n-m = -n-m,n ; n,m = -n,-m ; n,m = -(m,n)",
        "parity": "",
        "type": "color reversing plane group",
        "description": "",
        },
    }
# >>>1

NAMES = [    # <<<1
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
        "432",
        "532",
        "3*2",
        "*332",
        "*432",
        "*532",
        "NN",
        "22N",
        "*NN",
        "N*",
        "*22N",
        "N×",
        "2*N",
        # friezes
        "∞∞",
        "22∞",
        "*∞∞",
        "∞*",
        "*22∞",
        "∞×",
        "2*∞",
        ]
# >>>1

W_NAMES = ["{} ({})".format(p, PATTERN[p]["alt_name"])
           for p in NAMES
           if PATTERN[p]["type"] == "plane group"]

S_NAMES = ["{} ({})".format(p, PATTERN[p]["alt_name"])
           for p in NAMES
           if PATTERN[p]["type"] == "sphere group"]

F_NAMES = ["{} ({})".format(p, PATTERN[p]["alt_name"])
           for p in NAMES
           if PATTERN[p]["type"] == "frieze"]


def C_NAMES(s):
    r = []
    for p in NAMES:
        if (p, s) in PATTERN:
            r.append("{} ({})".format(p, PATTERN[p]["alt_name"]))
    return r
###
# utility functions
# <<<1
class Error(Exception):     # <<<2
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
    def res(*args):
        for f in fs:
            f()
    return res
# >>>2


def invert22(M):        # <<<2
    d = M[0][0] * M[1][1] - M[1][0] * M[0][1]
    I = [[M[1][1]/d, -M[0][1]/d],
         [-M[1][0]/d, M[0][0]/d]]
    return I
# >>>2


def mult_M(M1, M2):     # <<<2
    assert len(M1[0]) == len(M2)
    R = [[0]*len(M2[0]) for i in range(len(M1))]
    for i in range(len(M1)):
        for j in range(len(M2[0])):
            for k in range(len(M2)):
                R[i][j] += M1[i][k] * M2[k][j]
    return R
# >>>2


def rotation_matrix(x, y, z):       # <<<2
    # see https://en.wikipedia.org/wiki/Euler_angles#Rotation_matrix
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
    # see http://stackoverflow.com/questions/18433801/converting-a-3x3-matrix-to-euler-tait-bryan-angles-pitch-yaw-roll
    theta_z = atan2(R[2][1], R[2][2])
    theta_y = -asin(R[2][0])
    theta_x = atan2(R[1][0], R[0][0])
    return theta_x, theta_y, theta_z
# >>>2


def str_to_floats(s):       # <<<2
    if s.strip() == "":
        return []
    else:
        return list(map(float, s.split(",")))
# >>>2


def float_to_str(x):       # <<<2
    return re.sub("\.0*\s*$", "", str(x))
# >>>2


def floats_to_str(l):       # <<<2
    return ", ".join(map(float_to_str, l))
# >>>2


def complex_to_str(z, precision=4):    # <<<2
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
    return [((n, m), (z.real, z.imag)) for (n, m), z in M.items()]
# >>>2


def list_to_matrix(L):      # <<<2
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


def eqn_indices(eq, n, m):        # <<<2
    """return a list of (s, (j, k))"""
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
    """BFS like algorithm to compute all the related indices to n and m"""
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
    parity = parity.strip()
    if parity == "":
        return M

    print("parity:", parity)
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
    """return a matrix computed from ``M`` by adding symmetries given by ``recipe``
``recipe`` can be of the form "n,m = -n,-m = -(m,n) ; n,m = -{n+m}(n,m)"...
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


def basis(pattern, *params):
    lattice = PATTERN[pattern]["description"].split()[0]
    if lattice == "general":
        return [[1, 0], [params[0], params[1]]]
    elif lattice == "rhombic":
        return [[1/2, params[0]/2], [1/2, -params[0]/2]]
    elif lattice == "rectangular":
        return [[1, 0], [0, 1/params[0]]]
    elif lattice == "square":
        return [[1, 0], [0, 1]]
    elif lattice == "hexagonal":
        return [[1, 0], [-1/2, sqrt(3)/2]]
    else:
        assert False
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


def apply_color(        # <<<2
        res,
        filename=None,                  # image for the colorwheel image
        geometry=COLOR_GEOMETRY,          # coordinates of the colorwheel
        modulus="1",
        angle="0",
        color="black"):

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
    color_im.paste(tmp, (1, 1))

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


def make_rosette_image(zs,                # <<<2
                       matrix,
                       pattern,
                       N=5,
                       unwind=False,
                       message_queue=None):

    matrix = add_symmetries(matrix,
                            PATTERN[pattern]["recipe"],
                            parity="n-m = 0 mod {}".format(N))

    if unwind:
        np.multiply(1j, zs, out=zs)
        np.exp(zs, out=zs)
    zsc = np.conj(zs)

    res = np.zeros(zs.shape, complex)
    w1, w2 = 1, len(matrix)
    for (n, m) in matrix:
        np.add(res,  matrix[(n, m)] * zs**n * zsc**m, out=res)
        if message_queue is not None:
            message_queue.put(w1/w2)
        w1 += 1
    return res
# >>>2


def make_wallpaper_image(zs,     # <<<2
                         matrix,
                         pattern,
                         lattice_params=None,      # additional parameters
                         color_pattern="",
                         message_queue=None):

    if color_pattern:
        cp = PATTERN[color_pattern, pattern]
        matrix = add_symmetries(matrix, cp["recipe"], cp["parity"])
    else:
        matrix = add_symmetries(matrix, PATTERN[pattern]["recipe"])

    lattice_basis = basis(pattern, *lattice_params)
    C = invert22(lattice_basis)

    res = np.zeros(zs.shape, complex)

    w1, w2 = 1, len(matrix)
    for (n, m) in matrix:
        xs = zs.real
        ys = zs.imag
        np.add(res,
               matrix[(n, m)] * np.exp(2j*pi*(n*(C[0][0]*xs+C[1][0]*ys) +
                                              m*(C[0][1]*xs+C[1][1]*ys))),
               out=res)
        if message_queue is not None:
            message_queue.put(w1/w2)
        w1 += 1
    return res
# >>>2


def plane_coordinates_to_sphere(zs, rotations=(0, 0, 0)):       # <<<2
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


def make_sphere_image(zs,      # <<<2
                      matrix,
                      pattern,
                      N=5,
                      message_queue=None):

    recipe = PATTERN[pattern]["recipe"]
    parity = PATTERN[pattern]["parity"].replace("N", str(N))
    matrix = add_symmetries(matrix, recipe, parity)

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


def make_sphere_background(zs, img, background="back.jpg", shade=128, stars=0):
    width, height = zs.shape
    mask = (zs.real**2 + zs.imag**2 > 1).astype(int).transpose(1, 0)
    mask = (255-shade) * mask
    mask = PIL.Image.fromarray(np.array(mask, dtype=np.uint8), "L")
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
                background_img.putpixel((randrange(0, width), randrange(0, height)), getrgb(STAR_COLOR))
            seed()
        except ValueError:
            background_img = PIL.Image.new(mode="RGB",
                                           size=(width, height),
                                           color=DEFAULT_SPHERE_BACKGROUND)
    img.paste(background_img, None, mask)
    return img
# >>>2


def make_lattice_image(zs,          # <<<2
                       matrix,
                       basis=None,
                       N=1,
                       message_queue=None):
    if basis is None:
        basis = [[1, 0], [0, 1]]

    B = invert22(basis)

    res = np.zeros(zs.shape, dtype=complex)
    w1, w2 = 1, len(matrix)
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
        np.divide(ZS, N, out=ZS)
        np.multiply(ZS, matrix[(n, m)], out=ZS)
        np.add(res, ZS, out=res)

        if message_queue is not None:
            message_queue.put(w1/w2)
        w1 += 1
    return res
# >>>2


def make_image(color=None,     # <<<2
               world=None,
               pattern="",
               matrix=None,
               message_queue=None,
               stretch_color=False,
               **params):

    zs = make_coordinates_array(world["size"],
                                world["geometry"],
                                world["modulus"],
                                world["angle"])
    _zs = zs

    if not world["sphere_projection"]:
        _zs = np.copy(zs)
        zs = plane_coordinates_to_sphere(zs, world["sphere_rotations"])


    if PATTERN[pattern]["type"] == "frieze":
        res = make_rosette_image(zs,
                                 matrix,
                                 pattern,
                                 N=params["N"],
                                 unwind=not params["rosette"],
                                 message_queue=message_queue)
    elif PATTERN[pattern]["type"] == "plane group":
        res = make_wallpaper_image(zs,
                                   matrix,
                                   pattern,
                                   lattice_params=params["lattice_params"],
                                   color_pattern=params["color_pattern"],
                                   message_queue=message_queue)
    elif PATTERN[pattern]["type"] == "sphere group":
        res = make_sphere_image(zs,
                                matrix,
                                pattern,
                                N=params["N"],
                                message_queue=message_queue)
    else:
        res = make_lattice_image(zs,
                                 matrix,
                                 basis=params["basis"],
                                 N=params["N"],
                                 message_queue=message_queue)

    if stretch_color:
        np.divide(res, np.sqrt(1 + res.real**2 * res.imag**2), out=res)

    img = apply_color(res,
                      color["filename"],
                      color["geometry"],
                      color["modulus"],
                      color["angle"],
                      color["color"])

    if world["sphere_background"] and not world["sphere_projection"]:
        return make_sphere_background(_zs,
                                      img,
                                      background=world["sphere_background"],
                                      shade=world["sphere_shading"],
                                      stars=world["sphere_stars"])
    else:
        return img
# >>>2


def background_output(     # <<<2
        message_queue=None,
        output_message_queue=None, **config):

    filename_template = config["world"]["filename"]

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
                       stretch_color=color["stretch"],
                       **params)

    function = config["function"]
    info = {"type": "", "name": "", "alt_name": ""}
    if function["tab"] == "wallpaper":
        info["type"] = "planar"
        info["name"] = function["wallpaper_pattern"]
        info["alt_name"] = PATTERN[info["name"]]["alt_name"]
        cp = function["wallpaper_color_pattern"]
        if cp != "--":
            info["name"] = cp + "_" + info["name"]
            info["alt_name"] = (PATTERN[cp]["alt_name"] +
                                "_" +
                                info["alt_name"])
    elif function["tab"] == "sphere":
        info["type"] = "spherical"
        p = function["sphere_pattern"]
        N = function["sphere_N"]
        info["name"] = p.replace("N", str(N))
        info["alt_name"] = PATTERN[p]["alt_name"]
        info["alt_name"] = info["alt_name"].replace("N", str(N))
    elif function["tab"] == "frieze":
        if function["rosette"]:
            info["type"] = "rosette"
            N = function["rosette_N"]
            info["type"] += "_{}fold_symmetry".format(N)
        else:
            info["type"] = "frieze"
            p = function["frieze_pattern"]
            info["name"] = p
            info["alt_name"] = PATTERN[p]["alt_name"]
    elif function["tab"] == "raw":
        info["type"] = "lattice"
        N = function["raw_N"]
        if N != 1:
            info["type"] += "_{}fold_symmetry".format(N)
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
    def color(self):    # <<<4
        return self._color.get()
    # >>>4

    @color.setter
    def color(self, color):    # <<<4
        self._color.set("#{:02x}{:02x}{:02x}"
                        .format(color[0], color[1], color[2]))
    # >>>4

    @property
    def color_string(self):    # <<<4
        return self._color.entry_widget.get()
    # >>>4

    @color_string.setter
    def color_string(self, color):    # <<<4
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
        except:
            return None
    # >>>4

    @filename.setter
    def filename(self, filename):   # <<<4
        self._filename = filename
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
                    command=lambda: self.change_colorwheel(self.filename)
                    ).grid(row=1, column=0, padx=5, pady=0)

        self._canvas = Canvas(self, width=200, height=200, bg="white")
        self._canvas.grid(row=3, column=0, padx=5, pady=5)
        for i in range(5, COLOR_SIZE, 10):
            for j in range(5, COLOR_SIZE, 10):
                self._canvas.create_line(i-1, j, i+2, j, fill="gray")
                self._canvas.create_line(i, j-1, i, j+2, fill="gray")
        self._colorwheel_id = None
        self._canvas.bind("<Button-3>", self.set_origin)
        self._canvas.bind("<Double-Button-1>", self.choose_colorwheel)

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

        self._reset_button = Button(coord_frame, text="reset",
                                    command=self.reset_geometry)
        self._reset_button.grid(row=2, column=0, columnspan=2,
                                padx=5, pady=5)

        transformation_frame = LabelFrame(self, text="transformation")
        transformation_frame.grid(row=6, column=0, sticky=E+W, padx=5, pady=5)
        self._modulus = LabelEntry(transformation_frame, label="modulus",
                                   value=1,
                                   convert=float,
                                   width=4)
        self._modulus.pack(padx=5, pady=5)

        self._angle = LabelEntry(transformation_frame, label="angle (°)",
                                 value=0,
                                 convert=float,
                                 width=4)
        self._angle.pack(padx=5, pady=5)

        self.update_defaultcolor()

        if os.path.exists("./colorwheel.jpg"):
            self.change_colorwheel("colorwheel.jpg")
        else:
            self.filename = None
    # >>>3

    def update_defaultcolor(self, *args):     # <<<3
        if self._color.validate():
            self._canvas.config(bg="#{:02x}{:02x}{:02x}".format(*self.color))
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
                        geometry=(-7, 7, -7, 7))
                np.divide(zs, np.sqrt(1 + zs.real**2 + zs.imag**2), out=zs)
                img = apply_color(zs,
                                  filename,
                                  self.geometry,
                                  self.modulus,
                                  self.angle,
                                  self.color)
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
        except Exception as e:
            error("problem while loading {} for color image: {}"
                  .format(filename, e))
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
    # >>>3

    def reset_geometry(self, *args):        # <<<3
        if self.stretch:
            return
        if self.filename is not None:
            self.change_colorwheel(self.filename)
        else:
            self.geometry = COLOR_GEOMETRY
    # >>>3

    def get_config(self):           # <<<3
        return {
                "filename": self.filename,
                "color": self.color_string,
                "geometry": self.geometry,
                "modulus": self.modulus,
                "angle": self.angle,
                "stretch": self.stretch,
                }
    # >>>3

    def set_config(self, cfg):      # <<<3
        if "geometry" in cfg:
            self.geometry = cfg["geometry"]
        if "modulus" in cfg:
            self.modulus = cfg["modulus"]
        if "angle" in cfg:
            self.angle = cfg["angle"]
        if "stretch" in cfg:
            self.stretch = cfg["stretch"]
        if "color" in cfg:
            self.color_string = cfg["color"]
            self.update_defaultcolor()
        if "filename" in cfg:
            self.change_colorwheel(cfg["filename"])
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
    def stereographic(self):    # <<<4
        return self._stereographic.get()
    # >>>4

    @stereographic.setter
    def stereographic(self, b):    # <<<4
        self._stereographic.set(b)
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
        try:
            return self._sphere_background_str
        except:
            return ""
    # >>>4

    @sphere_background.setter
    def sphere_background(self, s):    # <<<4
        if os.path.exists(s):
            self._sphere_background_str = s
            self._sphere_background.set(os.path.basename(s))
        else:
            self._sphere_background_str = s
            self._sphere_background.set(s)
    # >>>4

    @property
    def sphere_shading(self):    # <<<4
        return self._sphere_shading.get()
    # >>>4

    @sphere_shading.setter
    def sphere_shading(self, n):    # <<<4
        self._sphere_shading.set(n)
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
    # >>>3

    def __init__(self, root):       # <<<3

        self.root = root

        LabelFrame.__init__(self, root)
        self.configure(text="World")

        # the preview image     <<<4
        self._canvas = Canvas(self, width=PREVIEW_SIZE, height=PREVIEW_SIZE,
                              bg="white")
        for i in range(5, PREVIEW_SIZE, 10):
            for j in range(5, PREVIEW_SIZE, 10):
                self._canvas.create_line(i-1, j, i+2, j, fill="gray")
                self._canvas.create_line(i, j-1, i, j+2, fill="gray")
        self._canvas.grid(row=0, column=0, rowspan=4, padx=5, pady=5)
        self._image_id = None
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

        Button(coord_frame, text="zoom -",
               command=self.zoom(2**.1)).grid(row=3, column=0,
                                              padx=5, pady=5)
        Button(coord_frame, text="zoom +",
               command=self.zoom(2**-.1)).grid(row=3, column=1,
                                               padx=5, pady=5)

        transformation_frame = LabelFrame(self._geometry_plane_tab,
                                          text="transformation")
        transformation_frame.pack(padx=5, pady=5, fill=BOTH)
        self._modulus = LabelEntry(transformation_frame, label="modulus",
                                   value=1,
                                   convert=float,
                                   width=4)
        self._modulus.pack(padx=5, pady=5)

        self._angle = LabelEntry(transformation_frame, label="angle (°)",
                                 value=0,
                                 convert=float,
                                 width=4)
        self._angle.pack(padx=5, pady=5)

        Button(coord_frame, text="reset",
               command=self.reset_geometry).grid(row=4, column=0, columnspan=2,
                                                 padx=5, pady=5)
        # >>>4

        # sphere parameters     <<<4
        self._geometry_sphere_tab = Frame(self._geometry_tabs)
        self._geometry_tabs.add(self._geometry_sphere_tab, text="sphere")
        self._stereographic = BooleanVar()
        self._stereographic.set(True)

        stereographic_button = Checkbutton(self._geometry_sphere_tab,
                                           text="stereographic projection",
                                           variable=self._stereographic,
                                           onvalue=True, offvalue=False,
                                           )
        stereographic_button.pack(padx=5, pady=10)

        self._rotations = LabelEntry(self._geometry_sphere_tab,
                                     label="rotations x, y, z (°)",
                                     orientation="V",
                                     value="15, 15, 0",
                                     convert=str_to_floats,
                                     width=15)
        self._rotations.pack(padx=5, pady=10)

        self._sphere_background = LabelEntry(self._geometry_sphere_tab,
                                             label="background",
                                             value=DEFAULT_SPHERE_BACKGROUND,
                                             width=10)
        self.sphere_background = DEFAULT_SPHERE_BACKGROUND
        self._sphere_background.pack(padx=5, pady=10)
        self._sphere_background.bind("<Double-Button-1>",
                                     self.choose_sphere_background)

        self._sphere_shading = LabelEntry(self._geometry_sphere_tab,
                                          label="shading",
                                          value=128,
                                          width=5,
                                          convert=int)
        self._sphere_shading.pack(padx=5, pady=10)

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

        self._filename_template = LabelEntry(settings_frame, label="filename template",
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
        self._preview_button.pack(side=LEFT, padx=10, pady=10)

        self._save_button = Button(tmp, text="save", command=None)
        self._save_button.pack(side=RIGHT, padx=10, pady=10)
        # >>>4

        self.adjust_geometry()
    # >>>3

    def reset_geometry(self, *args):        # <<<3
        self.geometry = WORLD_GEOMETRY
        self.adjust_geometry()
        self.rotations = 0, 0, 0
    # >>>3

    def zoom(self, alpha):      # <<<3
        def zoom_tmp(*args):
            self.geometry = map(lambda x: x*alpha, self.geometry)
        return zoom_tmp
    # >>>3

    def translate(self, dx, dy):    # <<<3
        x_min, x_max, y_min, y_max = self.geometry
        delta_x = x_max - x_min
        delta_y = y_max - y_min
        self.geometry = x_min + dx*delta_x, x_max + dx*delta_x, y_min + dy*delta_y, y_max + dy*delta_y
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

    def adjust_geometry(self, *args):       # <<<3
        ratio = self.width / self.height
        x_min, x_max, y_min, y_max = self.geometry
        if ratio > 1:
            delta_y = y_max - y_min
            delta_x = delta_y * ratio
            middle_x = (x_min+x_max) / 2
            self.geometry = middle_x - delta_x/2, middle_x + delta_x/2, y_min, y_max
        else:
            delta_x = x_max - x_min
            delta_y = delta_x / ratio
            middle_y = (y_min+y_max) / 2
            self.geometry = x_min, x_max, middle_y - delta_y/2, middle_y + delta_y/2
    # >>>3

    def get_config(self):           # <<<3
        return {
                "geometry": self.geometry,
                "modulus": self.modulus,
                "angle": self.angle,
                "sphere_projection": self.stereographic,
                "sphere_rotations": self.sphere_rotations,
                "sphere_background": self.sphere_background,
                "sphere_shading": self.sphere_shading,
                "sphere_stars": self.sphere_stars,
                "geometry_tab": self.geometry_tab,
                "size": self.size,
                "filename": self.filename_template,
                }
    # >>>3

    def set_config(self, cfg):      # <<<3
        if "geometry" in cfg:
            self.geometry = cfg["geometry"]
        if "modulus" in cfg:
            self.modulus = cfg["modulus"]
        if "angle" in cfg:
            self.angle = cfg["angle"]
        if "sphere_projection" in cfg:
            self.stereographic = cfg["sphere_projection"]
        if "sphere_rotations" in cfg:
            self.sphere_rotations = cfg["sphere_rotations"]
        if "sphere_background" in cfg:
            self.sphere_background = cfg["sphere_background"]
        if "sphere_shading" in cfg:
            self.sphere_shading = cfg["sphere_shading"]
        if "sphere_stars" in cfg:
            self.sphere_stars = cfg["sphere_stars"]
        if "size" in cfg:
            self.size = cfg["size"]
        if "filename" in cfg:
            self.filename_template = cfg["filename"]
        if "geometry_tab" in cfg:
            self.geometry_tab = cfg["geometry_tab"]
    # >>>3
# >>>2


class Function(LabelFrame):     # <<<2

    # setters and getters <<<3
    @property
    def current_tab(self):      # <<<4
        if ("wallpaper" in self._tabs.tab(self._tabs.select(), "text")):
            return "wallpaper"
        elif ("frieze" in self._tabs.tab(self._tabs.select(), "text")):
            return "frieze"
        elif ("raw" in self._tabs.tab(self._tabs.select(), "text")):
            return "raw"
        elif ("sphere" in self._tabs.tab(self._tabs.select(), "text")):
            return "sphere"
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
        elif tab == "frieze":
            self._tabs.select(self._frieze_tab)
        elif tab == "raw":
            self._tabs.select(self._raw_tab)
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
    def rosette(self):     # <<<4
        return self._rosette.get()
    # >>>4

    @rosette.setter
    def rosette(self, b):     # <<<4
        self._rosette.set(b)
    # >>>4

    @property
    def rosette_N(self):     # <<<4
        return self._rosette_N.get()
    # >>>4

    @rosette_N.setter
    def rosette_N(self, N):     # <<<4
        self._rosette_N.set(N)
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
    def raw_N(self):     # <<<4
        return self._raw_N.get()
    # >>>4

    @raw_N.setter
    def raw_N(self, N):     # <<<4
        self._raw_N.set(N)
    # >>>4

    @property
    def change_entry(self):     # <<<4
        return self._change_entry.get().strip()
    # >>>4

    @change_entry.setter
    def change_entry(self, s):     # <<<4
        self._change_entry.set(s)
    # >>>4

    # TODO: refactor
    @property
    def rotational_symmetry(self):      # <<<4
        if self.current_tab == "raw":
            return self._raw_N
        elif self.current_tab == "wallpaper":
            return 1
        elif self.current_tab == "frieze":
            if self.rosette:
                return self.rosette_N
            else:
                return 1
        elif self.current_tab == "sphere":
            return self.sphere_N
        else:
            assert False
    # >>>4

    @property
    def pattern(self):          # <<<4
        if self.current_tab == "frieze":
            return self._frieze_type.get().split()[0]
        elif self.current_tab == "wallpaper":
            return self._wallpaper_type.get().split()[0]
        elif self.current_tab == "sphere":
            return self._sphere_type.get().split()[0]
        elif self.current_tab == "raw":
            return ""
        else:
            return ""
    # >>>4

    @property
    def color_pattern(self):          # <<<4
        if self.current_tab == "wallpaper":
            sub = self._color_reversing_color_pattern.get()
            if sub == "--":
                return ""
            else:
                return sub.split()[0]
        else:
            return ""
    # >>>4

    @property
    def lattice_basis(self):       # <<<4
        if self.current_tab == "wallpaper":
            return basis(self.pattern, *self._lattice_params.get())
        elif self.current_tab == "raw":
            v1 = self._basis_matrix1.get()
            v2 = self._basis_matrix2.get()
            v1 = [v1[0], v1[1]]
            v2 = [v2[0], v2[1]]
            return [v1, v2]
        elif self.current_tab == "frieze":
            return None
        elif self.current_tab == "sphere":
            return None
        else:
            assert False
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

        self._frieze_tab = Frame(self._tabs)
        self._tabs.add(self._frieze_tab, text="frieze")

        self._raw_tab = Frame(self._tabs)
        self._tabs.add(self._raw_tab, text="raw")
        # >>>4

        # wallpaper tab      <<<4
        self._wallpaper_type = StringVar()

        Label(self._wallpaper_tab,
              text="symmetry group").pack(padx=5, pady=(20, 0))
        self._wallpaper_combo = Combobox(
                self._wallpaper_tab, width=20, exportselection=0,
                textvariable=self._wallpaper_type,
                state="readonly",
                values=W_NAMES
                )
        self._wallpaper_combo.pack(padx=5, pady=5)
        self._wallpaper_combo.current(0)

        self._lattice_params = LabelEntry(self._wallpaper_tab,
                                          label="lattice parameters",
                                          value="1,1",
                                          convert=str_to_floats,
                                          width=7)
        self._lattice_params.pack(padx=5, pady=5)

        self._wallpaper_combo.bind("<<ComboboxSelected>>",
                                   self.update)

        Label(self._wallpaper_tab,
              text="color symmetry group").pack(padx=5, pady=(20, 0))
        self._color_reversing_color_pattern = StringVar()
        self._color_reversing_combo = Combobox(
                self._wallpaper_tab, width=10, exportselection=0,
                textvariable=self._color_reversing_color_pattern,
                state="readonly",
                values=["--"]
                )
        self._color_reversing_combo.pack(padx=5, pady=5)
        self._color_reversing_combo.current(0)
        # # >>>4

        # frieze / rosette tab   <<<4
        Label(self._frieze_tab,
              text="frieze pattern").pack(padx=5, pady=(20, 0))
        self._frieze_type = StringVar()
        self._frieze_combo = Combobox(self._frieze_tab, width=15,
                                      exportselection=0,
                                      textvariable=self._frieze_type,
                                      state="readonly",
                                      values=F_NAMES)
        self._frieze_combo.pack(padx=5, pady=5)
        self._frieze_combo.current(0)

        self._rosette = BooleanVar()
        self.rosette = False

        rosette_button = Checkbutton(self._frieze_tab, text="rosette",
                                     variable=self._rosette,
                                     onvalue=True, offvalue=False,
                                     command=self.update)
        rosette_button.pack(padx=5, pady=5)

        self._rosette_N = LabelEntry(self._frieze_tab,
                                     label="symmetries",
                                     value=5,
                                     convert=int,
                                     width=2)
        self._rosette_N.pack(padx=5, pady=5)
        # # >>>4

        # raw tab   <<<4
        self._basis_matrix1 = LabelEntry(self._raw_tab,
                                         label="first vector",
                                         value="1, 0",
                                         convert=str_to_floats,
                                         width=10)
        self._basis_matrix2 = LabelEntry(self._raw_tab,
                                         label="second vector",
                                         value="0, 1",
                                         convert=str_to_floats,
                                         width=10)
        self._basis_matrix1.grid(row=0, column=0, sticky=E,
                                 padx=5, pady=(20, 0))
        self._basis_matrix2.grid(row=1, column=0, sticky=E,
                                 padx=5, pady=(0, 5))

        self._raw_N = LabelEntry(self._raw_tab,
                                        label="rotational symmetry",
                                        value=1,
                                        convert=int,
                                        width=3)
        self._raw_N.grid(row=2, column=0, padx=5, pady=20)
        # >>>4

        # sphere tab        <<<4
        Label(self._sphere_tab,
              text="symmetry group").pack(padx=5, pady=(20, 0))
        self._sphere_type = StringVar()
        self._sphere_combo = Combobox(self._sphere_tab, width=15,
                                      exportselection=0,
                                      textvariable=self._sphere_type,
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
        a = self.random_min_degre
        b = self.random_max_degre
        coeffs = list(product(range(a, b+1), range(a, b+1)))
        shuffle(coeffs)
        n = self.random_nb_coeffs
        coeffs = coeffs[:n]
        M = {}
        for (n, m) in coeffs:
            modulus = uniform(0, self.random_modulus) / self.random_nb_coeffs
            angle = uniform(0, 2*pi)
            M[(n, m)] = modulus * complex(cos(angle), sin(angle))
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
        if self.current_tab == "raw":
            return M

        pattern = self.pattern

        if self.current_tab == "frieze" and self.rosette:
            p = self.rotational_symmetry
            keys = list(M.keys())
            for (n, m) in keys:
                if (n-m) % p != 0 or n == m:
                    del M[(n, m)]
            M = add_symmetries(M, PATTERN[pattern]["recipe"])
        elif self.current_tab == "frieze":
            M = add_symmetries(M, PATTERN[pattern]["recipe"])
        elif self.current_tab == "wallpaper":
            M = add_symmetries(M, PATTERN[pattern]["recipe"])
            color_pattern = self.color_pattern
            if color_pattern:
                sub = PATTERN[color_pattern, pattern]
                parity = sub["parity"]
                M = add_symmetries(M, sub["recipe"], parity)
            else:
                M = add_symmetries(M, PATTERN[pattern]["recipe"])
        elif self.current_tab == "sphere":
            M = add_symmetries(M,
                               PATTERN[pattern]["recipe"],
                               PATTERN[pattern]["parity"]
                               .replace("N", str(self.sphere_N)))

        return M
    # >>>3

    def get_config(self):           # <<<3
        return {
                "matrix": self.matrix,
                #
                "random_nb_coeffs": self.random_nb_coeffs,
                "random_degre": (self.random_min_degre,
                                 self.random_max_degre),
                "random_modulus": self.random_modulus,
                "random_noise": self.random_noise,
                #
                "tab": self.current_tab,
                # wallpaper tab
                "wallpaper_pattern": self._wallpaper_type.get().split()[0],
                "lattice_parameters": self._lattice_params.get(),
                "wallpaper_color_pattern": self._color_reversing_color_pattern.get().split()[0],
                # frieze tab
                "frieze_pattern": self._frieze_type.get(),
                "rosette": self.rosette,
                "rosette_N": self.rosette_N,
                # raw tab
                "raw_basis": [self._basis_matrix1.get(),
                              self._basis_matrix2.get()],
                "raw_N": self.raw_N,
                # sphere tab
                "sphere_pattern": self._sphere_type.get().split()[0],
                "sphere_N": self.sphere_N,
                }
    # >>>3

    def set_config(self, cfg):      # <<<3
        if "matrix" in cfg:
            self.change_matrix(cfg["matrix"])
        if "random_nb_coeffs" in cfg:
            self.random_nb_coeffs = cfg["random_nb_coeffs"]
        if "random_degre" in cfg:
            self.random_min_degre = cfg["random_degre"][0]
            self.random_max_degre = cfg["random_degre"][1]
        if "random_modulus" in cfg:
            self.random_modulus = cfg["random_modulus"]
        if "random_noise" in cfg:
            self.random_noise = cfg["random_noise"]
        if "tab" in cfg:
            self.current_tab = cfg["tab"]
        if "wallpaper_pattern" in cfg:
            for i in range(len(W_NAMES)):
                tmp = W_NAMES[i]
                tmp = tmp.replace("(", " ").replace(")", " ")
                tmp = tmp.split()
                if cfg["wallpaper_pattern"] in tmp:
                    self._wallpaper_combo.current(i)
        if "wallpaper_color_pattern" in cfg:
            l = self._color_reversing_combo.cget("values")
            for i in range(len(l)):
                tmp = l[i].replace("(", "").replace(")", "")
                tmp = tmp.split()
                if cfg["wallpaper_color_pattern"] in tmp:
                    self._color_reversing_combo.current(i),
        if "lattice_parameters" in cfg:
            self._lattice_params.set(floats_to_str(cfg["lattice_parameters"]))
        if "frieze_pattern" in cfg:
            for i in range(len(F_NAMES)):
                tmp = F_NAMES[i]
                tmp = tmp.replace("(", " ").replace(")", " ")
                tmp = tmp.split()
                if cfg["frieze_pattern"] in tmp:
                    self._frieze_combo.current(i)
        if "rosette" in cfg:
            self.rosette = cfg["rosette"]
        if "rosette_N" in cfg:
            self.rosette_N = cfg["rosette_N"]
        if "raw_basis" in cfg:
            self._basis_matrix1.set(floats_to_str(cfg["raw_basis"][0]))
            self._basis_matrix2.set(floats_to_str(cfg["raw_basis"][1]))
        if "raw_N" in cfg:
            self.raw_N = cfg["raw_N"]
        if "sphere_pattern" in cfg:
            for i in range(len(S_NAMES)):
                tmp = S_NAMES[i]
                tmp = tmp.replace("(", " ").replace(")", " ")
                tmp = tmp.split()
                if cfg["sphere_pattern"] in tmp:
                    self._sphere_combo.current(i)
        if "sphere_N" in cfg:
            self.sphere_N = cfg["sphere_N"]
        self.update()
    # >>>3

    # refactor
    def set_frieze_type(self, *args):       # <<<3
        frieze_combo.select_clear()
        self.function["frieze_type"] = frieze_combo.stringvar.get()
    # >>>3

    def update(self, *args):     # <<<3
        # sphere tab  <<<4
        if "N" in self.pattern:
            self._sphere_N.enable()
        else:
            self._sphere_N.disable()
        # >>>4

        # rosette tab   <<<4
        if self.rosette:
            self._rosette_N.enable()
        else:
            self._rosette_N.disable()
        # >>>4

        # wallpaper tab     <<<4
        pattern = self._wallpaper_type.get().split()[0]
        lattice = PATTERN[pattern]["description"].split()[0]
        if lattice == "general":
            self._lattice_params.enable()
            self._lattice_params.label_widget.config(text="x, y")
            self._lattice_params.set("1, 1")
        elif lattice == "rhombic":
            self._lattice_params.enable()
            self._lattice_params.label_widget.config(text="b")
            self._lattice_params.set(".5")
        elif lattice == "rectangular":
            self._lattice_params.enable()
            self._lattice_params.set(".5")
            self._lattice_params.label_widget.config(text="H")
        elif lattice == "square":
            self._lattice_params.set("")
            self._lattice_params.label_widget.config(text="lattice parameters")
            self._lattice_params.disable()
        elif lattice == "hexagonal":
            self._lattice_params.set("")
            self._lattice_params.label_widget.config(text="lattice parameters")
            self._lattice_params.disable()
        elif lattice == "frieze":
            pass
        else:
            assert False

        # color reversing combo
        self._color_reversing_combo.configure(
                values=["--"] + C_NAMES(pattern)
                )
        self._color_reversing_combo.current(0)
        # >>>4
    # >>>3

    def get_pattern_params(self):       # <<<3
        if self.current_tab == "frieze":
            return {"N": self.rosette_N,
                    "rosette": self.rosette}
        elif self.current_tab == "wallpaper":
            return {"lattice_params": self._lattice_params.get(),
                    "color_pattern": self.color_pattern}
        elif self.current_tab == "sphere":
            return {"N": self.sphere_N}
        elif self.current_tab == "raw":
            return {"N": self.raw_N,
                    "basis": [self._basis_matrix1.get(),
                              self._basis_matrix2.get()]}
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
        # s.configure("TFrame", background="red")
        # s.configure("TLabel", background="green")
        # s.configure("TEntry", background="yellow")
        # s.configure("TButton", background="blue")

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
        self._console.grid(row=1, column=0, sticky=E+W+N+S, padx=10, pady=(10, 0))
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
        # >>>4

        # keybindings       <<<4
        self.bind("<Control-h>", sequence(self.display_help))
        self.bind("?", sequence(self.display_help))
        self.bind("<F1>", sequence(self.display_help))

        self.bind("<Control-q>", sequence(self.destroy))

        self.bind("<Control-p>", sequence(self.make_preview))
        self.bind("<Control-s>", sequence(self.make_output))

        self.bind("<Control-n>", sequence(self.function.add_noise))
        self.bind("<Control-N>", sequence(self.function.add_noise,
                                          self.make_preview))

        self.bind("<Control-g>", sequence(self.function.new_random_matrix))
        self.bind("<Control-G>", sequence(self.new_random_preview))

        self.bind("<Control-Key-minus>", sequence(self.world.zoom(2**.1),
                                                  self.make_preview))
        self.bind("<Control-Key-plus>", sequence(self.world.zoom(2**-.1),
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

        self.bind("<Control-u>", sequence(self.undo,
                                          self.make_preview))
        self.bind("<Control-r>", sequence(self.redo,
                                          self.make_preview))
        # >>>4

        # list of matrices, for UNDO
        self.undo_list = []
        self.undo_index = -1

        # queue containing parameters for pending output jobs
        self.output_params_queue = multiprocessing.Queue()
        # are there pending output jobs?
        self.pending_output_jobs = False
        self.output_message_queue = multiprocessing.Queue()

        # queue containing the preview image, computed by make_preview_job
        # the function ``update_GUI`` empties the queue
        self.preview_image_queue = multiprocessing.Queue()
        self.preview_message_queue = multiprocessing.Queue()

        self.message_queue = multiprocessing.Queue()
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

  Control-u     undo: go back to previous matrix
  Control-r     redo
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

    def update_GUI(self):        # <<<3

        # console messages
        self._console.config(state=NORMAL)
        while not self.message_queue.empty():
            self._console.insert(END, self.message_queue.get(block=False) + "\n")
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
                    self.world._canvas.tk_img = PIL.ImageTk.PhotoImage(image)
                    self.world._canvas.delete(self.world._image_id)
                    # self.world._canvas.delete(ALL)
                    self.world._image_id = self.world._canvas.create_image(
                                    (PREVIEW_SIZE//2, PREVIEW_SIZE//2),
                                    image=self.world._canvas.tk_img)
                break

        #         # draw tile
        #         if self.function.lattice_basis is not None:

        #             B = self.function.lattice_basis

        #             corner = self.world._canvas.coords(self.world._image_id)
        #             xc = corner[0] - width / 2
        #             yc = corner[1] - height / 2

        #             x_min, x_max, y_min, y_max = self.world.geometry
        #             delta_x = (x_max-x_min) / (width-1)
        #             delta_y = (y_max-y_min) / (height-1)
        #             a = self.world.angle * pi / 180
        #             t = self.world.modulus * complex(cos(a), sin(a))

        #             x0, y0 = 0, 0
        #             x0, y0 = x0*B[0][0] + y0*B[1][0], x0*B[0][1] + y0*B[1][1]
        #             z0 = complex(x0, y0) * t
        #             x0, y0 = z0.real, z0.imag
        #             x0, y0 = xc + (x0-x_min)/delta_x, yc + (y_max-y0)/delta_y

        #             x1, y1 = 1, 0
        #             x1, y1 = x1*B[0][0] + y1*B[1][0], x1*B[0][1] + y1*B[1][1]
        #             z1 = complex(x1, y1) * t
        #             x1, y1 = z1.real, z1.imag
        #             x1, y1 = xc + (x1-x_min)/delta_x, yc + (y_max-y1)/delta_y

        #             x2, y2 = 0, 1
        #             x2, y2 = x2*B[0][0] + y2*B[1][0], x2*B[0][1] + y2*B[1][1]
        #             z2 = complex(x2, y2) * t
        #             x2, y2 = z2.real, z2.imag
        #             x2, y2 = xc + (x2-x_min)/delta_x, yc + (y_max-y2)/delta_y

        #             x3, y3 = 1, 1
        #             x3, y3 = x3*B[0][0] + y3*B[1][0], x3*B[0][1] + y3*B[1][1]
        #             z3 = complex(x3, y3) * t
        #             x3, y3 = z3.real, z3.imag
        #             x3, y3 = xc + (x3-x_min)/delta_x, yc + (y_max-y3)/delta_y

        #             try:
        #                 for tmp in self.__tmp:
        #                     self.world._canvas.delete(tmp)
        #             except Exception as e:
        #                 self.__tmp = []
        #             self.__tmp.append(
        #                     self.world._canvas.create_polygon(
        #                         x0, y0, x1, y1, x3, y3, x2, y2,
        #                         fill="",
        #                         width=1, outline="white"))

        #             # self.__tmp.append(
        #             #         self.world._canvas.create_oval(
        #             #             x1-10, y1-10, x1+10, y1+10,
        #             #             fill="", outline="blue", width=3))
        #             # self.__tmp.append(
        #             #         self.world._canvas.create_oval(
        #             #             x2-10, y2-10, x2+10, y2+10,
        #             #             fill="", outline="green", width=3))
        #             self.__tmp.append(
        #                     self.world._canvas.create_oval(
        #                         x0-10, y0-10, x0+10, y0+10,
        #                         fill="", outline="white", width=1))

        self.after(100, self.update_GUI)
    # >>>3

    def make_output(self, *args):      # <<<3
        config = {
                "color": self.colorwheel.get_config(),
                "world": self.world.get_config(),
                "function": self.function.get_config(),
                "params": self.function.get_pattern_params(),
                "pattern": self.function.pattern,
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
                config["output_message_queue"] = self.message_queue
                p = multiprocessing.Process(target=background_output,
                                            kwargs=config)
                p.start()
                p.join()
            self.pending_output_jobs = False

        if not self.pending_output_jobs:
            threading.Thread(target=output_thread).start()
    # >>>3

    def make_preview(self, nb_tries=10, *args):      # <<<3

        self.world.adjust_geometry()
        ratio = self.world.width / self.world.height
        if ratio > 1:
            width = PREVIEW_SIZE
            height = round(PREVIEW_SIZE / ratio)
        else:
            width = round(PREVIEW_SIZE * ratio)
            height = PREVIEW_SIZE

        def make_preview_job():
            color = self.colorwheel.get_config()
            world = self.world.get_config()
            world["size"] = (width, height)
            params = self.function.get_pattern_params()


            image = make_image(color=color,
                               world=world,
                               pattern=self.function.pattern,
                               matrix=self.function.matrix,
                               message_queue=self.preview_message_queue,
                               stretch_color=self.colorwheel.stretch,
                               **params)
            self.preview_image_queue.put(image)

        try:
            self.preview_process.terminate()
            self.preview_process.join()
            # redefine queues to avoid corruption
            self.preview_message_queue = multiprocessing.Queue()
            self.preview_image_queue = multiprocessing.Queue()
        except AttributeError as e:
            pass

        try:
            self.preview_process = multiprocessing.Process(target=make_preview_job)
            self.preview_process.start()
            self.undo_list = self.undo_list[-UNDO_SIZE:]
            if self.undo_index == -1:
                if (len(self.undo_list) == 0 or
                        self.function.matrix != self.undo_list[-1]):
                    self.undo_list.append(self.function.matrix)
        except Error as e:
            self.message_queue.put("* {}".format(e))
    # >>>3

    def translate_rotate(self, dx, dy, dz=0):   # <<<3
        def translate_rotate_tmp(*args):
            if self.world.geometry_tab == "sphere":
                if dx != 0 or dy != 0 or dz != 0:
                    self.world.rotate(dx, dy, dz)
            elif self.world.geometry_tab == "plane":
                if dx != 0 or dy != 0:
                    self.world.translate(dx/10, dy/10)
            else:
                assert False
        return translate_rotate_tmp
    # >>>3

    def new_random_preview(self):       # <<<3
        N = 100
        for i in range(N):
            self.function.new_random_matrix()
            if self.function.add_symmetries(self.function.matrix):
                break
        self.make_preview()
    # >>>3

    def undo(self):     # <<<3
        if self.undo_index > -len(self.undo_list):
            self.undo_index -= 1
            self.function.change_matrix(self.undo_list[self.undo_index])
        # print(self.undo_index, len(self.undo_list))
    # >>>3

    def redo(self):     # <<<3
        if self.undo_index < -1:
            self.undo_index += 1
            self.function.change_matrix(self.undo_list[self.undo_index])
        # print(self.undo_index, len(self.undo_list))
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
    --modulus  /  --angle               transformation to apply to the result

    -c FILE  /  --color=FILE            choose color file
    --color-geometry=X,Y,X,Y            choose "geometry" of the color file
    --color-modulus  /  --color-angle   transformation to apply to the colorwheel

    --matrix=...                        transformation matrix
    --rotation-symmetry=P               p-fold symmetry around the origin

    --wallpaper=...                     name of wallpaper group
    --frieze=...                        name of frieze group
    --rosette=...                       name of frieze group
    --raw=...                           rotation for arbitrary function
    --params=...                        additional parameters:
                                           basis for lattice (for wallpaper)
                                           nb of rotations for rosettes
                                           basis for lattice (for raw)

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
            "wallpaper=", "frieze=", "rosette=", "raw=", "params=",
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
            world_config["filename"] = a
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
            tab = "wallpaper"
            pattern = a
        elif o in ["--frieze"]:
            tab = "frieze"
            pattern = a
        elif o in ["--rosette"]:
            tab = "rosette"
            pattern = a
        elif o in ["--raw"]:
            tab = "raw"
            pattern = a
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

    # color_config["modulus"] = 2
    # function_config["wallpaper_pattern"] = "4*2"
    # function_config["wallpaper_color_pattern"] = "*442"
    # function_config["matrix"] = { (0,1): 1 }

    # function_config["tab"] = "sphere"
    # function_config["sphere_pattern"] = "532"

    gui = CreateSymmetry()
    gui.colorwheel.set_config(color_config)
    gui.world.set_config(world_config)
    gui.function.set_config(function_config)
    if make_preview:
        gui.make_preview()
    gui.mainloop()

# >>>1


if __name__ == "__main__":
    main()

# vim: textwidth=0 foldmarker=<<<,>>> foldmethod=marker foldlevel=0
