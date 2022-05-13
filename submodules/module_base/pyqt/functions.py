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

from qgis.PyQt.QtWidgets import QLabel, QGroupBox

from .constants import STYLE_SHEET_NEUTRAL, STYLE_SHEET_WARNING, STYLE_SHEET_ERROR


def grp_visibility_changed(group: QGroupBox):
    """ Hides/Shows all children from group box, depends on check state.

        :param group:
    """
    state = group.isChecked()
    children = group.children()
    if state:
        for child in children:
            if not hasattr(child, 'show'):
                # kann nicht eingeblendet werden, bspw. QLayout
                continue
            child.show()
    else:
        for child in children:
            # kann nicht ausgeblendet werden, bspw. QLayout
            if not hasattr(child, 'hide'):
                continue
            child.hide()


def set_label_status(label: QLabel, text: str, style: str = STYLE_SHEET_NEUTRAL) -> None:
    """ sets labels text and css style

        :param label: label where to change text and stylesheet in css
        :param text: text to set, keep it empty and label will be hidden
        :param style: css stylesheet, defaults to `_qt_constants.STYLE_SHEET_NEUTRAL`
    """
    label.setText(text)
    if not text:
        label.hide()
        return

    label.setStyleSheet(style)
    label.show()


def set_label_error(label: QLabel, text: str) -> None:
    """ sets labels text

        :param label: label where to change text and stylesheet in css
        :param text: text to set, keep it empty and label will be hidden
    """
    set_label_status(label, text, STYLE_SHEET_ERROR)


def set_label_warning(label: QLabel, text: str) -> None:
    """ sets labels text

        :param label: label where to change text and stylesheet in css
        :param text: text to set, keep it empty and label will be hidden
    """
    set_label_status(label, text, STYLE_SHEET_WARNING)
