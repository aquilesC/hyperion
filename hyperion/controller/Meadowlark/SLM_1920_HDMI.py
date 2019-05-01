# -*- coding: utf-8 -*-
"""
================
SLM controller
================

This is a fake device, simulated for developing and testing the code.
It can be used as an example to build your own controller for your device.


"""
import logging
from hyperion.controller.base_controller import BaseController
import ctypes as ct

class SLM1920HDMI(BaseController):
    """ Meadowlark SLM 1920 HDMI"""


    def __init__(self, port, dll_path='D://tabauer//nanooptics-code//SLM_control//'):
        """ Init of the class.

        :param port: connection port to use
        :type port: str
        :param dummy: if the device connects to the real or not. in this case is useless, this is a dummy inivented device
        :type dummy: logical
        """
        self._port = port
        self.dummy = dummy
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        ct.cdll.LoadLibrary(dll_path + 'BlinkHdmiSdk')
        self.slm_lib = ct.CDLL(dll_path + 'BlinkHdmiSdk')
        self.logger.info('Class SLM1920HDMI created.')

    def initialize(self, lut_file='D://tabauer//nanooptics-code//SLM_control//lut_optim.blt'):
        """ Starts the connection to the device in port """
        self.lut_file = lut_file
        self.lut = (ct.c_ushort * 256)()

        self.logger.info('Opening connection to device in port {}.'.format(self._port))
        self.sdk = self.slm_lib.Create_SDK()
        self.slm_lib.Read_lut(self.sdk, self.lut_file, self.lut)

        self.slm_lib.Load_lut(self.sdk, self._port, self.lut)

        self.logger.info('Initialized device SLM1920HDMI at port {}.'.format(self.port))
        self._is_initialized = True  # this is to prevent you to close the device connection if you
        # have not initialized it inside a with statement

    def finalize(self):
        """ This method closes the connection to the device.
        It is ran automatically if you use a with block

        """
        self.logger.info('Closing connection to device.')

    def idn(self):
        """ Identify command

        :return: identification for the device
        :rtype: string
        """
        self.logger.debug('Ask IDN to device.')
        return 'Dummy Output controller'

    def query(self, msg):
        """ writes into the device msg

        :param msg: command to write into the device port
        :type msg: string
        """
        self.logger.info('Writing into the example device:{}'.format(msg))
        self.write(msg)
        ans = self.read()
        return ans

    def read(self):
        """ Fake read that returns always the value in the dictionary FAKE RESULTS.
        
        :return: fake result
        :rtype: string
        """
        return self.FAKE_RESPONSES['A']

    def write(self, msg):
        """ Writes into the device
        :param msg: message to be written in the device port
        :type msg: string
        """
        self.logger.debug('Writing into the device:{}'.format(msg))


    @property
    def amplitude(self):
        """ Gets the amplitude value.

        :getter:
        :return: amplitude value in Volts
        :rtype: float

        For example, to use the getter you can do the following

        >>> with DummyOutputController() as dev:
        >>>    dev.initialize('COM10')
        >>>    dev.amplitude
        1

        :setter:
        :param value: value for the amplitude to set in Volts
        :type value: float

        For example, using the setter looks like this:

        >>> with DummyOutputController() as dev:
        >>>    dev.initialize('COM10')
        >>>    dev.amplitude = 5
        >>>    dev.amplitude
        5


        """
        self.logger.debug('Getting the amplitude.')
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):
        # would be nice to add a way to check that the value is within the limits of the device.
        if self._amplitude != value:
            self.logger.info('Setting the amplitude to {}'.format(value))
            self._amplitude = value
            self.write('A{}'.format(value))
        else:
            self.logger.info('The amplitude is already {}. Not changing the value in the device.'.format(value))


class ExampleControllerDummy(ExampleController):
    """ A dummy version of the Example Controller.

    In essence we have the same methods and we re-write the query to answer something meaninfull but
    without connecting to the real device.

    """


    def query(self, msg):
        """ writes into the device msg

        :param msg: command to write into the device port
        :type msg: string
        """
        self.logger.debug('Writing into the dummy device:{}'.format(msg))
        ans = 'dummy answer'
        return ans



if __name__ == "__main__":
    from hyperion import _logger_format
    logging.basicConfig(level=logging.DEBUG, format=_logger_format,
        handlers=[logging.handlers.RotatingFileHandler("logger.log", maxBytes=(1048576*5), backupCount=7),
                  logging.StreamHandler()])

    with ExampleController() as dev:
        dev.initialize('COM10')
        print(dev.amplitude)
        dev.amplitude = 5
        print(dev.amplitude)


