"""
Raspberry Pi configurator

notes:
predictable network interface names
sudo iw dev wlx74da38de4952

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

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        hl = QVBoxLayout()

        hl.addWidget(QPushButton('Detect Raspberry Pi SD card', self, clicked=self.detect_rpi_sd_card))
        self.rpi_detected = QPlainTextEdit("")
        hl.addWidget(self.rpi_detected)

        wifi_btn = QPushButton('WiFi configuration', self, clicked=self.wifi_config)
        wifi_btn.setEnabled(False)
        hl.addWidget(wifi_btn)

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
            if os.path.ismount(f"/media/{current_user}/rootfs"):
                print(f"SD card found in /media/{current_user}/rootfs\n")
                out = f"Raspberry Pi SD card found in /media/{current_user}/rootfs\n"
                # check hostname
                try:
                    with open("/media/olivier/rootfs/etc/hostname", "r") as file_in:
                        hostname = file_in.read()
                except Exception:
                    hostname = ""
                out += f"\nHostname: {hostname}"

                # check wifi network
                try:
                    with open("/media/olivier/rootfs/etc/wpa_supplicant/wpa_supplicant.conf", "r") as file_in:
                        wpa_supplicant = file_in.read()
                except Exception:
                    wpa_supplicant = ""
                out += f"\nWiFi network:\n{wpa_supplicant}\n"

                self.rpi_detected.setPlainText(out)
            else:
                print(f"No SD card found")
                self.rpi_detected.setPlainText(f"No Raspberry Pi SD card found")

<<<<<<< HEAD
=======
        if sys.platform.startswith('win'):
            self.rpi_device = ""
            drvArr = ['c:', 'd:', 'e:', 'f:', 'g:', 'h:', 'i:', 'j:', 'k:', 'l:']
            for dl in drvArr:
                try:
                    if (os.path.isdir(dl) != 0):
                        val = subprocess.check_output(["cmd", "/c vol " + dl])
                        if ('is boot' in str(val)) and (pathlib.Path(dl) / pathlib.Path("cmdline.txt")).is_file():
                            self.rpi_device = pathlib.Path(dl)
                            print(f"Raspberry Pi SD card found: {dl}")
                            out = f"Raspberry Pi SD card found in {dl}"
                            break
                except:
                    print("Error: findDriveByDriveLabel(): exception")
            else:
                print("Raspberry Pi SD card not found")
                out = "No Raspberry Pi SD card found"

            self.rpi_detected.setPlainText(out)
>>>>>>> 774e291a70216d2dd20894fd05a43cef0e203155


    @pyqtSlot()
    def wifi_config(self):
        print('wifi config')
        wifi_name, ok = QInputDialog().getText(self, "WiFi Network ", "name:", QLineEdit.Normal, "")
        if not ok or not wifi_name:
            return
        wifi_password, ok = QInputDialog().getText(self, "WiFi Network ", "Password", QLineEdit.Normal, "")
        if not ok or not wifi_password:
            return
        wpa_template = f"""country=US
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
