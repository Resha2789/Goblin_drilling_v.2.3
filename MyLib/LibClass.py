from MyLib.RWMemory import Ram
from PyQt5.QtWidgets import QWidget, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from MyLib.Windows import MessageBox as Msg
from datetime import datetime
from MyLib import Variables as Gl
import datetime as date_time
import json
import time
import pythoncom
import win32com.client
import binascii
import sys
import re
import struct


class ExceptHook:
    def __init__(self):
        self.init_except_hook()

    def init_except_hook(self):
        import sys
        sys.excepthook = self.show_exception_and_exit

    @staticmethod
    def show_exception_and_exit(exc_type, exc_value, tb):
        import traceback
        traceback.print_exception(exc_type, exc_value, tb)
        input("Press key to exit.")
        sys.exit(-1)


class Communicate(QObject):
    dataChange_outputLogger = QtCore.pyqtSignal(str, int)


class OutputLogger:
    class Severity:
        DEBUG = 0
        ERROR = 1

    def __init__(self, io_stream, severity):
        super().__init__()
        self.Communicate = Communicate()
        self.emit_write = self.Communicate.dataChange_outputLogger
        self.io_stream = io_stream
        self.severity = severity

    def write(self, text):
        self.io_stream.write(text)
        self.emit_write.emit(text, self.severity)

    def flush(self):
        self.io_stream.flush()


class OutLogger:
    OUTPUT_LOGGER_STDOUT = OutputLogger(sys.stdout, OutputLogger.Severity.DEBUG)
    OUTPUT_LOGGER_STDERR = OutputLogger(sys.stderr, OutputLogger.Severity.ERROR)
    sys.stdout = OUTPUT_LOGGER_STDOUT
    sys.stderr = OUTPUT_LOGGER_STDERR


# Класс для сворачивания приложения в трее
class TrayIcon(QWidget):
    def __init__(self, parent=None, exit=False, style=None):
        super().__init__()
        self.window = parent

        # Объявим и добавим действия для работы с иконкой системного трея
        # show - показать окно
        # hide - скрыть окно
        # exit - выход из программы

        self.window.tray_icon = QSystemTrayIcon()
        self.window.tray_icon.setIcon(self.window.style().standardIcon(style))
        self.window.tray_icon.ActivationReason()

        show_action = QAction("Показать", self.window)
        hide_action = QAction("Скрыть", self.window)
        quit_action = QAction("Закрыть", self.window)

        # self.window.tray_icon.DoubleClick.connect(self.window.show)
        show_action.triggered.connect(self.window.show)
        hide_action.triggered.connect(self.window.hide)
        if exit:
            quit_action.triggered.connect(self.window.exit_action)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        if exit:
            tray_menu.addAction(quit_action)

        self.window.tray_icon.activated.connect(self.onActivated)
        self.window.tray_icon.setContextMenu(tray_menu)
        self.window.tray_icon.show()

    def exit(self):

        self.window.tray_icon.hide()
        self.window.tray_icon.deleteLater()
        self.window = None

    # noinspection PyPep8Naming
    def onActivated(self, reason):
        if reason == 3:
            if self.window.isVisible():
                self.window.hide()
            else:
                self.window.show()


# Обновляем данные в файле inp_gti
class InpGti:
    def __init__(self):
        self.init_inp_gti()

    def init_inp_gti(self):

        self.inp_gti_data = None
        self.inp_gti_dir = Gl.md['Директория_inp_gti']

    def read_inp_gti(self):
        # noinspection PyBroadException
        try:
            self.inp_gti_data = open(self.inp_gti_dir).read()
            return True

        except:
            print(f"Не удалось открыть read_inp_gti {self.inp_gti_dir}")
            return False

    def write_inp_gti(self, data, pattern):  # 2 После запускам функцию write

        if not self.read_inp_gti():
            return False

        # noinspection PyBroadException
        try:
            original_data = re.search(pattern, self.inp_gti_data)[0]
            changed_data = str(re.sub(r'\d+[,.]*\d*$', str(data), original_data))

            inp_gti_file = open(self.inp_gti_dir, 'w')
            inp_gti_file.write(re.sub(pattern, changed_data, self.inp_gti_data))
            inp_gti_file.close()

            print(f"Запись в inpgti сохранена: {changed_data}")
            return True

        except PermissionError:
            print(f"Файл inpgti занят")
            time.sleep(1)
            self.write_inp_gti(data, pattern)

        except TypeError:
            (my_type, value, traceback) = sys.exc_info()
            sys.excepthook(my_type, value, traceback)
            print(f"Паттерн не найден: {pattern}")
            return False

        except:
            (my_type, value, traceback) = sys.exc_info()
            sys.excepthook(my_type, value, traceback)
            return False


# Чтение registr.nbl.extended (Названии параметров)
class NblExtended:
    def __init__(self, parent=None):
        self.mainWindow = parent
        self.init_nbl_extended()

    def init_nbl_extended(self):
        pass

    def read_nbl_extended(self):
        # noinspection PyBroadException
        try:

            text = open(Gl.md['Директория_registr'], 'r').read()
            x = re.findall(r'\s\w{2,}\s{4}', re.sub(r"(\x00)|(\x01)|(\x02)|(\x03)", ' ', text))

            Gl.md['Названия_параметров'] = []
            for i in x:
                Gl.md['Названия_параметров'].append(re.sub(r'\s*', '', str(i)))  # Формируем список.

            print(f"Названия_параметров: {Gl.md['Названия_параметров']}")
            print('Чтение названий параметров Успешно!')

            return True

        except FileNotFoundError:
            # groupBox_deepControl
            Gl.md['Контроль_глубины'] = False
            self.mainWindow.groupBox_deepControl.setChecked(QtCore.Qt.Unchecked)
            msg_box = Msg.Message(
                text='Выберите папку Registr. \n Обычно расположен на диске E:\\registr',
                title='Внимание!!!!',
                button_1=QMessageBox.Ok,
                button_2=QMessageBox.Cancel
            )

            if msg_box.result == QMessageBox.Ok:
                self.mainWindow.browse_folder_registr_nbl_extended()
            else:
                return False

        except:

            print('Чтение названий параметров ОШИБКА!')
            return False


