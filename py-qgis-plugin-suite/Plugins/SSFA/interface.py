#Interface pyQT 
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from ui import Ui_Dialog
from dialog_modif import Ui_modifDialog
class Interface(QDialog, Ui_Dialog):
    def __init__(self,parent=None):
        QDialog.__init__(self, parent) #Le constructeur
        self.setupUi(self)    
 
class modifDialog(QDialog, Ui_modifDialog):
    def __init__(self,parent):
        QDialog.__init__(self, parent) #Le constructeur
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Interface()
    ui.show()
    sys.exit(app.exec_())