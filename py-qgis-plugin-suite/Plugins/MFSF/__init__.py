from filtre_selection import Plugin

def name():
  return "MFSF"

def description():
  return "Multi-filtre for select feature"

def version():
  return "Version 0.1"

def plugin_type(): #on renvoye le bon type
  return QgisPlugin.UI

def classFactory(iface): #l'appel de la classe
  return Plugin(iface)

