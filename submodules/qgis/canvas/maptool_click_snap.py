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

from qgis.PyQt.QtCore import pyqtSignal, Qt, QPoint
from qgis.core import (QgsVectorLayer, QgsPointXY, Qgis, QgsPointLocator)
from qgis.gui import (QgsMapTool, QgisInterface, QgsSnapIndicator)

from typing import Optional, List


class MapToolQgisSnap(QgsMapTool):
    """ Creates a map tool. This map tool uses the snapping config from QGIS.
        When needed, you can add individual layers.
        Default snap color from QGIS profile will be used.
        Editable Snap color at:
            - Options
            - Digitizing
            - Snapping
            - Snapping marker color

        .. code-block:: python

            # get iface
            from qgis.utils import iface
            layer = iface.activeLayer()

            # create an extra snap layer
            params = {"INPUT": layer, "VERTICES": "0,-1", "OUTPUT": "TEMPORARY_OUTPUT"}
            output = processing.run("native:extractspecificvertices", params)['OUTPUT']

            iface.mapCanvas().setMapTool(
                MapToolDrawLine(
                    iface,
                    layer,
                    snap_on_layers=[output]
                )
            )

        :param iface: current qgis iface from running instance
        :param layer: to use layer for drawing/snapping
        :param snap_on_layers: prevent intersection with
                               https://qgis.org/pyqgis/3.16/core/QgsSnappingUtils.html#qgis.core.QgsSnappingUtils.LayerConfig
        :param match_filter: Define your own match filter. If None and snap_on_layers are set,
                             then a default filter will be generated from `LayerMatchFilter`.
        :param force_snap: force only use snapped points for poly line. Each point for poly line must be snapped.
        :param min_segment_length: minimum new segment length, defaults to 0.1. Set to -1 to disable it

    """
    aborted = pyqtSignal(name="aborted")
    clicked = pyqtSignal(QgsPointXY, name="clicked")
    moved = pyqtSignal(QgsPointXY, name="moved")

    def __init__(self, iface: QgisInterface,
                 layer: QgsVectorLayer,
                 snap_on_layers: Optional[List[QgsVectorLayer]] = None,
                 match_filter: Optional[QgsPointLocator.MatchFilter] = None,
                 force_snap: bool = False):

        self.canvas = iface.mapCanvas()
        QgsMapTool.__init__(self, self.canvas)
        self._disabled = False
        self.iface = iface
        self.force_snap = force_snap
        self.previous_tool = self.canvas.mapTool()

        self._utils = self.canvas.snappingUtils()
        self._indicator = QgsSnapIndicator(self.canvas)
        self._snap_on_layers = snap_on_layers if snap_on_layers else []
        self._remove_layers_later = [l for l in self._snap_on_layers if l not in self._utils.layers()]
        self._match_filter = None
        if self._snap_on_layers and match_filter is None:
            # create a filter only for snap layers
            self._match_filter = LayerMatchFilter(self._snap_on_layers)

        elif match_filter is not None:
            # use the given match filter
            self._match_filter = match_filter

        for extra_layer in self._remove_layers_later:
            self._utils.addExtraSnapLayer(extra_layer)

        # layer with same build method
        self.layer = layer

        # activate self as Maptool
        self.canvas.setMapTool(self)

    def _get_snapped_match(self, pos):
        """ Returns snapped point. Point's crs is in projects/canvas crs. """
        coord = self.toMapCoordinates(pos)

        # test for default snapping
        return self._utils.snapToMap(coord, filter=self._match_filter)

    def canvasReleaseEvent(self, event):
        """user releases mouse button after clicking"""

        if self._disabled:
            self.unload_tool()
            return

        mouse_btn = event.button()

        # left button was clicked
        if mouse_btn == Qt.LeftButton:
            point = self._get_point(event.pos())

            if not point:
                if self.force_snap:
                    self.iface.messageBar().pushMessage("Tool",
                                                        "Bitte auf einen Punkt einrasten",
                                                        level=Qgis.Warning,
                                                        duration=5)
                else:
                    self.iface.messageBar().pushMessage("Tool",
                                                        "Kein nächster Punkt gefunden.",
                                                        level=Qgis.Warning,
                                                        duration=3)
                return

            self.clicked.emit(point)

        # right button was clicked -> save drawings
        elif mouse_btn == Qt.RightButton:
            # user pressed right mouse button with only on point set
            self.unload_tool()
            self.aborted.emit()

    def keyReleaseEvent(self, event):
        """user presses button"""

        if self._disabled:
            self.unload_tool()
            return

        pressed_key = event.key()
        # escape button is pressed, drawing tool is unloaded, temporary drawings are removed
        if pressed_key == Qt.Key_Escape:
            self.unload_tool()
            # inform User
            self.aborted.emit()

    def _get_point(self, pos: QPoint):
        match = self._get_snapped_match(pos)
        valid = match.isValid()
        point = match.point()

        if self.force_snap or valid:
            if not valid:
                self._hide_indicator()
                point = None
            else:
                self._show_indicator(match)
                point = self.toLayerCoordinates(self.layer, point)

        else:
            self._hide_indicator()
            if not valid:
                coord = self.toMapCoordinates(pos)
                point = self.toLayerCoordinates(self.layer, coord)

        return point

    def canvasMoveEvent(self, event):
        """mouse move event on canvas"""

        if self._disabled:
            self.unload_tool()
            return

        point = self._get_point(event.pos())
        if point:
            self.moved.emit(point)

    def _hide_indicator(self):
        if self._indicator.isVisible():
            self._indicator.setVisible(False)

    def _show_indicator(self, match):
        self._indicator.setMatch(match)
        self._indicator.setVisible(True)

    @property
    def disabled(self):
        return self._disabled

    def unload_tool(self):
        self._hide_indicator()
        self.canvas.unsetMapTool(self)
        if not self._disabled:
            self.canvas.setMapTool(self.previous_tool)

        self._disabled = True

        for extra_layer in self._remove_layers_later:
            self._utils.removeExtraSnapLayer(extra_layer)
        self._remove_layers_later.clear()


class LayerMatchFilter(QgsPointLocator.MatchFilter):

    def __init__(self, layers):
        self._layers = layers
        super().__init__()

    def acceptMatch(self, match: QgsPointLocator.Match) -> bool:

        if match.layer() not in self._layers:
            return False

        return True


if __name__ in ("__main__", "__console__"):
    import processing
    from qgis.utils import iface

    params = {"INPUT": iface.activeLayer(), "VERTICES": "0,-1", "OUTPUT": "TEMPORARY_OUTPUT"}
    output = processing.run("native:extractspecificvertices", params)['OUTPUT']

    tool = MapToolQgisSnap(
        iface,
        iface.activeLayer(),
        snap_on_layers=[output]
    )
    tool.clicked.connect(print)
