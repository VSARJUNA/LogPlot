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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QListView, QPlainTextEdit,
    QProgressBar, QPushButton, QSizePolicy, QSlider,
    QTabWidget, QTableWidget, QTableWidgetItem, QTextBrowser,
    QTextEdit, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(1537, 754)
        self.DataRangeTab = QTabWidget(Widget)
        self.DataRangeTab.setObjectName(u"DataRangeTab")
        self.DataRangeTab.setGeometry(QRect(10, 100, 1521, 651))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.TextArea = QTextBrowser(self.tab)
        self.TextArea.setObjectName(u"TextArea")
        self.TextArea.setGeometry(QRect(10, 10, 1491, 591))
        self.DataRangeTab.addTab(self.tab, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.DatarangegraphicsView = QGraphicsView(self.tab_4)
        self.DatarangegraphicsView.setObjectName(u"DatarangegraphicsView")
        self.DatarangegraphicsView.setGeometry(QRect(340, 10, 1151, 551))
        self.RangeDataTextView = QTextEdit(self.tab_4)
        self.RangeDataTextView.setObjectName(u"RangeDataTextView")
        self.RangeDataTextView.setGeometry(QRect(10, 10, 321, 571))
        self.hslider2 = QSlider(self.tab_4)
        self.hslider2.setObjectName(u"hslider2")
        self.hslider2.setGeometry(QRect(340, 590, 1151, 18))
        self.hslider2.setOrientation(Qt.Orientation.Horizontal)
        self.hslider1 = QSlider(self.tab_4)
        self.hslider1.setObjectName(u"hslider1")
        self.hslider1.setGeometry(QRect(340, 570, 1151, 18))
        self.hslider1.setMaximum(100)
        self.hslider1.setSliderPosition(0)
        self.hslider1.setOrientation(Qt.Orientation.Horizontal)
        self.hslider1.setInvertedAppearance(True)
        self.hslider1.setInvertedControls(False)
        self.DataRangeTab.addTab(self.tab_4, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.GraphsListView = QListView(self.tab_2)
        self.GraphsListView.setObjectName(u"GraphsListView")
        self.GraphsListView.setGeometry(QRect(10, 10, 1491, 601))
        self.DataRangeTab.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.tableWidget = QTableWidget(self.tab_3)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(10, 10, 991, 601))
        self.ExportButton = QPushButton(self.tab_3)
        self.ExportButton.setObjectName(u"ExportButton")
        self.ExportButton.setGeometry(QRect(1120, 60, 91, 29))
        self.ScriptButton = QPushButton(self.tab_3)
        self.ScriptButton.setObjectName(u"ScriptButton")
        self.ScriptButton.setGeometry(QRect(1010, 60, 101, 29))
        self.AddColButton = QPushButton(self.tab_3)
        self.AddColButton.setObjectName(u"AddColButton")
        self.AddColButton.setGeometry(QRect(1010, 10, 101, 29))
        self.EditColButton = QPushButton(self.tab_3)
        self.EditColButton.setObjectName(u"EditColButton")
        self.EditColButton.setGeometry(QRect(1120, 10, 91, 29))
        self.DataRangeTab.addTab(self.tab_3, "")
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
        self.layoutWidget.setGeometry(QRect(10, 10, 421, 41))
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

        self.ThemeButton = QPushButton(self.layoutWidget)
        self.ThemeButton.setObjectName(u"ThemeButton")

        self.horizontalLayout_2.addWidget(self.ThemeButton)

        self.layoutWidget1 = QWidget(Widget)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(520, 10, 231, 41))
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
        self.progressBar = QProgressBar(Widget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(770, 20, 241, 23))
        self.progressBar.setValue(0)
        self.progressBarLabel = QLabel(Widget)
        self.progressBarLabel.setObjectName(u"progressBarLabel")
        self.progressBarLabel.setGeometry(QRect(1030, 20, 211, 20))

        self.retranslateUi(Widget)

        self.DataRangeTab.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.TextArea.setPlaceholderText(QCoreApplication.translate("Widget", u"Uh No Data Loaded!!! :(", None))
        self.DataRangeTab.setTabText(self.DataRangeTab.indexOf(self.tab), QCoreApplication.translate("Widget", u"Data", None))
        self.DataRangeTab.setTabText(self.DataRangeTab.indexOf(self.tab_4), QCoreApplication.translate("Widget", u"Data Range", None))
        self.DataRangeTab.setTabText(self.DataRangeTab.indexOf(self.tab_2), QCoreApplication.translate("Widget", u"Graphs", None))
        self.ExportButton.setText(QCoreApplication.translate("Widget", u"Export", None))
        self.ScriptButton.setText(QCoreApplication.translate("Widget", u"Script", None))
        self.AddColButton.setText(QCoreApplication.translate("Widget", u"Add Column", None))
        self.EditColButton.setText(QCoreApplication.translate("Widget", u"EditColumn", None))
        self.DataRangeTab.setTabText(self.DataRangeTab.indexOf(self.tab_3), QCoreApplication.translate("Widget", u"Tables", None))
        self.label.setText(QCoreApplication.translate("Widget", u"🝖", None))
        self.LoadButton.setText(QCoreApplication.translate("Widget", u"Load  📁", None))
        self.PlotButton.setText(QCoreApplication.translate("Widget", u"Plot  📊", None))
        self.SaveButton.setText(QCoreApplication.translate("Widget", u"Save  💾", None))
        self.FilterButton.setText(QCoreApplication.translate("Widget", u"Apply Filters 🔍", None))
        self.ClearFilter.setText(QCoreApplication.translate("Widget", u"Clear ❌", None))
        self.label_2.setText("")
        self.progressBarLabel.setText("")
    # retranslateUi

