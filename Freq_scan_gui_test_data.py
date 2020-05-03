from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import numpy as np
import math
from pyqtgraph.Qt import QtGui, QtCore
import SR_810 as sr_810
import pyvisa
import datetime;
import random;
import time
import os

# STARTING PARAMETERS OF OSCILLOSCOPE AND PROGRAMM
i = 0;              # points iterator
array_x = [];
array_r = [];
array_freq = [];
j = 1;              # scans iterator
path = '';          # memorize path to Open/Sae file
s = 1;              # check for save data

frequency_1 = 80000; # frequency start in Hz
frequency_2 = 2;     # frequency finish in Hz
points = 20;       # points in scan
number_scans = 1;    # number od scans
mod_amplitude = 2;   # modulation amplitude in V

time_constant= 1000;   # TC in ms
set_timer = float(time_constant); # timer for updating graph; in ms

# tc_index for QComboBox handling
if set_timer == 0.01:
    tc_index = 0;
elif set_timer == 0.03:
    tc_index = 1;
elif set_timer == 0.1:
    tc_index = 2;
elif set_timer == 0.3:
    tc_index = 3;
elif set_timer == 1:
    tc_index = 4;
elif set_timer == 3:
    tc_index = 5;
elif set_timer == 10:
    tc_index = 6;
elif set_timer == 30:
    tc_index = 7;
elif set_timer == 100:
    tc_index = 8;
elif set_timer == 300:
    tc_index = 9;
elif set_timer == 1000:
    tc_index = 10;
elif set_timer == 3000:
    tc_index = 11;
elif set_timer == 10000:
    tc_index = 12;
elif set_timer == 30000:
    tc_index = 13;
elif set_timer == 100000:
    tc_index = 14;
elif set_timer == 300000:
    tc_index = 15;
else:
    tc_index = 11;

# STARTING INITIALIZATION
##sr_810.connection()

