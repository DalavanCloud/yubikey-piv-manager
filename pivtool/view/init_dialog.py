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

from PySide import QtGui, QtCore
from pivtool import messages as m
from pivtool.piv import DeviceGoneError
from pivtool.view.utils import pin_field
from pivtool.utils import complexity_check

KEY_VALIDATOR = QtGui.QRegExpValidator(QtCore.QRegExp(r'[0-9a-fA-F]{48}'))
HEADER = "<br><b>%s</b>"


class InitDialog(QtGui.QDialog):

    def __init__(self, controller, parent=None):
        super(InitDialog, self).__init__(parent)

        self._controller = controller
        self._build_ui()

    def _build_ui(self):
        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel(m.initialize))

        layout.addLayout(self._build_pin_settings())
        layout.addLayout(self._build_key_settings())
        layout.addStretch()

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        self._ok_btn = buttons.button(QtGui.QDialogButtonBox.Ok)
        self._ok_btn.setDisabled(True)
        buttons.accepted.connect(self._initialize)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _build_pin_settings(self):
        layout = QtGui.QFormLayout()
        layout.addRow(QtGui.QLabel(HEADER % m.pin))
        self._new_pin = pin_field()
        layout.addRow(m.new_pin_label, self._new_pin)
        self._confirm_pin = pin_field()
        layout.addRow(m.verify_pin_label, self._confirm_pin)
        self._new_pin.textChanged.connect(self._check_confirm)
        self._confirm_pin.textChanged.connect(self._check_confirm)
        return layout

    def _build_key_settings(self):
        self._key_layout = QtGui.QFormLayout()
        self._key_layout.addRow(QtGui.QLabel(HEADER % m.management_key))
        self._key_type = QtGui.QComboBox()
        self._key_type.addItem(m.key_type_pin)
        self._key_type.addItem(m.key_type_password)
        self._key_type.addItem(m.key_type_key)
        self._key_layout.addRow(m.key_type_label, self._key_type)
        self._key_type.currentIndexChanged.connect(self._change_key_type)

        self._key = QtGui.QLineEdit()
        self._key.setValidator(KEY_VALIDATOR)
        self._password = QtGui.QLineEdit()
        self._password.setEchoMode(QtGui.QLineEdit.Password)
        self._password_verify = QtGui.QLineEdit()
        self._password_verify.setEchoMode(QtGui.QLineEdit.Password)
        return self._key_layout

    def _change_key_type(self, index):
        for widget in [self._key, self._password, self._password_verify]:
            widget.setText('')
            label = self._key_layout.labelForField(widget)
            if label is not None:
                self._key_layout.removeWidget(label)
                label.hide()
            self._key_layout.removeWidget(widget)
            widget.hide()
        if index == 0:  # PIN
            return

        if index == 1:  # Password
            self._key_layout.addRow(m.password_label, self._password)
            self._key_layout.addRow(m.verify_password_label, self._password_verify)
            self._password.show()
            self._password_verify.show()
            self._password.setFocus()
        else:  # Key
            self._key_layout.addRow(m.key_label, self._key)
            self._key.show()
            self._key.setFocus()

    def _check_confirm(self):
        new_pin = self._new_pin.text()
        if len(new_pin) > 0 and new_pin == self._confirm_pin.text():
            self._ok_btn.setDisabled(False)
        else:
            self._ok_btn.setDisabled(True)

    def _initialize(self):
        new_pin = self._new_pin.text()

        if not complexity_check(new_pin):
            QtGui.QMessageBox.warning(self, m.pin_not_complex,
                                      m.pin_complexity_desc)
            return

        index = self._key_type.currentIndex()
        if index == 0:  # PIN
            key = None
            use_password = True
        elif index == 1:  # Password
            key = self._password.text()
            use_password = True
        else:  # Key
            key = self._key.text()
            use_password = False

        try:
            self._controller.ensure_authenticated()
            worker = QtCore.QCoreApplication.instance().worker
            worker.post(
                m.initializing,
                (self._controller.initialize, new_pin, None, key, use_password),
                self._init_callback,
                True
            )
        except ValueError as e:
            QtGui.QMessageBox.warning(self, m.error, str(e))

    def _init_callback(self, result):
        if isinstance(result, DeviceGoneError):
            QtGui.QMessageBox.warning(self, m.error, m.device_unplugged)
            self.accept()
        elif isinstance(result, Exception):
            QtGui.QMessageBox.warning(self, m.error, str(result))
        else:
            self.accept()
