class ErreurVelo:
	def __init__(self,parent = None):
		self.__parent = parent

class ErreurPedalier:
	def __init__(self,parent=None):
		self.__parent = parent
	
	def valeurGrandPlateau(self, maxP, valP):
		print "ERROR : valeur Grand plateau incorrete, elle doit être comprit entre 0 et %s (valeur entree : %s)" % (maxP, valP)
	
	def valeurPetitPlateau(self, maxP, valP):
		print "ERROR : valeur petit plateau incorrete, elle doit être comprit entre 0 et %s (valeur entree : %s)" % (maxP, valP)