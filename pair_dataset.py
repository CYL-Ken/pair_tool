import os
import json

class PairingDataset():
    def __init__(self) -> None:
        self.device_mac_list = []
        self.pair_dataset = dict()


    def create_action(self, info) -> dict():
        try:
            action = dict()
            action["cmd"]      = info["cmd"]
            action["mac-addr"] = info["mac-addr"]
            action["endpoint"] = int(info["endpoint"])
        except Exception as e:
            print("Missing some value:", e)
            return -1

        if info.get("level"):
            action["level"] = info["level"]
        if info.get("duration"):
            action["duration"] = info["duration"]
        if info.get("timeout"):
            action["timeout-ms"] = info["timeout"]
        if info.get("delay"):
            action["delay-ms"] = info["delay"]

        return action

    
    def add_to_device(self, mac, endpoint, cmd, target_action_info):
        action = self.create_action(target_action_info)
        if action == -1:
            return False

        if self.pair_dataset.get(mac) != None:
            exist_pair = False
            for table in self.pair_dataset[mac]:
                if table["cmd"] == cmd and table["endpoint"] == endpoint:
                    # exist pair
                    table["actions"].append(action)
                    exist_pair = True
            
            if exist_pair is False:
                # add new one
                cmd_table = dict()
                cmd_table["cmd"] = cmd
                cmd_table["type"] = 0
                cmd_table["description"] = "0"
                cmd_table["endpoint"] = int(endpoint)
                cmd_table["check-rules"] = []
                cmd_table["actions"] = [action]
                self.pair_dataset[mac].append(cmd_table)
        else:
            # no mac ever, create a new one
            cmd_table = dict()
            cmd_table["cmd"] = cmd
            cmd_table["type"] = 0
            cmd_table["description"] = "0"
            cmd_table["endpoint"] = int(endpoint)
            cmd_table["check-rules"] = []
            cmd_table["actions"] = [action]
            self.pair_dataset[mac] = [cmd_table]

        return True
        

    def save_json(self):
        result_folder = "result/"
        try:
            for mac, pair_table in self.pair_dataset.items():
                mac = mac.replace(":", "").upper()
                target_folder = os.path.join(result_folder, mac)
                if os.path.exists(target_folder) is False:
                    os.mkdir(target_folder)
                target_path = target_folder + "/device_pair.json"
                json_data = json.dumps(pair_table, indent=4)
                with open(target_path, 'w') as f:
                    f.write(json_data)
            return True, ""
        except Exception as e:
            return False, e