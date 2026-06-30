import nmap

nm = nmap.PortScanner()


def scan_host(ip):
    nm.scan(ip, arguments="-Pn -sT")
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


print(scan_host("192.168.1.15"))
