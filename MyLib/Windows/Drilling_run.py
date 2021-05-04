from MyLib.Windows.My_pyqt5 import Drilling_win
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore
from MyLib import Variables as Gl
from MyLib.Windows import FramelessWindow as Fr


class Drilling(QWidget, Drilling_win.Ui_Drilling_win):
    def __init__(self, frame=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.mainWindow = parent
        self.fr = frame
        self.init_drilling()

    def init_drilling(self):

        # Запускаем дополнительный поток
        self.mainWindow.Commun.data_change_drilling.connect(self.data_change_drilling)

        self.set_event_filter()

        self.set_value()

        self.set_connect()

    def set_value(self):

        # Вес на роторе
        self.doubleSpinBox_rotor.setValue(Gl.md['Вес_ротор'])

        # Вес на слайд
        self.weight_slaid()

    def set_connect(self):

        # Вес на роторе
        self.pushButton_rotor.clicked.connect(self.set_weight)

        # Вес на слайд
        self.pushButton_slaid.clicked.connect(self.set_weight)

    def set_event_filter(self):

        # EventFilter на виджет Drilling
        self.installEventFilter(self)

        # Вес на роторе
        self.doubleSpinBox_rotor.installEventFilter(self)

        # Вес на слайд
        self.doubleSpinBox_slaid.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Enter:
            # print('Enter')
            pass

        if event.type() == QtCore.QEvent.Leave:
            # print('Leave')
            pass

        # Вес на роторе
        if source.objectName() == self.doubleSpinBox_rotor.objectName():
            if event.type() == QtCore.QEvent.KeyPress and (event.key() == 16777220 or event.key() == 16777221):
                Gl.md['Вес_ротор'] = self.doubleSpinBox_rotor.value()
                self.doubleSpinBox_rotor.clearFocus()

        # Вес на слайд
        if source.objectName() == self.doubleSpinBox_slaid.objectName():
            if event.type() == QtCore.QEvent.KeyPress and (event.key() == 16777220 or event.key() == 16777221):
                Gl.md['Вес_слайд'] = self.doubleSpinBox_slaid.value()
                self.doubleSpinBox_slaid.clearFocus()

        return False

    def data_change_drilling(self, data):
        self.lineEdit_plan_depth.setText(str(Gl.md['до_бурил']))
        self.lineEdit_left_drilling.setText(str(Gl.md['Осталось_бурить']))
        self.lineEdit_total_candle.setText(str(Gl.md['Спущено_свеч']))

        # Прогресс бар
        self.progressBar.setValue(data['Прогресс'])

        self.set_my_style(data['Ротор'])

        # Активация фокуса окна
        self.fr.raise_()
        # self.fr.activateWindow()

        if not self.doubleSpinBox_rotor.hasFocus():
            self.doubleSpinBox_rotor.lineEdit().setCursorPosition(0)

        if not self.doubleSpinBox_slaid.hasFocus():
            self.doubleSpinBox_slaid.lineEdit().setCursorPosition(0)

    def set_weight(self):
        sender = self.sender()

        # Вес ротор
        if sender.objectName() == self.pushButton_rotor.objectName():
            self.doubleSpinBox_rotor.setValue(Gl.pr['вес_на_крюке'])
            Gl.md['Вес_ротор'] = Gl.pr['вес_на_крюке']
            print(f"Вес_ротор  {Gl.md['Вес_ротор']}")

        # Вес слайд
        if sender.objectName() == self.pushButton_slaid.objectName():
            self.doubleSpinBox_slaid.setValue(Gl.pr['вес_на_крюке'])
            Gl.md['Вес_слайд'] = Gl.pr['вес_на_крюке']
            print(f"Вес_слайд  {Gl.md['Вес_слайд']}")

    def weight_slaid(self):
        if self.mainWindow.checkBox_slaid_weight.isChecked():
            self.pushButton_slaid.setEnabled(True)
            self.doubleSpinBox_slaid.setEnabled(True)
            self.drill_doubleSpinBox_4.setEnabled(True)
            self.doubleSpinBox_slaid.setValue(Gl.md['Вес_слайд'])
        else:
            self.pushButton_slaid.setEnabled(False)
            self.doubleSpinBox_slaid.setEnabled(False)
            self.drill_doubleSpinBox_4.setEnabled(False)
            self.doubleSpinBox_slaid.setValue(0)

    def set_my_style(self, data):

        style = ""

        if data:
            style = """
					#doubleSpinBox_rotor
					{
						background-color: rgb(0, 255, 0);
					}
					#doubleSpinBox_slaid
					{
						background-color: rgb(255, 255, 255);
					}
					"""

        if not data and data is not None:
            style = """
					#doubleSpinBox_rotor
					{
						background-color: rgb(255, 255, 255);
					}
					#doubleSpinBox_slaid
					{
						background-color: rgb(0, 255, 0);
					}
					"""

        Fr.STYLE_SHEET = Fr.STYLE_SHEET + style
        self.setStyleSheet(Fr.STYLE_SHEET)