# Запись заметок в Заметки.rem
class NotesRem:
    def __init__(self):
        self.init_notes_rem()

    def init_notes_rem(self):
        pass

    @staticmethod
    def set_notes(my_time, text, my_format_time):
        # noinspection PyBroadException
        try:

            notes = open(Gl.md['Директория_заметки'], 'a')
            data = f'0.00 0.00 {str(my_time)} 0 "{text}" 0 0 7\n'
            notes.write(data)
            notes.close()
            print(f"Добавлена заметка: {my_format_time} {data}")

        except:
            print(f"Записать в файл не удалось: {Gl.md['Директория_заметки']}")


class ResetProperties:
    def __init__(self):
        self.init_reset_properties()

    def init_reset_properties(self):
        pass

    def reset_properties(self):
        self.inserted_depth_tool = False
        self.direction_spo = None


# Считываем данных с setting.txt
class Md:
    def __init__(self):
        pass

    def init_setting(self):
        self.load_setting()

    def load_setting(self):
        # noinspection PyBroadException
        try:
            Gl.md = json.load(open('setting.txt'))

        except:
            self.safe_setting()
            print(f"Данных нет {Gl.md}")

    # Сохраняем данные в setting.txt
    @staticmethod
    def safe_setting():
        up_data_md = {}
        up_data_md.update(Gl.md)
        up_data_md["Названия_параметров"] = []
        up_data_md["Значения_параметров"] = []
        up_data_md["Параметры"] = {'Факт_кол_элем': 0, 'Расч_кол_элем': 0, 'Фактическая_глубина': 0, 'Расчетная_глубина': 0}
        up_data_md["Промер_регистрации"] = []
        up_data_md["Адреса"] = {'Временные_адреса_1': [], 'Временные_адреса_2': []}
        up_data_md["Карта_памяти"] = []
        up_data_md["Мера"] = []
        up_data_md["Наст_inp_gti"] = {}
        up_data_md["НастРег"] = {}
        up_data_md["Время_заметок"] = 0

        setting_json = open('setting.txt', 'w')
        json.dump(up_data_md, setting_json, sort_keys=True, indent=4, ensure_ascii=False)
        setting_json.close()
        print(f"Данные сохранены {up_data_md}")

    def close_md(self):
        self.safe_setting()
        self.load_setting()


# Работа с файлами Excel
class Excel:
    def __init__(self):
        self.init_excel()

    def init_excel(self):
        pass

    def open_excel(self):

        if not self.open_excel_bool:
            # Показываем что СОМ объект будет использовать в отдельном потоке
            pythoncom.CoInitialize()

            # COM объект
            self.Excel = win32com.client.Dispatch("Excel.Application")

            if not self.set_properties_excel():
                return False

            if self.Excel.Application.Workbooks.Count > 0:
                # Проверяем наличие открытой сводки
                for i in range(1, self.Excel.Application.Workbooks.Count + 1):
                    print(f"{Gl.md['Название_файла_меры_инстр']} / {self.Excel.Application.Workbooks(i).Name}")
                    if Gl.md['Название_файла_меры_инстр'] == self.Excel.Application.Workbooks(i).Name:
                        print(f"Найден открытый файл слежение за глубиной")
                        self.work_book = self.Excel.Application.Workbooks(i)
                        self.opened_excel_bool = True
                        break

            if not self.opened_excel_bool:
                print(f"Нету открытого файла {Gl.md['Название_файла_меры_инстр']} / Открываем слежение за глубиной")
                self.work_book = self.Excel.Workbooks.Open(Gl.md['Директория_меры_инстр'])
                if not self.set_properties_excel():
                    return False

            # Если файл Слежения за глубиной не открыта то завершаем работу
            if self.work_book is None or self.open_excel_bool is None:
                print(f"Не удалось открыть Excel")
                return False

            # Выбираем лист "Слежение за глубиной"
            self.sheet = self.work_book.Sheets("Слежение за глубиной")

            return True

        else:
            return True

    def set_properties_excel(self):
        # noinspection PyBroadException
        try:
            self.Excel.Application.DisplayAlerts = False
            self.Excel.Application.ScreenUpdating = True
            # self.Excel.Application.visible = True
            return True

        except:
            print("except")
            msg_box = Msg.Message(
                text='Выйдете из режима редактирования в Excel\nПосле нажмите Ок',
                title='Внимание!!!!',
                button_1=QMessageBox.Ok,
                button_2=QMessageBox.Cancel
            )

            if msg_box.result == QMessageBox.Ok:
                return self.open_excel()
            else:
                return False

    def read_excel(self):
        # noinspection PyBroadException
        try:
            read_data = self.sheet.Range(self.sheet.Cells(14, 7), self.sheet.Cells(1000, 17)).Value
            self.composition = []
            self.pipe = []
            self.pipe_items = []

            row = 0
            for i in read_data:
                # КНБК
                if i[10] is not None and row <= 29:
                    self.composition.append(i[0])
                # Трубы
                if i[0] is not None and row > 29:
                    self.pipe.append(i[0])
                # Мера по нарастающи
                if i[0] is not None:
                    self.pipe_items.append(round(self.pipe_items[-1] + i[0], 2)) if row > 0 else self.pipe_items.append(i[0] - Gl.md['L_до_АКБ'])
                # Выход из цикла если мера закончилась
                if i[0] is None and row > 29:
                    break

                row += 1

            if not self.opened_excel_bool:

                if self.Excel.Application.Workbooks.Count == 1:
                    # Закроем файл
                    self.work_book.Close()
                    # Закроем COM объект
                    self.Excel.Quit()
                else:
                    # Закроем файл
                    self.work_book.Close()

            return True

        except:

            print(f"not read")
            self.read_data = False
            return False

    def up_data_pipe_items(self):

        self.Excel = None
        self.work_book = None
        self.sheet = None
        self.open_excel_bool = False
        self.opened_excel_bool = False
        self.read_data = False

        # Открытие файла
        self.open_excel_bool = self.open_excel()

        # Чтение данных
        self.read_data = self.read_excel()

    def write_excel(self):
        pass


# Создаем лист с промером инструмента
class Tools(Excel):
    def __init__(self, parent=None):
        super().__init__()
        self.mainWindow = parent
        self.init_tools()

    def init_tools(self):
        pass

    def read_tools(self):
        self.up_data_pipe_items()
        if self.read_data:
            Gl.md['Мера'] = self.pipe_items
            Gl.md['Элем_КНБК'] = len(self.composition)
            print(f"Элементов в КНБК: {len(self.composition)}; Труб: {len(self.pipe)}; Мера: {self.pipe_items}")
            print('Чтение файла слежения за глубиной Успешно!')
            return True
        else:
            self.mainWindow.groupBox_deepControl.setChecked(QtCore.Qt.Unchecked)
            print('Чтение файла слежения за глубиной ОШИБКА!')
            return False


