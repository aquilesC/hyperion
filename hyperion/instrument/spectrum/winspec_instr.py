# -*- coding: utf-8 -*-
"""
==================
Winspec Instrument
==================

Aron Opheij, TU Delft 2019

IMPORTANT REMARK:
In the current implementation it is not possible to use this instrument in threads.

Tips for finding new functionality:

Once you have an WinspecInstr object named ws, try the following things:
This will list all keywords:
[key for key in ws.controller.params]
There are shorter lists with only experiment (EXP) and spectrograph (SPT) commands:
[key for key in ws.controller.params_exp]       # note that prefix EXP_ is removed
[key for key in ws.controller.params_spt]       # note that prefix SPT_ is removed
To filter in those you could try:
[key for key in ws.controller.params_exp if 'EXPOSURE' in key]
[key for key in ws.controller.params_spt if 'GROOVES' in key]

To request the value for a keyword try:
ws.controller.exp_get('EXPOSURETIME')
ws.controller.exp_get('GRAT_GROOVES')

"""

import logging
from hyperion.instrument.base_instrument import BaseInstrument
from hyperion import ur, Q_
from hyperion.view.general_worker import WorkThread
import time
# import numpy as np      # I'm having issues with numpy on the computer I'm developing, so I disable it temporarily and modified take_spectrum not to depend on it



