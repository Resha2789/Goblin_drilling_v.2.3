pyinstaller --onefile --noconsole --distpath V:\ Goblin.py
pyinstaller --onefile --noconsole --distpath D:\Programming\Python\Goblin_drilling_v.2.1\dist\Goblin.py
pyinstaller --onefile --noconsole --distpath Z:\Плагин_goblin_v2.2\ -n Goblin_v2.2 Main.py

pyuic5 D:\Programming\Python\Goblin_drilling_v.2.2\Lib\site-packages\QtDesigner\Main_win.ui -o Lib\site-packages\myLibrary\Main_win.py

pyuic5 D:\Programming\Python\Goblin_drilling_v.2.2\Lib\site-packages\QtDesigner\Spo_win.ui -o Lib\site-packages\myLibrary\Spo_win.py

pyuic5 D:\Programming\Python\Goblin_drilling_v.2.2\Lib\site-packages\QtDesigner\Drilling_win.ui -o Lib\site-packages\myLibrary\Drilling_win.py

pyuic5 D:\Programming\Python\Goblin_drilling_v.2.2\Lib\site-packages\QtDesigner\Diolog_win.ui -o Lib\site-packages\myLibrary\Diolog_win.py

Для удаления файлов и папок с git
git rm -r --cached folder_or_file
