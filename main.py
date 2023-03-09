import os
import json
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QGridLayout, QGroupBox, QPushButton, QWidget

from main_ui import Ui_MainWindow
from pair_dataset import PairingDataset

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # in python3, super(Class, self).xxx = super().xxx
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        
        self.sub_window = SubWindow()
        self.pop_up_window = PopUpWindow()
        

        with open("layout_config.json") as f:
            self.layout_congfig = json.load(f)

        self.devices_layout_config = self.layout_congfig["Device Layout"]
        
        self.channels = 96

        self.device_buttom = dict()
        self.target_buttom = dict()

        self.temp_pair_table = [0, 0]

        self.pair_dataset = list()

        self.ui.setupUi(self)

        self.get_device_and_info()

        self.setup_control()

        


        self.ui.comboBox.currentTextChanged.connect(self.update_device)
        self.ui.comboBox_2.currentTextChanged.connect(self.update_target)

    def setup_control(self):
        # TODO
        self.ui.output.clicked.connect(self.output_to_json)

        self.update_device()
        self.update_target()

        print(self.target_buttom)
        

    def output_to_json(self):
        ret, msg = pairing_dataset.save_json()
        if ret:
            self.pop_up_window.show_output_json_message(True)
        else:
            self.pop_up_window.show_output_json_message(False, msg)
        
    
    def update_device(self):
        self.device_mac = self.ui.comboBox.currentText()
        self.device_channels = self.default_data[self.device_mac]["channels"]
        self.device_buttom = dict()
        self.create_btns(object=self.device_buttom, 
                         click_func=self.click_device, 
                         device_type=self.default_data[self.device_mac]["type"], 
                         layout_group=self.ui.device_button_group)
        
        device_type = self.default_data[self.device_mac]["type"]
        self.ui.device_title.setText(f"配對裝置 {device_type} - {self.device_mac.upper()}")
        # self.create_port_button(object="device", channels=self.device_channels)
        

    def update_target(self):
        self.target_mac = self.ui.comboBox_2.currentText()
        self.target_channels = self.default_data[self.target_mac]["channels"]
        self.target_buttom = dict()
        self.create_btns(object=self.target_buttom, 
                         click_func=self.click_target, 
                         device_type=self.default_data[self.target_mac]["type"], 
                         layout_group=self.ui.target_button_group)

        device_type = self.default_data[self.target_mac]["type"]
        self.ui.target_title.setText(f"目標裝置 {device_type} - {self.target_mac.upper()}")
        # self.create_port_button(object="target", channels=self.target_channels)
        


    def get_device_and_info(self):
        self.device_list = []
        with open("virtual.json") as f:
            self.default_data = json.load(f)
            self.device_list = self.default_data.keys()

        self.ui.comboBox.addItems(self.device_list)
        self.ui.comboBox_2.addItems(self.device_list)

    def create_port_button(self, object="device", channels={}):
        if object == "device":
            count = 0
            grid = QGridLayout()
            for row in range(2):
                for col in range(8):
                    # 建立每個grid
                    group_box = QGroupBox(f"Port {row*8+col+1}")  # 按照順序編號
                    group_box.setAlignment(QtCore.Qt.AlignCenter)
                    group_layout = QGridLayout()

                    # 建立每個grid內的button
                    for i in range(2):
                        for j in range(3):
                            count += 1
                            if i == 0:
                                btn = CustomButton(text=f"{count}", channel_type="Input")
                            else:
                                btn = CustomButton(text=f"{count}", channel_type="Output")
                            btn.clicked.connect(self.click_device)
                            group_layout.addWidget(btn, i, j)
                            self.device_buttom[count] = btn

                    # 將grid的layout設為每個group box的layout
                    group_box.setLayout(group_layout)

                    # 將每個group box加入到grid中
                    grid.addWidget(group_box, row, col)
            self.ui.device_button_group.setLayout(grid)
        elif object == "target":
            count = 0
            grid = QGridLayout()
            for row in range(1):
                for col in range(1):
                    # 建立每個grid
                    group_box = QGroupBox()
                    group_box.setAlignment(QtCore.Qt.AlignCenter)
                    group_layout = QGridLayout()

                    # 建立每個grid內的button
                    for i in range(1):
                        for j in range(8):
                            count += 1
                            btn = CustomButton(text=f"{count}")
                            btn.clicked.connect(self.click_target)
                            group_layout.addWidget(btn, i, j)
                            self.target_buttom[count] = btn

                    # 將grid的layout設為每個group box的layout
                    group_box.setLayout(group_layout)

                    # 將每個group box加入到grid中
                    grid.addWidget(group_box, row, col)
            self.ui.target_button_group.setLayout(grid)


    def click_device(self):
        sender = self.sender()
        print("Device click: ", sender.text())
        self.temp_pair_table[0] = sender.text()
        for i in self.device_buttom.keys():
            if self.device_buttom[i].text() != sender.text():
                self.device_buttom[i].setEnabled(False)
                self.device_buttom[i].set_btn_disable()

    def click_target(self):
        if self.temp_pair_table[0] == 0:
            return 
        sender = self.sender()
        print("Target click: ", sender.text())
        self.temp_pair_table[1] = sender.text()
        for i in self.target_buttom.keys():
            if self.target_buttom[i].text() != sender.text():
                self.target_buttom[i].setEnabled(False)
        self.show_sub_window(self.temp_pair_table)

    
    def show_sub_window(self, temp_pair_table):
        cmd_list = self.device_channels.get(temp_pair_table[0])
        target_cmd_list = self.target_channels.get(temp_pair_table[1])
        
        self.sub_window.info_title.setText(f"配對裝置: endpoint {temp_pair_table[0]}, 配對目標: endpoint {temp_pair_table[1]}")
        self.sub_window.create_config_item(config=["level", "duration", "timeout", "delay"], 
                                            command_list=cmd_list, target_command_list=target_cmd_list)
        self.sub_window.show()

    

    def create_btns(self, 
                    object, 
                    click_func, 
                    device_type, 
                    layout_group):

        if layout_group.layout():
            QWidget().setLayout(layout_group.layout())
        print("Click Function", click_func)
            
        count = 0
        grid = QGridLayout()
        config = self.devices_layout_config.get(device_type)
        ROWs, COLs, btnROWs, btnCOLs = config["rows"], config["cols"], config["btn_rows"], config["btn_cols"]
        for row in range(ROWs):
            for col in range(COLs):
                # 建立每個grid
                group_box = QGroupBox()
                group_box.setAlignment(QtCore.Qt.AlignCenter)
                group_layout = QGridLayout()

                # 建立每個grid內的button
                for i in range(btnROWs):
                    for j in range(btnCOLs):
                        count += 1
                        if device_type == "SCU" or device_type == "SCULite":
                            if i == 0:
                                btn = CustomButton(text=f"{count}", channel_type="Input")
                            else:
                                btn = CustomButton(text=f"{count}", channel_type="Output")
                        else:
                            btn = CustomButton(text=f"{count}")
                        btn.clicked.connect(click_func)
                        group_layout.addWidget(btn, i, j)
                        object[count] = btn

                # 將grid的layout設為每個group box的layout
                group_box.setLayout(group_layout)

                # 將每個group box加入到grid中
                grid.addWidget(group_box, row, col)
        layout_group.setLayout(grid)
        del grid
       

