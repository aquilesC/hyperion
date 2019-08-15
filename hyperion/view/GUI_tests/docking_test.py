import importlib
import random
import string
import sys
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDockWidget, QListWidget, QTextEdit, QPushButton, \
    QGraphicsView, QAction, QLineEdit, QScrollArea, QVBoxLayout, QHBoxLayout, QGridLayout
import pyqtgraph as pg
from examples.example_experiment import ExampleExperiment

class App(QMainWindow):

    def __init__(self, experiment):
        super().__init__()
        self.title = 'master gui'
        self.left = 40
        self.top = 40
        self.width = 800
        self.height = 500
        self.button_pressed = False
        self.experiment = experiment

        self.setWindowTitle("Dock demo")

        self.initUI()
    def initUI(self):
        self.set_gui_specifics()

        self.get_view_instances_and_load_instruments()

        self.set_menu_bar()

        self.make_automatic_dock_widgets()

        self.show()

    def set_gui_specifics(self):
        """"
        In this function the specifics of the gui are set.
        Such as the Geometry and the ability to have more docking options.
        """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        _DOCK_OPTS = QMainWindow.AllowTabbedDocks
        # _DOCK_OPTS |= QMainWindow.AllowNestedDocks         # This has no impact on the code if switched on
        # _DOCK_OPTS |= QMainWindow.AnimatedDocks            # I don't know what this does

        # Turn the central widget into a QMainWindow which gives more docking possibilities
        self.central = QMainWindow()
        self.central.setWindowFlags(Qt.Widget)
        self.central.setDockOptions(_DOCK_OPTS)
        self.setCentralWidget(self.central)

    def set_menu_bar(self):
        """"
        In this method the menubar of the gui is created and filled with
        menu's and menu's are filled with actions. The actions of edgeDockMenu and centralDockMenu
        are filled in randomDockWindow method.
        """
        mainMenu = self.menuBar()
        self.fileMenu = mainMenu.addMenu('File')
        self.fileMenu.addAction("Exit NOW", self.close)
        self.instrument_menu = mainMenu.addMenu('Edge Dock windows')
        self.visiualise_menu = mainMenu.addMenu('Central Dock Windows')

        self.draw_something = mainMenu.addMenu('draw')
        self.draw_something.addAction("Draw", self.draw_random_graph)

        self.toolsMenu = mainMenu.addMenu('Tools')
        self.toolsMenu.addAction("Let widget 1 disappear", self.get_status_open_or_closed)
        self.toolsMenu.addAction("Make widget", self.create_single_qdockwidget)

        self.helpMenu = mainMenu.addMenu('Help')

    def get_status_open_or_closed(self):
        """"
        An example of how to make a widget visible and not visible.
        Can be automated as menuaction in RandomDockWidget, with additional code(ofcourse).
        """
        self.dock_widget_dict["ExampleInstrument_3"].setVisible(not self.dock_widget_dict["ExampleInstrument_3"].isVisible())
    def create_single_qdockwidget(self):
        """"
        In this method the goal is to create a blank QDockwidget and set this widget in the main_gui.
        It must be done only once because else errors will be created.
        This is example code of how to do this.
        """
        if self.button_pressed == False:
            self.random_widget = QDockWidget("some_widget",self)

            self.random_widget.setFloating(False)

            self.random_widget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
            self.random_widget.setAllowedAreas(Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)

            self.addDockWidget(Qt.TopDockWidgetArea, self.random_widget)

            self.button_pressed = True

    def draw_random_graph(self):
        """"
        Simple code to make a literal random graph using pyqt5 plotting stuff.
        """
        self.ydata = [random.random() for i in range(25)]
        self.xdata = [random.random() for i in range(25)]
        self.experiment.graph_view_instance["Gui_with_graphGraph"].random_plot.plot(self.xdata, self.ydata, clear=True)

    def make_automatic_dock_widgets(self):
        """"
        In this method there will be made automatically QDockWidgets using the lijst_met_dock_widget.
        The widget's are saved in the self.dock_widget_dict, through this way the widgets are approachable via self.
        Each QDockWidget will be given it's specifics in the make_dock_widgets left and right + central left and right.
        The rest of the things will be filled in at the RandomDockWidget method.
        """
        self.dock_widget_dict = {}
        opteller = 1

        self.get_left_right_amount_of_gui(len(self.experiment.view_instances.keys()))
        for dock_widget in self.experiment.view_instances.keys():
            if opteller <= self.left_amount_of_gui:
                self.make_left_dock_widgets(dock_widget, opteller)
            elif opteller > self.right_amount_of_gui:
                self.make_right_dock_widgets(dock_widget, opteller)
            opteller += 1
        self.get_left_right_amount_of_gui(len(self.experiment.graph_view_instance.keys()))
        opteller = 1
        for dock_widget in self.experiment.graph_view_instance.keys():
            if opteller <= self.left_amount_of_gui:
                self.make_central_right_dock_widgets(dock_widget, opteller)
            elif opteller > self.right_amount_of_gui:
                self.make_central_left_dock_widgets(dock_widget, opteller)
            opteller += 1
    def get_left_right_amount_of_gui(self, amount_of_gui):
        amount_of_instrument_gui = amount_of_gui
        if amount_of_instrument_gui % 2 == 0:
            # there are a number of gui's
            self.left_amount_of_gui = amount_of_instrument_gui / 2
            self.right_amount_of_gui = amount_of_instrument_gui / 2
        else:
            # there are a uneven amount of gui's
            self.left_amount_of_gui = int(amount_of_instrument_gui / 2)
            self.right_amount_of_gui = (int(amount_of_instrument_gui / 2) + (amount_of_instrument_gui % 2 > 0))

    def make_left_dock_widgets(self, dock_widget, opteller):
        self.dock_widget_dict[dock_widget] = self.randomDockWindow(self.instrument_menu, dock_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget_dict[dock_widget])
        if opteller == 0:
            self.dock_widget_dict[dock_widget].setFeatures(QDockWidget.NoDockWidgetFeatures)
        elif opteller == 1:
            self.dock_widget_dict[dock_widget].setFeatures(
                QDockWidget.NoDockWidgetFeatures | QDockWidget.DockWidgetClosable)
    def make_right_dock_widgets(self, dock_widget, opteller):
        self.dock_widget_dict[dock_widget] = self.randomDockWindow(self.instrument_menu, dock_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget_dict[dock_widget])
        if opteller == 3:
            self.dock_widget_dict[dock_widget].setFeatures(
                QDockWidget.NoDockWidgetFeatures | QDockWidget.DockWidgetMovable)
        elif opteller == 4:
            self.dock_widget_dict[dock_widget].setFeatures(
                QDockWidget.NoDockWidgetFeatures | QDockWidget.DockWidgetFloatable)
    def make_central_right_dock_widgets(self, dock_widget, opteller):
        self.dock_widget_dict[dock_widget] = self.randomDockWindow(self.visiualise_menu, dock_widget)
        self.central.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget_dict[dock_widget])
        if opteller == 2:
            self.dock_widget_dict[dock_widget].setFeatures(QDockWidget.NoDockWidgetFeatures)
    def make_central_left_dock_widgets(self, dock_widget, opteller):
        self.dock_widget_dict[dock_widget] = self.randomDockWindow(self.visiualise_menu, dock_widget)
        self.central.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget_dict[dock_widget])
        if opteller == 4:
            self.dock_widget_dict[dock_widget].setFeatures(QDockWidget.NoDockWidgetFeatures)

    def randomString(self, N):
        return ''.join([random.choice(string.ascii_lowercase) for n in range(N)])
    def randomDockWindow(self, menu, name=None):
        """"
        In this method the widget will be made a QDockWidget.
        There are some nested functions in this method with which
        the action to toggle the widget will be available in the given menu.

        :param menu: a menu to set a quick action in
        :type QmenuBar
        :param name: the name of the widget to add
        :type string
        """
        dock, name = self.setting_standard_dock_settings(name)

        self.setting_dock_content(dock, name)

        def toggle_visibility():
            dock.setVisible(not dock.isVisible())
        def toggle_collapsed():
            if not dock.collapsed:
                #dock.uncollapsed_height = dock.height()    # Haven't worked this out yet
                dock.setMinimumHeight(dock.collapsed_height)
                dock.setMaximumHeight(dock.collapsed_height)
                dock.collapsed = True
            else:
                dock.setMinimumHeight(dock.uncollapsed_height)
                dock.collapsed = False

        menu.addAction(name, toggle_collapsed)
        return dock
    def setting_dock_content(self, dock, name):
        """"
        Setting some widgets with gui's from different files and
        setting the 'normal' gui's with some content so that they are not empty.

        :param dock: a generic qdockwidget
        :type QDockWidget, used to set gui's in
        :param name: name of the dock_widget
        :type string
        """
        if name[-5:] == "Graph":
            #it are graph widgets
            dock.setWidget(self.experiment.graph_view_instance[name])
        else:
            #the widget is an instrument widget
            dock.setWidget(self.experiment.view_instances[name])
        """"
        #old code used to make some random stuff in a widget.
        string_list = [self.randomString(5) for n in range(5)]
        listwidget = QListWidget(dock)
        listwidget.addItems(string_list)
        dock.setWidget(listwidget)
        """
    def setting_standard_dock_settings(self, name):
        """"
        Setting standard functionality of a QDockWidget.
        """
        if name == None:
            name = self.randomString(7)
        dock = QDockWidget(name, self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.collapsed = False
        dock.collapsed_height = 22
        dock.uncollapsed_height = 200
        return dock, name

    def set_dock_widget_2(self):
        """
        Old code needed to have an example of how to add a QdockWidget by hand.
        For the rest, it is not needed.
        """
        """
        # how to add Qobjects to a dockable goes as follows.
        # First you make a Qwidget where the content will be placed in. Call this things something with content in the name
        # Then define the Qobjects you want to make
        # Finally, you choose a layout((maybe absolute positioning is possible,
        # haven't seen it in examples so it is not implemented in this code)QVBoxLayout, QHBoxLayout and QGridLayout)
        # then you add the layout to the content widget and lastly you set the beginning Qwhatever as the widget of the dockwidget.

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

    def get_view_instances_and_load_instruments(self):
        """"
        In this function with functions found in the ExampleExperiment class
        Instruments and interfaces will be loaded via the .yml file.
        The .yml file should be in the same folder as this python file in order to not hardcode the
        path to the .yml file.
        """
        # name = 'example_experiment_config'
        # config_folder = os.path.dirname(os.path.abspath(__file__))
        # config_file = os.path.join(config_folder, name)

        self.experiment.load_config('C:\\Users\\ariel\\Desktop\\Delft_code\\hyperion\\examples\\example_experiment_config.yml')
        self.experiment.load_instruments()
        self.load_interfaces()
    def load_interfaces(self):
        """"
        Method to get instances of gui's through load_gui and set these in self.ins_bag.
        Through this way they can later be retrieved in the self object.
        """
        self.ins_bag = {}

        for instrument in self.experiment.properties['Instruments']:
            if not instrument == 'VariableWaveplate':
                #get the right name
                self.ins_bag[instrument] = self.load_gui(instrument)
                for index in self.experiment.properties['Instruments'][instrument]:
                    #get an additional gui(if available) on which will be a graph.
                    if index == "graphView":
                        self.load_graph_gui(instrument)
    def load_gui(self, name):
        """
        Create instances of gui's and returns these to the load_intefaces.

        :param name: name of view to load. It has to be specified in the config file under Instruments
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
            print("the view key(aka,"+str(name)+") does not exist in properties,\n meaning that it is not in the .yml file.\n This not a bad thing, if there is a gui"
                                                "than you can ignore this message.")
            return None

    def load_graph_gui(self, name):
        dictionairy = self.experiment.properties['Instruments'][name]
        module_name, class_name = dictionairy['graphView'].split('/')
        MyClass = getattr(importlib.import_module(module_name), class_name)
        # instr is variable that will be the instrument name of a device. For example: OsaInstrument.
        instr = ((dictionairy['instrument']).split('/')[1])
        instance = MyClass()
        # Getting certain uniquetiy by addiding _graph as a name. For example: OsaInstrumentGraph.
        self.experiment.graph_view_instance[name + "Graph"] = instance


if __name__ == '__main__':
    experiment = ExampleExperiment()
    app = QApplication(sys.argv)

    main_gui = App(experiment)

    sys.exit(app.exec_())