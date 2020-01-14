"""
    ==================
    Example Experiment
    ==================



    This is an example of an experiment class.
"""
import os
from hyperion.core import logman
# You could also import the logging manager as logging if you don't want to change your line: logger = logging.getLogger(__name_)
# from hyperion.core import logman as logging
# from hyperion import logging    # equivalent to line aboveimport numpy as np
import winsound
from time import sleep
# from hyperion import ur, root_dir
from hyperion.experiment.base_experiment import BaseExperiment
from hyperion.tools.array_tools import *
from datetime import datetime
import sys

class MyExperiment(BaseExperiment):
    """ Example class with basic functions """

    def __init__(self):
        """ initialize the class"""
        super().__init__()                      # Mandatory line
        self.logger = logman.getLogger(__name__)
        self.logger.info('Initializing the ExampleExperiment object.')
        self.logger.critical('test critical')
        self.logger.error('test error')
        self.logger.warning('test warning')
        self.logger.info('test info')
        self.logger.debug('test debug')

        #initialize dictionaries where instances of instruments and gui's can be found
        self.devices = {}
        self.properties = {}
        self.instruments_instances = {}
        self.view_instances = {}
        self.graph_view_instance = {}


    # def __enter__(self):
    #     return self
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #    self.finalize()

    def measurement(self):
        for i in range(1, 10):
            print(i)


    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    def image(self, actiondict, nesting):
        # print('performing action of Name {} with exposuretime {}'.format(actiondict['Name'],actiondict['exposuretime']))
        print(actiondict['Name'], '   indices: ',self._nesting_indices, '  nest parents: ', self._nesting_parents)
        self.save(0)
        # self._data.auto(data, actiondict)
        nesting()       # either takes care of nested actions or checks for pause state
        # data = np.array([[0,1],[2,3]])
        # return data

    def image_modified(self, actiondict, nesting):
        #print('image: ',actiondict['Name'])
        print(actiondict['Name'], '   indices: ',self._nesting_indices, '  nest parents: ', self._nesting_parents)
        self.save(0)
        nesting()

    def spectrum(self, actiondict, nesting):
        # print('spectrum: ',actiondict['Name'])
        print(actiondict['Name'], '   indices: ',self._nesting_indices, '  nest parents: ', self._nesting_parents)
        self.save(0)
        nesting()

    def spectrum_modified(self, actiondict, nesting):
        # print('spectrum: ',actiondict['Name'])
        print(actiondict['Name'], '   indices: ',self._nesting_indices, '  nest parents: ', self._nesting_parents)

        self.save(0)
        nesting()

    def histogram(self, actiondict, nesting):
        # print('histogram: ',actiondict['Name'])
        print(actiondict['Name'], '   indices: ',self._nesting_indices, '  nest parents: ', self._nesting_parents)
        self.save(0)
        #store_data
        nesting()



    def insideXafterY(self, actiondict, nesting):
        print(actiondict['Name'], '   indices: ',self._nesting_indices, '  nest parents: ', self._nesting_parents)
        self.save(0)

    def initialize_example_measurement_A(self, actiondict, nesting):
        self.logger.info('Measurement specific initialization. Could be without GUI')
        # Open datafile with data manager (datman):
        self.datman.open_file('test.nc')
        self.datman.meta(dic={'start_time':str(datetime.now())})
        # # test
        # self.datman.meta(dic=self._saving_meta)

        # self.datman.meta(measurement_name = 'initialize_example_measurement_A')
        # By assigning the finalize method to self._finalize_measurement_method, that method will also be executed when
        # the Stop button is pressed:
        self._finalize_measurement_method = self.finalize_example_measurement_A
        # nesting()

    def finalize_example_measurement_A(self, actiondict, nesting):
        self.logger.info('Measurement specific finalization. Probably be without GUI')
        # Do stuff to finalize your measurement (e.g. switch off laser)

        # Close datafile
        # self.datman.meta(dic={'finish_time': str(datetime.now())})
        self.datman.meta(None, None, False, finish_time=str(datetime.now()))
        self.datman.meta(None, None, False, finish_time=str(datetime.now()))
        # self.datman.meta(dic={'finish_time': str(datetime.now())})
        self.datman.meta(dic={'finish_time':str(datetime.now())})
        self.datman.close()
        nesting()

    def image_with_filter(self, actiondict, nesting):
        self.logger.info('Initialize filters')
        # self.instruments_instances['Filters'].filter_a(action_dict['filter_a'])
        # self.instruments_instances['Filters'].filter_b(action_dict['filter_b'])
        self.logger.info('LED on')
        # self.instruments_instances['LED'].enable = True

        self.logger.info('Set camera exposure')
        # self.instruments_instances['Camera'].set_exposure(actiondict['exposure'])
        self.logger.info('Acquire image')
        # camera_image = self.instruments_instances['Camera'].acquire_image()

        self.logger.info('LED off')
        # self.instruments_instances['LED'].enable = False
        self.logger.info('Clear filters')
        # self.instruments_instances['Filters'].filter_a(False)
        # self.instruments_instances['Filters'].filter_b(False)

        fake_data = np.random.random((20,60))
        # Because this is higher dimensional data, create dimensions:
        self.datman.dim('im_y', fake_data.shape[0])     # add extra axes if they don't exist yet
        self.datman.dim('im_x', fake_data.shape[1])
        self.datman.var(actiondict, fake_data, extra_dims=('im_y', 'im_x') )
        self.datman.meta(actiondict, {'exposuretime': actiondict['exposuretime'], 'filter_a': actiondict['filter_a'], 'filter_b': actiondict['filter_b'] })

    def sweep_atto(self, actiondict, nesting):
        # print('sweep_atto: ',actiondict['Name'])
        # print(actiondict['Name'], '   indices: ', self._nesting_indices, '  nest parents: ', self._nesting_parents)
        arr, unit = array_from_settings_dict(actiondict)
        self.datman.dim_coord(actiondict, arr, meta={'units': str(unit), **actiondict})
        # self.datman.meta(actiondict, actiondict)
        # self.datman.meta(actiondict['Name'], units=str(unit))
        for s in arr:
            print(actiondict['axis'],' : ', s)
            #store_coord()

            nesting()
        if self.break_measurement(): return  # Use this line to check for stop

    def measure_power(self, actiondict, nesting):
        fake_data = np.random.random()
        self.datman.var(actiondict, fake_data, meta=actiondict, unit='mW')
        nesting()

    def fake_spectrum(self, actiondict, nesting):
        fake_wav_nm = np.arange(500, 601, 10)
        fake_data = np.random.random(11)
        self.datman.dim_coord('wav', fake_wav_nm, meta={'unit': 'nm'})
        self.datman.var(actiondict, fake_data, extra_dims=('wav'), meta=actiondict, unit='counts')
        sleep(0.1)  # slow down this dummy measurement
        # nesting()

    def dummy_measurement_for_testing_gui_buttons(self):
        self.logger.info('Starting test measurement')
        self.reset_measurement_flags()
        self.running_status = self._running
        for outer in range(4):
            print('outer', outer)
            for inner in range(4):
                print('    inner', inner)
                sleep(1)
                # if self.stop_measurement(): return      # Use this line to check for stop
                if self.pause_measurement(): return  #: return     # Use this line to check for pause
            if self.break_measurement(): return      # Use this line to check for stop
        self.reset_measurement_flags()
        self.logger.info('Measurement finished')

