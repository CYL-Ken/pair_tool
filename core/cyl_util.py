import json
import logging
import os
import re
import subprocess
import time
from typing import Any, Callable, Optional, Tuple, TypeVar, Union

from .const import LOGGING_LEVEL
from .cyl_telnet import CYLResultParser, CYLTelnet

_LOGGER = logging.getLogger(__name__)
#_LOGGER.setLevel(LOGGING_LEVEL)

success_sign = """
██████   █████   ██████  ██████
██   ██ ██   ██ ██      ██
██████  ███████ ███████ ███████
██      ██   ██      ██      ██
██      ██   ██ ██████  ██████ 
"""

fail_sign = """
███████  █████  ███████ ██
██      ██   ██   ███   ██
██████  ███████   ███   ██
██      ██   ██   ███   ██
██      ██   ██ ███████ ███████
"""

def setting_cyl_telnet(CONNECTION_TIMEOUT = 0.3,
                       EPILOG: str = '#',
                       ENTER: str = '\r\n',
                       ENCODING: str = 'utf-8',
                       READ_NON_BLOCK_INTERVAL: int = 50,
                       RESULT_PARSER= CYLResultParser()):

    CYLTelnet.CONNECTION_TIMEOUT = CONNECTION_TIMEOUT
    CYLTelnet.EPILOG: str = EPILOG
    CYLTelnet.ENTER: str = ENTER
    CYLTelnet.ENCODING: str = ENCODING
    CYLTelnet.READ_NON_BLOCK_INTERVAL: int = READ_NON_BLOCK_INTERVAL
    CYLTelnet.RESULT_PARSER = RESULT_PARSER


def waitUntilConnect(ip: str = "192.168.2.200",
                     port: int = 23,
                     timeout: float = 1.5) -> Optional[CYLTelnet]:
    """Try to connect the host until timeout"""

    start_time = time.time()
    while (time.time() - start_time < timeout):
        dut = CYLTelnet(host = ip, port=port)

        if (dut.is_connected() is True):
            _LOGGER.debug("Successfully connected to %s:%d", ip, port)
            _LOGGER.debug("Dut connection takes time : {t}"\
                            .format(t=(time.time() - start_time)))
            if port == 23:
                dut.response(read_until=True, timeout=2)

            return dut
        time.sleep(0.1)
    return None

def make_cmd(cmd: str,
              **kwargs) -> str:
    """Generate the lgw cmd"""

    keys_map = {
        'target_id': 'target-id',
        'timeout_ms': 'timeout-ms',
        'raw_data': 'raw-data',
        'slave_addr': 'slave-addr',
        'start_addr': 'start-addr',
        'write_data': 'write-data',
    }

    kwargs_dict = dict(kwargs)
    for key in keys_map:
        if key in kwargs_dict:
            kwargs_dict[keys_map[key]] = kwargs_dict.pop(key)
        
    data = {"cmd": cmd}
    data.update(kwargs_dict)
    script = json.dumps(data)
    return '#:' + script + ':#'

def make_target_id(MAC: str,
                   channel: int) -> str:
    """Generate the target_id"""

    targetMAC = MAC.replace(":","").lower()
    return f"0000{targetMAC}:{channel}"


def retry_function(function: Callable[[Any,], Tuple[bool, Any]],
                    func_description: str = "",
                    retry: int = 1,
                    time_sleep: float = 0.1,
                    **kwargs):
    """retry the function"""

    if func_description == "":
        func_description = f"{function.__name__}()"

    ret, out = True, ""
    for i in range(0, retry):
        ret, out = function(**kwargs)
        if ret is True:
            break
        _LOGGER.warning(f"retry function {i}: {func_description}, out: {out}")
        time.sleep(time_sleep)
    return (ret, out)


def MAC_to_ipv6(MAC: str) -> str:
    """Generate the IPv6 address"""

    parts = MAC.split(":")
    # modify parts to match IPv6 value
    parts.insert(3, "ff")
    parts.insert(4, "fe")
    parts[0] = "%x" % (int(parts[0], 16) ^ 2)

    # format output
    ipv6Parts = list()
    for i in range(0, len(parts), 2):
        ipv6Parts.append("".join(parts[i:i+2]))
    ipv6 = "fe80::%s" % (":".join(ipv6Parts))
    return ipv6.lower()