class WinspecInstr(BaseInstrument):
    """ Winspec Instrument

        :param settings: this includes all the settings needed to connect to the device in question.
        :type settings: dict

    """

    def __init__(self, settings):                   # not specifying a default value for settings is less confusing for novice users
        # don't place the docstring here but above in the class definition
        super().__init__(settings)                  # mandatory line
        self.logger = logging.getLogger(__name__)   # mandatory line
        self.logger.info('Class ExampleInstrument created.')
        self.settings = settings
        self.default_name = 'temp.SPE'

        self._timing_modes = self._remove_unavailable('timing_modes', [0, 'Free Run', 2, 'External Sync'])
        self._shutter_controls = self._remove_unavailable('shutter_controls', [0, 'Normal', 'Disabled Closed', 'Disabled Opened'])
        self._fast_safe = self._remove_unavailable('fast_safe', ['Fast', 'Safe'])
        self._ccd = self._remove_unavailable('CCD', ['Full', 'ROI'])

        self._horz_width_multiple = 1   # This parameter specifies if camera requires horizontal range of certain interval

        self.initialize()   # ! required to do this in the __init__

        # self._is_acquiring = False
        self._is_moving = False

        # !!!!!   THREADING WILL NOT WORK IN THE CURRENT IMPLENTATION
        #         I have some ideas to try, but I'll first finish an operational version without threading

        # self.move_grating_thread = threading.Thread(target = self._move_grating)
        # self.move_grating_thread = WorkThread(self._move_grating)

    def initialize(self):
        """ Starts the connection to the Winspec softare and retrieves parameters. """
        self.logger.info('Opening connection to device.')
        self.controller.initialize()
        # self._gain = self.gain
        self._exposure_time = self.exposure_time
        # self._accums = self.accumulations
        # self._target_temp = self.target_temp
        # # Get grating info:
        self.gratings_grooves = []  # list to hold the grooves/mm for the different gratings
        self.gratings_blaze_name = []  # list to hold the blaze text
        # self.gratings_blaze = []  # list to hold numeric blaze wavelength value
        self.number_of_gratings = self.controller.spt_get('GRATINGSPERTURRET')[0]
        # this seems to be the same value:   self.controller.spt_get('INST_CUR_GRAT_NUM')[0]
        for k in range(self.number_of_gratings):
            self.gratings_grooves.append(self.controller.spt_get('INST_GRAT_GROOVES', k + 1)[0])
            text = self.controller.spt_get('GRAT_USERNAME', k + 1)[0]
            self.gratings_blaze_name.append(text)
            # # try to interpret the blaze wavelength:
            # self.gratings_blaze.append(int(''.join(filter(str.isdigit, text))))

        self.logger.info(
            '{} gratings found. grooves/mm: {}, blaze: {}'.format(self.number_of_gratings, self.gratings_grooves,
                                                                  self.gratings_blaze_name))

    def _move_grating(self):
        """ Low level function to move grating after specifying the new position. """
        self._is_moving = True
        self.controller.spt.Move()
        self._is_moving = False

    def finalize(self):
        """ Mandatory function. Get's called when exiting a 'with' statement."""
        self.logger.info('Closing connection to device.')
        self.controller.finalize()

    def _remove_unavailable(self, settings_key, default_options_list):
        """
        Low level function to remove items from options_list that don't occur in settings_list and replace with their index.
        :param settings_key: the key name in the settings dict
        :param default_options_list: list of default values
        :return: corrected list
        """
        if settings_key in self.settings:
            for index, value in enumerate(default_options_list):
                if value not in self.settings[settings_key]:
                    default_options_list[index] = index
        return default_options_list

    def idn(self):
        """
        Identify command

        :return: Identification string of the device.
        :rtype: string
        """
        self.logger.debug('Ask IDN to device.')
        return self.controller.idn()

    def start_spectrum(self, name=None):
        if name==None:
            name=self.default_name
        self.doc = self.controller.docfile()
        self.controller.exp.Start(self.doc)

    @property
    def is_acquiring(self):
        return self.controller.exp_get('RUNNING')[0]==1

    def nm_axis(self, frame):
        # Retrieve nm axis in cumbersome way. (There must be a better/faster way,  but haven't found it yet)
        wav = []
        cal = self.doc.GetCalibration()
        for index in range(len(frame)):
            wav.append([cal.Lambda(index+1)])
        return wav

    def collect_spectrum(self, wait=True):
        # requires the existence of self.doc
        if wait:
            while self.is_acquiring:
                time.sleep(0.01)
        frame = self.doc.GetFrame(1,self.controller._variant_array)
        # return frame                      # direct tuple of tuples
        # return np.asarray(frame)          # np approach
        return self.nm_axis(frame), [list(col) for col in frame] # convert to nested list

    def take_spectrum(self, name=None):
        self.start_spectrum(name)
        return self.collect_spectrum()



    # Grating Settings:  -----------------------------------------------------------------------------------------

    # ws.controller.spt.Move()

    #        print('GRATINGSPERTURRET: {}'.format(dev.spt_get('GRATINGSPERTURRET')))
    #        print('INST_GRAT_GROOVES 0: {}'.format(dev.spt_get('INST_GRAT_GROOVES',0)))
    #        print('INST_GRAT_GROOVES 1: {}'.format(dev.spt_get('INST_GRAT_GROOVES',1)))
    #        print('INST_GRAT_GROOVES 2: {}'.format(dev.spt_get('INST_GRAT_GROOVES',2)))
    #        print('CUR_GRATING: {}'.format(dev.spt_get('CUR_GRATING')))
    #        print('INST_CUR_GRAT_NUM: {}'.format(dev.spt_get('INST_CUR_GRAT_NUM')))
    #        print('CUR_POSITION: {}'.format(dev.spt_get('CUR_POSITION')))                  <<  in nm
    #        print('ACTIVE_GRAT_POS: {}'.format(dev.spt_get('ACTIVE_GRAT_POS')))            <<  in ???

    @property
    def grating(self):
        return self.controller.spt_get('CUR_GRATING')[0]

    @grating.setter
    def grating(self, number):
        current = self.controller.spt_get('CUR_GRATING')[0]
        if 0 < number <= self.number_of_gratings:
            if number == current:
                self.logger.debug('Grating {} already in place'.format(number))
            else:
                self.controller.spt_set('NEW_GRATING', number)
                self.logger.info('changing grating from {} to {} ...'.format(current, number))
                self.controller.spt.Move()
                self.logger.info('finished changing grating')
        else:
            self.logger.warning('{} is invalid grating number (1-{})'.format(number, self.number_of_gratings))

    @property
    def central_nm(self):
        return self.controller.spt_get('CUR_POSITION')[0]

    @central_nm.setter
    def central_nm(self, nanometers):
        current = self.controller.spt_get('CUR_POSITION')[0]
        if nanometers == current:
            self.logger.debug('Grating already at {}nm'.format(nanometers))
        else:
            self.controller.spt_set('NEW_POSITION', nanometers)
            self.logger.info('moving grating from {} to {} ...'.format(current, nanometers))
            self.controller.spt.Move()
            self.logger.info('finished moving grating')
            # self.move_grating_thread.start()

    # Hardware settings:   ---------------------------------------------------------------------------------------

    @property
    def current_temp(self):
        """
        read-only attribute: Temperature measured by Winspec in degrees Celcius.

        getter: Returns the Temperature measued by Winspec.
        type: float
        """
        return self.controller.exp_get('ACTUAL_TEMP')[0]

    @property
    def temp_locked(self):
        """
        read-only attribute: Temperature locked state measured by Winspec in degrees Celcius.

        getter: Returns True is the Temperature is "locked"
        type: bool
        """
        return self.controller.exp_get('TEMP_STATUS')[0] == 1

    @property
    def target_temp(self):
        """
        attribute: Detector target temperature in degrees Celcius.

        getter: Returns Target Temperature set in Winspec
        setter: Attempts to updates Target Temperature in Winspec if required. Gives warning if failed.
        type: float
        """
        self._target_temp = self.controller.exp_get('TEMPERATURE')[0]
        return self._target_temp

    @target_temp.setter
    def target_temp(self, value):
        # don't place doctring here. add setter info to the getter/property method
        if value != self._target_temp:
            if self.controller.exp_set('TEMPERATURE', value):        # this line also sets the value in winspec
                self.logger.warning('error setting value: {}'.format(value))
            if self.target_temp != value:          # this line also makes sure self._target_temp contains the actual Winspec value
                self.logger.warning('attempted to set target temperature to {}, but Winspec is at {}'.format(self._gain, value))

    @property
    def display_rotate(self):
        """
        attribute: Display Rotate.

        getter: Returns if Display Rotation is set in Winspec.
        setter: Sets Display Rotation in Winspec.
        type: bool
        """
        return self.controller.exp_get('ROTATE')[0] == 1

    @display_rotate.setter
    def display_rotate(self, value):
        self.controller.exp_set('ROTATE', value!=0)     # the value!=0 converts it to a bool

    @property
    def display_reverse(self):
        """
        attribute: Display Reverse (left-right)

        getter: Returns if Display Reverse is set in Winspec.
        setter: Sets Display Reverse in Winspec.
        type: bool
        """
        return self.controller.exp_get('REVERSE')[0] == 1

    @display_reverse.setter
    def display_reverse(self, value):
        self.controller.exp_set('REVERSE', value!=0)     # the value!=0 converts it to a bool

    @property
    def display_flip(self):
        """
        attribute: Display Flip (up-down).

        getter: Returns if Display Flip is set in Winspec.
        setter: Sets Display Flip in Winspec.
        type: bool
        """
        return self.controller.exp_get('FLIP')[0] == 1

    @display_flip.setter
    def display_flip(self, value):
        self.controller.exp_set('FLIP', value!=0)     # the value!=0 converts it to a bool


    # Experiment / ADC settings:   --------------------------------------------

    @property
    def gain(self):
        """
        attribute: ADC Gain value. (Known allowed values: 1, 2)

        getter: Returns Gain set in Winspec
        setter: Attempts to updates Gain setting in Winspec if required. Gives warning if failed.
        type: int
        """
        self._gain = self.controller.exp_get('GAIN')[0]
        return self._gain

    @gain.setter
    def gain(self, value):
        if value != self._gain:
            if self.controller.exp_set('GAIN', value):        # this line also sets the value in winspec
                self.logger.warning('error setting value: {}'.format(value))
            if self.gain != value:          # this line also makes sure self._gain contains the actual Winspec value
                self.logger.warning('attempted to set gain to {}, but Winspec is at {}'.format(value, self._gain))

    # Experiment / Main settings:  --------------------------------------------

    @property
    def ccd(self):
        number = ws.controller.exp_get('USEROI')[0]
        return self._ccd[number]

    @ccd.setter
    def ccd(self, string):
        number = self._setter_string_to_number(string, self._ccd)
        if number>=0:
            self.controller.exp_set('USEROI', number)

    @property
    def spec_mode(self):
        """


        :return: True for Spectroscopy Mode, False for Imaging Mode
        :rtpye: bool
        """
        return ws.controller.exp_get('ROIMODE')[0]==1

    @spec_mode.setter
    def spec_mode(self, value):
        ws.controller.exp_set('ROIMODE', value!=0)

    def getROI(self):
        # return top, bottom, v_group, left, right, h_group
        self._roi = self.controller.exp.GetROI(1)
        r = self._roi.Get()    # returns tuple: (top, left, bottom, right, h_group, v_group)
        return [r[0], r[2], r[5], r[1], r[3], r[4]]

    def setROI(self, top='full_im', bottom=None, v_group=None, left=1, right=None, h_group=1):
        """
        Note for the new camera (the 1024x1024 one) the  horizontal range needs to be a multiple of 4 pixels.
        If the users input fails this criterium, this method will expand the range.
        Also the v_group and h_group, need to fit in the specified range. If the input fails, a suitable value will be used. And the user will be warned.
        :param top: Top-pixel number (inclusive) (integer starting at 1). Alternatively 'full_im' (=DEFAULT) of 'full_spec' can be use.
        :param bottom: Bottom-pixel number (integer). DEFAULT value is bottom of chip
        :param v_group: Vertical bin-size in number of pixels (integer). None sums from 'top' to 'bottom'. DEFAULT: None
        :param left: Left-pixel number (inclusive) (integer starting from 1). DEFAULT is 1
        :param right: Right-pixel number (integer). DEFAULT is rightmost pixel
        :param h_group: Horizontal binning (integer), DEFAULT is 1
        :return:

        Examples:
        setROI('full_im')   returns the full CCD
        setROI('full_spec') returns the full CCD, summed vertically to result in 1D array
        setROI(51)          sums from pixel 51 to the bottom
        setROI(51, 70)      sums vertically from pixel 51 to 70
        setROI(51, 70, 20)  sums vertically from pixel 51 to 70
        setROI(41, 60, 5)   result in 4 bins of 5 pixles
        setROI(41, 60, 1)   no binning, result will be 20 pixels high
        setROI(41, 60, None, 101, 601)      modify horizontal range
        setROI(41, 60, None, 101, 601, 10)  apply horizontal binning of 10 pixels (result will be 50 datapoints wide)
        """

        if bottom is None:
            bottom = self.controller.ydim

        if right is None:
            right = self.controller.xdim

        if type(top) is str:
            top = 1
            if top=='full_im':
                v_group = 1
            elif top !='full_spec':
                self.logger.warning('unknown command {}, using full_spec ')

        # if v_group is not specified assume summing vertically from top to bottom:
        if v_group is None:
            v_group = bottom-(top-1)

        # Some basic range corrections:
        # revert top/bottom and left/right if they're inverted
        if bottom<top:
            temp = top
            top = bottom
            bottom = temp
        if right < left:
            temp = left
            left = right
            right = temp
        # apply basic limits of the CCD
        if top < 1: top = 1
        if left < 1: left = 1
        if bottom > self.controller.ydim: bottom = self.controller.ydim
        if right > self.controller.xdim: right = self.controller.xdim

        # if bottom < top:
        #     if top < self.controller.ydim-1:
        #         bottom = top
        #     else:
        #         top = bottom
        # if right < left:
        #     if left < self.controller.xdim-1:
        #         right = left + 1
        #     else:
        #         left = right - 1
        # if not 0 < top <= bottom: self.logger.error('top value invalid')
        # if not top <= bottom <= self.controller.ydim: self.logger.error('bottom value invalid')
        # if not 0 < left <= right: self.logger.error('left value invalid')
        # if not left <= right <= self.controller.xdim: self.logger.error('right value invalid')

        pix = right - (left - 1)
        if self._horz_width_multiple > 1:
            # note: I've generalized this from 4 to self._horz_width_multiple
            # Check if horizontal range is multiple of 4 pixels. Expand if required.
            # This is rquired for the new spectrometer (the one with 1024x1024 pixels)
            if pix%self._horz_width_multiple:
                ad = self._horz_width_multiple-pix+self._horz_width_multiple*int(pix/self._horz_width_multiple) # number of pixels to add (1,2,3)
                while ad:
                    if ad and right < self.controller.xdim:
                        right += 1
                        ad -= 1
                    if ad and left>1:
                        left -= 1
                        ad -= 1
            self.logger.warning('horizontal range is not muliple of {}: expanded to [{}-{}]'.format(self._horz_width_multiple, left, right))
            pix = right - (left - 1)

        # if necessary correct h_group to fit horizontal range:
        new_h = h_group
        if pix%h_group:
            new_h = h_group-((h_group-1)%self._horz_width_multiple)+(self._horz_width_multiple-1)   # ceil to nearest multiple of self._horz_width_multiple
            while pix%new_h:        # note: this loop should end at the latest when new_h == 1
                new_h -= 1

        if new_h != h_group:
            self.logger.warning('h_group {} does not fit in horizontal range of [{}-{}]: changing to: {}'.format(h_group, left, right, h_new))
            h_group = h_new

        pix = bottom - (top-1)
        if pix%v_group:
            new_v = v_group+1
            while pix%new_v:        # note: this loop should end at the latest when new_v == 1
                new_v -= 1

        if new_v != v_group:
            self.logger.warning('v_group {} does not fit in verical range of [{}-{}]: changing to: {}'.format(v_group, top, bottom, v_new))
            v_group = v_new

        # set the new ROI:
        self._roi = self.controller.exp.GetROI(1)                       # get ROI object
        self._roi.Set(top, left, bottom, right, h_group, v_group)       # put in the new values
        self.controller.exp.ClearROIs()                                 # clear ROIs in WinsSpec
        self.controller.exp.SetROI(self._roi)                           # set the ROI object in WinSpec
        self.ccd = 'ROI'                                                # switch from Full Chip to Region Of Interest mode

        # I'm not sure if I need to do something with ROIMODE (0= Imaging Mode,   1= Spectroscopy Mode)

    @property
    def accumulations(self):
        """
        attribute: Number of Accumulations.

        getter: Returns the Number of Accumulations set in Winspec
        setter: Attempts to updates the Number of Accumulations in Winspec if required. Gives warning if failed.
        type: int
        """
        self._accums = self.controller.exp_get('ACCUMS')[0]
        return self._accums

    @accumulations.setter
    def accumulations(self, value):
        if value != self._accums:
            if self.controller.exp_set('ACCUMS', value):        # this line also sets the value in winspec
                self.logger.warning('error setting value: {}'.format(value))
            if self.accumulations != value:          # this line also makes sure self._accums contains the actual Winspec value
                self.logger.warning('attempted to set accumulations to {}, but Winspec is at {}'.format(self._accums, value))

    @property
    def exposure_time(self):
        """
        attribute: Exposure Time.

        getter: Returns the Exposure Time set in Winspec
        setter: Attempts to updates the Exposure Time in Winspec if required. Gives warning if failed.
        type: Pint Quantity of unit time
        """

        winspec_exposure_units = [ur('us'), ur('ms'), ur('s'), ur('min')]
        exp_pint_unit = winspec_exposure_units[ self.controller.exp_get('EXPOSURETIME_UNITS')[0] -1 ]
        exp_value = self.controller.exp_get('EXPOSURETIME')[0]
        self._exposure_time = exp_value * exp_pint_unit
        return self._exposure_time

    @exposure_time.setter
    def exposure_time(self, value):
        if type(value) is not type(Q_('s')):
            self.logger.error('exposure_time should be Pint quantity')
        if value.dimensionality != Q_('s').dimensionality:
            self.logger.error('exposure_time should be Pint quantity with unit of time')
        else:
            if value.m_as('us') < 1:                                                    # remove this if necessary
                self.logger.warning('WinSpec will not accept exposuretime smaller than 1 us')

            if value != self._exposure_time or value.m != self._exposure_time.m:
                if value.units == 'microsecond':
                    exp_unit = 1
                    exp_value = value.m_as('microsecond')
                elif value.units == 'millisecond':
                    exp_unit = 2
                    exp_value = value.m_as('millisecond')
                elif value.units == 'second':
                    exp_unit = 3
                    exp_value = value.m_as('second')
                elif value.units == 'minute':
                    exp_unit = 4
                    exp_value = value.m_as('minute')
                elif value > 10*ur('minute'):
                    exp_unit= 4
                    exp_value = value.m_as('minute')
                elif value < 1*ur('microsecond'):
                    exp_unit = 1
                    exp_value = value.m_as('microsecond')
                else:
                    exp_unit = 3
                    exp_value = value.m_as('second')

                self.controller.exp_set('EXPOSURETIME_UNITS',exp_unit)
                self.controller.exp_set('EXPOSURETIME',exp_value)

        if self.exposure_time != value:     # this line also makes sure self._exposuretime gets the real Winspec value
            self.logger.warning('attempted to set exposure time to {}, but Winspec is at {}'.format(value, self._exposure_time))

    # Experiment / Data Correction settings: ----------------------------------

    @property
    def bg_subtract(self):
        return self.controller.exp_get('BBACKSUBTRACT')[0] == 1     # turn it into bool

    @bg_subtract.setter
    def bg_subtract(self, value):
        self.controller.exp_set('BBACKSUBTRACT',value!=0)       # !=0  forces it to be bool

    @property
    def bg_file(self):
        return self.controller.exp_get('DARKNAME')[0]

    @bg_file.setter
    def bg_file(self, filename):
        # NOTE, this does not check if the file exists
        return self.controller.exp_set('DARKNAME', filename)

