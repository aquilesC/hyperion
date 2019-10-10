# -*- coding: utf-8 -*-
"""
================
Santec controller
================

This is a fake device, simulated for developing and testing the code.
It can be used as an example to build your own controller for your device.


"""
import logging
import serial
from hyperion.controller.base_controller import BaseController

class SantecController(BaseController):
    """ Controller for the Santec TSL-710 laser"""
    
    DEFAULTS = {'COMMON': {'encoding': 'UTF-8',
                            'read_termination': '\r\n',
                            'write_termination': '\r\n',
                         },
                'ASRL': {'baud_rate': 19200,
                         'bytesize': 8,
                         #'parity': constants.Parity.none,
                         #'stop_bits': constants.StopBits.one,
                         }}
    
    def __init__(self):
        """ Init of the class. """
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.logger.info('Class SantecController created.')
        self._amplitude = []



    def initialize(self, port,speed=19200):
        """ Starts the connection to the device in port

        :param port: port name to connect to
        :type port: string
        """
        self.logger.info('Opening connection to device.')
        try:
            self.ser=serial.Serial(port, speed, timeout=.1)
        except IOError: # if port is already opened, close it and open it again and print message
            self.ser.close()
            self.ser.open()
            self.logger.warning("port was already open, was closed and opened again!")
        
        self._is_initialized = True     # this is to prevent you to close the device connection if you
                                        # have not initialized it inside a with statement
                                
                                        
    def finalize(self):
        """ This method closes the connection to the device.
        It is ran automatically if you use a with block

        """
        self.logger.info('Closing connection to device.')
        self.ser.close()
        
    def write(self,msg):
        """ Write a message to the device

        :param msg: message to send to the device
        :type msg: string
        """
        
        self.ser.write((msg+'\r').encode('UTF-8'))
        
    def read(self):
        """ Read a message from the device

        """
        
        ans=self.ser.readline().decode('UTF-8')
        return ans
    
    def query(self,msg):
        """ Query the device. Sends a message and reads the reply

        :param msg: message to send to the device
        :type msg: string
        """
        
        self.write(msg)
        ans=self.read()
        
        return ans
    
    def idn(self):
        """ Ask the device for identification
        
        :return: ID of the device

        """
        
        self.logger.info('Trying to identify device')
        ans=self.query('*IDN?')
        self.logger.info('Device identified as %s'%ans)
        return ans
    
    
    def get_wavelength(self):
        """ Get the current wavelength in nm
        
        :return: Wavelength in nm
        """
        
        self.logger.info('Getting current wavelength')
        return self.query('WA')


    def set_wavelength(self, value):
        
        """ Set the wavelength in nm

        :param value: Wavelength in nm
        :type value float
        """
        
        if (1480.0>value or value>1640.0):
            self.logger.warning('Value outside of the range of the laser. Please enter a number between 1480 and 1640')
        self.logger.info('Changing wavelength to %.4f'%value)
        self.query('WA%.4f' % value)
        

    def get_frequency(self):
        """ Get the frequency in THz
        
        :return: Frequency in THz

        """
        
        self.logger.info('Getting current frequency')
        return self.query('FQ')


    def set_frequency(self, value):
        """ Set the frequency in THz

        :param value: Frequency in Thz
        :type value float
        """
        
        self.logger.info('Changing frequency to {}'.format(value))
        self.query('FQ%.5f' % value)
        
    def get_powermW(self):
        """
        gets the optical power in mW
        
        :return: Optical power in mW
        """
        self.logger.info('Getting current power (mW)')
        return self.query('LP')
    
    
    def set_powermW(self, value):
        """ Set the power in mW

        :param value: Power in mW
        :type value float
        """
        
        self.logger.info('Changing power to {}'.format(value))
        self.query('LP%.2f' % value)
        
    #@Feat(limits=(-20, 10, 0.01))
    def get_powerdB(self):
        """
        get the optical power in dBm
        :return: Optical power in dBm
        """
        self.logger.info('Getting current power (dBm)')
        return self.query('OP')

    #@powerdB.setter
    def set_powerdB(self, value):
        """ Set the optical power in dBm

        :param value: Optical power in dBm
        :type value float
        """
        
        self.logger.info('Changing power to {}'.format(value))
        self.query('OP%.2f' % value)
        
    def get_start_wavelength(self):
        """ Get the starting wavelength in nm

        :return: Starting wavelength in nm
        """
        
        self.logger.info('Getting starting wavelength')
        return self.query('SF')

    def set_start_wavelength(self, value):
        """ Set the starting wavelength in nm

        :param value: Wavelength in nm
        :type value float
        """
        
        if (1480.0>value or value>1640.0):
            self.logger.warning('Value outside of the range of the laser. Please enter a number between 1480 and 1640')
        self.logger.info('Changing starting wavelength to %.4f'%value)
        self.query('SS%.4f' % value)
        
        
    def get_stop_wavelength(self):
        """ Get the stopping wavelength in nm

        :return: Stopping wavelength in nm
        """
        
        self.logger.info('Getting stopping wavelength')
        return self.query('SE')

    def set_stop_wavelength(self, value):
        """ Set the Stopping wavelength in nm

        :param value: Wavelength in nm
        :type value float
        """
        
        if (1480.0>value or value>1640.0):
            self.logger.warning('Value outside of the range of the laser. Please enter a number between 1480 and 1640')
        self.logger.info('Changing stopping wavelength to %.4f'%value)
        self.query('SE%.4f' % value)
        
    def lo(self):
        """
        Sets ON the LD current
        
        """
        self.query('LO')


    def lf(self):
        """
        Sets OFF the LD current.

        """
        self.query('LF')


    def get_fine_tune(self):
        return self.query('FT')

    def set_fine_tune(self, value):
        self.query('FT%.2f' % value)

    def fine_tune_stop(self):
        """
        Stops fine-tuning mode and starts closed-loop wavelength controlling.
        :return:
        """
        self.query('FTF')


    def auto_power_on(self):
        """Sets the power control to auto."""
        self.query('AF')
    def manual_power(self):
        self.query('AO')

    def get_attenuator(self):
        return self.query('AT')

    def set_attenuator(self, value):
        self.query('AT%.2f' % value)




    def get_stop_frequency(self):
        """ Get the stopping frequency for the sweep in THz

        :return: Stopping frequency in THz
        """
        return self.query('FF')

    def set_stop_frequency(self, value):
        """ Set the stopping frequency for the sweep in THz

        :param value: Stopping frequency in THz
        :param type: float
        """
        
        self.query('FF%.5f' % value)

    def get_wait_time(self):
        """Get the wait time between each sweep in continuous sweep operation.
        
        :return: Waiting time in ?
        """
        return self.query('SA')

    def set_wait_time(self, value):
        """Set the wait time between each sweep in continuous sweep operation.
        
        :param value: Waiting time in ?
        :param type: float
        """
        
        self.query('SA%.1f' % value)

    def get_step_time(self):
        """Amount of time spent during each step in step sweep operation.
        
        :return: Step time in ?
        """
        return self.query('SB')


    def set_step_time(self, value):
        """Set the time in each step in step sweep operation.
        
        :param value: Step time in ?
        :param type: float
        """
        
        self.query('SB%.1f' % value)

    def get_wavelength_sweeps(self):
        """Gets the number of wavelengths sweeps.
        
        :return: Amount of sweeps to be executed
        """
        return self.query('SZ')

    def set_wavelength_sweeps(self, value):
        """Set the number of wavelengths sweeps.
        
        :param value: Number of sweeps to be executed
        :param type: int
        """
        
        self.query('SZ%i' % value)

    def get_wavelength_speed(self):
        """Get speed for continuous sweeps (in nm/s)
        
        :return: Sweep speed in nm/s
        """
        return self.query('SN')

    def set_wavelength_speed(self, value):
        """Set the speed for continuous wavelengths sweeps.
        
        :param value: Speed of the sweep in nm/s
        :param type: float
        """
        
        self.query('SN%.1f' % value)

    def get_step_wavelength(self):
        """Get step interval of step sweeps. 
        
        :return: Step size in nm
        """
        return self.query('WW')

    def set_step_wavelength(self, value):
        """Set the stepsize for step wavelengths sweeps.
        
        :param value: Step of the sweep in nm
        :param type: float
        """
        
        self.query('WW%.4f' % value)
        
        
    def get_step_frequency(self):
        """Get step interval of step sweeps. 
        
        :return: Step size in THz
        """
        
        return self.query('WF')

    def set_step_frequency(self, value):
        """Set the stepsize for step wavelengths sweeps.
        
        :param value: Step of the sweep in THz
        :param type: float
        """
        
        self.query('WF%.5f' % value)


    def get_sweep_mode(self):
        """ Get the sweep mode
        :return: Current sweep mode set
        
        """
        return self.query('SM')


    def set_sweep_mode(self, value):
        """Set the sweep mode
        :param value: Mode ?
        :param type: string
        """ 
        
        self.query('SM%s' % value)


    def execute_sweep(self):
        """
        Executes sweeps or puts the device in trigger signal standby.
        The number of sweeps is defined by the method wavelength_sweeps.
        """
        self.query('SG')

    
    def pause_sweep(self):
        """Pauses the wavelength sweeps
        """
        
        self.query('SP')

    
    def stop_sweep(self):
        """Stops the sweeps
        """
        
        self.query('SQ')

    
    def resume_sweep(self):
        """Resumes the sweeps
        """
        self.query('SR')

    
    def software_trigger(self):
        self.query('ST')

    
    def number_sweeps(self):
        return self.query('SX')

    
    def sweep_condition(self):
        return int(self.query('SK'))


    def get_timing_trigger(self):
        return self.query('TM')

    def set_timing_trigger(self, value):
        self.query('TM%i' % value)

    def get_interval_trigger(self):
        """Sets the interval of the trigger signal output in nm."""
        return self.query('TW')

    def set_interval_trigger(self, value):
        self.query('TW%.4f' % value)
        


            

    def get_start_frequency(self):
        """ Get the starting frequency for sweeps in THz

        :return: Starting frequency in THz
        """
        return self.query('SS')
    
    def set_start_frequency(self, value):
        """ Set the starting wavelength in nm

        :param value: Frequency in THz
        :type value float
        """
        self.query('SS%.5f' % value)
        
    def get_coherent_control(self):
       return self.coherent

    def set_coherent_control(self, value):
       if value:
           self.coherent_control_on()
           print('Coherent ON')
       else:
           self.coherent_control_off
           print('Coherent off')
       self.coherent = value

    def get_LD_current(self):
       return self.LD

    def set_LD_current(self, value):
       if value:
           self.lo()
       else:
           self.lf()
       self.LD = value

   
    def get_auto_power(self):
        return self.auto_power_status


    def set_auto_power(self, value):
        if value:
            self.auto_power_on()
        else:
            self.manual_power()
        self.auto_power_status = value

    def get_trigger(self):
        return self.trigger_status


    def set_trigger(self, value):
        if value:
            self.enable_trigger()
        else:
            self.disable_trigger()
        self.trigger_status = value

    
    def get_shutter(self):
        """Get shutter status.
        
        :return: Shutter status. True=open, False=closed.
        """
        self.logger.info('Getting shutter status.')
        return self.shutter_status

    
    def set_shutter(self, value):
        """Set shutter status
        
        :param value: Shutter status. True=open, False=closed.
        :param type: Bool
        """
        if value:
            self.open_shutter()
        else:
            self.close_shutter()
        self.shutter_status = value

    
    def close_shutter(self):
        """Close the laser shutter
        """
        
        self.query('SC')

    
    def open_shutter(self):
        """Open the laser shutter
        """
        self.query('SO')

    
    def enable_trigger(self):
        self.query('TRE')

    
    def disable_trigger(self):
        self.query('TRD')


    
    def coherent_control_on(self):
        self.query('CO')


    def coherent_control_off(self):
        self.query('CF')

class SantecControllerDummy(SantecController):
    pass

if __name__ == "__main__":
    from hyperion import _logger_format
    logging.basicConfig(level=logging.DEBUG, format=_logger_format,
        handlers=[logging.handlers.RotatingFileHandler("logger.log", maxBytes=(1048576*5), backupCount=7),
                  logging.StreamHandler()])

    with SantecController() as dev:
        dev.initialize('COM11')
        dev.idn()
        #dev.get_shutter()
        print('Current wavelength is {}'.format(dev.get_start_wavelength()))
        #dev.set_wavelength(1400)
        #dev.get_power()
        

