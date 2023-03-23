import sys
import json
import argparse
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QWidget, QGridLayout, QVBoxLayout, QScrollArea, QHBoxLayout

from layout.main_ui import Ui_MainWindow
from layout.pairwindow_ui import Ui_PairWindow
from pair_dataset import PairDataset
from network_scanner import NetworkScanner
from core import cyl_util as util
from core.cyl_telnet import CYLTelnet

"""
    - MainWindow: The homepage of this application
    - PairWindow: For user type command detail
    - PopUpWindow: For displaying any message
"""

SUPPORT_DEVICE = ["SCU", "SCULite", "Dimmer", "POC", "Smart Switch"]
DEVICE_CONFIG = ""

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        

        self.pop_up_window = PopUpWindow()
        self.pair_window = PairWindow()
        
        self.network_scanner = NetworkScanner()
        
        self.process_thread = ProcessThread()
        self.process_thread.finish_update.connect(self.update_devices_ui)
        self.process_thread.show_message.connect(self.pop_window)
        
        self.device_list = []
        self.default_data = {}
        self.iot_devices = {}
        
        # Different device's button layout
        with open("configs/layout_config.json") as f:
            self.layout_config = json.load(f)

        self.devices_layout_config = self.layout_config["Device Layout"]
        
        self.device_button = dict()
        self.target_button = dict()

        # For record new pair information
        self.temp_pair_table = [0, 0]

        
        # Initial UI
        self.ui.setupUi(self)
        self.setWindowTitle("配對工具")
        self.setup_control()


    def setup_control(self):
        self.ui.output.clicked.connect(self.output_to_json)
        self.ui.refresh_button.clicked.connect(self.start_update)
        self.ui.comboBox.currentTextChanged.connect(self.update_device)
        self.ui.comboBox_2.currentTextChanged.connect(self.update_target)

        # First Update btns in two group 
        self.launch = True
        self.start_update()


    def update_devices_ui(self, ret, device_data, device_list):
        self.pop_up_window.close_window()
        if ret:
            self.device_list = device_list
            self.default_data = device_data
            
            self.ui.comboBox.blockSignals(True)
            self.ui.comboBox.clear()
            self.ui.comboBox_2.blockSignals(True)
            self.ui.comboBox_2.clear()
            
            if len(self.device_list) > 0:
                self.ui.comboBox.addItems(self.device_list)
                self.ui.comboBox_2.addItems(self.device_list)
            
                self.ui.comboBox.blockSignals(False)
                self.ui.comboBox_2.blockSignals(False)
                self.update_device()
                self.update_target()
            else:
                pass
            
        else:
            if self.ui.device_button_group.layout():
                QWidget().setLayout(self.ui.device_button_group.layout())
            if self.ui.target_button_group.layout():
                QWidget().setLayout(self.ui.target_button_group.layout())
            self.ui.device_title.setText("")
            self.ui.target_title.setText("")
        self.pop_up_window.show_message(title="提示", message="設備列表更新完成!")


    def start_update(self):
        # self.pop_up_window.show_message(title="提示", message="設備列表更新中...", show_button=False)
        print("Start")
        self.process_thread.start()
        
        
    def pop_window(self):
        self.pop_up_window.show_message(title="提示", message="設備列表更新中...", show_button=False)
        self.setDisabled(True)
        pass

    def update_connected_devices(self):
        # self.pop_up_window.show_message(title="提示", message="設備列表更新中...", show_button=False)
        ret = self.get_device_and_info()
        if ret:
            self.update_device()
            self.update_target()
        else:
            if self.ui.device_button_group.layout():
                QWidget().setLayout(self.ui.device_button_group.layout())
            if self.ui.target_button_group.layout():
                QWidget().setLayout(self.ui.target_button_group.layout())
            self.ui.device_title.setText("")
            self.ui.target_title.setText("")
        
        
        # self.pop_up_window.close_window()
        
        if self.launch is True:
            self.launch = False
        else:
            self.pop_up_window.show_message(title="提示", message="設備列表更新完成!")


    def get_device_and_info(self):
        self.device_list = []
        self.default_data = {}
        self.iot_devices = {}
        
        self.ui.comboBox.blockSignals(True)
        self.ui.comboBox.clear()
        self.ui.comboBox_2.blockSignals(True)
        self.ui.comboBox_2.clear()
        
        self.iot_devices = self.network_scanner.get_iot_devices()
        # self.device_list = self.iot_devices.values()
        
        # with open("configs/virtual.json") as f:
        #     default_data = json.load(f)
        #     self.default_data = default_data
        #     f.close()
        
        for ip, mac in self.iot_devices.items():
            result = self.enumerate_from_device(ip=ip, mac=mac)
            if result != False:
                self.default_data[mac] = result
                self.device_list.append(mac)
            
        
        if len(self.device_list) > 0:
            self.ui.comboBox.addItems(self.device_list)
            self.ui.comboBox_2.addItems(self.device_list)
        
            self.ui.comboBox.blockSignals(False)
            self.ui.comboBox_2.blockSignals(False)
            
            return True
        else:
            return False
        
    def enumerate_from_device(self, ip="", mac=""):
        my_dict = {}
        my_endpoint = {}

        conn = CYLTelnet(ip, 9528)
        target_id = util.make_target_id(mac, 1)
        command = util.make_cmd("enumerate", target_id=target_id)

        ret, out = conn.sends(command, read_until=True, verbose=False, expect_string=':#', timeout=15)
        if ret is False:
            print("Enumerate Failed")
            print(out)
            return False 

        for channel in out["devices"]:
            device_type = [d for d in SUPPORT_DEVICE if d in channel["name"]][0]
            endpoint = channel["id"].split(":")[-1]
            support_cmd = channel["commands"]
            my_endpoint[endpoint] = support_cmd

        if endpoint == "24":
            device_type = "SCULite"
        my_dict["type"] = device_type
        my_dict["channels"] = my_endpoint

        return my_dict


    def refresh_devices(self):
        self.pop_up_window.show_message(title="提示", message="設備列表更新中...", show_button=False)
        


    def update_device(self):
        self.device_mac = self.ui.comboBox.currentText()
        self.device_channels = self.default_data[self.device_mac]["channels"]
        self.device_button = dict()
        self.create_btns(object=self.device_button, 
                        click_func=self.click_device, 
                        device_type=self.default_data[self.device_mac]["type"], 
                        layout_group=self.ui.device_button_group, 
                        mac=self.device_mac, 
                        space="device")
        
        device_type = self.default_data[self.device_mac]["type"]
        self.ui.device_title.setText(f"{device_type} - {self.device_mac.upper()}")
        

    def update_target(self):
        self.target_mac = self.ui.comboBox_2.currentText()
        self.target_channels = self.default_data[self.target_mac]["channels"]
        self.target_button = dict()
        self.create_btns(object=self.target_button, 
                        click_func=self.click_target, 
                        device_type=self.default_data[self.target_mac]["type"], 
                        layout_group=self.ui.target_button_group,
                        mac=self.target_mac,
                        space="target")

        device_type = self.default_data[self.target_mac]["type"]
        self.ui.target_title.setText(f"{device_type} - {self.target_mac.upper()}")
        

    def click_device(self):
        sender = self.sender()
        print("Device click: ", sender.text())
        self.temp_pair_table[0] = sender.text()
        for i in self.device_button.keys():
            if self.device_button[i].text() != sender.text():
                self.device_button[i].set_btn_status(False)


    def click_target(self):
        if self.temp_pair_table[0] == 0:
            return 
        sender = self.sender()
        print("Target click: ", sender.text())
        self.temp_pair_table[1] = sender.text()

        try:
            self.show_pair_window(self.temp_pair_table)
            for i in self.target_button.keys():
                if self.target_button[i].text() != sender.text():
                    self.target_button[i].set_btn_status(False)
        except Exception as e:
            self.release_btns()
            self.pop_up_window.show_message(title="警告", message="找不到Command!")
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
                self.target_button[target_channel].show_pair_connection(is_pair=is_pair)
            else:
                if target_mac != self.device_mac:
                    continue
                self.device_button[target_channel].show_pair_connection(is_pair=is_pair)


    def show_pair_window(self, temp_pair_table):
        cmd_list = self.device_channels.get(temp_pair_table[0])
        target_cmd_list = self.target_channels.get(temp_pair_table[1])
        dataset = pair_dataset.current_dataset

        self.pair_window.init_cmd(source_command_list=cmd_list, target_command_list=target_cmd_list)
        self.pair_window.show_window(self.device_mac, self.target_mac, temp_pair_table[0], temp_pair_table[1], dataset)


    def release_btns(self):
        for i in self.device_button.keys():
            self.device_button[i].set_btn_status(True)
        for i in self.target_button.keys():
            self.target_button[i].set_btn_status(True)

    
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
        self.setWindowTitle("新增配對內容")
        

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
        widget.setObjectName("container")
        
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
                            
                            command_space = QGridLayout()
                            delete_button = DeleteButton()
                            
                            delete_button.set_info(source_mac=self.source_mac, 
                                                    source_cmd=cmd, 
                                                    source_endpoint=self.source_endpoint, 
                                                    action=action)
                            
                            
                            command_text = QLabel("TextLabel")
                            command_text.setText(text)
                            command_text.setFont(font)
                            
                            command_space.addWidget(delete_button, 0, 0)
                            command_space.addWidget(command_text, 0, 1)
                            
                            layout.addLayout(command_space)

        widget.setLayout(layout)
        scroll_area.setWidget(widget)
        
        h_layout.addWidget(scroll_area)
        self.ui.cmd_group.setLayout(h_layout)
        
    
    def remove_action(self, source_mac="", source_cmd="", source_endpoint="", action={}):
        
        try:
            pair_list = pair_dataset.current_dataset.get(source_mac)
            print(pair_list)
            for pair in pair_list:
                print(source_cmd)
                print(source_endpoint)
                if pair["cmd"] == source_cmd and pair["endpoint"] == int(source_endpoint):
                    print(action)
                    
                    actions = pair["actions"]
                    index = actions.index(action)
                    del actions[index]
                    
                    if len(actions) == 0:
                        i = pair_list.index(pair)
                        del pair_list[i]
            
            
            self.add_exist_pair()
            print(pair_list)
            
        except Exception as e:
            print(e)


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
        
        self.setWindowTitle("提示訊息")
        
    
    def show_message(self, title="", message="", show_button=True):
        self.msg.setText(message)
        self.setWindowTitle(title)
        self.button.setVisible(show_button)
        if show_button:
            self.button.clicked.connect(self.back_to_window)
        self.show()

    def back_to_window(self):
        window.setDisabled(False)
        self.close_window()

    def close_window(self):
        self.msg.clear()
        self.close()

    def show_warning_message(self, message=""):
        self.msg.setText("沒有Command.................")
        self.show()
        
    def show_processing_message(self, message=""):
        self.msg.setText(message)
        self.button.setVisible(False)
        self.show()
        
    def close_window(self):
        self.close()
        
    def show_update_message(self, message=""):
        self.msg.setText("設備列表更新完成!")
        self.button.setVisible(True)
        self.show()

    def show_output_json_message(self, result, message=""):
        if result:
            self.msg.setText("輸出JSON檔成功!")
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
        self.bg_color = "CADEFC"
        self.hover_color = "FFFFFF"
        self.hover_bg_color = "3E54AC"

        # Input/Output Channel
        if self.button_type == "Input":
            self.bg_color = "D3E0DC"
        elif self.button_type == "Output":
            self.bg_color = "E9D5DA"

        self.setStyleSheet(f'''
            QPushButton {{
                border: 1px solid #3F72AF;
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
            self.setup_button()


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
    
    
class DeleteButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setText("X")
        self.setFixedSize(30, 30)
        self.setStyleSheet('''
            QPushButton {
                
            }
            QPushButton:hover {
                
            }
        ''')
        self.clicked.connect(self.delete_action)
        
        
    def set_info(self, source_mac="", source_cmd="", source_endpoint="", action={}):
        self.source_mac = source_mac
        self.source_cmd = source_cmd
        self.source_endpoint = source_endpoint
        self.action = action
        
    def delete_action(self):
        window.pair_window.remove_action(source_mac=self.source_mac, 
                                        source_cmd=self.source_cmd, 
                                        source_endpoint=self.source_endpoint, 
                                        action=self.action)
        pass
    
class ProcessThread(QThread):
    finish_update = pyqtSignal(bool, dict, list)
    show_message = pyqtSignal()
    
    def __init__(self, ) -> None:
        super(ProcessThread, self).__init__()
        self.start_update = pyqtSignal(bool)
        
    def run(self):
        self.show_message.emit()
        self.update_devices()
        
    def update_devices(self):
        self.device_data = {}
        self.device_list = []
        
        self.network_scanner = NetworkScanner()
        self.iot_devices = self.network_scanner.get_iot_devices()
        
        for ip, mac in self.iot_devices.items():
            result = self.enumerate_from_device(ip=ip, mac=mac)
            if result != False:
                self.device_data[mac] = result
                self.device_list.append(mac)
        
        
        ret = True if len(self.device_list) > 0 else False
        self.finish_update.emit(ret, self.device_data, self.device_list)
    
    def enumerate_from_device(self, ip="", mac=""):
        my_dict = {}
        my_endpoint = {}

        conn = CYLTelnet(ip, 9528)
        target_id = util.make_target_id(mac, 1)
        command = util.make_cmd("enumerate", target_id=target_id)

        ret, out = conn.sends(command, read_until=True, verbose=False, expect_string=':#', timeout=15)
        if ret is False:
            print("Enumerate Failed")
            print(out)
            return False 

        for channel in out["devices"]:
            device_type = [d for d in SUPPORT_DEVICE if d in channel["name"]][0]
            endpoint = channel["id"].split(":")[-1]
            support_cmd = channel["commands"]
            my_endpoint[endpoint] = support_cmd

        if endpoint == "24":
            device_type = "SCULite"
        my_dict["type"] = device_type
        my_dict["channels"] = my_endpoint
        
        return my_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="配對工具")
    parser.add_argument("-d", "--debug", help="debug mode")
    parser.add_argument("-f", "--file", help="file mode path")
    
    args = parser.parse_args()
    DEVICE_CONFIG = args.file
    
    
    
    app = QtWidgets.QApplication(sys.argv)
    
    pair_dataset = PairDataset()
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
