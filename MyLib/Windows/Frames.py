from PyQt5.QtWidgets import QStyle
from PyQt5 import QtCore
from MyLib.Windows.Drilling_run import Drilling
from MyLib.Windows.Spo_run import Spo
from MyLib.LibClass import Md
from MyLib.Windows import FramelessWindow as Fr
from MyLib import LibClass
from MyLib import Variables as Gl


class FrameDrilling(Fr.FramelessWindow, Md):
    def __init__(self, parent=None):
        super().__init__()
        self.mainWin = parent
        self.init_main_frame()

    def init_main_frame(self):

        self.set_value()

        # Добавляем виджет Drilling
        self.setWidget(Drilling(frame=self, parent=self.mainWin))

        # Инициализируем QSystemTrayIcon
        self.trayIcon = LibClass.TrayIcon(self, False, style="drill")

        # EventFilter на все окно
        self.installEventFilter(self)

    def set_value(self):
        # Поверх всех окон
        # noinspection PyTypeChecker
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)

        # Прозрачность окна
        self.setWindowOpacity(0.67)

        # Скрываем верхнею панель
        self.titleBar.setVisible(False)

        self.set_size()

        self.set_my_style()

    def closeEvent(self, event):

        if self.mainWin.groupBox_deepControl.isChecked():
            event.ignore()
            self.hide()
            print('Виджет бурения hide')
        else:
            self.trayIcon.exit()
            self.mainWin.win_drilling = None
            print('Виджет бурения close')
        Gl.md['Размер_окна_бурения'] = [self.geometry().left(), self.geometry().top(), self.size().width(), self.size().height()]
        self.safe_setting()

    def eventFilter(self, source, event):

        if source.objectName() == 'win_drilling':

            if event.type() == QtCore.QEvent.Resize:
                Gl.md['Размер_окна_бурения'] = [self.geometry().left(), self.geometry().top(), self.size().width(), self.size().height()]

            if event.type() == QtCore.QEvent.Enter:
                self.unsetCursor()
                self.titleBar.setVisible(True)
                self.setGeometry(self.geometry().left(), self.geometry().top(), self.size().width(),
                                 Gl.md['Размер_окна_бурения'][3] + self.titleBar.size().height())

            if event.type() == QtCore.QEvent.Leave:
                self.unsetCursor()
                self.titleBar.setVisible(False)
                self.setGeometry(self.geometry().left(), self.geometry().top(), self.size().width(),
                                 Gl.md['Размер_окна_бурения'][3] - self.titleBar.size().height())

        return False

    def set_size(self):
        self.setMaximumHeight(140)
        self.setMinimumHeight(80)

        self.setTitleBarHeight(15)
        self.titleBar.buttonClose.setMinimumWidth(50)
        self.titleBar.buttonMinimum.hide()
        self.titleBar.buttonMaximum.hide()

        self.setGeometry(Gl.md['Размер_окна_бурения'][0], Gl.md['Размер_окна_бурения'][1], Gl.md['Размер_окна_бурения'][2], Gl.md['Размер_окна_бурения'][3])

    def set_my_style(self):
        pass


class FrameSpo(Fr.FramelessWindow, Md):
    def __init__(self, parent=None):
        super().__init__()
        self.mainWin = parent
        self.init_main_frame()

    def init_main_frame(self):

        self.set_value()

        # Добавляем виджет Spo
        self.setWidget(Spo(frame=self, parent=self.mainWin))

        # Инициализируем QSystemTrayIcon
        self.trayIcon = LibClass.TrayIcon(self, False, style="up_arrow")

        # EventFilter на все окно
        self.installEventFilter(self)

    def set_value(self):
        # Поверх всех окон
        # noinspection PyTypeChecker
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)

        # Прозрачность окна
        self.setWindowOpacity(0.67)

        # Скрываем верхнею панель
        self.titleBar.setVisible(False)

        self.set_size()

    def closeEvent(self, event):

        if self.mainWin.groupBox_deepControl.isChecked():
            event.ignore()
            self.hide()
            print('Виджет СПО hide')
        else:
            self.trayIcon.exit()
            self.mainWin.win_spo = None
            print('Виджет СПО close')
        Gl.md['Размер_окна_СПО'] = [self.geometry().left(), self.geometry().top(), self.size().width(), self.size().height()]
        self.safe_setting()

    def eventFilter(self, source, event):

        if source.objectName() == 'win_spo':
            if event.type() == QtCore.QEvent.Resize:
                Gl.md['Размер_окна_СПО'] = [self.geometry().left(), self.geometry().top(), self.size().width(), self.size().height()]

            if event.type() == QtCore.QEvent.Enter:
                self.unsetCursor()
                self.titleBar.setVisible(True)
                self.setGeometry(self.geometry().left(), self.geometry().top(), self.size().width(),
                                 Gl.md['Размер_окна_СПО'][3] + self.titleBar.size().height())

            if event.type() == QtCore.QEvent.Leave:
                self.unsetCursor()
                self.titleBar.setVisible(False)
                self.setGeometry(self.geometry().left(), self.geometry().top(), self.size().width(),
                                 Gl.md['Размер_окна_СПО'][3] - self.titleBar.size().height())

        return False

    def set_size(self):
        self.setMaximumHeight(140)
        self.setMinimumHeight(80)

        self.setTitleBarHeight(15)
        self.titleBar.buttonClose.setMinimumWidth(50)
        self.titleBar.buttonMinimum.hide()
        self.titleBar.buttonMaximum.hide()

        self.setGeometry(Gl.md['Размер_окна_СПО'][0], Gl.md['Размер_окна_СПО'][1], Gl.md['Размер_окна_СПО'][2], Gl.md['Размер_окна_СПО'][3])
