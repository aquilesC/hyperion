# -*- coding: utf-8 -*-
"""
=========================
Generic Serial Controller
=========================

This is a generic controller for Serial devices (like Arduino).
It includes serial write and query methods.
Higher level stuff could (should?) be done at Instrument level.
Extra methods could however also be added to this controller,
as long as they don't break the existing functionality.

This controller is however intended to be agnostic of what code/firmware/sketch
is running on the device. I suggest to keep it that way and put device
specific functionality in a dedicated instrument.
This also means Dummy mode needs to be implemented mostly at Instrument level.

"""
import serial
import serial.tools.list_ports
import time
import logging
from hyperion.controller.base_controller import BaseController

class GenericSerialController(BaseController):
    """ Generic Serial Controller """


    def __init__(self, settings = {'port':'COM4', 'dummy': False, 'baudrate': 9600, 'write_termination': '\n', 'read_timeout':1.0}):
        """ Init of the class.

        :param settings: this includes all the settings needed to connect to the device in question.
        :type settings: dict

        """
        super().__init__(settings)  # mandatory line
        self.logger = logging.getLogger(__name__)
        self.rsc = None
        self.logger.debug('Generic Serial Controller created.')
        self.name = 'Generic Serial Controller'

        if 'dummy' in settings:
            self.dummy = settings['dummy']
        else:
            self.dummy = False
            
        if 'port' in settings:
            self._port = settings['port']
        else:
            self._port = None
        
        if 'baudrate' in settings:
            self._baud = settings['baudrate']
        else:
            self._baud = 9600
            
        if 'write_termination' in settings:
            self._write_termination = settings['write_termination']
        else:
            self._write_termination = '\n'
            
        if 'read_termination' in settings:
            self._read_termination = settings['read_termination']
        else:
            self._read_termination = '\n'

        if 'write_timeout' in settings:
            self._write_timeout = settings['write_timeout']
        else:
            self._write_timeout = 0.1
            
        if 'read_timeout' in settings:
            self._read_timeout = settings['read_timeout']
        else:
            self._read_timeout = 0.1
            
        if 'encoding' in settings:
            self._encoding = settings['encoding']
        else:
            self._encoding = 'ascii'
            
        if 'name' in settings:
            self.name = settings['name']
        else:
            self.name = 'Serial Device'
            
        

    def initialize(self):
        """ Starts the connection to the device in port """
        self.rsc = serial.Serial(port=self._port,
                                     baudrate=self._baud,
                                     timeout=self._read_timeout,
                                     write_timeout=self._write_timeout)
        self.logger.debug('Initialized Serial connection to {} on port {}.'.format(self.name, self._port))
        self._is_initialized = True     # THIS IS MANDATORY!!
                                        # this is to prevent you to close the device connection if you
                                        # have not initialized it inside a with statement


    def finalize(self):
        """ This method closes the connection to the device.
        It is ran automatically if you use a with block
        """
        
        if self._is_initialized:
            if self.rsc is not None:
                self.rsc.close()
                self.logger.debug('The Serial connection to {} is closed.'.format(self.name))
        else:
            self.logger.warning('Finalizing before initializing connection to {}'.format(self.name))

        self._is_initialized = False
        

    def idn(self):
        """ Identify command

        :return: identification for the device
        :rtype: string
        """
        self.logger.debug('Ask *IDN? to device.')
        return self.query('*IDN?')

    def write(self, message):
        """ Sends the message to the device.

        :param message: the message to write to the device
        :type message: string

        """
        if not self._is_initialized:
            raise Warning('Trying to write to device before initializing')

        message += self._write_termination
        self.logger.debug('Sending to device: {}'.format(message))
        self.rsc.write( message.encode(self._encoding) )



    def read_serial_buffer_in(self, wait_for_termination_char = True):
        """
        Reads everything the device has sent. By default it waits until a line
        is terminated by a termination character (\n or \r), but that check can
        be disabled using the input parameter.

        :param untill_at_least_one_termination_char: defaults to True
        :type untill_at_least_one_termination_char: bool 
        :return: complete serial buffer from the device
        :rtype: bytes

        """
        if not self._is_initialized:
            raise Warning('Trying to read from {} before initializing'.format(self.name))
        
        # At least for Arduino, it appears the buffer is filled in chuncks of max 32 bytes
        byte_time = 1/self.rsc.baudrate * (self.rsc.bytesize + self.rsc.stopbits + (self.rsc.parity != 'N'))
        raw = b''
        in_buffer = 0
        new_in_buffer = 0
        term_chars = '\n\r'.encode(self._encoding)
        ends_at_term_char = False
        #start_time = time.time() + 0.0001
        # Keep checking 
        expire_time = time.time() +  self._read_timeout + .0000000001
        while (not ends_at_term_char) and (time.time() < expire_time):
            time.sleep(byte_time*20)
            new_in_buffer = self.rsc.in_waiting
            if new_in_buffer > in_buffer:
                # if the buffer has grown make sure the expire_time is at least long enough to read in another 32 bytes
                expire_time = max(expire_time, time.time()+byte_time*32)
                in_buffer = new_in_buffer
            
            raw += self.rsc.read( self.rsc.in_waiting )
            if not wait_for_termination_char or (len(raw) and (raw[-1] in term_chars)):
                ends_at_term_char = True
            
        self.logger.debug('{} bytes received'.format(len(raw)))
        return raw
           
    def read_lines(self, remove_leading_trailing_empty_line=True):
        """
        Reads all lines the device has sent and returns list of strings.
        It interprets both \r \n and combinations as a newline character.

        :param remove_leading_trailing_empty_line: defaults to True
        :type remove_leading_trailing_empty_line: bool
        :return: list of lines received from the device
        :rtype: list of strings
        """
        
        response = str(self.read_serial_buffer_in(), encoding=self._encoding)
        response = response.replace('\n\r','\n')
        response = response.replace('\r\n','\n')
        response = response.replace('\r','\n')
        response_list = response.split('\n')
        if remove_leading_trailing_empty_line:
            if len(response_list) and response_list[-1]=='':
                del response_list[-1]
            if len(response_list) and response_list[0]=='':
                del response_list[0]
            
        return response_list
    
    def query(self, message):
        """
        Writes message in the device Serial buffer and Reads the response.
        Note, it clears the input buffer before sending out the query.

        :param message: command to send to the device
        :type message: str
        :return: response from the device
        :rtype: str
        """
        
        if not self._is_initialized:
            raise Warning('Trying to query from the device before initializing.')

        self.rsc.reset_output_buffer()
        self.rsc.reset_input_buffer()
        self.write(message)
        self.logger.debug('Sent message: {}.'.format(message))
        ans = self.read_lines()
        self.logger.debug('Received message: {}.'.format(ans))
        return ans
    


