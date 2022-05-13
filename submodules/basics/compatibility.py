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

import sys
import os


def qgis_unload_keyerror(plugin_dir: str) -> None:
    """ A special KeyError workaround in QGIS unloading mechanism of plugins.

        :param plugin_dir: plugin path
    """
    from collections import OrderedDict
    from qgis import utils

    _loaded_qgs_mod = {}
    count = 0

    # Stored Modules from QGIS
    plugin_dir = os.path.basename(os.path.normpath(plugin_dir))
    loaded_qgs_mod = [i for i in utils._plugin_modules[plugin_dir]]

    # Stored Modules from sys
    loaded_sys_mod = [i for i in sys.modules if i.startswith(plugin_dir)]

    for smod in loaded_sys_mod:
        if smod not in loaded_qgs_mod:
            loaded_qgs_mod.append(smod)  # Add to qgis-list

    for qmod in loaded_qgs_mod.copy():
        if qmod not in loaded_sys_mod:
            loaded_qgs_mod.remove(qmod)  # Del from qgis-list

    for mod in loaded_qgs_mod.copy():
        path = mod.split(".")
        path_len = len(mod.split("."))
        if path_len > 1:
            key = path[0] + path[1]
        elif path_len == 1:
            key = path[0]
        else:
            key = 'ERROR'
        key = str(path_len) + "/" + key + "/" + str(count)
        count += 1
        _loaded_qgs_mod.setdefault(key, mod)

    _loaded_qgs_mod = OrderedDict(sorted(_loaded_qgs_mod.copy().items(),
                                         reverse=True))
    sorted_list = [value for key, value in _loaded_qgs_mod.items()]
    utils._plugin_modules[plugin_dir] = sorted_list
