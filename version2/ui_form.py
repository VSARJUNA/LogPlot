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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QListView, QPlainTextEdit, QPushButton, QSizePolicy,
    QTabWidget, QTextBrowser, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(1541, 870)
        self.GraphTab = QTabWidget(Widget)
        self.GraphTab.setObjectName(u"GraphTab")
        self.GraphTab.setGeometry(QRect(10, 100, 1511, 731))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.TextArea = QTextBrowser(self.tab)
        self.TextArea.setObjectName(u"TextArea")
        self.TextArea.setGeometry(QRect(10, 10, 1491, 691))
        self.GraphTab.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.GraphsListView = QListView(self.tab_2)
        self.GraphsListView.setObjectName(u"GraphsListView")
        self.GraphsListView.setGeometry(QRect(10, 10, 1491, 671))
        self.GraphTab.addTab(self.tab_2, "")
        self.FiltersSearchBox = QLineEdit(Widget)
        self.FiltersSearchBox.setObjectName(u"FiltersSearchBox")
        self.FiltersSearchBox.setGeometry(QRect(10, 60, 421, 28))
        self.label = QLabel(Widget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(440, 59, 63, 31))
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.FilterInput = QPlainTextEdit(Widget)
        self.FilterInput.setObjectName(u"FilterInput")
        self.FilterInput.setGeometry(QRect(520, 60, 1001, 31))
        self.layoutWidget = QWidget(Widget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 20, 341, 41))
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.LoadButton = QPushButton(self.layoutWidget)
        self.LoadButton.setObjectName(u"LoadButton")

        self.horizontalLayout_2.addWidget(self.LoadButton)

        self.PlotButton = QPushButton(self.layoutWidget)
        self.PlotButton.setObjectName(u"PlotButton")

        self.horizontalLayout_2.addWidget(self.PlotButton)

        self.SaveButton = QPushButton(self.layoutWidget)
        self.SaveButton.setObjectName(u"SaveButton")

        self.horizontalLayout_2.addWidget(self.SaveButton)

        self.layoutWidget1 = QWidget(Widget)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(520, 20, 231, 41))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.FilterButton = QPushButton(self.layoutWidget1)
        self.FilterButton.setObjectName(u"FilterButton")

        self.horizontalLayout.addWidget(self.FilterButton)

        self.ClearFilter = QPushButton(self.layoutWidget1)
        self.ClearFilter.setObjectName(u"ClearFilter")

        self.horizontalLayout.addWidget(self.ClearFilter)

        self.label_2 = QLabel(Widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(770, 10, 51, 51))
        self.label_2.setPixmap(QPixmap(u"../../Downloads/load_image.png"))
        self.label_2.setScaledContents(True)

        self.retranslateUi(Widget)

        self.GraphTab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.TextArea.setPlaceholderText(QCoreApplication.translate("Widget", u"Uh No Data Loaded!!! :(", None))
        self.GraphTab.setTabText(self.GraphTab.indexOf(self.tab), QCoreApplication.translate("Widget", u"Data", None))
        self.GraphTab.setTabText(self.GraphTab.indexOf(self.tab_2), QCoreApplication.translate("Widget", u"Graphs", None))
        self.label.setText(QCoreApplication.translate("Widget", "🝖", None))
        self.LoadButton.setText(QCoreApplication.translate("Widget", "Load  📁", None))
        self.PlotButton.setText(QCoreApplication.translate("Widget", "Plot  📊", None))
        self.SaveButton.setText(QCoreApplication.translate("Widget", "Save  💾", None))
        self.FilterButton.setText(QCoreApplication.translate("Widget", "Apply Filters 🔍", None))
        self.ClearFilter.setText(QCoreApplication.translate("Widget", "Clear ❌", None))
        self.label_2.setText("")
    # retranslateUi

