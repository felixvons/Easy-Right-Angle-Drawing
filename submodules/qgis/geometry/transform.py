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

from qgis.core import (QgsCoordinateReferenceSystem, QgsCoordinateTransform,
                       QgsGeometry, QgsProject)


def get_transform(src_coordinate_system: QgsCoordinateReferenceSystem,
                  dst_coordinate_system: QgsCoordinateReferenceSystem) -> QgsCoordinateTransform:
    """ get transform object.
        Transforming geometry is needed, when you want to use a geometry in a different coordinate reference system.

        :param src_coordinate_system: source coordinate system
        :param dst_coordinate_system: destination coordinate system
        :return: transform object
    """
    transform_params = QgsCoordinateTransform(
        src_coordinate_system,
        dst_coordinate_system,
        QgsProject.instance())

    return transform_params


def transform_geometry(geometry: QgsGeometry, src_coordinate_system: QgsCoordinateReferenceSystem,
                       dst_coordinate_system: QgsCoordinateReferenceSystem) -> QgsGeometry:
    """ Transform Geometry-Points to another coordinate
        reference system

        :param geometry: geometry to transform
        :param src_coordinate_system: source coordinate system
        :param dst_coordinate_system: destination coordinate system
        :return: converted point
    """

    # get geometry from point
    copy_geometry = QgsGeometry(geometry)

    transform_params = get_transform(src_coordinate_system, dst_coordinate_system)
    copy_geometry.transform(transform_params)

    return copy_geometry
