# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
'''
This file is part of WinConn.

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

import gettext
from gettext import gettext as _
gettext.textdomain('winconn')

from gi.repository import Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('winconn')

from winconn_lib import Window
from winconn.AboutWinconnDialog import AboutWinconnDialog
from winconn.PreferencesWinconnDialog import PreferencesWinconnDialog

from collections import OrderedDict
from time import time

import os
import os.path
from subprocess import Popen
from winconn_lib import Commons

from quickly import prompts

# See winconn_lib.Window.py for more details about how this class works
class WinconnWindow(Window):
    __gtype_name__ = 'WinconnWindow'
    common = None
    
    def readApps(self):
        for lApp in self.common.getApp():
            self.ui.lsApps.append(lApp)
        
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(WinconnWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutWinconnDialog
        self.PreferencesDialog = PreferencesWinconnDialog
        
        # connect tree to values
        cell = Gtk.CellRendererText()
        col = self.ui.tvApps.get_column(0)        
        col.pack_start(cell, True)
        col.add_attribute (cell, 'text', 0)
        
        col = self.ui.tvApps.get_column(1)
        col.pack_start(cell, True)
        col.add_attribute (cell, 'text', 1)

        col = self.ui.tvApps.get_column(2)
        col.pack_start(cell, True)
        col.add_attribute (cell, 'text', 2)
        
        self.common = Commons.Commons()
        self.readApps()

    def tbExec_clicked(self, widget, row=None, data=None):
        if self.ui.tsApp.count_selected_rows() == 0:
            self.ui.lStatus.set_text(_('No application selected'))
            return

        cmd = self.common.buildCmd()
        if cmd is not None:
            # TODO check return code for error
            print(cmd)
            proc = Popen(cmd)
            proc.wait()
        
    def tbNew_clicked(self, widget):
        self.ui.tsApp.unselect_all()
        self.common.init_App()
        self.show_App()
        self.ui.notebook.set_current_page(1)
        
    def tbDel_clicked(self, widget):
        tm, ti = self.ui.tsApp.get_selected()
        if ti is None:
            self.ui.lStatus.set_text(_('No application selected'))
            return

        response = prompts.yes_no('WinConn', _("Are you sure you want to delete %s ?") % self.common.get_App_opt('name'))
        if response == Gtk.ResponseType.YES:
            self.common.delApp()
            self.ui.lsApps.remove(ti)

    def tbQuit_clicked(self, widget):
        self.destroy()

    def bCancel_clicked(self, widget):
        self.ui.notebook.set_current_page(0)
        self.common.init_App()
        self.ui.tsApp.unselect_all()

    def bSave_clicked(self, widget, data=None):
        sis = 'secondary-icon-stock'
        
        #build our conf
        self.common.init_App()
        self.common.set_App_opt('name', self.ui.eName.get_text())
        self.common.set_App_opt('app', self.ui.eApp.get_text())
        self.common.set_App_opt('server', self.ui.eSrv.get_text())
        self.common.set_App_opt('port', self.ui.ePort.get_text())
        self.common.set_App_opt('user', self.ui.eUser.get_text())
        self.common.set_App_opt('pass', self.ui.ePass.get_text())
        self.common.set_App_opt('domain', self.ui.eDomain.get_text())
        self.common.set_App_opt('folder', self.ui.eFolder.get_text())
        self.common.set_App_opt('compress', self.ui.sComp.get_active())
        self.common.set_App_opt('clipboard', self.ui.sClip.get_active())
        self.common.set_App_opt('sound', self.ui.sSound.get_active())
        self.common.set_App_opt('remotefx', self.ui.sRFX.get_active())
           
        # check our input values
        valid = True
        # Name
        if self.common.get_App_opt('name') == '':
            self.ui.eName.set_property(sis, Gtk.STOCK_DIALOG_WARNING)
            valid = False
        else:
            self.ui.eName.set_property(sis, None)
        
        # Application
        if self.common.get_App_opt('app') == '':
            self.ui.eApp.set_property(sis, Gtk.STOCK_DIALOG_WARNING)
            valid = False
        else:
            self.ui.eApp.set_property(sis, None)
            
        # Server
        if self.common.get_App_opt('server') == '':
            self.ui.eSrv.set_property(sis, Gtk.STOCK_DIALOG_WARNING)
            valid = False
        else:
            self.ui.eSrv.set_property(sis, None)
        
        # Port
        try:
            p = int(self.common.get_App_opt('port'))
            if p <= 0 or p >= 65535:
                raise ValueError
            self.ui.ePort.set_property(sis, None)
        except ValueError:
            self.ui.ePort.set_property(sis, Gtk.STOCK_DIALOG_WARNING)
            valid = False
        
        # User
        if self.common.get_App_opt('user') == '':
            self.ui.eUser.set_property(sis, Gtk.STOCK_DIALOG_WARNING)
            valid = False
        else:
            self.ui.eUser.set_property(sis, None)
        
        # Folder
        if self.common.get_App_opt('folder') and not os.path.isdir(self.common.get_App_opt('folder')):
            self.ui.eFolder.set_property(sis, Gtk.STOCK_DIALOG_WARNING)
            valid = False
        else:
            self.ui.eFolder.set_property(sis, None)
        
        if not valid:
            self.ui.lStatus.set_text(_('Please check your application configuration'))
            return

        if self.ui.tsApp.count_selected_rows() == 0:
            # this is a new savefile
            self.common.set_App_opt('conf', str(int(round(time())))+'.winconn')

            self.ui.lsApps.append(self.common.get_App_opt())
            self.ui.lStatus.set_text(_('New application added successfully'))
        else:
            # this is current App update
            tm, ti = self.ui.tsApp.get_selected()
            # get conf, must be always the last col
            self.common.set_App_opt('conf', tm.get_value(ti, tm.get_n_columns()-1))
            lApp = self.common.get_App_opt()
            for i in range(0, tm.get_n_columns()-1):
                self.ui.lsApps.set_value(ti, i, lApp[i])
            self.ui.lStatus.set_text(_('Application updated successfully'))
            
        self.common.setApp()
        
    def show_App(self):
        self.ui.eName.set_text(self.common.get_App_opt('name'))
        self.ui.eApp.set_text(self.common.get_App_opt('app'))
        self.ui.eSrv.set_text(self.common.get_App_opt('server'))
        self.ui.ePort.set_text(self.common.get_App_opt('port'))
        self.ui.eUser.set_text(self.common.get_App_opt('user'))
        self.ui.ePass.set_text(self.common.get_App_opt('pass'))
        self.ui.eDomain.set_text(self.common.get_App_opt('domain'))
        self.ui.eFolder.set_text(self.common.get_App_opt('folder'))
        self.ui.sComp.set_active(self.common.get_App_opt('compress'))
        self.ui.sClip.set_active(self.common.get_App_opt('clipboard'))
        self.ui.sSound.set_active(self.common.get_App_opt('sound'))
        self.ui.sRFX.set_active(self.common.get_App_opt('remotefx'))

    def tsApp_changed(self, widget):
        tm, ti = self.ui.tsApp.get_selected()
        if ti is None:
            return
        
        self.common.init_App()
        for i in range(0, tm.get_n_columns()):
            self.common.set_App_opt(i, tm.get_value(ti, i))

        self.show_App()

        self.ui.notebook.set_current_page(1)
        self.ui.lStatus.set_text('')
        
    def eFolder_icon_press(self, widget, icon=None, data=None):
        response, path = prompts.choose_directory()
        if response == Gtk.ResponseType.OK:
            widget.set_text(path)