# Класс считывания и редактирования (для редактируемых параметров)
class EditParameter(Ram, Tools, InpGti, ResetProperties):
    def __init__(self, parent=None):
        super().__init__()
        self.mainWindow = parent
        self.init_edit_parameter()

    def init_edit_parameter(self):
        self.depth = None
        self.depth_tool = None
        self.tal = None
        self.item_tool = None

    # Загружаем данные по редактируемым параметрам
    def read_edit_param(self):
        self.depth = self.read_process_memory(address=Gl.md['Адреса']['Забой'], bytes_read=8, my_structure='<d', i_round=2)
        self.depth_tool = self.read_process_memory(address=Gl.md['Адреса']['Гл_инстр'], bytes_read=8, my_structure='<d', i_round=2)
        self.tal = self.read_process_memory(address=Gl.md['Адреса']['Высота_таль'], bytes_read=8, my_structure='<d', i_round=2)
        self.item_tool = self.read_process_memory(address=Gl.md['Адреса']['Cпущ_элем'], bytes_read=4, my_structure='<I', i_round=2)
        self.cf_dol = self.read_process_memory(address=Gl.md['Адреса']['коэффицент_ДОЛа'], bytes_read=4, my_structure='<f', i_round=2)
        self.weight_tool = self.read_process_memory(address=Gl.md['Адреса']['общий_вес_колонны'], bytes_read=4, my_structure='<f', i_round=2)
        self.min_tal = self.read_process_memory(address=Gl.md['Адреса']['мин_тальблок'], bytes_read=4, my_structure='<f', i_round=2)
        self.candle = self.read_process_memory(address=Gl.md['Адреса']['свеча'], bytes_read=4, my_structure='<f', i_round=2)
        self.min_weight = self.read_process_memory(address=Gl.md['Адреса']['нулевой_вес'], bytes_read=4, my_structure='<f', i_round=2)
        self.min_press = self.read_process_memory(address=Gl.md['Адреса']['нулевое_давление'], bytes_read=4, my_structure='<f', i_round=2)
        self.cf_rotor = self.read_process_memory(address=Gl.md['Адреса']['коэф_ротора'], bytes_read=4, my_structure='<f', i_round=2)
        self.max_load = self.read_process_memory(address=Gl.md['Адреса']['макс_нагрузка'], bytes_read=4, my_structure='<f', i_round=2)
        self.min_load = self.read_process_memory(address=Gl.md['Адреса']['мин_нагрузка'], bytes_read=4, my_structure='<f', i_round=2)
        self.dep_load = self.read_process_memory(address=Gl.md['Адреса']['глубина_для_нагрузки'], bytes_read=4, my_structure='<f', i_round=2)

        Gl.md['Забой'] = self.depth
        Gl.md['Гл_инстр'] = self.depth_tool
        Gl.md['Высота_таль'] = self.tal
        Gl.md['Cпущ_элем'] = self.item_tool
        Gl.md['Коф_дол'] = self.cf_dol
        Gl.md['Вес_инстр'] = self.weight_tool
        Gl.md['Мин_таль'] = self.min_tal
        Gl.md['Свеча'] = self.candle
        Gl.md['Мин_вес'] = self.min_weight
        Gl.md['Мин_давл'] = self.min_press
        Gl.md['Коф_ротор'] = self.cf_rotor
        Gl.md['Макс_нагр'] = self.max_load
        Gl.md['Мин_нагр'] = self.min_load
        Gl.md['Гл_нагр'] = self.dep_load

    # Округление
    @staticmethod
    def my_round(x, base=5):
        return base * round(x / base)

    # Запись
    def w_depth(self):
        pass

    def w_depth_tool(self, data):
        self.write_process_memory(Gl.md['Адреса']['Гл_инстр'], struct.pack('<d', data), buffer_size=8)

    def w_tal(self, data):
        self.write_process_memory(Gl.md['Адреса']['Высота_таль'], struct.pack('<d', data), buffer_size=8)
        print(f'Тальблок исправлен {data}')

    def w_item(self, data):
        self.write_process_memory(Gl.md['Адреса']['Cпущ_элем'], struct.pack('<I', data), buffer_size=4)

    def w_cf_dol(self, data):
        self.write_process_memory(Gl.md['Адреса']['коэффицент_ДОЛа'], struct.pack('<f', data), buffer_size=4)
        self.write_inp_gti(data, r'коэффицент_ДОЛа=\d+[.,]*\d*')

    def w_weight_tool(self, data):
        self.write_process_memory(Gl.md['Адреса']['общий_вес_колонны'], struct.pack('<f', data), buffer_size=4)
        self.write_inp_gti(data, r'общий_вес_колонны=\d+[.,]*\d*')

    def w_dep_load(self, data):
        self.write_process_memory(Gl.md['Адреса']['глубина_для_нагрузки'], struct.pack('<f', data), buffer_size=4)
        self.write_inp_gti(data, r'глубина_для_нагрузки=\d+[.,]*\d*')


class CalculateDepthTool(EditParameter):
    def __init__(self):
        super().__init__()
        self.init_calculate_depth_tool()

    def init_calculate_depth_tool(self):
        pass

    def calculate_plan_depth_tool(self, weight=False):
        if not weight:
            if Gl.pr['вес_на_крюке'] < self.min_weight:
                self.plan_depth_tool = min(Gl.md['Мера'], key=lambda x: abs(self.depth_tool - x))
                self.plan_item_tool = int(Gl.md['Мера'].index(self.plan_depth_tool) + 1)

                return True

        if weight:
            if Gl.pr['вес_на_крюке'] > self.min_weight:
                self.plan_depth_tool = min(Gl.md['Мера'], key=lambda x: abs(self.depth_tool - x))
                self.plan_item_tool = int(Gl.md['Мера'].index(self.plan_depth_tool) + 1)

                return True

        return False


