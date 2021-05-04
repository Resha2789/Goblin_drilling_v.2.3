from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore


class Message:
	def __init__(self, text='', title='', button_1=None, button_2=None):
		self.text = text
		self.title = title
		self.button_1 = button_1
		self.button_2 = button_2
		self.result = None
		
		self.init_message()
	
	def init_message(self):
		self.msgBox = QMessageBox()
		# noinspection PyTypeChecker
		self.msgBox.setWindowFlags(self.msgBox.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
		self.msgBox.setIcon(QMessageBox.Information)
		self.msgBox.setText(self.text)
		self.msgBox.setWindowTitle(self.title)
		
		if self.button_2 is None:
			self.msgBox.setStandardButtons(self.button_1)
		else:
			self.msgBox.setStandardButtons(self.button_1 | self.button_2)
		
		self.result = self.msgBox.exec()

# msgBox.setText('Программа регистрации не запущена \n запустите программу регистрации.')
