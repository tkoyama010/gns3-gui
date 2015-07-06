# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Configuration page for VMware preferences.
"""

import os
import sys
import shutil
from gns3.qt import QtWidgets

from .. import VMware
from ..ui.vmware_preferences_page_ui import Ui_VMwarePreferencesPageWidget
from ..settings import VMWARE_SETTINGS


class VMwarePreferencesPage(QtWidgets.QWidget, Ui_VMwarePreferencesPageWidget):

    """
    QWidget preference page for VMware.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        # connect signals
        self.uiUseLocalServercheckBox.stateChanged.connect(self._useLocalServerSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiVmrunPathToolButton.clicked.connect(self._vmrunPathBrowserSlot)

        if sys.platform.startswith("darwin"):
            # we do not support VMware Fusion for now
            self.uiUseLocalServercheckBox.setChecked(False)
            self.uiUseLocalServercheckBox.setEnabled(False)
            self.uiHostTypeComboBox.addItem("VMware Fusion", "fusion")
        else:
            self.uiHostTypeComboBox.addItem("VMware Player", "player")
            self.uiHostTypeComboBox.addItem("VMware Workstation", "ws")

        if sys.platform.startswith("win"):
            # VMnet limit on Windows is 19
            self.uiVMnetEndRangeSpinBox.setMaximum(19)
        else:
            # VMnet limit on Linux is 255
            self.uiVMnetEndRangeSpinBox.setMaximum(255)

    def _vmrunPathBrowserSlot(self):
        """
        Slot to open a file browser and select vmrun.
        """

        vmrun_path = shutil.which("vmrun")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select vmrun", vmrun_path)
        if not path:
            return

        if self._checkVmrunPath(path):
            self.uiVmrunPathLineEdit.setText(os.path.normpath(path))

    def _checkVmrunPath(self, path):
        """
        Checks that the vmrun path is valid.

        :param path: vmrun path
        :returns: boolean
        """

        if not os.path.exists(path):
            QtWidgets.QMessageBox.critical(self, "vmrun", '"{}" does not exist'.format(path))
            return False

        if not os.access(path, os.X_OK):
            QtWidgets.QMessageBox.critical(self, "vmrun", "{} is not an executable".format(os.path.basename(path)))
            return False

        return True

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(VMWARE_SETTINGS)

    def _useLocalServerSlot(self, state):
        """
        Slot to enable or not local server settings.
        """

        if state:
            self.uiVmrunPathLineEdit.setEnabled(True)
            self.uiVmrunPathToolButton.setEnabled(True)
            self.uiHostTypeComboBox.setEnabled(True)
            self.uiNetworkTab.setEnabled(True)
        else:
            self.uiVmrunPathLineEdit.setEnabled(False)
            self.uiVmrunPathToolButton.setEnabled(False)
            self.uiHostTypeComboBox.setEnabled(False)
            self.uiNetworkTab.setEnabled(False)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: VMware settings
        """

        self.uiVmrunPathLineEdit.setText(settings["vmrun_path"])
        index = self.uiHostTypeComboBox.findData(settings["host_type"])
        if index != -1:
            self.uiHostTypeComboBox.setCurrentIndex(index)
        self.uiVMnetStartRangeSpinBox.setValue(settings["vmnet_start_range"])
        self.uiVMnetEndRangeSpinBox.setValue(settings["vmnet_end_range"])
        self.uiUseLocalServercheckBox.setChecked(settings["use_local_server"])

    def loadPreferences(self):
        """
        Loads VMware preferences.
        """

        vmware_settings = VMware.instance().settings()
        self._populateWidgets(vmware_settings)

    def savePreferences(self):
        """
        Saves VMware preferences.
        """

        vmrun_path = self.uiVmrunPathLineEdit.text().strip()
        if self.uiUseLocalServercheckBox.isChecked() and not self._checkVmrunPath(vmrun_path):
            return

        new_settings = {"vmrun_path": vmrun_path,
                        "host_type": self.uiHostTypeComboBox.itemData(self.uiHostTypeComboBox.currentIndex()),
                        "vmnet_start_range": self.uiVMnetStartRangeSpinBox.value(),
                        "vmnet_end_range": self.uiVMnetEndRangeSpinBox.value(),
                        "use_local_server": self.uiUseLocalServercheckBox.isChecked()}
        VMware.instance().setSettings(new_settings)