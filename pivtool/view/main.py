# Copyright (c) 2014 Yubico AB
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Additional permission under GNU GPL version 3 section 7
#
# If you modify this program, or any covered work, by linking or
# combining it with the OpenSSL project's OpenSSL library (or a
# modified version of that library), containing parts covered by the
# terms of the OpenSSL or SSLeay licenses, We grant you additional
# permission to convey the resulting work. Corresponding Source for a
# non-source form of such a combination shall include the source code
# for the parts of OpenSSL used as well as that of the covered work.

from PySide import QtGui
from PySide import QtCore
from pivtool.storage import settings


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setCentralWidget(self.build_ui())

        self.resize(settings.value('window/size', QtCore.QSize(0, 0)))
        pos = settings.value('window/pos')
        if pos:
            self.move(pos)

    def build_ui(self):
        widget = QtGui.QWidget()
        widget.setMinimumWidth(320)
        widget.setMinimumHeight(200)
        layout = QtGui.QHBoxLayout()
        widget.setLayout(layout)

        return widget

    def closeEvent(self, event):
        settings.setValue('window/size', self.size())
        settings.setValue('window/pos', self.pos())
        event.accept()

    def customEvent(self, event):
        event.callback()
