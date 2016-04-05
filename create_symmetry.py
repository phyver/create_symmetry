#!/usr/bin/env python3

###
# imports
# <<<1

# image (Pillow)
import PIL
import PIL.ImageTk
from PIL.ImageColor import getrgb

import numpy as np

# Tkinter for GUI
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog

# misc functions
import getopt
import sys
import os.path
from itertools import product
import re
import json
import time

# math
from cmath import exp
from math import sqrt, pi, sin, cos
from random import randint, uniform, shuffle

# multiprocessing
import multiprocessing
import threading
from queue import Queue


# >>>1

verbose = 1
PREVIEW_SIZE = 500
OUTPUT_WIDTH = 1280
OUTPUT_HEIGHT = 960
COLOR_SIZE = 200
COLOR_GEOMETRY = (-1, 1, -1, 1)
WORLD_GEOMETRY = (-2, 2, -2, 2)


FRIEZE_TYPES = [    # <<<1
        "∞∞ (p111)",
        "22∞ (p211)",
        "∞∞* (p1m1)",
        "*∞ (p11m)",
        "*22∞ (p2mm)",
        "∞× (p11g)",
        "2*∞ (p2mg)",
        ]
# >>>1

WALLPAPER_TYPES = [     # <<<1
        "o (p1)" + "   -- general",
        "2222 (p2)",
        "*× (cm)" + "   -- rhombic",
        "2*22 (cmm)",
        "** (pm)" + "   -- rectangular",
        "×× (pg)",
        "*2222 (pmm)",
        "22* (pmg)",
        "22× (pgg)",
        "442 (p4)" + "   -- square",
        "*442 (p4m)",
        "4*2 (p4g)",
        "333 (p3)" + "   -- hexagonal",
        "3*3 (p31m)",
        "*333 (p3m1)",
        "632 (p6)",
        "*632 (p6m)",
        ]
# >>>1


###
# some utility functions
# <<<1
def error(*args, **kwargs):
    """print message on stderr"""
    print("***", *args, file=sys.stderr, **kwargs)


def message(*args, **kwargs):
    """print message if verbosity is greater than 1"""
    if verbose > 0:
        print(*args, **kwargs)


def sequence(*fs):
    def res(*args):
        for f in fs:
            f()
    return res


def invert22(M):
    d = M[0][0] * M[1][1] - M[1][0] * M[0][1]
    return [[M[1][1]/d, M[0][0]/d],
            [-M[0][1]/d, -M[1][0]/d]]


def str_to_floats(s):
    if s.strip() == "":
        return []
    else:
        return list(map(float, s.split(",")))


def floats_to_str(l):
    l = map(str, l)
    l = map(lambda s: re.sub("\.0*\s*$", "", s), l)
    return ", ".join(l)
# >>>1


###
# functions to manipulate matrices of functions
# <<<1
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


def mean(l, M):     # <<<2
    """compute the mean of the existing values with keys in l,
from the dictionnary M"""
    vs = []
    for k in l:
        if k in M:
            vs.append(M[k])
    return sum(vs) / len(vs)
# >>>2


def lattice_type(pattern):      # <<<2
    if pattern is None:
        return "raw"
    elif pattern in ["o", "p1", "2222", "p2"]:
        return "general"
    elif pattern in ["*×", "cm", "2*22", "cmm"]:
        return "rhombic"
    elif pattern in ["**", "pm", "××", "pg", "*2222", "pmm",
                     "22*", "pmg", "22×", "pgg"]:
        return "rectangular"
    elif pattern in ["442", "p4", "*442", "p4m", "4*2", "p4g"]:
        return "square"
    elif pattern in ["333", "p3", "3*3", "p31m", "*333", "p3m1",
                     "632", "p6", "*632", "p6m"]:
        return "hexagonal"
    elif pattern in ["∞∞", "p111", "22∞", "p211", "∞∞*", "p1m1", "*∞", "p11m",
                     "*22∞", "p2mm", "∞×", "p11g", "2*∞", "p2mg"]:
        return "frieze"
    else:
        error("unknown pattern type: '{}'".format(pattern))

# >>>2


def add_symmetries_to_matrix(M, pattern):     # <<<2
    """modify the matrix ``M`` to give a matrix with appropriate symetries.
``pattern`` can be any of the seven types of pattern patterns or wallpaper
patterns, in crystallographic convention or orbifold notation.
"""
    if pattern in ["p111", "∞∞", "o", "p1", "333", "p3", "442", "p4"]:
        return M
    elif pattern in ["p211", "22∞", "2222", "p2", "632", "p6"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (-n, -m)], M)
            R[(n, m)] = R[(-n, -m)] = coeff
        return R
    elif pattern in ["p1m1", "∞∞*", "*×", "cm", "*442", "p4m", "3*3", "p31m"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (m, n)], M)
            R[(n, m)] = R[(m, n)] = coeff
        return R
    elif pattern in ["p11m", "*∞", "*333", "p3m1"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (-m, -n)], M)
            R[(n, m)] = R[(-m, -n)] = coeff
        return R
    elif pattern in ["p11g", "∞×"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (-m, -n)], M)
            R[(n, m)] = R[(-m, -n)] = coeff
        S = {}
        for (n, m) in R:
            coeff = R[(n, m)]
            if (n+m) % 2 == 1:
                S[(n, m)] = coeff
                S[(-m, -n)] = -coeff
            else:
                S[(n, m)] = coeff
                S[(-m, -n)] = coeff
        return S
    elif pattern in ["p2mm", "*22∞", "2*22", "cmm", "*632", "p6m"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (m, n), (-n, -m), (-m, -n)], M)
            R[(n, m)] = R[(m, n)] = R[(-n, -m)] = R[(-m, -n)] = coeff
        return R
    elif pattern in ["p2mg", "2*∞"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (m, n), (-n, -m), (-m, -n)], M)
            R[(n, m)] = R[(m, n)] = R[(-n, -m)] = R[(-m, -n)] = coeff
        S = {}
        for (n, m) in R:
            coeff = R[(n, m)]
            if (n+m) % 2 == 1:
                S[(n, m)] = coeff
                S[(-n, -m)] = coeff
                S[(m, n)] = -coeff
                S[(-m, -n)] = -coeff
            else:
                S[(n, m)] = coeff
                S[(-n, -m)] = coeff
                S[(m, n)] = coeff
                S[(-m, -n)] = coeff
        return S
    elif pattern in ["**", "pm"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (n, -m)], M)
            R[(n, m)] = R[(n, -m)] = coeff
        return R
    elif pattern in ["pg", "××"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (n, -m)], M)
            R[(n, m)] = R[(n, -m)] = coeff
        S = {}
        for (n, m) in R:
            coeff = R[(n, m)]
            if n % 2 == 1:
                S[(n, m)] = coeff
                S[(n, -m)] = -coeff
            else:
                S[(n, m)] = coeff
                S[(n, -m)] = coeff
        return S
    elif pattern in ["pmm", "*2222"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (-n, -m), (-n, m), (n, -m)], M)
            R[(n, m)] = R[(-n, -m)] = R[(-n, m)] = R[(n, -m)] = coeff
        return R
    elif pattern in ["pmg", "22*"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (-n, -m), (n, -m), (-n, m)], M)
            R[(n, m)] = R[(-n, -m)] = R[(n, -m)] = R[(-n, m)] = coeff
        S = {}
        for (n, m) in R:
            coeff = R[(n, m)]
            if n % 2 == 1:
                S[(n, m)] = S[(-n, -m)] = coeff
                S[(n, -m)] = S[(-n, m)] = -coeff
            else:
                S[(n, m)] = S[(-n, -m)] = coeff
                S[(n, -m)] = S[(-n, m)] = coeff
        return S
    elif pattern in ["pgg", "22×"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (-n, -m), (n, -m), (-n, m)], M)
            R[(n, m)] = R[(-n, -m)] = R[(n, -m)] = R[(-n, m)] = coeff
        S = {}
        for (n, m) in R:
            coeff = R[(n, m)]
            if (n+m) % 2 == 1:
                S[(n, m)] = S[(-n, -m)] = coeff
                S[(n, -m)] = S[(-n, m)] = -coeff
            else:
                S[(n, m)] = S[(-n, -m)] = coeff
                S[(n, -m)] = S[(-n, m)] = coeff
        return S
    elif pattern in ["p4g", "4*2"]:
        R = {}
        for (n, m) in M:
            coeff = mean([(n, m), (m, n)], M)
            R[(n, m)] = R[(m, n)] = coeff
        S = {}
        for (n, m) in R:
            coeff = R[(n, m)]
            if (n+m) % 2 == 1:
                S[(n, m)] = coeff
                S[(m, n)] = -coeff
            else:
                S[(n, m)] = coeff
                S[(m, n)] = coeff
        return S
    else:
        return M
