import json
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QWidget, QGridLayout, QVBoxLayout, QScrollArea, QHBoxLayout

from layout.main_ui import Ui_MainWindow
from layout.pairwindow_ui import Ui_PairWindow
from pair_dataset import PairDataset

"""
 - MainWindow: The homepage of this application
 - PairWindow: For user type command detail
 - PopUpWindow: For displaying any message
"""

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        

        self.pop_up_window = PopUpWindow()
        self.pair_window = PairWindow()
        
        # Different device's button layout
        with open("configs/layout_config.json") as f:
            self.layout_congfig = json.load(f)

        self.devices_layout_config = self.layout_congfig["Device Layout"]
        
        self.device_buttom = dict()
        self.target_buttom = dict()

        # For record new pair information
        self.temp_pair_table = [0, 0]

        
        # Initial UI
        self.ui.setupUi(self)
        self.setWindowTitle("配對工具")
        self.get_device_and_info()
        self.setup_control()
    
    
    def setup_control(self):
        self.ui.output.clicked.connect(self.output_to_json)
        self.ui.comboBox.currentTextChanged.connect(self.update_device)
        self.ui.comboBox_2.currentTextChanged.connect(self.update_target)

        # First Update btns in two group 
        self.update_device()
        self.update_target()
        
    
    def get_device_and_info(self):
        self.device_list = []
        with open("configs/virtual.json") as f:
            self.default_data = json.load(f)
            self.device_list = self.default_data.keys()

        self.ui.comboBox.addItems(self.device_list)
        self.ui.comboBox_2.addItems(self.device_list)

    
    def update_device(self):
        self.device_mac = self.ui.comboBox.currentText()
        self.device_channels = self.default_data[self.device_mac]["channels"]
        self.device_buttom = dict()
        self.create_btns(object=self.device_buttom, 
                         click_func=self.click_device, 
                         device_type=self.default_data[self.device_mac]["type"], 
                         layout_group=self.ui.device_button_group,
                         mac=self.device_mac,
                         space="device")
        
        device_type = self.default_data[self.device_mac]["type"]
        self.ui.device_title.setText(f"來源裝置 {device_type} - {self.device_mac.upper()}")
        

    def update_target(self):
        self.target_mac = self.ui.comboBox_2.currentText()
        self.target_channels = self.default_data[self.target_mac]["channels"]
        self.target_buttom = dict()
        self.create_btns(object=self.target_buttom, 
                         click_func=self.click_target, 
                         device_type=self.default_data[self.target_mac]["type"], 
                         layout_group=self.ui.target_button_group,
                         mac=self.target_mac,
                         space="target")

        device_type = self.default_data[self.target_mac]["type"]
        self.ui.target_title.setText(f"目標裝置 {device_type} - {self.target_mac.upper()}")
        

    def click_device(self):
        sender = self.sender()
        print("Device click: ", sender.text())
        self.temp_pair_table[0] = sender.text()
        for i in self.device_buttom.keys():
            if self.device_buttom[i].text() != sender.text():
                self.device_buttom[i].set_btn_status(False)


    def click_target(self):
        if self.temp_pair_table[0] == 0:
            return 
        sender = self.sender()
        print("Target click: ", sender.text())
        self.temp_pair_table[1] = sender.text()

        try:
            self.show_pair_window(self.temp_pair_table)
            for i in self.target_buttom.keys():
                if self.target_buttom[i].text() != sender.text():
                    self.target_buttom[i].set_btn_status(False)
        except Exception as e:
            self.release_btns()
            self.pop_up_window.show_warning_message()
            print(e)


    def create_btns(self, 
                    object, 
                    click_func, 
                    device_type, 
                    layout_group,
                    mac,
                    space):

        if layout_group.layout():
            QWidget().setLayout(layout_group.layout())
            
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
                                btn = CustomButton(text=f"{count}", channel_type="Input", mac=mac, space=space)
                            else:
                                btn = CustomButton(text=f"{count}", channel_type="Output", mac=mac, space=space)
                        else:
                            btn = CustomButton(text=f"{count}", mac=mac, space=space)
                        btn.clicked.connect(click_func)
                        group_layout.addWidget(btn, i, j)
                        object[count] = btn

                # 將grid的layout設為每個group box的layout
                group_box.setLayout(group_layout)

                # 將每個group box加入到grid中
                grid.addWidget(group_box, row, col)
        layout_group.setLayout(grid)
        del grid


    def show_pair_connection(self, mac, endpoint, space, target_list=[], is_pair=False):
        for i in target_list:
            target_channel, target_mac = i[0], i[1]
            if space == "device":
                if target_mac != self.target_mac:
                    continue
                self.target_buttom[target_channel].show_pair_connection(is_pair=is_pair)
            else:
                if target_mac != self.device_mac:
                    continue
                self.device_buttom[target_channel].show_pair_connection(is_pair=is_pair)


    def show_pair_window(self, temp_pair_table):
        cmd_list = self.device_channels.get(temp_pair_table[0])
        target_cmd_list = self.target_channels.get(temp_pair_table[1])
        dataset = pair_dataset.current_dataset

        self.pair_window.init_cmd(source_command_list=cmd_list, target_command_list=target_cmd_list)
        self.pair_window.show_window(self.device_mac, self.target_mac, temp_pair_table[0], temp_pair_table[1], dataset)


    def release_btns(self):
        for i in self.device_buttom.keys():
            self.device_buttom[i].set_btn_status(True)
        for i in self.target_buttom.keys():
            self.target_buttom[i].set_btn_status(True)

    
    def output_to_json(self):
        ret, msg = pair_dataset.save_json()
        if ret:
            self.pop_up_window.show_output_json_message(True)
        else:
            self.pop_up_window.show_output_json_message(False, msg)
       

