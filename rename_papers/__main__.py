#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Name:         __main__
# Purpose:      Interactively rename a PDF file containing a paper to its title.
# Author:       Tom Fawcett <tfawcett@acm.org>
# Copyright:    (c) 2019 by Tom Fawcett
# Created:      Fri Sep 15 2017 by Tom Fawcett (<tfawcett@acm.org>)
# ----------------------------------------------------------------------------
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from .fragments import get_fragments
from .gui import RenameWindow


def main():
    args = parse_args(sys.argv)
    logging.basicConfig(
          format="%(asctime)s - %(message)s",
          datefmt="%y-%b-%d %H:%M:%S",
          level=(logging.DEBUG if args.debug else logging.INFO),
    )
    logging.info(f"Invocation: {' '.join(sys.argv)}")
    for infile in args.infiles:
        infile = Path(infile)
        if not infile.exists():
            logging.warning(f"File {infile} doesn't exist, skipping")
            continue
        fragments = get_fragments(infile)
        if not fragments:
            continue
        logging.debug(f"Got fragments: {fragments}")
        win = RenameWindow(filename=infile, fragments=fragments)
        win.mainloop()

        if win.abort:
            print("Run aborted")
            exit()
        new_name = win.new_filename
        if (not win.do_rename) or new_name is None or new_name == "":
            logging.info(f"Canceled rename of {infile}")
            continue
        else:
            logging.debug(f"Calling do_rename({infile}, {new_name})")
            do_rename(infile, new_name)


def do_rename(file1, file2):
    file1 = Path(file1)
    file2 = Path(file2)
    if file2.exists():
        logging.error(f"{file2} exists -- refusing to do rename")
        # TODO: Move this into the gui so it doesn't return from OK if file2 exists
        return
    else:
        logging.info(f"Renaming {file1} to {file2}")
        file1.rename(file2)



def parse_args(args):
    """Parse the command line args."""
    parser = ArgumentParser(
          description="""Rename PDF file(s) containing research papers to their titles.
          This script scans each file, extracts the text, and tries to find a title at the
          beginning.  It then presents fragments from which to compose the filename, which you
          select along with some options for text conversion.  The second frame contains the
          assembled filename.  When you click OK it renames the file.
""")
    parser.add_argument("infiles", nargs="+", type=str, help="PDF files to rename")
    parser.add_argument("--debug",
                        default=False,
                        action="store_true",
                        help="Turn on debugging logging")
    return parser.parse_args(args)


if __name__ == "__main__":
    main()