# Считываем адреса параметров
class ReadAddress(EditParameter):
    def __init__(self, parent=None):
        super().__init__()
        self.mainWindow = parent
        self.init_read_address()

    def init_read_address(self):
        self.readAddress = False

    def read_address(self):

        Gl.md['Наст_inp_gti'] = \
            {
                'коэффицент_ДОЛа': 0, 'общий_вес_колонны': 0, 'мин_тальблок': 0, 'свеча': 0, 'нулевой_вес': 0,
                'нулевое_давление': 0, 'коэф_ротора': 0, 'макс_нагрузка': 0, 'мин_нагрузка': 0, 'глубина_для_нагрузки': 0
            }
        # noinspection PyBroadException
        try:
            # Загружаем настроичный данные
            input_text = re.sub(r',', '.', open(Gl.md['Директория_inp_gti']).read())
            for i in Gl.md['Наст_inp_gti']:
                pattern = i + r'=\d+[.,]*\d*'
                Gl.md['Наст_inp_gti'][i] = float(re.search(r'\d+[.,]*\d*', re.search(pattern, input_text)[0])[0])

            # Создаем паттерт
            pattern = \
                binascii.hexlify(struct.pack('f', Gl.md['Наст_inp_gti']['коэффицент_ДОЛа'])) + b'.{24}' + \
                binascii.hexlify(struct.pack('f', Gl.md['Наст_inp_gti']['общий_вес_колонны'])) + b'.{8}' + \
                binascii.hexlify(struct.pack('f', Gl.md['Наст_inp_gti']['мин_тальблок'])) + \
                binascii.hexlify(struct.pack('f', Gl.md['Наст_inp_gti']['свеча'])) + b'.{8}' + \
                binascii.hexlify(struct.pack('f', Gl.md['Наст_inp_gti']['нулевой_вес'])) + \
                binascii.hexlify(struct.pack('f', Gl.md['Наст_inp_gti']['нулевое_давление'])) + \
                binascii.hexlify(struct.pack('f', Gl.md['Наст_inp_gti']['коэф_ротора'])) + b'.{8}' + \
                binascii.hexlify(struct.pack('f', Gl.md['Наст_inp_gti']['макс_нагрузка'])) + \
                binascii.hexlify(struct.pack('f', Gl.md['Наст_inp_gti']['мин_нагрузка'])) + b'.{120}' + \
                binascii.hexlify(struct.pack('f', Gl.md['Наст_inp_gti']['глубина_для_нагрузки']))

            # Находим паттерн в оперативной памяти процесса
            self.mainWindow.text_progressBar = 'Поиск значений настроек в оперативной памяти'
            self.find_pattern(pattern)

            if self.find_pattern_result:
                # Начальное смещение для поиска адресов редактируемых параметров (Забой, Глубина_инструмента, Высота_таль, Количество_элементов)
                Gl.md['Блок_памяти'].update({'НастРег': Gl.md['Карта_памяти'][self.index_vm_map]})

                # Начальное смещение для поиска остальных адресов редактируемых параметров
                Gl.md['Адреса'].update({'НастРег': int(Gl.md['Карта_памяти'][self.index_vm_map][0] + (self.find_pattern_result.start() / 2))})

                # Загружаем адреса редактируемых параметров
                Gl.md['Адреса'].update({'коэффицент_ДОЛа': Gl.md['Адреса']['НастРег']})
                Gl.md['Адреса'].update({'общий_вес_колонны': Gl.md['Адреса']['НастРег'] + 16})
                Gl.md['Адреса'].update({'мин_тальблок': Gl.md['Адреса']['НастРег'] + 24})
                Gl.md['Адреса'].update({'свеча': Gl.md['Адреса']['НастРег'] + 28})
                Gl.md['Адреса'].update({'нулевой_вес': Gl.md['Адреса']['НастРег'] + 36})
                Gl.md['Адреса'].update({'нулевое_давление': Gl.md['Адреса']['НастРег'] + 40})
                Gl.md['Адреса'].update({'коэф_ротора': Gl.md['Адреса']['НастРег'] + 44})
                Gl.md['Адреса'].update({'макс_нагрузка': Gl.md['Адреса']['НастРег'] + 52})
                Gl.md['Адреса'].update({'мин_нагрузка': Gl.md['Адреса']['НастРег'] + 56})
                Gl.md['Адреса'].update({'глубина_для_нагрузки': Gl.md['Адреса']['НастРег'] + 120})
                Gl.md['Адреса'].update({'Забой': Gl.md['Блок_памяти']['НастРег'][0] + Gl.md['Offset_забой']})
                Gl.md['Адреса'].update({'Гл_инстр': Gl.md['Блок_памяти']['НастРег'][0] + Gl.md['Offset_глубина_инструмента']})
                Gl.md['Адреса'].update({'Высота_таль': Gl.md['Блок_памяти']['НастРег'][0] + Gl.md['Offset_тальблок']})
                Gl.md['Адреса'].update({'Cпущ_элем': Gl.md['Блок_памяти']['НастРег'][0] + Gl.md['Offset_Количество_элементов']})
                Gl.md['Адреса'].update({'Параметров': []})  # 16848

                # Загружаем не радактируемые адреса параметров
                address = Gl.md['Адреса']['Забой'] - 16848
                for i in range(0, len(Gl.md['Названия_параметров'])):
                    Gl.md['Адреса']['Параметров'].append(address)
                    Gl.md['Значения_параметров'].append(0)
                    address += 8

                # Загружаем значения редактируемых параметров
                self.read_edit_param()

                Gl.md['НастРег'].update({'Забой': self.depth})
                Gl.md['НастРег'].update({'Гл_инстр': self.depth_tool})
                Gl.md['НастРег'].update({'Высота_таль': self.tal})
                Gl.md['НастРег'].update({'Cпущ_элем': self.item_tool})
                Gl.md['НастРег'].update({'Коф_дол': self.cf_dol})
                Gl.md['НастРег'].update({'Вес_инстр': self.weight_tool})
                Gl.md['НастРег'].update({'Мин_таль': self.min_tal})
                Gl.md['НастРег'].update({'Свеча': self.candle})
                Gl.md['НастРег'].update({'Мин_вес': self.min_weight})
                Gl.md['НастРег'].update({'Мин_давл': self.min_press})
                Gl.md['НастРег'].update({'Коф_ротор': self.cf_rotor})
                Gl.md['НастРег'].update({'Макс_нагр': self.max_load})
                Gl.md['НастРег'].update({'Мин_нагр': self.min_load})
                Gl.md['НастРег'].update({'Гл_нагр': self.dep_load})

                print(f"Значения по настройкам из оперативной памяти: {Gl.md['НастРег']}")
                self.readAddress = True

                print('Чтение настроек Успешно!')
                return True

            else:

                msg_box = Msg.Message(
                    text='Зайдите в Настройки/Настройки/Настройки распознавания \n измените нулевой весь на 1 десятую + - нажмите применить и ОК',
                    title='Внимание!!!! Данные по настройкам регистрации не найдены.', button_1=QMessageBox.Ok,
                    button_2=QMessageBox.Cancel
                )

                if msg_box.result == QMessageBox.Ok:
                    return self.read_address()
                else:
                    return False

        except:
            print('Чтение настроек ОШИБКА!')
            (my_type, value, traceback) = sys.exc_info()
            sys.excepthook(my_type, value, traceback)


