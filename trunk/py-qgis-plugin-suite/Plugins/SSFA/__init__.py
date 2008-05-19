from show_attribut import Plugin

def name():
  return "show selection attribut"

def description():
  return "Pour voir les attributs en commun de la selection"

def version():
  return "Version 0.2"

def plugin_type(): #on renvoye le bon type
  return QgisPlugin.UI

def classFactory(iface): #l'appel de la classe
  return Plugin(iface)

