# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uiFile/untitled.ui'
#
# Created: Wed May 14 17:05:20 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DiagMain(object):
    def setupUi(self, DiagMain):
        DiagMain.setObjectName("DiagMain")
        DiagMain.resize(QtCore.QSize(QtCore.QRect(0,0,325,157).size()).expandedTo(DiagMain.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(DiagMain)
        self.buttonBox.setGeometry(QtCore.QRect(-30,120,341,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.layerComboBox = QtGui.QComboBox(DiagMain)
        self.layerComboBox.setEnabled(True)
        self.layerComboBox.setGeometry(QtCore.QRect(70,10,241,22))
        self.layerComboBox.setEditable(False)
        self.layerComboBox.setObjectName("layerComboBox")

        self.label = QtGui.QLabel(DiagMain)
        self.label.setGeometry(QtCore.QRect(10,10,55,16))
        self.label.setObjectName("label")

        self.label_2 = QtGui.QLabel(DiagMain)
        self.label_2.setGeometry(QtCore.QRect(10,40,55,16))
        self.label_2.setObjectName("label_2")

        self.comboBox = QtGui.QComboBox(DiagMain)
        self.comboBox.setGeometry(QtCore.QRect(70,40,241,22))
        self.comboBox.setObjectName("comboBox")

        self.ajouter = QtGui.QPushButton(DiagMain)
        self.ajouter.setGeometry(QtCore.QRect(100,70,77,26))
        self.ajouter.setObjectName("ajouter")

        self.modifer = QtGui.QPushButton(DiagMain)
        self.modifer.setGeometry(QtCore.QRect(20,70,77,26))
        self.modifer.setObjectName("modifer")

        self.appliquer = QtGui.QPushButton(DiagMain)
        self.appliquer.setGeometry(QtCore.QRect(180,70,91,26))
        self.appliquer.setObjectName("appliquer")

        self.retranslateUi(DiagMain)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),DiagMain.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),DiagMain.reject)
        QtCore.QMetaObject.connectSlotsByName(DiagMain)

    def retranslateUi(self, DiagMain):
        DiagMain.setWindowTitle(QtGui.QApplication.translate("DiagMain", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("DiagMain", "Nom layer :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("DiagMain", "Build class :", None, QtGui.QApplication.UnicodeUTF8))
        self.ajouter.setText(QtGui.QApplication.translate("DiagMain", "Ajouter", None, QtGui.QApplication.UnicodeUTF8))
        self.modifer.setText(QtGui.QApplication.translate("DiagMain", "Modifer", None, QtGui.QApplication.UnicodeUTF8))
        self.appliquer.setText(QtGui.QApplication.translate("DiagMain", "Appliquer les bc", None, QtGui.QApplication.UnicodeUTF8))

