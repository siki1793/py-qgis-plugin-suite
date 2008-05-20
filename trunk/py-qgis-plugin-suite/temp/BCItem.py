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