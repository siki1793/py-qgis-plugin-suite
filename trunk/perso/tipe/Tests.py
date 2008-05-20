from Velo import *
 
 # la batterie de test
print "Demarrage batterie de tests"
monVelo = Velo(veloCycliste = VeloCycliste("Adrien",59200,43))
print monVelo

monVelo.pedalier().setGrandPlateau(20)
monVelo.pedalier().setPetitPlateau(2)

print monVelo