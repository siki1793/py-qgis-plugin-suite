
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from interface import *

#FIXME: erreur selection 

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
        QObject.connect(self.wMain.appliquerFiltre,SIGNAL("clicked()"),self.appliquerfiltre)
        
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
            
    def appliquerfiltre(self):
        self.__appliquerfiltrePostGis()
        
    def __appliquerfiltrePostGis(self):
        req = self.filtres[0].postGisRequet()
        for filtre in self.filtres[1:]:
            req = " AND " + filtre.postGisRequet()
        #Notre requette est build
        myLayer = self.layermap[self.wMain.layerCombo.currentText()]
        myLayer.setSubsetString(req)
        myProvider = myLayer.getDataProvider()
        
        selectedFeatures = []
        f = QgsFeature()
                
        while(myProvider.getNextFeature(f)):
            selectedFeatures.append(f.featureId())
        QMessageBox.information(self.iface.getMainWindow(),"Find by Attribute",str(len(selectedFeatures)))
        myLayer.setSelectedFeatures(selectedFeatures)
        
        
    def ajouterfiltre(self):
        try:
            self.__ajouterfiltreinterne()
        except:
            pass
        else:
            self.__ajouterfiltretree()
    
    def __ajouterfiltreinterne(self):
        self.filtres.append(Filtre(self.wMain.attributeCombo.currentText(),self.wMain.operator.currentText(),self.wMain.valueLine.displayText()))
        
        
    def __ajouterfiltretree(self):
        self.wMain.treeFiltre.addTopLevelItem(QTreeWidgetItem([self.wMain.attributeCombo.currentText(),self.wMain.operator.currentText(),self.wMain.valueLine.displayText() ]))
    
                
        
class Filtre:
    def __init__(self, attrName, operator, value):
        self.attr = attrName
        self.op = operator
        self.value = value
    
    def postGisRequet(self):
        requet = "(%s%s%s)" %(self.attr,self.op,self.value)
        return requet
        
    
                
        
    
        
    
    
    

        
        
      

