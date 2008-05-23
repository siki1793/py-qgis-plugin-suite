from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from interface import *

class Plugin:
    def __init__(self, iface):
        # save reference to the QGIS interface
        self.iface = iface
    def initGui(self):
        # create action that will start plugin configuration
        self.action = QAction("CFT", self.iface.getMainWindow())
        QObject.connect(self.action, SIGNAL("activated()"), self.run)

        # add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginMenu("&CFT", self.action)
    
    def unload(self):
        # remove the plugin menu item and icon
        self.iface.removePluginMenu("&CFT", self.action)
        self.iface.removeToolBarIcon(self.action)
    
    def run(self):
        #Marche pour l'instant que pour DB
        pass
        