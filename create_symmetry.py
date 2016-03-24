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

# math
from cmath import exp
from math import sqrt, pi
from random import randint, uniform, shuffle
# >>>1

verbose = 0


###
# some utility functions
# <<<1
def error(s):
    """print string ``s`` on stderr"""
    print("*** " + s, file=sys.stderr)


def horner(P, z):
    """apply the polynomial ``\sum_{n} P[n] Z^n`` to ``z``"""
    r = 0
    for i in range(len(P)):
        r = r*z + P[-i-1]
    return r


def apply(M, z):
    """apply the function ``\sum_{n,m} M[n,m] Z^n \conj(Z)^m`` to ``z``"""
    zc = z.conjugate()
    r = 0
    for (n, m) in M:
        r += M[(n, m)] * z**n * zc**m
    return r
# >>>1


###
# functions to manipulate matrices of functions
# <<<1
def make_frieze(M, frieze):     # <<<2
    """modify the matrix ``M`` to give a frieze pattern with symetries
``frieze`` can be any of the seven types of frieze patterns (p111, p211,
p1m1, p11m, p2mm, p11g or p2mg)"""
    if frieze == "p111":
        return M
    elif frieze == "p211":
        R = {}
        for (n, m) in M:
            coeff = (M.get((n, m), 0) + M.get((-n, -m), 0)) / 2
            R[(n, m)] = R[(-n, -m)] = coeff
        return R
    elif frieze == "p1m1":
        R = {}
        for (n, m) in M:
            coeff = (M.get((n, m), 0) + M.get((m, n), 0)) / 2
            R[(n, m)] = R[(m, n)] = coeff
        return R
    elif frieze == "p11m":
        R = {}
        for (n, m) in M:
            coeff = (M.get((n, m), 0) + M.get((-m, -n), 0)) / 2
            R[(n, m)] = R[(-m, -n)] = coeff
        return R
    elif frieze == "p2mm":
        R = {}
        for (n, m) in M:
            coeff = (M.get((n, m), 0) + M.get((m, n), 0) +
                     M.get((-n, -m), 0) + M.get((-m, -n), 0)) / 4
            R[(n, m)] = R[(m, n)] = R[(-n, -m)] = R[(-m, -n)] = coeff
        return R
    elif frieze == "p11g":
        R = {}
        for (n, m) in M:
            coeff = (M.get((n, m), 0) + M.get((-m, -n), 0)) / 2
            R[(n, m)] = R[(-m, -n)] = coeff
        S = {}
        for (n, m) in R:
            if (n+m) % 2 == 1:
                S[(n, m)] = -R[(-m, -n)]
                S[(-m, -n)] = R[(-m, -n)]
            else:
                S[(n, m)] = S[(-m, -n)] = R[(-m, -n)]
        return S
    elif frieze == "p2mg":
        R = {}
        for (n, m) in M:
            coeff = (M.get((n, m), 0) + M.get((m, n), 0) +
                     M.get((-n, -m), 0) + M.get((-m, -n), 0)) / 4
            R[(n, m)] = R[(m, n)] = R[(-n, -m)] = R[(-m, -n)] = coeff
        S = {}
        for (n, m) in R:
            if (n+m) % 2 == 1:
                S[(-m, -n)] = R[(-m, -n)]
                S[(m, n)] = R[(m, n)]
                S[(n, m)] = -R[(-m, -n)]
                S[(-n, -m)] = -R[(m, n)]
            else:
                S[(-m, -n)] = R[(-m, -n)]
                S[(m, n)] = R[(m, n)]
                S[(n, m)] = R[(-m, -n)]
                S[(-n, -m)] = R[(m, n)]
        return S
    else:
        error("Unknown frieze pattern type: {}".format(frieze))
        sys.exit(1)
# >>>2
# >>>1


