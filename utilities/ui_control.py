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
from ..plugin import EasyRightAngleDraw


def load_tool_bar(plugin: EasyRightAngleDraw):
    """ loads default action for your plugin """
    from qgis.PyQt.QtGui import QIcon

    from ..modules.draw import RightAngleTool

    icon = QIcon(plugin.get_icon_path("icon.png"))
    plugin.draw_action = plugin.add_action(
        "EasyRightAngleDraw",
        icon,
        False,
        lambda *_, p=plugin: RightAngleTool.draw(p),
        True,
        plugin.plugin_menu_name,
        plugin.plugin_menu_name,
        True,
        True)
    plugin.draw_action.setCheckable(True)
