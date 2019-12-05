# -*- coding: utf-8 -*-
"""
=====================================
Instrument for the laser 08NLD laser
=====================================

This class is the instrument layer to control the Cobolt laser model 08-NLD
It ads the use of units with pint
"""
import logging
from hyperion import ur, Q_
from hyperion.instrument.base_instrument import BaseInstrument


class CoboltLaser(BaseInstrument):
    """ This class is to control the laser.

    """
    def __init__(self, settings):
        """ init of the class"""
        super().__init__(settings)
        self.logger = logging.getLogger(__name__)
        self.logger.info('Class CoboltLaser Instrument created.')

        self.initialize()
        self.DEFAULTS = {}
        #self.load_defaults(defaults)

    def idn(self):
        """
        Ask for the identification

        :return: message with identification from the device
        :rtype: string
        """
        return self.controller.idn

    @property
    def power_sp(self):
        """ Power set point for the laser, when used in constant power mode

        : getter :
        Asks for the current power set point

        :return: The power set point
        :rtype: pint quantity

        : setter :
        Sets the power setpoint

        :param value: power to set
        :type value: pint Quantity

        """
        return self.controller.power_sp

    @power_sp.setter
    def power_sp(self, value):
        self.controller.power_sp = value


if __name__ == '__main__':
    import hyperion
    #hyperion.file_logger.setLevel(logging.INFO)


    with CoboltLaser(settings={'dummy': False,
                               'controller': 'hyperion.controller.cobolt.cobolt08NLD/Cobolt08NLD',
                               'via_serial': 'COM5'}) as d:

        # #### test idn
        #print('Identification = {}.'.format(d.controller.idn()))
        print('power {}'.format(d.power_sp))
        d.power_sp = Q_(115,'mW')
        print('power {}'.format(d.power_sp))