###
# making an image from a transformation and a colorwheel
def make_world_numpy(                   # <<<1
        A,                              # the matrix of the transformation
        color_im,                       # image for the colorwheel image
        width, height,                  # size of the output image
        x_min=-1,                       # coordinates of the world
        x_max=1,                        # ...
        y_min=-1,                       # ...
        y_max=1,                        # ...
        E=None,                         # None, an integer, or the 2x2 matrix giving the transformation to apply to the input
        color_x_min=-1,                 # coordinates of the colorwheel
        color_x_max=1,                  # ...
        color_y_min=-1,                 # ...
        color_y_max=1,                  # ...
        default_color="black"
        ):

    if isinstance(default_color, str):
        default_color = getrgb(default_color)

    if isinstance(color_im, str):
        tmp = PIL.Image.open(color_im)
        border_size = 1
        color_im = PIL.Image.new("RGB",
                                 (tmp.size[0]+2*border_size,
                                  tmp.size[1]+2*border_size),
                                 color=default_color)
        color_im.paste(tmp, (border_size, border_size))
        del tmp

    import numpy as np
    delta_x = (x_max-x_min) / (width-1)
    delta_y = (y_max-y_min) / (height-1)

    color_width, color_height = color_im.size
    color_delta_x = (color_x_max-color_x_min) / (color_width-1)
    color_delta_y = (color_y_max-color_y_min) / (color_height-1)

    xs = np.arange(width)
    xs = x_min + xs*delta_x

    ys = np.arange(height)
    ys = y_max - ys*delta_y
    res = np.zeros((width, height), complex)
    for (n, m) in A:
        if E is None:
            zs = xs[:, None] + 1j*ys
            zcs = np.conj(zs)
            res = res + A[(n, m)] * zs**n * zcs**m
        elif isinstance(E, float) or isinstance(E, int):
            zs = xs[:, None] + 1j*ys
            zs = np.exp(E * 2j * pi * zs)
            zcs = np.conj(zs)
            res = res + A[(n, m)] * zs**n * zcs**m
        elif isinstance(E, str):
            if E == "square":
                zs = (np.exp(2j*pi*(n*xs[:, None] + m*ys)) +
                      np.exp(2j*pi*(m*xs[:, None] - n*ys)) +
                      np.exp(2j*pi*(-n*xs[:, None] - m*ys)) +
                      np.exp(2j*pi*(-m*xs[:, None] + n*ys))) / 4
                res = res + A[(n, m)] * zs
            elif E == "hexagonal":
                Xs = xs[:, None] + ys/sqrt(3)
                Ys = 2*ys / sqrt(3)
                zs = (np.exp(2j*pi*(n*Xs + m*Ys)) +
                      np.exp(2j*pi*(m*Xs - (n+m)*Ys)) +
                      np.exp(2j*pi*(-(n+m)*Xs + n*Ys))) / 3
                res = res + A[(n, m)] * zs
            else:
                error("unknown lattice: '{}'".format(E))
        else:   # E should be a 2x2 array
            zs = (n*(E[0][0]*xs[:, None] + E[0][1]*ys) +
                  m*(E[1][0]*xs[:, None] + E[1][1]*ys))
            res = res + A[(n, m)] * np.exp(2j*pi*zs)

    xs = np.rint((res.real - color_x_min) / color_delta_x).astype(int)
    ys = np.rint((color_y_max - res.imag) / color_delta_y).astype(int)

    np.place(xs, xs < 0, [0])
    np.place(xs, xs >= color_width, [0])
    np.place(ys, ys < 0, [0])
    np.place(ys, ys >= color_height, [0])

    res = np.dstack([xs, ys])

    color = np.array(color_im.getdata())
    color = color.reshape(color_height, color_width, 3)
    color = color.transpose(1, 0, 2)

    res = color[xs, ys]
    res = np.array(res, dtype=np.uint8)

    res = res.transpose(1, 0, 2)

    return PIL.Image.fromarray(res, "RGB")
# >>>1


