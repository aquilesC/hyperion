"""
================
Thorlabs motors Instrument
================

Connects for now to the TDC001 controller.

Example:
    Shows the list of available devices conects to motor x and initialize (without homing) it and moves it by 10 micro meter. 

```python
    >>> from hyperion.intstrument.motors.Thorlabsmotor_instrument import Thorlabsmotor
	>>> checkdevices = Thorlabsmotor()
	>>> checkdevices.list_available_device()
	>>> [(31,81818251)]
    >>> motorx = Thorlabsmotor()
	>>> motorx.initialize(81818251)
    >>> motorx.move_home(True)
    >>> motorx.move_relative_um(10)
```


"""
import logging
from hyperion.instrument.base_instrument import BaseInstrument
from hyperion.controller.thorlabs.TDC001 import TDC001
from hyperion import ur


class Thorlabsmotor(BaseInstrument):
    """ Thorlabsmotor instrument

    """
    
    def __init__(self, settings = {'dummy': True,'port':'COM10',
                               'controller': 'hyperion.controller.thorlabs.TDC001/TDC001'}):
        """ init of the class"""
        self.logger = logging.getLogger(__name__)
        self.logger.info('Class ExampleInstrument created.')
    
        self._port = settings['port']    
        self.dummy = settings['dummy']
        self.logger.debug('Creating the instance of the controller')
        self.controller_class = self.load_controller(settings['controller'])
        self.controller = self.controller_class()

#    def __init__(self, settings = {}):
#        """ init of the class"""
#        self.logger = logging.getLogger(__name__)
#        self.logger.info('Class ExampleInstrument created.')
#        self.controller = TDC001()


    def list_devices(self):
        """ List all available devices. Returns serial numbers"""
        
        aptmotorlist=self.controller.list_available_devices()
        print(str(len(aptmotorlist)) + ' motor boxes found:')
        print(aptmotorlist)
    
    def initialize(self, port, homing=0):
        """ Starts the connection to the device in port

        :param port: Serial number to connect to
        :type port: string
        
        :param homing: if homing is not 0 than the motor first homes to its zero position so 
        hardware and software are connected. Afterwards it goes to the position defined by homing. This can be saved
        position from before.
        :type homing: number
        """
        self.logger.info('Opening connection to device.')
        motor=self.controller.initialize(port)
        if homing != 0:
            self.controller.move_home(True)
            self.controller.move_to(homing)
        return motor
    
    def move_relative_um(self,distance):
        """ Moves the motor to a relative position
        
        :param distance: relative distance in micro meter
        :type homing: number
        """
        distance_mm=distance/1000
        self.controller.move_by(distance_mm)
        

    def finalize(self):
        """ this is to close connection to the device."""
        self.logger.info('Closing connection to device.')
        self.controller.finalize()

    def idn(self):
        """ Identify command

        :return: identification for the device
        :rtype: string

        """
        self.logger.debug('Ask IDN to device.')
        return self.controller.idn()


    @property
    def amplitude(self):
        """ Gets the amplitude value
        :return: voltage amplitude value
        :rtype: pint quantity
        """
        self.logger.debug('Getting the amplitude.')
        return self.controller.amplitude * ur('volts')

    @amplitude.setter
    def amplitude(self, value):
        """ This method is to set the amplitude
        :param value: voltage value to set for the amplitude
        :type value: pint quantity
        """
        self.controller.amplitude = value.m_as('volts')


if __name__ == "__main__":
    from hyperion import _logger_format
    logging.basicConfig(level=logging.DEBUG, format=_logger_format,
        handlers=[logging.handlers.RotatingFileHandler("logger.log", maxBytes=(1048576*5), backupCount=7),
                  logging.StreamHandler()])

    with Thorlabsmotor() as dev:
        dev.list_devices()
#        dev.initialize('COM10')
#        print(dev.amplitude)
#        v = 2 * ur('volts')
#        dev.amplitude = v
#        print(dev.amplitude)
#        dev.amplitude = v
#        print(dev.amplitude)


