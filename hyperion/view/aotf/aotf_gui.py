"""
===================
AOTF instrument GUI
===================

This is the GUI for the AOTF



"""

import logging
import sys, os
from PyQt5 import uic
from PyQt5.QtGui import QStandardItem, QColor, QIcon
from PyQt5.QtWidgets import *
from hyperion.instrument.aotf.aa_aotf import AaAotf
from hyperion import Q_, ur, root_dir


class AotfGui(QWidget):

    def __init__(self, aotf_ins):
        """
        Init of the AOTFGui

        :param aotf_ins: instrument
        :type an instance of the aoft instrument
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # to load from the UI file
        gui_file = os.path.join(root_dir,'view', 'aotf','aotf_instrument.ui')
        self.logger.info('Loading the GUI file: {}'.format(gui_file))
        self.gui = uic.loadUi(gui_file, self)
        # define internal variables to update the GUI
        self._output = None
        self._mode = None
        self._analog_value_1 = None
        self._analog_value_2 = None

        # setup the gui
        self.aotf_ins = aotf_ins
        self.customize_gui()
        self.get_device_state()
        self.set_device_state_to_gui()
        self.show()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
       self.logger.debug('Exiting')

    def customize_gui(self):
        """ Make changes to the gui """
        self.logger.debug('Setting Wavelength spinboxes settings')

        # enable
        self.gui.pushButton_state.clicked.connect(self.state_clicked)
        self.gui.enabled = QWidget()

        # connect the voltage and frequency spinbox a function to send the
        self.gui.doubleSpinBox_wavelength_delta.valueChanged.connect(
            lambda value: self.gui.doubleSpinBox_wavelength.setSingleStep(value))
        self.gui.doubleSpinBox_wavelength.valueChanged.connect(self.send_wavelegnth)


    def send_wavelegnth(self, value):
        """ Sets the QWP wavelength to the device"""
        self.aotf_ins.set_wavelength(Q_(value, self.gui.doubleSpinBox_wavelength.suffix()))


    def get_device_state(self):
        """ Gets the state for all the settings form the device """
        pass

    def set_device_state_to_gui(self):
        """ Sets the device state to the GUI """
        self.state_clicked(self._states[self.aotf_ins._channel_in_use-1])
        self.gui.pushButton_state.setChecked(self._output)
        self.gui.doubleSpinBox_v1.setValue(self._analog_value_1.m_as('volt'))
        self.gui.doubleSpinBox_v2.setValue(self._analog_value_2.m_as('volt'))
        self.gui.doubleSpinBox_frequency.setValue(self.variable_waveplate_ins.freq.m_as('Hz'))
        self.gui.comboBox_mode.setCurrentIndex(self.variable_waveplate_ins.MODES.index(self.variable_waveplate_ins.mode))
        self.gui.doubleSpinBox_wavelength.setValue(self.variable_waveplate_ins._wavelength.m_as('nm'))

    def state_clicked(self, state):
        """ Enable output"""
        self.logger.debug('Send the state to the device')
        self.variable_waveplate_ins.output = state
        self._output = state
        self.logger.debug('Changing apearence of the button')
        self.gui.pushButton_state.setText(['Disabled','Enabled'][state])
        self.gui.pushButton_state.setStyleSheet("background-color: "+['red','green'][state])
        return state

    def change_step_v1(self, v, obj):
        self.gui.doubleSpinBox_v1.setDecimals(3)

    def set_channel_textfield_disabled(self, v):
        """
        if the mode is Voltage1 then it is not possible to
        write something in textbox of Voltage 2 or the others
        """
        if self.gui.comboBox_mode.currentText() == "Voltage1":
            self.gui.doubleSpinBox_v1.setEnabled(True)
            self.gui.doubleSpinBox_v1_delta.setEnabled(True)
            self.gui.doubleSpinBox_v2.setEnabled(False)
            self.gui.doubleSpinBox_v2_delta.setEnabled(False)
            self.gui.doubleSpinBox_frequency.setEnabled(False)
            self.gui.doubleSpinBox_frequency_delta.setEnabled(False)
            self.gui.doubleSpinBox_wavelength.setEnabled(False)
            self.gui.doubleSpinBox_wavelength_delta.setEnabled(False)

        elif self.gui.comboBox_mode.currentText() == "Voltage2":
            self.gui.doubleSpinBox_v1.setEnabled(False)
            self.gui.doubleSpinBox_v1_delta.setEnabled(False)
            self.gui.doubleSpinBox_v2.setEnabled(True)
            self.gui.doubleSpinBox_v2_delta.setEnabled(True)
            self.gui.doubleSpinBox_frequency.setEnabled(False)
            self.gui.doubleSpinBox_frequency_delta.setEnabled(False)
            self.gui.doubleSpinBox_wavelength.setEnabled(False)
            self.gui.doubleSpinBox_wavelength_delta.setEnabled(False)

        elif self.gui.comboBox_mode.currentText() == "Modulation":
            self.gui.doubleSpinBox_v1.setEnabled(True)
            self.gui.doubleSpinBox_v1_delta.setEnabled(True)
            self.gui.doubleSpinBox_v2.setEnabled(True)
            self.gui.doubleSpinBox_v2_delta.setEnabled(True)
            self.gui.doubleSpinBox_frequency.setEnabled(True)
            self.gui.doubleSpinBox_frequency_delta.setEnabled(True)
            self.gui.doubleSpinBox_wavelength.setEnabled(False)
            self.gui.doubleSpinBox_wavelength_delta.setEnabled(False)


        elif self.gui.comboBox_mode.currentText() == "QWP":
            self.gui.doubleSpinBox_v1.setEnabled(False)
            self.gui.doubleSpinBox_v1_delta.setEnabled(False)
            self.gui.doubleSpinBox_v2.setEnabled(False)
            self.gui.doubleSpinBox_v2_delta.setEnabled(False)
            self.gui.doubleSpinBox_frequency.setEnabled(False)
            self.gui.doubleSpinBox_frequency_delta.setEnabled(False)
            self.gui.doubleSpinBox_wavelength.setEnabled(True)
            self.gui.doubleSpinBox_wavelength_delta.setEnabled(True)


if __name__ == '__main__':
    from hyperion import _logger_format, _logger_settings, root_dir
    from os import path

    logging.basicConfig(level=logging.INFO, format=_logger_format,
                        handlers=[
                            logging.handlers.RotatingFileHandler(_logger_settings['filename'],
                                                                 maxBytes=_logger_settings['maxBytes'],
                                                                 backupCount=_logger_settings['backupCount']),
                            logging.StreamHandler()])

    logging.info('Running AOTF GUI file.')
    with AaAotf(settings = {'port':'COM10', 'dummy':False,
                           'controller': 'hyperion.controller.aa.aa_modd18012/AaModd18012'}) as aotf_ins:

        aotf_ins.initialize()
        app = QApplication(sys.argv)
        #app.setWindowIcon(QIcon(path.join(root_dir,'view','gui','vwp_icon.png')))
        GUI = AotfGui(aotf_ins)
        sys.exit(app.exec_())


