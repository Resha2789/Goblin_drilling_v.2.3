import sys
import re
import struct
from MyLib import Variables as Gl
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QSystemTrayIcon, QStyle
from PyQt5.QtCore import QObject, pyqtSignal
from MyLib.Windows.My_pyqt5 import Main_win
from MyLib.Windows import Frames
from MyLib.MainThread import MainThreading
from MyLib.LibClass import Md, OutLogger, OutputLogger, FindOffset, ReadAddress
from MyLib import LibClass


class Communicate(QObject):
    dataChange_mainWindow: pyqtSignal = QtCore.pyqtSignal(object)
    data_change_drilling = QtCore.pyqtSignal(object)
    data_change_spo = QtCore.pyqtSignal(object)
    dataChange_progressBar = QtCore.pyqtSignal(object)


class MainWindow(QWidget, Md, FindOffset, OutLogger, OutputLogger, ReadAddress, Main_win.Ui_Main_win):
    def __init__(self):
        super().__init__()

        self.initMainWindow()

    def initMainWindow(self):
        self.setupUi(self)
        self.mainWindow = self

        # Инициализируем эксземпляр класса Md
        self.init_setting()

        # Инициализируем эксземпляр класса FindOffset
        self.init_find_offset()

        # Инициализируем эксземпляр класса ReadAddress
        self.init_read_address()

        # Инициализируем эксземпляр класса Ram
        self.init_ram()

        # Поверх всех окон
        # noinspection PyTypeChecker
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # Объект Communicate
        self.Commun = Communicate()

        # Виджет бурение
        self.win_drilling = None

        # Виджет СПО
        self.win_spo = None

        # Инициализируем QSystemTrayIcon
        self.trayIcon = LibClass.TrayIcon(self, True, QStyle.SP_MessageBoxWarning)

        # Запрещаем вывод сообщений в консоль главного окна
        self.startLog = False

        self.original_style = self.styleSheet()

        self.set_value()

        self.set_connect()

    def set_value(self):
        # Инициализация статуса программы
        self.status_of_start = False

        # Размеры главного окна
        self.resize(Gl.md['Размер_главное_окно'][0], Gl.md['Размер_главное_окно'][1])

        # Максимальная_разница_глубины
        self.doubleSpinBox_maxDiffirent.setValue(Gl.md['Макс_раз_гл'])

        # Выбор файла (inpgti)
        self.pushButton_1.setText(f"Папка скважины: {Gl.md['Директория_inp_gti']}")

        # Выбор файла (registr_nbl_extended)
        self.pushButton_2.setText(f"Папка регистр: {Gl.md['Директория_registr']}")

        # Выбор файла (Слежение за глубиной)
        self.pushButton_salectFile.setText(f"Файл слеж. за гл.: {Gl.md['Директория_меры_инстр']}")

        # L до АКБ
        self.doubleSpinBox_L_AKB.setValue(Gl.md['L_до_АКБ'])

        # Труб в свече
        self.spinBox_piples_in_candel.setValue(Gl.md['Труб_в_свече'])

        # Последняя труба
        self.spinBox_last_piple.setValue(Gl.md['Последняя_труба'])

        # Количество труб до подъема
        self.spinBox_piples_befor_up.setValue(Gl.md['Кол_труб_до_подъема'])

        # Труб в свече
        self.spinBox_step_setNotes.setValue(Gl.md['Шаг_уст_заметок'])

        # Устанавливаем адреса
        self.setOffset()

        # Вес на роторе
        self.doubleSpinBox_rotor.setValue(Gl.md['Вес_ротор'])

        # Вес на слайд
        self.doubleSpinBox_slaid.setValue(Gl.md['Вес_слайд'])

        # Изменение веса на слайде
        self.checkBox_slaid_weight.setCheckState(QtCore.Qt.Checked) if Gl.md['Изменения_веса_слайд'] == True \
            else self.checkBox_slaid_weight.setCheckState(QtCore.Qt.Unchecked)

        # Глубина над забоем для нагрузки
        self.doubleSpinBox_depLoad.setValue(Gl.md['Гл_для_нагрузки'])

    def set_connect(self):

        # Конектим пользовательский сигнал на mainWindow
        self.Commun.dataChange_mainWindow.connect(self.dataChange_mainWindow)
        self.Commun.dataChange_progressBar.connect(self.dataChange_progressBar)

        # СТАРТ программы
        self.pushButton_Start.clicked.connect(self.start)

        # Контроль глубины
        self.groupBox_deepControl.clicked.connect(self.depth_control)

        # Запуск виджета Бурение
        self.pushButton_drilling.clicked.connect(self.show_drilling_window)

        # Запуск Виджета СПО
        self.pushButton_spo.clicked.connect(self.show_SPO_window)

        # Максимальная_разница_глубины
        self.doubleSpinBox_maxDiffirent.valueChanged.connect(self.max_difference_depth)

        # Разрешаем установку заметок
        self.groupBox_spo_notes.clicked.connect(self.check_box_set_notes)

        # Пойск адреса забоя
        self.pushButton_findOffsetBottomHole.clicked.connect(self.findOffsetBottomHole)

        # Пойск адреса глубины инструмента
        self.pushButton_findOffsetDepth.clicked.connect(self.findOffsetDepth)

        # Пойск адреса высоты тальблока
        self.pushButton_findOffsetHoistBlock.clicked.connect(self.findOffsetHoistBlock)

        # Пойск адреса Число эл. в скважине
        self.pushButton_findOffsetItemCandel.clicked.connect(self.findOffsetItemCandel)

        # Изменение забоя (проверка адреса)
        self.pushButton_checkOffsetBottomHole.clicked.connect(self.checkOffsetBottomHole)

        # Изменение глубины инструмента (проверка адреса)
        self.pushButton_checkOffsetDepth.clicked.connect(self.checkOffsetDepth)

        # Изменение высоты тальблока (проверка адреса)
        self.pushButton_checkOffsetHoistBlock.clicked.connect(self.checkOffsetHoistBlock)

        # Выбор файла (inpgti)
        self.pushButton_1.clicked.connect(self.browse_folder_inpgti)

        # Выбор файла (registr_nbl_extended)
        self.pushButton_2.clicked.connect(self.browse_folder_registr_nbl_extended)

        # Выбор файла (Слежение за глубиной)
        self.pushButton_salectFile.clicked.connect(self.browse_folder_salectFile)

        # Активация фрейма для поиска адресов в RAM
        self.groupBox_findOffsetOfRAM.clicked.connect(self.findOffsetOfRAM)

        # L до АКБ
        self.doubleSpinBox_L_AKB.valueChanged.connect(self.L_AKB)

        # Последняя труба
        self.spinBox_last_piple.valueChanged.connect(self.last_piple)

        # Труб в свече
        self.spinBox_piples_in_candel.valueChanged.connect(self.piples_in_candel)

        # Количество труб до подъема
        self.spinBox_piples_befor_up.valueChanged.connect(self.piples_befor_up)

        # Обновление меры инструмента
        self.pushButton_updata_tools.clicked.connect(self.updata_tools)

        # Труб в свече
        self.spinBox_step_setNotes.valueChanged.connect(self.step_setNotes)

        # Изменение веса на слайде
        self.checkBox_slaid_weight.clicked.connect(self.slaid_weight)

        # Глубина над забоем для нагрузки
        self.doubleSpinBox_depLoad.valueChanged.connect(self.dep_load)

        # Вывод сообщений в консоль
        self.OUTPUT_LOGGER_STDOUT.emit_write.connect(self.append_log)
        self.OUTPUT_LOGGER_STDERR.emit_write.connect(self.append_log)

    def dataChange_mainWindow(self, value):
        self.lineEdit_bottomHole.setText(f"{Gl.md['Забой']}")
        self.lineEdit_depth.setText(f"{Gl.md['Гл_инстр']}")
        self.lineEdit_3.setText(f"{Gl.md['Спущено_свеч']}")
        self.lineEdit_4.setText(f"{Gl.md['Спущено_труб']}")
        self.lineEdit_5.setText(f"{Gl.md['Поднято_свеч']}")
        self.lineEdit_6.setText(f"{Gl.md['Поднято_труб']}")

    def start(self):
        if self.get_pid() is None:
            self.groupBox_deepControl.setChecked(QtCore.Qt.Unchecked)
            return

        if not self.status_of_start:
            self.status_of_start = True
            self.connect()

            style = """#pushButton_Start
            {background-color: rgb(0, 255, 0);}
            """
            self.pushButton_Start.setText('STOP')
            self.setStyleSheet(self.original_style + style)
        else:
            self.status_of_start = False
            self.disconnect()
            style = """#pushButton_Start
                        {background-color: rgb(255, 0, 0);}
                        """
            self.pushButton_Start.setText('START')
            self.setStyleSheet(self.original_style + style)

    def connect(self):
        self.startLog = True  # Разришаем вывод сообщений в консоль главного окна
        self.mainThreading = MainThreading(parent=self)  # Запускаем дополнительный поток
        self.groupBox_deepControl.setEnabled(True)  # Активируем groupBox_deepControl
        self.groupBox_findOffsetOfRAM.setEnabled(False)  # Диактивируем groupBox_findOffsetOfRAM для поиска адреса в RAM
        self.groupBox_findOffsetOfRAM.setChecked(QtCore.Qt.Unchecked)
        self.pushButton_updata_tools.setEnabled(True)  # Активируем кнопку обновленя промера

    def disconnect(self):
        self.startLog = False  # Диактивируем вывод сообщений в консоль главного окна
        self.groupBox_deepControl.setChecked(QtCore.Qt.Unchecked)
        self.groupBox_deepControl.setEnabled(False)  # Активируем groupBox_deepControl
        self.groupBox_findOffsetOfRAM.setEnabled(True)  # Активируем groupBox_findOffsetOfRAM для поиска адреса в RAM
        self.pushButton_updata_tools.setEnabled(False)  # Диактивируем кнопку обновленя промера

    def depth_control(self):

        if self.groupBox_deepControl.isChecked():
            if self.get_pid() is None:
                self.groupBox_deepControl.setChecked(QtCore.Qt.Unchecked)
                return

            # Разришаем вывод сообщений в консоль главного окна
            # self.startLog = True

            # Запускаем дополнительный поток
            # self.mainThreading = MainThreading(parent=self)
            self.mainThreading.start()

            self.pushButton_drilling.setEnabled(True)  # pushButton_drilling активирует кнопку запуска виджета бурения
            self.groupBox_spo_notes.setEnabled(True)  # groupBox_spo_notes для СПО активируем

            print(f"Контроль глубины запущен!")

        else:
            print(f"Контроль глубины остановлен!")
            self.groupBox_spo_notes.setEnabled(False)
            self.pushButton_drilling.setEnabled(False)
            self.pushButton_spo.setEnabled(False)

            # Закрыаем виджаты
            if self.win_drilling:
                self.win_drilling.close()

            if self.win_spo:
                self.win_spo.close()
            self.close_md()

    def show_drilling_window(self):
        if not self.win_drilling:
            print('Запустили win_drilling')
            self.win_drilling = Frames.FrameDrilling(parent=self)
            self.win_drilling.setObjectName('win_drilling')
            self.win_drilling.show()
        elif self.win_drilling.isHidden():
            print('Показали win_drilling')
            self.win_drilling.setVisible(True)
        elif self.win_drilling.isMinimized():
            print('Развернули win_drilling')
            self.win_drilling.showNormal()

    def show_SPO_window(self):
        if not self.win_spo:
            print('Запустили win_spo')
            self.win_spo = Frames.FrameSpo(parent=self)
            self.win_spo.setObjectName('win_spo')
            self.win_spo.show()
        elif self.win_spo.isHidden():
            print('Показали win_spo')
            self.win_spo.setVisible(True)
        elif self.win_spo.isMinimized():
            print('Развернуть win_spo')
            self.win_spo.showNormal()

    def max_difference_depth(self, value):
        Gl.md['Макс_раз_гл'] = value

    def exit_action(self):
        print('Закрытие через трей')
        self.minimize.setCheckState(QtCore.Qt.Unchecked)
        self.groupBox_deepControl.setChecked(QtCore.Qt.Unchecked)
        self.close()

    def closeEvent(self, event):
        Gl.md['Размер_главное_окно'] = [self.size().width(), self.size().height()]

        if self.minimize.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage("Tray Program", "Плагин скрыт в трей", QSystemTrayIcon.Information, 2000)

        else:
            self.groupBox_deepControl.setChecked(QtCore.Qt.Unchecked)
            self.groupBox_spo_notes.setChecked(QtCore.Qt.Unchecked)
            # write_inp_gti('глубина_для_нагрузки=\d+[.,]*\d', str(md['Глубина_для_нагрузки']))
            if self.win_drilling:
                self.win_drilling.close()

            if self.win_spo:
                self.win_spo.close()

            self.close_md()
            self.close()
            self.deleteLater()
            self.trayIcon.exit()
            print('Главное окно close')

    def check_box_set_notes(self):

        if self.groupBox_spo_notes.isChecked():
            self.pushButton_spo.setEnabled(True)
            self.init_spo()
        else:
            self.pushButton_spo.setEnabled(False)
            if self.win_spo:
                self.win_spo.close()

    def browse_folder_inpgti(self):

        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку скважины")
        # открыть диалог выбора директории и установить значение переменной
        if directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            self.pushButton_1.setText(f"Папка скважины: {directory}/inpgti.ini")
            Gl.md['Директория_inp_gti'] = f"{directory}/inpgti.ini"
            Gl.md['Директория_заметки'] = f"{directory}/Заметки.rem"

    def browse_folder_registr_nbl_extended(self):

        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку registr")
        # открыть диалог выбора директории и установить значение переменной
        if directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            self.pushButton_2.setText(f"Папка скважины: {directory}/registr.nbl.extended")
            Gl.md['Директория_registr'] = f"{directory}/registr.nbl.extended"

    def browse_folder_salectFile(self):

        directory = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите файл: Cлежения за глубиной")
        print(directory[0])
        # открыть диалог выбора директории и установить значение переменной
        if directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            self.pushButton_salectFile.setText(f"Файл слеж. за гл.: {directory[0]}")
            Gl.md['Директория_меры_инстр'] = directory[0]
            Gl.md['Название_файла_меры_инстр'] = re.sub(r'.*[/]+', '', directory[0])
            self.safe_setting()

    def append_log(self, text, severity):
        pass
        if self.startLog == True:
            if severity == self.Severity.ERROR:
                self.textBrowser.append('<b>{}</b>'.format(text))
                if self.groupBox_deepControl.isChecked():
                    self.groupBox_deepControl.setChecked(QtCore.Qt.Unchecked)
                    self.depth_control()

            else:
                self.textBrowser.append('<small>{}</small>'.format(text))

    def dataChange_progressBar(self, data):  # Вызывается для обработки сигнала

        if Gl.data_progressBar != data['temp']:
            Gl.data_progressBar = data['temp']
            self.progressBar.setFormat("%p% " + data['temp'])
            procent = (100 / (len(data['Карта_памяти']) / (data['i'] + 1)))
            self.progressBar.setValue(int(procent))

    def findOffsetBottomHole(self):
        self.find_offset(self.spinBox_findOffsetBottomHole, self.spinBox_checkOffsetBottomHole, my_structure='<d')

    def findOffsetDepth(self):
        self.find_offset(self.spinBox_findOffsetDepth, self.spinBox_checkOffsetDepth, my_structure='<d')

    def findOffsetHoistBlock(self):
        self.find_offset(self.spinBox_findOffsetHoistBlock, self.spinBox_checkOffsetHoistBlock, my_structure='<d')

    def findOffsetItemCandel(self):
        self.find_offset(self.spinBox_findOffsetItemCandel, self.spinBox_checkOffsetItemCandel, my_structure='<I', total_bytes=4)

    def checkOffsetBottomHole(self):
        Gl.md['Адреса'].update({'Забой': self.spinBox_checkOffsetBottomHole.value()})
        Gl.md['Offset_забой'] = self.spinBox_checkOffsetBottomHole.value() - Gl.md['Блок_памяти']['НастРег'][0]
        self.write_process_memory(Gl.md['Адреса']['Забой'], struct.pack('<d', self.spinBox_findOffsetBottomHole.value()), buffer_size=8)
        print(f"{Gl.md['Адреса']['Забой']}  {self.spinBox_findOffsetBottomHole.value()}")

        Gl.md['Адреса'].update({'Гл_инстр': Gl.md['Адреса']['Забой'] + 8})
        Gl.md['Offset_глубина_инструмента'] = Gl.md['Адреса']['Гл_инстр'] - Gl.md['Блок_памяти']['НастРег'][0]
        self.spinBox_checkOffsetDepth.setValue(Gl.md['Адреса']['Гл_инстр'])

        self.safe_setting()

    def checkOffsetDepth(self):
        Gl.md['Адреса'].update({'Гл_инстр': self.spinBox_checkOffsetDepth.value()})
        Gl.md['Offset_глубина_инструмента'] = self.spinBox_checkOffsetDepth.value() - Gl.md['Блок_памяти']['НастРег'][0]
        self.write_process_memory(Gl.md['Адреса']['Гл_инстр'], struct.pack('<d', self.spinBox_findOffsetDepth.value()), buffer_size=8)
        print(f"{Gl.md['Адреса']['Гл_инстр']}  {self.spinBox_findOffsetDepth.value()}")

        Gl.md['Адреса'].update({'Забой': Gl.md['Адреса']['Гл_инстр'] - 8})
        Gl.md['Offset_забой'] = Gl.md['Адреса']['Забой'] - Gl.md['Блок_памяти']['НастРег'][0]
        self.spinBox_checkOffsetBottomHole.setValue(Gl.md['Адреса']['Забой'])

        self.safe_setting()

    def checkOffsetHoistBlock(self):
        Gl.md['Адреса'].update({'Высота_таль': self.spinBox_checkOffsetHoistBlock.value()})
        Gl.md['Offset_тальблок'] = self.spinBox_checkOffsetHoistBlock.value() - Gl.md['Блок_памяти']['НастРег'][0]
        self.write_process_memory(Gl.md['Адреса']['Высота_таль'], struct.pack('<d', self.spinBox_findOffsetHoistBlock.value()), buffer_size=8)
        print(f"{Gl.md['Адреса']['Высота_таль']}  {self.spinBox_findOffsetHoistBlock.value()}")

        self.safe_setting()

    def checkOffsetItemCandel(self):
        Gl.md['Адреса'].update({'Cпущ_элем': self.spinBox_checkOffsetItemCandel.value()})
        Gl.md['Offset_Количество_элементов'] = self.spinBox_checkOffsetItemCandel.value() - Gl.md['Блок_памяти']['НастРег'][0]
        self.write_process_memory(Gl.md['Адреса']['Cпущ_элем'], struct.pack('<I', self.spinBox_findOffsetItemCandel.value()), buffer_size=4)
        print(f"{Gl.md['Адреса']['Cпущ_элем']}  {self.spinBox_findOffsetItemCandel.value()}")

        self.safe_setting()

    def setOffset(self):
        # Адреса в RAM (глубина забоя)
        self.spinBox_checkOffsetBottomHole.setValue(Gl.md['Offset_забой'] + Gl.md['Блок_памяти']['НастРег'][0])

        # Адреса в RAM (глубина инструмента)
        self.spinBox_checkOffsetDepth.setValue(Gl.md['Offset_глубина_инструмента'] + Gl.md['Блок_памяти']['НастРег'][0])

        # Адреса в RAM (высоты тальблока)
        self.spinBox_checkOffsetHoistBlock.setValue(Gl.md['Offset_тальблок'] + Gl.md['Блок_памяти']['НастРег'][0])

        # Адреса в RAM (колличества спущенных элементов)
        self.spinBox_checkOffsetItemCandel.setValue(Gl.md['Offset_Количество_элементов'] + Gl.md['Блок_памяти']['НастРег'][0])

    def findOffsetOfRAM(self):
        if self.groupBox_findOffsetOfRAM.isChecked():
            # Разришаем вывод сообщений в консоль главного окна
            self.startLog = True
            if not self.readAddress:
                # Считываем адреса по настройк в RAM и их значения
                self.read_address()

    def L_AKB(self, value):
        Gl.md['L_до_АКБ'] = value

    def last_piple(self, value):
        Gl.md['Последняя_труба'] = value

    def init_spo(self):

        # Спущено все элементов
        self.spinBox_all_itemTool.setValue(Gl.md['Cпущ_элем'])

        # Считываем настройки для заметок
        self.notes_spo = {
            'down': [
                [self.spinBox_item_down_1, self.spinBox_piple_down_1, self.lineEdit_text_down_1],
                [self.spinBox_item_down_2, self.spinBox_piple_down_2, self.lineEdit_text_down_2],
                [self.spinBox_item_down_3, self.spinBox_piple_down_3, self.lineEdit_text_down_3]
            ],

            'up': [
                [self.spinBox_item_up_1, self.spinBox_piple_up_1, self.lineEdit_text_up_1],
                [self.spinBox_item_up_2, self.spinBox_piple_up_2, self.lineEdit_text_up_2],
                [self.spinBox_item_up_3, self.spinBox_piple_up_3, self.lineEdit_text_up_3]
            ]
        }

        for i in self.notes_spo:
            for j in range(len(self.notes_spo[i])):
                for ij in range(len(self.notes_spo[i][j])):

                    if type(self.notes_spo[i][j][ij]) == type(self.spinBox_item_down_1):
                        self.notes_spo[i][j][ij].setValue(Gl.md['Заметки_спо'][i][j][ij])
                        self.notes_spo[i][j][ij].valueChanged.connect(self.notes_change_spo)
                    else:
                        self.notes_spo[i][j][ij].setText(Gl.md['Заметки_спо'][i][j][ij])
                        self.notes_spo[i][j][ij].textChanged.connect(self.notes_change_spo)

        self.notes_change_spo()

    def notes_change_spo(self):
        # print(f"{self.sender().objectName()}")
        # print(f"{self.sender().value()}")

        x = self.sender()
        if x.objectName() == 'spinBox_piple_up_1':
            self.spinBox_item_up_1.setValue(self.mainThreading.item_tool + 1)
        if x.objectName() == 'spinBox_piple_up_2':
            self.spinBox_item_up_2.setValue(self.mainThreading.item_tool + 1)
        if x.objectName() == 'spinBox_piple_up_3':
            self.spinBox_item_up_3.setValue(self.mainThreading.item_tool + 1)
        if x.objectName() == 'spinBox_piple_down_1':
            self.spinBox_item_down_1.setValue(self.mainThreading.item_tool)
        if x.objectName() == 'spinBox_piple_down_2':
            self.spinBox_item_down_2.setValue(self.mainThreading.item_tool)
        if x.objectName() == 'spinBox_piple_down_3':
            self.spinBox_item_down_3.setValue(self.mainThreading.item_tool)

        if self.spinBox_piple_down_2.value() > 0:
            self.spinBox_item_down_2.setMinimum(self.spinBox_item_down_1.value() + 1)
        else:
            self.spinBox_item_down_2.setMinimum(0)
            self.spinBox_item_down_2.setValue(0)

        if self.spinBox_piple_down_3.value() > 0:
            self.spinBox_item_down_3.setMinimum(self.spinBox_item_down_2.value() + 1)
        else:
            self.spinBox_item_down_3.setMinimum(0)
            self.spinBox_item_down_3.setValue(0)

        if self.spinBox_piple_up_2.value() > 0:
            self.spinBox_item_up_2.setMaximum(self.spinBox_item_up_1.value() - 1)
        else:
            self.spinBox_item_up_2.setMaximum(999)
            self.spinBox_item_up_2.setValue(0)

        if self.spinBox_piple_up_3.value() > 0:
            self.spinBox_item_up_3.setMaximum(self.spinBox_item_up_2.value() - 1)
        else:
            self.spinBox_item_up_3.setMaximum(999)
            self.spinBox_item_up_3.setValue(0)

        Gl.md['Заметки_спо'] = \
            {
                'up': [
                    [self.spinBox_item_up_1.value(), self.spinBox_piple_up_1.value(), self.lineEdit_text_up_1.text()],
                    [self.spinBox_item_up_2.value(), self.spinBox_piple_up_2.value(), self.lineEdit_text_up_2.text()],
                    [self.spinBox_item_up_3.value(), self.spinBox_piple_up_3.value(), self.lineEdit_text_up_3.text()]
                ],
                'down': [
                    [self.spinBox_item_down_1.value(), self.spinBox_piple_down_1.value(), self.lineEdit_text_down_1.text()],
                    [self.spinBox_item_down_2.value(), self.spinBox_piple_down_2.value(), self.lineEdit_text_down_2.text()],
                    [self.spinBox_item_down_3.value(), self.spinBox_piple_down_3.value(), self.lineEdit_text_down_3.text()]
                ]
            }

    def piples_in_candel(self, value):
        Gl.md['Труб_в_свече'] = value

    def updata_tools(self):
        if not self.mainThreading.read_tools():
            pass

    def piples_befor_up(self, value):
        # Количество труб до подъема
        Gl.md['Кол_труб_до_подъема'] = value

    def step_setNotes(self, value):
        Gl.md['Шаг_уст_заметок'] = value

    def slaid_weight(self):
        Gl.md['Изменения_веса_слайд'] = True if self.checkBox_slaid_weight.isChecked() else False

        if self.win_drilling:
            if self.checkBox_slaid_weight.isChecked():
                self.win_drilling.findChild(QObject, 'pushButton_slaid').setEnabled(True)
                self.win_drilling.findChild(QObject, 'doubleSpinBox_slaid').setEnabled(True)
                self.win_drilling.findChild(QObject, 'drill_doubleSpinBox_4').setEnabled(True)

            else:
                self.win_drilling.findChild(QObject, 'pushButton_slaid').setEnabled(False)
                self.win_drilling.findChild(QObject, 'doubleSpinBox_slaid').setEnabled(False)
                self.win_drilling.findChild(QObject, 'drill_doubleSpinBox_4').setEnabled(False)

    def dep_load(self, value):
        Gl.md['Гл_для_нагрузки'] = value


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    w = MainWindow()
    w.show()  # Показываем окно
    sys.exit(app.exec())  # Запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
