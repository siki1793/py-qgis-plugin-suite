# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uiFile/ModifBuildClass.ui'
#
# Created: Wed May 14 17:05:21 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ModifBuildClass(object):
    def setupUi(self, ModifBuildClass):
        ModifBuildClass.setObjectName("ModifBuildClass")
        ModifBuildClass.resize(QtCore.QSize(QtCore.QRect(0,0,262,300).size()).expandedTo(ModifBuildClass.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(ModifBuildClass)
        self.buttonBox.setGeometry(QtCore.QRect(-80,270,341,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.wTab = QtGui.QTabWidget(ModifBuildClass)
        self.wTab.setGeometry(QtCore.QRect(0,10,261,261))
        self.wTab.setObjectName("wTab")

        self.Value = QtGui.QWidget()
        self.Value.setObjectName("Value")

        self.groupBox = QtGui.QGroupBox(self.Value)
        self.groupBox.setGeometry(QtCore.QRect(10,10,241,101))
        self.groupBox.setObjectName("groupBox")

        self.hauteurCheck = QtGui.QCheckBox(self.groupBox)
        self.hauteurCheck.setGeometry(QtCore.QRect(10,20,70,19))
        self.hauteurCheck.setObjectName("hauteurCheck")

        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10,40,57,16))
        self.label.setObjectName("label")

        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(10,70,46,14))
        self.label_2.setObjectName("label_2")

        self.operatorHauteur = QtGui.QComboBox(self.groupBox)
        self.operatorHauteur.setGeometry(QtCore.QRect(80,40,151,22))
        self.operatorHauteur.setObjectName("operatorHauteur")

        self.valHauteur = QtGui.QLineEdit(self.groupBox)
        self.valHauteur.setGeometry(QtCore.QRect(80,70,113,20))
        self.valHauteur.setObjectName("valHauteur")

        self.groupBox_2 = QtGui.QGroupBox(self.Value)
        self.groupBox_2.setGeometry(QtCore.QRect(10,120,241,101))
        self.groupBox_2.setObjectName("groupBox_2")

        self.aireCheck = QtGui.QCheckBox(self.groupBox_2)
        self.aireCheck.setGeometry(QtCore.QRect(10,20,70,19))
        self.aireCheck.setObjectName("aireCheck")

        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(10,40,57,16))
        self.label_3.setObjectName("label_3")

        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setGeometry(QtCore.QRect(10,70,46,14))
        self.label_4.setObjectName("label_4")

        self.operatorAire = QtGui.QComboBox(self.groupBox_2)
        self.operatorAire.setGeometry(QtCore.QRect(80,40,151,22))
        self.operatorAire.setObjectName("operatorAire")

        self.valAire = QtGui.QLineEdit(self.groupBox_2)
        self.valAire.setGeometry(QtCore.QRect(80,70,113,20))
        self.valAire.setObjectName("valAire")
        self.wTab.addTab(self.Value,"")

        self.Option = QtGui.QWidget()
        self.Option.setObjectName("Option")

        self.FlatRoof = QtGui.QCheckBox(self.Option)
        self.FlatRoof.setGeometry(QtCore.QRect(10,10,111,19))
        self.FlatRoof.setObjectName("FlatRoof")
        self.wTab.addTab(self.Option,"")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.label_5 = QtGui.QLabel(self.tab)
        self.label_5.setGeometry(QtCore.QRect(10,20,121,16))
        self.label_5.setObjectName("label_5")

        self.selectionnerCouleur = QtGui.QPushButton(self.tab)
        self.selectionnerCouleur.setGeometry(QtCore.QRect(130,20,81,26))
        self.selectionnerCouleur.setObjectName("selectionnerCouleur")

        self.showSelectColor = QtGui.QLabel(self.tab)
        self.showSelectColor.setGeometry(QtCore.QRect(40,80,161,41))

        font = QtGui.QFont()
        font.setPointSize(20)
        self.showSelectColor.setFont(font)
        self.showSelectColor.setObjectName("showSelectColor")
        self.wTab.addTab(self.tab,"")

        self.retranslateUi(ModifBuildClass)
        self.wTab.setCurrentIndex(2)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),ModifBuildClass.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),ModifBuildClass.reject)
        QtCore.QMetaObject.connectSlotsByName(ModifBuildClass)

    def retranslateUi(self, ModifBuildClass):
        ModifBuildClass.setWindowTitle(QtGui.QApplication.translate("ModifBuildClass", "modifer building class", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ModifBuildClass", "Hauteur", None, QtGui.QApplication.UnicodeUTF8))
        self.hauteurCheck.setText(QtGui.QApplication.translate("ModifBuildClass", "Actif", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ModifBuildClass", "Operateur :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ModifBuildClass", "Valeur :", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("ModifBuildClass", "Aire", None, QtGui.QApplication.UnicodeUTF8))
        self.aireCheck.setText(QtGui.QApplication.translate("ModifBuildClass", "Actif", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ModifBuildClass", "Operateur :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ModifBuildClass", "Valeur :", None, QtGui.QApplication.UnicodeUTF8))
        self.wTab.setTabText(self.wTab.indexOf(self.Value), QtGui.QApplication.translate("ModifBuildClass", "Valeur", None, QtGui.QApplication.UnicodeUTF8))
        self.FlatRoof.setText(QtGui.QApplication.translate("ModifBuildClass", "BOOL--FLAT-ROOF", None, QtGui.QApplication.UnicodeUTF8))
        self.wTab.setTabText(self.wTab.indexOf(self.Option), QtGui.QApplication.translate("ModifBuildClass", "Option", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ModifBuildClass", "Selectionner la couleur :", None, QtGui.QApplication.UnicodeUTF8))
        self.selectionnerCouleur.setText(QtGui.QApplication.translate("ModifBuildClass", "Selectionner", None, QtGui.QApplication.UnicodeUTF8))
        self.showSelectColor.setText(QtGui.QApplication.translate("ModifBuildClass", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.wTab.setTabText(self.wTab.indexOf(self.tab), QtGui.QApplication.translate("ModifBuildClass", "Couleur", None, QtGui.QApplication.UnicodeUTF8))

