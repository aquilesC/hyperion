"""
===============
Polarimeter GUI
===============

This is the variable waveplate GUI.


"""
import logging
import sys, os
import numpy as np
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from hyperion.instrument.polarization.polarimeter import Polarimeter
from hyperion import Q_, ur, root_dir
from hyperion.view.base_plot_windows import BaseGraph

class PolarimeterGui(QWidget):
    """ This is the Polarimeter GUI class.
    It builds the GUI for the instrument: polarization.

    """

    MODES = ['Monitor', 'Time Trace'] # measuring modes

    def __init__(self, polarimeter_ins, plot_window):
        """
        Init of the Polarimeter Gui

        :param polarimeter_ins: instrument
        :type an instance of the polarization instrument
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.test = QDoubleSpinBox() # to be removed

        # to load from the UI file
        gui_file = os.path.join(root_dir,'view', 'polarization','polarimeter.ui')
        self.logger.info('Loading the GUI file: {}'.format(gui_file))
        self.gui = uic.loadUi(gui_file, self)

        self.plot_window = plot_window

        # setup the gui
        self.polarimeter_ins = polarimeter_ins
        self.customize_gui()
        #self.get_device_state()
        #self.set_device_state_to_gui()
        self.show()

        #
        self._is_measuring = False
        self.data = np.zeros((13, self.gui.spinBox_measurement_length.value())) # save data
        # to handle the update of the plot we use a timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
       self.logger.debug('Exiting')

    def update_dummy_data(self):
        """ Dummy data update"""
        raw = np.random.rand(13)
        self.data[:, :-1] = self.data[:, 1:]
        self.data[:, -1] = np.array(raw)


    def update_data(self):
        """ sdfsdf """
        raw = self.polarimeter_ins.get_data()
        self.data[:,:-1] =self.data[:,1:]
        self.data[:,-1] = np.array(raw)

    def update_plot(self):
        self.update_data()
        index = 2
        y = self.data[index,:]
        x = np.array(range(len(y)))
        #self.logger.debug('Data: x = {}, y = {}'.format(x,y))
        #self.plot_window.pg_plot.plot(x, y, clear=True)
        self.plot_window.pg_plot.setData(x, y)

    def customize_gui(self):
        """ Make changes to the gui """

        self.logger.debug('Setting channels to plot')
        self._channels_labels = []
        self._channels_check_boxes = []

        self.gui.pushButton_apply_wavelength.clicked.connect(self.change_wavelength)

        # add the channels to detect
        for index, a in enumerate(self.polarimeter_ins.DATA_TYPES_NAME):
            label = QLabel(a)
            box = QCheckBox()
            self._channels_labels.append(label)
            self._channels_check_boxes.append(box)

            self.gui.formLayout_channels.addRow(box, label)

        # set the mode
        self.gui.comboBox_mode.addItems(self.MODES)

        #self.gui.pushButton_start.pressed.connect(self.plot_data)

        self.gui.pushButton_start.clicked.connect(self.start_button)

    def start_button(self):

        #lenth = self.gui.doubleSpinBox_measurement_length
        if self._is_measuring:
            self.logger.debug('Stopping sweep')
            self._is_measuring = False
            # change the button text
            self.gui.pushButton_start.setText('Start')
            self.timer.stop()

        else:
            self.logger.debug('Starting measurement')
            self._is_measuring = True
            # change the button text
            self.gui.pushButton_start.setText('Stop')
            self.timer.start(50)  # in ms
            # self.measurement_thread = WorkThread(self.continuous_data)
            # self.measurement_thread.start()


    def change_wavelength(self):
        """ Gui method to set the wavelength to the device


        """
        w = Q_(self.doubleSpinBox_wavelength.value(), self.doubleSpinBox_wavelength.suffix())
        self.logger.info('Setting the wavelength: {}'.format(w))
        self.polarimeter_ins.change_wavelength(w)


# this is to create a graph output window to dump our data later.
class Graph(BaseGraph):
    """
    In this class a widget is created to draw a graph on.
    """
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.debug('Creating the Graph for the polarization')
        self.title = 'Graph view: Polarimeter'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.initUI()       # This should be called here (not in the parent)

if __name__ == '__main__':
    from hyperion import _logger_format, _logger_settings, root_dir

    logging.basicConfig(level=logging.DEBUG, format=_logger_format,
                        handlers=[
                            logging.handlers.RotatingFileHandler(_logger_settings['filename'],
                                                                 maxBytes=_logger_settings['maxBytes'],
                                                                 backupCount=_logger_settings['backupCount']),
                            logging.StreamHandler()])

    logging.info('Running Polarimeter GUI file.')

    # Create the Instrument (in this case we use the with statement)
    with Polarimeter(settings = {'dummy' : False,
                                 'controller': 'hyperion.controller.sk.sk_pol_ana/Skpolarimeter',
                                 'dll_name': 'SKPolarimeter'}) as polarimeter_ins:
        # Mandatory line for gui
        app = QApplication(sys.argv)

        logging.debug('Creating the graph for the GUI.')
        plot_window = Graph()

        logging.debug('Now starting the GUI')
        PolarimeterGui(polarimeter_ins, plot_window)

        # Mandatory line for gui
        # app.exec_()               # if you don't want it to close the python kernel afterwards
        sys.exit(app.exec_())       # if you do want it to close the python kernal afterwards