# Считываем значения параметров
class ReadParameters(EditParameter):
    def __init__(self, parent=None):
        super().__init__()
        self.mainWindow = parent
        self.init_read_parameters()

    def init_read_parameters(self):
        self.__initParameters = False

    def read_parameters(self):
        # noinspection PyBroadException
        try:
            # Чтение не редактируемых адресов
            for i in range(0, len(Gl.md['Названия_параметров'])):
                my_round = 2
                if Gl.md['Названия_параметров'][i] == 'скорость_тальблока':
                    my_round = 6
                elif Gl.md['Названия_параметров'][i] == 'сумм_газ':
                    my_round = 8
                Gl.md['Значения_параметров'][i] = self.read_process_memory(
                    address=Gl.md['Адреса']['Параметров'][i], bytes_read=8, my_structure='<d', i_round=my_round
                )

                # Массив с параметрами
                Gl.pr.update({Gl.md['Названия_параметров'][i]: Gl.md['Значения_параметров'][i]})

            # Чтение редактируемых параметров
            self.read_edit_param()

            # Выводим параметры с их значениями
            if not self.__initParameters:
                x = 0
                for i in Gl.pr:
                    x += 1
                    print(f"{x}.  {i}:  {Gl.pr[i]}")
                self.__initParameters = True
                print('Чтение редактируемых параметров Успешно!')
        except:
            (my_type, value, traceback) = sys.exc_info()
            sys.excepthook(my_type, value, traceback)
            print('Чтение редактируемых параметров ОШИБКА!')


# Считываем смещение
class FindOffset(Ram):
    def __init__(self, parent=None):
        super().__init__()
        self.mainWindow = parent
        self.init_find_offset()

    def init_find_offset(self):
        self.__sender_val = None
        self.__sender_address = None

    def find_offset(self, sender_val, sender_address, my_structure=None, total_bytes=8):

        if self.__sender_val != sender_val:
            self.__offset_list_1 = []
            self.__offset_list_2 = []
            self.__size_last_list = 0
            self.__sender_val = sender_val
            self.__sender_address = sender_address

        pattern = binascii.hexlify(struct.pack(my_structure, self.__sender_val.value()))

        offset_list = []

        # Массив с разрешенными для чтения регионами памяти
        for i in self.vm_map:

            # print(f"{i[0]}  {i[3]}")
            data = self.read_process_memory(i[0], i[3])
            if data is not None:
                result = re.finditer(pattern, binascii.hexlify(data))

                for match in result:
                    offset_list.append(int(i[0] + (match.start() / 2)))

        # Находим совподении в двух массивах, остальное удаляем
        if len(self.__offset_list_1) == 0:
            self.__offset_list_1 = offset_list
        else:
            self.__offset_list_2 = offset_list
            data = set(self.__offset_list_1) & set(self.__offset_list_2)
            self.__offset_list_1 = []
            for i in data:
                self.__offset_list_1.append(i)

        # Если массив с адресами не меняется
        set_data = self.__sender_val.value() + 1

        if len(self.__offset_list_1) == self.__size_last_list:
            for i in range(0, self.__size_last_list):

                # Записываем новое значение по адресу i
                self.write_process_memory(self.__offset_list_1[i], struct.pack(my_structure, set_data), buffer_size=total_bytes)
                check_list = []
                # noinspection PyUnusedLocal
                read_data = 0
                QtCore.QThread.msleep(1000)

                # Считываем по адресам значении на совподение
                for j in range(0, self.__size_last_list):
                    read_data = self.read_process_memory(address=self.__offset_list_1[j], bytes_read=total_bytes, my_structure=my_structure, i_round=2)
                    if j != i and read_data == set_data:
                        check_list.append(self.__offset_list_1[j])

                # print(f"{self.__offset_list_1} / {check_list}")
                # Если совподение найдено
                if len(check_list) > 0:
                    self.__sender_address.setValue(self.__offset_list_1[i])
                    print(self.__offset_list_1[i])
                    return

                set_data += 1

        self.__size_last_list = len(self.__offset_list_1)

        print(self.__offset_list_1)


# Определение операции
class Operation(CalculateDepthTool):
    def __init__(self, parent=None):
        super().__init__()
        self.mainWindow = parent
        self.init_operation()

    def init_operation(self):
        self.direction_spo = None
        self.inserted_depth_tool = False
        self.__last_pipe = 0
        self.__timeStar_build_up = None
        self.__timeStop_build_up = None
        self.__duration_build_up = None
        self.__calculate_build_up = False

    def get_direction_spo(self):

        # Определения направления СПО
        if self.calculate_plan_depth_tool(weight=False):

            if self.__last_pipe == 0:
                self.__last_pipe = self.item_tool

            if self.inserted_depth_tool:
                print(f"Было элементов {self.__last_pipe} / {self.plan_item_tool} / {self.inserted_depth_tool}")
                if self.__last_pipe < self.plan_item_tool:
                    self.__last_pipe = self.plan_item_tool
                    self.direction_spo = 'down'

                if self.__last_pipe > self.plan_item_tool:
                    self.__last_pipe = self.plan_item_tool
                    self.direction_spo = 'up'
                print(f"direction_spo {self.direction_spo}")

    def get_build_up_time(self):

        if not self.__timeStar_build_up and None and not self.inserted_depth_tool:
            return False

        if not self.__timeStar_build_up and self.inserted_depth_tool and Gl.pr['тальблок'] < 3:
            self.__timeStop_build_up = None
            self.__duration_build_up = None
            self.__calculate_build_up = False
            self.__timeStar_build_up = datetime.now()

        if self.__timeStar_build_up is not None and Gl.pr['тальблок'] > 10 and Gl.pr['вес_на_крюке'] > self.min_weight:
            self.__timeStop_build_up = datetime.now()
            self.__duration_build_up = self.my_round(divmod((self.__timeStop_build_up - self.__timeStar_build_up).seconds, 60)[0])

        if self.__duration_build_up is not None and self.__calculate_build_up is None:
            self.__calculate_build_up = True
            self.__timeStar_build_up = None
            print(f"Время наращивания {self.__duration_build_up}")