def make_world_plain(                   # <<<1
        A,                              # the matrix of the transformation
        color_im,                       # image for the colorwheel image
        width, height,                  # size of the output image
        x_min=-1,                       # coordinates of the world
        x_max=1,                        # ...
        y_min=-1,                       # ...
        y_max=1,                        # ...
        E=None,                         # None, an integer, a string ("square" or "hexagonal") or the 2x2 matrix giving the transformation to apply to the input
        color_x_min=-1,                 # coordinates of the colorwheel
        color_x_max=1,                  # ...
        color_y_min=-1,                 # ...
        color_y_max=1,                  # ...
        default_color="black"
        ):

    if isinstance(default_color, str):
        default_color = getrgb(default_color)

    if isinstance(color_im, str):
        tmp = PIL.Image.open(color_im)
        border_size = 1
        color_im = PIL.Image.new("RGB",
                                 (tmp.size[0]+2*border_size,
                                  tmp.size[1]+2*border_size),
                                 color=default_color)
        color_im.paste(tmp, (border_size, border_size))
        del tmp

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
            res = 0
            for (n, m) in A:
                if E is None:
                    z = complex(x, y)
                    zc = z.conjugate()
                    res = res + A[(n, m)] * z**n * zc**m
                elif isinstance(E, float):
                    z = exp(E * 1j * z)
                    zc = z.conjugate()
                    res = res + A[(n, m)] * z**n * zc**m
                elif isinstance(E, str):
                    if E == "square":
                        z = (exp(2j*pi*(n*x + m*y)) +
                             exp(2j*pi*(m*x - n*y)) +
                             exp(2j*pi*(-n*x - m*y)) +
                             exp(2j*pi*(-m*x + n*y))) / 4
                        res = res + A[(n, m)] * z
                    elif E == "hexagonal":
                        X = x + y/sqrt(3)
                        Y = 2*y / sqrt(3)
                        z = (exp(2j*pi*(n*X + m*Y)) +
                             exp(2j*pi*(m*X - (n+m)*Y)) +
                             exp(2j*pi*(-(n+m)*X + n*Y))) / 3
                        res = res + A[(n, m)] * z
                    else:
                        error("unknown lattice: '{}'".format(E))
                else:   # E should be a 2x2 array
                    z = exp(2j*pi*(
                            n*(E[0][0]*x + E[0][1]*y) +
                            m*(E[1][0]*x + E[1][1]*y)
                            ))
                    res = res + A[(n, m)] * z

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
# <<<1

class LabelEntry(Frame):  # <<<2
    """
    An Entry widget with a label on its left.
    """
    __entry = None  # the Entry widget
    __label = None  # the Label widget
    content = None  # the corresponding StringVar

    def __init__(self, parent, label, on_click=None,  # <<<3
                 state=NORMAL, **kwargs):
        Frame.__init__(self, parent)

        if label:
            self.__label = Label(self, text=label)
            self.__label.pack(side=LEFT, padx=(0, 5))

        self.content = StringVar("")
        self.__entry = Entry(self, textvar=self.content, state=state, **kwargs)
        self.__entry.pack(side=LEFT)

        for method in ["configure", "bind", "focus_set"]:
            setattr(self, method, getattr(self.__entry, method))
    # >>>3

    def set(self, s):  # <<<3
        if s is None:
            self.content.set("")
        else:
            self.content.set(s)
    # >>>3

    def get(self):  # <<<3
        return self.content.get()
    # >>>3

    def delete(self):  # <<<3
        self.content.set("")
    # >>>3
# >>>2


