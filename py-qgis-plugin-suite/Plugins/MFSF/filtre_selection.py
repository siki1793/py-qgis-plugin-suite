
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from interface import *

class Plugin:

  # ----------------------------------------- #
    def __init__(self, iface):
        # save reference to the QGIS interface
        self.iface = iface
        

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
        self.wMain = DiagMain(self.iface.getMainWindow())
        self.wAjouter = DiagCreate(self.wMain)
        self.wModifer = DiagModif(self.wMain)
        
        self.__layermap=QgsMapLayerRegistry.instance().mapLayers() #Avoir toutes les layers
        self.__selectLayermap = None
        self.__selectLayermapProvider = None
        self.__BCList = [] #TODO: voir si on veut garder les valeur quand on ferme ou pas
        self.__BCListCurrent = []
        self.__BCCurrent = None
        
        QObject.connect(self.wMain.ajouter,SIGNAL('clicked()'),self.openAjouter)
        QObject.connect(self.wMain.modifer,SIGNAL('clicked()'),self.openModifer)
        QObject.connect(self.wMain.layerComboBox,SIGNAL('currentIndexChanged(int)'),self.setSelectLayer)
        QObject.connect(self.wAjouter.buttonBox,SIGNAL('accepted()'),self.createNewBC)
        QObject.connect(self.wModifer.buttonBox,SIGNAL('accepted()'),self.modifBC)
        QObject.connect(self.wModifer.selectionnerCouleur,SIGNAL('clicked()'),self.modifCouleur)
        QObject.connect(self.wMain.appliquer,SIGNAL('clicked()'),self.appliquerFiltre)
        self.wMain.show()
        
        #Pour ajouter les layers a la comboBox
        for (name,layer) in self.__layermap.iteritems():
            self.wMain.layerComboBox.addItem(name)
        
        #Initialisation des comboBox pour les operateurs
        self.wModifer.operatorHauteur.addItems(["LOWER","HIGHER"])
        self.wModifer.operatorAire.addItems(["LOWER","HIGHER"])
        
            
    #--------------------------------------Les fonctions--------------------------------
#    def appliquerFiltre(self):
#        """Nous allons appliquer le filtre sur une layer"""
#        #FIXME: faire l'application sur toutes les layers
#        #Visualisation:
#        affichage = QProgressDialog(self.wMain)
#        affichage.setLabelText("Initialisation")
#        
#        #recherche de la cle pour la hauteur:
#        self.__selectLayermapProvider.reset()
#        fieldmap=self.__selectLayermapProvider.fields()
#        numeroId = -1
#        for (k,attr) in fieldmap.iteritems():      
#            if ("height"==attr.name()):
#                numeroId = k
#        
#        if numeroId == -1:
#             QMessageBox.warning(self.wMain,"ERROR","FATAL ERROR : Pas d'attribut hauteur : height")
#             return None
#        
#        #Pour avoir toutes les features
#        self.__selectLayermapProvider.reset()
#        self.__selectLayermapProvider.select(self.__selectLayermapProvider.allAttributesList())
#        f=QgsFeature()
#        dictionnaire = {}
#        
#        #initialisation du dictionnaire
#        for i in range(len(self.__BCListCurrent)):
#            dictionnaire[i] = []
#        
#        
#        u = True
#        
#        affichage.setLabelText("Passage du filtre")
#        affichage.setRange(1, self.__selectLayermapProvider.featureCount())
#        idFeature = 1
#        #On parcours toutes les features
#        while(self.__selectLayermapProvider.getNextFeature(f)):
#            passed = False
#            i = 0
#            #Les choses que l'on aura besoin pour les calcul
#            aire = QgsDistanceArea().measure(f.geometry())
#            hauteur = f.attributeMap()[numeroId]
#            
#            
#            for bc in self.__BCListCurrent:
#                if bc.getValid():
#                    if (bc.comparaisonHauteur(hauteur) & bc.comparaisonAire(aire)):
#                        passed = True
#                        if u:
#                            QMessageBox.warning(self.wMain,"ERROR","Pass")
#                            u = False
#                        dictionnaire[i].append(f)
#                i = i + 1
#            if passed:
#                pass #Tout c'est bien passer
#            else:
#                #QMessageBox.warning(self.wMain,"ERROR","Pour cette feature touts les tests ont echouee")
#                #FIXME: Faire quelque chose de plus fonctionnel
#                pass
#            affichage.setValue(idFeature)
#            idFeature = idFeature + 1
#            
#        #On color se que l'on a trouver
#        for (k,listF) in dictionnaire.iteritems():
#            self.__selectLayermap.setSelectedFeatures(listF)
#            self.__selectLayermap.renderer().setSelectionColor(self.__BCCurrent[k].getColor())

    def appliquerFiltre(self):
        """On applique le filtre"""
        for i in range(len(self.__BCListCurrent)):
            tmp = QgsVectorLayer()
            tmp = self.__selectLayermap
            
            if self.__BCListCurrent[i].getValid(): #FIXME: attentio test au premier
                if i!=0:
                    req = "(" + self.__BCListCurrent[0].buildSQL() + ")"
                    for el in self.__BCListCurrent[:i-1]:
                        req = "(" + el.buildSQL() + ") AND " + req
                    #self.__selectLayermap.setSubsetString(self.__BCListCurrent[i].buildSQL() + " NOT (" + req + ")" )
                    tmp.setSubsetString(self.__BCListCurrent[i].buildSQL() + " NOT (" + req + ")" )
                else:
                    tmp.setSubsetString(self.__BCListCurrent[i].buildSQL())
                    #self.__selectLayermap.setSubsetString(self.__BCListCurrent[i].buildSQL())
                for el in tmp.renderer().symbols():
                    el.setFillColor(self.__BCListCurrent[i].getColor())
                #On a recupere toutes les feature
                
                 #FIXME: important enum LAYERS.VECTOR = 0
                
                
