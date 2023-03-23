import logging
import os
import time

from core import cyl_util as util
from core.cyl_logger import Log
from core.cyl_telnet import CYLTelnet

if __name__ == '__main__':

    # 確定	rtl8196e	172.16.50.4			D0:14:11:B0:10:3C			
    # 確定	rtl8196e-2	172.16.50.5			D0:14:11:B0:10:7B

    # scu = CYLController('D0:14:11:B0:10:7B')			
    # scu = CYLController('D0:14:11:B0:10:3C')

    # res, out = scu.send_cmd(util.make_cmd(cmd="configure", pretty_print=False), timeout=3, just_send=False)
    # print(res, out)

    # exit()
    # slave = CYLTelnet('172.16.50.5', 9528)

    # master = CYLTelnet('172.16.50.5', 9528)
    # mac = 'D0:14:11:B0:10:7B'
    # mac = 'D0:14:11:B0:10:7B'
    # print(master.sends(util.make_cmd("enumerate", refresh = True), timeout = 10))
    # target_id = util.make_target_id(mac, 1)
    # command = util.make_cmd("read-attr", target_id=target_id, attr="commit-id")
    # ret, out = master.sends(command, read_until=False, verbose=True)
    # print(out)
    # time.sleep(0.25)
    # exit()

    # dut = CYLTelnet('192.168.2.200', 9528)
    # dut_mac = 'D0:14:11:B0:10:4E'
    
    util.setting_cyl_telnet(EPILOG=":#")
    test = CYLTelnet('172.16.50.4', 9528)
    test_mac = 'd0:14:11:b0:0f:75'
    
    
    # ret, receiver_response = dut.response(read_until=False)
    # print(f"DUT Response: {ret}, {receiver_response}")

    # target_id = util.make_target_id(test_mac, 4)

    # print("INIT")
    # command = util.make_cmd("read-attr", target_id=target_id, attr="on-off-state")
    # print(test.sends(command, read_until=False, verbose=True, just_send=False))

    # command = util.make_cmd("switch-on", target_id=target_id)
    # print(test.sends(command, read_until=False, verbose=True))

    # ret, out = dut.response(read_until=False, verbose=True)
    # print("out", out)
    target_id = util.make_target_id(test_mac, 1)
    command = util.make_cmd("enumerate", target_id=target_id)
    print(command)
    print("\n")
    print(test.sends(command, read_until=True, verbose=False, timeout=10))
    
    # command = util.make_cmd("switch-off", target_id=target_id)
    # print(command)
    # print(test.sends(command, read_until=False, verbose=False))

    # ret, receiver_response = dut.response(read_until=True)
    # print(f"DUT Response: {ret}, {receiver_response}")

    
    # target_id = util.make_target_id(dut_mac, 7)

    # for i in range(1000):

    #     # mylogger.info("switch-on")
    #     # command = util.make_cmd("switch-on", target_id=target_id)
    #     # ret, out = dut.sends(command, read_until=False, verbose=False)
    #     # if ret is False:
    #     #     mylogger.warning(f"ret: {ret}, out: {out}")

    #     # mylogger.info("read")
    #     # command = util.make_cmd("read-attr", target_id=target_id, attr="on-off-state")
    #     # ret, out = dut.sends(command, read_until=False, verbose=False)
    #     # if out.get("value") != True:
    #     #     mylogger.warning(f"ret: {ret}, out: {out}")

    #     # mylogger.info("switch-off")
    #     # command = util.make_cmd("switch-off", target_id=target_id)
    #     # ret, out = dut.sends(command, read_until=False, verbose=False)
    #     # if ret is False:
    #     #     mylogger.warning(f"ret: {ret}, out: {out}")

    #     # mylogger.info("read")
    #     # command = util.make_cmd("read-attr", target_id=target_id, attr="on-off-state")
    #     # ret, out = dut.sends(command, read_until=False, verbose=False)
    #     # if out.get("value") != False:
    #     #     mylogger.warning(f"ret: {ret}, out: {out}")

    #     # mylogger.info("switch-toggle")
    #     # command = util.make_cmd("switch-toggle", target_id=target_id)
    #     # ret, out = dut.sends(command, read_until=False, verbose=False)
    #     # if ret is False:
    #     #     mylogger.warning(f"ret: {ret}, out: {out}")

    #     mylogger.info("read")
    #     command = util.make_cmd("read-attr", target_id=target_id, attr="on-off-state")
    #     ret, out = dut.sends(command, read_until=False, verbose=False)
    #     # if out.get("value") != True:
    #     #     mylogger.warning(f"ret: {ret}, out: {out}")
    #     mylogger.warning(f"ret: {ret}, out: {out}")
    #     time.sleep(2)

    #     mylogger.info("reset")
    #     command = util.make_cmd("reset-device", target_id=target_id, delay=1000)
    #     ret, out = dut.sends(command, read_until=False, verbose=False)
    #     time.sleep(2)
    #     if ret is False:
    #         mylogger.warning(f"ret: {ret}, out: {out}")

    #     mylogger.info("read")
    #     command = util.make_cmd("read-attr", target_id=target_id, attr="on-off-state")
    #     ret, out = dut.sends(command, read_until=False, verbose=False)
    #     # if out.get("value") != True:
    #     #     mylogger.warning(f"ret: {ret}, out: {out}")
    #     mylogger.warning(f"ret: {ret}, out: {out}")


