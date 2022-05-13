# -*- coding: utf-8 -*-
"""
/***************************************************************************
        copyright            : (C) 2022 Felix von Studsinske
        email                : felix.vons@gmail.com
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

import os.path
import os
import shutil
import sys

from time import time
from datetime import datetime

from pathlib import Path

from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from qgis.PyQt.QtWidgets import QMenu, QMessageBox, QApplication, QAction
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import pyqtSignal

from typing import List, Optional

from .submodules.basics.versions_reader import VersionPlugin
from .submodules.basics.compatibility import qgis_unload_keyerror

from .submodules.module_base.base_class import ModuleBase, Plugin


class EasyRightAngleDraw(Plugin):
    """ Main class for this plugin.

        Attachments when contacting support are stored in:
        * Path to qgis profile/_temp_files/plugin name.
        * This folder will be cleared on startup and end.

        Qt Signals:
        * pluginReloaded: add your callables to trigger, when user triggered manual reloading

        :param iface: qgis interface (QMainWindow, layer handling, etc.)
        :param kwargs: dictionary with keyword arguments, if empty -> then QGIS handle this plugin, else an other
                       ModuleBase loads this
    """
    pluginUnloaded = pyqtSignal(name="pluginUnloaded")
    pluginReloaded = pyqtSignal(name="pluginReloaded")
    versionRead = pyqtSignal(ModuleBase, name="versionRead")
    feedbackClicked = pyqtSignal(ModuleBase, name="feedbackClicked")

    def __init__(self, iface: QgisInterface, *args, **kwargs: dict):

        self._iface: QgisInterface = iface

        # Plugin files/folders variables
        self.plugin_dir = os.path.normpath(os.path.normcase(os.path.dirname(__file__)))
        self.meta_file = os.path.join(self.plugin_dir, 'metadata.txt')
        self.icons_dir = os.path.join(self.plugin_dir, 'templates', 'icons')
        self.plugin_version = VersionPlugin.get_local_version(self.meta_file)
        self.plugin_name = VersionPlugin.get_meta_value(self.meta_file, "name")
        self.plugin_menu_name = VersionPlugin.get_meta_value(self.meta_file, "name_menu_bar")
        self.log_filename = f"{self.plugin_name}_{str(self.plugin_version).replace('.', '_')}"
        self.log_dir = os.path.join(QgsApplication.qgisSettingsDirPath(), '_logs')
        self.temp_files = os.path.join(QgsApplication.qgisSettingsDirPath(), '_temp_files', self.log_filename)

        self.menu_bar: Optional[QMenu] = kwargs.get("menu_bar", None)
        self.menu_bar_action: Optional[QAction] = kwargs.get("menu_bar_action", None)

        self.zip_file_name = VersionPlugin.get_local_zipname(self.meta_file)
        self.repo_version = self.repo_version_error = None

        super().__init__(*args, log_name=self.log_filename,
                         name=self.plugin_name, **kwargs)

        self.connect(self.pluginUnloaded, self.reloaded)

        if self.is_qgis_plugin():
            self.connect(self.iface.mapCanvas().mapToolSet, self.check_map_tool_changed)

    def check_map_tool_changed(self, new_tool, old_tool):
        for drawing in self.drawings:
            if drawing:
                self.iface.mapCanvas().scene().removeItem(drawing)

        if hasattr(old_tool, "unload_tool"):
            old_tool.unload_tool()
            self.draw_action.setChecked(False)

        self.drawings.clear()

    def is_qgis_plugin(self) -> bool:
        """ is this a module loaded per default from QGIS? """
        path = Path(QgsApplication.qgisSettingsDirPath()) / 'python' / 'plugins'
        path = path / Path(self.plugin_dir).name / Path(__file__).name

        return path == Path(__file__)

    def is_module(self) -> bool:
        """ is this a module loaded by another module? """
        path = Path(QgsApplication.qgisSettingsDirPath()) / 'python' / 'plugins'
        path = path / Path(self.plugin_dir).name / Path(__file__).name

        return not (path == Path(__file__))

    # noinspection PyPep8Naming
    def initGui(self):
        """ Called by QGIS on programm start or loading this plugin.
            At this point you can interacting with QGIS gui, e.g. `self.iface.mainWindow()`.
            Add your own QActions/QToolBars in `utilities.ui_control.load_tool_bar`
        """

        # setup menu bar in QGIS
        menu_bar = self.iface.mainWindow().menuBar()
        if self.is_qgis_plugin():
            # this is a plugin
            self.menu_bar = QMenu(self.plugin_menu_name, menu_bar)
            self.menu_bar_action: QAction = menu_bar.addMenu(self.menu_bar)
        else:
            # this is handled as a module
            # use menu bar from plugin instead
            self.menu_bar = QMenu(self.plugin_menu_name, self.get_main_plugin().menu_bar)
            self.menu_bar_action: QAction = menu_bar.addMenu(self.menu_bar)

        # add log action to menu bar, only if this the plugin object and not a boring module
        if self.is_qgis_plugin():

            tool_tip = ("Das Plugin sowie enthaltene Untermodule werden neugestartet.\n"
                        "Stelle sicher, dass du alle notwendigen Änderungen gespeichert hast.\n\n"
                        "Es können nicht gespeicherte Änderungen verloren gehen!\n\n"
                        "Diese Funktion sollte zur Fehlerbehebung verwendet werden, "
                        "wenn beispielsweise das Plugin komplett abstürzt und nicht mehr reagiert.")
            icon = QgsApplication.getThemeIcon("mActionRefresh.svg")
            self.add_action(f"Plugin (+ Module) neuladen",
                            icon,
                            False,
                            lambda: self.reload(),
                            True,
                            None,
                            None,
                            True,
                            True,
                            tool_tip=tool_tip)

        # Do not add you actions in initGui, keep it clean and use load_tool_bar instead
        from .utilities import ui_control
        ui_control.load_tool_bar(self)

    def reloaded(self):
        self.iface.messageBar().pushSuccess(f"{self.plugin_menu_name}", "QGIS-Plugin erfolgreich neugestartet")

    def reload(self):
        """ reloads this QGIS plugin """
        if not self.is_qgis_plugin():
            return
        from qgis.utils import reloadPlugin, plugins
        module = os.path.basename(self.get_plugin().plugin_dir)
        reloadPlugin(module)
        module = plugins[module]
        module.pluginReloaded.emit()
        self.pluginUnloaded.emit()

    def unload(self, self_unload: bool = False):
        """ Auto-call when plugin will be unloaded from QGIS plugin manager. """
        super().unload()

        QApplication.restoreOverrideCursor()

        # Entferne QActions und QToolBars
        self.iface.mainWindow().menuBar().removeAction(self.menu_bar_action)

        # Entferne Actions
        for action in self._actions:
            self.iface.removePluginMenu(self.plugin_menu_name, action)
            self.iface.removeToolBarIcon(action)

        qgis_unload_keyerror(self.plugin_dir)

        for marker in self.drawings:
            self.iface.mapCanvas().scene().removeItem(marker)
        self.drawings.clear()

    def __repr__(self) -> str:
        if self.is_qgis_plugin():
            managed_by = "QgsApplication(stand-alone)"
            plugin = ""
        else:
            parent = self.get_parent()
            if parent is None:
                managed_by = "self managed, no parent"
                plugin = ""
            else:
                managed_by = self.get_parent().__class__.__name__
                plugin = f", plugin={self.get_plugin().plugin_menu_name}"

        version = getattr(self, "plugin_version", "not set")
        plugin_menu_name = getattr(self, "plugin_menu_name", "not set")

        return f"{self.__class__.__name__}(version={version}, " \
               f"plugin_menu_name={plugin_menu_name}, managed_by={managed_by}{plugin})"
