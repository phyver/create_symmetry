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

# math
from cmath import exp
from math import sqrt, pi, sin, cos
from random import randint, uniform, shuffle
# >>>1

verbose = 0
PREVIEW_SIZE = 500
OUTPUT_WIDTH = 1280
OUTPUT_HEIGHT = 960
COLOR_SIZE = 200
COLOR_GEOMETRY = (-1., 1., -1., 1.)
WORLD_GEOMETRY = (-2., 2., -2., 2.)


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
def error(s):
    """print string ``s`` on stderr"""
    print("*** " + s, file=sys.stderr)


def sequence(*fs):
    def res(*args):
        for f in fs:
            f()
    return res
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
    if pattern in ["o", "p1", "2222", "p2"]:
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
        error("unkwnow pattern type: '{}'".format(pattern))

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
        error("Unknown pattern type: {}".format(pattern))
        sys.exit(1)
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
        lattice="plain",                # "frieze", "rosette", "general",
                                        # "rhombic", "rectangular", "square"
                                        # or "hexagonal"
        lattice_params=(),              # (xsi,eta) for "general", (b) for
                                        # "rhombic", (L) for "rectangular",
                                        # () for other lattices
        default_color="black"
        ):

    assert matrix is not None
    assert color_filename != ""
    assert lattice in ["frieze", "rosette", "general", "rhombic",
                       "rectangular", "square", "hexagonal", "plain"]

    if lattice == "general":
        xsi, eta = lattice_params
        E = [[1, -xsi/eta], [0, 1/eta]]
        p_rot = 1
    elif lattice == "rhombic":
        b = lattice_params
        E = [[1, 1/(2*b)], [1, -1/(2*b)]]
        p_rot = 1
    elif lattice == "rectangular":
        L = lattice_params
        E = [[2, 0], [0, 1/L]]
        p_rot = 1
    elif lattice == "square":
        E = [[1, 0], [0, 1]]
        p_rot = 4
    elif lattice == "hexagonal":
        E = [[1, 1/sqrt(3)], [0, 2/sqrt(3)]]
        p_rot = 3
    else:
        E = None

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
        else:   # E should be a 2x2 array
            ZS = np.zeros((width, height), complex)
            for k in range(0, p_rot):
                _tmp = zs * complex(cos(2*pi*k/p_rot), sin(2*pi*k/p_rot))
                _xs = _tmp.real
                _ys = _tmp.imag
                _tmp = (n*(E[0][0]*_xs + E[0][1]*_ys) +
                        m*(E[1][0]*_xs + E[1][1]*_ys))
                ZS += np.exp(2j*pi*_tmp)
            ZS = ZS / p_rot
            res = res + matrix[(n, m)] * ZS
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

    return PIL.Image.fromarray(res, "RGB")
# >>>1


###
# GUI
class LabelEntry(Frame):  # <<<1
    """
    An Entry widget with a label on its left.
    """
    entry_widget = None  # the Entry widget
    label_widget = None  # the Label widget
    content = None  # the corresponding StringVar / IntVar / BoolVar
    __init = ""

    def __init__(self, parent, label, on_click=None,  # <<<3
                 value="",
                 state=NORMAL, **kwargs):
        Frame.__init__(self, parent)

        if label:
            self.label_widget = Label(self, text=label)
            self.label_widget.pack(side=LEFT, padx=(0, 5))

        self.__init = value
        if isinstance(value, int):
            self.content = IntVar()
            self.content.set(value)
        elif isinstance(value, float):
            self.content = StringVar()
            self.content.set(float(value))
        elif isinstance(value, bool):
            self.content = BoolVar()
            self.content.set(value)
        else:
            self.content = StringVar("")
            self.content.set(value)
        self.entry_widget = Entry(self, textvar=self.content,
                                  state=state, **kwargs)
        self.entry_widget.pack(side=LEFT)

        for method in ["config", "configure", "bind", "focus_set"]:
            setattr(self, method, getattr(self.entry_widget, method))
    # >>>3

    def set(self, s):  # <<<3
        if s is None:
            self.content.set("")
        else:
            self.content.set(s)
    # >>>3

    def get(self):  # <<<3
        s = self.content.get()
        try:
            if isinstance(self.__init, int):
                return int(s)
            elif isinstance(self.__init, float):
                return float(s)
            elif isinstance(self.__init, bool):
                return bool(s)
            else:
                return s
        except Exception as e:
            error("cannot convert value of field '{}': {}".format(s, e))
    # >>>3

    def delete(self):  # <<<3
        self.content.set("")
    # >>>3

    def disable(self):  # <<<3
        self.entry_widget.config(state=DISABLED)
        self.label_widget.config(state=DISABLED)
    # >>>3

    def enable(self):  # <<<3
        self.entry_widget.config(state=NORMAL)
        self.label_widget.config(state=NORMAL)
    # >>>3