class PairWindow(QtWidgets.QWidget):
    def __init__(self):
        super(PairWindow, self).__init__()
        self.ui = Ui_PairWindow()
        self.ui.setupUi(self)
        

    def show_window(self, source_mac, target_mac, source_endpoint, target_endpoint, dataset):
        self.source_mac = source_mac
        self.target_mac = target_mac
        self.source_endpoint = source_endpoint
        self.target_endpoint = target_endpoint
        self.dataset = dataset

        self.ui.source_title.setText(source_mac.upper())
        self.ui.source_channel.setText(source_endpoint)
        self.ui.target_title.setText(target_mac.upper())
        self.ui.target_channel.setText(target_endpoint)

        self.add_exist_pair()
        self.ui.add.clicked.connect(self.submit_setting)
        self.ui.confirm.clicked.connect(self.close)
        self.show()

    def add_exist_pair(self):
        if self.ui.cmd_group.layout():
            QWidget().setLayout(self.ui.cmd_group.layout())

        h_layout = QHBoxLayout()
        widget = QWidget(self.ui.cmd_group)
        
        layout = QVBoxLayout()
        scroll_area = QScrollArea()

        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(12)

        data = self.dataset.get(self.source_mac)
        if data != None:
            for pair in data:
                if pair['endpoint'] == int(self.source_endpoint) and pair.get('actions') != None:
                    cmd = pair['cmd']
                    for action in pair['actions']:
                        output_str = ""
                        if action['endpoint'] == int(self.target_endpoint) and action['mac-addr'] == self.target_mac:
                            for key, value in action.items():
                                if key != "endpoint" and key != "mac-addr" and key != "cmd":
                                    output_str += f", {key}:{value}"
                            text = f"{cmd} -> {action['cmd']}{output_str}"
                            object = QLabel("TextLabel")
                            object.setText(text)
                            object.setFont(font)
                            layout.addWidget(object)

        widget.setLayout(layout)
        scroll_area.setWidget(widget)
        scroll_area.setStyleSheet('''
            QScrollArea {
                border: 1px solid #2D2727;
                background-color: #EEEEEE;
            }
        ''')
        h_layout.addWidget(scroll_area)
        self.ui.cmd_group.setLayout(h_layout)

        

    def init_cmd(self, source_command_list=[], target_command_list=[]):
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(12)

        self.ui.source_cmd_box.setFont(font)
        self.ui.source_cmd_box.addItems(source_command_list)
        
        self.ui.target_cmd_box.setFont(font)
        self.ui.target_cmd_box.addItems(target_command_list)

    def submit_setting(self):
        device_mac = window.ui.comboBox.currentText()
        device_endpoint = window.temp_pair_table[0]
        device_cmd = self.ui.source_cmd_box.currentText()
        target_info = {
            "cmd": self.ui.target_cmd_box.currentText(),
            "mac-addr": window.ui.comboBox_2.currentText(),
            "endpoint": window.temp_pair_table[1]
        }
        try:
            non_empty = 0
            if self.ui.level_check.isChecked() and len(self.ui.level_edit.text()) != 0:
                target_info["level"] = int(self.ui.level_edit.text())
                non_empty += 1

            if self.ui.duration_check.isChecked() and len(self.ui.duration_edit.text()) != 0:
                target_info["duration"] = int(self.ui.duration_edit.text())
                non_empty += 1

            if self.ui.timeout_check.isChecked() and len(self.ui.timeout_edit.text()) != 0:
                target_info["timeout"] = int(self.ui.timeout_edit.text())
                non_empty += 1

            if self.ui.delay_check.isChecked() and len(self.ui.delay_edit.text()) != 0:
                target_info["delay"] = int(self.ui.delay_edit.text())
                non_empty += 1
            
            if non_empty != 0:
                
                print(f"Before submit:\n{pair_dataset.current_dataset}")
                result = pair_dataset.add_to_device(mac=device_mac,
                        endpoint=device_endpoint,
                        cmd=device_cmd,
                        target_action_info=target_info
                )
                print(f"After submit:\n{pair_dataset.current_dataset}\n---\n")
        except Exception as e:
            print("Wrong input data")
        self.clean_data()
        self.add_exist_pair()

    def clean_data(self):
        self.ui.level_check.setChecked(False)
        self.ui.duration_check.setChecked(False)
        self.ui.timeout_check.setChecked(False)
        self.ui.delay_check.setChecked(False)

        self.ui.level_edit.clear()
        self.ui.duration_edit.clear()
        self.ui.timeout_edit.clear()
        self.ui.delay_edit.clear()

    def closeEvent(self, event):
        window.temp_pair_table = [0, 0]
        window.release_btns()
        self.ui.source_cmd_box.clear()
        self.ui.target_cmd_box.clear()
        self.clean_data()
        
        event.accept()


