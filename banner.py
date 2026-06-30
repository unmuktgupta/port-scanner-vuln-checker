import socket

import nmap

from scanner import scan_host

nm = nmap.PortScanner()


def get_banner(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, port))
        banner = s.recv(1024)
        dbanner = banner.decode()  # decoded banner
        s.close()
        return dbanner
    except (TimeoutError, ConnectionError, UnicodeDecodeError):
        return ""


open_ports = scan_host("192.168.1.11")
for port in open_ports:
    print(get_banner("192.168.1.11", port["port"]))
