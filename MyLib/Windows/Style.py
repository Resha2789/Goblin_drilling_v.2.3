from Main import MainWindow
from MyLib import Variables as Gl


class CustomStyle:
    def __init__(self, parent=None, widget=None, style=None):
        m: MainWindow
        m = parent

        self.m = m
        self.style_data = None

        self.style_pushButton_Start = "#pushButton_Start{background-color: rgba(255, 0, 0, 40%);}" \
                                      "#pushButton_Start:hover{background: rgba(255, 0, 0, 60%); color: rgb(255, 255, 255);}" \
                                      "#pushButton_Start:pressed{background: rgba(255, 0, 0, 50%); color: rgb(255, 255, 255);" \
                                      "border: 1px outset gray;}"

        self.style_pushButton_drilling = "#pushButton_drilling{background: rgba(255,255,255,40%); border-radius: 5px; border: 2px outset gray;}" \
                                         "#pushButton_drilling:hover{background: rgba(255,255,255,60%); color: rgb(0, 0, 0);}" \
                                         "#pushButton_drilling:pressed{background: rgba(255,255,255,50%); color: rgb(0, 0, 0);}"

        self.style_pushButton_spo = "#pushButton_spo{background: rgba(255,255,255,40%); border-radius: 5px; border: 2px outset gray;}" \
                                    "#pushButton_spo:hover{background: rgba(255,255,255,60%); color: rgb(0, 0, 0);}" \
                                    "#pushButton_spo:pressed{background: rgba(255,255,255,50%); color: rgb(0, 0, 0);}"

        self.style_label = f".QLabel{{color: rgb{Gl.md['Цвет_надписей'][0]};}}"
        self.style_pushButton_color_label = f"#pushButton_color_label{{color: rgb{Gl.md['Цвет_надписей'][0]};}}"
        self.style_pushButton_color_button = f"#pushButton_color_button{{color: rgb{Gl.md['Цвет_надписей_кнопок'][0]};}}"
        self.style_pushButton_color_line_edit = f"#pushButton_color_line_edit{{color: rgb{Gl.md['Цвет_значений'][0]};}}"
        self.style_pushButton = f".QPushButton{{background: rgba(255,255,255,40%); " \
                                f"color: rgb{Gl.md['Цвет_надписей_кнопок'][0]}; " \
                                f"border-radius: 5px; " \
                                f"border: 2px outset gray;}}"
        self.style_lineEdit = f".QLineEdit, .QSpinBox, " \
                              f".QDoubleSpinBox{{" \
                              f"border-radius: 3px; color: rgb{Gl.md['Цвет_значений'][0]};" \
                              f"border: 2px inset gray;" \
                              "box-shadow: 10px 10px 5px rgba(182, 191, 193, 0.5);" \
                              f"}}"
        self.style_frame_Main = f"#frame_Main{{background-image: url({Gl.md['Фоновая_картинка']}); " \
                                f"border:0px; background-repeat: no-repeat; background-position: center;}}"

    def set_style(self):
        self.get_style()
        self.m.setStyleSheet(self.style_data)

    def get_style(self):
        self.style_data = \
            f"{self.style_pushButton_Start}" \
            f"{self.style_pushButton_drilling}" \
            f"{self.style_pushButton_spo}" \
            f"{self.style_pushButton_color_label}" \
            f"{self.style_pushButton_color_button}" \
            f"{self.style_pushButton_color_line_edit}" \
            f"{self.style_lineEdit}" \
            f"{self.style_frame_Main}" \
            ".QLineEdit[readOnly='true']{ background: rgb(230,230,230) }" \
            ".QDoubleSpinBox[readOnly='true']{ background: rgb(193,193,193) }" \
            ".QLineEdit::disabled{ background: rgb(193,193,193) }" \
            ".QDoubleSpinBox::disabled{ background: rgb(193,193,193) }" \
            ".QSpinBox::disabled{ background: rgb(193,193,193) }" \
            "#textBrowser_console{font: 10pt Arial;}" \
            "#plainTextEdit_about{background: rgba(0,0,0,30%);}" \
            "#textBrowser_console{background: rgba(0,0,0,50%); color: rgb(255, 255, 255);}" \
            "#plainTextEdit_about{background: rgba(0,0,0,30%); color: rgb(255, 255, 255);}" \
            f"{self.style_label}" \
            ".QLabel::disabled{color: gray;}" \
            f".QCheckBox{{color: rgb{Gl.md['Цвет_надписей'][0]};}}" \
            ".QCheckBox:hover{color: rgb(150, 255, 150);}" \
            ".QCheckBox::indicator:checked{image: url(Нужное/галочка.ico);}" \
            ".QCheckBox::indicator:unchecked{image: url(Нужное/крестик.ico);}" \
            f"{self.style_pushButton}" \
            ".QPushButton:hover{background: rgba(255,255,255,60%); color: rgb(0, 0, 0);}" \
            ".QPushButton:pressed{background: rgba(255,255,255,50%); color: rgb(0, 0, 0);}" \
            "#pushButton_updata_tools{background: rgba(255,255,255,90%); color: rgb(0, 0, 0); border: 2px outset silver;}" \
            "#pushButton_updata_tools:hover{background: rgba(255,255,255,100%); color: rgb(0, 0, 0);}" \
            "#pushButton_updata_tools:pressed{background: rgba(255,255,255,90%); border: 1px outset gray;}" \
            "#groupBox_6,#groupBox_8,#groupBox_9{border: 0px} " \
            ".QGroupBox::title:hover{color: rgb(150, 255, 150);}" \
            ".QGroupBox::indicator:checked{image: url(Нужное/галочка.ico);}" \
            ".QGroupBox::indicator:unchecked{image: url(Нужное/крестик.ico);}" \
            ".QGroupBox::disabled{color: gray;}" \
            ".QCheckBox::disabled{color: gray;}" \
            ".QGroupBox{border: 1px outset gray; " \
            "border-radius: 6px; " \
            "subcontrol-origin: margin; " \
            "subcontrol-position: top left; " \
            "padding-top: 10px; " \
            "padding-left: 3px; " \
            "padding-right: 3px; " \
            "padding-bottom: 3px; " \
            "color: rgb(250, 176, 0);}"
