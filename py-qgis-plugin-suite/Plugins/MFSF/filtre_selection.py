
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from interface import *

class Plugin:

  # ----------------------------------------- #
    def __init__(self, iface):
        # save reference to the QGIS interface
        self.iface = iface
        self.layermap = None
        self.filtres = []
        
    def initGui(self):
        # create action that will start plugin configuration
        self.action = QAction("filtre selection", self.iface.getMainWindow())
        self.action.setWhatsThis("Pour selectionner des batiments par des filtres")
        QObject.connect(self.action, SIGNAL("activated()"), self.run)

        # add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginMenu("&filtre selection", self.action)

  # ----------------------------------------- #
    def unload(self):
        # remove the plugin menu item and icon
        self.iface.removePluginMenu("&filtre selection", self.action)
        self.iface.removeToolBarIcon(self.action)
        
    def run(self):
        # create and show a configuration dialog or something similar
        #On appelle notre interface
        #flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint #FIXME: a revoir
        #self.inter = Interface(self.iface.getMainWindow(),flags)
        self.wMain = Main(self.iface.getMainWindow())
        
        QObject.connect(self.wMain.layerCombo,SIGNAL('currentIndexChanged (int)'),self.readlayercolumns)
        QObject.connect(self.wMain.ajouterFiltre,SIGNAL("clicked()"),self.ajouterfiltre)
        
        
        self.__initwMain()
        self.wMain.show()
        
    def __initwMain(self):
        self.wMain.operator.addItems(["=",">","<",">=","<="])
        
        self.layermap=QgsMapLayerRegistry.instance().mapLayers()
        for (name,layer) in self.layermap.iteritems():
            self.wMain.layerCombo.addItem(name)
        
    def readlayercolumns(self,args):
        vectorlayer=self.layermap[self.wMain.layerCombo.currentText()]
        provider=vectorlayer.getDataProvider()
        fieldmap=provider.fields()
        
        self.wMain.attributeCombo.clear()
        for (k,attr) in fieldmap.iteritems():
            self.wMain.attributeCombo.addItem(attr.name())
            
    def ajouterfiltre(self):
        self.__ajouterfiltretree()
    
    def __ajouterfiltretree(self):
        self.wMain.treeFiltre.addTopLevelItem(QTreeWidgetItem([self.wMain.attributeCombo.currentText(),self.wMain.operator.currentText(),self.wMain.valueLine.displayText() ]))
    
                
        
        
    
        
    
                
        
    
        
    
    
    

        
        
      

