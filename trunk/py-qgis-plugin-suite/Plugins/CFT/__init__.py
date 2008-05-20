from plugin import Plugin

def name():
  return "CFT"

def description():
  return "Un test pour les chevauchement entre les layers"

def version():
  return "Version 0.1"

def plugin_type(): #on renvoye le bon type
  return QgisPlugin.UI

def classFactory(iface): #l'appel de la classe
  return Plugin(iface)
