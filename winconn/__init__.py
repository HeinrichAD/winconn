# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
'''
This file is part of WinConn http://stanev.org/winconn
Copyright (C) 2012 Alex Stanev <alex@stanev.org>

WinConn is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

WinConn is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with WinConn.  If not, see <http://www.gnu.org/licenses/>.
'''
### END LICENSE

import argparse

import gettext
from gettext import gettext as _
gettext.textdomain('winconn')

from gi.repository import Gtk, GObject # pylint: disable=E0611

from winconn import WinconnWindow
from winconn_lib import set_up_logging, get_version

GObject.threads_init()

def parse_options():
    """Support for command line options"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%%prog %s' % get_version())
    parser.add_argument(
        "-v", "--verbose", action="count", dest="verbose",
        help=_("Show debug messages (-vv debugs winconn_lib also)"))
    parser.add_argument(
        "-n", "--new",
        help=_("Create new application connection"))
    parser.add_argument(
        "-e", "--execute", dest="FILE",
        help=_("Execute saved session from file in ~/.config/winconn"))
    args = parser.parse_args()

    set_up_logging(args)

def main():
    'constructor for your class instances'
    parse_options()

    # Run the application.
    window = WinconnWindow.WinconnWindow()
    window.show()
    Gtk.main()
