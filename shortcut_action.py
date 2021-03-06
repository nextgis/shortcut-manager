# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ShortcutManagerDialog
                                 A QGIS plugin
 This plugin create shortcuts in toolbar
                             -------------------
        begin                : 2014-07-18
        git sha              : $Format:%H$
        copyright            : (C) 2014 by NextGIS
        email                : info@nextgis.ru
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import sys
import subprocess
import webbrowser
import functools

from PyQt4.QtGui import QAction, QMessageBox, QDesktopServices
from PyQt4.QtCore import QObject, SIGNAL, QFileInfo, QUrl

from shortcut_utils import getShortcutIcon, getShortcutType

from qgis.core import QgsMessageLog

class ShorcutAction(QAction):
    def __init__(self, iface, shortcut):
        self._iface = iface
        QAction.__init__(self, self._iface.mainWindow())
        
        self._shortcut = shortcut
        
        self.setEnabled(True)
        
        QObject.connect(self._shortcut, SIGNAL("updated()"), self.__shortcutUpdated)
        QObject.connect(self._shortcut, SIGNAL("deleted()"), self.__shortcutDeleted)
        
        self.__shortcutUpdated()
        
        self._iface.addToolBarIcon(self)
        
        self.triggered.connect(self._triggeredFunction)
    
    def __shortcutUpdated(self):
        self.setIcon(getShortcutIcon(self._shortcut.icon, self._shortcut.uri))
        self.setText(self._shortcut.name)
        
        '''
        shortcutType = getShortcutType(self._shortcut.uri)
        if shortcutType == "desktop":
            #self._callbackFunction = functools.partial(self._runApplication, self._shortcut.uri, self._shortcut.directory)
            self._callbackFunction = functools.partial(self._runApplication, self._shortcut.uri)
        elif shortcutType == "web":
            self._callbackFunction = functools.partial(self._runBrowser, self._shortcut.uri)
        else:
            self._callbackFunction = lambda: QMessageBox.information(
                                            self._iface.mainWindow(), 
                                            'Unknown shortcut type',
                                            'Unknown shortcut type',
                                            QMessageBox.Ok)
        '''
        self._callbackFunction = functools.partial(self._runApplication, self._shortcut.uri)
        
    def _triggeredFunction(self):
        self._callbackFunction()
    
    def __shortcutDeleted(self):
        self.setParent(None)
        self._iface.removeToolBarIcon(self)
    '''
    def _runBrowser(self, url):
        try:
            webbrowser.open(url)
        except webbrowser.Error as err:
            QgsMessageLog.logMessage(
                "Shortcuts manager. Error when open shortcut with http url: %s"%url + "\n" + str(err),
                None, QgsMessageLog.CRITICAL)
    '''
        
    def _runApplication(self, app):
        try:
            app = app.encode(sys.getfilesystemencoding())
            
            '''            
            if QUrl(app).host() != u'':
                QDesktopServices.openUrl(QUrl(app))
            else:
                if QFileInfo(app).exists() == True:
                    QDesktopServices.openUrl( QUrl('file:///%s'%app) )
                else:
                    QDesktopServices.openUrl( QUrl(app) )
            
            '''
            if sys.platform.startswith('darwin'):
                if os.path.exists(app) == False or os.access(app, os.X_OK):
                    subprocess.call([app])
                else:
                    subprocess.call(['open', app])
            elif os.name == 'nt':
                os.startfile(app)
            elif os.name == 'posix':
                if os.path.exists(app) == False or os.access(app, os.X_OK):
                    subprocess.Popen([app])
                else:
                    subprocess.Popen(['xdg-open', app])
            
        except Exception as err:
            QgsMessageLog.logMessage(
                "Shortcuts manager. Error when open shortcut for app: %s"%app + "\n" + str(err),
                None, QgsMessageLog.CRITICAL)
            raise err