#:{"cmd": "switch-on", "target-id": "0000d01411b0103c:11"}:#
#:{"cmd": "switch-on", "target-id": "0000d01411b0107b:11"}:#


    """
    # command = util.make_cmd("enumerate", refresh=True)
    # print(dut.sends(command, read_until=False, verbose=True, timeout=10))
    # command = util.make_cmd("write-attr", target_id=target_id, attr="location-description", value="")
    # command = util.make_cmd("read-attr", target_id=target_id, attr="on-off-state")
    # print(dut.sends(command, read_until=False, verbose=True, just_send=False))
    # time.sleep(1)

    time.sleep(0.3)
    command = util.make_cmd("switch-on", target_id=target_id)
    print(dut.sends(command, read_until=False, verbose=False))
    
    time.sleep(0.3)
    print(" response")
    print(test.response(verbose=True, read_until=True))
    
    time.sleep(0.3)
    command = util.make_cmd("switch-off", target_id=target_id)
    print(dut.sends(command, read_until=False, verbose=False))

    # time.sleep(0.3)
    # command = util.make_cmd("switch-off", target_id=target_id)
    # print(dut.sends(command, read_until=False, verbose=False))
    test.close()
    time.sleep(0.3)
    test = CYLTelnet('172.16.50.7', 9528)
    command = util.make_cmd("switch-on", target_id=target_id)
    print(dut.sends(command, read_until=False, verbose=False))
    
    time.sleep(0.3)
    print("rrrrrrrrrrrrrrrrrrrrrresponse")
    print(test.response(verbose=True, read_until=True))
    
    time.sleep(0.3)
    command = util.make_cmd("switch-off", target_id=target_id)
    print(dut.sends(command, read_until=False, verbose=True))
    
    #time.sleep(0.3)
    dut.close()
    test.close()

    print("/////////////////////////////////////////")
    # print(slave.response())
    # slave.close()
    """

    """
    <RECEIVE>
    #:{"cmd":"receive-switch-on","target-id":"0000d01411b0107b:1"}:##:{"cmd":"switch-on","target-id":"0000d01411b0107b:1","code":0}:#
    </RECEIVE>
    (True, {'cmd': 'switch-on', 'target-id': '0000d01411b0107b:1', 'code': 0, 'other': [{'cmd': 'receive-switch-on', 'target-id': '0000d01411b0107b:1'}]})
    """