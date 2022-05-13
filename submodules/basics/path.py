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
import shutil

from pathlib import Path

from typing import List, Optional, Union, Tuple


def get_files(path, recursive: bool = True, ignore_paths: Optional[List[str]] = None):
    """ Get all files from folder.

        .. code-block:: python

            # walk through each folder and prints file and folder
            for file in get_files("C:/"):
                print("file", file")


        :param path: start path
        :param recursive: Can go in sub folders?
        :param ignore_paths: List of paths to ignore.
                             Current path in iteration is checked with "startswith" in `ignore_paths`.
    """
    if ignore_paths is None:
        ignore_paths = []

    ignored_roots = []

    def skip_root(file_):
        for x in ignored_roots:
            if file_.startswith(x):
                return True

        return False

    for root, _, files in os.walk(path):

        # current iter path should be ignored
        root = os.path.normpath(root)
        if root in ignore_paths:
            ignored_roots.append(root)
            continue

        if skip_root(root):
            continue

        for file in files:

            if skip_root(file):
                continue

            path = os.path.normpath(os.path.join(root, file))

            # file path should be ignored
            if path in ignore_paths:
                continue

            yield path

        # do not go deeper in folder structure
        if not recursive:
            break


def check_storage_capacity(path: Union[str, Path], min_storage: float) -> Tuple[bool, float]:
    """ Checks if the needed space is free

        :param path: path
        :param min_storage: minimum free storage on drive
        :return: bool (0, True =  enough there), free space in megabytes (1)
    """
    try:
        directory = path if isinstance(path, str) else str(path.parent)
        free_storage = [i / 1000000 for i in shutil.disk_usage(directory)]
        free_storage = free_storage[-1]

        if free_storage < min_storage:
            return False, free_storage

        return True, free_storage

    except FileNotFoundError:
        return False, 0.0
