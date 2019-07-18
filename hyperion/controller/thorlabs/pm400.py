# -*- coding: utf-8 -*-
"""
================
PM 400 controler
================



"""
import ctypes
import logging
from hyperion.controller.base_controller import BaseController


class Pm400(BaseController):
    """Thorlambs Pm400 power meter.

    """
    DEFAULTS = {'serial number': 'P5000958'
                }


    def __init__(self, settings = {'instrument_id':'PM400', 'dummy': False}):
        """ Init for the class. It takes a dictionary that passes the settings needed. In this case
        it needs

        instrument_id : '8967' # instrument id for the device you have
        dummy : False


        """
        super().__init__()
        # TODO: put this in a config.yml file so the code doe not depend on the location (PC)
        path = 'C:/Program Files/IVI Foundation/VISA/Win64/Bin/'
        name = 'TLPM_64'
        self.logger.debug('DLL to use: {}'.format(path + name))
        self.dll = ctypes.CDLL(path + name)
        self.logger.debug('Using DLL: {}'.format(self.dll))

        self.rsc = None
        self.instrument_id = settings['instrument_id']
        self.dummy = settings['dummy']
        self.logger.info('Created controller class for PM400 ')
        self.logger.info('Dummy mode: {}'.format(self.dummy))

    def find_resource(self):

        #    ViStatus        _VI_FUNC        TLPM_findRsrc(ViSession        instrumentHandle, ViPUInt32        resourceCount);
        handle = 0
        handle = ctypes.
        self.logger.info('Initialization of PM400 name {}, with ID = {} , reset = {}, ' \
                         'handle = {}.'.format(name.value, id.value, reset.value, handle.value))

        func = self.dll.TLPM_init
        func.argtypes = [ctypes.c_int, ctypes.c_bool, ctypes.c_bool, ctypes.c_char]

        ans = func(resourceName, idquery, reset, handle)
        self.logger.debug('Answer from the SkInitPolarimeter: {}'.format(ans))

    def initialize(self):
        """ This method opens the communication with the device.

        """
        self.logger.debug('Now initializing the PM400 ')
        #TLPM_init(ViRsrc resourceName, ViBoolean        IDQuery, ViBoolean        resetDevice, ViPSession        instrumentHandle)
        resourceName = b'PM'
        idquery = False
        reset = False
        handle = b' '
        name = ctypes.c_char(resourceName)
        id = ctypes.c_bool(idquery)
        reset = ctypes.c_bool(reset)
        handle = ctypes.c_char(handle)

        self.logger.info('Initialization of PM400 name {}, with ID = {} , reset = {}, '\
                         'handle = {}.'.format(name.value, id.value, reset.value, handle.value))

        func = self.dll.TLPM_init
        func.argtypes = [ctypes.c_int, ctypes.c_bool, ctypes.c_bool, ctypes.c_char]

        ans = func(resourceName, idquery, reset, handle)
        self.logger.debug('Answer from the SkInitPolarimeter: {}'.format(ans))

        return ans

        self._is_initialized = True

    def finalize(self):
        """ Closing communication with device

        """
        self.logger.info('Closing connection with device number: {}'.format(self.id))
        ans = self.dll.SkCloseConnectionByID(self.id)
        self.logger.debug('Answer from the SkCloseConnection: {}'.format(ans))

        return ans

    def get_device_information(self):
        """ Get SK polarization analyzer information. This function adds the obtained values
        to the properties of the class so they are accessible for all the functions

        :return: reading answer from the function
        :rtype: int


        """
        len = ctypes.c_int(0)
        id = ctypes.c_int(0)
        serial_number = ctypes.c_int(0)
        min_w = ctypes.c_int(0)
        max_w = ctypes.c_int(0)
        self.logger.info('Getting device information')
        self.logger.debug('Sending to device: len: {}, id: {}, serial: {}, min: {}, max: {}. '.format(
            len, id, serial_number, min_w, max_w))
        ans = self.dll.SkGetDeviceInformation(len, ctypes.pointer(id), ctypes.pointer(serial_number),
                                              ctypes.pointer(min_w), ctypes.pointer(max_w))
        self.logger.debug('Answer from SkGetDeviceInformation: {}'.format(ans))
        self.id = int(id.value)
        self.serial_number = int(serial_number.value)
        self.min_w = int(min_w.value)
        self.max_w = int(max_w.value)
        self.logger.info('ID: {}'.format(self.id))
        self.logger.info('Serial number: {}'.format(self.serial_number))
        self.logger.info('Min Wavelength: {} nm'.format(self.min_w))
        self.logger.info('Max Wavelength: {} nm'.format(self.max_w))


if __name__ == "__main__":
    from hyperion import _logger_format, _logger_settings

    logging.basicConfig(level=logging.DEBUG, format=_logger_format,
                        handlers=[logging.handlers.RotatingFileHandler(_logger_settings['filename'],
                                                                       maxBytes=_logger_settings['maxBytes'],
                                                                       backupCount=_logger_settings['backupCount']),
                                  logging.StreamHandler()])

    with Pm400(settings = {'instrument_id':'PM400', 'dummy': False}) as pwm:
        # initialize
        pwm.initialize()