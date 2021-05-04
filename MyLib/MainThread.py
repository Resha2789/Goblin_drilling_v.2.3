from MyLib.LibClass import NblExtended, ReadAddress, ReadParameters, GetDataMainWindow, ExceptHook, NotesPipe, FixTal, CalculateDrilling, CalculateSpo
from PyQt5.QtCore import QThread
from PyQt5 import QtCore
from MyLib import Variables as Gl


# Объект, который будет перенесён в другой поток для выполнения кода
class MainThreading(QThread, NblExtended, ReadAddress, ReadParameters, GetDataMainWindow, ExceptHook, NotesPipe, FixTal, CalculateDrilling, CalculateSpo):
	def __init__(self, parent=None):
		super().__init__()
		self.mainWindow = parent
		self.init_main_threading()
	
	def init_main_threading(self):
		
		# При ошибки не будет закрываться окно
		self.init_except_hook()
		
		# Инициализируем эксземпляр класса ReadAddress
		self.init_read_address()
		
		# Инициализируем эксземпляр класса Ram
		self.init_ram()
		
		# Инициализируем эксземпляр класса InpGti
		self.init_inp_gti()
		
		# Инициализируем эксземпляр класса EditParameter
		self.init_edit_parameter()
		
		# Инициализируем эксземпляр класса ReadParameters
		self.init_read_parameters()
		
		# Инициализируем эксземпляр класса Operation
		self.init_operation()
		
		# Инициализируем эксземпляр класса SPO
		self.init_spo()
		
		# Инициализируем эксземпляр класса NotesPipe
		self.init_notes_pipe()
		
		# Инициализируем эксземпляр класса FixTal
		self.init_fix_tal()
		
		# Инициализируем эксземпляр класса CalculateDrilling
		self.init_calculate_drilling()
		
		# Инициализируем эксземпляр класса CalculateSpo
		self.init_calculate_spo()
		
		# Инициализируем эксземпляр класса SetData_mainWindow
		self.init_set_data_main_window()
		
		# Считываем промер регистрации
		if not self.read_tools():
			return
		
		# Чтение registr.nbl.extended (Названии параметров)
		if not self.read_nbl_extended():
			return
		
		# Считываем адреса в RAM и их значения
		if not self.read_address():
			return
	
	# Метод, который будет выполнять алгоритм в другом потоке
	def run(self):
		while self.mainWindow.groupBox_deepControl.isChecked():
			
			# Считываем значения параметров
			self.read_parameters()
			
			# Получаем значения полей для главного окна
			self.get_data_for_main_window()
			
			# Распознование операции
			self.get_direction_spo()
			self.get_build_up_time()
			
			# Установка заметок о колличестве труб
			if self.mainWindow.groupBox_spo_notes.isChecked():
				self.set_notes_pipe()
			
			# Коррекция тальблока
			if self.mainWindow.checkBox_tal.isChecked():
				self.fix_tal()
			
			# Сброс своист на начальные значения
			self.reset_properties()
			
			# Коррецкия глубины долота при СПО
			self.spo()
			
			# Посылаем сигнал из второго потока в GUI поток в окно goblin_window
			self.mainWindow.Commun.dataChange_mainWindow.emit(Gl.pr)
			
			# Посылаем сигнал из второго потока в GUI поток в окно drilling_window
			if self.mainWindow.win_drilling:
				self.calculate_drilling()
				self.mainWindow.Commun.data_change_drilling.emit(self.data_drilling)
			
			# Посылаем сигнал из второго потока в GUI поток в окно spo_window
			if self.mainWindow.win_spo:
				self.calculate_spo()
				self.mainWindow.Commun.data_change_spo.emit(self.data_spo)
			
			QtCore.QThread.msleep(3000)
