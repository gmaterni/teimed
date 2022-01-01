#!/usr/bin/env python3
# coding: utf-8

# FONT_GENERAL = ('Helvetica', 14, 'normal')


########
# EDITOR
########
editor_theme = 0
if editor_theme == 0:
    BG_TXT = "#222222"
    FG_TXT = "#ffffff"
    BG_LNUM = "#333333"
    FG_LNUM = "#ffffff"
    BG_LOG = "#000000"
    FG_LOG = "#ffff00"
else:
    BG_TXT = "#ffffff"
    FG_TXT = "#000000"
    BG_LNUM = "#aaaaaa"
    FG_LNUM = "#000000"
    BG_LOG = "#ffffff"
    FG_LOG = "#000000"

editor_size = 0
if editor_size == 0:
    FONT_EDIT = ('Helvetica', 14, 'normal')
    FONT_TXT = ('Helvetica', 14, 'normal')
    FONT_LNUM = ('Helvetica', 14, 'normal')
    FONT_LOG = ('Monospace', 12, 'normal')
    FONT_MENU = ('Helvetica', 16, 'bold')
    FONT_LABEL = ('Helvetica', 14, 'bold')
    FONT_BOTTOM = ('Helvetica', 18, 'bold')
    FONT_LIST = ('Monospace', 14, 'normal')
    FONT_LBL_BOX = ('Helvetica', 14, 'bold')
    FONT_BTN_BOX = ('Helvetica', 14, 'normal')
    FONT_BTN_CLOSE = ('Helvetica', 14, 'bold underline')
else:
    FONT_EDIT = ('Helvetica', 16, 'normal')
    FONT_TXT = ('Helvetica', 16, 'normal')
    FONT_LNUM = ('Helvetica', 16, 'normal')
    FONT_LOG = ('Monospace', 14, 'normal')
    FONT_MENU = ('Helvetica', 14, 'bold')
    FONT_LABEL = ('Helvetica', 12, 'bold')
    FONT_BOTTOM = ('Helvetica', 16, 'bold')
    FONT_LIST = ('Monospace', 12, 'normal')
    FONT_LBL_BOX = ('Helvetica', 12, 'bold')
    FONT_BTN_BOX = ('Helvetica', 12, 'normal')
    FONT_BTN_CLOSE = ('Helvetica', 12, 'bold underline')

# BG_SEP = "#111111"
# FG_SEP = "#FFFFFF"


BG_LBL = "#111111"
FG_LBL = "#FFff00"

BG_WIN = "#333333"
FG_WIN = "#FFFFF"

BG_INS = "#ff0000"
BG_SEL = "#00ff00"

BG_BAR = "#00ff00"
BG2_BAR = "#FF0000"


BG_MENU = "#000000"
FG_MENU = "#00ff00"
BG2_MENU = "#00ff00"
FG2_MENU = "#000000"

BG_MENU_LBL = "#000000"
FG_MENU_LBL = "#ff4500"
BG2_MENU_LBL = "#ff4500"
FG2_MENU_LBL = "#000000"

BG_BOTTOM = "#222222"
BG_BOTTOM_LBL = "#222222"
FG_BOTTOM_LBL = "#FF4500"

BG_CURSOR = "#ff0000"
CURSOR_TEXT = 'arrow'
# CURSOR_EDIT='crosshair'
CURSOR_EDIT = 'xterm red'
CURSOR_MENU = 'arrow'

BG_BLIST = "#333333"
FG_BLIST = "#00ff00"
BG2_BLIST = "#00ff00"
FG2_BLIST = "#000000"

# tag di controllo sull'editor
BG_TAG = '#006622'
FG_TAG = '#ffffff'

BG2_TAG = '#ffff00'
FG2_TAG = '#000000'

FIND_TAGS = ["findaa", "findbb"]
