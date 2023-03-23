import json

from core import cyl_util as util
from core.cyl_telnet import CYLTelnet

SUPPORT_DEVICE = ["SCU", "SCULite", "Dimmer", "POC", "Smart Switch"]

device_mac = "d0:14:11:b0:0f:75"
device_ip = "172.16.50.4"
# device_ip = ""

def enumerate_from_device(ip="", mac=""):
    my_dict = {}
    my_endpoint = {}

    conn = CYLTelnet(ip, 9528)
    target_id = util.make_target_id(mac, 1)
    command = util.make_cmd("enumerate", target_id=target_id)

    ret, out = conn.sends(command, read_until=True, verbose=False, expect_string=':#', timeout=10)
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

if __name__ == "__main__":
    a = {}        
    a[device_mac] = enumerate_from_device(device_ip, device_mac)
    print(a)
