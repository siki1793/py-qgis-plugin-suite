# Le poids est en gramme
# les distances en metres

from Pedalier import Pedalier
from VeloCycliste import VeloCycliste
from Erreurs import ErreurVelo

# Les liste des plateau doit etre en rayon et la distance est en mm
class Velo:
	def __init__(self,vitesse = 0,veloCycliste=VeloCycliste(), poidsVelo = 1200, pedalier = Pedalier(), longueurRayonRoue = 200 ): 
		"Constructeur : prend (vitesse,velo cycliste, poids velo, pedalier, longeur rayon roue)"
		#FIXME: voir les valeurs par default 
		#Variable importante du system
		self.__vitesse = vitesse
		
		#Constance class
		self.__error = ErreurVelo(self)
		
		#Constance du velo
		self.__veloCycliste = veloCycliste
		self.__poidsVelo = poidsVelo
		self.__pedalier = pedalier
		self.__rayonRoue = longueurRayonRoue
	
	def __repr__(self):
		"Renvoie la representation complete du velo (avec velo cycliste et pedalier)"
		trace = ""
		trace = trace + "%s" % (self.__veloCycliste)
		trace = trace + "----- Etat velo ----- : \n"
		trace = trace + " * Poids (Velo, cycliste, total) en g : %s, %s, %s\n" % (self.__poidsVelo, self.__veloCycliste.getPoids(), self.__poidsVelo +self.__veloCycliste.getPoids())
		trace = trace + " * Longueur rayon roue : %s\n" % (self.__rayonRoue)
		trace = trace + " * Vitesse : %s \n" % (self.__vitesse)
		trace = trace + "---- Etat pedalier ---- : \n%s \n" % (self.__pedalier)
		return trace
	
	def vitesse(self):
		"Renvoie la vistesse"
		return self.__vitesse
	
	def setVitesse(self,v):
		"Affecte la vitesse = v"
		self.__vistesse = v
	
	def veloCycliste(self):
		"Renvoie le velo cycliste"
		return self.__veloCycliste
	
	def setVeloCycliste(self,VeloC):
		"Change la velo cycliste"
		self.__veloCycliste = VeloC
	
	def pedalier(self):
		"Renvoie le pedalier"
		return self.__pedalier
	
	def setPedalier(self, NouvPedalier):
		"Change le pedalier"
		self.__pedalier = NouvPedalier
		
	