class SubWindow(QtWidgets.QWidget):
    def __init__(self):
        super(SubWindow, self).__init__()
        self.resize(640, 480)

        # Title
        self.info_title = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(14)
        self.info_title.setFont(font)
        self.info_title.setGeometry(QtCore.QRect(20, 10, 620, 40))
        self.info_title.setAlignment(QtCore.Qt.AlignCenter)
        self.info_title.setObjectName("info_title")

        # Button
        self.submit = QtWidgets.QPushButton(self)
        self.submit.setText("確認")
        self.submit.setStyleSheet("font-size:20px")
        self.submit.setGeometry(QtCore.QRect(240, 430, 140, 40))
        self.submit.clicked.connect(self.submit_setting)

        # Detail
        self.cmd_title = QtWidgets.QLabel(self)
        self.cmd_title.setGeometry(QtCore.QRect(120, 60, 140, 40))
        self.cmd_combobox = QtWidgets.QComboBox(self)
        self.cmd_combobox.setGeometry(QtCore.QRect(260, 60, 280, 40))

        self.target_cmd_title = QtWidgets.QLabel(self)
        self.target_cmd_title.setGeometry(QtCore.QRect(120, 120, 140, 40))
        self.target_cmd_combobox = QtWidgets.QComboBox(self)
        self.target_cmd_combobox.setGeometry(QtCore.QRect(260, 120, 280, 40))

        self.level_edit = QtWidgets.QLineEdit(self)
        self.level_edit.setGeometry(QtCore.QRect(260, 180, 280, 40))
        self.level_edit.setObjectName("level_edit")
        
        self.duration_edit = QtWidgets.QLineEdit(self)
        self.duration_edit.setGeometry(QtCore.QRect(260, 240, 280, 40))
        self.duration_edit.setObjectName("duration_edit")
        
        self.timeout_edit = QtWidgets.QLineEdit(self)
        self.timeout_edit.setGeometry(QtCore.QRect(260, 300, 280, 40))
        self.timeout_edit.setObjectName("timeout_edit")
        
        self.delay_edit = QtWidgets.QLineEdit(self)
        self.delay_edit.setGeometry(QtCore.QRect(260, 360, 280, 40))
        self.delay_edit.setObjectName("delay_edit")
        
        self.level_edit.setVisible(False)
        self.duration_edit.setVisible(False)
        self.timeout_edit.setVisible(False)
        self.delay_edit.setVisible(False)
        
        self.level_edit.setValidator(QIntValidator())
        self.duration_edit.setValidator(QIntValidator())
        self.timeout_edit.setValidator(QIntValidator())
        self.delay_edit.setValidator(QIntValidator())

    def create_config_item(self, config=["timeout", "delay"], command_list=[], target_command_list=[]):
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(12)
        self.cmd_title.setFont(font)
        self.cmd_title.setText("Device cmd")
        self.cmd_combobox.setFont(font)
        self.cmd_combobox.addItems(command_list)
        
        self.target_cmd_title.setFont(font)
        self.target_cmd_title.setText("Target cmd")
        self.target_cmd_combobox.setFont(font)
        self.target_cmd_combobox.addItems(target_command_list)

        config_table = {
            "level": ["level", self.level_edit, "255"],
            "duration": ["duration", self.duration_edit, "50"],
            "timeout": ["timeout (ms)", self.timeout_edit, "1000"],
            "delay": ["delay (ms)", self.delay_edit, "0"]
        } 

        for i in range(len(config)):
            
            # Text
            label = QtWidgets.QLabel(self)
            label.setFont(font)
            label.setText(config_table[config[i]][0])
            label.setGeometry(QtCore.QRect(120, 180 + i*60, 140, 40))

            # Edit
            edit = config_table[config[i]][1]
            edit.setText(config_table[config[i]][2])
            edit.setGeometry(QtCore.QRect(260, 185 + i*60, 280, 35))
            edit.setFont(font)
            edit.setVisible(True)
            

    def submit_setting(self):
        device_mac = window.ui.comboBox.currentText()
        device_endpoint = window.temp_pair_table[0]
        device_cmd = self.cmd_combobox.currentText()
        target_info = {
            "cmd": self.target_cmd_combobox.currentText(),
            "mac-addr": window.ui.comboBox_2.currentText(),
            "endpoint": window.temp_pair_table[1]
        }
        target_info["level"] = int(self.level_edit.text())
        target_info["duration"] = int(self.duration_edit.text())
        target_info["timeout"] = int(self.timeout_edit.text())
        target_info["delay"] = int(self.delay_edit.text())
        
        print(f"Before submit:\n{pairing_dataset.pair_dataset}")
        result = pairing_dataset.add_to_device(mac=device_mac,
                endpoint=device_endpoint,
                cmd=device_cmd,
                target_action_info=target_info
        )
        print(f"After submit:\n{pairing_dataset.pair_dataset}")

        self.close()

    def closeEvent(self, event):
        # do stuff
        window.temp_pair_table = [0, 0]
        for i in window.device_buttom.keys():
            window.device_buttom[i].setEnabled(True)
        for i in window.target_buttom.keys():
            window.target_buttom[i].setEnabled(True)

        self.cmd_combobox.clear()
        self.target_cmd_combobox.clear()
        
        self.level_edit.clear()
        self.duration_edit.clear()
        self.timeout_edit.clear()
        self.delay_edit.clear()
        
        event.accept()