# Could repeat this for flatfield and blemish
#        FLATFLDNAME
#        BDOFLATFIELD
#        BLEMISHFILENAME
#        DOBLEMISH


# BGTYPE ??

    # Experiment / Timing settings: ----------------------------------

    @property
    def delay_time_s(self):
        # Experiment / Timing / Delay Time in seconds
        return self.controller.exp_get('DELAY_TIME')[0]

    @delay_time_s.setter
    def delay_time_s(self, seconds):
        # Experiment / Timing / Delay Time in seconds
        self.controller.exp_set('DELAY_TIME', seconds)

    # helper function:
    def _setter_string_to_number(self, string, available_list):
        # also allows for int and checks if it is in the available list as a string
        if type(string)==int:
            if type(available_list[string])!=int:
                return string
        elif string in available_list:
            return available_list.index(string)
        self.logger.warning("{} Is not a valid option in {}".format(string, available_list))
        return -1  # use this to indicate invalid

    @property
    def timing_mode(self):
        number = self.controller.exp_get('TIMING_MODE')[0]
        return self._timing_modes[number]

    @timing_mode.setter
    def timing_mode(self, string):
        number = self._setter_string_to_number(string, self._timing_modes)
        if number>=0:
            self.controller.exp_set('TIMING_MODE', number)

    @property
    def shutter_control(self):
        number = self.controller.exp_get('SHUTTER_CONTROL')[0]
        return self._shutter_controls[number]

    @shutter_control.setter
    def shutter_control(self, string):
        number = self._setter_string_to_number(string, self._shutter_controls)
        if number>=0:
            self.controller.exp_set('SHUTTER_CONTROL', number)

    @property
    def fast_safe(self):
        number = self.controller.exp_get('SYNC_ASYNC')[0]
        return self._fast_safe[number]

    @fast_safe.setter
    def fast_safe(self, string):
        number = self._setter_string_to_number(string, self._fast_safe)
        if number>=0:
            self.controller.exp_set('SYNC_ASYNC', number)

    # Could add
    #edge_trigger



