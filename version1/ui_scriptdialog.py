# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QPushButton, QSizePolicy,
    QTextEdit, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(1455, 663)
        self.editor = QTextEdit(Dialog)
        self.editor.setObjectName(u"editor")
        self.editor.setGeometry(QRect(10, 50, 881, 591))
        self.load_button = QPushButton(Dialog)
        self.load_button.setObjectName(u"load_button")
        self.load_button.setGeometry(QRect(10, 10, 83, 29))
        self.save_button = QPushButton(Dialog)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setGeometry(QRect(110, 10, 83, 29))
        self.run_button = QPushButton(Dialog)
        self.run_button.setObjectName(u"run_button")
        self.run_button.setGeometry(QRect(840, 60, 41, 31))
        font = QFont()
        font.setPointSize(14)
        self.run_button.setFont(font)
        self.output_display = QTextEdit(Dialog)
        self.output_display.setObjectName(u"output_display")
        self.output_display.setGeometry(QRect(910, 50, 531, 591))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.load_button.setText(QCoreApplication.translate("Dialog", u"Load", None))
        self.save_button.setText(QCoreApplication.translate("Dialog", u"Save", None))
        self.run_button.setText(QCoreApplication.translate("Dialog", u"\u25b6\ufe0f", None))
    # retranslateUi

