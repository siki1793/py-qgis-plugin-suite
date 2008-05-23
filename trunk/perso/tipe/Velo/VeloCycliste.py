class VeloCycliste:
	def __init__(self,nom="Personne",poids=60000,aireFace=0): #TODO: voir calcul pour l'aire face
		self.__nom = nom
		self.__poids = poids
		self.__aireFace = aireFace
		
	def getPoids(self):
		return self.__poids
	
	def __repr__(self):
		return "%s Poids : %s g, Aire face : %s mm3 \n" % (self.__nom, self.__poids, self.__aireFace) 