# Коррекция гл. долота
class SPO(Operation):
    def __init__(self, parent=None):
        super().__init__()
        self.mainWindow = parent
        self.init_spo()
        self.init_operation()

    def init_spo(self):
        self.__plan_itemTool = None
        self.__direction_down = True
        self.diff_depth_tool = 0
        self.plan_depth_tool = None
        self.plan_item_tool = 0
        self.bool_diff_depth_tool = False
        self.inserted_depth_tool = False

    # Обработка события СПО
    def spo(self):

        # Устанавливаем коэфицент дола
        self.set_cf_dol()
        self.set_item_tool()

        if self.check_sub():
            self.set_depth_tool()
            self.set_item_tool()

        if self.calculate_plan_depth_tool(weight=True):
            pass

    # print(f"До ближайшей расчетной глубины: {round(self.depth_tool - self.plan_depth_tool, 2)} м. Ближайшая глубина по мере: {self.plan_depth_tool} м")

    # Проверка события на СПО
    def check_sub(self):
        if self.calculate_depth_tool():
            self.inserted_depth_tool = True

            return True
        return False

    # Устанавливаем глубину долота
    def set_depth_tool(self):
        if self.calculate_depth_tool():
            # Ставим расчетную глубину долота
            self.w_depth_tool(self.plan_depth_tool)
            print(f"Старая глубина - {self.depth_tool} / Новая глубина - {self.plan_depth_tool}")

    # Устанавливаем Количество спущенных элементов
    def set_item_tool(self):
        if self.calculate_item_tool():
            # Количество спущенных элементов
            self.w_item(self.plan_item_tool)
            print(f"Старое колл. элементов - {self.item_tool} / Новая колл. элементов - {self.plan_item_tool}")

    # Устанавливаем коэфицент дола
    def set_cf_dol(self):

        if self.calculate_cf_dol():
            self.w_cf_dol(round(self.new_cf_dol, 1))
            print(f"Старый коф. дола - {self.cf_dol} / Новый коф. дола - {self.new_cf_dol}")

    # Расчитываем глубину долота
    def calculate_depth_tool(self):
        if len(Gl.md['Мера']) == 0 or not self.calculate_plan_depth_tool(weight=False):
            return False

        self.diff_depth_tool = round(self.depth_tool - self.plan_depth_tool, 2)

        self.bool_diff_depth_tool = True if Gl.md['Макс_раз_гл'] * (-1) < self.diff_depth_tool < Gl.md['Макс_раз_гл'] else False

        if self.bool_diff_depth_tool and self.depth_tool != self.plan_depth_tool < self.depth:
            return True

    # Расчет Количество спущенных элементов
    def calculate_item_tool(self):
        if len(Gl.md['Мера']) == 0 or not self.calculate_plan_depth_tool(weight=False):
            return False

        if self.plan_item_tool != self.item_tool and self.plan_depth_tool is not None:
            return True

        return False

    # Расчет коэфициента для дола
    def calculate_cf_dol(self):

        if not self.__plan_itemTool:
            self.__plan_itemTool = self.item_tool

        if self.calculate_plan_depth_tool(weight=False) and self.__plan_itemTool != self.plan_item_tool:
            # Направление
            self.__direction_down = True if self.__plan_itemTool < self.plan_item_tool else False

            # Разница между текущей глубиной и плановой
            self.diff_depth_tool = round(self.depth_tool - self.plan_depth_tool, 2)

            self.new_cf_dol = 0

            if self.diff_depth_tool > 0.1 or self.diff_depth_tool < (-0.1):
                if self.__direction_down:
                    if self.diff_depth_tool > 0:
                        # Увеличить
                        self.new_cf_dol = self.cf_dol + 1 if self.diff_depth_tool > 1 else self.cf_dol + 0.2
                        print(f"Спуск, увеличиваем коф. на: {self.new_cf_dol} / {self.diff_depth_tool}")
                    else:
                        # Уменьшить
                        self.new_cf_dol = self.cf_dol - 1 if (-1) * self.diff_depth_tool > 1 else self.cf_dol - 0.2
                        print(f"Спуск, уменьшаем коф. на: {self.new_cf_dol} / {self.diff_depth_tool}")

                if not self.__direction_down:
                    if self.diff_depth_tool > 0:
                        # Уменьшить
                        self.new_cf_dol = self.cf_dol - 1 if self.diff_depth_tool > 1 else self.cf_dol - 0.2
                        print(f"Подъем, уменьшаем коф. на: {self.new_cf_dol} / {self.diff_depth_tool}")
                    else:
                        # Увеличить
                        self.new_cf_dol = self.cf_dol + 1 if (-1) * self.diff_depth_tool > 1 else self.cf_dol + 0.2
                        print(f"Подъем, увеличиваем коф. на: {self.new_cf_dol} / {self.diff_depth_tool}")

            # Элементов в скважине
            self.__plan_itemTool = self.plan_item_tool

            if self.new_cf_dol > 0:
                return True

        return False


# Обновление данных в главном окне
class GetDataMainWindow(SPO):
    def __init__(self):
        super().__init__()
        self.init_set_data_main_window()

    def init_set_data_main_window(self):
        self.__plan_itemTool = None

    def get_data_for_main_window(self):

        if self.__plan_itemTool is None:
            self.__plan_itemTool = self.item_tool

        if self.calculate_plan_depth_tool(weight=False) and self.__plan_itemTool != self.plan_item_tool:
            self.__plan_itemTool = self.plan_item_tool

        if self.__plan_itemTool > len(self.composition):
            Gl.md['Спущено_труб'] = self.__plan_itemTool - len(self.composition)
            x = Gl.md['Спущено_труб'] % Gl.md['Труб_в_свече']
            Gl.md['Спущено_свеч'] = int((Gl.md['Спущено_труб'] - x) / Gl.md['Труб_в_свече']) if x > 0 else int(Gl.md['Спущено_труб'] / Gl.md['Труб_в_свече'])
        else:
            Gl.md['Спущено_труб'], Gl.md['Спущено_свеч'] = 0, 0

        if Gl.md['Кол_труб_до_подъема'] > Gl.md['Спущено_труб']:
            Gl.md['Поднято_труб'] = Gl.md['Кол_труб_до_подъема'] - Gl.md['Спущено_труб']
            x = Gl.md['Поднято_труб'] % Gl.md['Труб_в_свече']
            Gl.md['Поднято_свеч'] = int((Gl.md['Поднято_труб'] - x) / Gl.md['Труб_в_свече']) if x > 0 else int(Gl.md['Поднято_труб'] / Gl.md['Труб_в_свече'])
        else:
            Gl.md['Поднято_труб'], Gl.md['Поднято_свеч'] = 0, 0


