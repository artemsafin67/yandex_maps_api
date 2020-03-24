from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from sys import argv

import requests
import os

from static_helper import define_coords


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.start()

    def start(self):
        # Initialization of servers' names
        self.static_api_server = 'https://static-maps.yandex.ru/1.x/'
        self.geocode_api_server = ''
        self.org_api_server = ''

        # Buttons
        self.showMapButton.clicked.connect(self.update_map)
        self.addPointButton.clicked.connect(self.add_point)
        self.resetButton.clicked.connect(self.reset_points)

        # Options of map's type
        self.map_types = {'Схема': 'map', 'Спутник': 'sat', 'Гибрид': 'sat,skl'}

        # Points on the map
        self.pt = ''

        # Distances to move then pressing Left, Right, Up and Down arrows
        self.delta_width = {17: 0.0025}
        for i in range(16, 0, -1):
            self.delta_width[i] = self.delta_width[i + 1] * 2

        self.delta_height = {17: 0.00125}
        for i in range(16, 0, -1):
            self.delta_height[i] = self.delta_height[i + 1] * 2

        # Right focus then pressing keyboard
        self.setFocusPolicy(Qt.ClickFocus)

        self.mapTypeComboBox.addItem('Схема')
        self.mapTypeComboBox.addItem('Спутник')
        self.mapTypeComboBox.addItem('Гибрид')
        self.mapTypeComboBox.activated[str].connect(self.update_map)

        # Updating map then chosen option changes
        self.postIndexOnRadioButton.toggled.connect(self.add_point)
        self.postIndexOffRadioButton.toggled.connect(self.add_point)

    def update_map(self):
        # Updates map taking data from Edit Widgets

        try:
            # Getting data
            lattitude = float(self.lattitudeEdit.text())
            longitude = float(self.longitudeEdit.text())
            scale = int(self.scaleSpinBox.value())
            map_type = self.map_types[self.mapTypeComboBox.currentText()]

        except ValueError:
            return

        self.show_map(lattitude, longitude, map_type, scale)

    def show_map(self, lattitude, longitude, map_type, scale=False, spn=False):
        # Puts an image of a map into special label

        # Data for request
        center = '{},{}'.format(str(longitude), str(lattitude))
        map_params = {
            'l': map_type,
            'll': center,
            'size': '650,450',
        }

        if scale:
            map_params['z'] = scale
        if spn:
            map_params['spn'] = spn
        if self.pt:
            map_params['pt'] = self.pt.lstrip('~')

        response = requests.get(self.static_api_server, params=map_params)

        if not response:  # If something goes wrong
            return

        # Saving the image of the map
        map_file = 'map_image.png'
        with open(map_file, 'wb') as file:
            file.write(response.content)

        # Changing our label
        self.mapImage.setPixmap(QPixmap(map_file))

        # Cleaning everything
        os.remove(map_file)

    def add_point(self):
        toponym = self.objectAddressEdit.text()
        post_index_bool = self.postIndexOnRadioButton.isChecked()

        delta, center, address, post_index = define_coords(toponym)

        if post_index_bool and post_index:
            address += ', {}'.format(post_index)

        self.fullAddressLabel.setText(address)

        self.pt += '~{},pm2dbl'.format(','.join(center))

        longitude, lattitude = center
        self.lattitudeEdit.setText(lattitude)
        self.longitudeEdit.setText(longitude)

        self.show_map(lattitude, longitude, 'map', scale=int(self.scaleSpinBox.value()))

    def reset_points(self):
        self.pt = ''
        self.fullAddressLabel.setText('')
        self.objectAddressEdit.setText('')
        self.update_map()

    def keyPressEvent(self, event):
        scale = self.scaleSpinBox.value()

        if event.key() == Qt.Key_PageDown:
            self.scaleSpinBox.setValue(self.scaleSpinBox.value() - 1)
            self.update_map()
        if event.key() == Qt.Key_PageUp:
            self.scaleSpinBox.setValue(self.scaleSpinBox.value() + 1)
            self.update_map()

        if event.key() == Qt.Key_Left:
            if abs(float(self.longitudeEdit.text()) - self.delta_width[scale]) > 90:
                return

            self.longitudeEdit.setText(str(float(self.longitudeEdit.text()) - self.delta_width[scale]))
            self.update_map()

        if event.key() == Qt.Key_Right:
            if abs(float(self.longitudeEdit.text()) + self.delta_width[scale]) > 90:
                return

            self.longitudeEdit.setText(str(float(self.longitudeEdit.text()) + self.delta_width[scale]))
            self.update_map()

        if event.key() == Qt.Key_Up:
            if abs(float(self.lattitudeEdit.text()) + self.delta_height[scale]) > 90:
                return

            self.lattitudeEdit.setText(str(float(self.lattitudeEdit.text()) + self.delta_height[scale]))
            self.update_map()

        if event.key() == Qt.Key_Down:
            if abs(float(self.lattitudeEdit.text()) - self.delta_height[scale]) > 90:
                return

            self.lattitudeEdit.setText(str(float(self.lattitudeEdit.text()) - self.delta_height[scale]))
            self.update_map()


if __name__ == '__main__':
    app = QApplication(argv)
    ex = MainWindow()
    ex.show()
    app.exec()
