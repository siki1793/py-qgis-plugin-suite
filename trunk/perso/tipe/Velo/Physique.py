#FIXME: Il faut prendre en compte la topologie

class ModelVelo:
	def __init__(self,velo):
		"Constructeur : prend velo pour le model"
		self.__velo = velo
	 
	def energieCinetique(self):
		"renvoie la valeur de l'energie cinetique"
		return 0.5 * self.__velo.poidsTotal() * (self.__velo.vitesse() ** 2)
	
	def puissanceChaine(self):
		"renvoie la valeur de la puissance de la dispation de la chaine"
		return 0
	
	def puissanceFrottementFrontal(self):
		"renvoie la valeur de la puissance du frottement frontal"
		return 0
	
	def puissancePedalier(self):
		"renvoie la puissance mit dans les deux pedales"
		return 0
	
	
