"""
Raspberry Pi configurator

notes:
predictable network interface names
sudo iw dev wlx74da38de4952


ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no pi@192.168.1.4

"""



import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPlainTextEdit,
                             QInputDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

import getpass
import os
import subprocess
import pathlib

class Rpi_configurator(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Raspberry Pi configurator'
        self.left = 100
        self.top = 100
        self.width = 320
        self.height = 200
        self.initUI()

        self.rpi_device = ""

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        hl = QVBoxLayout()

        hl.addWidget(QPushButton('Detect Raspberry Pi SD card', self, clicked=self.detect_rpi_sd_card))
        self.rpi_detected = QPlainTextEdit("")
        hl.addWidget(self.rpi_detected)

        self.hostname_btn = QPushButton('Hostname configuration', self, clicked=self.hostname_config)
        self.hostname_btn.setEnabled(False)
        hl.addWidget(self.hostname_btn)


        self.wifi_btn = QPushButton('WiFi configuration', self, clicked=self.wifi_config)
        self.wifi_btn.setEnabled(False)
        hl.addWidget(self.wifi_btn)

        main_widget = QWidget(self)
        main_widget.setLayout(hl)

        self.setCentralWidget(main_widget)

        self.show()

    @pyqtSlot()
    def detect_rpi_sd_card(self):
        print('detect_rpi_sd_card')
        print("currentuser:", getpass.getuser())
        current_user = getpass.getuser()

        if sys.platform.startswith('linux'):
            if os.path.ismount(f"/media/{current_user}/boot"):

                out = f"Raspberry Pi SD card found in /media/{current_user}/boot\n"

                self.rpi_device = pathlib.Path(f"/media/{current_user}/boot")

                self.wifi_btn.setEnabled(True)
                self.hostname_btn.setEnabled(True)

                # check current hostname on other partition
                try:
                    with open(f"/media/{current_user}/rootfs/etc/hostname", "r") as file_in:
                        hostname = file_in.read()
                except Exception:
                    hostname = ""
                out += f"\nHostname: {hostname}"

                # check current wifi network on other partition
                try:
                    with open(f"/media/{current_user}/rootfs/etc/wpa_supplicant/wpa_supplicant.conf", "r") as file_in:
                        wpa_supplicant = file_in.read()
                except Exception:
                    wpa_supplicant = ""
                out += f"\nWiFi network:\n{wpa_supplicant}\n"

                self.rpi_detected.setPlainText(out)
            else:
                self.rpi_detected.setPlainText(f"No Raspberry Pi SD card found")


        if sys.platform.startswith('win'):
            self.rpi_device = ""
            drvArr = ['c:', 'd:', 'e:', 'f:', 'g:', 'h:', 'i:', 'j:', 'k:', 'l:']
            for dl in drvArr:
                try:
                    if (os.path.isdir(dl) != 0):
                        val = subprocess.check_output(["cmd", "/c vol " + dl])
                        if ('is boot' in str(val)) and (pathlib.Path(dl) / pathlib.Path("cmdline.txt")).is_file():
                            self.rpi_device = pathlib.Path(dl)
                            out = f"Raspberry Pi SD card found in {dl}"

                            self.wifi_btn.setEnabled(True)
                            self.hostname_btn.setEnabled(True)
                            break
                except:
                    print("Error: findDriveByDriveLabel(): exception")
            else:
                out = "No Raspberry Pi SD card found"

            self.rpi_detected.setPlainText(out)


    @pyqtSlot()
    def hostname_config(self):
        """
        set hostname
        hostname is defined in the /boot/hostname and set during execution of /et
        """
        hostname, ok = QInputDialog().getText(self, "Hostname", "name:", QLineEdit.Normal, "")
        if not ok or not hostname:
            return
        if "_" in hostname:
            return
        try:
            with open(self.rpi_device / "hostname", "w") as f_out:
                f_out.write(hostname)
        except Exception:
            print("Error writing /boot/hostname file")

        



    @pyqtSlot()
    def wifi_config(self):
        wifi_name, ok = QInputDialog().getText(self, "WiFi Network ", "name:", QLineEdit.Normal, "")
        if not ok or not wifi_name:
            return
        wifi_password, ok = QInputDialog().getText(self, "WiFi Network ", "Password", QLineEdit.Normal, "")
        if not ok or not wifi_password:
            return
        wifi_country, ok = QInputDialog().getText(self, "WiFi Network ", "Country (2 letters code)", QLineEdit.Normal, "")
        if not ok or not wifi_country:
            return


        wpa_template = f"""country={wifi_country}
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
ssid="{wifi_name}"
psk="{wifi_password}"
key_mgmt=WPA-PSK
}}
"""
        try:
            with open(self.rpi_device / "wpa_supplicant.conf", "w") as f_out:
                f_out.write(wpa_template)
        except Exception:
            print("Error writing wpa file")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Rpi_configurator()
    sys.exit(app.exec_())
