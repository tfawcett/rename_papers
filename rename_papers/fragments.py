# -*- coding: utf-8 -*-
# Name:         fragments.py
# Purpose:      Various functions for breaking and reassembling text fragments.
# Author:       Tom Fawcett <tfawcett@acm.org>
# Copyright:    (c) 2019 by Tom Fawcett
# Created:      Fri Sep 15 2017 by Tom Fawcett (<tfawcett@acm.org>)
# ----------------------------------------------------------------------------
import logging
import re
import string
from subprocess import CalledProcessError, run

# =====  CONSTANTS

# Name of the PDF-to-text executable
PDF_TO_TEXT = "pdftotext"

#  How many top lines of pdftotext output to consider
TOP_LINES_TO_SCAN = 20

#  Number of elements to be presented to the user
ELEMENTS_TO_PRESENT = 10

PROBLEMATIC_CHARS = "!:;?'\"*/\\\t\n."

#  StackOverflow snippet by jfs:
SAFECHARS = bytearray(('_-' + string.digits + string.ascii_letters).encode())
ALLCHARS = bytearray(range(0x100))
DELETECHARS = bytearray(set(ALLCHARS) - set(SAFECHARS))

# Note: strings have RE interpretation in here
title_words_ignore = r"""
JOURNAL
PROCEEDINGS
LECTURE NOTES
ACCEPTED MANUSCRIPT
TRANSACTIONS
ORIGINAL PAPER
OPEN ACCESS
SUBMITTED
PUBLISH
ORIGINAL ARTICLE
REGULAR PAPER
ScienceDirect
Open Access
IEEE TRANSACTIONS
REGULAR ARTICLE
AUTHOR
PRINTED
MANUSCRIPT
EDITOR
IN PRESS
TO APPEAR
PREPRINT
doi
arXiv
AVAILABLE ONLINE
COPYRIGHT
19\d\d
20\d\d
VOL(\. | UME)
 NO\.
""".split("\n")

title_words_ignore = [string for string in title_words_ignore if string != ""]
RE_NONTITLE_WORDS = re.compile("(" + "|".join(title_words_ignore) + ")")

RE_UNCAPITALIZED_WORDS = re.compile(r"\b(and|a|of|to|for|the|in|with|an|by|on)\b",
                                    re.IGNORECASE)


def get_fragments(infile):
    try:
        # Run pdftotext and capture output into result.stdout
        result = run(
              [PDF_TO_TEXT, "-raw", "-f", "1", "-l", "2", infile, "-"],
              text=True,
              capture_output=True,
        )
    except CalledProcessError as e:
        logging.warning("Got error from subprocess:", e)
        return ["--error, see log--"]
    return get_text_fragments(result.stdout)


def get_text_fragments(text):
    fragments = []
    title_seen = False
    for (line_i, line) in enumerate(text.splitlines()):
        if line_i > TOP_LINES_TO_SCAN:
            break
        line = only_printable(line.strip())
        if line == "" or line.isdigit():
            continue
        elif len(line) < 3:
            continue
        logging.debug(f"Candidate: {line}")
        if title_seen or RE_NONTITLE_WORDS.search(line):
            #  TODO: Move this defaulting into the GUI
            checkbox_default = False
        else:
            checkbox_default = True
            title_seen = True
        fragments.append(line)
        if len(fragments) == ELEMENTS_TO_PRESENT:
            break
    return fragments


def clean_and_assemble_fragments(fragments, used_indices):
    fragments_used = [fragments[idx] for idx in used_indices]
    tokens = []
    for fragment in fragments_used:
        #        fragment_split = re.split(r"\s+", fragment)
        fragment_split = fragment.split()
        tokens.extend(fragment_split)
    new_filename = " ".join(tokens)
    return new_filename


def only_printable(str0):
    return "".join(filter(lambda char: char in string.printable, str0))


def make_titlecase(string):
    """
    Convert string s to title case(my version).
    Like python's, title() method but keeps small words lower cased.
    """
    string = string.title()

    def lower_case(m):
        return m.group(1).lower()

    string = re.sub(RE_UNCAPITALIZED_WORDS, lower_case, string)
    string = string[0].upper() + string[1:]

    return string


def compose_new_filename(fragments, case_choice, sanitizing_choice, n_fragments,
                         fragment_selected):
    used_indices = [i for i in range(n_fragments) if fragment_selected[i].get()]
    new_filename = clean_and_assemble_fragments(fragments, used_indices)
    # -----   Sanitize
    if sanitizing_choice == 1:    # No change
        pass
    elif sanitizing_choice == 2:    # Just remove problematic chars
        for special in PROBLEMATIC_CHARS:
            new_filename = new_filename.replace(special, "")
    elif sanitizing_choice == 3:
        # First replace spaces with underscore, then remove everything else
        new_filename = new_filename.replace(" ", "_")
        new_filename = new_filename.encode('ascii', 'ignore').translate(
              None, DELETECHARS).decode()
    # -----  Case choice
    if case_choice == "UPPER":
        new_filename = new_filename.upper()
    elif case_choice == "lower":
        new_filename = new_filename.lower()
    elif case_choice == "Title":
        new_filename = make_titlecase(new_filename)
        #  else just keep original case.
    return new_filename


# end of fragments.py