if __name__ == "__main__":
    from hyperion import _logger_format
#   from hyperion import Q_
    import hyperion

#    hyperion.set_logfile('winspec_instr.log')
    hyperion.file_logger.setLevel( logging.WARNING )
    hyperion.stream_logger.setLevel( logging.DEBUG )




    ws = WinspecInstr(settings = {'port': 'None', 'dummy' : False,
                                   'controller': 'hyperion.controller.princeton.winspec_contr/WinspecContr', 'shutter_controls':['Disabled Closed','Disabled Opened']})

    if False:

        print('\nHardware Display settings:')
        print('display_rotate = ', ws.display_rotate)
        print('display_reverse = ', ws.display_reverse)
        print('display_flip = ', ws.display_flip)

        print('\nHardware Temperature settings:')
        print('target_temp = ', ws.target_temp)
        print('current_temp = ', ws.current_temp, '  (read-only property)')
        print('temp_locked = ', ws.temp_locked, '  (read-only property)')

        print('\nExperiment Settings:')
        print('ADC              gain = ', ws.gain)
        print('Timing           timing_mode = ', ws.timing_mode)
        print('Timing           shutter_control = ', ws.shutter_control)
        print('Timing           fast_safe = ', ws.fast_safe)
        print('Timing           delay_time_s = ', ws.delay_time_s)
        ws.bg_subtract = False
        print('Data Corrections bg_subtract = ', ws.bg_subtract)
        print('Data Corrections bg_file = ', ws.bg_file)
        ws.exposure_time = Q_('3s')
        print('Main             exposure_time = ', ws.exposure_time)
        ws.ccd = 'ROI'
        print('Main             ccd = ', ws.ccd)
        print('Main             accumulations = ', ws.accumulations)
        print('ROI              spec_mode = ', ws.spec_mode)

        print('\nGrating Settings:')
        print(ws.number_of_gratings, ' gratings found')
        for k in range(ws.number_of_gratings):
            print(k+1, ':  ', ws.gratings_grooves[k], 'gr/mm  ',  ws.gratings_blaze_name[k])

        print('current grating = ', ws.grating)
        print('Switching grating ...')
        if ws.grating == 2:
            ws.grating = 1
        elif ws.grating == 1:
            ws.grating = 2

        print('central_nm = ', ws.central_nm)
        print('Changing grating central nm ...')
        if ws.central_nm < 450:
            ws.central = 500
        if ws.central_nm > 450:
            ws.central = 400

    print('Taking spectrum ...')
    nm, counts = ws.take_spectrum()
    print(nm,counts)

    # import matplotlib.pyplot as plt
    # plt.plot

    ws.central_wav = 300
    

