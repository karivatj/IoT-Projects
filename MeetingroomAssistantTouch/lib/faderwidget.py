#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QTimeLine
from PyQt5 import QtGui, QtWidgets

class FaderWidget(QtWidgets.QWidget):

    pixmap_opacity = 0

    def __init__(self, old_widget, new_widget):

        QtWidgets.QWidget.__init__(self, new_widget)

        self.old_pixmap = QtGui.QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.0

        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(500)
        self.timeline.start()

        self.resize(new_widget.size())
        self.show()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()

    def animate(self, value):
        self.pixmap_opacity = 1.0 - value
        self.repaint()

class StackedWidget(QtWidgets.QStackedWidget):

    def __init__(self, parent = None):
        QtWidgets.QStackedWidget.__init__(self, parent)

    def setCurrentIndex(self, index):
        self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index))
        QtWidgets.QStackedWidget.setCurrentIndex(self, index)