class WarningWindow(QtWidgets.QWidget):
    def __init__(self):
        super(WarningWindow, self).__init__()
        self.resize(320, 240)

class PopUpWindow(QtWidgets.QWidget):
    def __init__(self):
        super(PopUpWindow, self).__init__()
        self.resize(320, 240)

        self.button = QtWidgets.QPushButton(self)
        self.button.setText("確認")
        self.button.setStyleSheet("font-size:16px")
        self.button.setGeometry(QtCore.QRect(100, 200, 120, 30))
        self.button.clicked.connect(self.close)

    def show_output_json_message(self, result, message=""):
        self.msg = QtWidgets.QLabel(self)
        self.msg.setGeometry(QtCore.QRect(60, 40, 200, 120))
        self.msg.setAlignment(QtCore.Qt.AlignCenter)
        self.msg.setStyleSheet("font-size:20px")
        self.msg.setWordWrap(True)

        if result:
            self.msg.setText("輸出JSON檔成功!!")
        else:
            self.msg.setText(f"輸出JSON檔失敗: {message}")

        self.show()

    def closeEvent(self, event):
        self.msg.clear()
        event.accept()


class CustomButton(QPushButton):
    def __init__(self, text, channel_type=""):
        super().__init__(text)
        self.button_type = channel_type
        self.channel_number = text
        self.setup_button()
        self.setMouseTracking(True)  # 啟用滑鼠追蹤，這樣才能在鼠標不點擊的情況下接收 enter 和 leave 事件

    def setup_button(self):
        # Normal Channel
        bg_color = "ECF2FF"
        hover_bg = "3E54AC"
        hover_color = "FFFFFF"

        # Input/Output Channel
        if self.button_type == "Input":
            bg_color = "D7E9B9"
        elif self.button_type == "Output":
            bg_color = "FFC6D3"

        self.setStyleSheet(f'''
            QPushButton {{
                border: 1.5px solid #332C39;
                border-radius: 7px;
                padding: 5px 1px;
                font-size: 20px;
                font-weight: bold;
                font-family: Consolas;
                background-color: #{bg_color};
            }}
            QPushButton:hover {{
                border: 1.5px solid #95BDFF;
                background-color: #{hover_bg};
                color: #{hover_color};
            }}
        ''')

    def set_btn_disable(self):
        # Change StyleSheet

        pass

    def show_pair_connection(self):
        pass

    def enterEvent(self, event):
    #     # Check pair table
    #     # self.setStyleSheet('''
        
    #     # ''')
        pass

    # def leaveEvent(self, event):
    #     pass

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    pairing_dataset = PairingDataset()
    
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
