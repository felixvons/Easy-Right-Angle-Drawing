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

import configparser
import xml.etree.ElementTree as ET

from pkg_resources import packaging
from urllib.request import urlopen


class VersionPlugin:

    @staticmethod
    def get_repository_version_name(xml_url: str, plugin_name: str) -> tuple:
        """ Reads plugins.xml content and returns version number from given plugin.

            :param xml_url: web url
            :param plugin_name: name of plugin
            :returns: version string/None and error text
        """
        try:
            tree = ET.parse(urlopen(xml_url))
        # url nicht erreicht
        # TODO: entsprechende exceotions erforderlich!
        except Exception as e:
            return None, str(e)

        for item in tree.getroot():
            if item.tag != 'pyqgis_plugin':
                continue
            if item.get('name') == plugin_name:
                version_str = item.attrib['version']
                version_obj = packaging.version.parse(version_str)
                return version_obj, ""

        return None, f"plugin '{plugin_name}' not found on xml_url"

    @staticmethod
    def get_repository_version_zipname(xml_url: str, zip_file: str) -> tuple:
        """ Reads plugins.xml content and returns version number and error string from given zip file name

            :param xml_url: web url
            :param zip_file: zip file name (e.g. "plugin.zip")
            :returns: version string/None and error text
        """
        try:
            tree = ET.parse(urlopen(xml_url))
        # url nicht erreicht
        # TODO: entsprechende exceptions erforderlich!
        except Exception as e:
            err = f"Bei der Abfrage ist ein Fehler aufgetreten:\n\n{str(e)}"
            return None, err

        for item in tree.getroot():
            if item.tag != 'pyqgis_plugin':
                continue

            version = item.attrib['version']

            for child in item:

                if child.tag != 'file_name':
                    continue

                if child.text == zip_file:
                    version_str = version
                    version_obj = packaging.version.parse(version_str)
                    return version_obj, ""

        return None, f"plugin '{zip_file}' not found"

    @classmethod
    def get_local_version(cls, metadata_path: str) -> str:
        """ Reads local version string from local metadata.txt

            :param metadata_path: path to metadata.txt file
        """
        version_str = cls.get_meta_value(metadata_path, 'version')
        version_obj = packaging.version.parse(version_str)
        return version_obj

    @classmethod
    def get_local_zipname(cls, metadata_path) -> str:
        """ Reads zip file name from local metadata.txt

            :param metadata_path: path to metadata.txt file
        """

        return cls.get_meta_value(metadata_path, 'zipFilename')

    @staticmethod
    def get_version_int(version: str) -> int:
        """ converts version str e.g. "1.0.1" into version integer 101 """

        version = version.replace(".", "").replace(",", "")
        version = int(version)
        return version

    @staticmethod
    def get_meta_value(metadata_path: str, key: str) -> str:
        """ Reads a value from metadata.txt.

            :param metadata_path: path to metadata.txt file
            :param key: key in 'general' section
        """

        config = configparser.ConfigParser()
        config.read(metadata_path, encoding='utf-8')
        return config['general'][key]