#                for (name,layer) in self.__layermap:
#                    if name == self.__BCListCurrent[i].getName():
#                        layer
                    
                #on on ajoute
                
        
        
    def modifCouleur(self):
        couleur = QColorDialog.getColor(Qt.white,self.iface.getMainWindow())
        self.__BCCurrent.setColor(couleur)
        #On rafraichi notre fenetre
        self.wModifer.showSelectColor.setText(str(self.__BCCurrent.getColor().value()))
        
    def openAjouter(self):
        self.wAjouter.show()
    
    def openModifer(self):
        self.__BCCurrent = None
        for el in self.__BCListCurrent:
            if str(el) == self.wMain.comboBox.currentText():
                self.__BCCurrent = el
        if self.__BCCurrent == None:
            QMessageBox.warning(self.wMain,"ERROR","Fatal error : On a pas pu determiner la bc selectionner dans la comboBox")
        self.__BCCurrent.getValues(self.wModifer)
        self.wModifer.show()
        
    def setSelectLayer(self,args):
        self.__selectLayermap=self.__layermap[self.wMain.layerComboBox.currentText()]
        self.__selectLayermapProvider=self.__selectLayermap.getDataProvider()
        self.wMain.comboBox.clear()
        self.__BCListCurrent = []
        #On met a jour les bc de la layer associee
        for bcIt in self.__BCList:
            if bcIt.getLayer == self.__selectLayermap:
                self.__BCListCurrent.append(bcIt)
                self.wMain.comboBox.addItem(QString(str(bc))) #On ajoute a notre liste
                
        
    def createNewBC(self):
        """Creation d'une nouvelle building class"""
        #On recupere le nom de notre building class
        bcName = self.wAjouter.lineEdit.displayText()
        #On ajoute a notre combobox des BC
        bc = BCItem(bcName, self.__selectLayermap)
        #On append aux autres liste
        self.__BCList.append(bc)
        self.__BCListCurrent.append(bc)
        #TODO: voir si on change de layer on supprime les bc mise
        self.wMain.comboBox.addItem(QString(str(bc)))
        
    
    def modifBC(self):
        self.__BCCurrent.setValues(self.wModifer)
    
