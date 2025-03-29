
import os
import sys

# Add the current directory to the path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main application class
from src.ui.main_window import RisonCopyChecker
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RisonCopyChecker()
    sys.exit(app.exec_())