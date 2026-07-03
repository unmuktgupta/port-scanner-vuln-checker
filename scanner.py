import os

import dotenv
import nmap

dotenv.load_dotenv()

TEST_IP = os.getenv("TEST_IP")

nm = nmap.PortScanner()


def scan_host(ip):
    nm.scan(ip, arguments="-Pn -sT -sV --top-ports 100")
    open_ports = []
    try:
        for port in nm[ip]["tcp"]:
            if nm[ip]["tcp"][port]["state"] == "open":
                port_info = {
                    "port": port,
                    "name": nm[ip]["tcp"][port]["name"],
                    "cpe": nm[ip]["tcp"][port]["cpe"],
                }
                open_ports.append(port_info)
    except KeyError:
        return []
    return open_ports


if __name__ == "__main__":
    print(scan_host(TEST_IP))