# >>>2
# >>>1


###
# making an image from a transformation and a colorwheel
def make_world(                   # <<<1
        matrix=None,                        # the matrix of the transformation
        color_filename="",                  # image for the colorwheel image
        size=(OUTPUT_WIDTH, OUTPUT_HEIGHT),     # size of the output image
        modulus="1",
        angle="0",
        geometry=(-2, 2, -2, 2),                # coordinates of the world
        color_geometry=COLOR_GEOMETRY,          # coordinates of the colorwheel
        color_modulus="1",
        color_angle="0",
        lattice_matrix=None,
        lattice="",
        rotational_symmetry=1,
        default_color="black",
        message_queue=None,
        **_
        ):

    assert matrix is not None
    assert color_filename != ""

    x_min, x_max, y_min, y_max = geometry
    color_x_min, color_x_max, color_y_min, color_y_max = color_geometry
    width, height = size

    if isinstance(default_color, str):
        default_color = getrgb(default_color)

    # print("start")
    tmp = PIL.Image.open(color_filename)
    color_width, color_height = tmp.size

    # we add a border to the top / right of the color image, using the default
    # color
    color_im = PIL.Image.new("RGB",
                             (color_width+1,
                              color_height+1),
                             color=default_color)
    color_im.paste(tmp, (1, 1))
    # print("got color")

    delta_x = (x_max-x_min) / (width-1)
    delta_y = (y_max-y_min) / (height-1)

    color_delta_x = (color_x_max-color_x_min) / (color_width-1)
    color_delta_y = (color_y_max-color_y_min) / (color_height-1)

    xs = np.arange(width)
    xs = x_min + xs*delta_x
    # ys = ys / (modulus * complex(cos(angle*pi/180), sin(angle*pi/180)))
    # print("got xs")

    ys = np.arange(height)
    ys = y_max - ys*delta_y
    # xs = xs / (modulus * complex(cos(angle*pi/180), sin(angle*pi/180)))
    # print("got ys")

    zs = xs[:, None] + 1j*ys
    zs = zs / (modulus * complex(cos(angle*pi/180), sin(angle*pi/180)))
    zsc = None
    ezs = None
    ezsc = None
    xs, ys = None, None

    res = np.zeros((width, height), complex)
    # print("initialized res")
    w1, w2 = 1, len(matrix)
    for (n, m) in matrix:
        if lattice == "rosette" or lattice == "plain":
            if zsc is None:
                zsc = np.conj(zs)
            res = res + matrix[(n, m)] * zs**n * zsc**m
        elif lattice == "frieze":
            if ezs is None or ezsc is None:
                ezs = np.exp(1j * zs)
                ezsc = np.conj(ezs)
            res = res + matrix[(n, m)] * ezs**n * ezsc**m
        else:   # lattice_matrix should be a 2x2 array
            ZS = np.zeros((width, height), complex)
            for k in range(0, rotational_symmetry):
                _tmp = zs * complex(cos(2*pi*k/rotational_symmetry),
                                    sin(2*pi*k/rotational_symmetry))
                _xs = _tmp.real
                _ys = _tmp.imag
                _tmp = (n*(lattice_matrix[0][0]*_xs+lattice_matrix[0][1]*_ys) +
                        m*(lattice_matrix[1][0]*_xs+lattice_matrix[1][1]*_ys))
                ZS += np.exp(2j*pi*_tmp)
            ZS = ZS / rotational_symmetry
            res = res + matrix[(n, m)] * ZS
        if message_queue is not None:
            message_queue.put("wave {}/{}".format(w1, w2))
        w1 += 1
    # print("computed res")

    res = res / (color_modulus *
                 complex(cos(color_angle*pi/180), sin(color_angle*pi/180)))

    xs = np.rint((res.real - color_x_min) / color_delta_x).astype(int)
    # print("xs to int")
    ys = np.rint((color_y_max - res.imag) / color_delta_y).astype(int)
    # print("ys to int")

    xs = xs + 1
    ys = ys + 1

    np.place(xs, xs < 0, [0])
    np.place(xs, xs >= color_width, [0])
    # print("remove invalid values in xs")
    np.place(ys, ys < 0, [0])
    np.place(ys, ys >= color_height, [0])
    # print("remove invalid values in ys")

    res = np.dstack([xs, ys])
    # print("stack res")

    color = np.asarray(color_im)
    # print("got color")
    color = color.reshape(color_height+1, color_width+1, 3)
    # print("reshape color")
    color = color.transpose(1, 0, 2)
    # print("transpose color")

    res = color[xs, ys]
    # print("apply color to res")
    res = np.array(res, dtype=np.uint8)
    # print("convert res")

    res = res.transpose(1, 0, 2)
    # print("transpose res")

    # print("end")
    return PIL.Image.fromarray(res, "RGB")
# >>>1


###
# GUI
class Error(Exception):
    pass


class LabelEntry(Frame):  # <<<1
    """
    An Entry widget with a label on its left.
    """
    entry_widget = None  # the Entry widget
    label_widget = None  # the Label widget
    content = None       # the corresponding StringVar
    convert = None       # the conversion function used for validation

    def __init__(self, parent, label, on_click=None,  # <<<2
                 value="",
                 convert=None,
                 state=NORMAL, **kwargs):
        Frame.__init__(self, parent)

        self.convert = convert

        if label:
            self.label_widget = Label(self, text=label)
            self.label_widget.pack(side=LEFT, padx=(0, 5))

        self.content = StringVar("")
        self.content.set(value)
        self.entry_widget = Entry(self, textvar=self.content,
                                  state=state, **kwargs)
        self.entry_widget.pack(side=LEFT)

        for method in ["config", "configure", "bind", "focus_set"]:
            setattr(self, method, getattr(self.entry_widget, method))

        if self.convert is not None:
            self.bind("<Enter>", self.validate)
            self.bind("<FocusOut>", self.validate)
    # >>>2

    def validate(self, *args):     # <<<2
        if self.convert is None:
            return
        else:
            try:
                self.convert(self.content.get())
            except Exception as e:
                self.entry_widget.config(foreground="red")
    # >>>2

    def set(self, s):  # <<<2
        if s is None:
            self.content.set("")
        else:
            self.content.set(s)
            if self.convert is not None:
                self.validate()
    # >>>2

    def get(self):  # <<<2
        s = self.content.get()
        if self.convert is not None:
            try:
                return self.convert(s)
            except Exception as e:
                raise Error("{}: cannot convert value of field '{}': {}"
                            .format(self.label_widget.cget("text"), s, e))
        else:
            return s
    # >>>2

    def delete(self):  # <<<2
        self.content.set("")
    # >>>2

    def disable(self):  # <<<2
        self.entry_widget.config(state=DISABLED)
        self.label_widget.config(state=DISABLED)
    # >>>2

    def enable(self):  # <<<2
        self.entry_widget.config(state=NORMAL)
        self.label_widget.config(state=NORMAL)
    # >>>2