def ipv6_to_MAC(ipv6: str) -> str:
    """Get MAC from IPv6 address"""

    # remove subnet info if given
    subnetIndex = ipv6.find("/")
    if subnetIndex != -1:
        ipv6 = ipv6[:subnetIndex]

    ipv6Parts = ipv6.split(":")
    macParts = list()
    for ipv6Part in ipv6Parts[-4:]:
        while len(ipv6Part) < 4:
            ipv6Part = "0" + ipv6Part
        macParts.append(ipv6Part[:2])
        macParts.append(ipv6Part[-2:])

    # modify parts to match MAC value
    macParts[0] = "%02x" % (int(macParts[0], 16) ^ 2)
    del macParts[4]
    del macParts[3]

    return (":".join(macParts)).upper()


def is_valid_MAC(MAC: str) -> bool:
    """Check the MAC"""

    pattern = r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$"
    if re.fullmatch(pattern, MAC):
        return True
    return False

def is_valid_IP(IP: str) -> bool:

    pattern = r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
    if re.fullmatch(pattern, IP):
        return True
    return False

def content9528_to_dict(content: str) -> TypeVar('T', None, dict, str):
    """Convert lgw content to dict()"""
    try:
        while "#:" in content:
            content=content.replace('#:','')
        dict_content = json.loads(content.replace(':#',''))
        dict_content = eval(str(dict_content))
    except Exception as e:
        return None
    return dict_content

def ascii_to_decimal(str_content: str):
    """Convert ascii to decimal"""
    return [ord(x) for x in str_content]

def decimal_to_ascii(decimal_list):
    """Convert decimal to ascii"""
    return ''.join([chr(x) for x in decimal_list])

def extract_Numerical_value(content: str):
    """get all numerical value from a string content"""
    result = re.findall(r"[-+]?\d*\.\d+|\d+", content)
    return [float(n) for n in result]


def load_config_json(json_path: str):
    """load a json file"""
    if not os.path.exists(json_path):
        _LOGGER.error(f"Couldn't find the device Json file: {json_path}.")
        return None

    with open(json_path, 'r') as j:
        try:
            config = json.load(j)
        except Exception:
            _LOGGER.error("The device Json file is invalid")
            return None

    return config

def decode16bit(z, mask):
    """decode 16 bit"""
    def shift(b):
        if (b == 0x0):
            return 0
        move = 0
        while(b):
            if ((b+1) >> 1) != (b >> 1):
                break
            b = b >> 1
            move+=1
        return move
    return (z & mask) >> shift(mask)

def is_float(elem) -> bool:
    """Is element a number ?"""
    
    try:
        float(elem)
    except ValueError:
        return False
    return True


def is_process_alive(fullCmd: str) -> Union[Tuple[bool, list], Tuple[bool, str]]:
    """Is process alive ? if true, get the PIDs."""

    pid_cmd = "pgrep -f '{}'".format(fullCmd)
    ret, out = do_command(pid_cmd)
    if ret is False:
        msg = out
        return (False, msg)

    lines = str(out).splitlines()
    if len(lines) == 0:
        msg = 'no output !'
        return (False, msg)

    pids = [int(i) for i in lines if is_float(i)]
    if len(pids) == 0:
        return (False, 'the pids length is 0 !')
     
    return (True, pids)


def do_command(cmd: str) -> Tuple[bool, str]:
    """Do command with host"""

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,
                            stderr=subprocess.PIPE) #, close_fds=True)
    out, err = p.communicate()
    if p.returncode != 0:
        msg = "Non zero exit code:{} executing: {} error: {}"\
                .format(p.returncode, cmd, err.decode())
        _LOGGER.warning(msg)
        return (False, msg)

    return (True, out.decode())

def source_hash(dir) -> str:
    """make source hash"""
    if source_hash.__doc__:
        return source_hash.__doc__

    try:
        import hashlib
        import os

        m = hashlib.md5()
        path = os.path.dirname(os.path.dirname(dir))
        for root, dirs, files in os.walk(path):
            dirs.sort()
            for file in sorted(files):
                if not file.endswith(".py"):
                    continue
                path = os.path.join(root, file)
                with open(path, "rb") as f:
                    m.update(f.read())

        source_hash.__doc__ = m.hexdigest()[:7]
        return source_hash.__doc__

    except Exception as e:
        return f"{type(e).__name__}: {e}"