# Ставим заметки о колличестве спущенных тр.
class NotesPipe(NotesRem, Operation):
    def __init__(self):
        super().__init__()
        self.init_notes_pipe()

    def init_notes_pipe(self):
        self.__time = 0
        self.__time_format = 0
        self.__direction_spo = None
        self.__text_fixed = None
        self.__text = None

    def set_notes_pipe(self):

        if not self.__direction_spo and self.direction_spo is not None:
            self.__direction_spo = self.direction_spo

        set_note = False
        if self.__get_time_set_notes_pipe() and self.__direction_spo is not None and self.__made_text():

            if self.__direction_spo == 'down':
                self.set_notes(self.__time, self.__text, self.__time_format)
                set_note = True

            if self.__direction_spo == 'up' and Gl.pr['скорость_тальблока'] > 0.001 and Gl.pr['тальблок'] < 8:
                self.set_notes(self.__time, self.__text, self.__time_format)
                set_note = True

            if set_note:
                self.__text_fixed = self.__text
                self.__direction_spo = None
                self.__time = 0

    def __get_time_set_notes_pipe(self):
        # Записываем время для заметок
        if Gl.pr['тальблок'] > 8 and round(Gl.pr['скорость_тальблока'], 4) == 0 and Gl.pr['давление_на_входе'] < self.min_press and \
                Gl.pr['вес_на_крюке'] < self.min_weight:
            self.__time = int(time.time()) + (24 * 60 * 60) + (5 * 60 * 60)
            self.__time_format = datetime.now().strftime("%H:%M:%S")

        # print(f"Время {self.__time_format}   / 'скорость_тальблока' {round(Gl.pr['скорость_тальблока'], 4)}")

        if self.__time > 0:
            return True
        else:
            return False

    def __made_text(self):

        down = Gl.md['Заметки_спо']['down']
        up = Gl.md['Заметки_спо']['up']
        item, pipe, get_pipe, text, calculate, pipes = 0, 0, 0, '', False, []

        if not self.calculate_plan_depth_tool(weight=False):
            return False

        if self.__direction_spo == 'down':
            for i in down:
                if 0 < i[0] <= self.plan_item_tool:
                    item = i[0]
                    pipe = i[1]
                    text = i[2]

            if 0 < item <= self.plan_item_tool:
                pipes = Gl.md['Мера'][item:]
                get_pipe = int(pipes.index(self.plan_depth_tool) + pipe) + 1
                calculate = True

        if self.__direction_spo == 'up':
            item = 10000
            for i in up:
                if 0 < i[0] > self.plan_item_tool < item:
                    item = i[0]
                    pipe = i[1]
                    text = i[2]

            if 1000 != item > self.plan_item_tool:
                pipes = self.pipe_items[:item]
                pipes.reverse()
                get_pipe = int(pipes.index(self.plan_depth_tool) + pipe) - 1
                calculate = True

        if calculate and self.__candle_or_pipe(get_pipe, text):
            return True

        return False

    def __candle_or_pipe(self, get_pipe, text):
        # Если поднимают свечи с половинкой то записываем в переменную х
        x = 0
        if re.search('^тр[.]*', text):
            total = get_pipe
        else:
            x = get_pipe % Gl.md['Труб_в_свече']
            total = int((get_pipe - x) / Gl.md['Труб_в_свече']) if x > 0 else int(get_pipe / Gl.md['Труб_в_свече'])

        if total % Gl.md['Шаг_уст_заметок'] == 0:
            self.__text = f"{total}{text}" if x == 0 else f"{total},5{text}"

        if self.__text_fixed != self.__text is not None:
            return True

        return False


# Исправляем высоту тальблока.
class FixTal(Operation):
    def __init__(self):
        super().__init__()
        self.init_fix_tal()

    def init_fix_tal(self):
        self.__plan_itemTool = None
        self.__direction_down = True
        self.__tal = None
        self.__total = 0

    def fix_tal(self):
        if self.__calculate_tal():
            self.w_tal(self.__tal)

    def __calculate_tal(self):

        if not self.__plan_itemTool:
            self.__plan_itemTool = self.item_tool

        if self.calculate_plan_depth_tool(weight=False) and self.__plan_itemTool != self.plan_item_tool:
            # Направление
            self.__direction_down = True if self.__plan_itemTool < self.plan_item_tool else False

            self.__tal = None

            if self.__direction_down:

                self.__total = self.plan_item_tool - self.__plan_itemTool

                # Спустили свечю
                if self.__total == Gl.md['Труб_в_свече']:
                    self.__tal = self.min_tal

                if self.__total == 1:
                    # Спустили трубу
                    if Gl.pr['тальблок'] < 5:
                        self.__tal = self.min_tal

                    # Спустили половинку
                    if Gl.pr['тальблок'] > 8:
                        a = Gl.md['Мера'][self.plan_item_tool]
                        b = Gl.md['Мера'][self.__plan_itemTool]
                        self.__tal = round(a - b, 2)

                # Элементов в скважине
                self.__plan_itemTool = self.plan_item_tool

                if self.__tal is not None:
                    print(f"Коррекция тальблока {self.__tal}")
                    return True

        return False