# >>>1


class ColorWheel(LabelFrame):   # <<<1

    @property
    def geometry(self):     # <<<2
        x_min = self._x_min.get()
        x_max = self._x_max.get()
        y_min = self._y_min.get()
        y_max = self._y_max.get()
        return x_min, x_max, y_min, y_max
    # >>>2

    @property
    def modulus(self):  # <<<2
        return self._modulus.get()
    # >>>2

    @property
    def angle(self):    # <<<2
        return self._angle.get()
    # >>>2

    @property
    def color(self):    # <<<2
        return self._color.get()
    # >>>2

    def __init__(self,              # <<<2
                 root,
                 filename=None,
                 geometry=COLOR_GEOMETRY,
                 modulus=1,
                 angle=0,
                 default_color="black"):

        LabelFrame.__init__(self, root)
        self.configure(text="Color Wheel")

        self._color = LabelEntry(self,
                                 label="default color",
                                 value=default_color,
                                 width=10,
                                 convert=getrgb)
        self._color.grid(row=0, column=0, padx=5, pady=5)

        self._filename = Label(self, text="...")
        self._filename.grid(row=1, column=0, padx=5, pady=5)

        self._canvas = Canvas(self, width=200, height=200, bg="white")
        self._canvas.grid(row=2, column=0, padx=5, pady=5)
        for i in range(5, COLOR_SIZE, 10):
            for j in range(5, COLOR_SIZE, 10):
                self._canvas.create_line(i-1, j, i+2, j, fill="gray")
                self._canvas.create_line(i, j-1, i, j+2, fill="gray")
        self._colorwheel_id = None
        self._canvas.bind("<Button-3>", self.set_origin)
        self._canvas.bind("<Double-Button-1>", self.choose_colorwheel)

        Button(self, text="choose file",
               command=self.choose_colorwheel).grid(row=3, column=0,
                                                    padx=5, pady=5)

        coord_frame = LabelFrame(self, text="coordinates")
        coord_frame.grid(row=4, column=0, sticky=E+W, padx=5, pady=5)
        coord_frame.columnconfigure(0, weight=1)
        coord_frame.columnconfigure(1, weight=1)

        self._x_min = LabelEntry(coord_frame, label="x min",
                                 value=geometry[0],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._x_min.grid(row=0, column=0, padx=5, pady=5)

        self._x_max = LabelEntry(coord_frame, label="x max",
                                 value=geometry[1],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._x_max.grid(row=0, column=1, padx=5, pady=5)

        self._y_min = LabelEntry(coord_frame, label="y min",
                                 value=geometry[2],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._y_min.grid(row=1, column=0, padx=5, pady=5)

        self._y_max = LabelEntry(coord_frame, label="y max",
                                 value=geometry[3],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._y_max.grid(row=1, column=1, padx=5, pady=5)

        Button(coord_frame, text="reset",
               command=self.reset_geometry).grid(row=2, column=0, columnspan=2,
                                                 padx=5, pady=5)

        transformation_frame = LabelFrame(self, text="transformation")
        transformation_frame.grid(row=5, column=0, sticky=E+W, padx=5, pady=5)
        self._modulus = LabelEntry(transformation_frame, label="modulus",
                                   value=modulus,
                                   convert=float,
                                   width=4)
        self._modulus.pack(padx=5, pady=5)

        self._angle = LabelEntry(transformation_frame, label="angle (°)",
                                 value=angle,
                                 convert=float,
                                 width=4)
        self._angle.pack(padx=5, pady=5)

        self.update_defaultcolor()

        if filename is not None:
            self.change_colorwheel(filename)
        elif os.path.exists("./colorwheel.jpg"):
            self.change_colorwheel("colorwheel.jpg")
        else:
            self.filename = None
    # >>>2

    def update_defaultcolor(self, *args):     # <<<2
        try:
            c = self.color
            self._canvas.config(bg="#{:02x}{:02x}{:02x}".format(*c))
            self._color.config(foreground="black")
        except Exception as e:
            error("error: '{}'".format(e))
            self._color.config(foreground="red")
    # >>>2

    def change_colorwheel(self, filename):  # <<<2
        try:
            img = PIL.Image.open(filename)
            img.thumbnail((COLOR_SIZE, COLOR_SIZE), PIL.Image.ANTIALIAS)
            self._image = img
            tk_img = PIL.ImageTk.PhotoImage(img)
            self._tk_image = tk_img     # prevent garbage collection
            self._canvas.delete(self._colorwheel_id)
            self._canvas.create_image((100, 100), image=tk_img)
            self.filename = filename
            self._filename.config(text=os.path.basename(filename))
            width, height = self._image.size
            ratio = width / height
            if ratio > 1:
                self._x_min.set(COLOR_GEOMETRY[0])
                self._x_max.set(COLOR_GEOMETRY[1])
                self._y_min.set(COLOR_GEOMETRY[2] / ratio)
                self._y_max.set(COLOR_GEOMETRY[3] / ratio)
            else:
                self._x_min.set(COLOR_GEOMETRY[0] * ratio)
                self._x_max.set(COLOR_GEOMETRY[1] * ratio)
                self._y_min.set(COLOR_GEOMETRY[2])
                self._y_max.set(COLOR_GEOMETRY[3])
        except Exception as e:
            error("problem while opening {} for color image: {}"
                  .format(filename, e))
    # >>>2

    def choose_colorwheel(self, *args):    # <<<2
        filename = filedialog.askopenfilename(
                title="Create Symmetry: choose color wheel image",
                initialdir="./",
                filetypes=[("images", "*.jpg *.jpeg *.png"), ("all", "*.*")])
        if filename:
            self.change_colorwheel(filename)
    # >>>2

    def set_origin(self, event):        # <<<2
        x, y = event.x, event.y
        x_min, x_max, y_min, y_max = self.geometry
        delta_x = x_max - x_min
        delta_y = y_max - y_min

        x_min = -x/COLOR_SIZE * delta_x
        x_max = x_min + delta_x
        y_max = y/COLOR_SIZE * delta_y
        y_min = y_max - delta_y
        self._x_min.set(x_min)
        self._x_max.set(x_max)
        self._y_min.set(y_min)
        self._y_max.set(y_max)
    # >>>2

    def reset_geometry(self, *args):        # <<<2
        if self.filename is not None:
            self.change_colorwheel(self._filename)
        else:
            self._x_min.set(COLOR_GEOMETRY[0])
            self._x_max.set(COLOR_GEOMETRY[1])
            self._y_min.set(COLOR_GEOMETRY[2])
            self._y_max.set(COLOR_GEOMETRY[3])
    # >>>2

    def get_config(self):           # <<<2
        return {
                "filename": self.filename,
                "color": self._color.entry_widget.get(),    # don't use _color.get to avoid conversion to rgb
                "geometry": self.geometry,
                "modulus": self.modulus,
                "angle": self.angle,
                }
    # >>>2

    def set_config(self, cfg):      # <<<2
        if "filename" in cfg:
            self.change_colorwheel(cfg["filename"])
        if "color" in cfg:
            self._color.set(cfg["color"])
            self.update_defaultcolor()
        if "geometry" in cfg:
            g = cfg["geometry"]
            self._x_min.set(g[0])
            self._x_max.set(g[1])
            self._y_min.set(g[2])
            self._y_max.set(g[3])
        if "modulus" in cfg:
            self._modulus.set(cfg["modulus"])
        if "angle" in cfg:
            self._angle.set(cfg["angle"])
    # >>>2
# >>>1


class World(LabelFrame):     # <<<1

    @property
    def geometry(self):     # <<<2
        x_min = self._x_min.get()
        x_max = self._x_max.get()
        y_min = self._y_min.get()
        y_max = self._y_max.get()
        return x_min, x_max, y_min, y_max
    # >>>2

    @property
    def modulus(self):  # <<<2
        return self._modulus.get()
    # >>>2

    @property
    def angle(self):    # <<<2
        return self._angle.get()
    # >>>2

    @property
    def size(self):    # <<<2
        return self._width.get(), self._height.get()
    # >>>2

    @property
    def width(self):    # <<<2
        return self._width.get()
    # >>>2

    @property
    def height(self):    # <<<2
        return self._height.get()
    # >>>2

    @property
    def filename_template(self):    # <<<2
        return self._filename_template.get()
    # >>>2

    def __init__(self,              # <<<2
                 root,
                 geometry=WORLD_GEOMETRY,
                 modulus=1,
                 angle=0,
                 size=(OUTPUT_WIDTH, OUTPUT_HEIGHT),
                 filename_template="output-{:03}"):

        LabelFrame.__init__(self, root)
        self.configure(text="World")

        # the preview image     <<<3
        self._canvas = Canvas(self, width=PREVIEW_SIZE, height=PREVIEW_SIZE,
                              bg="white")
        for i in range(5, PREVIEW_SIZE, 10):
            for j in range(5, PREVIEW_SIZE, 10):
                self._canvas.create_line(i-1, j, i+2, j, fill="gray")
                self._canvas.create_line(i, j-1, i, j+2, fill="gray")
        # self._canvas.pack(side=LEFT)
        self._canvas.grid(row=0, column=0, rowspan=4, padx=5, pady=5)
        self._image_id = None
        # >>>3

        # geometry of result    <<<3
        coord_frame = LabelFrame(self, text="coordinates")
        # coord_frame.pack()
        coord_frame.grid(row=0, column=1, sticky=E+W, padx=5, pady=5)
        coord_frame.columnconfigure(0, weight=1)
        coord_frame.columnconfigure(1, weight=1)

        self._x_min = LabelEntry(coord_frame, label="x min",
                                 value=geometry[0],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._x_min.grid(row=0, column=0, padx=5, pady=5)

        self._x_max = LabelEntry(coord_frame, label="x max",
                                 value=geometry[1],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._x_max.grid(row=0, column=1, padx=5, pady=5)

        self._y_min = LabelEntry(coord_frame, label="y min",
                                 value=geometry[2],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._y_min.grid(row=1, column=0, padx=5, pady=5)

        self._y_max = LabelEntry(coord_frame, label="y max",
                                 value=geometry[3],
                                 convert=float,
                                 width=4, justify=RIGHT)
        self._y_max.grid(row=1, column=1, padx=5, pady=5)

        Button(coord_frame, text="zoom -",
               command=self.zoom_out).grid(row=3, column=0,
                                           padx=5, pady=5)
        Button(coord_frame, text="zoom +",
               command=self.zoom_in).grid(row=3, column=1,
                                          padx=5, pady=5)

        transformation_frame = LabelFrame(self, text="transformation")
        transformation_frame.grid(row=1, column=1, sticky=E+W, padx=5, pady=5)
        self._modulus = LabelEntry(transformation_frame, label="modulus",
                                   value=modulus,
                                   convert=float,
                                   width=4)
        self._modulus.pack(padx=5, pady=5)

        self._angle = LabelEntry(transformation_frame, label="angle (°)",
                                 value=angle,
                                 convert=float,
                                 width=4)
        self._angle.pack(padx=5, pady=5)

        Button(coord_frame, text="reset",
               command=self.reset_geometry).grid(row=4, column=0, columnspan=2,
                                                 padx=5, pady=5)
        # >>>3

        # result settings       <<<3
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

        self._filename_template = LabelEntry(settings_frame, label=None,
                                             value=filename_template,
                                             width=15)
        self._filename_template.pack(padx=5, pady=5)
        # >>>3

        tmp = LabelFrame(self, text="image")
        tmp.grid(row=3, column=1, sticky=E+W, padx=5, pady=5)

        self._preview_button = Button(tmp, text="preview", command=None)
        self._preview_button.pack(padx=5, pady=5)

        self._save_button = Button(tmp, text="save", command=None)
        self._save_button.pack(padx=5, pady=5)

        width, height = self.size
        if width > height:
            self.adjust_preview_X()
        else:
            self.adjust_preview_X()
    # >>>2

    def zoom_out(self, *args):      # <<<2
        a = 2**0.1
        for c in ["_x_min", "_x_max", "_y_min", "_y_max"]:
            self.__dict__[c].set(self.__dict__[c].get() * a)
    # >>>2

    def zoom_in(self, *args):       # <<<2
        a = 2**0.1
        for c in ["_x_min", "_x_max", "_y_min", "_y_max"]:
            self.__dict__[c].set(self.__dict__[c].get() / a)
    # >>>2

    def reset_geometry(self, *args):        # <<<2
        self._x_min.set(WORLD_GEOMETRY[0])
        self._x_max.set(WORLD_GEOMETRY[1])
        self._y_min.set(WORLD_GEOMETRY[2])
        self._y_max.set(WORLD_GEOMETRY[3])
        if self.width > self.height:
            self.adjust_preview_X()
        else:
            self.adjust_preview_X()
    # >>>2

    def adjust_preview_X(self, *args):      # <<<2
        ratio = self.width / self.height
        x_min, x_max, y_min, y_max = self.geometry
        delta_y = y_max - y_min
        delta_x = delta_y * ratio
        middle_x = (x_min+x_max) / 2
        self._x_min.set(middle_x - delta_x/2)
        self._x_max.set(middle_x + delta_x/2)
    # >>>2

    def adjust_preview_Y(self, *args):      # <<<2
        ratio = self.height / self.width
        x_min, x_max, y_min, y_max = self.geometry
        delta_x = x_max - x_min
        delta_y = delta_x * ratio
        middle_y = (y_min+y_max) / 2
        self._y_min.set(middle_y - delta_y/2)
        self._y_max.set(middle_y + delta_y/2)
    # >>>2

    def get_config(self):           # <<<2
        return {
                "geometry": self.geometry,
                "modulus": self.modulus,
                "angle": self.angle,
                "size": self.size,
                }
    # >>>2

    def set_config(self, cfg):      # <<<2
        if "geometry" in cfg:
            g = cfg["geometry"]
            self._x_min.set(g[0])
            self._x_max.set(g[1])
            self._y_min.set(g[2])
            self._y_max.set(g[3])
        if "modulus" in cfg:
            self._modulus.set(cfg["modulus"])
        if "angle" in cfg:
            self._angle.set(cfg["angle"])
        if "size" in cfg:
            self._width.set(cfg["size"][0])
            self._height.set(cfg["size"][1])
    # >>>2
# >>>1


class Function(LabelFrame):     # <<<1

    @property
    def current_tab(self):      # <<<2
        if ("wallpaper" in self._tabs.tab(self._tabs.select(), "text")):
            return "wallpaper"
        elif ("frieze" in self._tabs.tab(self._tabs.select(), "text")):
            if self.rosette:
                return "rosette"
            else:
                return "frieze"
        elif ("raw" in self._tabs.tab(self._tabs.select(), "text")):
            return "raw"
        else:
            assert False
    # >>>2

    @property
    def rosette(self):          # <<<2
        return self._rosette.get()
    # >>>2

    @property
    def rotational_symmetry(self):      # <<<2
        if self.current_tab == "rosette":
            return self._rosette_rotation.get()
        elif self.current_tab == "raw":
            return self._raw_rotation.get()
        elif self.current_tab == "wallpaper":
            lattice = lattice_type(self.pattern)
            if lattice == "square":
                return 4
            elif lattice == "hexagonal":
                return 3
            else:
                return 1
        elif self.current_tab == "frieze":
            return 1
        else:
            assert False
    # >>>2

    @property
    def pattern(self):          # <<<2
        if self.current_tab == "frieze" or self.current_tab == "rosette":
            return self._frieze_type.get().split()[0]
        elif self.current_tab == "wallpaper":
            return self._wallpaper_type.get().split()[0]
        elif self.current_tab == "raw":
            return self._raw_rotation.get()
        else:
            assert False
    # >>>2

    @property
    def lattice_parameters(self):       # <<<2
        s = self._lattice_params.get()

        if self.current_tab == "raw":
            return s
        else:
            lattice = lattice_type(self.pattern)
            lattice_params = ()

            try:
                if lattice == "general":
                    xsi, eta = s
                    lattice_params = (xsi, eta)
                elif lattice == "rhombic":
                    b = s
                    lattice_params = b
                elif lattice == "rectangular":
                    L = s
                    lattice_params = L
            except Exception as e:
                raise Error("error while getting lattice parameters '{}': {}"
                            .format(s, e))
            return lattice_params
    # >>>2

    @property
    def lattice_matrix(self):       # <<<2
        if self.current_tab == "wallpaper":
            lattice = lattice_type(self.pattern)
            if lattice == "general":
                xsi, eta = self.lattice_parameters
                return [[1, -xsi/eta], [0, 1/eta]]
            elif lattice == "rhombic":
                b = self.lattice_parameters
                return [[1, 1/(2*b)], [1, -1/(2*b)]]
            elif lattice == "rectangular":
                L = self.lattice_parameters
                return [[2, 0], [0, 1/L]]
            elif lattice == "square":
                return [[1, 0], [0, 1]]
            elif lattice == "hexagonal":
                return [[1, 1/sqrt(3)], [0, 2/sqrt(3)]]
            else:
                assert False
        elif self.current_tab == "raw":
            v1 = self._basis_matrix1.get()
            v2 = self._basis_matrix2.get()
            v1 = [v1[0], v1[1]]
            v2 = [v2[0], v2[1]]
            return [v1, v2]
        elif self.current_tab == "frieze":
            return None
        elif self.current_tab == "rosette":
            return None
        else:
            assert False
    # >>>2

    def __init__(self, root, matrix=None,      # <<<2
                 tab=None,      # which tab to select ("wallpaper", "frieze", "rosette", "raw")
                 pattern=None,  # which pattern to select (group name, or rotation symmetry for "raw")
                 pattern_params=None    # additional parameters (lattice parameters, rotation symmetry for rosettes)
                 ):

        LabelFrame.__init__(self, root)
        self.configure(text="Function")

        # tabs for the different kinds of functions / symmetries  <<<3
        self._tabs = Notebook(self)
        self._tabs.grid(row=0, column=0, rowspan=2, sticky=N+S, padx=5, pady=5)

        wallpaper_tab = Frame(self._tabs)
        self._tabs.add(wallpaper_tab, text="wallpaper")

        frieze_tab = Frame(self._tabs)
        self._tabs.add(frieze_tab, text="frieze")

        raw_tab = Frame(self._tabs)
        self._tabs.add(raw_tab, text="raw")
        # >>>3

        # wallpaper tab      <<<3
        self._wallpaper_type = StringVar()

        self._wallpaper_combo = Combobox(
                wallpaper_tab, width=20, exportselection=0,
                textvariable=self._wallpaper_type,
                state="readonly",
                values=WALLPAPER_TYPES
                )
        self._wallpaper_combo.pack(padx=5, pady=5)
        self._wallpaper_combo.current(0)

        self._lattice_params = LabelEntry(wallpaper_tab,
                                          label="lattice parameters",
                                          value="1,1",
                                          convert=str_to_floats,
                                          width=7)
        self._lattice_params.pack(padx=5, pady=5)

        self._wallpaper_combo.bind("<<ComboboxSelected>>",
                                   self.select_wallpaper)

        Button(wallpaper_tab, text="make matrix",
               command=self.make_matrix).pack(side=BOTTOM, padx=5, pady=5)
        # # >>>3

        # frieze / rosette tab   <<<3
        self._frieze_type = StringVar()
        self._frieze_combo = Combobox(frieze_tab, width=15, exportselection=0,
                                      textvariable=self._frieze_type,
                                      state="readonly",
                                      values=FRIEZE_TYPES)
        self._frieze_combo.pack(padx=5, pady=5)
        self._frieze_combo.current(0)

        self._rosette = BooleanVar()
        self._rosette.set(False)

        rosette_button = Checkbutton(frieze_tab, text="rosette",
                                     variable=self._rosette,
                                     onvalue=True, offvalue=False,
                                     command=self.set_rosette)
        rosette_button.pack(padx=5, pady=5)

        self._rosette_rotation = LabelEntry(frieze_tab,
                                               label="symmetries",
                                               value=5,
                                               convert=int,
                                               width=2)
        self._rosette_rotation.pack(padx=5, pady=5)

        Button(frieze_tab, text="make matrix",
               command=self.make_matrix).pack(side=BOTTOM, padx=5, pady=5)
        # # >>>3

        # raw tab   <<<3
        self._basis_matrix1 = LabelEntry(raw_tab,
                                         label="first vector",
                                         value="1, 0",
                                         convert=str_to_floats,
                                         width=10)
        self._basis_matrix2 = LabelEntry(raw_tab,
                                         label="second vector",
                                         value="0, 1",
                                         convert=str_to_floats,
                                         width=10)
        self._basis_matrix1.grid(row=0, column=0, sticky=E, padx=5, pady=5)
        self._basis_matrix2.grid(row=1, column=0, sticky=E, padx=5, pady=5)

        self._raw_rotation = LabelEntry(raw_tab,
                                               label="rotational symmetry",
                                               value=1,
                                               convert=int,
                                               width=3)
        self._raw_rotation.grid(row=2, column=0, padx=5, pady=5)
        # >>>3

        # display matrix    <<<3
        tmp = LabelFrame(self, text="matrix")
        tmp.grid(row=0, column=1, rowspan=2, sticky=N+S,  padx=5, pady=5)

        tmp2 = Frame(tmp)
        tmp2.pack()
        self._display_matrix = Listbox(tmp2, selectmode=MULTIPLE,
                                       font="TkFixedFont",
                                       width=28, height=12)
        self._display_matrix.pack(side=LEFT)

        scrollbar = Scrollbar(tmp2)
        scrollbar.pack(side=RIGHT, fill=Y)
        self._display_matrix.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self._display_matrix.yview)

        self._display_matrix.bind("<BackSpace>", self.remove_entries)
        self._display_matrix.bind("<Delete>", self.remove_entries)

        if matrix is not None:
            self.change_matrix(matrix)
        else:
            self.change_matrix({})
        # >>>3

        # change entries <<<3
        self._change_entry = LabelEntry(tmp, label="change entry", value="",
                                        width=17, font="TkFixedFont")
        self._change_entry.pack(padx=5, pady=5)
        self._change_entry.bind("<Return>", self.add_entry)
        # >>>3

        # random matrix     <<<3
        tmp = LabelFrame(self, text="random matrix")
        tmp.grid(row=0, column=2, sticky=N+S, padx=5, pady=5)

        self._random_nb_coeff = LabelEntry(tmp, label="nb coefficients",
                                           value=3,
                                           convert=int,
                                           width=4)
        self._random_nb_coeff.pack(padx=5, pady=5)

        self._random_min_degre = LabelEntry(tmp, label="min degre",
                                            value=-6,
                                            convert=int,
                                            width=4)
        self._random_min_degre.pack(padx=5, pady=5)

        self._random_max_degre = LabelEntry(tmp, label="max degre",
                                            value=6,
                                            convert=int,
                                            width=4)
        self._random_max_degre.pack(padx=5, pady=5)

        self._random_min_coeff = LabelEntry(tmp, label="min coefficient",
                                            value=-.1,
                                            convert=float,
                                            width=4)
        self._random_min_coeff.pack(padx=5, pady=5)

        self._random_max_coeff = LabelEntry(tmp, label="max coefficient",
                                            value=.1,
                                            convert=float,
                                            width=4)
        self._random_max_coeff.pack(padx=5, pady=5)

        generate = Button(tmp, text="generate", command=self.new_random_matrix)
        generate.pack(padx=5, pady=5)
        # >>>3

        # add noise <<<3
        tmp3 = Frame(tmp)
        tmp3.pack(padx=5, pady=5)
        self._noise = LabelEntry(tmp3, label="(%)",
                                 value=10, convert=float,
                                 width=3)
        self._noise.pack(side=RIGHT, padx=5, pady=5)
        self._noise.bind("<Return>", self.add_noise)

        random_noise = Button(tmp3, text="random noise",
                              command=self.add_noise)
        random_noise.pack(side=LEFT, padx=5, pady=5)
        # >>>3

        # make sure the layout reflects the selected options    <<<3
        self.select_wallpaper()
        self.set_rosette()

        if tab == "wallpaper":
            self._tabs.select(0)
            self._wallpaper_combo.current(0)
            for i in range(len(WALLPAPER_TYPES)):
                if re.search("\\b{}\\b".format(pattern), WALLPAPER_TYPES[i]):
                    self._wallpaper_combo.current(i)
            if pattern_params:
                self._lattice_params.set(pattern_params)

        elif tab == "frieze" or tab == "rosette":
            self._tabs.select(1)
            self._frieze_combo.current(0)
            for i in range(len(FRIEZE_TYPES)):
                if re.search("\\b{}\\b".format(pattern), FRIEZE_TYPES[i]):
                    self._frieze_combo.current(i)
            if tab == "rosette":
                self._rosette.set(True)
                self.set_rosette()
            if pattern_params:
                self._rosette_rotation.set(pattern_params)

        elif tab == "raw":
            self._tabs.select(2)
            if pattern_params:
                try:
                    params = pattern_params.split(",")
                    self._basis_matrix1.set(", ".join(params[0:2]))
                    self._basis_matrix2.set(", ".join(params[2:4]))
                    self._raw_rotation.set(pattern)
                except:
                    self._basis_matrix1.set("1, 0")
                    self._basis_matrix2.set("0, 1")
                    self._raw_rotation.set(1)
        # >>>3
    # >>>2

    def change_matrix(self, M=None):    # <<<2
        if M is None:
            M = self.matrix
        else:
            self.matrix = M
        self._display_matrix.delete(0, END)
        keys = list(M.keys())
        keys.sort()

        def show(z):
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
                x = "{:.4f}".format(z.real).rstrip("0")
                y = "{:.4f}".format(abs(z.imag)).rstrip("0")
                x = x.rstrip(".").rjust(7)
                y = y.rstrip(".")
                return "{} {} {}i".format(x, sign, y)

        for (n, m) in keys:
            self._display_matrix.insert(END, "{:2}, {:2} : {}"
                                             .format(n, m, show(M[(n, m)])))
    # >>>2

    def add_entry(self, *args):     # <<<2
        e = self._change_entry.get().strip()
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
            self._change_entry.set("")
        except Exception as err:
            error("cannot parse matrix entry '{}': {}".format(e, err))
        # >>>2

    def remove_entries(self, *args):        # <<<2
        entries = self._display_matrix.curselection()
        p = 0
        for e in entries:
            tmp = self._display_matrix.get(e-p)
            n, m, _ = re.split("\s*(?:[,;:]|(?:[-=]>))\s*", tmp)
            self.matrix.pop((int(n), int(m)))
            self._display_matrix.delete(e-p, e-p)
            p += 1
    # >>>2

    def add_noise(self, *args):     # <<<2
        try:
            e = self._noise.get()/100
        except:
            e = 0.1
        M = self.matrix
        for n, m in M:
            z = M[(n, m)]
            modulus = abs(z) * uniform(0, e)
            angle = uniform(0, 2*pi)
            M[(n, m)] = z + modulus * complex(cos(angle), sin(angle))
        self.change_matrix()
    # >>>2

    def new_random_matrix(self, *args):     # <<<2
        a = self._random_min_degre.get()
        b = self._random_max_degre.get()
        coeffs = list(product(range(a, b+1), range(a, b+1)))
        shuffle(coeffs)
        n = self._random_nb_coeff.get()
        coeffs = coeffs[:n]
        a = self._random_min_coeff.get()
        b = self._random_max_coeff.get()
        M = {}
        for (n, m) in coeffs:
            M[(n, m)] = complex(uniform(a, b), uniform(a, b))
        self.change_matrix(M)
    # >>>2

    def set_frieze_type(self, *args):       # <<<2
        frieze_combo.select_clear()
        self.function["frieze_type"] = frieze_combo.stringvar.get()
    # >>>2

    def set_rosette(self, *args):     # <<<2
        if self.rosette:
            self._rosette_rotation.enable()
        else:
            self._rosette_rotation.disable()
    # >>>2

    def select_wallpaper(self, *args):        # <<<2
        pattern = self.pattern
        lattice = lattice_type(pattern)
        if lattice == "general":
            self._lattice_params.enable()
            self._lattice_params.set("1, 2")
            self._lattice_params.label_widget.config(text="xsi, eta")
        elif lattice == "rhombic":
            self._lattice_params.enable()
            self._lattice_params.set("2")
            self._lattice_params.label_widget.config(text="b")
        elif lattice == "rectangular":
            self._lattice_params.enable()
            self._lattice_params.set("2")
            self._lattice_params.label_widget.config(text="L")
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
    # >>>2

    def make_matrix(self):       # <<<2
        M = self.matrix

        if (self.current_tab == "rosette"):
            p = self.rotational_symmetry
            try:
                keys = list(M.keys())
                for (n, m) in keys:
                    if (n-m) % p != 0 or n == m:
                        del M[(n, m)]
            except Exception as err:
                error("problem while adding '{}'-fold symmetry "
                      "to the matrix: {}"
                      .format(p, err))
                return

        M = add_symmetries_to_matrix(M, self.pattern)
        self.change_matrix(M)
    # >>>2

    def get_config(self):           # <<<2
        return {
                "matrix": str(self.matrix).replace(" ", ""),
                "random_nb_coeff": self._random_nb_coeff.get(),
                "random_degre": (self._random_min_degre.get(),
                                 self._random_max_degre.get()),
                "random_coeff": (self._random_min_coeff.get(),
                                 self._random_max_coeff.get()),
                "random_noise": self._noise.get(),
                "tab": self.current_tab,
                "wallpaper_type": self._wallpaper_type.get(),
                "lattice_parameters": self._lattice_params.get(),
                "frieze_type": self._frieze_type.get(),
                "rosette": self.rosette,
                "rosette_rotation": self._rosette_rotation.get(),
                "raw_basis": [self._basis_matrix1.get(),
                              self._basis_matrix2.get()],
                "raw_rotation": self._raw_rotation.get(),
                }
    # >>>2

    def set_config(self, cfg):      # <<<2
        if "matrix" in cfg:
            self.matrix = parse_matrix(cfg["matrix"])
        if "random_nb_coeff" in cfg:
            self._random_nb_coeff.set(cfg["random_nb_coeff"])
        if "random_degre" in cfg:
            self._random_min_degre.set(cfg["random_degre"][0])
            self._random_max_degre.set(cfg["random_degre"][1])
        if "random_coeff" in cfg:
            self._random_min_coeff.set(cfg["random_coeff"][0])
            self._random_max_coeff.set(cfg["random_coeff"][1])
        if "random_noise" in cfg:
            self._noise.set(cfg["random_noise"])
        if "tab" in cfg:
            if cfg["tab"] == "wallpaper":
                self._tabs.select(0)
            elif cfg["tab"] == "frieze":
                self._tabs.select(1)
            elif cfg["tab"] == "raw":
                self._tabs.select(2)
            else:
                self._tabs.select(0)
        if "wallpaper_type" in cfg:
            for i in range(len(WALLPAPER_TYPES)):
                if re.search("\\b{}\\b".format(cfg["wallpaper_type"]),
                             WALLPAPER_TYPES[i]):
                    self._wallpaper_combo.current(i)
        if "lattice_parameters" in cfg:
            self._lattice_params.set(floats_to_str(cfg["lattice_parameters"]))
        if "frieze_type" in cfg:
            for i in range(len(FRIEZE_TYPES)):
                if re.search("\\b{}\\b".format(cfg["frieze_type"]),
                             FRIEZE_TYPES[i]):
                    self._frieze_combo.current(i)
        if "rosette" in cfg:
            self._rosette.set(cfg["rosette"])
        if "rosette_rotation" in cfg:
            self._rosette_rotation.set(cfg["rosette_rotation"])
        if "raw_basis" in cfg:
            self._basis_matrix1.set(floats_to_str(cfg["raw_basis"][0]))
            self._basis_matrix2.set(floats_to_str(cfg["raw_basis"][1]))
        if "raw_rotation" in cfg:
            self._raw_rotation.set(cfg["raw_rotation"])
    # >>>2
# >>>1


class CreateSymmetry(Tk):      # <<<1

    def __init__(self,      # <<<2
                 matrix=None,
                 color_filename=None,
                 size=(OUTPUT_WIDTH, OUTPUT_HEIGHT),
                 output_filename="output-{:03}",
                 modulus=1.0,
                 angle=0.0,
                 geometry=(-2, 2, -2, 2),
                 color_modulus=1.0,
                 color_angle=0.0,
                 color_geometry=COLOR_GEOMETRY,
                 default_color="black",
                 tab="",
                 pattern=None,
                 params=None
                 ):

        # tk interface
        Tk.__init__(self)
        self.resizable(width=False, height=False)
        # self.geometry("1200x600")
        self.title("Create Symmetry")

        # s = Style()
        # s.configure("TFrame", background="red")
        # s.configure("TLabel", background="green")
        # s.configure("TEntry", background="yellow")
        # s.configure("TButton", background="blue")

        # components    <<<3
        self.colorwheel = ColorWheel(self,
                                     filename=color_filename,
                                     geometry=color_geometry,
                                     modulus=color_modulus,
                                     angle=color_angle,
                                     default_color=default_color)

        self.world = World(self,
                           geometry=geometry,
                           modulus=modulus,
                           angle=angle,
                           filename_template=output_filename)

        self.function = Function(self, matrix=matrix, tab=tab,
                                 pattern=pattern, pattern_params=params)

        self.colorwheel.grid(row=0, column=0, sticky=N+S, padx=10, pady=10)
        self.world.grid(row=0, column=1, sticky=N+S, padx=10, pady=10)
        self.function.grid(row=1, column=1, sticky=E, padx=10, pady=10)

        self._console = Text(self, width=1, height=1,
                             background="black", foreground="white",
                             font="TkFixedFont",
                             borderwidth=3,
                             relief="ridge")
        self._console.grid(row=1, column=0, sticky=E+W+N+S, padx=10, pady=10)
        self._console.config(state=DISABLED)
        self._nb_pending = Label(self)
        self._nb_pending.grid(row=1, column=0, sticky=E+S, padx=10, pady=10)

        # self.function.new_random_matrix()
        # cfg = self.function.get_config()
        # import json
        # print(json.dumps(cfg, separators=(",", ":")))
        # >>>3

        # attach appropriate actions to buttons     <<<3
        self.world._preview_button.config(command=sequence(self.make_preview))
        self.world._save_button.config(command=sequence(self.make_output))
        # >>>3

        # keybindings       <<<3
        self.bind("<Control-h>", sequence(self.display_help))
        self.bind("?", sequence(self.display_help))
        self.bind("<F1>", sequence(self.display_help))

        self.bind("<Control-q>", sequence(self.destroy))

        self.bind("<Control-p>", sequence(self.make_preview))
        self.bind("<Control-s>", sequence(self.make_output))

        self.bind("<Control-n>", sequence(self.function.add_noise))
        self.bind("<Control-N>", sequence(self.function.add_noise,
                                          self.function.make_matrix,
                                          self.make_preview))

        self.bind("<Control-g>", sequence(self.function.new_random_matrix))
        self.bind("<Control-G>", sequence(self.function.new_random_matrix,
                                          self.function.make_matrix,
                                          self.make_preview))

        self.bind("<Control-Key-minus>", sequence(self.world.zoom_out,
                                                  self.make_preview))
        self.bind("<Control-Key-plus>", sequence(self.world.zoom_in,
                                                 self.make_preview))
        # >>>3

        self.output_queue = Queue()
        self.message_queue = multiprocessing.Queue()
        self.output_running = False

        self.message_queue.put("""  create_symmetry.py
 Control-h for shortcuts
-------------------------
""")
        self.show_messages()
    # >>>2

    def show_messages(self):        # <<<2
        self._console.config(state=NORMAL)
        while not self.message_queue.empty():
            self._console.insert(END, self.message_queue.get(0) + "\n")
        self._console.yview(END)
        self._console.config(state=DISABLED)
        self.after(100, self.show_messages)
        if self.output_running:
            self._nb_pending.grid()
            self._nb_pending.config(text="{} pending tasks"
                                         .format(1+self.output_queue.qsize()))
        else:
            self._nb_pending.grid_remove()
    # >>>2

    def process_output(self):       # <<<2
        """thread to create background processes for the output"""
        if not self.output_running:
            threading.Thread(target=self.process_pending_jobs).start()
    # >>>2

    def process_pending_jobs(self):     # <<<2
        """generate background processes for the pending image generation"""
        self.output_running = True
        while not self.output_queue.empty():
            params = self.output_queue.get(0)
            params["message_queue"] = self.message_queue
            p = multiprocessing.Process(target=self.background_output,
                                        kwargs=params)
            p.start()
            p.join()
        message("output queue empty")
        self.output_running = False
    # >>>2

    def display_help(self):     # <<<2
        dialog = Toplevel(self)
        dialog.resizable(width=False, height=False)

        text = Text(dialog)
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
  Control-G     generate random matrix, add symmetries and display preview

  Control--     zoom out the result file and display preview
  Control-+     zoom in the result file and display preview
""")
        text.config(state=DISABLED)

        dialog.bind("<Escape>", lambda _: dialog.destroy())
        dialog.bind("<Control-q>", lambda _: dialog.destroy())
        ok = Button(dialog, text="OK",
                    command=lambda: dialog.destroy())
        ok.pack(padx=10, pady=10)
        ok.focus_set()
        self.wait_window(dialog)
    # >>>2

    def get_image_parameters(self):      # <<<2
        geometry = self.world.geometry
        modulus = self.world.modulus
        angle = self.world.angle

        color_geometry = self.colorwheel.geometry
        color_mod = self.colorwheel.modulus
        color_ang = self.colorwheel.angle

        default_color = self.colorwheel.color

        lattice = self.function.current_tab
        pattern = self.function.pattern
        lattice_params = self.function.lattice_parameters

        matrix = self.function.matrix
        if not matrix:
            raise Error("missing parameter: matrix")

        if not self.colorwheel.filename:
            raise Error("missing parameter: colorwheel")

        pattern = self.function.pattern
        params = ""
        if lattice == "wallpaper":
            params = self.function.lattice_parameters
        elif lattice == "frieze":
            params = self.function.rotational_symmetry
        elif lattice == "raw":
            B = ",".join(map(str, self.function._basis_matrix1.get() +
                                  self.function._basis_matrix2.get()))
            params = B

        return {
                "matrix": matrix,
                "color_filename": self.colorwheel.filename,
                "geometry": geometry,
                "modulus": modulus,
                "angle": angle,
                "lattice": lattice,
                "lattice_matrix": self.function.lattice_matrix,
                "rotational_symmetry": self.function.rotational_symmetry,
                "color_geometry": color_geometry,
                "color_modulus": color_mod,
                "color_angle": color_ang,
                "default_color": default_color,
                "pattern": pattern,
                "params": params
                }
    # >>>2

    def make_preview(self, *args):      # <<<2

        ratio = self.world.width / self.world.height
        if ratio > 1:
            width = PREVIEW_SIZE
            height = round(PREVIEW_SIZE / ratio)
        else:
            width = round(PREVIEW_SIZE * ratio)
            height = PREVIEW_SIZE

        try:
            params = self.get_image_parameters()
            params["size"] = (width, height)

            image = make_world(**params)

            # FIXME: methode change_preview in World class
            self.world._canvas.tk_img = PIL.ImageTk.PhotoImage(image)
            self.world._canvas.delete(self.world._image_id)
            self.world._image_id = self.world._canvas.create_image(
                            (PREVIEW_SIZE//2, PREVIEW_SIZE//2),
                            image=self.world._canvas.tk_img)
        except Error as e:
            self.message_queue.put("* {}".format(e))
    # >>>2

    def make_output(self, *args):      # <<<2
        width = self.world.width
        height = self.world.height

        params = self.get_image_parameters()
        params["size"] = (width, height)
        params["filename_template"] = self.world.filename_template

        self.output_queue.put(params)
        self.process_output()

    def background_output(self, message_queue=None, **params):

        filename_template = params.pop("filename_template")

        image = make_world(queue=self.message_queue, **params)

        nb = 1
        while True:
            filename = filename_template.format(nb)
            if (not os.path.exists(filename+".jpg") and
                    not os.path.exists(filename+".sh")):
                break
            nb += 1
        image.save(filename + ".jpg")
        if message_queue is not None:
            message_queue.put("saved file {}".format(filename+".jpg"))

        style = "--{}={} \\\n            --params={}".format(
                params["lattice"],
                params["pattern"],
                str(params["params"]).strip("()").replace(" ", "")
                )
        for k in params:
            params[k] = str(params[k]).strip("()").replace(" ", "")
        cmd = ("""#!/bin/sh
CREATE_SYM={prog_path:}

$CREATE_SYM --color={color_filename:} \\
            --color-geometry={color_geometry:} \\
            --color-modulus={color_modulus:} \\
            --color-angle={color_angle:} \\
            --geometry={geometry:} \\
            --modulus={modulus:} \\
            --angle={angle:} \\
            --size={size:} \\
            --matrix='{matrix:}' \\
            {style:} \\
            --output={output:} \\
            $@
""".format(
           prog_path=os.path.abspath(sys.argv[0]),
           output=filename,
           style=style,
           **params
           ))

        cs = open(filename + ".sh", mode="w")
        cs.write(cmd)
        cs.close()
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

    -v  /  -verbose                     add information messages
    -h  /  --help                       this message
""")

    # parsing the command line arguments
    short_options = "hc:o:s:g:v"
    long_options = [
            "help",
            "color=", "color-geometry=", "color-modulus=", "color-angle=",
            "output=", "size=", "geometry=", "modulus=", "angle=",
            "matrix=", "rotation-symmetry=",
            "wallpaper=", "frieze=", "rosette=", "raw=", "params=",
            "verbose"]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(-1)

    if len(sys.argv) == 1:
        CreateSymmetry().mainloop()
        return

    output_filename = "output.jpg"
    color_filename = None
    width, height = 400, 400
    x_min, x_max, y_min, y_max = -2, 2, -2, 2
    modulus = 1
    angle = 0
    color_x_min, color_x_max, color_y_min, color_y_max = -1, 1, -1, 1
    color_modulus = 1
    color_angle = 0
    matrix = {}
    rotational_symmetry = 1
    tab = None
    pattern = None
    params = None
    global verbose
    for o, a in opts:
        if o in ["-h", "--help"]:
            display_help()
            sys.exit(0)
        elif o in ["-c", "--color"]:
            color_filename = a
        elif o in ["-o", "--output"]:
            output_filename = a
        elif o in ["-s", "--size"]:
            try:
                tmp = map(int, a.split(","))
                width, height = tmp
            except:
                error("problem with size '{}'".format(a))
                width, height = 400, 400
        elif o in ["-g", "--geometry"]:
            try:
                tmp = map(float, a.split(","))
                x_min, x_max, y_min, y_max = tmp
            except:
                error("problem with geometry '{}' for output".format(a))
                x_min, x_max, y_min, y_max = -2, 2, -2, 2
                sys.exit(1)
        elif o in ["--rotation-symmetry"]:
            try:
                rotational_symmetry = int(a)
            except:
                error("problem with rotational symmetry '{}'".format(a))
        elif o in ["--modulus"]:
            try:
                modulus = float(a)
            except:
                error("problem with modulus '{}'".format(a))
        elif o in ["--angle"]:
            try:
                angle = float(a)
            except:
                error("problem with angle '{}'".format(a))
        elif o in ["--color-geometry"]:
            try:
                tmp = map(float, a.split(","))
                color_x_min, color_x_max, color_y_min, color_y_max = tmp
            except:
                error("problem with geometry '{}' for color image".format(a))
                color_x_min, color_x_max, color_y_min, color_y_max = -1, 1, -1, 1
                sys.exit(1)
        elif o in ["--color-modulus"]:
            try:
                color_modulus = float(a)
            except:
                error("problem with modulus '{}'".format(a))
        elif o in ["--color-angle"]:
            try:
                color_angle = float(a)
            except:
                error("problem with angle '{}'".format(a))
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
        elif o in ["-v", "--verbose"]:
            verbose += 1
        elif o in ["--matrix"]:
            matrix = parse_matrix(a)
        else:
            assert False

    CreateSymmetry(
            matrix=matrix,
            color_filename=color_filename,
            size=(width, height),
            geometry=(x_min, x_max, y_min, y_max),
            modulus=modulus,
            angle=angle,
            color_geometry=(color_x_min, color_x_max,
                            color_y_min, color_y_max),
            color_modulus=color_modulus,
            color_angle=color_angle,
            default_color="black",
            tab=tab,
            pattern=pattern,
            params=params
            ).mainloop()

# >>>1


if __name__ == "__main__":
    main()

# vim: textwidth=0 foldmarker=<<<,>>> foldmethod=marker foldlevel=0
