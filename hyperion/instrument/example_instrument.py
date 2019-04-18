"""
================
Dummy Instrument
================

This is a dummy device, simulated for developing and testing the code

"""
import logging
from hyperion.instrument.base_instrument import BaseInstrument
from hyperion import ur
import lantz.drivers.stanford.sr830 as LockIn

class ExampleInstrument(BaseInstrument):
    """ Example instrument. it is a fake instrument

    """
    def __init__(self, settings = {'port':'COM10', 'dummy': True,
                                   'controller': 'hyperion.controller.example_controller/ExampleController'}):
        """ init of the class"""
        self.logger = logging.getLogger(__name__)
        self.logger.info('Class ExampleInstrument created.')

        self.controller = None
        self.controller_class = None
        self._port = settings['port']
        self.dummy = settings['dummy']
        self.logger.debug('Creating the instance of the controller')
        self.controller_class = self.load_controller(settings['controller'])
        self.controller = self.controller_class(self._port, dummy=self.dummy)

    def initialize(self):
        """ Starts the connection to the device"
        """
        self.logger.info('Opening connection to device.')
        self.controller.initialize()

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

    with ExampleInstrument() as dev:
        dev.initialize()
        print(dev.amplitude)
        v = 2 * ur('volts')
        dev.amplitude = v
        print(dev.amplitude)
        dev.amplitude = v
        print(dev.amplitude)