if __name__ == '__main__':
    # ### To change the logging level:
    # logman.stream_level(logman.WARNING)
    # logman.file_level('INFO')
    # ### To change the stream logging layout:
    # logman.set_stream(compact=0.2, color_scheme='dim') # and other parameters
    # ### To change the logging file:
    # logman.set_file('example_experiment.log')

    test_with_gui = True

    # prepare folders and files:
    this_folder = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(this_folder, 'my_experiment.yml')
    from hyperion import parent_path
    # data_folder = os.path.join(parent_path, 'data')
    # if not os.path.isdir(data_folder):
    #     os.mkdir(data_folder)

    with MyExperiment() as e:
        e.load_config(config_file)
        e.load_instruments()

        if not test_with_gui:
            e.perform_measurement('Example Measurement A')

        else:
            ######### testing gui stuff

            from PyQt5.QtWidgets import QApplication
            from hyperion.view.base_guis import BaseMeasurementGui, ModifyMeasurement

            app = QApplication(sys.argv)
            q = BaseMeasurementGui(e, 'Example Measurement A')
            # q = ModifyMeasurement(e,'Measurement A')
            # q.show()

            ## Introduce corruption in actionlist for testing:
            # del(e.properties['Measurements']['Measurement A'][0]['Name'])
            # del (e.properties['Measurements']['Measurement A'][0])

            # q = BaseMeasurementGui(e, 'Example Measurement A')

            app.exec_()

    print('-----------------   DONE with the experiment   -----------------')

