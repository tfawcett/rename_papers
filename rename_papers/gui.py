# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Name:         gui.py
# Purpose:      GUI (tkinter) code for rename_papers
# Author:       Tom Fawcett <tfawcett@acm.org>
# Copyright:    (c) 2019 by Tom Fawcett
# Created:      Fri Sep 15 2017 by Tom Fawcett (<tfawcett@acm.org>)
# ----------------------------------------------------------------------------
import tkinter as tk
import tkinter.ttk as ttk

from .fragments import compose_new_filename

#  Max length of new filename
MAX_FILENAME_LENGTH = 150

#  How many of the first fragments from pdftotext to consider
N_FIRST_FRAGMENTS = 10

CASE_CHOICES = [
      ("Original", "Original"),
      ("UPPER", "UPPER"),
      ("lower", "lower"),
      ("Title", "Title"),
]

SANITIZING_CHOICES = [("No change", 1), ("Remove problematic chars", 2),
                      ("Use only alphanumerics plus - and _", 3)]


class RenameWindow(tk.Tk):

    def __init__(self, filename, fragments):
        super().__init__()
        self.abort = False
        self.do_rename = False
        self.title(f"Rename {filename}")
        self.filename = filename
        filename = str(filename)
        self.fragments = fragments

        mainframe = ttk.Frame(self, padding="20 20 20 20")
        mainframe.grid(column=0, row=0, sticky=("N", "W", "E", "S"))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        ofile_frame = ttk.Frame(mainframe, padding="10 10 10 10")
        ofile_frame.grid(row=0, column=0, sticky="NW")
        ttk.Label(ofile_frame, text="Original:", font="TkHeadingFont 20").grid(column=0,
                                                                               row=0,
                                                                               sticky="W")
        ttk.Label(ofile_frame,
                  text=((filename[:60] + "..." if len(filename) > 60 else filename)),
                  borderwidth=0,
                  relief="solid",
                  font="Courier 20").grid(column=1, sticky="W")

        nfile_frame = ttk.Frame(mainframe, padding="10 10 10 10")
        nfile_frame.grid(sticky="W")
        ttk.Label(nfile_frame, text="New:", font="TkHeadingFont 20").grid(column=0,
                                                                          sticky="W")
        self.new_filename_text = tk.Text(nfile_frame,
                                         borderwidth=1,
                                         relief="solid",
                                         font="Courier 20 ",
                                         width=50,
                                         height=3,
                                         bg="white")
        self.new_filename_text.grid(column=1, sticky="W")

        ttk.Label(mainframe, text="Choose fragments:",
                  font="systemApplicationFont 20").grid(row=3, sticky="W")

        N = min(N_FIRST_FRAGMENTS, len(fragments))
        self.N = N
        self.checkbuttons = [None] * N
        self.fragment_selected = [0] * N
        for i in range(N):
            self.fragment_selected[i] = tk.IntVar()
            self.checkbuttons[i] = ttk.Checkbutton(
                  mainframe,
                  text=fragments[i],
                  variable=self.fragment_selected[i],
                  command=self.calculate_new_filename,
            )
            self.checkbuttons[i].grid(sticky="W")

        ttk.Label(mainframe, text="", font="Helvetica 16").grid(padx=10, pady=1)

        ttk.Label(mainframe, text="Options:", font="HelveticaBold 20").grid(padx=5,
                                                                            pady=1,
                                                                            sticky="W")

        ttk.Label(mainframe,
                  text="How much to sanitize new filename",
                  font="Helvetica 16").grid(padx=1, pady=1, sticky="W")
        self.sanitizing_level = tk.IntVar()
        self.sanitizing_level.set(1)
        for (text, val) in SANITIZING_CHOICES:
            ttk.Radiobutton(mainframe,
                            text=text,
                            variable=self.sanitizing_level,
                            value=val,
                            command=self.calculate_new_filename).grid(padx=10, sticky="W")

        ttk.Label(mainframe, text="Choose filename case",
                  font="Helvetica 16").grid(padx=1, pady=1, sticky="W")
        self.case_choice = tk.StringVar()
        self.case_choice.set("Original")
        for (text, val) in CASE_CHOICES:
            ttk.Radiobutton(mainframe,
                            text=text,
                            variable=self.case_choice,
                            value=val,
                            command=self.calculate_new_filename).grid(padx=10, sticky="W")

        buttonframe = ttk.Frame(mainframe, padding="10 10 10 10")
        ttk.Button(buttonframe, text="Rename", command=self.ok_pressed).grid(column=0,
                                                                             row=0)
        ttk.Button(buttonframe, text="Cancel", command=self.cancel).grid(column=1, row=0)
        ttk.Button(buttonframe, text="Abort entirely", command=self.abort).grid(column=2,
                                                                                row=0)

        buttonframe.grid(column=0, columnspan=3, sticky="S W")
        self.new_filename = None
        self.calculate_new_filename()

    def ok_pressed(self):
        self.do_rename = True
        self.destroy()

    def cancel(self):
        self.new_filename = None
        self.do_rename = False
        self.destroy()

    def abort(self):
        self.abort = True
        self.destroy()

    # All this fragmentation logic shouldn't be here!
    def calculate_new_filename(self):
        new_filename = compose_new_filename(self.fragments,
                                            case_choice=self.case_choice.get(),
                                            sanitizing_choice=self.sanitizing_level.get(),
                                            n_fragments=self.N,
                                            fragment_selected=self.fragment_selected)
        #   Sanitize
        self.new_filename = new_filename[:MAX_FILENAME_LENGTH] + ".pdf"
        self.new_filename_text.delete("1.0", "end")
        self.new_filename_text.insert("1.0", new_filename[:MAX_FILENAME_LENGTH] + ".pdf")
