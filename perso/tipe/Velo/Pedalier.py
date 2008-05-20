from Erreurs import ErreurPedalier

class Pedalier:
	def __init__(self,longueurBranche = 100, initAngle = 0, GrandPlateau = [15,25,35], PetitPlateau = [5,10,15,20,25,30], initGP = 1, initPP = 1):
		self.__nbGrandPlateau = len(GrandPlateau)
		self.__nbPetitPlateau = len(PetitPlateau)
		
		self.__grandPlateau = GrandPlateau
		self.__petitPlateau = PetitPlateau
		
		self.__GPCourant = initGP - 1
		self.__PPCourant = initPP - 1
		
		self.__longueur = longueurBranche
		
		self.__error = ErreurPedalier(self)
	
	def __repr__(self):
		trace = ""
		trace = " * Plateau courant (grand, petit) : %s, %s\n" % (self.__GPCourant + 1, self.__PPCourant + 1)
		trace = trace + "--General-- : \n"
		trace = trace + " * Nombre plateau (Grand, Petit): %s, %s \n" % (self.__nbGrandPlateau, self.__nbPetitPlateau)
		trace = trace + " * Longueur Branche : %s \n" % (self.__longueur)
		trace = trace + "--Detail-- : \n"
		tmp = ""
		i = 1
		for el in self.__grandPlateau:
			tmp = tmp + " [%seme : %s mm]" % (i, el)
			i = i + 1
		trace = trace + " * Grand plateau (numero plateau, taille rayon) : " + tmp + "\n"
		i = 1
		for el in self.__petitPlateau:
			tmp = tmp + " [%seme : %s mm]" % (i, el)
			i = i + 1
		trace = trace + " * Petit plateau (numero plateau, taille rayon) : " + tmp + "\n"
		return trace
	
	def setGrandPlateau(self, valeur):
		if (valeur > 0) and valeur < self.__nbGrandPlateau:
			self.__GPCourant = valeur - 1
		else:
			self.__error.valeurGrandPlateau(self.__nbGrandPlateau, valeur)
	
	def getGrandPlateau(self):
		return self.__mGrandPlateau + 1
	
	def setPetitPlateau(self, valeur):
		if (valeur > 0) and valeur < self.__nbPetitPlateau:
			self.__PPCourant = valeur - 1
		else:
			self.__error.valeurPetitPlateau(self.__nbPetitPlateau, valeur)
	
	def getPetitPlateau(self):
		return self.__mPetitPlateau + 1
	
	def getLongueur(self):
		return self.__longueur
	
	def setLongeur(self,v):
		self.__longueur = v
	
	
