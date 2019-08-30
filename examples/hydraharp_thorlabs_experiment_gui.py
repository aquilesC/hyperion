import sys
from PyQt5.QtWidgets import QApplication
from hyperion.view.master_gui import App
from examples.example_experiment import ExampleExperiment
from hyperion.instrument.correlator.hydraharp_instrument import HydraInstrument
from hyperion.instrument.motor.thorlabs_motor_instrument import Thorlabsmotor
from hyperion import ur
ureg = ur

def main():
    experiment = ExampleExperiment()
    app = QApplication(sys.argv)
    main_gui = App(experiment)
    sys.exit(app.exec_())

def hydraharp_and_thorlabsmotor_experiment():
    """
    This method is here to have a small example of how in the hyperion way
    multiple instruments can be combined to do a experiment. In this case the instruments
    are the hydraharp and the thorlabsmotor.
    """
    #create instances of the hydraharp and thorlabsmotor
    hydra = HydraInstrument(settings={'devidx':0, 'mode':'Histogram', 'clock':'Internal',
                                   'controller': 'hyperion.controller.picoquant.hydraharp/Hydraharp'})
    motor = Thorlabsmotor()
    #initialize the hydraharp and thorlabsmotor
    #motor.initialize(83815760)
    print(motor.list_devices())

    motor.initialize(83841160)
    hydra.initialize()
    hydra.configurate()
    #doing something that resembles an experiment:
    motor_steps = 5
    for step in range(0, motor_steps):
        #for each step their should be done a scan and the motor should move a certain distance
        #take histogram with the hydraharp
        hydra.set_histogram(leng=65536, res=8.0 * ureg('ps'))
        hist = hydra.make_histogram(tijd=5 * ureg('s'), count_channel=0)
        #move the motor 0.01 micrometer
        motor.move_relative(0.01)
    motor.finalize()
    hydra.finalize()

hydraharp_and_thorlabsmotor_experiment()