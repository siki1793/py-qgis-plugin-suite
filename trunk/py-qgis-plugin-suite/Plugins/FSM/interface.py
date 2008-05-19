#Interface pyQT 
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from GUI import *
class DiagModif(QDialog, Ui_ModifBuildClass):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        self.setupUi(self)

class DiagCreate(QDialog, Ui_CreateBuildClass):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        self.setupUi(self)

class DiagMain(QDialog, Ui_DiagMain):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = DiagMain()
    ui.show()
    sys.exit(app.exec_())
    
        
