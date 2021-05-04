from MyLib.LibClass import Md
from MyLib.Windows.My_pyqt5 import Spo_win
from PyQt5.QtWidgets import QWidget
import MyLib.Variables as Gl


class Spo(QWidget, Spo_win.Ui_Spo_win):
    def __init__(self, frame=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.mainWindow = parent
        self.fr = frame
        self.init_spo()

    def init_spo(self):

        # Запускаем дополнительный поток
        self.mainWindow.Commun.data_change_spo.connect(self.data_change_spo)

    def closeEvent(self, event):
        Gl.md['Размер_окна_СПО'] = [self.size().width(), self.size().height()]
        if self.mainWindow.groupBox_6.isChecked() and self.mainWindow.groupBox_5.isChecked():
            event.ignore()
            self.hide()
            print('Виджет СПО hide')
        else:
            self.trayIcon.exit()
            self.mainWindow.win_spo = None
            print('Виджет СПО close')
        Md.safe_setting()

    def data_change_spo(self, data):

        if data['down']:
            self.label_direction.setText('Спущено')
            self.label_direction_left.setText('Осталось\nспустить')
            self.lineEdit_pipe.setText(str(data['Спущено'][0]))
            self.lineEdit_candle.setText(str(data['Спущено'][1]))
            self.lineEdit_pipes_left.setText(str(data['Осталось'][0]))
            self.lineEdit_candles_left.setText(str(data['Осталось'][1]))
        else:
            self.label_direction.setText('Поднято')
            self.label_direction_left.setText('Осталось\nподнять')
            self.lineEdit_pipe.setText(str(data['Поднято'][0]))
            self.lineEdit_candle.setText(str(data['Поднято'][1]))
            self.lineEdit_pipes_left.setText(str(data['Осталось'][0]))
            self.lineEdit_candles_left.setText(str(data['Осталось'][1]))

        # Активация фокуса окна
        self.fr.raise_()

        # Прогресс бар
        self.progressBar.setValue(data['Прогресс'])
