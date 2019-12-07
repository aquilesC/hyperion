import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import *
from hyperion import root_dir
from hyperion.controller.cobolt.cobolt08NLD import Cobolt08NLD
# Import from a lantz the start_gui helper function
from lantz.qt.app import start_gui
from lantz.qt.widgets import *


main = uic.loadUi(os.path.join(root_dir,'view', 'laser','cobolt.ui')) # load the gui

with Cobolt08NLD.via_serial('5') as inst:
    app = QApplication(sys.argv)
    start_gui(main, inst)  # All signals and slots are connected here!
    print('doing stuff')

