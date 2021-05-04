from ctypes import wintypes as w
from PyQt5.QtWidgets import QMessageBox
from MyLib.Windows import MessageBox as Msg
from datetime import datetime
from MyLib import Variables as Gl
import ctypes as c
import win32con
import win32api
import binascii
import psutil
import re
import struct
import platform


# Считываем карту оперативной памяти
class MemoryBasicInformation64(c.Structure):
    _fields_ = [
        ("BaseAddress", w.LARGE_INTEGER),
        ("AllocationBase", w.LARGE_INTEGER),
        ("AllocationProtect", w.DWORD),
        ("RegionSize", w.LARGE_INTEGER),
        ("State", w.DWORD),
        ("Protect", w.DWORD),
        ("Type", w.DWORD)
    ]


class MemoryBasicInformation32(c.Structure):
    _fields_ = [
        ("BaseAddress", w.DWORD),
        ("AllocationBase", w.DWORD),
        ("AllocationProtect", w.DWORD),
        ("RegionSize", w.UINT),
        ("State", w.DWORD),
        ("Protect", w.DWORD),
        ("Type", w.DWORD)
    ]


class Ram:
    def __init__(self, parent=None):

        self.mainWindow = parent

    # self.init_ram()

    def init_ram(self):

        self.PROCESS_VM_READ = 0x0010
        self.PROCESS_VM_WRITE = 0x0020
        self.PROCESS_VM_OPERATION = 0x0008
        self.PAGE_READWRITE = 0x04

        self.k32 = c.windll.kernel32

        self.OpenProcess = self.k32.OpenProcess
        self.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
        self.OpenProcess.restype = w.HANDLE

        self.ReadProcessMemory = self.k32.ReadProcessMemory
        self.ReadProcessMemory.argtypes = [w.HANDLE, w.LPCVOID, w.LPVOID, c.c_size_t, c.POINTER(c.c_size_t)]
        self.ReadProcessMemory.restype = w.BOOL

        self.GetLastError = self.k32.GetLastError
        self.GetLastError.argtypes = None
        self.GetLastError.restype = w.DWORD

        self.CloseHandle = self.k32.CloseHandle
        self.CloseHandle.argtypes = [w.HANDLE]
        self.CloseHandle.restype = w.BOOL

        self.WriteProcessMemory = self.k32.WriteProcessMemory
        self.VirtualProtectEx = self.k32.VirtualProtectEx

        self.pid = self.get_pid()

        checker = platform.architecture()
        self.is_64 = True if checker[0] == '64bit' else False

        if self.pid is None:
            Msg.Message(text='Программа регистрации не запущена \n запустите программу регистрации.', title='Внимание!!!!', button_1=QMessageBox.Cancel)
            return

        self.get_vm_map(self.pid, is_64=False)

        self.processHandle = self.OpenProcess(self.PROCESS_VM_READ | self.PROCESS_VM_WRITE | self.PROCESS_VM_OPERATION, 0, self.pid)

        self.readRam_result = None
        self.write_result = None
        self.find_pattern_result = None
        self.index_vm_map = 0
        self.text_progressBar = ""

    @staticmethod
    def get_pid():

        for process in psutil.process_iter():
            if "registr.exe" in str(process.name):
                return process.pid

    @staticmethod
    def get_time():
        print(datetime.now().strftime("%H:%M:%S"))

    def read_process_memory(self, address=None, bytes_read=None, my_structure=None, i_round=None):

        self.data = c.create_string_buffer(bytes_read)
        self.bytesRead = c.c_ulonglong() if self.is_64 else c.c_ulong()
        if not self.ReadProcessMemory(self.processHandle, address, c.byref(self.data), c.sizeof(self.data), c.byref(self.bytesRead)):
            self.readRam_result = None
            raise c.WinError()

        if my_structure is None:
            self.readRam_result = self.data
            return self.readRam_result
        else:
            self.readRam_result = round(struct.unpack(my_structure, self.data[0:])[0], i_round)
            return self.readRam_result

    def write_process_memory(self, address, data, buffer_size):
        # noinspection PyBroadException
        try:
            self.buffer = c.create_string_buffer(data)
            self.bytesWriten = c.c_ulong(0)

            self.old_protect = c.c_ulong(0)
            self.VirtualProtectEx(self.processHandle, address, buffer_size, self.PAGE_READWRITE, c.byref(self.old_protect))  # Разрешаем запись

            if not self.WriteProcessMemory(self.processHandle, address, c.byref(self.buffer), buffer_size, c.byref(self.bytesWriten)):  # Записываем
                self.write_result = None
                raise c.WinError()

            self.VirtualProtectEx(self.processHandle, address, buffer_size, self.old_protect.value, c.byref(self.old_protect))  # Запрещаем запись

            self.write_result = self.bytesWriten.value  # Результат
            self.get_time()

        except:
            print(f"Прочесть адрес: {address} не получилось :(")

    def find_pattern(self, pattern):

        self.readRam_result = None
        self.find_pattern_result = None
        self.get_vm_map(self.pid, is_64=False)

        for i in range(len(self.vm_map)):

            if i > len(self.vm_map) - 1:
                break

            while self.readRam_result is None:
                self.read_process_memory(self.vm_map[i][0], self.vm_map[i][3])
                if self.readRam_result is None:
                    self.get_vm_map(self.pid, is_64=False)

            if re.search(pattern, binascii.hexlify(self.readRam_result)):
                self.find_pattern_result = re.search(pattern, binascii.hexlify(self.readRam_result))
                self.index_vm_map = i
                break
            else:
                self.readRam_result = None

            # Посылаем сигнал на главное окно в прогресс бар
            self.mainWindow.Commun.dataChange_progressBar.emit({'i': i, 'Карта_памяти': self.vm_map, 'temp': self.text_progressBar})
        # time.sleep(0.02)

        # Посылаем сигнал на главное окно в прогресс бар
        self.mainWindow.Commun.dataChange_progressBar.emit({'i': len(self.vm_map), 'Карта_памяти': self.vm_map, 'temp': self.text_progressBar})

    def get_vm_map(self, pid, is_64=False):
        seg_protection_r = 4
        seg_protection_w = 2
        seg_protection_x = 1

        base = 0

        if self.is_64:
            mbi = MemoryBasicInformation64()
            address_type = w.LARGE_INTEGER
        else:
            mbi = MemoryBasicInformation32()
            address_type = w.DWORD
        process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, 0, pid)

        md = []
        while c.windll.kernel32.VirtualQueryEx(process.handle, address_type(base), c.byref(mbi), c.sizeof(mbi)) > 0:
            map_perm = 0
            if mbi.Protect & win32con.PAGE_EXECUTE:
                map_perm = seg_protection_x
            elif mbi.Protect & win32con.PAGE_EXECUTE_READ:
                map_perm = seg_protection_x | seg_protection_r
            elif mbi.Protect & win32con.PAGE_EXECUTE_READWRITE:
                map_perm = seg_protection_x | seg_protection_r | seg_protection_w
            elif mbi.Protect & win32con.PAGE_EXECUTE_WRITECOPY:
                map_perm = seg_protection_x | seg_protection_r
            elif mbi.Protect & win32con.PAGE_NOACCESS:
                map_perm = 0
            elif mbi.Protect & win32con.PAGE_READONLY:
                map_perm = seg_protection_r
            elif mbi.Protect == win32con.PAGE_READWRITE:
                map_perm = seg_protection_r | seg_protection_w
            elif mbi.Protect & win32con.PAGE_WRITECOPY:
                map_perm = seg_protection_r

            if map_perm == 6:
                md.append([mbi.BaseAddress, mbi.BaseAddress + mbi.RegionSize, map_perm, mbi.RegionSize])
            # print(str(mbi.BaseAddress) + "\t" + str(mbi.BaseAddress + mbi.RegionSize) + "\t" + str(map_perm) + "\t" +
            # 	  str(mbi.RegionSize))

            base += mbi.RegionSize

        win32api.CloseHandle(process)
        # print(md['Карта_памяти'])

        self.vm_map = md

        Gl.md['Карта_памяти'] = md