class GenericSerialControllerDummy(GenericSerialController):
    """
    Serial Controller Dummy
    ========================

    A dummy version of the Generic Serial Controller.

    In essence we have the same methods and we re-write the query to answer something meaningful but
    without connecting to the real device.

    """


    def query(self, msg):
        """ writes into the device msg

        :param msg: command to write into the device port
        :type msg: string
        """
        self.logger.debug('Writing into the dummy device:{}'.format(msg))
        ans = 'A general dummy answer'
        return ans



if __name__ == "__main__":
    from hyperion import _logger_format, _logger_settings
    logging.basicConfig(level=logging.ERROR, format=_logger_format,
                        handlers=[
                            logging.handlers.RotatingFileHandler(_logger_settings['filename'],
                                                                 maxBytes=_logger_settings['maxBytes'],
                                                                 backupCount=_logger_settings['backupCount']),
                            logging.StreamHandler()])

    dummy = False  # change this to false to work with the real device in the COM specified below.

    if dummy:
        my_class = GenericSerialControllerDummy
    else:
        my_class = GenericSerialController

    with my_class(settings = {'port':'COM4', 'write_termination':'\n'}) as dev:
        dev.initialize()
        time.sleep(1.5)
        print('start')
        
#        for x in range(2):
#            time.sleep(.3)
#            dev.write('2r')
#            time.sleep(.3)
#            dev.write('2g')
        
        print('after start up: {}'.format(dev.read_lines()))
        print('ch1: {}'.format(dev.query('1?')))
        print('ch2: {}'.format(dev.query('2?')))        
        print('idn: {}'.format(dev.idn()))
        print('done')
        


""" Tip:
    Useful featurtes of pyserial are
    
    To list all devices:
    
    comports = serial.tools.list_ports.comports()
    for port, desc, hwid in comports:
        print((port,desc,hwid))
        
    To find a specific device by part of the name

    part_of_name = 'rduino'
    usb_dev = next(serial.tools.list_ports.grep(part_of_name))
    print( usb_dev.description )
    print( usb_dev.hwid )
    print( usb_dev.device )
"""