class PopUpWindow(QtWidgets.QWidget):
    def __init__(self):
        super(PopUpWindow, self).__init__()
        self.resize(320, 240)

        self.msg = QLabel(self)
        self.msg.setGeometry(QtCore.QRect(60, 40, 200, 120))
        self.msg.setAlignment(QtCore.Qt.AlignCenter)
        self.msg.setStyleSheet("font-size:20px")
        self.msg.setWordWrap(True)

        self.button = QPushButton(self)
        self.button.setText("確認")
        self.button.setStyleSheet("font-size:16px")
        self.button.setGeometry(QtCore.QRect(100, 200, 120, 30))
        self.button.clicked.connect(self.close)

    def show_warning_message(self, message=""):
        self.msg.setText("沒有Command!!!")
        self.show()

    def show_output_json_message(self, result, message=""):
        if result:
            self.msg.setText("輸出JSON檔成功!!!")
        else:
            self.msg.setText(f"輸出JSON檔失敗: {message}")

        self.show()

    def closeEvent(self, event):
        self.msg.clear()
        event.accept()


class CustomButton(QPushButton):
    def __init__(self, text, channel_type="", mac="", space=""):
        super().__init__(text)
        self.button_type = channel_type
        self.channel_number = text
        self.mac = mac
        self.space = space
        self.target_channels = list()

        self.setup_button()
        self.setMouseTracking(True)

    def setup_button(self):
        # Normal Channel
        self.bg_color = "ECF2FF"
        self.hover_color = "FFFFFF"
        self.hover_bg_color = "3E54AC"

        # Input/Output Channel
        if self.button_type == "Input":
            self.bg_color = "D7E9B9"
        elif self.button_type == "Output":
            self.bg_color = "FFC6D3"

        self.setStyleSheet(f'''
            QPushButton {{
                border: 1.5px solid #332C39;
                border-radius: 7px;
                padding: 5px 1px;
                font-size: 20px;
                font-weight: bold;
                font-family: Consolas;
                background-color: #{self.bg_color};
            }}
            QPushButton:hover {{
                border: 1.5px solid #95BDFF;
                background-color: #{self.hover_bg_color};
                color: #{self.hover_color};
            }}
        ''')

    def set_btn_status(self, enable=True):
        self.setEnabled(enable)
        
        # Change StyleSheet
        if enable:
            self.setup_button()
        else:
            self.setStyleSheet(f'''
                QPushButton {{
                    border: 1.5px solid #BDCDD6;
                    border-radius: 7px;
                    padding: 5px 1px;
                    font-size: 20px;
                    font-weight: bold;
                    font-family: Consolas;
                    background-color: #E9E8E8;
                    color: #7B8FA1;
                }}
            ''')
        

    def show_pair_connection(self, is_pair=False):
        if is_pair:
            self.setStyleSheet(f'''
                QPushButton {{
                    border: 1.5px solid #95BDFF;
                    border-radius: 7px;
                    padding: 5px 1px;
                    font-size: 20px;
                    font-weight: bold;
                    font-family: Consolas;
                    background-color: #{self.hover_bg_color};
                    color: #{self.hover_color};
                }}
            ''')
        else:
            self.setStyleSheet(f'''
            QPushButton {{
                border: 1.5px solid #332C39;
                border-radius: 7px;
                padding: 5px 1px;
                font-size: 20px;
                font-weight: bold;
                font-family: Consolas;
                background-color: #{self.bg_color};
            }}
            QPushButton:hover {{
                border: 1.5px solid #95BDFF;
                background-color: #{self.hover_bg_color};
                color: #{self.hover_color};
            }}
        ''')

    def enterEvent(self, event):
        self.target_channels = list()
        # Check pair table
        dataset = pair_dataset.current_dataset
        data = dataset.get(self.mac)
        if data != None:
            for i in data:
                # print(i, self.channel_number)
                if i["endpoint"] == int(self.channel_number):
                    target_actions = i["actions"]
                    # print(target_actions)
                    for target in target_actions:
                        self.target_channels.append((target["endpoint"], target["mac-addr"]))
        
        # print("mouse enter")
        window.show_pair_connection(self.mac, self.channel_number, self.space, self.target_channels, is_pair=True)
        pass

    
    def leaveEvent(self, event):
        # print("mouse leave")
        window.show_pair_connection(self.mac, self.channel_number, self.space, self.target_channels, is_pair=False)
    
    
    def make_style(self, status="normal"):
        if status == "normal":
            style_sheet = f'''

            '''
        elif status == "highlight":
            style_sheet = f'''

            '''
        return style_sheet

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    pair_dataset = PairDataset()
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
