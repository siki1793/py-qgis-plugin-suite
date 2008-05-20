#Interface pyQT 
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from GUI import *

class Main(QDialog, Ui_Dialog):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    sys.exit(app.exec_())