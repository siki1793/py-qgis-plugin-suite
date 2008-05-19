# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FentreModif.ui'
#
# Created: Tue May 13 11:35:10 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_modifDialog(object):
    def setupUi(self, modifDialog):
        modifDialog.setObjectName("modifDialog")
        modifDialog.resize(QtCore.QSize(QtCore.QRect(0,0,216,112).size()).expandedTo(modifDialog.minimumSizeHint()))

        self.label = QtGui.QLabel(modifDialog)
        self.label.setGeometry(QtCore.QRect(10,10,46,14))
        self.label.setObjectName("label")

        self.comboBox = QtGui.QComboBox(modifDialog)
        self.comboBox.setGeometry(QtCore.QRect(60,10,151,22))
        self.comboBox.setObjectName("comboBox")

        self.label_2 = QtGui.QLabel(modifDialog)
        self.label_2.setGeometry(QtCore.QRect(10,40,46,14))
        self.label_2.setObjectName("label_2")

        self.lineEdit = QtGui.QLineEdit(modifDialog)
        self.lineEdit.setGeometry(QtCore.QRect(60,40,151,20))
        self.lineEdit.setObjectName("lineEdit")

        self.ok = QtGui.QPushButton(modifDialog)
        self.ok.setGeometry(QtCore.QRect(130,80,77,25))
        self.ok.setObjectName("ok")

        self.cancel = QtGui.QPushButton(modifDialog)
        self.cancel.setGeometry(QtCore.QRect(50,80,81,25))
        self.cancel.setObjectName("cancel")

        self.retranslateUi(modifDialog)
        QtCore.QObject.connect(self.cancel,QtCore.SIGNAL("clicked()"),modifDialog.reject)
        QtCore.QObject.connect(self.ok,QtCore.SIGNAL("clicked()"),modifDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(modifDialog)

    def retranslateUi(self, modifDialog):
        modifDialog.setWindowTitle(QtGui.QApplication.translate("modifDialog", "Modif attribut value", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("modifDialog", "Attribut :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("modifDialog", "Valeur :", None, QtGui.QApplication.UnicodeUTF8))
        self.ok.setText(QtGui.QApplication.translate("modifDialog", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel.setText(QtGui.QApplication.translate("modifDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

