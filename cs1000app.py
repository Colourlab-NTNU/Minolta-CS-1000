#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cs1000app: Simple GUI app for taking measurements with the Minolta CS-1000

Copyright (C) 2012-2014 Ivar Farup

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import cs1000
import sys
import os
import numpy as np
import PyQt4.QtGui as qt
import PyQt4.QtCore as qtcore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as \
     NavigationToolbar
from matplotlib.figure import Figure

class AppForm(qt.QMainWindow):
    """
    The main application window.
    """
    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowTitle('CS-1000')
        self.cs = cs1000.CS1000()
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
    
    def on_draw(self):
        # SPD plot
        self.axes.clear()
        spec = self.results['spectrum']
        self.axes.plot(spec[:,0], spec[:,1])
        self.axes.grid(True)
        self.axes.axis('auto')
        self.canvas.draw()
        
        # SPD table
        self.spd_table.setRowCount(np.shape(spec)[0])
        self.spd_table.setColumnCount(np.shape(spec)[1])
        self.spd_table.setHorizontalHeaderLabels(['lambda', 'SPD'])
        for i in range(np.shape(spec)[0]):
            self.spd_table.setItem(i, 0,
                               qt.QTableWidgetItem('%.0f' % spec[i, 0]))
            self.spd_table.setItem(i, 1,
                               qt.QTableWidgetItem('%.4e' % spec[i, 1]))

        # Colour table
        self.colour_table.setRowCount(11)
        self.colour_table.setColumnCount(3)
        self.colour_table.setHorizontalHeaderLabels(['Description', 'Value (2)', 'Value (10)'])
        self.colour_table.setItem(0, 0,
                                  qt.QTableWidgetItem('Le'))
        self.colour_table.setItem(0, 1,
                                  qt.QTableWidgetItem(str(self.results['Le2'])))
        self.colour_table.setItem(0, 2,
                                  qt.QTableWidgetItem(str(self.results['Le10'])))
        self.colour_table.setItem(1, 0,
                                  qt.QTableWidgetItem('Lv'))
        self.colour_table.setItem(1, 1,
                                  qt.QTableWidgetItem(str(self.results['Lv2'])))
        self.colour_table.setItem(1, 2,
                                  qt.QTableWidgetItem(str(self.results['Lv10'])))
        self.colour_table.setItem(2, 0,
                                  qt.QTableWidgetItem('X'))
        self.colour_table.setItem(2, 1,
                                  qt.QTableWidgetItem(str(self.results['X2'])))
        self.colour_table.setItem(2, 2,
                                  qt.QTableWidgetItem(str(self.results['X10'])))
        self.colour_table.setItem(3, 0,
                                  qt.QTableWidgetItem('Y'))
        self.colour_table.setItem(3, 1,
                                  qt.QTableWidgetItem(str(self.results['Y2'])))
        self.colour_table.setItem(3, 2,
                                  qt.QTableWidgetItem(str(self.results['Y10'])))
        self.colour_table.setItem(4, 0,
                                  qt.QTableWidgetItem('Z'))
        self.colour_table.setItem(4, 1,
                                  qt.QTableWidgetItem(str(self.results['Z2'])))
        self.colour_table.setItem(4, 2,
                                  qt.QTableWidgetItem(str(self.results['Z10'])))
        self.colour_table.setItem(5, 0,
                                  qt.QTableWidgetItem('x'))
        self.colour_table.setItem(5, 1,
                                  qt.QTableWidgetItem(str(self.results['x2'])))
        self.colour_table.setItem(5, 2,
                                  qt.QTableWidgetItem(str(self.results['x10'])))
        self.colour_table.setItem(6, 0,
                                  qt.QTableWidgetItem('y'))
        self.colour_table.setItem(6, 1,
                                  qt.QTableWidgetItem(str(self.results['y2'])))
        self.colour_table.setItem(6, 2,
                                  qt.QTableWidgetItem(str(self.results['y10'])))
        self.colour_table.setItem(7, 0,
                                  qt.QTableWidgetItem('u'))
        self.colour_table.setItem(7, 1,
                                  qt.QTableWidgetItem(str(self.results['u2'])))
        self.colour_table.setItem(7, 2,
                                  qt.QTableWidgetItem(str(self.results['u10'])))
        self.colour_table.setItem(8, 0,
                                  qt.QTableWidgetItem('v'))
        self.colour_table.setItem(8, 1,
                                  qt.QTableWidgetItem(str(self.results['v2'])))
        self.colour_table.setItem(8, 2,
                                  qt.QTableWidgetItem(str(self.results['v10'])))
        self.colour_table.setItem(9, 0,
                                  qt.QTableWidgetItem('T'))
        self.colour_table.setItem(9, 1,
                                  qt.QTableWidgetItem(str(self.results['T2'])))
        self.colour_table.setItem(9, 2,
                                  qt.QTableWidgetItem(str(self.results['T10'])))
        self.colour_table.setItem(10, 0,
                                  qt.QTableWidgetItem('Duv'))
        self.colour_table.setItem(10, 1,
                                  qt.QTableWidgetItem(str(self.results['Duv2'])))
        self.colour_table.setItem(10, 2,
                                  qt.QTableWidgetItem(str(self.results['Duv10'])))
                                
    def on_save_spd(self):
        file_choices = "CSV (*.csv)|*.csv"        
        suggest = 'spd.csv'
        path = unicode(qt.QFileDialog.getSaveFileName(self, 
                        'Save file', suggest, 
                        file_choices))
        if path:
            self.statusBar().showMessage('Saved to %s' % path, 2000)
            np.savetxt(path, self.results['spectrum'], '%.0f, %.4e')

    def on_save_colour(self):
        file_choices = "CSV (*.csv)|*.csv"        
        suggest = 'colour.csv'
        path = unicode(qt.QFileDialog.getSaveFileName(self, 
                        'Save file', suggest, 
                        file_choices))
        if path:
            self.statusBar().showMessage('Saved to %s' % path, 2000)
            f = open(path, 'w')
            f.write('Description, Value (2), Value (10)\n')
            f.write('Le, %.4f, %.4f\n' % (self.results['Le2'], self.results['Le10']))
            f.write('Lv, %.4f, %.4f\n' % (self.results['Lv2'], self.results['Lv10']))
            f.write('X, %.4f, %.4f\n' % (self.results['X2'], self.results['X10']))
            f.write('Y, %.4f, %.4f\n' % (self.results['Y2'], self.results['Y10']))
            f.write('Z, %.4f, %.4f\n' % (self.results['Z2'], self.results['Z10']))
            f.write('x, %.4f, %.4f\n' % (self.results['x2'], self.results['x10']))
            f.write('y, %.4f, %.4f\n' % (self.results['y2'], self.results['y10']))
            f.write('u, %.4f, %.4f\n' % (self.results['u2'], self.results['u10']))
            f.write('v, %.4f, %.4f\n' % (self.results['v2'], self.results['v10']))
            f.write('T, %s, %s\n' % (self.results['T2'], self.results['T10']))
            f.write('Duv, %s, %s\n' % (self.results['Duv2'], self.results['Duv10']))
            f.close()

    def on_about(self):
        msg = """
CS-1000: Control the Minolta CS-1000 Spectroradiometer.
        
Copyright (C) 2012-2014 Ivar Farup

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
        """
        qt.QMessageBox.about(self, "About the demo", msg.strip())
    
    def on_connect(self):
        if self.connect_check.isChecked():
            port = str(self.port_text.text())
            if port == '':
                port = 0
            baud = int(self.baud_combo.currentText())
            self.cs.connect(port, baud)
            self.cs.set_remote(True)
        else:
            self.cs.set_remote(False)
            self.cs.disconnect()
    
    def on_measure(self):
        if self.connect_check.isChecked():
            self.cs.measure()
            self.results = self.cs.get_results()
            self.on_draw()
    
    def on_close(self):
        if self.connect_check.isChecked():
            self.cs.set_remote(False)
        self.close()

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = qt.QAction(text, self)
        if icon is not None:
            action.setIcon(qt.QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, qtcore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")
        
        save_spd_action = self.create_action("&Save SPD table",
            shortcut="Ctrl+S", slot=self.on_save_spd, 
            tip="Save the SPD table")
        save_colour_action = self.create_action("Save colour data",
            slot=self.on_save_colour, 
            tip="Save the colour data")
        quit_action = self.create_action("&Quit", slot=self.on_close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (save_spd_action, save_colour_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About CIE Functions')
        
        self.add_actions(self.help_menu, (about_action,))

    def create_main_frame(self):
        self.main_frame = qt.QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((7.0, 5.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Create check box to connect to CS-1000
        self.connect_check = qt.QCheckBox('Connect')
        self.connect(self.connect_check,
                     qtcore.SIGNAL('stateChanged(int)'), self.on_connect)
        
        # Name of the port
        port_name = '<enter port name, e.g., /dev/ttyS0 (posix), COM1 (windows)>'
        if os.name == 'posix':
            if os.path.exists('/dev/ttyUSB0'): # linux usb-serial converter
                port_name = '/dev/ttyUSB0'
            elif os.path.exists('/dev/ttyS0'): # linux serial port
                port_name = '/dev/ttyS0'
            elif os.path.exists('/dev/tty.usbserial'): # mac usb-serial converter
                port_name = '/dev/tty.usbserial'
        elif os.name == 'nt':
            port_name = 'COM3'
        self.port_text = qt.QLineEdit(port_name)

        # Baud rate
        self.baud_combo = qt.QComboBox()
        self.baud_combo.addItem('19200')
        self.baud_combo.addItem('9600')
        self.baud_combo.addItem('4800')
                     
        # Create button for performing measurement:
        self.measure_button = qt.QPushButton('Measure')
        self.connect(self.measure_button,
                     qtcore.SIGNAL('clicked(bool)'), self.on_measure)
        
        self.spd_table = qt.QTableWidget()
        self.colour_table = qt.QTableWidget()

        # Lay out everything
        inner_vbox = qt.QVBoxLayout()
        inner_vbox.addWidget(self.canvas)
        inner_vbox.addWidget(self.mpl_toolbar)
        inner_widget = qt.QWidget()
        inner_widget.setLayout(inner_vbox)      

        tabs = qt.QTabWidget()
        tabs.addTab(inner_widget, 'SPD plot')
        tabs.addTab(self.spd_table, 'SPD table')
        tabs.addTab(self.colour_table, 'Colour data')

        bottom_hbox = qt.QHBoxLayout()
        bottom_hbox.addWidget(self.port_text)
        bottom_hbox.addWidget(self.baud_combo)
        bottom_hbox.addWidget(self.connect_check)
        bottom_hbox.addWidget(self.measure_button)
        
        vbox = qt.QVBoxLayout()
        vbox.addWidget(tabs)
        vbox.addLayout(bottom_hbox)
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def create_status_bar(self):
        self.status_text = qt.QLabel("Ready")
        self.statusBar().addWidget(self.status_text, 1)

def main():
    """
    Run the CS1000 application.
    """
    app = qt.QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
