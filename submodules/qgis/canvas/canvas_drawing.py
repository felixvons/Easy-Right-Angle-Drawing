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

from qgis.gui import QgsMapTool, QgsVertexMarker, QgsRubberBand
from qgis.core import QgsGeometry, QgsVectorLayer, QgsPointXY

from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import Qt, QPointF

from typing import Optional, Union, List


class DrawTool:
    """ Zur Erstellung einfacher Grafiken und Markierungen auf der Karte.

        Example Usage:

            .. code-block:: python

                # initialize the draw object
                tool = DrawTool(parent)
                # create point on canvas
                point = tool.create_vpoint(pointxy,
                                           reference_layer,  # needed to convert point to canvas point
                                           QColor(255, 120, 0, 70),
                                           QgsVertexMarker.ICON_CIRCLE,
                                           15,
                                           15)
                # add text to canvas (no scaling)
                tool.add_text("Von", point.pos(), font)

        :param color: color from Qt, defaults to QColor(0, 250, 0, 100)
        :param size: size, defaults to 10
        :param width: width, defaults to 7
        :param drawings: optional vertex marker list to add marker to the list
    """

    def __init__(self, canvas, color: QColor = QColor(0, 250, 0, 100), size: int = 10, width: int = 7, drawings: Optional[List] = None):

        self.canvas = canvas
        self.QgsMapTool = QgsMapTool(self.canvas)
        self.width = width
        self.size = size
        self.color = color

        if drawings is None:
            drawings = []

        self.drawings = drawings
        self.drawn_objekts = []

    def add_text(self, text: str, point: Union[QPointF, QgsVertexMarker], font: Optional[QFont] = None):
        """ Adds text to current canvas scene at given point.

            Hint:

                Added text needs point position relative to current canvas, not to an QgsPointXY.
                You can add text at VertexMarkers location mit `QgsVertexMarker().pos()`.
                On canvas moving, you have to reload the text

            :param text: text to display
            :param point: point position
            :param font: optional font, defaults to default font settings

        """
        if font is None:
            font = QFont()

        if isinstance(point, QgsVertexMarker):
            point = point.pos()

        item = self.canvas.scene().addText(text, font)
        item.setPos(point)
        self.drawn_objekts.append(item)
        self.drawings.append(item)

    def set_color(self, red: int, green: int, blue: int, transparency: int):
        """ Ändere die Farbe des Zeichentools

            :param red: 0 - 255
            :type red: int

            :param green: 0 - 255
            :type green: int

            :param blue: 0 - 255
            :type blue: int

            :param transparency: 0 - 255
            :type transparency: int
        """
        self.color = QColor(red, green, blue, transparency)

    def set_size(self, size: int):
        """ Ändere die Größe des Zeichentools

            :param size: size
            :type size: int
        """
        self.size = size

    def set_width(self, width: int):
        """ Ändere die Breite des Zeichentools

            :param width: width
            :type width: int
        """
        self.width = width

    def create_vpoint(self, point, source_layer: QgsVectorLayer,
                      color: QColor = None, icon_type: QgsVertexMarker.IconType = None,
                      size: int = None, width: int = None, fill_color: QColor = None):
        """ Erstellt ein oder mehrere Punktgrafiken (QgsVertexMarker)

            :param point: QgsPoint or QgsPointXY or QgsGeometry or list of points
            :param source_layer: converts point types to correct crs
            :param color: color, defaults to None
            :param icon_type: icon_type, defaults to None
            :param size: size, defaults to None
            :param width: width, defaults to None
            :return: QgsVertexMarker or List[QgsVertexMarker]

            :raises ValueError: Übergebener `point` ist nicht gültig
        """
        if color is None:
            color = self.color
        if size is None:
            size = self.size
        if width is None:
            width = self.width
        if icon_type is None:
            icon_type = QgsVertexMarker.ICON_CIRCLE

        if isinstance(point, list):
            v_points = []
            for geo in point:
                qpointxy_map = self.QgsMapTool.toMapCoordinates(source_layer, geo)
                v_point = QgsVertexMarker(self.canvas)
                v_point.setCenter(qpointxy_map)
                v_point.setColor(color)
                v_point.setIconSize(size)
                v_point.setIconType(icon_type)
                v_point.setPenWidth(width)
                if fill_color:
                    v_point.setFillColor(fill_color)
                self.drawn_objekts.append(v_point)
                v_points.append(v_point)
                self.drawings.append(v_point)
            return v_points

        elif isinstance(point, QgsPointXY):
            v_point = QgsVertexMarker(self.canvas)
            qpointxy_map = self.QgsMapTool.toMapCoordinates(source_layer, point)
            # qpoint = self.QgsMapTool.toCanvasCoordinates(qpointxy_map)
            # print(qpoint)
            # point = self.QgsMapTool.toMapCoordinates(qpoint)
            v_point.setCenter(qpointxy_map)
            v_point.setColor(color)
            v_point.setIconSize(size)
            v_point.setIconType(icon_type)
            v_point.setPenWidth(width)
            if fill_color:
                v_point.setFillColor(fill_color)
            self.drawn_objekts.append(v_point)
            self.drawings.append(v_point)
            return v_point

        elif isinstance(point, QgsGeometry):
            qpointxy = point.asPoint()
            v_point = QgsVertexMarker(self.canvas)
            qpointxy_map = self.QgsMapTool.toMapCoordinates(source_layer, qpointxy)
            v_point.setCenter(qpointxy_map)
            v_point.setColor(color)
            v_point.setIconSize(size)
            v_point.setIconType(icon_type)
            v_point.setPenWidth(width)
            if fill_color:
                v_point.setFillColor(fill_color)
            self.drawn_objekts.append(v_point)
            self.drawings.append(v_point)
            return v_point

        else:
            raise ValueError("Übergebener Punkt ist nicht gültig")

    def create_rubber_band(self, geometry, source_layer: QgsVectorLayer, line_type: Qt.PenStyle = Qt.DashLine,
                           color: QColor = None, width: int = None, drawn: bool = False) -> QgsRubberBand:
        """ Erstellt eine oder Liniengrafik (QgsRubberBand)

            :param geometry: QgsGeometry or List[QgsGeometry]
            :param source_layer:
            :param line_type: Aussehen der Linie (Gestrichelt, Durchgängig, ...), defaults to
            :param color:
            :param width:
            :param drawn:

            :return: created QgsRubberBand
        """
        if color is None:
            color = self.color
        if width is None:
            width = self.width

        if isinstance(geometry, list):
            qpointsxy = []
            for point in geometry:
                qpointsxy.append(self.QgsMapTool.toMapCoordinates(source_layer, point))
            geometry = QgsGeometry.fromPolylineXY(qpointsxy)

        else:
            qpointsxy = []
            points = geometry.asPolyline()
            for point in points:
                qpointsxy.append(self.QgsMapTool.toMapCoordinates(source_layer, point))
            geometry = QgsGeometry.fromPolylineXY(qpointsxy)

        rubber_band = QgsRubberBand(self.canvas, False)
        rubber_band.setToGeometry(geometry, None)
        rubber_band.setColor(color)
        rubber_band.setWidth(width)
        rubber_band.setLineStyle(line_type)
        if not drawn:
            self.drawn_objekts.append(rubber_band)
        self.drawings.append(rubber_band)
        return rubber_band

    def remove_class_drawings(self):
        """ entfernt alle Zeichnungen dieser Klasse """
        for drawing in self.drawn_objekts:
            self.canvas.scene().removeItem(drawing)
        self.drawn_objekts = []

    def remove_all_drawings(self):
        """ entfernt alle Zeichnungen """
        for drawing in self.drawings:
            self.canvas.scene().removeItem(drawing)
        self.drawings = []

    def remove_last_drawings(self, quantity: int = 1):
        """ entfernt die letzten `quantity` Zeichnungen

            :param quantity: Anzahl der zu entfernenden letzten Zeichnungen
            :type quantity: int
        """
        for i in range(quantity):
            try:
                self.canvas.scene().removeItem(self.drawings[-1])
                self.drawings.pop(-1)
            except IndexError:
                pass