class BCItem:
    def __init__(self, name,layer=None):
        self.__name = name
        self.__layer = layer
        
        self.__HauteurEnable = False
        self.__Hauteur = -1
        self.__AireEnable = False
        self.__Aire = -1
        #Regles sur les operateurs:
        # 0 = Lower
        # 1 = Highter
        # -1 = No define
        self.__opHauteur = -1
        self.__opAire = -1
        self.__FLAT_ROOF = None
        
        self.__color = QColor(255,0,0)
        
    def __repr__(self):
        return self.__name
    
    def __str__(self):
        return str(self.__name)
    
    def getHauteurEnable(self):
        return self.__HauteurEnable
    
    def getAireEnable(self):
        return self.__AireEnable
    
    def getHauteurValue(self):
        return self.__Hauteur
    
    def getAireValue(self):
        return self.__Aire
        
    def comparaisonHauteur(self,valeur):
        """Pour comparer une hauteur et une valeur avec le filtre"""
        if self.__HauteurEnable:
            if self.__opHauteur == 0:
                return (QVariant(self.__Hauteur) > valeur)
            else:
                return (QVariant(self.__Hauteur) < valeur)
        else:
            return True
    
    def comparaisonAire(self,valeur):
        """Pour comparer une hauteur et une valeur avec le filtre"""
        if self.__AireEnable:
            if self.__opAire == 0:
                return (self.__Aire > valeur)
            else:
                return (self.__Aire < valeur)
        else:
            return True
    
    def __buildSQLHauteur(self):
        
        if self.__opHauteur == 0:
             return "height<%s" % (self.__Hauteur)
        else:
             return "height>%s" % (self.__Hauteur)
    
    def __buildSQLAire(self):
        
        if self.__opHauteur == 0:
             return "area2d(wkb_geometry)<%s" % (self.__Aire)
        else:
             return "area2d(wkb_geometry)>%s" % (self.__Aire)
         
    
    def buildSQL(self):
        requet = ""
        if self.__HauteurEnable & self.__AireEnable:
            return self.__buildSQLHauteur() + " AND " + self.__buildSQLAire()
        elif self.__HauteurEnable:
            return self.__buildSQLHauteur()
        elif self.__AireEnable:
            return self.__buildSQLAire()
        else:
            return "height>0" #FIXME: a fixer
        
    def getName(self):
        return self.__name
    
    def setColor(self,Color):
        self.__color = Color

    def getColor(self):
        return self.__color
        
    def getLayer(self):
        return self.__layer
    
    def getValues(self,interface):
        """Rend les valeurs par l'interface"""
        self.__interfaceNormale(interface)
        if self.__FLAT_ROOF == None: # pas de varleurs initialisee
            pass
        else:
            #On rend notre interface
            #Pour FLAT_ROOF
            if self.__FLAT_ROOF:
                interface.FlatRoof.setCheckState(Qt.Checked)
            else:
                interface.FlatRoof.setCheckState(Qt.Unchecked)
            
            #Pour la hauteur
            if self.__HauteurEnable:
                interface.hauteurCheck.setCheckState(Qt.Checked)
                if self.__Hauteur == -1:
                    interface.valHauteur.setText("ERROR")
                else:
                    interface.valHauteur.setText(str(self.__Hauteur))
                
                interface.operatorHauteur.setCurrentIndex(self.__opHauteur)
            
            #Pour l'aire
            if self.__AireEnable:
                interface.aireCheck.setCheckState(Qt.Checked)
                if self.__Aire == -1:
                    interface.valAire.setText("ERROR")
                else:
                    interface.valAire.setText(str(self.__Aire))
                
                interface.operatorAire.setCurrentIndex(self.__opAire)
            
    
    def setValues(self,interface):
        """Prend l'interface pour recuperer les valeurs"""
        self.__FLAT_ROOF = (interface.FlatRoof.checkState() == Qt.Checked)
        if interface.hauteurCheck.checkState() == Qt.Checked:
            self.__HauteurEnable = True
            if interface.operatorHauteur.currentText() == "": #TODO: cas impossible
                QMessageBox.warning(interface,"ERROR","Vous devez sepcifier un operateur pour la hauteur")
            else:
                #Si l'utilisateur a bien choisi
                if interface.operatorHauteur.currentText() == "HIGHER":
                    self.__opHauteur = 1
                else:
                    self.__opHauteur = 0
            
            if interface.valHauteur.displayText() == "":
                QMessageBox.warning(interface,"ERROR","Vous devez mettre une valeur pour la hauteur")
            else:
                try:
                    self.__Hauteur = float(interface.valHauteur.displayText())
                except:
                    self.__Hauteur = -1
                    QMessageBox.warning(interface,"ERROR","vous devez mettre comme valeur un nombre dans la valeur de la hauteur")
        else:
            self.__HauteurEnable = False
            self.__Hauteur = -1
            self.__opHauteur = -1
        
        if interface.aireCheck.checkState() == Qt.Checked:
            self.__AireEnable = True
            if interface.operatorAire.currentText() == "": #TODO: cas impossible
                QMessageBox.warning(interface,"ERROR","Vous devez sepcifier un operateur pour l'aire")
            else:
                #Si l'utilisateur a bien choisi
                if interface.operatorAire.currentText() == "HIGHER":
                    self.__opAire = 1
                else:
                    self.__opAire = 0
            
            if interface.valAire.displayText() == "":
                QMessageBox.warning(interface,"ERROR","Vous devez mettre une valeur pour l'aire")
            else:
                try:
                    self.__Aire = float(interface.valAire.displayText())
                except:
                    self.__Aire = -1
                    QMessageBox.warning(interface,"ERROR","vous devez mettre comme valeur un nombre dans la valeur de l'aire")
        else:
            self.__AireEnable = False
            self.__Aire = -1
            self.__opAire = -1
            
    def __interfaceNormale(self,interface):
        """Pour reinitialiser l'interface de depard"""
        interface.operatorHauteur.setCurrentIndex(0)
        interface.operatorAire.setCurrentIndex(0)
        interface.valHauteur.setText("")
        interface.valAire.setText("")
        interface.aireCheck.setCheckState(Qt.Unchecked)
        interface.hauteurCheck.setCheckState(Qt.Unchecked)
        interface.FlatRoof.setCheckState(Qt.Unchecked)
        interface.showSelectColor.setText(str(self.__color.value()))
    def getValid(self):
        """Verfier que le BC item est valide"""
        if self.__FLAT_ROOF==None:
            return False
        
        if self.__HauteurEnable:
            if (self.__Hauteur == -1) | (self.__opHauteur == -1):
                return False
        
        if self.__AireEnable:
            if (self.__Aire == -1) | (self.__opAire == -1):
                return False
        
        #Si tous les tests sont passee :
        return True
        
        
      

