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
from math import degrees, radians, cos

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor

from qgis.core import (QgsWkbTypes, QgsTriangle, QgsVectorLayer,
                       QgsPointXY, QgsGeometry, QgsFeature)

from ..submodules.qgis.canvas.maptool_click_snap import MapToolQgisSnap
from ..submodules.qgis.canvas.canvas_drawing import DrawTool


class RightAngleTool:

    def __init__(self, iface, layer: QgsVectorLayer, drawings, max_creations: int = -1):
        self._iface = iface
        self._layer = layer
        self._points = []
        self._draw_tool = DrawTool(self._iface.mapCanvas(), drawings=drawings)
        self._tool = None
        self._max_creations = max_creations
        self._creations = 0

    def start(self):
        self._draw_tool.remove_all_drawings()
        self._tool = MapToolQgisSnap(self._iface, self._layer)
        self._tool.clicked.connect(self._clicked)
        self._tool.aborted.connect(self._aborted)
        self._tool.moved.connect(self._moved)

    def _draw(self, point):
        self._draw_tool.remove_all_drawings()

        if len(self._points) == 1:
            # draw a simple line
            self._draw_tool.create_rubber_band(
                QgsGeometry.fromPolylineXY(self._points + [point]),
                self._layer,
                color=QColor(0, 0, 255),
                line_type=Qt.SolidLine,
                width=0.6
            )

        if len(self._points) == 2:
            # draw pre calculated line
            lines = self._get_lines(self._points + [point])
            for line in lines:
                self._draw_tool.create_rubber_band(
                    QgsGeometry.fromPolylineXY(line),
                    self._layer,
                    color=QColor(0, 0, 255),
                    line_type=Qt.SolidLine,
                    width=0.6
                )

    def _clicked(self, point: QgsPointXY):
        self._draw_tool.remove_all_drawings()

        if not point:
            return

        self._draw(point)

        self._points.append(point)

        if len(self._points) == 3:
            self._finalize()

            self._creations += 1
            self._points.clear()
            if self._creations >= self._max_creations and self._max_creations > -1:
                self._tool.unload_tool()

    def _moved(self, point: QgsPointXY):
        self._draw_tool.remove_all_drawings()
        self._draw(point)

    def _finalize(self):
        lines = self._get_lines(self._points)
        self._draw_tool.remove_all_drawings()

        for line in lines:
            feature = QgsFeature(self._layer.dataProvider().fields())
            feature.setGeometry(QgsGeometry.fromPolylineXY(line))
            if self._layer.isEditable():
                self._layer.addFeature(feature)
            else:
                self._layer.dataProvider().addFeatures([feature])
                self._layer.reload()

    def _get_lines(self, points):
        xa, a, b = points

        length_hypo = a.distance(b)

        triangle = QgsTriangle(xa, a, b)
        angles = triangle.angles()
        angle_new_a = 180 - degrees(angles[1])

        length_b = length_hypo * cos(radians(angle_new_a))
        azimuth = xa.azimuth(a)

        c = a.project(length_b, azimuth)
        return [[a, c], [c, b]]

    def _aborted(self):
        self._draw_tool.remove_all_drawings()
        self._points.clear()
        del self._layer

    @classmethod
    def draw(cls, plugin):
        iface = plugin.iface
        layer = iface.activeLayer()
        if not isinstance(layer, QgsVectorLayer):
            iface.messageBar().pushWarning("Easy Right Angle Drawing", "Bitte einen Layer auswählen")
            plugin.draw_action.setChecked(False)
            return

        if layer.wkbType() != QgsWkbTypes.LineString:
            iface.messageBar().pushWarning("Easy Right Angle Drawing", "Bitte einen Linienlayer (LineString) auswählen.")
            plugin.draw_action.setChecked(False)
            return

        tool = RightAngleTool(iface, layer, drawings=plugin.drawings)
        tool.start()
        plugin.triangle_tool = tool
        plugin.draw_action.setChecked(True)
        return tool