# >>>1


class ColorWheel(LabelFrame):   # <<<1

    @property
    def geometry(self): # <<<2
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
        try:
            return getrgb(self._color.get())
        except Exception as e:
            error("'{}' is not a color".format(e))
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
                                 width=10)
        self._color.grid(row=0, column=0, padx=5, pady=5)
        self._color.bind("<Enter>", self.update_defaultcolor)
        self._color.bind("<FocusOut>", self.update_defaultcolor)

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

        Button(self, text="choose file",
               command=self.choose_colorwheel).grid(row=3, column=0, padx=5, pady=5)

        coord_frame = LabelFrame(self, text="coordinates")
        coord_frame.grid(row=4, column=0, sticky=E+W, padx=5, pady=5)
        coord_frame.columnconfigure(0, weight=1)
        coord_frame.columnconfigure(1, weight=1)

        self._x_min = LabelEntry(coord_frame, label="x min",
                                 value=float(geometry[0]),
                                 width=4, justify=RIGHT)
        self._x_min.grid(row=0, column=0, padx=5, pady=5)

        self._x_max = LabelEntry(coord_frame, label="x max",
                                 value=float(geometry[1]),
                                 width=4, justify=RIGHT)
        self._x_max.grid(row=0, column=1, padx=5, pady=5)

        self._y_min = LabelEntry(coord_frame, label="y min",
                                 value=float(geometry[2]),
                                 width=4, justify=RIGHT)
        self._y_min.grid(row=1, column=0, padx=5, pady=5)

        self._y_max = LabelEntry(coord_frame, label="y max",
                                 value=float(geometry[3]),
                                 width=4, justify=RIGHT)
        self._y_max.grid(row=1, column=1, padx=5, pady=5)

        Button(coord_frame, text="reset",
               command=self.reset_geometry).grid(row=2, column=0, columnspan=2,
                                                 padx=5, pady=5)

        transformation_frame = LabelFrame(self, text="transformation")
        transformation_frame.grid(row=5, column=0, sticky=E+W, padx=5, pady=5)
        self._modulus = LabelEntry(transformation_frame, label="modulus",
                                   value=float(modulus),
                                   width=4)
        self._modulus.pack(padx=5, pady=5)

        self._angle = LabelEntry(transformation_frame, label="angle (°)",
                                 value=float(angle),
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

    def choose_colorwheel(self):    # <<<2
        filename = filedialog.askopenfilename(
                title="Create Symmetry: choose color wheel image",
                initialdir="./",
                filetypes=[("images", "*.jpg *.jpeg *.png"), ("all", "*.*")])
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
                                 value=float(geometry[0]),
                                 width=4, justify=RIGHT)
        self._x_min.grid(row=0, column=0, padx=5, pady=5)

        self._x_max = LabelEntry(coord_frame, label="x max",
                                 value=float(geometry[1]),
                                 width=4, justify=RIGHT)
        self._x_max.grid(row=0, column=1, padx=5, pady=5)

        self._y_min = LabelEntry(coord_frame, label="y min",
                                 value=float(geometry[2]),
                                 width=4, justify=RIGHT)
        self._y_min.grid(row=1, column=0, padx=5, pady=5)

        self._y_max = LabelEntry(coord_frame, label="y max",
                                 value=float(geometry[3]),
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
                                   value=float(modulus),
                                   width=4)
        self._modulus.pack(padx=5, pady=5)

        self._angle = LabelEntry(transformation_frame, label="angle (°)",
                                 value=float(angle),
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
                                 width=6, justify=RIGHT)
        self._width.pack(padx=5, pady=5)

        self._height = LabelEntry(settings_frame,
                                  label="height", value=OUTPUT_HEIGHT,
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
# >>>1


class Function(LabelFrame):     # <<<1

    @property
    def current_tab(self):      # <<<2
        if ("wallpaper" in self._tabs.tab(self._tabs.select(), "text")):
            return "wallpaper"
        elif ("frieze" in self._tabs.tab(self._tabs.select(), "text")):
            return "frieze"
        else:
            assert False
    # >>>2

    @property
    def rosette(self):          # <<<2
        return self._rosette.get()
    # >>>2

    @property
    def rotational_symmetry(self):      # <<<2
        return int(self._rotational_symmetry.get())
    # >>>2

    @property
    def pattern(self):          # <<<2
        if self.current_tab == "frieze":
            return self._frieze_type.get().split()[0]
        if self.current_tab == "wallpaper":
            return self._wallpaper_type.get().split()[0]
        else:
            assert False
    # >>>2

    @property
    def lattice_parameters(self):       # <<<2
        lattice = lattice_type(self.pattern)
        lattice_params = ()

        s = self._lattice_params.get()
        try:
            if lattice == "general":
                xsi, eta = s.split(",")
                lattice_params = (float(xsi), float(eta))
            elif lattice == "rhombic":
                b = s
                lattice_params = float(b)
            elif lattice == "rectangular":
                L = s
                lattice_params = float(L)
        except Exception as e:
            error("error while getting lattice parameters '{}': {}"
                  .format(s, e))
        return lattice_params
    # >>>2

    def __init__(self, root, matrix=None):      # <<<2

        LabelFrame.__init__(self, root)
        self.configure(text="Function")

        # display matrix    <<<3
        tmp = LabelFrame(self, text="matrix")
        tmp.grid(row=0, column=0, rowspan=2, sticky=N+S,  padx=5, pady=5)

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
        self._change_entry = LabelEntry(tmp, label="change entry", value="", width=17, font="TkFixedFont")
        self._change_entry.pack(padx=5, pady=5)
        self._change_entry.bind("<Return>", self.add_entry)
        # >>>3

        # random matrix     <<<3
        tmp = LabelFrame(self, text="random matrix")
        tmp.grid(row=0, column=1, sticky=N+S, padx=5, pady=5)

        self._random_nb_coeff = LabelEntry(tmp, label="nb coefficients",
                                           value=3, width=4)
        self._random_nb_coeff.pack(padx=5, pady=5)

        self._random_min_degre = LabelEntry(tmp, label="min degre",
                                            value=-6, width=4)
        self._random_min_degre.pack(padx=5, pady=5)

        self._random_max_degre = LabelEntry(tmp, label="max degre",
                                            value=6, width=4)
        self._random_max_degre.pack(padx=5, pady=5)

        self._random_min_coeff = LabelEntry(tmp, label="min coefficient",
                                            value=float(-.1), width=4)
        self._random_min_coeff.pack(padx=5, pady=5)

        self._random_max_coeff = LabelEntry(tmp, label="max coefficient",
                                            value=float(.1), width=4)
        self._random_max_coeff.pack(padx=5, pady=5)

        Button(tmp, text="generate", command=self.new_random_matrix).pack(padx=5, pady=5)
        # >>>3

        # add noise <<<3
        tmp3 = Frame(tmp)
        tmp3.pack(padx=5, pady=5)
        self._noise = LabelEntry(tmp3, label="(%)", value=10, width=3)
        self._noise.pack(side=RIGHT, padx=5, pady=5)
        self._noise.bind("<Return>", self.add_noise)

        Button(tmp3, text="random noise", command=self.add_noise).pack(side=LEFT, padx=5, pady=5)
        # >>>3


        # tabs for the different kinds of functions / symmetries
        self._tabs = Notebook(self)
        self._tabs.grid(row=0, column=2, rowspan=2, sticky=N+S, padx=5, pady=5)

        wallpaper_tab = Frame(self._tabs)
        self._tabs.add(wallpaper_tab, text="wallpaper")

        frieze_tab = Frame(self._tabs)
        self._tabs.add(frieze_tab, text="frieze")

        raw_tab = Frame(self._tabs)
        self._tabs.add(raw_tab, text="raw")

        self._tabs.select(0)  # select wallpaper tab

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
                                          value="1,1", width=7)
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

        self._rotational_symmetry = LabelEntry(frieze_tab,
                                               label="symmetries",
                                               value=5,
                                               width=2)
        self._rotational_symmetry.pack(padx=5, pady=5)

        Button(frieze_tab, text="make matrix",
               command=self.make_matrix).pack(side=BOTTOM, padx=5, pady=5)
        # # >>>3

        # raw tab   <<<3
        Label(raw_tab, text="TODO").pack(padx=5, pady=5)
        # >>>3

        # make sure the layout reflects the selected options
        self.select_wallpaper()
        self.set_rosette()

        # self._wallpaper_combo.current(9)
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
            self._rotational_symmetry.enable()
        else:
            self._rotational_symmetry.disable()
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

        if (self.current_tab == "frieze" and self.rosette):
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
                 default_color="black"):

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

        self.function = Function(self, matrix=matrix)

        self.colorwheel.grid(row=0, column=0, sticky=N+S, padx=10, pady=10)
        self.world.grid(row=0, column=1, sticky=N+S, padx=10, pady=10)
        self.function.grid(row=1, column=0, columnspan=2, sticky=E+W, padx=10, pady=10)
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
        self.bind("<Control-N>", sequence())

        self.bind("<Control-g>", sequence(self.function.new_random_matrix))
        self.bind("<Control-G>", sequence(self.function.new_random_matrix,
                                          self.function.make_matrix,
                                          self.make_preview))

        self.bind("<Control-Key-minus>", sequence(self.world.zoom_out,
                                                  self.make_preview))
        self.bind("<Control-Key-plus>", sequence(self.world.zoom_in,
                                                 self.make_preview))
        # >>>3
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

    def make_image(self, width, height, filename="output.jpg"):      # <<<2
        geometry = self.world.geometry
        modulus = self.world.modulus
        angle = self.world.angle

        color_geometry = self.colorwheel.geometry
        color_mod = self.colorwheel.modulus
        color_ang = self.colorwheel.angle

        default_color = self.colorwheel.color

        if self.function.current_tab == "frieze":
            pattern = self.function.pattern
            if self.function.rosette:
                lattice = "rosette"
            else:
                lattice = "frieze"
        elif self.function.current_tab == "wallpaper":
            pattern = self.function.pattern
            lattice = lattice_type(pattern)
        else:
            assert False

        lattice_params = self.function.lattice_parameters

        matrix = self.function.matrix

        image = make_world(
                    matrix=matrix,
                    color_filename=self.colorwheel.filename,
                    size=(width, height),
                    geometry=geometry,
                    modulus=modulus,
                    angle=angle,
                    lattice=lattice,
                    lattice_params=lattice_params,
                    color_geometry=color_geometry,
                    color_modulus=color_mod,
                    color_angle=color_ang,
                    default_color=default_color)

        cmd = ("""#!/bin/sh
CREATE_SYM={prog_path:}

$CREATE_SYM --color={color:} \\
            --color-geometry={color_geometry:} \\
            --color-modulus={color_mod:} \\
            --color-angle={color_ang:} \\
            --geometry={geometry:} \\
            --modulus={modulus:} \\
            --angle={angle:} \\
            --size={width:},{height:} \\
            --matrix='{matrix:}' \\
            --output={output:} \\
            $@
""".format(cwd=os.getcwd(),
           prog_path=os.path.abspath(sys.argv[0]),
           color=self.colorwheel.filename,
           color_geometry=str(color_geometry).strip("()"),
           color_mod=color_mod,
           color_ang=color_ang,
           geometry=str(geometry).strip("()"),
           modulus=modulus,
           angle=angle,
           width=width,
           height=height,
           matrix=str(self.function.matrix),
           output=filename
           ))
        return image, cmd
    # >>>2

    def make_preview(self, *args):      # <<<2

        ratio = self.world.width / self.world.height
        if ratio > 1:
            width = PREVIEW_SIZE
            height = round(PREVIEW_SIZE / ratio)
        else:
            width = round(PREVIEW_SIZE * ratio)
            height = PREVIEW_SIZE

        preview_image, _ = self.make_image(width, height)

        # FIXME: methode change_preview in World class
        self.world._canvas.tk_img = PIL.ImageTk.PhotoImage(preview_image)
        self.world._canvas.delete(self.world._image_id)
        self.world._image_id = self.world._canvas.create_image(
                        (PREVIEW_SIZE//2, PREVIEW_SIZE//2),
                        image=self.world._canvas.tk_img)
    # >>>2

    def make_output(self, *args):      # <<<2
        width = self.world.width
        height = self.world.height

        filename_template = self.world.filename_template
        nb = 1
        while True:
            filename = filename_template.format(nb)
            if (not os.path.exists(filename+".jpg") and
                    not os.path.exists(filename+".sh")):
                break
            nb += 1

        output_image, cmd = self.make_image(width, height, filename + ".jpg")

        output_image.save(filename + ".jpg")
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

    -c FILE  /  --color=FILE            choose color file
    -o FILE  /  --output=FILE           choose output file
    -s W,H  /  --size=W,H               choose width and height of output
    -g X,Y,X,Y  /  --geometry=X,Y,X,Y   choose "geometry of output"
    --modulus  /  --angle               transformation to apply to the result
    --color-geometry=X,Y,X,Y            choose "geometry" of the color file
    --color-modulus  /  --color-angle   transformation to apply to the colorwheel
    --matrix=...                        transformation matrix

    --gui                               use GUI instead of CLI
                                        (default when no flag is present)

    -v  /  -verbose                     add information messages
    -h  /  --help                       this message
""")

    # parsing the command line arguments
    short_options = "hc:o:s:g:v"
    long_options = [
            "help",
            "color=", "color-geometry=", "color-modulus=", "color-angle=",
            "output=", "size=", "geometry=", "modulus=", "angle=",
            "matrix=",
            "verbose", "gui"]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(-1)

    if len(sys.argv) == 1:
        CreateSymmetry().mainloop()
        # GUI().mainloop()
        return

    output_filename = "output.jpg"
    color_filename = None
    width, height = 400, 400
    x_min, x_max, y_min, y_max = -2, 2, -2, 2
    modulus=1
    angle=0
    color_x_min, color_x_max, color_y_min, color_y_max = -1, 1, -1, 1
    color_modulus=1
    color_angle=0
    matrix = {}
    gui = False
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
        elif o in ["-v", "--verbose"]:
            verbose += 1
        elif o in ["--matrix"]:
            matrix = parse_matrix(a)
        elif o in ["--gui"]:
            gui = True
        else:
            assert False

    # # M = { (1,0): 2 }
    # M = {
    #      (0, 1): .3,
    #      (1, -1): -.123,
    #      (3, 1): .4,
    #     }
    # # M = add_symmetries_to_matrix(M, "p211")
    # a = .7
    # b = -.3
    # M = {
    #      (1, 2): a,
    #      (1, -2): a,
    #      (3, 1): -b,
    #      (3, -1): -b,
    #      }
    # assert M == parse_matrix(str(M))

    if gui:
        CreateSymmetry(matrix=matrix,
        # GUI(matrix=matrix,
            color_filename=color_filename,
            size=(width, height),
            geometry=(x_min, x_max, y_min, y_max),
            modulus=modulus,
            angle=angle,
            color_geometry=(color_x_min, color_x_max,
                            color_y_min, color_y_max),
            color_modulus=color_modulus,
            color_angle=color_angle,
            default_color="black"
            ).mainloop()

    else:
        output_image = make_world(matrix=matrix,
                                  color_filename=color_filename,
                                  size=(width, height),
                                  geometry=(x_min, x_max, y_min, y_max),
                                  modulus=modulus,
                                  angle=angle,
                                  color_geometry=(color_x_min, color_x_max,
                                                  color_y_min, color_y_max),
                                  color_modulus=color_modulus,
                                  color_angle=color_angle,
                                  default_color="black")
        output_image.save(output_filename)
        output_image.show()
# >>>1


if __name__ == "__main__":
    main()

# vim: textwidth=0 foldmarker=<<<,>>> foldmethod=marker foldlevel=0
