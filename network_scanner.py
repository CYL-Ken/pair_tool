import socket
import scapy.all as scapy


class NetworkScanner():
    def __init__(self) -> None:
        self.hostname = ""
        self.ip_gateway = ""
        self.all_devices = {}
        self.iot_devices = {}
        
    
    def get_hostname(self):
        self.hostname = socket.getfqdn().split('.')[0]
        ip_address = socket.gethostbyname(self.hostname)
        network_prefix = '.'.join(ip_address.split('.')[:3]) + '.'

        self.ip_gateway = f"{network_prefix}0/24"
        print(f"本機所在網域為：{network_prefix}0/24")
    
    
    def scan_devices(self):
        arp_request = scapy.ARP(pdst=self.ip_gateway)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
        
        for element in answered_list:
            ip = element[1].psrc
            mac = element[1].hwsrc
            self.all_devices[ip] = mac
            if "d0:14:11" in mac[:8]:
                self.iot_devices[ip] = mac
        
    
    def list_all_devices(self):
        print("設備列表:")
        for key, value in self.all_devices.items():
            print(f"{key}\t\t{value}")
            
        print("IOT設備列表:")
        for key, value in self.iot_devices.items():
            print(f"{key}\t\t{value}")

    def get_iot_devices(self):
        self.hostname = ""
        self.ip_gateway = ""
        self.all_devices = {}
        self.iot_devices = {}
        self.get_hostname()
        self.scan_devices()
        self.list_all_devices()
        return self.iot_devices

if __name__ == "__main__":
    NetworkScanner = NetworkScanner()
    NetworkScanner.get_hostname()
    NetworkScanner.scan_devices()
    NetworkScanner.list_all_devices()