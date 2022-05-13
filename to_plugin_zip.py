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
import os
import sys
import getopt


def run():
    # Annahme, dass hier eine Plugin-ZIP erstellt werden soll

    repo_location = os.path.dirname(__file__)  # dieses Verzeichnis
    zip_file_name = os.path.basename(repo_location)  # Wie soll die ZIP-Datei heißen?
    # Wo soll diese ZIP-Datei gespeichert werden?
    destination_zip_file = os.path.join(repo_location, zip_file_name + ".zip")

    return build(zip_file_name, repo_location, destination_zip_file)


def build(zip_file_name, repo_location, destination_zip_file):
    ignore_paths = [
        # root folder
        ".idea", ".editorconfig", ".gitignore", ".gitignore", ".git", ".vscode",
        ".mypy_cache"
    ]

    p = os.path.dirname(__file__)
    sys.path.insert(0, p)

    from submodules.basics.create_plugin_zip import CreatePluginZip
    obj = CreatePluginZip(zip_file_name,
                          repo_location,
                          destination_zip_file,
                          ignore_paths=ignore_paths,
                          overwrite=True)
    return obj


def from_sys_args(argv):
    """ Run this script from console with or without argument.

        .. code-block::

            python path/to/plugin_template/to_plugin_zip.py -o "path/to/plugin.zip"

        Arguments:

            * `-o` with destination zip file name

    """
    if not argv:
        return run()

    opts, args = getopt.getopt(argv, "o:", [])
    map_ = dict(opts)
    destination_zip_file = map_['-o']
    zip_file_name = os.path.basename(destination_zip_file)
    zip_file_name = ".".join(zip_file_name.split(".")[:-1])
    repo_location = os.path.dirname(__file__)  # dieses Verzeichnis

    return build(zip_file_name, repo_location, destination_zip_file)


if __name__ == "__main__":
    from_sys_args(sys.argv[1:])
