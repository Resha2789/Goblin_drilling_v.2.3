import PyInstaller.__main__
import shutil

def install(name='Name'):

    src_data = f"D:\Programming\Python\Goblin_drilling_v.2.3\Нужное"
    dst_data = f"Z:\Плагин_goblin_v2.4\\Нужное_2"
    try:
        shutil.rmtree(dst_data)
    except FileNotFoundError:
        print('Файл не найден!')

    shutil.copytree(src_data, dst_data, ignore=shutil.ignore_patterns('*.pyc', 'tmp*'))

    PyInstaller.__main__.run([
        "Main.py",
        "--noconsole",
        "--onefile",
        f"--icon=D:\Programming\Python\Goblin_drilling_v.2.3\Нужное\icon-robots-72.ico",
        f"--distpath=Z:\Плагин_goblin_v2.4\\",
        f"-n={name}"
    ])

if __name__ == '__main__':
    install(name='Goblin_v2.5')
