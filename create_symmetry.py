#!/usr/bin/env python3

###
# imports
# <<<1

# image (Pillow)
import PIL
import PIL.ImageTk
from PIL.ImageColor import getrgb

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
        "-- general lattice",
        "o (p1)",
        "2222 (p2)",
        "-- rhombic lattice",
        "*× (cm)",
        "2*22 (cmm)",
        "-- rectangular lattice",
        "** (pm)",
        "×× (pg)",
        "*2222 (pmm)",
        "22* (pmg)",
        "22× (pgg)",
        "-- square lattice",
        "442 (p4)",
        "*442 (p4m)",
        "4*2 (p4g)",
        "-- hexagonal lattice",
        "333 (p3)",
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
def make_world_numpy(                   # <<<1
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
    elif lattice == "rhombic":
        b = lattice_params
        E = [[1, 1/(2*b)], [1, -1/(2*b)]]
    elif lattice == "rectangular":
        L = lattice_params
        E = [[2, 0], [0, 1/L]]
    # elif lattice == "square":
    #     E = [[1, 0], [0, 1]]
    # elif lattice == "hexagonal":
    #     E = [[1, 1/sqrt(3)], [0, 2/sqrt(3)]]
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

    import numpy as np
    delta_x = (x_max-x_min) / (width-1)
    delta_y = (y_max-y_min) / (height-1)

    color_delta_x = (color_x_max-color_x_min) / (color_width-1)
    color_delta_y = (color_y_max-color_y_min) / (color_height-1)

    xs = np.arange(width)
    xs = x_min + xs*delta_x
    xs = xs / (modulus * complex(cos(angle*pi/180), sin(angle*pi/180)))
    # print("got xs")

    ys = np.arange(height)
    ys = y_max - ys*delta_y
    ys = ys / (modulus * complex(cos(angle*pi/180), sin(angle*pi/180)))
    # print("got ys")

    res = np.zeros((width, height), complex)
    # print("initialized res")
    for (n, m) in matrix:
        if lattice == "rosette" or lattice == "plain":
            zs = xs[:, None] + 1j*ys
            zcs = np.conj(zs)
            res = res + matrix[(n, m)] * zs**n * zcs**m
        elif lattice == "frieze":
            zs = xs[:, None] + 1j*ys
            zs = np.exp(1j * zs)
            zcs = np.conj(zs)
            res = res + matrix[(n, m)] * zs**n * zcs**m
        elif lattice == "square":
            zs = (np.exp(2j*pi*(n*xs[:, None] + m*ys)) +
                  np.exp(2j*pi*(m*xs[:, None] - n*ys)) +
                  np.exp(2j*pi*(-n*xs[:, None] - m*ys)) +
                  np.exp(2j*pi*(-m*xs[:, None] + n*ys))) / 4
            res = res + matrix[(n, m)] * zs
        elif lattice == "hexagonal":
            Xs = xs[:, None] + ys/sqrt(3)
            Ys = 2*ys / sqrt(3)
            zs = (np.exp(2j*pi*(n*Xs + m*Ys)) +
                  np.exp(2j*pi*(m*Xs - (n+m)*Ys)) +
                  np.exp(2j*pi*(-(n+m)*Xs + n*Ys))) / 3
            res = res + matrix[(n, m)] * zs
        else:   # E should be a 2x2 array
            zs = (n*(E[0][0]*xs[:, None] + E[0][1]*ys) +
                  m*(E[1][0]*xs[:, None] + E[1][1]*ys))
            res = res + matrix[(n, m)] * np.exp(2j*pi*zs)
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


def make_world_plain(                   # <<<1
        matrix=None,                        # the matrix of the transformation
        color_filename="",                  # image for the colorwheel image
        size=(OUTPUT_WIDTH, OUTPUT_HEIGHT),     # size of the output image
        geometry=(-2, 2, -2, 2),                # coordinates of the world
        modulus="1",
        angle="0",
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
    elif lattice == "rhombic":
        b = lattice_params
        E = [[1, 1/(2*b)], [1, -1/(2*b)]]
    elif lattice == "rectangular":
        L = lattice_params
        E = [[2, 0], [0, 1/L]]
    # elif lattice == "square":
    #     E = [[1, 0], [0, 1]]
    # elif lattice == "hexagonal":
    #     E = [[1, 1/sqrt(3)], [0, 2/sqrt(3)]]
    else:
        E = None

    if isinstance(default_color, str):
        default_color = getrgb(default_color)

    x_min, x_max, y_min, y_max = geometry
    color_x_min, color_x_max, color_y_min, color_y_max = color_geometry
    width, height = size

    tmp = PIL.Image.open(color_filename)
    border_size = 1
    color_im = PIL.Image.new("RGB",
                             (tmp.size[0]+2*border_size,
                              tmp.size[1]+2*border_size),
                             color=default_color)
    color_im.paste(tmp, (border_size, border_size))

    delta_x = (x_max-x_min) / (width-1)
    delta_y = (y_max-y_min) / (height-1)

    color_width, color_height = color_im.width, color_im.height
    color_delta_x = (color_x_max-color_x_min) / (color_width-1)
    color_delta_y = (color_y_max-color_y_min) / (color_height-1)

    out_im = PIL.Image.new("RGB", (width, height))
    pixels = out_im.load()
    for i in range(width):
        for j in range(height):
            x = x_min + i*delta_x
            y = y_max - j*delta_y
            x = x / (modulus * complex(cos(angle*pi/180), sin(angle*pi/180)))
            y = y / (modulus * complex(cos(angle*pi/180), sin(angle*pi/180)))
            res = 0
            for (n, m) in matrix:
                if lattice == "rosette" or lattice == "plain":
                    z = complex(x, y)
                    zc = z.conjugate()
                    res = res + matrix[(n, m)] * z**n * zc**m
                elif lattice == "frieze":
                    z = exp(E * 1j * z)
                    zc = z.conjugate()
                    res = res + matrix[(n, m)] * z**n * zc**m
                elif lattice == "square":
                    z = (exp(2j*pi*(n*x + m*y)) +
                         exp(2j*pi*(m*x - n*y)) +
                         exp(2j*pi*(-n*x - m*y)) +
                         exp(2j*pi*(-m*x + n*y))) / 4
                    res = res + matrix[(n, m)] * z
                elif lattice == "hexagonal":
                    X = x + y/sqrt(3)
                    Y = 2*y / sqrt(3)
                    z = (exp(2j*pi*(n*X + m*Y)) +
                         exp(2j*pi*(m*X - (n+m)*Y)) +
                         exp(2j*pi*(-(n+m)*X + n*Y))) / 3
                    res = res + matrix[(n, m)] * z
                else:   # E should be a 2x2 array
                    z = exp(2j*pi*(
                            n*(E[0][0]*x + E[0][1]*y) +
                            m*(E[1][0]*x + E[1][1]*y)
                            ))
                    res = res + matrix[(n, m)] * z

            res = res / (color_modulus *
                         complex(cos(color_angle*pi/180),
                                 sin(color_angle*pi/180)))
            res_x = round((res.real - color_x_min) / color_delta_x)
            res_y = round((color_y_max - res.imag) / color_delta_y)
            try:
                c = color_im.getpixel((res_x, res_y))
            except:
                c = default_color
            pixels[(i, j)] = c
    return out_im
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
        self._color.pack()
        self._color.bind("<Enter>", self.update_defaultcolor)
        self._color.bind("<FocusOut>", self.update_defaultcolor)

        self._filename = Label(self, text="...")
        self._filename.pack()

        self._canvas = Canvas(self, width=200, height=200, bg="white")
        self._canvas.pack()
        for i in range(5, COLOR_SIZE, 10):
            for j in range(5, COLOR_SIZE, 10):
                self._canvas.create_line(i-1, j, i+2, j, fill="gray")
                self._canvas.create_line(i, j-1, i, j+2, fill="gray")
        self._colorwheel_id = None
        self._canvas.bind("<Button-3>", self.set_origin)

        Button(self, text="choose file",
               command=self.choose_colorwheel).pack()

        coord_frame = LabelFrame(self, text="coordinates")
        coord_frame.pack()

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
                                                 padx=10, pady=10)

        transformation_frame = LabelFrame(self, text="transformation")
        transformation_frame.pack()
        self._modulus = LabelEntry(transformation_frame, label="modulus",
                                   value=float(modulus),
                                   width=4)
        self._modulus.pack()

        self._angle = LabelEntry(transformation_frame, label="angle (°)",
                                 value=float(angle),
                                 width=4)
        self._angle.pack()

        self.update_defaultcolor()

        if filename is not None:
            self.change_colorwheel(filename)
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
        if self._filename is not None:
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
        return self._filename_template()
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
        self._canvas.pack(side=LEFT)
        self._image_id = None
        # >>>3

        # geometry of result    <<<3
        coord_frame = LabelFrame(self, text="coordinates")
        coord_frame.pack()

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
                                           padx=10, pady=10)
        Button(coord_frame, text="zoom +",
               command=self.zoom_in).grid(row=3, column=1,
                                          padx=10, pady=10)

        transformation_frame = LabelFrame(self, text="transformation")
        transformation_frame.pack(padx=5, pady=5)
        self._modulus = LabelEntry(transformation_frame, label="modulus",
                                   value=float(modulus),
                                   width=4)
        self._modulus.pack()

        self._angle = LabelEntry(transformation_frame, label="angle (°)",
                                 value=float(angle),
                                 width=4)
        self._angle.pack()

        Button(coord_frame, text="reset",
               command=self.reset_geometry).grid(row=4, column=0, columnspan=2,
                                                 padx=10, pady=10)
        # >>>3

        # result settings       <<<3
        settings_frame = LabelFrame(self, text="output")
        settings_frame.pack(side=TOP, padx=5, pady=5)

        self._width = LabelEntry(settings_frame,
                                 label="width", value=OUTPUT_WIDTH,
                                 width=6, justify=RIGHT)
        self._width.pack()

        self._height = LabelEntry(settings_frame,
                                  label="height", value=OUTPUT_HEIGHT,
                                  width=6, justify=RIGHT)
        self._height.pack()

        self._filename_template = LabelEntry(settings_frame, label=None,
                                             value=filename_template,
                                             width=15)
        self._filename_template.pack()
        # >>>3

        tmp = LabelFrame(self, text="image")
        tmp.pack(padx=10, pady=10)

        self.preview_button = Button(tmp, text="preview", command=None)
        self.preview_button.pack()

        self.save_button = Button(tmp, text="save", command=None)
        self.save_button.pack()

        width, height = self.size
        if width > height:
            self.adjust_preview_X()
        else:
            self.adjust_preview_X()
    # >>>2

    def zoom_out(self, *args):
        a = 2**0.1
        for c in ["_x_min", "_x_max", "_y_min", "_y_max"]:
            self.__dict__[c].set(self.__dict__[c].get() * a)

    def zoom_in(self, *args):
        a = 2**0.1
        for c in ["_x_min", "_x_max", "_y_min", "_y_max"]:
            self.__dict__[c].set(self.__dict__[c].get() / a)

    def reset_geometry(self, *args):
        self._x_min.set(WORLD_GEOMETRY[0])
        self._x_max.set(WORLD_GEOMETRY[1])
        self._y_min.set(WORLD_GEOMETRY[2])
        self._y_max.set(WORLD_GEOMETRY[3])
        if self.width > self.height:
            self.adjust_preview_X()
        else:
            self.adjust_preview_X()

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


