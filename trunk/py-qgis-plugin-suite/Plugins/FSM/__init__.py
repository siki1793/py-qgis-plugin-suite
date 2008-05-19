from filtre_selection import Plugin

def name():
  return "filtre selection"

def description():
  return "Pour selectionner des batiments avec des attributs pour les build class"

def version():
  return "Version 0.3"

def plugin_type(): #on renvoye le bon type
  return QgisPlugin.UI

def classFactory(iface): #l'appel de la classe
  return Plugin(iface)

