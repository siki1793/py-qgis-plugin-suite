
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from interface import *

class Plugin:

  # ----------------------------------------- #
    def __init__(self, iface):
        # save reference to the QGIS interface
        self.iface = iface
        self.__listFeature = None
        self.__provider = None
        self.__layer = None
        
    def initGui(self):
        # create action that will start plugin configuration
        self.action = QAction("show attr", self.iface.getMainWindow())
        self.action.setWhatsThis("voir les attributs de la selection")
        QObject.connect(self.action, SIGNAL("activated()"), self.run)

        # add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginMenu("&show attr", self.action)

  # ----------------------------------------- #
    def unload(self):
        # remove the plugin menu item and icon
        self.iface.removePluginMenu("&show attr", self.action)
        self.iface.removeToolBarIcon(self.action)
        
    def run(self):
        # create and show a configuration dialog or something similar
        #On appelle notre interface        
        self.__layer = self.iface.activeLayer() #La layer qui nous interesse
        if not self.__layer or self.__layer.type() != QgsMapLayer.VECTOR:
            #On veut que un type de layer les autres nous interesse pas
            QMessageBox.information(self.iface.getMainWindow(), "No layer", "Select a vector layer!")
        else:
            self.inter = Interface(self.iface.getMainWindow())
            self.modifDiag = modifDialog(self.iface.getMainWindow())
            self.inter.show()
            
            QObject.connect(self.inter.modif,SIGNAL("clicked()"),self.afficherModifDia)
            QObject.connect(self.modifDiag.ok,SIGNAL("clicked()"),self.modifAttr)
            QObject.connect(self.modifDiag.cancel,SIGNAL("clicked()"),self.modifRejected)
            QObject.connect(self.inter.refresh,SIGNAL("clicked()"),self.rebuildTree)
            
            self.__listFeature = self.__layer.selectedFeatures()
            self.__provider = self.__layer.getDataProvider()
            
            self.__buildTree(self.__extractValSelect())
    #--------------------------------------Les fonctions--------------------------------
    def afficherModifDia(self):
        #Construction de notre fenetre
        if self.modifDiag.comboBox.count == 0:
            QMessageBox.information(self.iface.getMainWindow(), "Error", "Aucune valeur commune")
        else:
            self.inter.modif.setEnabled(False)
            self.modifDiag.show()
            
        
    def modifAttr(self):
        attrCombo = self.modifDiag.comboBox.currentText()
        valeur = self.modifDiag.lineEdit.text()
        
        #On cherche l'index de attribut selectionner :
        i = -1
        for (k,attr) in self.__provider.fields().iteritems():
            if attr.name() == attrCombo:
                 i = k
                 break # TODO: break dans une boucle
        if i == -1:
            QMessageBox.information(self.iface.getMainWindow(), "DBG", "Error : Don't find attribut index value")
        #elif type(QVariant(valeur))!= self.__provider.fields()[i].type(): FIXME:verif le type
        #    QMessageBox.information(self.iface.getMainWindow(), "DBG", "Error : No valid type ( %s != %s)" % (type(QVariant(valeur)),self.__provider.fields()[i].type()))
        else:
            QMessageBox.information(self.iface.getMainWindow(), "DBG", "Attr : %s = %s" % (attrCombo,valeur))
            for feature in self.__listFeature:
                feature.changeAttribute(i,QVariant(valeur))
                #On ajoute les modification
                tmp = {}
                tmp[feature.featureId()] = feature.attributeMap()
                self.__provider.changeAttributeValues(tmp)
            
            #On rafraichi nos valeur
            self.rebuildTree()
            
            
            
        self.inter.modif.setEnabled(True)
    def modifRejected(self):
        self.inter.modif.setEnabled(True)
        
    def rebuildTree(self):
        self.inter.treeWidget.clear()
        self.__buildTree(self.__extractValSelect())
        
    def __buildTree(self,valueSelectFeature):
        #FIXME: gestion de la selection vide
        i = 0
        
        for (k,attr) in self.__provider.fields().iteritems():
            try:
                value = valueSelectFeature[0][i]
                #QMessageBox.information(self.iface.getMainWindow(), "DBG", "Champ N :%s" % (str(k)))
            except:
                QMessageBox.information(self.iface.getMainWindow(), "DBG", "No info for attr :%s" % (attr.name()))
            else:
                
                same = True
                for each in valueSelectFeature[1:]:
                    if value!=each[i]:
                        same = False
                        break #TODO: break in for
                
                i = i + 1
                
                if same:
                    self.inter.treeWidget.addTopLevelItem(QTreeWidgetItem([attr.name(),str(value)]))
                else:
                    self.inter.treeWidget.addTopLevelItem(QTreeWidgetItem([attr.name(),"Plusieurs valeurs"]))
                self.modifDiag.comboBox.addItem(attr.name()) #TODO:Regle a eclairsir
                
    def __extractValSelect(self):
        listValSelectFeature = []
        for feature in self.__listFeature: #On iter sur une liste de feature
            listValFeature = []
            for (k,attr) in feature.attributeMap().iteritems(): #Iter sur dictionnaire
                listValFeature.append(attr.toString()) # le .toString() car attr QVariant
            listValSelectFeature.append(listValFeature)
        #QMessageBox.information(self.iface.getMainWindow(), "DBG", "Nombre champs:%s" % (str(len(listValSelectFeature[0]))))
        return listValSelectFeature
        
      

