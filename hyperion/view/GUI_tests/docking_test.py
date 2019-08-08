import importlib
import random

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDockWidget, QListWidget, QTextEdit, QPushButton, \
    QGraphicsView, QAction, QLineEdit, QScrollArea, QVBoxLayout, QHBoxLayout, QGridLayout
import pyqtgraph as pg
from examples.example_experiment import ExampleExperiment

class App(QMainWindow):

    def __init__(self, experiment):
        super().__init__()
        self.title = 'PyQt5 simple window'
        self.left = 40
        self.top = 40
        self.width = 800
        self.height = 500
        self.button_pressed = False
        self.experiment = experiment

        self.setWindowTitle("Dock demo")

        self.initUI()
    def set_menu_bar(self):
        mainMenu = self.menuBar()
        self.fileMenu = mainMenu.addMenu('File')
        self.fileMenu.addAction("Exit NOW", self.close)
        self.dock_widget_1_file_item = mainMenu.addMenu('float dock widget 1')
        self.dock_widget_1_file_item.addAction("widget 1 loose", self.make_widget_1_loose)
        self.dock_widget_2_file_item = mainMenu.addMenu('dock_widget_2')
        self.dock_widget_2_file_item.addAction("widget 2 loose", self.make_widget_2_loose)

        self.draw_something = mainMenu.addMenu('draw')
        self.draw_something.addAction("Draw", self.draw_random_graph)

        self.toolsMenu = mainMenu.addMenu('Tools')
        self.toolsMenu.addAction("Let widget 1 disappear", self.get_status_open_or_closed)
        self.toolsMenu.addAction("Make widget", self.create_single_qdockwidget)

        self.helpMenu = mainMenu.addMenu('Help')

    def make_widget_1_loose(self):
        self.dock_widget_1.setFloating(True)
    def make_widget_2_loose(self):
        self.dock_widget_2.setFloating(True)
    def get_status_open_or_closed(self):
        self.dock_widget_1.setVisible(not self.dock_widget_1.isVisible())
    def create_single_qdockwidget(self):
        #in this method the goal is to create a blank QDockwidget and set in the main_gui
        if self.button_pressed == False:
            self.random_widget = QDockWidget("some_widget",self)

            self.random_widget.setFloating(False)

            self.random_widget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
            self.random_widget.setAllowedAreas(Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)

            self.addDockWidget(Qt.TopDockWidgetArea, self.random_widget)

            self.button_pressed = True

    def draw_random_graph(self):
        self.ydata = [random.random() for i in range(25)]
        self.xdata = [random.random() for i in range(25)]
        self.main_plot.plot(self.xdata, self.ydata, clear=True)

    def set_dock_widget_1(self):
        """
        how to add Qobjects to a dockable goes as follows.
        First you make a Qwidget where the content will be placed in. Call this things something with content in the name
        Then define the Qobjects you want to make
        Finally, you choose a layout((maybe absolute positioning is possible,
        haven't seen it in examples so it is not implemented in this code)QVBoxLayout, QHBoxLayout and QGridLayout)
        then you add the layout to the content widget and lastly you set the beginning Qwhatever as the widget of the dockwidget.
        """

        self.dock_widget_1 = QDockWidget("dock_widget_1", self)
        """
        self.dock_widget_1_content = QWidget()
        self.dock_widget_1_content.setObjectName('de content voor de dock_widget')

        self.listWidget_right = QListWidget()
        self.listWidget_right.addItems(["item 1", "item 2", "item 3"])

        self.some_button = QPushButton('test', self)
        self.some_button.setToolTip('You are hovering over the button, \n what do you expect?')
        self.some_button.clicked.connect(self.on_click_submit)

        self.textbox = QLineEdit(self)
        self.textbox.setText('this is a test')

        self.vbox_1_scroll_area = QVBoxLayout()
        self.vbox_1_scroll_area.addWidget(self.some_button)
        self.vbox_1_scroll_area.addWidget(self.textbox)
        self.vbox_1_scroll_area.addWidget(self.listWidget_right)
        self.dock_widget_1_content.setLayout(self.vbox_1_scroll_area)
        self.dock_widget_1.setWidget(self.dock_widget_1_content)
        """
        self.dock_widget_1.setWidget(self.experiment.view_instances["ExampleInstrument"])


        self.dock_widget_1.setFloating(False)
        self.dock_widget_1.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.dock_widget_1.setAllowedAreas(Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)

        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget_1)
    def set_dock_widget_2(self):
        self.dock_widget_2 = QDockWidget("dock_widget_2", self)
        self.dock_widget_2_content = QWidget()
        self.dock_widget_2_content.setObjectName('de content voor de dock_widget')

        self.button_obey = QPushButton('obey', self)
        self.button_obey.setToolTip('You are hovering over the button, \n what do you expect?')

        self.main_plot = pg.PlotWidget()

        self.vbox_2 = QVBoxLayout()
        self.vbox_2.addWidget(self.button_obey)
        self.vbox_2.addWidget(self.main_plot)
        self.dock_widget_2_content.setLayout(self.vbox_2)
        self.dock_widget_2.setWidget(self.dock_widget_2_content)

        self.dock_widget_2.setFloating(False)
        self.dock_widget_2.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.dock_widget_2.setAllowedAreas(Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)

        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_widget_2)
    def set_osa_dock_widget(self):
        self.osa_dock_widget = QDockWidget("osa dock widget", self)

        self.osa_dock_widget.setWidget(self.experiment.view_instances["OsaInstrument"])

        self.osa_dock_widget.setFloating(False)
        self.osa_dock_widget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.osa_dock_widget.setAllowedAreas(Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.osa_dock_widget)

    def get_view_instances_and_load_instruments(self):
        # name = 'example_experiment_config'
        # config_folder = os.path.dirname(os.path.abspath(__file__))
        # config_file = os.path.join(config_folder, name)

        self.experiment.load_config('C:\\Users\\ariel\\Desktop\\Delft_code\\hyperion\\examples\\example_experiment_config.yml')
        self.experiment.load_instruments()
        self.load_interfaces()
    def load_interfaces(self):
        #method to get an instance of a grafical interface to set in the master gui.
        self.ins_bag = {}

        for instrument in self.experiment.properties['Instruments']:
            if not instrument == 'VariableWaveplate':
                #get the right name
                self.ins_bag[instrument] = self.load_gui(instrument)
    def load_gui(self, name):
        """ Loads gui's

        :param name: name of the instrument to load. It has to be specified in the config file under Instruments
        :type name: string
        """
        try:
            dictionairy = self.experiment.properties['Instruments'][name]
            module_name, class_name = dictionairy['view'].split('/')
            MyClass = getattr(importlib.import_module(module_name), class_name)
            #instr is variable that will be the instrument name of a device. For example: OsaInstrument.
            instr = ((dictionairy['instrument']).split('/')[1])
            #self.experiment.instruments_instances[instr] = the name of the instrument for a device. This is necessary
            #to communicate between instrument and view. Instance is still an instance of for example OsaView.
            instance = MyClass(self.experiment.instruments_instances[instr])
            self.experiment.view_instances[name] = instance
        except KeyError:
            print("the key(aka, your view/gui) does not exist in properties,\n meaning that it is not in the .yml file.")
            return None

    def initUI(self):
        self.get_view_instances_and_load_instruments()

        self.set_dock_widget_1()
        self.set_dock_widget_2()
        self.set_osa_dock_widget()

        self.set_menu_bar()

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

if __name__ == '__main__':
    experiment = ExampleExperiment()

    app = QApplication(sys.argv)

    main_gui = App(experiment)

    sys.exit(app.exec_())