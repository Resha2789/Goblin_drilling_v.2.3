pyinstaller --onefile --noconsole --distpath V:\ Goblin.py
pyinstaller --onefile --noconsole --distpath D:\Programming\Python\Goblin_drilling_v.2.1\dist\Goblin.py
pyinstaller --onefile --noconsole --distpath Z:\Плагин_goblin_v2.4\ -n Goblin_v2.4 Main.py

pyuic5 D:\Programming\Python\Goblin_drilling_v.2.2\Lib\site-packages\QtDesigner\Main_win.ui -o MyLib\Windows\My_pyqt5\Main_win.py

pyuic5 D:\Programming\Python\Goblin_drilling_v.2.2\Lib\site-packages\QtDesigner\Spo_win.ui -o Lib\site-packages\myLibrary\Spo_win.py

pyuic5 D:\Programming\Python\Goblin_drilling_v.2.2\Lib\site-packages\QtDesigner\Drilling_win.ui -o Lib\site-packages\myLibrary\Drilling_win.py

pyuic5 D:\Programming\Python\Goblin_drilling_v.2.2\Lib\site-packages\QtDesigner\Diolog_win.ui -o Lib\site-packages\myLibrary\Diolog_win.py

Для удаления файлов и папок с git
git rm -r --cached folder_or_file

# Используемые библиотеки
PyQt5	5.15.4	5.15.4
PyQt5-Qt5	5.15.2	5.15.2
PyQt5-sip	12.8.1	12.9.0
altgraph	0.17	0.17
future	0.18.2
pefile	2019.4.18
pip	21.1.1
psutil	5.8.0
pyinstaller	4.3
pyinstaller-hooks-contrib	2021.1
pywin32	300
pywin32-ctypes	0.2.0
setuptools	56.0.0