# DESCRIPTION OF GUI FUNCTIONS AND WINDOWS
class Help(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(Help, self).__init__(parent)

        uic.loadUi('help.ui', self)   # QtDesigner file with design
        self.actionQuit.triggered.connect(self.close_2)

    # Description of functions
    def close_2(self):
        self.close()
#####################################################################
class Scan_Change(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(Scan_Change, self).__init__(parent)

        uic.loadUi('scan.ui', self)   # QtDesigner file with design
        self.change_scan.setValue(number_scans)
        self.change_scan.valueChanged.connect(self.getValue)
        self.actionQuit.triggered.connect(self.close_2)
        self.butsubmit_scan.clicked.connect(self.submit)


    # Getting value from QSpinBox
    def getValue(self):
        self.value = self.change_scan.value()
        return self.value

    # Submitting parameters
    def submit(self):
        global number_scans, j

        number_scans = self.getValue()
        if number_scans < j:
            number_scans = j
            self.change_scan.setValue(number_scans)
            print("Too Low Scans")

    # Description of functions
    def close_2(self):
        self.close()
#########################################################################

class Parameters(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(Parameters, self).__init__(parent)

        uic.loadUi('parameters.ui', self)   # QtDesigner file with design

        self.modAmpl.setValue(mod_amplitude)        # for setting initial value in QSpinBox
        self.numScan.setValue(number_scans)
        self.freqstart.setValue(frequency_1)
        self.freqfinish.setValue(frequency_2)
        self.numpoints.setValue(points)
        self.timeconst.setCurrentIndex(tc_index)    # QComboBox works with indexes

        # Connection of different function to different action
        self.actionQuit.triggered.connect(self.close_2)
        self.modAmpl.valueChanged.connect(self.getValue)
        self.numScan.valueChanged.connect(self.getValue_2)
        self.freqstart.valueChanged.connect(self.getValue_3)
        self.freqfinish.valueChanged.connect(self.getValue_4)
        self.numpoints.valueChanged.connect(self.getValue_5)
        self.timeconst.currentIndexChanged.connect(self.getValue_6)
        self.butsubmit.clicked.connect(self.submit)

    # Description of functions
    def close_2(self):
        self.close()
    # Getting value from QSpinBox
    def getValue(self):
        self.value = self.modAmpl.value()    # Value of mod amplitude
        return self.value
    def getValue_2(self):
        self.value = self.numScan.value()    # Value of Number of scans
        return self.value
    def getValue_3(self):
        self.value = self.freqstart.value()    # Value of freq start
        return self.value
    def getValue_4(self):
        self.value = self.freqfinish.value()    # Value of freq finish
        return self.value
    def getValue_5(self):
        self.value = self.numpoints.value()    # Value of points
        return self.value
    def getValue_6(self):
        self.value = self.timeconst.currentText()    # Value of time constant
        return self.value
    def getValue_7(self):
        self.value = self.timeconst.currentIndex()    # Value of index of time constant
        return self.value


    # Submitting parameters to lock-in
    def submit(self):
        global frequency_1, mod_amplitude, time_constant, set_timer, number_scans, points, frequency_2, tc_index

        frequency_1 = self.getValue_3()
        mod_amplitude = self.getValue()
        number_scans = self.getValue_2()
        points = self.getValue_5()
        frequency_2 = self.getValue_4()
        time_constant = float(self.getValue_6())
        tc_index = int(self.getValue_7())
        set_timer = time_constant;

        #print(self.ampl_calibration(mod_amplitude, frequency_1))
        #self.close()
        #sr_810.lock_in_modulation_frequency(frequency_1)
        #sr_810.lock_in_amplitude(self.ampl_calibration(mod_amplitude, frequency_1))
        #sr_810.lock_in_time_constant(time_constant)

    def ampl_calibration(self, ampl_g, f):          # modulation amplitude calibration curve

        a = 0.017*math.sqrt(f)*ampl_g;
        return a


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('main_window.ui', self)        # Design file
        self.lineScans.setText("Scans: " + str(number_scans))    # number of scans

        # Connection of different action to different Menus and Buttons
        self.actionFile.triggered.connect(self.exit)
        self.actionOpen.triggered.connect(self.open_dialog) # open file dialog
        self.pushSave.clicked.connect(self.save_dialog)     # save file dialog
        self.actionlock_in.triggered.connect(self.parameters_window)
        self.actionAbout.triggered.connect(self.help_window)
        self.pushStart.clicked.connect(self.start)      # buttons here work better than menus
        self.pushStop.clicked.connect(self.stop)
        self.pushClear.clicked.connect(self.clear_plot)
        self.actionAdd_Scan.triggered.connect(self.change_scan_window)#########################################################################

    # Functions that are connected to Menu
    def ampl_calibration(self, ampl_g, f):

        a = 0.017*math.sqrt(f)*ampl_g;
        return a

    def new_point(self):
        global final_data_r, i, array_r, array_x, array_freq, j, start_time, end_time

        self.lineScans.setText("Scans: " + str(number_scans))    # number of scans

        if j <= number_scans:
            self.lineScans.setStyleSheet("QLabel { background-color : rgb(255, 0, 0) }");
            self.lineScans.setText("Scans: " + str(j) + "/"+ str(number_scans))    # number of scans

            if i < points and j == 1:
                # Getting data from lock-in
                #data_x, data_y, data_r = sr_810.lock_in_signal()

                data_x = random.randint(0, 1000)
                data_r = random.randint(0, 1000)

                #freq_current = lock_in_modulation_frequency(frequency_1-step)
                ####################################################################################################################### modulation_amplitude changing
                freq_current = 10**(math.log10(frequency_1 - frequency_2)/points*(points - i)) + frequency_2            # special log step
                mod_amplitude_v = self.ampl_calibration(mod_amplitude, freq_current);
                #print(mod_amplitude_v)
                #frequency_1-step*i

                array_x = np.append(array_x, np.asarray(data_x))
                #array_y = np.append(array_y, np.asarray(data_y))
                array_r = np.append(array_r, np.asarray(data_r))
                array_freq = np.append(array_freq, np.asarray(freq_current))

                final_data_r = np.column_stack((array_freq, array_r, array_x))                                                   # appropriate format for pyqtgraph


                i = i + 1;
                end_time = time.time();
                self.lineTime.setText("Time (s): " + str(round((end_time - start_time), 1)) + "/" + str(round(time_constant*points*number_scans/1000,0)))    # time update

                #print(array_r[0])
            elif i == points:
                # Getting data from lock-in
                #data_x, data_y, data_r = sr_810.lock_in_signal()
                i = 0;
                j = j + 1;
                print("scan done")
            elif i < points and j > 1:
                data_x = random.randint(0, 1000)
                data_r = random.randint(0, 1000)

                #freq_current = lock_in_modulation_frequency(frequency_1-step)
                ################################################################################################################### modulation_amplitude changing
                freq_current = 10**(math.log10(frequency_1 - frequency_2)/points*(points - i)) + frequency_2
                mod_amplitude_v = self.ampl_calibration(mod_amplitude, freq_current);
                #print(mod_amplitude_v)
                #freq_current = frequency_1-step*i

                array_x[i] = (array_x[i]*(j-1) + np.asarray(data_x))/j
                #array_y = np.append(array_y, np.asarray(data_y))
                array_r[i] = (array_r[i]*(j-1) + np.asarray(data_r))/j

                final_data_r = np.column_stack((array_freq, array_r, array_x))            # appropriate format for pyqtgraph

                i = i+1;
                end_time = time.time();
                self.lineTime.setText("Time (s): " + str(round((end_time - start_time), 1)) + "/" + str(round(time_constant*points*number_scans/1000,0)))    # time update
                #print(final_data_r)
        else:
            self.lineScans.setStyleSheet("QLabel { background-color : rgb(0, 255, 0) }");    # number of scans

            # for saving raw data
            currenttime = datetime.datetime.now();
            file = open("00_temp_data.txt",'ab')
            np.savetxt(file, np.array(['# '+ str(currenttime)  + ', \n' 'Frequency (Hz),' + 'Intensity (a. u.) R,' + 'Intensity (a. u.) X']), fmt='%s')
            np.savetxt(file, final_data_r, delimiter=',', fmt='%.5e')
            file.close()

            self.timer.stop()

        return final_data_r

    # Experimental data plotting
    def plot(self, data1, data2):
        pen = pg.mkPen(color = (255, 255, 0, 255)) # pen for plotting slightly transparent yellow line; the last argument is opacity; 255 - no transparancy; 0 - full transparancy
        pen2 = pg.mkPen(color = (0, 0, 255, 255)) # pen for plotting slightly transparent yellow line; the last argument is opacity; 255 - no transparancy; 0 - full transparancy
        self.graphicsView.setTitle(title = "Frequency Scan")
        self.graphicsView.plot(data1, pen = pen, clear = True)  # actual plotting and clear the previous one
        self.graphicsView.plot(data2, pen = pen2)  # actual plotting and clear the previous one
        self.graphicsView.showGrid(x=True, y=True) # Grid
        self.graphicsView.setLogMode(True, False)  # LogX Plot
        self.graphicsView.setXRange(math.log10(frequency_1), math.log10(frequency_2), padding=0.055) # x axis range
        self.graphicsView.setLabel('bottom', text = "Frequency (Hz)")
        self.graphicsView.setLabel('left', text = "Intensity (a. u.)")

    def exit(self):
        #sr_810.close_connection()
        sys.exit()
    # function for updating plot when a new data from lock-in arrives
    def updating(self):

        # clear our graphs
        #self.graphicsView.clear()      # changed to clear = True
        # get new data
        final_data_r = self.new_point()
        # plot new data
        self.plot(final_data_r[:,[0,1]], final_data_r[:,[0,2]])

    # function to start timer for updating
    def start(self):
        global set_timer, array_r, array_x, array_freq, i, j, start_time, s

        if s == 0:      # for checking whether the data was saved before the start button is pressed
            message = QMessageBox(self);            # Message Box fow warning of unsaved data
            message.setWindowTitle("Are you sure?")
            message.setStyleSheet("QWidget { background-color : rgb(136, 138, 133) }")  # change background color of the open file window
            message.addButton(QtGui.QPushButton('Save'), QtGui.QMessageBox.NoRole)      # adding buttons
            message.addButton(QtGui.QPushButton('Yes'), QtGui.QMessageBox.YesRole)
            message.setText("Data was not saved. Are you sure?    ");
            message.show();
            message.buttonClicked.connect(self.clicked)                         # connect function clicked to button; get the button name
            return                                                              # stop current function

        start_time = time.time()
        #recalculation of timer for real time_constant used
        #set_timer = float(lock_in_time_constant());
        array_x = [];
        array_r = [];
        array_freq = [];
        i = 0;
        j = 1;

        set_timer = float(time_constant);
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updating)
        self.timer.start(set_timer)

        s = 0;      #  for checking whether the data was saved before the start button is pressed

    def clicked(self, btn):             # Message Box fow warning of unsaved data
        global s
        if btn.text() == "Save":
            self.save_dialog()
        elif btn.text() == "Yes":
            s = 1;  #  for checking whether the data was saved before the start button is pressed
            self.start()
        else:
            return

    def clicked_2(self, btn):           # Message Box fow warning of unsaved data for clear button
        global s
        if btn.text() == "Save":
            self.save_dialog()
        elif btn.text() == "Yes":
            s = 1;      #  for checking whether the data was saved before the start button is pressed
            self.graphicsView.clear()
        else:
            return

    def stop(self):
        global i, j
        i = 0;
        j = 1;
        self.timer.stop()

    def clear_plot(self):
        global s

        if s == 0:
            message = QMessageBox(self);                # Message Box fow warning of unsaved data (see above)
            message.setWindowTitle("Are you sure?")
            message.setStyleSheet("QWidget { background-color : rgb(136, 138, 133) }")  # change background color of the open file window
            message.addButton(QtGui.QPushButton('Save'), QtGui.QMessageBox.NoRole)
            message.addButton(QtGui.QPushButton('Yes'), QtGui.QMessageBox.YesRole)
            message.setText("Data was not saved. Are you sure?    ");
            message.show();
            message.buttonClicked.connect(self.clicked_2)           # connect function clicked to button; get the button name
            return
        else:
            self.graphicsView.clear()
            s = 1;          # for checking whether the data was saved before the start button is pressed

    # New windows for parameters
    def parameters_window(self):
        global frequency_1, mod_amplitude, time_constant, number_scans, points, frequency_2

        #frequency_1 = sr_810.lock_in_modulation_frequency()
        #mod_amplitude_v = sr_810.lock_in_amplitude()
        #time_constant = sr_810.lock_in_time_constant()
        frequency_1 = frequency_1;
        mod_amplitude = mod_amplitude;
        points = points;
        number_scans = number_scans;
        time_constant = time_constant;

        self.dialog = Parameters(self)
        self.dialog.show()

############################################################################
    # New windows for scan change
    def change_scan_window(self):
        global number_scans

        number_scans = number_scans;

        self.dialog = Scan_Change(self)
        self.dialog.show()
############################################################################

    # New windows for help
    def help_window(self):

        self.dialog = Help(self)
        self.dialog.show()

    # Function for Open and Show file:
    def file_open(self, filename):
        global path
        file_data = np.genfromtxt(filename, skip_header = 1, delimiter=',', usecols=(0, 1))         # read csv with some useful options
        self.graphicsView.setTitle(title = "Frequency Scan")
        self.graphicsView.plot(file_data, pen = pg.mkPen(color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)))
        self.graphicsView.showGrid(x=True, y=True) # Grid
        self.graphicsView.setLogMode(True, False)  # LogX Plot
        self.graphicsView.setXRange(math.log10(file_data[0,0]), math.log10(file_data[-1,0]), padding=0.055) # x axis range
        self.graphicsView.setLabel('bottom', text = "Frequency (Hz)")
        self.graphicsView.setLabel('left', text = "Intensity (a. u.)")
        path = os.path.dirname(filename) # for memorizing the path to the last used folder

    def open_dialog(self):
        global path

        if path == '':
            path = "/home/anatoly/Documents"

        filedialog = QFileDialog(self, 'Open File', directory = path, filter ="text (*.txt *.csv *.dat)", options = QFileDialog.DontUseNativeDialog) # use QFileDialog.DontUseNativeDialog to change directory
        filedialog.setStyleSheet("QWidget { background-color : rgb(136, 138, 133) }")  # change background color of the open file window
        filedialog.setFileMode(QtGui.QFileDialog.AnyFile)

        filedialog.fileSelected.connect(self.file_open) # connect to action; send filename to fumction file_open
        filedialog.show()

    # Function for Save file:
    def file_save(self, filename):
        global path

        try:
            if len (final_data_r) > 1:
                open(filename, "w").close()     # remove all the data from file before saving
                file = open(filename,'ab')
                np.savetxt(file, np.array(['Frequency (Hz),' + 'Intensity R (a. u.),' + 'Intensity (a. u.) X']), fmt='%s')
                np.savetxt(file, final_data_r, delimiter=',', fmt='%.5e')
                file.close()
        except NameError:       # if there isno data to save
                message = QMessageBox(self);
                message.setWindowTitle("Warning")
                message.setStyleSheet("QWidget { background-color : rgb(136, 138, 133) }")  # change background color of the open file window
                message.setText("No data to save   ");
                message.show();

        path = os.path.dirname(filename) # for memorizing the path to the last used folder

    def save_dialog(self):
        global path, s

        s = 1;              # for checking whether the data was saved before the start button is pressed
        if path == '':
            path = "/home/anatoly/Documents"

        filedialog = QFileDialog(self, 'Enter File Name', directory = path, options = QFileDialog.DontUseNativeDialog) # use QFileDialog.DontUseNativeDialog to change directory
        filedialog.setStyleSheet("QWidget { background-color : rgb(136, 138, 133) }")  # change background color of the open file window
        filedialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)

        filedialog.fileSelected.connect(self.file_save)          # connect to action; send filename to fumction file_save
        filedialog.show()

# Running of the main window
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
    #sys.exit(app.exec_() and sr_810.close_connection())

if __name__ == '__main__':
    main()
