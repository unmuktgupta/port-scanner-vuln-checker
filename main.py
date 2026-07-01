from banner import get_banner
from scanner import scan_host
from vuln import vulns_from_cpe


def main(ip):
    port_info = []
    open_ports = scan_host(ip)
    for port in open_ports:
        print(f"Scanning port {port['port']} ({port['name']})...")
        banner = get_banner(ip, port["port"])
        cves = vulns_from_cpe(port["cpe"])
        port_info.append({"port": port["port"], "banner": banner, "cves": cves})
    return port_info


if __name__ == "__main__":
    ip = input("Enter the IP address you want to scan: ")
    result = main(ip)
    for r in result:
        print(f"Port {r['port']}: banner={r['banner'][:50]!r}, {len(r['cves'])} CVEs")