class CalculateDrilling(Operation):
    def __init__(self):
        super().__init__()
        self.init_calculate_drilling()

    def init_calculate_drilling(self):
        self.__last_item_tool = None
        self.__up_depth_tool = None
        self.__weight_tool = None
        self.__time_start = datetime.now() - date_time.timedelta(seconds=31)
        self.data_drilling = {
            'Прогресс': 0,
            'Ротор': None
        }

    def calculate_drilling(self):
        self.__set_weight_tool()
        self.__calculate_depth()
        if self.__up_depth_tool is not None:
            self.__set_depth_tool()

    def __set_weight_tool(self):

        if Gl.pr['расход_на_входе'] < 1:
            return False

        # Определяем количество секунд с момента включения оборотов ротора
        delta = 0
        if Gl.pr['обороты_ротора'] > 0:
            if self.__time_start is None:
                self.__time_start = datetime.now()
            else:
                delta = (datetime.now() - self.__time_start).seconds
        else:
            self.__time_start = None

        if Gl.md['Изменения_веса_слайд']:
            if Gl.pr['обороты_ротора'] > 0 and delta >= 30:
                self.__weight_tool = Gl.md['Вес_ротор']
                self.data_drilling['Ротор'] = True
            else:
                self.__weight_tool = Gl.md['Вес_слайд']
                self.data_drilling['Ротор'] = False
        else:
            self.__weight_tool = Gl.md['Вес_ротор']
            self.data_drilling['Ротор'] = True

        if self.weight_tool != self.__weight_tool:
            print(f"Обороты ротора {Gl.pr['обороты_ротора']} / {Gl.md['Изменения_веса_слайд']} / {self.data_drilling['Ротор']}")
            self.w_weight_tool(self.__weight_tool)
            return True
        else:
            self.data_drilling['Ротор'] = None
            return False

    def __calculate_depth(self):

        x = Gl.md['Труб_в_свече']

        Gl.md['до_бурил'] = round(Gl.md['Мера'][self.item_tool - 1 + x] + Gl.md['L_до_АКБ'], 2)
        Gl.md['Осталось_бурить'] = round(Gl.md['до_бурил'] - self.depth, 2)

        a = Gl.md['до_бурил'] - Gl.md['Мера'][self.item_tool - 1]
        b = self.depth - Gl.md['Мера'][self.item_tool - 1]
        percent = 100 / (a / b)

        if percent >= 100:
            self.data_drilling['Прогресс'] = 100
        else:
            self.data_drilling['Прогресс'] = percent

        if Gl.md['до_бурил'] <= round(self.depth_tool, 2) and Gl.pr['расход_на_входе'] > 1 and Gl.pr['тальблок'] < 5:
            self.__up_depth_tool = round(Gl.md['до_бурил'] - 0.10, 2)
        else:
            self.__up_depth_tool = None

    def __set_depth_tool(self):

        # Устанавливаем гл. нагрузки.
        self.w_dep_load(Gl.md['Гл_для_нагрузки'])

        # Устанавливаем долота выше расчетной глубины на 10см.
        self.w_depth_tool(self.__up_depth_tool)
        print(f"Старая глубина - {self.depth_tool} / Новая глубина - {self.__up_depth_tool}")

        self.__up_depth_tool = None


class CalculateSpo(Operation):
    def __init__(self):
        super().__init__()
        self.init_calculate_spo()

    def init_calculate_spo(self):
        self.__plan_itemTool = None
        self.__pipe_down = 0
        self.__pipe_up = 0
        self.__pipe_last = 0
        self.__pipe_all = 0
        self.data_spo = {
            'down': True,
            'Поднято': [0, 0],
            'Спущено': [0, 0],
            'Осталось': [0, 0],
            'Прогресс': 0
        }

    def calculate_spo(self):
        if self.__calculate_item_tool():
            pass

    def __calculate_item_tool(self):

        calculate = False

        if self.__plan_itemTool is None:
            self.__plan_itemTool = self.item_tool

        if self.calculate_plan_depth_tool(weight=False) and self.__plan_itemTool != self.plan_item_tool:
            # Направление
            self.data_spo['down'] = True if self.__plan_itemTool < self.plan_item_tool else False
            # Элементов в скважине
            self.__plan_itemTool = self.plan_item_tool

        # Если элементов в скважине меньше чем в компоновки то выходим
        if self.__plan_itemTool < len(self.composition):
            return False

        # Труб в скважине
        self.__pipe_down = self.__plan_itemTool - len(self.composition)

        # Спущено
        if self.__pipe_down < Gl.md['Последняя_труба'] or self.data_spo['down']:
            # Направление
            self.data_spo['down'] = True

            # Труб
            self.data_spo['Спущено'][0] = self.__pipe_down

            # свеч
            x = self.__pipe_down % Gl.md['Труб_в_свече']
            self.data_spo['Спущено'][1] = int((self.__pipe_down - x) / Gl.md['Труб_в_свече']) if x > 0 else int(self.__pipe_down / Gl.md['Труб_в_свече'])

            # Осталось спустить труб
            self.__pipe_last = Gl.md['Последняя_труба'] - self.__pipe_down
            self.data_spo['Осталось'][0] = self.__pipe_last

            # Осталось спустить свеч
            x = self.__pipe_last % Gl.md['Труб_в_свече']
            self.data_spo['Осталось'][1] = int((self.__pipe_last - x) / Gl.md['Труб_в_свече']) if x > 0 else int(self.__pipe_last / Gl.md['Труб_в_свече'])

            # Всего труб нужно спустить
            self.__pipe_all = Gl.md['Последняя_труба']

            calculate = True

        # Поднято
        if self.__pipe_down > Gl.md['Последняя_труба'] - 1 or not self.data_spo['down']:
            # Труб поднято со скважины
            self.__pipe_up = Gl.md['Кол_труб_до_подъема'] - self.__pipe_down

            # Направление
            self.data_spo['down'] = False

            # Труб
            self.data_spo['Поднято'][0] = self.__pipe_up

            # свеч
            x = self.__pipe_up % Gl.md['Труб_в_свече']
            self.data_spo['Поднято'][1] = int((self.__pipe_up - x) / Gl.md['Труб_в_свече']) if x > 0 else int(self.__pipe_up / Gl.md['Труб_в_свече'])

            # Осталось поднять труб
            self.__pipe_last = self.__pipe_down - (Gl.md['Последняя_труба'] - 1)
            self.data_spo['Осталось'][0] = self.__pipe_last

            # Осталось поднять свеч
            x = self.__pipe_last % Gl.md['Труб_в_свече']
            self.data_spo['Осталось'][1] = int((self.__pipe_last - x) / Gl.md['Труб_в_свече']) if x > 0 else int(self.__pipe_last / Gl.md['Труб_в_свече'])

            # Всего труб нужно поднять
            self.__pipe_all = Gl.md['Кол_труб_до_подъема'] - (Gl.md['Последняя_труба'] - 1)

            calculate = True

        if calculate:
            self.__calculate_progress_bar()
            return True

        return False

    def __calculate_progress_bar(self):

        # noinspection PyBroadException
        try:
            percent = 100 / (self.__pipe_all / (self.__pipe_all - self.__pipe_last))

            if percent >= 100:
                self.data_spo['Прогресс'] = 100
            else:
                self.data_spo['Прогресс'] = percent
        except:
            print(f"Деление на ноль")
