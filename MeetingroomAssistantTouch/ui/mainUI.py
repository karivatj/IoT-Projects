#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stackedWidget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from lib.faderwidget import StackedWidget

class OverflowLabel(QtWidgets.QLabel):
    def paintEvent( self, event ):
        painter = QtGui.QPainter(self)
        metrics = QtGui.QFontMetrics(self.font())
        elided  = metrics.elidedText(self.text(), QtCore.Qt.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)

class Ui_stackedUI(object):
    def setupUi(self, stackedUI):
        stackedUI.setObjectName("stackedUI")
        stackedUI.resize(320, 480)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(stackedUI.sizePolicy().hasHeightForWidth())
        stackedUI.setSizePolicy(sizePolicy)
        stackedUI.setMinimumSize(QtCore.QSize(320, 480))
        stackedUI.setMaximumSize(QtCore.QSize(320, 480))

        self.centralwidget = QtWidgets.QWidget(stackedUI)
        self.centralwidget.setObjectName("centralwidget")
        self.centralVerticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.centralVerticalLayout.setObjectName("centralLayout")
        self.centralVerticalLayout.setContentsMargins(0,0,0,0)

        ###################
        # central stack that handles changing the background and all the layouts
        ###################
        self.centralstack = StackedWidget()
        self.centralstack.setObjectName("centralStack")

        self.stack1 = QtWidgets.QStackedWidget()
        self.stack1.setObjectName("stack1") # for "free" layouts
        self.stack2 = QtWidgets.QStackedWidget()
        self.stack2.setObjectName("stack2") # for "reserved" layouts
        self.stack3 = QtWidgets.QStackedWidget()
        self.stack3.setObjectName("stack3") # for settings layouts

        ###################
        # page 1 of "green layout"
        ###################
        self.green_page1 = QtWidgets.QWidget()
        self.green_page1_VerticalLayout = QtWidgets.QVBoxLayout(self.green_page1)

        self.green_lblState_Page1 = QtWidgets.QLabel(self.green_page1)
        self.green_lblState_Page1.setAlignment(QtCore.Qt.AlignCenter)
        self.green_lblState_Page1.setMinimumHeight(80)
        self.green_lblNext_Page1 = QtWidgets.QLabel(self.green_page1)
        self.green_lblNext_Page1.setAlignment(QtCore.Qt.AlignCenter)
        self.green_lblNext_Page1.setMinimumHeight(20)
        self.green_lblNext_Page1.setObjectName("green_lblNext_Page1")
        self.green_lblSubject_Page1 = OverflowLabel(self.green_page1)
        self.green_lblSubject_Page1.setAlignment(QtCore.Qt.AlignCenter)
        self.green_lblSubject_Page1.setMinimumHeight(30)
        self.green_lblDuration_Page1 = QtWidgets.QLabel(self.green_page1)
        self.green_lblDuration_Page1.setAlignment(QtCore.Qt.AlignCenter)
        self.green_lblSubject_Page1.setMinimumHeight(30)

        self.green_btnPage1 = QtWidgets.QPushButton(self.green_page1)
        self.green_btnPage1.setObjectName("green_btnPage1")
        self.green_btnPage1.setMinimumSize(QtCore.QSize(200, 200))

        green_spacer1_page1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        green_spacer2_page1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        self.green_page1_VerticalLayout.addWidget(self.green_lblState_Page1)
        self.green_page1_VerticalLayout.addItem(green_spacer1_page1)
        self.green_page1_VerticalLayout.addWidget(self.green_btnPage1, 0, QtCore.Qt.AlignHCenter)
        self.green_page1_VerticalLayout.addItem(green_spacer2_page1)
        self.green_page1_VerticalLayout.addWidget(self.green_lblNext_Page1)
        self.green_page1_VerticalLayout.addWidget(self.green_lblSubject_Page1)
        self.green_page1_VerticalLayout.addWidget(self.green_lblDuration_Page1)

        self.stack1.addWidget(self.green_page1)

        ###################
        # page 2 of "green layout"
        ###################
        self.green_page2 = QtWidgets.QWidget()
        self.green_page2_VerticalLayout = QtWidgets.QVBoxLayout(self.green_page2)

        self.green_lblState_Page2 = QtWidgets.QLabel(self.green_page2)
        self.green_lblState_Page2.setAlignment(QtCore.Qt.AlignCenter)
        self.green_lblState_Page2.setMinimumHeight(80)

        self.green_dialPage2 = QtWidgets.QDial(self.green_page2)
        self.green_dialPage2.setObjectName("green_dialPage2")
        self.green_dialPage2.setNotchesVisible(True)
        self.green_dialPage2.setMinimum(3)
        self.green_dialPage2.setMaximum(24)
        self.green_dialPage2.setMinimumSize(QtCore.QSize(220, 220))

        self.green_lblPlaceholder = QtWidgets.QLabel(self.green_page2)
        self.green_lblPlaceholder.setAlignment(QtCore.Qt.AlignCenter)
        self.green_lblPlaceholder.setObjectName("green_lblPlaceholder")

        green_spacer1_page1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        green_spacer2_page1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        # layout containing X and Checkmark buttons
        self.green_page2_HorizontalLayout = QtWidgets.QHBoxLayout()

        self.green_btnDecline = QtWidgets.QPushButton(self.green_page2)
        self.green_btnDecline.setObjectName("green_btnDecline")
        self.green_btnDecline.setMinimumSize(QtCore.QSize(80, 80))
        self.green_btnDecline.setMaximumSize(QtCore.QSize(80, 80))

        self.green_lblDuration_Page2 = QtWidgets.QLabel(self.green_page2)
        self.green_lblDuration_Page2.setAlignment(QtCore.Qt.AlignCenter)
        self.green_lblDuration_Page2.setObjectName("green_lblDuration_Page2")
        self.green_lblDuration_Page2.setMinimumHeight(80)

        #green_spacer1_page2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.green_btnAccept = QtWidgets.QPushButton(self.green_page2)
        self.green_btnAccept.setObjectName("green_btnAccept")
        self.green_btnAccept.setMinimumSize(QtCore.QSize(80, 80))
        self.green_btnAccept.setMaximumSize(QtCore.QSize(80, 80))

        self.green_page2_HorizontalLayout.addWidget(self.green_btnDecline)
        self.green_page2_HorizontalLayout.addWidget(self.green_lblDuration_Page2)
        self.green_page2_HorizontalLayout.addWidget(self.green_btnAccept)
        # end

        self.green_page2_VerticalLayout.addWidget(self.green_lblState_Page2)
        self.green_page2_VerticalLayout.addItem(green_spacer1_page1)
        self.green_page2_VerticalLayout.addWidget(self.green_dialPage2, 0, QtCore.Qt.AlignHCenter)
        self.green_page2_VerticalLayout.addItem(green_spacer2_page1)
        self.green_page2_VerticalLayout.addWidget(self.green_lblPlaceholder)
        self.green_page2_VerticalLayout.addLayout(self.green_page2_HorizontalLayout)

        self.stack1.addWidget(self.green_page2)

        ###################
        # page 1 of "red layout"
        ###################
        self.red_page1 = QtWidgets.QWidget()
        self.red_page1_VerticalLayout = QtWidgets.QVBoxLayout(self.red_page1)

        self.red_lblState_Page1 = QtWidgets.QLabel(self.red_page1)
        self.red_lblState_Page1.setAlignment(QtCore.Qt.AlignCenter)
        self.red_lblState_Page1.setMinimumHeight(80)
        self.red_lblNext_Page1 = QtWidgets.QLabel(self.red_page1)
        self.red_lblNext_Page1.setAlignment(QtCore.Qt.AlignCenter)
        self.red_lblNext_Page1.setMinimumHeight(20)
        self.red_lblNext_Page1.setObjectName("red_lblNext_Page1")
        self.red_lblSubject_Page1 = OverflowLabel(self.red_page1)
        self.red_lblSubject_Page1.setAlignment(QtCore.Qt.AlignCenter)
        self.red_lblSubject_Page1.setMinimumHeight(30)
        self.red_lblDuration_Page1 = QtWidgets.QLabel(self.red_page1)
        self.red_lblDuration_Page1.setAlignment(QtCore.Qt.AlignCenter)
        self.red_lblDuration_Page1.setMinimumHeight(30)

        self.red_btnPage1 = QtWidgets.QPushButton(self.red_page1)
        self.red_btnPage1.setObjectName("red_btnPage1")
        self.red_btnPage1.setMinimumSize(QtCore.QSize(200, 200))

        red_spacer1_page1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        red_spacer2_page1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        self.red_page1_VerticalLayout.addWidget(self.red_lblState_Page1)
        self.red_page1_VerticalLayout.addItem(red_spacer1_page1)
        self.red_page1_VerticalLayout.addWidget(self.red_btnPage1, 0, QtCore.Qt.AlignHCenter)
        self.red_page1_VerticalLayout.addItem(red_spacer2_page1)
        self.red_page1_VerticalLayout.addWidget(self.red_lblNext_Page1)
        self.red_page1_VerticalLayout.addWidget(self.red_lblSubject_Page1)
        self.red_page1_VerticalLayout.addWidget(self.red_lblDuration_Page1)

        self.stack2.addWidget(self.red_page1)

        ###################
        # page 2 of "red layout"
        ###################
        self.red_page2 = QtWidgets.QWidget()
        self.red_page2_VerticalLayout = QtWidgets.QVBoxLayout(self.red_page2)

        self.red_lblState_Page2 = QtWidgets.QLabel(self.red_page2)
        self.red_lblState_Page2.setAlignment(QtCore.Qt.AlignCenter)
        self.red_lblState_Page2.setMinimumHeight(80)

        self.red_lblNext_Page2 = QtWidgets.QLabel(self.red_page2)
        self.red_lblNext_Page2.setAlignment(QtCore.Qt.AlignCenter)
        self.red_lblNext_Page2.setObjectName("red_lblNext_Page2")
        self.red_lblNext_Page2.setMinimumHeight(20)

        self.red_btnPage2 = QtWidgets.QPushButton(self.red_page2)
        self.red_btnPage2.setObjectName("red_btnPage2")
        self.red_btnPage2.setMinimumSize(QtCore.QSize(200, 200))

        self.red_btnCancel = QtWidgets.QPushButton(self.red_page2)
        self.red_btnCancel.setObjectName("red_btnCancel")
        self.red_btnCancel.setMinimumSize(QtCore.QSize(220, 70))

        red_spacer1_page1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        red_spacer2_page1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        self.red_page2_VerticalLayout.addWidget(self.red_lblState_Page2)
        self.red_page2_VerticalLayout.addItem(red_spacer1_page1)
        self.red_page2_VerticalLayout.addWidget(self.red_btnPage2, 0, QtCore.Qt.AlignHCenter)
        self.red_page2_VerticalLayout.addItem(red_spacer2_page1)
        self.red_page2_VerticalLayout.addWidget(self.red_lblNext_Page2)
        self.red_page2_VerticalLayout.addWidget(self.red_btnCancel, 0, QtCore.Qt.AlignHCenter)

        self.stack2.addWidget(self.red_page2)

        ###################
        # page 1 of "settings layout"
        ###################
        self.settings_page1 = QtWidgets.QWidget()
        self.settings_page1_VerticalLayout = QtWidgets.QVBoxLayout(self.settings_page1)

        self.settings_layout1 = QtWidgets.QHBoxLayout()
        self.btnSettings1_Previous = QtWidgets.QPushButton(self.settings_page1)
        self.btnSettings1_Previous.setEnabled(False)
        self.btnSettings1_Previous.setMaximumSize(QtCore.QSize(35, 16777215))
        self.btnSettings1_Previous.setObjectName("btnSettings1_Previous")
        self.lblSettings_Page1 = QtWidgets.QLabel(self.settings_page1)
        self.lblSettings_Page1.setStyleSheet("")
        self.lblSettings_Page1.setAlignment(QtCore.Qt.AlignCenter)
        self.lblSettings_Page1.setObjectName("lblSettings_Page1")
        self.btnSettings1_Next = QtWidgets.QPushButton(self.settings_page1)
        self.btnSettings1_Next.setEnabled(True)
        self.btnSettings1_Next.setMaximumSize(QtCore.QSize(35, 16777215))
        self.btnSettings1_Next.setObjectName("btnSettings1_Next")
        self.settings_layout1.addWidget(self.btnSettings1_Previous)
        self.settings_layout1.addWidget(self.lblSettings_Page1)
        self.settings_layout1.addWidget(self.btnSettings1_Next)

        self.lblMeetingroom = QtWidgets.QLabel(self.settings_page1)
        self.lblMeetingroom.setObjectName("lblMeetingroom")
        self.txtMeetingroom = QtWidgets.QLineEdit(self.settings_page1)
        self.txtMeetingroom.setMinimumSize(QtCore.QSize(0, 35))
        self.txtMeetingroom.setMaximumSize(QtCore.QSize(16777215, 35))
        self.txtMeetingroom.setObjectName("txtMeetingroom")
        self.lblMeetingroomEmail = QtWidgets.QLabel(self.settings_page1)
        self.lblMeetingroomEmail.setObjectName("lblMeetingroomEmail")
        self.txtMeetingroomEmail = QtWidgets.QLineEdit(self.settings_page1)
        self.txtMeetingroomEmail.setMinimumSize(QtCore.QSize(0, 35))
        self.txtMeetingroomEmail.setMaximumSize(QtCore.QSize(16777215, 35))
        self.txtMeetingroomEmail.setObjectName("txtMeetingroomEmail")
        self.lblServer = QtWidgets.QLabel(self.settings_page1)
        self.lblServer.setObjectName("lblServer")
        self.txtServer = QtWidgets.QLineEdit(self.settings_page1)
        self.txtServer.setMinimumSize(QtCore.QSize(0, 35))
        self.txtServer.setMaximumSize(QtCore.QSize(16777215, 35))
        self.txtServer.setObjectName("txtServer")
        self.lblCredentials = QtWidgets.QLabel(self.settings_page1)
        self.lblCredentials.setObjectName("lblCredentials")

        self.username_layout = QtWidgets.QHBoxLayout()
        self.lblUsername = QtWidgets.QLabel(self.settings_page1)
        self.lblUsername.setMinimumSize(QtCore.QSize(80, 35))
        self.lblUsername.setMaximumSize(QtCore.QSize(80, 35))
        self.lblUsername.setObjectName("lblUsername")
        self.lineUsername = QtWidgets.QLineEdit(self.settings_page1)
        self.lineUsername.setMinimumSize(QtCore.QSize(0, 35))
        self.lineUsername.setMaximumSize(QtCore.QSize(16777215, 35))
        self.lineUsername.setObjectName("lineUsername")
        self.username_layout.addWidget(self.lblUsername)
        self.username_layout.addWidget(self.lineUsername)

        self.password_layout = QtWidgets.QHBoxLayout()
        self.lblPassword = QtWidgets.QLabel(self.settings_page1)
        self.lblPassword.setMinimumSize(QtCore.QSize(80, 35))
        self.lblPassword.setMaximumSize(QtCore.QSize(80, 35))
        self.lblPassword.setObjectName("lblPassword")
        self.linePassword = QtWidgets.QLineEdit(self.settings_page1)
        self.linePassword.setMinimumSize(QtCore.QSize(0, 35))
        self.linePassword.setMaximumSize(QtCore.QSize(16777215, 35))
        self.linePassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.linePassword.setObjectName("linePassword")
        self.password_layout.addWidget(self.lblPassword)
        self.password_layout.addWidget(self.linePassword)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        self.label = QtWidgets.QLabel(self.settings_page1)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.buttonBox = QtWidgets.QDialogButtonBox(self.settings_page1)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("settings_buttonBox")

        self.settings_page1_VerticalLayout.addLayout(self.settings_layout1)
        self.settings_page1_VerticalLayout.addWidget(self.lblMeetingroom)
        self.settings_page1_VerticalLayout.addWidget(self.txtMeetingroom)
        self.settings_page1_VerticalLayout.addWidget(self.lblMeetingroomEmail)
        self.settings_page1_VerticalLayout.addWidget(self.txtMeetingroomEmail)
        self.settings_page1_VerticalLayout.addWidget(self.lblServer)
        self.settings_page1_VerticalLayout.addWidget(self.txtServer)
        self.settings_page1_VerticalLayout.addWidget(self.lblCredentials)
        self.settings_page1_VerticalLayout.addLayout(self.username_layout)
        self.settings_page1_VerticalLayout.addLayout(self.password_layout)
        self.settings_page1_VerticalLayout.addItem(spacerItem)
        self.settings_page1_VerticalLayout.addWidget(self.label)
        self.settings_page1_VerticalLayout.addWidget(self.buttonBox)

        self.stack3.addWidget(self.settings_page1)

        ###################
        # page 2 of "settings layout"
        ###################
        self.settings_page2 = QtWidgets.QWidget()
        self.settings_page2_VerticalLayout = QtWidgets.QVBoxLayout(self.settings_page2)

        self.settings_layout2 = QtWidgets.QHBoxLayout()
        self.btnSettings2_Previous = QtWidgets.QPushButton(self.settings_page2)
        self.btnSettings2_Previous.setEnabled(True)
        self.btnSettings2_Previous.setMaximumSize(QtCore.QSize(35, 16777215))
        self.btnSettings2_Previous.setObjectName("btnSettings2_Previous")
        self.lblSettings_Page2 = QtWidgets.QLabel(self.settings_page2)
        self.lblSettings_Page2.setAlignment(QtCore.Qt.AlignCenter)
        self.lblSettings_Page2.setObjectName("lblSettings_Page2")
        self.btnSettings2_Next = QtWidgets.QPushButton(self.settings_page2)
        self.btnSettings2_Next.setEnabled(False)
        self.btnSettings2_Next.setMaximumSize(QtCore.QSize(35, 16777215))
        self.btnSettings2_Next.setObjectName("btnSettings2_Next")
        self.settings_layout2.addWidget(self.btnSettings2_Previous)
        self.settings_layout2.addWidget(self.lblSettings_Page2)
        self.settings_layout2.addWidget(self.btnSettings2_Next)

        self.lblLogOutput = QtWidgets.QLabel(self.settings_page2)
        self.lblLogOutput.setObjectName("lblLogOutput")
        self.txtLogOutput = QtWidgets.QPlainTextEdit(self.settings_page2)
        self.txtLogOutput.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.txtLogOutput.setObjectName("txtLogOutput")
        self.lblOther = QtWidgets.QLabel(self.settings_page2)
        self.lblOther.setAlignment(QtCore.Qt.AlignCenter)
        self.lblOther.setObjectName("lblOther")
        self.btnExit = QtWidgets.QPushButton(self.settings_page2)
        self.btnExit.setObjectName("btnExit")

        self.settings_page2_VerticalLayout.addLayout(self.settings_layout2)
        self.settings_page2_VerticalLayout.addWidget(self.lblLogOutput)
        self.settings_page2_VerticalLayout.addWidget(self.txtLogOutput)
        self.settings_page2_VerticalLayout.addWidget(self.lblOther)
        self.settings_page2_VerticalLayout.addWidget(self.btnExit)

        self.stack3.addWidget(self.settings_page2)

        stackStyle = "QWidget#stack1{border-image:url(:backgrounds/green.png)} \
        QWidget#stack2{border-image:url(:backgrounds/red.png)} \
        QWidget#stack3{border-image:url(:backgrounds/grey.png)} \
        QLabel,QLabel#green_lblDuration_Page2{color:#fff;font:75 20pt \"Bebas Neue Bold\"} \
        QLabel#green_lblNext_Page1,QLabel#green_lblPlaceholder,QLabel#red_lblNext_Page1,QLabel#red_lblNext_Page2{color:#fff;font:75 12pt \"Bebas Neue Bold\"} \
        QPushButton#green_btnDecline{border-image:url(:/images/button_cross.png)} \
        QPushButton#green_btnDecline:pressed{border-image:url(:/images/button_cross_inverted.png)} \
        QPushButton#green_btnAccept{border-image:url(:/images/button_checkmark.png)} \
        QPushButton#green_btnAccept:pressed{border-image:url(:/images/button_checkmark_inverted.png)} \
        QPushButton#green_btnPage1,QPushButton#red_btnPage1,QPushButton#red_btnPage2{border-image:url(:/images/button.png);color:#fff;font:75 20pt \"Bebas Neue Bold\"} \
        QPushButton#green_btnPage1:pressed,QPushButton#red_btnPage1:pressed,QPushButton#red_btnPage2:pressed{border-image:url(:/images/button_inverted.png);color:#fff;font:75 20pt \"Bebas Neue Bold\"} \
        QPushButton#red_btnCancel{border-image:url(:/images/rounded_button.png);color:#fff;font:75 18pt \"Bebas Neue Bold\"} \
        QPushButton#red_btnCancel:pressed{border-image:url(:/images/rounded_button_inverted.png);color:#fff;font:75 18pt \"Bebas Neue Bold\"} \
        QDial#green_dialPage2{background-color:#fff;color:#fff}"

        settingsStyle = "QLineEdit,QPlainTextEdit,QTextEdit { \
                            background-color: rgba(0,0,0,20%); \
                            color:#fff \
                        } \
                        QDialog { \
                            border-image:url(:/backgrounds/grey.png) \
                        } \
                        #lblSettings_Page1,#lblSettings_Page2 { \
                            color:#fff; \
                            font:75 20pt \"Bebas Neue Bold\" \
                        } \
                        QLabel { \
                            color:#fff; \
                            font:75 12pt \"Bebas Neue Regular\" \
                        } \
                        QPlainTextEdit { \
                            font:75 6pt \"Seqoe UI\"; \
                        } \
                        QLineEdit,QTextEdit { \
                            font:75 8pt \"Seqoe UI\" \
                        }"


        self.centralwidget.setStyleSheet(stackStyle);
        self.settings_page1.setStyleSheet(settingsStyle)
        self.settings_page2.setStyleSheet(settingsStyle)

        # populate centralwidget
        self.centralVerticalLayout.addWidget(self.centralstack)
        self.centralstack.addWidget(self.stack1)
        self.centralstack.addWidget(self.stack2)
        self.centralstack.addWidget(self.stack3)

        stackedUI.setCentralWidget(self.centralwidget)

        self.retranslateUi(stackedUI)
        self.centralstack.setCurrentIndex(0)
        self.stack1.setCurrentIndex(0)
        self.stack2.setCurrentIndex(0)
        self.stack3.setCurrentIndex(0)

        QtCore.QMetaObject.connectSlotsByName(stackedUI)

    def retranslateUi(self, stackedUI):
        _translate = QtCore.QCoreApplication.translate
        stackedUI.setWindowTitle(_translate("stackedUI", "Dialog"))

        self.green_lblState_Page1.setText(_translate("stackedUI", "Haetaan\nVarauksia"))
        self.green_lblNext_Page1.setText(_translate("stackedUI", "Seuraava varaus"))
        self.green_lblSubject_Page1.setText(_translate("stackedUI", "Haetaan varauksia"))
        self.green_lblDuration_Page1.setText(_translate("stackedUI", "00:00 - 00:00"))
        self.green_btnPage1.setText(_translate("stackedUI", "Varaa"))

        self.green_lblState_Page2.setText(_translate("stackedUI", "Varaa Tila"))
        self.green_lblDuration_Page2.setText(_translate("stackedUI", ""))
        self.green_lblPlaceholder.setText(_translate("stackedUI", "     "))

        self.red_lblState_Page1.setText(_translate("stackedUI", "Varattu"))
        self.red_lblNext_Page1.setText(_translate("stackedUI", "Tämän hetkinen varaus"))
        self.red_lblSubject_Page1.setText(_translate("stackedUI", "Haetaan varauksia"))
        self.red_lblDuration_Page1.setText(_translate("stackedUI", "00:00 - 00:00"))
        self.red_btnPage1.setText(_translate("stackedUI", "Lisää"))

        self.red_lblState_Page2.setText(_translate("stackedUI", "Varaustiedot"))
        self.red_lblNext_Page2.setText(_translate("stackedUI", "Lisäasetukset"))
        self.red_btnPage2.setText(_translate("stackedUI", "Takaisin"))
        self.red_btnCancel.setText(_translate("stackedUI", "Keskeytä Varaus"))

        # settings page 1:
        self.btnSettings1_Previous.setText(_translate("stackedUI", "<-"))
        self.lblSettings_Page1.setText(_translate("stackedUI", "Asetukset 1/2"))
        self.btnSettings1_Next.setText(_translate("stackedUI", "->"))
        self.lblMeetingroom.setText(_translate("stackedUI", "Neuvotteluhuoneen nimi"))
        self.lblMeetingroomEmail.setText(_translate("stackedUI", "Neuvotteluhuoneen email"))
        self.lblServer.setText(_translate("stackedUI", "Palvelimen osoite"))
        self.lblCredentials.setText(_translate("stackedUI", "Tunnukset:"))
        self.lblUsername.setText(_translate("stackedUI", "Username:"))
        self.lblPassword.setText(_translate("stackedUI", "Password:"))
        self.label.setText(_translate("stackedUI", "Tallenna muutokset"))

        # settings page 2:
        self.btnSettings2_Previous.setText(_translate("settings_page2", "<-"))
        self.lblSettings_Page2.setText(_translate("settings_page2", "Asetukset 2/2"))
        self.btnSettings2_Next.setText(_translate("settings_page2", "->"))
        self.lblLogOutput.setText(_translate("settings_page2", "Loki"))
        self.lblOther.setText(_translate("settings_page2", "Muuta"))
        self.btnExit.setText(_translate("settings_page2", "Poistu ohjelmasta"))