class GUI(Tk):

    preview_width = 500
    preview_height = 500

    output_width = 1280
    output_height = 960
    output_filename = "output-{:03}"

    colorwheel = {}     # form elements for the colorwheel:
    #  - tk_image to keep a reference to the TkImage object
    #  - image for the corresponding Image
    #  - display for the corresponding Canvas showing the image
    #  - x_min, x_max, y_min, y_max for the geometry of the image (StringVars)
    #  - default_color for the default color (StringVar)
    #  - filename for the displayed filename (Label)
    #  - full_filename for the real filename

    result = {}     # form elements for the result
    #  - tk_image to keep a reference to the TkImage object
    #  - image for the corresponding Image
    #  - display for the corresponding Canvas showing the image
    #  - x_min, x_max, y_min, y_max for the geometry of the image (StringVars)
    #  - preview_width, preview_height for the size of the preview
    #  - output_width, output_height for the size of the final image
    #  - filename for the filename of saved images (StringVar)

    function = {}   # form element for the function
    #  - matrix for the matrix (dict) of coefficients
    #  - display for displaying the matrix (Text)
    #  - frieze_type for the frieze pattern type (StringVar)
    #  - rosette for the rosette boolean (StringVar)
    #  - nb_fold for the number of rotational symmetries for rosettes

    def __init__(self,      # <<<2
                 output_filename=None,
                 color_filename=None,
                 matrix=None):

        # tk interface
        Tk.__init__(self)
        # self.resizable(width=False, height=False)
        # self.geometry("1200x600")
        self.title("Create Symmetry")

        self.init_colorwheel()
        self.init_result()
        self.init_function()

        if output_filename is not None:
            self.output_filename = output_filename

        if color_filename is not None:
            self.change_colorwheel(color_filename)

        if matrix is not None:
            self.change_matrix(matrix)
        else:
            self.change_matrix({})

        # keybindings
        self.bind("q", lambda _: self.destroy())
        self.bind("p", lambda _: self.make_preview())
    # >>>2

    def init_colorwheel(self):     # <<<2
        frame = LabelFrame(self, text="Color Wheel Image")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky=N+S)

        canvas = Canvas(frame, width=200, height=200, bg="white")
        canvas.pack(side=TOP, padx=10, pady=10)
        self.colorwheel["display"] = canvas

        filename = Label(frame, text="...")
        filename.pack(side=TOP, pady=(0, 5))
        self.colorwheel["filename"] = filename
        self.colorwheel["full_filename"] = ""

        Button(frame, text="choose file",
               command=self.choose_colorwheel).pack(side=TOP)

        coord_frame = LabelFrame(frame, text="coordinates")
        coord_frame.pack(side=TOP, padx=5, pady=20)

        x_min = LabelEntry(coord_frame, label="x min", width=3, justify=RIGHT)
        x_min.grid(row=0, column=0, padx=5, pady=5)
        x_min.set("-1")
        self.colorwheel["x_min"] = x_min

        x_max = LabelEntry(coord_frame, label="x max", width=3, justify=RIGHT)
        x_max.grid(row=0, column=1, padx=5, pady=5)
        x_max.set("1")
        self.colorwheel["x_max"] = x_max

        y_min = LabelEntry(coord_frame, label="y min", width=3, justify=RIGHT)
        y_min.grid(row=1, column=0, padx=5, pady=5)
        y_min.set("-1")
        self.colorwheel["y_min"] = y_min

        y_max = LabelEntry(coord_frame, label="y max", width=3, justify=RIGHT)
        y_max.grid(row=1, column=1, padx=5, pady=5)
        y_max.set("1")
        self.colorwheel["y_max"] = y_max

        color = LabelEntry(frame, label="default color", width=10)
        color.pack(side=TOP, padx=5, pady=5)
        color.set("black")
        self.colorwheel["default_color"] = color

        Button(frame, text="update",
               command=self.update_colorwheel).pack(side=TOP, pady=10)
    # >>>2

    def init_result(self):     # <<<2
        frame = LabelFrame(self, text="Result Image")
        frame.grid(row=0, column=1, padx=10, pady=10)

        # the preview image     <<<3
        image = Canvas(frame, width=500, height=500, bg="white")
        image.pack(side=LEFT, padx=10, pady=10)
        self.result["display"] = image
        # >>>3

        # geometry of result    <<<3
        coord_frame = LabelFrame(frame, text="coordinates")
        coord_frame.pack(side=TOP, padx=5, pady=5)

        x_min = LabelEntry(coord_frame, label="x min", width=3, justify=RIGHT)
        x_min.grid(row=0, column=0, padx=5, pady=5)
        x_min.set("-2")
        self.result["x_min"] = x_min

        x_max = LabelEntry(coord_frame, label="x max", width=3, justify=RIGHT)
        x_max.grid(row=0, column=1, padx=5, pady=5)
        x_max.set("2")
        self.result["x_max"] = x_max

        y_min = LabelEntry(coord_frame, label="y min", width=3, justify=RIGHT)
        y_min.grid(row=1, column=0, padx=5, pady=5)
        y_min.set("-2")
        self.result["y_min"] = y_min

        y_max = LabelEntry(coord_frame, label="y max", width=3, justify=RIGHT)
        y_max.grid(row=1, column=1, padx=5, pady=5)
        y_max.set("2")
        self.result["y_max"] = y_max
        # >>>3

        # preview settings      <<<3
        preview_setting_frame = LabelFrame(frame, text="preview")
        preview_setting_frame.pack(side=TOP, fill=X, padx=5, pady=5)

        preview_width = LabelEntry(preview_setting_frame, label="width",
                                   width=6, justify=RIGHT)
        preview_width.pack(anchor=E, padx=5, pady=5)
        preview_width.set("500")
        self.result["preview_width"] = preview_width

        preview_height = LabelEntry(preview_setting_frame, label="height",
                                    width=6, justify=RIGHT)
        preview_height.pack(anchor=E, padx=5, pady=5)
        preview_height.set("500")
        self.result["preview_height"] = preview_height
        # >>>3
        Button(frame, text="preview",
               command=self.make_preview).pack(padx=10, pady=10)

        # result settings       <<<3
        settings_frame = LabelFrame(frame, text="output")
        settings_frame.pack(side=TOP, fill=X, padx=5, pady=5)

        output_width = LabelEntry(settings_frame, label="width",
                                  width=6, justify=RIGHT)
        output_width.pack(side=TOP, anchor=E, padx=5, pady=5)
        output_width.set(self.output_width)
        self.result["output_width"] = output_width

        output_height = LabelEntry(settings_frame, label="height",
                                   width=6, justify=RIGHT)
        output_height.pack(side=TOP, anchor=E, padx=5, pady=5)
        output_height.set(self.output_height)
        self.result["output_height"] = output_height

        output_filename = LabelEntry(settings_frame, label=None, width=15)
        output_filename.pack(side=TOP, anchor=E, padx=5, pady=5)
        output_filename.set(self.output_filename)
        self.result["output_filename"] = output_height
        # >>>3
        Button(frame, text="generate and save",
               command=None).pack(side=TOP, padx=10, pady=10)
    # >>>2

    def init_function(self):     # <<<2
        frame = LabelFrame(self, text="Function")
        frame.grid(row=1, column=0, columnspan=2, sticky=W+E, padx=10, pady=10)

        # display matrix    <<<3
        tmp = Frame(frame)
        tmp.pack(side=LEFT)
        Label(tmp, text="matrix").pack()
        display = Text(tmp, width=30, height=15)
        display.config(state=DISABLED, bg="gray", relief="ridge")
        display.pack(padx=5, pady=5)
        self.function["display"] = display
        # >>>3

        # change entries <<<3
        change_frame = Frame(frame)
        change_frame.pack(side=LEFT)

        tmp = LabelFrame(change_frame, text="Change entry")
        tmp.pack(side=TOP, padx=5, pady=5)
        new_entry = LabelEntry(tmp, label="", width=10)
        new_entry.pack(side=TOP, padx=5, pady=5)

        def add_entry(*args):
            e = new_entry.get().strip()
            if e == "":
                return
            try:
                tmp = re.split("\s*(?:[,;]|(?:=>))\s*", e)
                n, m, z = tmp
                n = int(n)
                m = int(m)
                z = re.sub("\s*", "", z)
                z = complex(z)
                if z == 0:
                    del self.function["matrix"][(n, m)]
                else:
                    self.function["matrix"][(n, m)] = z
                self.change_matrix()
            except Exception as err:
                error("cannot parse matrix entry '{}': {}".format(e, err))

        def clear_matrix(*args):
            self.change_matrix({})

        new_entry.bind("<Return>", add_entry)
        Button(tmp, text="update",
               command=add_entry
               ).pack(side=TOP, padx=5, pady=5)
        Button(tmp, text="clear",
               command=clear_matrix
               ).pack(side=TOP, padx=5, pady=5)
        # >>>3

        # add noise <<<3
        tmp = LabelFrame(change_frame, text="random noise")
        tmp.pack(side=TOP, padx=5, pady=5)
        noise_entry = LabelEntry(tmp, label="level (%)", width=3)
        noise_entry.set("10")
        noise_entry.pack(side=TOP, padx=5, pady=5)

        def add_noise(*args):
            try:
                e = float(noise_entry.get())/100
            except:
                e = 0.1
            M = self.function["matrix"]
            for n, m in M:
                z = M[(n, m)]
                x = z.real * (1 + uniform(-e, e))
                y = z.imag * (1 + uniform(-e, e))
                M[(n, m)] = complex(x, y)
            self.change_matrix()

        noise_entry.bind("<Return>", add_noise)
        Button(tmp, text="add noise",
               command=add_noise
               ).pack(side=TOP, padx=5, pady=5)
        # >>>3

        # random matrix     <<<3
        tmp = LabelFrame(frame, text="random matrix")
        tmp.pack(side=LEFT, padx=5, pady=5)

        nb_coeff = LabelEntry(tmp, label="nb coefficients", width=4)
        nb_coeff.set("3")
        nb_coeff.pack(side=TOP, anchor=E, padx=5, pady=5)

        min_degre = LabelEntry(tmp, label="min degre", width=4)
        min_degre.set("-6")
        min_degre.pack(side=TOP, anchor=E, padx=5, pady=5)

        max_degre = LabelEntry(tmp, label="max degre", width=4)
        max_degre.set("6")
        max_degre.pack(side=TOP, anchor=E, padx=5, pady=5)

        min_coeff = LabelEntry(tmp, label="min coefficient", width=4)
        min_coeff.set("-1")
        min_coeff.pack(side=TOP, anchor=E, padx=5, pady=5)

        max_coeff = LabelEntry(tmp, label="max coefficient", width=4)
        max_coeff.set("1")
        max_coeff.pack(side=TOP, anchor=E, padx=5, pady=5)

        def new_random_matrix(*args):
            a = int(min_degre.get())
            b = int(max_degre.get())
            coeffs = list(product(range(a, b+1), range(a, b+1)))
            shuffle(coeffs)
            n = int(nb_coeff.get())
            coeffs = coeffs[:n]
            a = int(min_coeff.get())
            b = int(max_coeff.get())
            M = {}
            for (n, m) in coeffs:
                M[(n, m)] = complex(uniform(a, b), uniform(a, b))
            self.change_matrix(M)

        Button(tmp, text="generate",
               command=new_random_matrix
               ).pack(side=TOP, padx=5, pady=5)
        # >>>3

        # tabs for the different kinds of functions / symmetries
        tabs = Notebook(frame)
        tabs.pack(side=LEFT, fill=Y, padx=10, pady=10)

        frieze_tab = Frame(tabs)
        wallpaper_tab = Frame(tabs)

        tabs.add(frieze_tab, text="frieze")
        tabs.add(wallpaper_tab, text="wallpaper")

        frieze_type = StringVar()
        OptionMenu(frieze_tab, frieze_type, "p111",
                   "p111", "p211", "p1m1", "p11m",
                   "p2mm", "p11g", "p2mg").pack(side=TOP, padx=5, pady=5)
        self.function["frieze_type"] = frieze_type

        rosette = BooleanVar()
        Checkbutton(frieze_tab, text="rosette",
                    variable=rosette,
                    onvalue=True, offvalue=False
                    ).pack(side=TOP, padx=5, pady=5)
        rosette.set(True)
        self.function["rosette"] = rosette

        nb_fold = LabelEntry(frieze_tab, label="symmetries", width=2)
        nb_fold.pack(side=TOP, padx=5, pady=5)
        nb_fold.set("5")
        self.function["nb_fold"] = nb_fold

        Button(frieze_tab, text="make matrix",
               command=self.make_matrix).pack(side=TOP, padx=5, pady=5)
    # >>>2

    def change_colorwheel(self, filename):  # <<<2
        try:
            img = PIL.Image.open(filename)
            # img = img.resize((200, 200), PIL.Image.ANTIALIAS)
            img.thumbnail((200, 200), PIL.Image.ANTIALIAS)
            self.colorwheel["image"] = img
            tk_img = PIL.ImageTk.PhotoImage(img)
            self.colorwheel["tk_image"] = tk_img
            self.colorwheel["display"].configure(bg=self.colorwheel["default_color"].get())
            self.colorwheel["display"].delete("all")
            self.colorwheel["display"].create_image((100, 100), image=tk_img)
            self.colorwheel["full_filename"] = filename
            self.colorwheel["filename"].configure(text=os.path.basename(filename))
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

    def update_colorwheel(self):    # <<<2
        filename = self.colorwheel["full_filename"]
        self.change_colorwheel(filename)
    # >>>2

    def change_matrix(self, M=None):    # <<<2
        if M is None:
            M = self.function["matrix"]
        else:
            self.function["matrix"] = M
        display = self.function["display"]
        display.config(state=NORMAL)
        display.delete(1.0, END)
        keys = list(M.keys())
        keys.sort()

        def show(z):
            x = "{:.4f}".format(z.real).rstrip("0")
            y = "{:.4f}".format(z.imag).rstrip("0")
            x = x.rstrip(".")
            y = y.rstrip(".")
            return "{} + {}j".format(x, y)

        for (n, m) in keys:
            display.insert(END, "{:2}, {:2} -> {}\n"
                                .format(n, m, show(M[(n, m)])))
        display.config(state=DISABLED)
    # >>>2

    def make_matrix(self):       # <<<2
        p = self.function["nb_fold"].get()
        try:
            p = int(p)
            M = self.function["matrix"]
            keys = list(M.keys())
            for (n, m) in keys:
                if (n-m) % p != 0 or n == m:
                    del M[(n, m)]
        except Exception as err:
            error("problem while adding '{}'-fold symmetry to the matrix: {}"
                  .format(p, err))
            return

        sym = self.function["frieze_type"].get()
        M = make_frieze(M, sym)
        self.change_matrix(M)
    # >>>2

    def make_preview(self, *args):      # <<<2

        if self.colorwheel.get("image") is None:
            error("choose a color wheel image")
            return

        if self.function["rosette"].get():
            E = None
        else:
            E = 1

        width = int(self.result["preview_width"].get())
        height = int(self.result["preview_height"].get())

        x_min = int(self.result["x_min"].get())
        x_max = int(self.result["x_max"].get())
        y_min = int(self.result["y_min"].get())
        y_max = int(self.result["y_max"].get())

        color_x_min = int(self.colorwheel["x_min"].get())
        color_x_max = int(self.colorwheel["x_max"].get())
        color_y_min = int(self.colorwheel["y_min"].get())
        color_y_max = int(self.colorwheel["y_max"].get())

        default_color = self.colorwheel["default_color"].get()

        matrix = self.function["matrix"]

        preview_image = make_world_numpy(matrix, self.colorwheel["full_filename"],
                                         width, height,
                                         x_min, x_max, y_min, y_max,
                                         E,
                                         color_x_min, color_x_max, color_y_min, color_y_max,
                                         default_color=default_color)

        tk_img = PIL.ImageTk.PhotoImage(preview_image)
        self.result["display"].tk_img = tk_img
        self.result["display"].delete("all")
        self.result["display"].create_image((self.preview_width//2, self.preview_height//2), image=tk_img)
    # >>>2

# >>>1


def main():     # <<<1
    def display_help():
        print("""Usage: {} [flags]

    -c FILE  /  --color=FILE            choose color file
    -o FILE  /  --output=FILE           choose output file
    -s W,H  /  --size=W,H               choose width and height of output
    -g X,Y,X,Y  /  --geometry=X,Y,X,Y   choose "geometry of output"
    --color-geometry=X,Y,X,Y            choose "geometry" of the color file
    --no-numpy                          do not use numpy for computation (slow)

    -v  /  -verbose                     add information messages
    -h  /  --help                       this message
""")

    # parsing the command line arguments
    short_options = "hc:o:s:g:v"
    long_options = ["help", "color=", "color-geometry", "output=", "size=",
                    "geometry=", "verbose", "no-numpy"]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(-1)

    output_filename = "output.jpg"
    colors_filename = None
    output_width, output_height = 400, 400
    x_min, x_max, y_min, y_max = -2, 2, -2, 2
    color_x_min, color_x_max, color_y_min, color_y_max = -1, 1, -1, 1
    use_numpy = True
    global verbose
    for o, a in opts:
        if o in ["-h", "--help"]:
            display_help()
            sys.exit(0)
        elif o in ["-c", "--color"]:
            colors_filename = a
        elif o in ["-o", "--output"]:
            output_filename = a
        elif o in ["-s", "--size"]:
            try:
                tmp = map(int, a.split(","))
                output_width, output_height = tmp
            except:
                error("problem with size '{}'".format(a))
                output_width, output_height = 400, 400
        elif o in ["-g", "--geometry"]:
            try:
                tmp = map(float, a.split(","))
                x_min, x_max, y_min, y_max = tmp
            except:
                error("problem with geometry '{}' for output".format(a))
                x_min, x_max, y_min, y_max = -2, 2, -2, 2
                sys.exit(1)
        elif o in ["--color-geometry"]:
            try:
                tmp = map(float, a.split(","))
                color_x_min, color_x_max, color_y_min, color_y_max = tmp
            except:
                error("problem with geometry '{}' for color image".format(a))
                color_x_min, color_x_max, color_y_min, color_y_max = -1, 1, -1, 1
                sys.exit(1)
        elif o in ["-v", "--verbose"]:
            verbose += 1
        elif o in ["--no-numpy"]:
            use_numpy = False
        else:
            assert False

    # M = { (1,0): 2 }
    M = {
         (0, 1): .3,
         (1, -1): -.123,
         (3, 1): .4,
        }
    # M = make_frieze(M, "p211")
    a = .7
    b = -.3
    M = {
         (1, 2): a,
         (1, -2): a,
         (3, 1): -b,
         (3, -1): -b,
         }

    if use_numpy:
        make_world = make_world_numpy
    else:
        make_world = make_world_plain
    output_image = make_world(M, colors_filename,
                              output_width, output_height,
                              x_min, x_max, y_min, y_max,
                              # "square",
                              "hexagonal",
                              # [[1,0],[0,1]],
                              # None,
                              color_x_min, color_x_max, color_y_min, color_y_max,
                              default_color="black")

    output_image.save(output_filename)
    output_image.show()
# >>>1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        M = {(4, -6): 0.5, (1, 6): -0.5, (-6, 4): 0.5, (5, 0): 1, (0, 5): 1, (6, 1): -0.5}
        # GUI(matrix=M, color_filename="./Farris-img/farris-027.jpg").mainloop()
        GUI(matrix=M, color_filename="./Images/leaf.jpg").mainloop()
    else:
        main()

# vim: textwidth=0 foldmarker=<<<,>>> foldmethod=marker foldlevel=0
