import os
import socket

import dotenv
import nmap

from scanner import scan_host

dotenv.load_dotenv()

TEST_IP = os.getenv("TEST_IP")

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


if __name__ == "__main__":
    open_ports = scan_host(TEST_IP)
    for port in open_ports:
        print(get_banner(TEST_IP, port["port"]))