class GUI(Tk):      # <<<1

    colorwheel = {}     # form elements for the colorwheel:
    #  - tk_image to keep a reference to the TkImage object
    #  - image for the corresponding Image
    #  - display for the corresponding Canvas showing the image
    #  - x_min, x_max, y_min, y_max for the geometry of the image
    #  - default_color for the default color
    #  - filename for the displayed filename
    #  - full_filename for the real filename

    result = {}     # form elements for the result
    #  - tk_image to keep a reference to the TkImage object
    #  - image for the corresponding Image
    #  - display for the corresponding Canvas showing the image
    #  - x_min, x_max, y_min, y_max for the geometry of the image
    #  - width, height for the size of the final image
    #  - filename for the filename of saved images

    function = {}   # form element for the function
    #  - matrix for the matrix (dict) of coefficients
    #  - display for displaying the matrix
    #  - frieze_type for the frieze pattern type
    #  - rosette for the rosette boolean
    #  - nb_fold for the number of rotational symmetries for rosettes
    #  - wallpaper_type for the wallpaper pattern type
    #  - tabs for the notebook frieze / wallpaper

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

        self.init_colorwheel(filename=color_filename,
                             geometry=color_geometry,
                             modulus=color_modulus,
                             angle=color_angle,
                             default_color=default_color)
        self.init_result(geometry=geometry,
                         modulus=modulus,
                         angle=angle,
                         filename=output_filename)
        self.init_function(matrix=matrix)

        # keybindings
        self.bind("<Control-h>", lambda _: self.display_help())
        self.bind("?", lambda _: self.display_help())
        self.bind("<F1>", lambda _: self.display_help())

        self.bind("<Control-q>", lambda _: self.destroy())

        self.bind("<Control-p>", lambda _: self.make_preview())
        self.bind("<Control-s>", lambda _: self.make_result())

        # tmp = ColorWheel(self)
        # tmp.grid(row=0, column=5)
        # tmp = World(self)
        # tmp.grid(row=0, column=6)
    # >>>2

    def init_colorwheel(self,       # <<<2
                        filename=None,
                        geometry=(-1, 1, -1, 1),
                        modulus=1.0,
                        angle=0.0,
                        default_color="black"):
        frame = LabelFrame(self, text="Colorwheel")
        frame.grid(row=0, column=0, padx=10, pady=10)

        color = LabelEntry(frame, label="default color", value=default_color,
                           width=10)
        color.pack(padx=5, pady=10)
        self.colorwheel["default_color"] = color

        short_filename = Label(frame, text="...")
        short_filename.pack(side=TOP)
        self.colorwheel["filename"] = short_filename
        self.colorwheel["full_filename"] = ""

        canvas = Canvas(frame, width=200, height=200, bg="white")
        canvas.pack(side=TOP, padx=10, pady=10)
        for i in range(5, COLOR_SIZE, 10):
            for j in range(5, COLOR_SIZE, 10):
                canvas.create_line(i-1, j, i+2, j, fill="gray")
                canvas.create_line(i, j-1, i, j+2, fill="gray")
        self.colorwheel["display"] = canvas
        self.colorwheel["colorwheel_id"] = None

        Button(frame, text="choose file",
               command=self.choose_colorwheel).pack(side=TOP)

        coord_frame = LabelFrame(frame, text="coordinates")
        coord_frame.pack(side=TOP, padx=5, pady=20)

        x_min = LabelEntry(coord_frame, label="x min",
                           value=float(geometry[0]),
                           width=4, justify=RIGHT)
        x_min.grid(row=0, column=0, padx=5, pady=5)
        self.colorwheel["x_min"] = x_min

        x_max = LabelEntry(coord_frame, label="x max",
                           value=float(geometry[1]),
                           width=4, justify=RIGHT)
        x_max.grid(row=0, column=1, padx=5, pady=5)
        self.colorwheel["x_max"] = x_max

        y_min = LabelEntry(coord_frame, label="y min",
                           value=float(geometry[2]),
                           width=4, justify=RIGHT)
        y_min.grid(row=1, column=0, padx=5, pady=5)
        self.colorwheel["y_min"] = y_min

        y_max = LabelEntry(coord_frame, label="y max",
                           value=float(geometry[3]),
                           width=4, justify=RIGHT)
        y_max.grid(row=1, column=1, padx=5, pady=5)
        self.colorwheel["y_max"] = y_max

        def set_origin(event):
            x, y = event.x, event.y
            x_min = self.colorwheel["x_min"].get()
            x_max = self.colorwheel["x_max"].get()
            y_min = self.colorwheel["y_min"].get()
            y_max = self.colorwheel["y_max"].get()
            delta_x = x_max - x_min
            delta_y = y_max - y_min

            x_min = -x/COLOR_SIZE * delta_x
            x_max = x_min + delta_x
            y_max = y/COLOR_SIZE * delta_y
            y_min = y_max - delta_y
            self.colorwheel["x_min"].set(x_min)
            self.colorwheel["x_max"].set(x_max)
            self.colorwheel["y_min"].set(y_min)
            self.colorwheel["y_max"].set(y_max)
        canvas.bind("<Button-3>", set_origin)

        def zoom_out(*args):
            a = 2**0.1
            for c in ["x_min", "x_max", "y_min", "y_max"]:
                self.colorwheel[c].set(self.colorwheel[c].get() * a)

        def zoom_in(*args):
            a = 2**0.1
            for c in ["x_min", "x_max", "y_min", "y_max"]:
                self.colorwheel[c].set(self.colorwheel[c].get() / a)

        def reset_geometry(*args):
            if self.colorwheel["full_filename"] != "":
                self.change_colorwheel(self.colorwheel["full_filename"])
            else:
                self.colorwheel["x_min"].set(COLOR_GEOMETRY[0])
                self.colorwheel["x_max"].set(COLOR_GEOMETRY[1])
                self.colorwheel["y_min"].set(COLOR_GEOMETRY[2])
                self.colorwheel["y_max"].set(COLOR_GEOMETRY[3])

        # Button(coord_frame, text="zoom -",
        #        command=zoom_out).grid(row=2, column=0,
        #                               padx=10, pady=10)
        # Button(coord_frame, text="zoom +",
        #        command=zoom_in).grid(row=2, column=1,
        #                              padx=10, pady=10)

        Button(coord_frame, text="reset",
               command=reset_geometry).grid(row=2, column=0, columnspan=2,
                                            padx=10, pady=10)

        transformation_frame = LabelFrame(frame, text="transformation")
        transformation_frame.pack(padx=5, pady=5)
        modulus = LabelEntry(transformation_frame, label="modulus",
                             value=float(modulus),
                             width=4)
        modulus.pack(padx=5, pady=5)
        self.colorwheel["modulus"] = modulus

        angle = LabelEntry(transformation_frame, label="angle (°)",
                           value=float(angle),
                           width=4)
        angle.pack(padx=5, pady=5)
        self.colorwheel["angle"] = angle

        def update_defaultcolor(*args):
            try:
                c = getrgb(self.colorwheel["default_color"].get())
                self.colorwheel["display"].config(bg="#{:02x}{:02x}{:02x}"
                                                     .format(*c))
                self.colorwheel["default_color"].config(foreground="black")
            except Exception as e:
                error("error: '{}'".format(e))
                self.colorwheel["default_color"].config(foreground="red")

        color.bind("<Enter>", update_defaultcolor)
        color.bind("<FocusOut>", update_defaultcolor)
        update_defaultcolor()
        if filename is not None:
            self.change_colorwheel(filename)

    # >>>2

    def init_result(self, geometry=(-2, 2, -2, 2),     # <<<2
                    modulus=1.0, angle=0.0,
                    filename="output-{03:}"):
        frame = LabelFrame(self, text="World")
        frame.grid(row=0, column=1, padx=10, pady=10)

        # the preview image     <<<3
        canvas = Canvas(frame, width=PREVIEW_SIZE, height=PREVIEW_SIZE,
                        bg="white")
        for i in range(5, PREVIEW_SIZE, 10):
            for j in range(5, PREVIEW_SIZE, 10):
                canvas.create_line(i-1, j, i+2, j, fill="gray")
                canvas.create_line(i, j-1, i, j+2, fill="gray")
        canvas.pack(side=LEFT, padx=10, pady=10)
        self.result["display"] = canvas
        self.result["preview_id"] = None
        # >>>3

        # geometry of result    <<<3
        coord_frame = LabelFrame(frame, text="coordinates")
        coord_frame.pack(side=TOP, padx=5, pady=5)

        x_min = LabelEntry(coord_frame, label="x min",
                           value=float(geometry[0]),
                           width=4, justify=RIGHT)
        x_min.grid(row=0, column=0, padx=5, pady=5)
        self.result["x_min"] = x_min

        x_max = LabelEntry(coord_frame, label="x max",
                           value=float(geometry[1]),
                           width=4, justify=RIGHT)
        x_max.grid(row=0, column=1, padx=5, pady=5)
        self.result["x_max"] = x_max

        y_min = LabelEntry(coord_frame, label="y min",
                           value=float(geometry[2]),
                           width=4, justify=RIGHT)
        y_min.grid(row=1, column=0, padx=5, pady=5)
        self.result["y_min"] = y_min

        y_max = LabelEntry(coord_frame, label="y max",
                           value=float(geometry[3]),
                           width=4, justify=RIGHT)
        y_max.grid(row=1, column=1, padx=5, pady=5)
        self.result["y_max"] = y_max

        # Button(coord_frame, text="X to ratio",
        #        command=self.adjust_preview_X).grid(row=2, column=0,
        #                                            padx=10, pady=10)
        # Button(coord_frame, text="Y to ratio",
        #        command=self.adjust_preview_Y).grid(row=2, column=1,
        #                                            padx=10, pady=10)

        def zoom_out(*args):
            a = 2**0.1
            for c in ["x_min", "x_max", "y_min", "y_max"]:
                self.result[c].set(self.result[c].get() * a)

        def zoom_in(*args):
            a = 2**0.1
            for c in ["x_min", "x_max", "y_min", "y_max"]:
                self.result[c].set(self.result[c].get() / a)

        def zoom_in_preview(*args):
            zoom_in()
            self.make_preview()

        def zoom_out_preview(*args):
            zoom_out()
            self.make_preview()

        self.bind("<Control-Key-minus>", zoom_out_preview)
        self.bind("<Control-Key-plus>", zoom_in_preview)

        def reset_geometry(*args):
            self.result["x_min"].set(WORLD_GEOMETRY[0])
            self.result["x_max"].set(WORLD_GEOMETRY[1])
            self.result["y_min"].set(WORLD_GEOMETRY[2])
            self.result["y_max"].set(WORLD_GEOMETRY[3])
            if self.result["width"].get() > self.result["height"].get():
                self.adjust_preview_X()
            else:
                self.adjust_preview_X()

        Button(coord_frame, text="zoom -",
               command=zoom_out).grid(row=3, column=0,
                                      padx=10, pady=10)
        Button(coord_frame, text="zoom +",
               command=zoom_in).grid(row=3, column=1,
                                     padx=10, pady=10)

        transformation_frame = LabelFrame(frame, text="transformation")
        transformation_frame.pack(padx=5, pady=5)
        modulus = LabelEntry(transformation_frame, label="modulus",
                             value=float(modulus),
                             width=4)
        modulus.pack(padx=5, pady=5)
        self.result["modulus"] = modulus

        angle = LabelEntry(transformation_frame, label="angle (°)",
                           value=float(angle),
                           width=4)
        angle.pack(padx=5, pady=5)
        self.result["angle"] = angle

        Button(coord_frame, text="reset",
               command=reset_geometry).grid(row=4, column=0, columnspan=2,
                                            padx=10, pady=10)
        # >>>3

        # result settings       <<<3
        settings_frame = LabelFrame(frame, text="output")
        settings_frame.pack(side=TOP, padx=5, pady=5)

        width = LabelEntry(settings_frame,
                           label="width", value=OUTPUT_WIDTH,
                           width=6, justify=RIGHT)
        width.pack(side=TOP, anchor=E, padx=5, pady=5)
        self.result["width"] = width

        height = LabelEntry(settings_frame,
                            label="height", value=OUTPUT_HEIGHT,
                            width=6, justify=RIGHT)
        height.pack(side=TOP, anchor=E, padx=5, pady=5)
        self.result["height"] = height

        output_filename = LabelEntry(settings_frame,
                                     label=None, value=filename,
                                     width=15)
        output_filename.pack(side=TOP, anchor=E, padx=5, pady=5)
        self.result["filename"] = output_filename
        # >>>3

        tmp = LabelFrame(frame, text="image")
        tmp.pack(padx=10, pady=10)

        Button(tmp, text="preview",
               command=self.make_preview).pack(padx=10, pady=10)

        Button(tmp, text="save",
               command=self.make_output).pack(side=TOP, padx=10, pady=10)

        if self.result["width"].get() > self.result["height"].get():
            self.adjust_preview_X()
        else:
            self.adjust_preview_X()
    # >>>2

    def init_function(self, matrix=None):     # <<<2
        frame = LabelFrame(self, text="Function")
        frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # display matrix    <<<3
        tmp = Frame(frame)
        tmp.pack(side=LEFT)
        Label(tmp, text="matrix").pack(side=TOP)

        tmp2 = Frame(tmp)
        tmp2.pack(padx=5, pady=5)
        display = Listbox(tmp2, selectmode=MULTIPLE, width=30, height=15)
        display.pack(side=LEFT)
        self.function["display"] = display
        scrollbar = Scrollbar(tmp2)
        scrollbar.pack(side=RIGHT, fill=Y)
        display.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=display.yview)

        def remove_entries(*args):
            entries = display.curselection()
            p = 0
            for e in entries:
                tmp = display.get(e-p)
                n, m, _ = re.split("\s*(?:[,;:]|(?:[-=]>))\s*", tmp)
                self.function["matrix"].pop((int(n), int(m)))
                display.delete(e-p, e-p)
                p += 1

        display.bind("<BackSpace>", remove_entries)
        display.bind("<Delete>", remove_entries)

        if matrix is not None:
            self.change_matrix(matrix)
        else:
            self.change_matrix({})
        # >>>3

        # change entries <<<3
        change_frame = Frame(frame)
        change_frame.pack(side=LEFT)

        tmp = LabelFrame(change_frame, text="Change entry")
        tmp.pack(side=TOP, padx=5, pady=5)
        new_entry = LabelEntry(tmp, label="", value="", width=10)
        new_entry.pack(side=TOP, padx=5, pady=5)

        def add_entry(*args):
            e = new_entry.get().strip()
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
                    del self.function["matrix"][(n, m)]
                else:
                    self.function["matrix"][(n, m)] = z
                self.change_matrix()
                new_entry.set("")
            except Exception as err:
                error("cannot parse matrix entry '{}': {}".format(e, err))

        new_entry.bind("<Return>", add_entry)
        # Button(tmp, text="update",
        #        command=add_entry
        #        ).pack(side=TOP, padx=5, pady=5)

        # def clear_matrix(*args):
        #     self.change_matrix({})

        # Button(tmp, text="clear",
        #        command=clear_matrix
        #        ).pack(side=TOP, padx=5, pady=5)
        # >>>3

        # add noise <<<3
        tmp = LabelFrame(change_frame, text="random noise")
        tmp.pack(side=TOP, padx=5, pady=5)
        noise_entry = LabelEntry(tmp, label="(%)", value=10, width=3)
        noise_entry.pack(side=RIGHT, padx=5, pady=5)

        def add_noise(*args):
            try:
                e = noise_entry.get()/100
            except:
                e = 0.1
            M = self.function["matrix"]
            for n, m in M:
                z = M[(n, m)]
                modulus = abs(z) * uniform(0, e)
                angle = uniform(0, 2*pi)
                M[(n, m)] = z + modulus * complex(cos(angle), sin(angle))
            self.change_matrix()

        def add_noise_preview(*args):
            add_noise()
            self.make_preview()

        noise_entry.bind("<Return>", add_noise)
        self.bind("<Control-n>", add_noise)
        self.bind("<Control-N>", add_noise_preview)

        Button(tmp, text="add noise",
               command=add_noise
               ).pack(side=LEFT, padx=5, pady=5)
        # >>>3

        # random matrix     <<<3
        tmp = LabelFrame(frame, text="random matrix")
        tmp.pack(side=LEFT, padx=5, pady=5)

        nb_coeff = LabelEntry(tmp, label="nb coefficients", value=3, width=4)
        nb_coeff.pack(side=TOP, anchor=E, padx=5, pady=5)

        min_degre = LabelEntry(tmp, label="min degre", value=-6, width=4)
        min_degre.pack(side=TOP, anchor=E, padx=5, pady=5)

        max_degre = LabelEntry(tmp, label="max degre", value=6, width=4)
        max_degre.pack(side=TOP, anchor=E, padx=5, pady=5)

        min_coeff = LabelEntry(tmp, label="min coefficient", value=float(-.1),
                               width=4)
        min_coeff.pack(side=TOP, anchor=E, padx=5, pady=5)

        max_coeff = LabelEntry(tmp, label="max coefficient", value=float(.1),
                               width=4)
        max_coeff.pack(side=TOP, anchor=E, padx=5, pady=5)

        def new_random_matrix(*args):
            a = min_degre.get()
            b = max_degre.get()
            coeffs = list(product(range(a, b+1), range(a, b+1)))
            shuffle(coeffs)
            n = nb_coeff.get()
            coeffs = coeffs[:n]
            a = min_coeff.get()
            b = max_coeff.get()
            M = {}
            for (n, m) in coeffs:
                M[(n, m)] = complex(uniform(a, b), uniform(a, b))
            self.change_matrix(M)

        def random_matrix_preview(*args):
            new_random_matrix()
            self.make_matrix()
            self.make_preview()

        Button(tmp, text="generate",
               command=new_random_matrix
               ).pack(side=TOP, padx=5, pady=5)
        self.bind("<Control-g>", new_random_matrix)
        self.bind("<Control-G>", random_matrix_preview)
        # >>>3

        # tabs for the different kinds of functions / symmetries
        tabs = Notebook(frame)
        tabs.pack(side=LEFT, padx=10, pady=10)
        self.function["tabs"] = tabs

        frieze_tab = Frame(tabs)
        wallpaper_tab = Frame(tabs)

        # symmetries for rosettes and frieze patterns   <<<3
        tabs.add(frieze_tab, text="frieze")
        tabs.add(wallpaper_tab, text="wallpaper")
        tabs.select(1)  # select wallpaper tab

        frieze_type = StringVar()

        frieze_combo = Combobox(frieze_tab, width=15, exportselection=0,
                                textvariable=frieze_type,
                                state="readonly",
                                values=FRIEZE_TYPES
                                )
        # make sure the stringvar isn't garbage collected
        frieze_combo.stringvar = frieze_type
        frieze_combo.pack(side=TOP, padx=5, pady=5)
        frieze_combo.current(0)
        self.function["frieze_type"] = frieze_combo.stringvar.get()

        def set_frieze_type(*args):
            frieze_combo.select_clear()
            self.function["frieze_type"] = frieze_combo.stringvar.get()

        frieze_combo.bind("<<ComboboxSelected>>", set_frieze_type)

        rosette = BooleanVar()
        rosette.set(False)
        self.function["rosette"] = rosette.get()

        def set_rosette(*args):
            b = rosette.get()
            self.function["rosette"] = b
            if b:
                self.function["nb_fold"].config(state=NORMAL)
                self.function["nb_fold"].label_widget.config(state=NORMAL)
            else:
                self.function["nb_fold"].config(state=DISABLED)
                self.function["nb_fold"].label_widget.config(state=DISABLED)

        rosette_button = Checkbutton(frieze_tab, text="rosette",
                                     variable=rosette,
                                     onvalue=True, offvalue=False,
                                     )
        rosette_button.pack(side=TOP, padx=5, pady=5)

        nb_fold = LabelEntry(frieze_tab, label="symmetries", value=5, width=2)
        nb_fold.pack(side=TOP, padx=5, pady=5)
        self.function["nb_fold"] = nb_fold

        rosette_button.config(command=set_rosette)
        set_rosette()

        Button(frieze_tab, text="make matrix",
               command=self.make_matrix).pack(side=BOTTOM, padx=5, pady=5)
        # >>>3

        # symmetries for wallpaper
        wallpaper_type = StringVar()

        wallpaper_combo = Combobox(
                wallpaper_tab, width=18, exportselection=0,
                textvariable=wallpaper_type,
                state="readonly",
                values=WALLPAPER_TYPES
                )
        # make sure the stringvar isn't garbage collected
        wallpaper_combo.stringvar = wallpaper_type
        wallpaper_combo.pack(side=TOP, padx=5, pady=5)
        wallpaper_combo.current(1)
        self.function["wallpaper_type"] = wallpaper_combo.stringvar.get()

        lattice_params = LabelEntry(wallpaper_tab,
                                    label="lattice parameters",
                                    value="1,1", width=7)
        lattice_params.pack(side=TOP, padx=5, pady=5)
        self.function["lattice_params"] = lattice_params

        def select_wallpaper(*args):
            old = self.function["wallpaper_type"]
            s = wallpaper_combo.stringvar.get()
            if s.startswith("-- "):
                wallpaper_combo.stringvar.set(old)
            else:
                self.function["wallpaper_type"] = s
            wallpaper_combo.select_clear()
            pattern = self.function["wallpaper_type"].split()[0]
            lattice = lattice_type(pattern)
            if lattice == "general":
                lattice_params.config(state=NORMAL)
                lattice_params.set("1, 2")
                lattice_params.label_widget.config(state=NORMAL)
                lattice_params.label_widget.config(text="xsi, eta")
            elif lattice == "rhombic":
                lattice_params.config(state=NORMAL)
                lattice_params.set("2")
                lattice_params.label_widget.config(state=NORMAL)
                lattice_params.label_widget.config(text="b")
            elif lattice == "rectangular":
                lattice_params.config(state=NORMAL)
                lattice_params.set("2")
                lattice_params.label_widget.config(state=NORMAL)
                lattice_params.label_widget.config(text="L")
            elif lattice == "square":
                lattice_params.config(state=DISABLED, width=3)
                lattice_params.set("")
                lattice_params.label_widget.config(state=DISABLED)
                lattice_params.label_widget.config(text="lattice parameters")
            elif lattice == "hexagonal":
                lattice_params.config(state=DISABLED, width=3)
                lattice_params.set("")
                lattice_params.label_widget.config(state=DISABLED)
                lattice_params.label_widget.config(text="lattice parameters")
            else:
                assert False

        select_wallpaper()

        wallpaper_combo.bind("<<ComboboxSelected>>", select_wallpaper)

        Button(wallpaper_tab, text="make matrix",
               command=self.make_matrix).pack(side=BOTTOM, padx=5, pady=5)
        # >>>3

    # >>>2

    def change_colorwheel(self, filename):  # <<<2
        try:
            filename = os.path.abspath(filename)
            img = PIL.Image.open(filename)
            # img = img.resize((200, 200), PIL.Image.ANTIALIAS)
            img.thumbnail((200, 200), PIL.Image.ANTIALIAS)
            self.colorwheel["image"] = img
            tk_img = PIL.ImageTk.PhotoImage(img)
            self.colorwheel["tk_image"] = tk_img
            self.colorwheel["display"].delete(self.colorwheel["colorwheel_id"])
            self.colorwheel["display"].create_image((100, 100), image=tk_img)
            self.colorwheel["full_filename"] = filename
            self.colorwheel["filename"].config(text=os.path.basename(filename))
            width, height = self.colorwheel["image"].size
            ratio = width / height
            if ratio > 1:
                self.colorwheel["x_min"].set(COLOR_GEOMETRY[0])
                self.colorwheel["x_max"].set(COLOR_GEOMETRY[1])
                self.colorwheel["y_min"].set(COLOR_GEOMETRY[2] / ratio)
                self.colorwheel["y_max"].set(COLOR_GEOMETRY[3] / ratio)
            else:
                self.colorwheel["x_min"].set(COLOR_GEOMETRY[0] * ratio)
                self.colorwheel["x_max"].set(COLOR_GEOMETRY[1] * ratio)
                self.colorwheel["y_min"].set(COLOR_GEOMETRY[2])
                self.colorwheel["y_max"].set(COLOR_GEOMETRY[3])
        except:
            error("problem while opening {} for color image".format(filename))
    # >>>2

    def choose_colorwheel(self):    # <<<2
        filename = filedialog.askopenfilename(
                title="Create Symmetry: choose color wheel image",
                initialdir="./",
                filetypes=[("images", "*.jpg *.jpeg *.png"), ("all", "*.*")])
        self.change_colorwheel(filename)
    # >>>2

    def change_matrix(self, M=None):    # <<<2
        if M is None:
            M = self.function["matrix"]
        else:
            self.function["matrix"] = M
        display = self.function["display"]
        display.delete(0, END)
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
                x = "{:.4f}".format(z.real).rstrip("0")
                y = "{:.4f}".format(z.imag).rstrip("0")
                x = x.rstrip(".")
                y = y.rstrip(".")
                return "{} + {}i".format(x, y)

        for (n, m) in keys:
            display.insert(END, "{:2}, {:2} : {}"
                                .format(n, m, show(M[(n, m)])))
    # >>>2

    def make_matrix(self):       # <<<2
        tabs = self.function["tabs"]
        M = self.function["matrix"]

        if ("frieze" in tabs.tab(tabs.select(), "text") and
                self.function["rosette"]):
            p = self.function["nb_fold"].get()
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

        if "frieze" in tabs.tab(tabs.select(), "text"):
            pattern = self.function["frieze_type"].split()[0]
        elif "wallpaper" in tabs.tab(tabs.select(), "text"):
            pattern = self.function["wallpaper_type"].split()[0]
        else:
            assert False

        M = add_symmetries_to_matrix(M, pattern)
        self.change_matrix(M)
    # >>>2

    def make_preview(self, *args):      # <<<2

        ratio = self.result["width"].get() / self.result["height"].get()
        if ratio > 1:
            width = PREVIEW_SIZE
            height = round(PREVIEW_SIZE / ratio)
        else:
            width = round(PREVIEW_SIZE * ratio)
            height = PREVIEW_SIZE

        preview_image, _ = self.make_image(width, height)

        tk_img = PIL.ImageTk.PhotoImage(preview_image)
        self.result["display"].tk_img = tk_img
        self.result["display"].delete(self.result["preview_id"])
        self.result["preview_id"] = self.result["display"].create_image((PREVIEW_SIZE//2, PREVIEW_SIZE//2), image=tk_img)
    # >>>2

    def make_output(self, *args):      # <<<2
        width = self.result["width"].get()
        height = self.result["height"].get()

        filename_template = self.result["filename"].get()
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

    def make_image(self, width, height, filename="output.jpg"):      # <<<2
        x_min = self.result["x_min"].get()
        x_max = self.result["x_max"].get()
        y_min = self.result["y_min"].get()
        y_max = self.result["y_max"].get()

        modulus = self.result["modulus"].get()
        angle = self.result["angle"].get()

        color_x_min = self.colorwheel["x_min"].get()
        color_x_max = self.colorwheel["x_max"].get()
        color_y_min = self.colorwheel["y_min"].get()
        color_y_max = self.colorwheel["y_max"].get()

        color_mod = self.colorwheel["modulus"].get()
        color_ang = self.colorwheel["angle"].get()

        default_color = self.colorwheel["default_color"].get()

        tabs = self.function["tabs"]
        if "frieze" in tabs.tab(tabs.select(), "text"):
            pattern = self.function["frieze_type"].split()[0]
            if self.function["rosette"]:
                lattice = "rosette"
            else:
                lattice = "frieze"
        elif "wallpaper" in tabs.tab(tabs.select(), "text"):
            pattern = self.function["wallpaper_type"].split()[0]
            lattice = lattice_type(pattern)
        else:
            assert False

        lattice_params = ()
        s = self.function["lattice_params"].get()
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

        matrix = self.function["matrix"]

        image = make_world_numpy(
                    matrix=matrix,
                    color_filename=self.colorwheel["full_filename"],
                    size=(width, height),
                    geometry=(x_min, x_max, y_min, y_max),
                    modulus=modulus,
                    angle=angle,
                    lattice=lattice,
                    lattice_params=lattice_params,
                    color_geometry=(color_x_min, color_x_max,
                                    color_y_min, color_y_max),
                    color_modulus=color_mod,
                    color_angle=color_ang,
                    default_color=default_color)

        cmd = ("""#!/bin/sh
CREATE_SYM={prog_path:}

$CREATE_SYM --color={color:} \\
            --color-geometry={c_x_min:},{c_x_max:},{c_y_min:},{c_y_max:} \\
            --color-modulus={color_mod:} \\
            --color-angle={color_ang:} \\
            --geometry={x_min:},{x_max:},{y_min:},{y_max:} \\
            --modulus={modulus:} \\
            --angle={angle:} \\
            --size={width:},{height:} \\
            --matrix='{matrix:}' \\
            --output={output:} \\
            $@
""".format(cwd=os.getcwd(),
           prog_path=os.path.abspath(sys.argv[0]),
           color=self.colorwheel["full_filename"],
           c_x_min=color_x_min,
           c_x_max=color_x_max,
           c_y_min=color_y_min,
           c_y_max=color_y_max,
           color_mod=color_mod,
           color_ang=color_ang,
           x_min=x_min,
           x_max=x_max,
           y_min=y_min,
           y_max=y_max,
           modulus=modulus,
           angle=angle,
           width=width,
           height=height,
           matrix=str(self.function["matrix"]),
           output=filename
           ))
        return image, cmd
    # >>>2

    def adjust_preview_X(self, *args):      # <<<2
        ratio = self.result["width"].get() / self.result["height"].get()
        x_min = self.result["x_min"].get()
        x_max = self.result["x_max"].get()
        delta_y = self.result["y_max"].get() - self.result["y_min"].get()
        delta_x = delta_y * ratio
        middle_x = (x_min+x_max) / 2
        self.result["x_min"].set(middle_x - delta_x/2)
        self.result["x_max"].set(middle_x + delta_x/2)
    # >>>2

    def adjust_preview_Y(self, *args):      # <<<2
        ratio = self.result["height"].get() / self.result["width"].get()
        y_min = self.result["y_min"].get()
        y_max = self.result["y_max"].get()
        delta_x = self.result["x_max"].get() - self.result["x_min"].get()
        delta_y = delta_x * ratio
        middle_y = (y_min+y_max) / 2
        self.result["y_min"].set(middle_y - delta_y/2)
        self.result["y_max"].set(middle_y + delta_y/2)
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
    --no-numpy                          do not use numpy for computation (slow)
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
            "verbose", "no-numpy", "gui"]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(-1)

    if len(sys.argv) == 1:
        GUI().mainloop()
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
    use_numpy = True
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
        elif o in ["--no-numpy"]:
            use_numpy = False
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
        GUI(matrix=matrix,
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
        if use_numpy:
            make_world = make_world_numpy
        else:
            make_world = make_world_plain
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
