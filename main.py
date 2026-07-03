from concurrent.futures import ThreadPoolExecutor

from banner import get_banner
from scanner import scan_host
from vuln import vulns_from_cpe


def process_port(ip, port):
    banner = get_banner(ip, port["port"])
    cves = vulns_from_cpe(port["cpe"])
    return {"port": port["port"], "name": port["name"], "banner": banner, "cves": cves}


def main(ip):
    open_ports = scan_host(ip)
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(process_port, [ip] * len(open_ports), open_ports)
    port_info = list(results)
    return port_info


if __name__ == "__main__":
    ip = input("Enter the IP address you want to scan: ")
    result = main(ip)
    for r in result:
        print(f"Port {r['port']}: banner={r['banner'][:50]!r}, {len(r['cves'])} CVEs")
