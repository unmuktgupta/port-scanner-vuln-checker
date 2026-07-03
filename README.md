# Port Scanner + Vulnerability Checker

A Python tool that scans a host for open ports, grabs service banners, and cross-references detected services against the National Vulnerability Database (NVD) to surface known CVEs — with a Streamlit web UI on top.

Built as part of an individual cybersecurity project (Weeks 2–4): **"One Real Tool per Member — Port Scanner + Vulnerability Checker."**

## Features

- **Port scanning** via `python-nmap`, using service/version detection (`-sV`) against the top 100 most common ports
- **Banner grabbing** via raw TCP sockets, with graceful handling of timeouts, refused connections, and non-UTF-8 responses
- **CVE lookup** via the NVD REST API 2.0:
  - Converts nmap's CPE 2.2 format (`cpe:/a:vendor:product:version`) to CPE 2.3 (`cpe:2.3:a:vendor:product:version:*:*:*:*:*:*:*`)
  - Falls back to a keyword search (vendor + product) when an exact CPE match returns no results — but only if nmap actually detected a version. A versionless CPE (e.g. `cpe:/a:mysql:mysql` with no version number) would otherwise produce an overly generic keyword search like "mysql mysql" that matches thousands of unrelated CVEs, so the fallback is skipped entirely in that case and 0 CVEs are returned instead of noise
  - Extracts CVE ID, description, and CVSS severity score, falling back across CVSS v3.1 → v3.0 → v2.0 depending on what's available per CVE
- **Concurrent processing** — banner grabbing and CVE lookups run in parallel across ports using `ThreadPoolExecutor`, instead of sequentially
- **Streamlit UI** — enter an IP, hit scan, and get an expandable per-port breakdown of banners and CVEs, color-coded by severity
- **Error handling throughout** — unreachable hosts, malformed CPEs, empty banners, rate-limited/failed API calls, and missing data are all handled without crashing

## Project Structure

```
port-scanner-vuln-checker/
├── scanner.py      # nmap wrapper — scans a host, returns open ports with service/CPE info
├── banner.py       # raw socket banner grabbing for a given host/port
├── vuln.py         # NVD API integration — CPE conversion, CVE lookup, keyword fallback
├── main.py         # orchestrates scanner + banner + vuln with threaded execution
├── app.py          # Streamlit UI
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites

- Python 3.10+
- [nmap](https://nmap.org/download.html) installed and available on your system PATH (the `python-nmap` package is just a wrapper — it needs the actual nmap binary)
- A free [NVD API key](https://nvd.nist.gov/developers/request-an-api-key) (works without one too, but with much stricter rate limits)

### Installation

```bash
git clone https://github.com/unmuktgupta/port-scanner-vuln-checker.git
cd port-scanner-vuln-checker
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
NVD_API_KEY=your_nvd_api_key_here
TEST_IP=127.0.0.1
```

`TEST_IP` is only used by each module's built-in `if __name__ == "__main__":` test block — the Streamlit app takes the target IP directly from the UI.

> ⚠️ **Only scan hosts you own or have explicit permission to scan.** This tool is intended for use against your own lab environment (e.g. a local [Metasploitable 2](https://sourceforge.net/projects/metasploitable/) VM), not third-party systems.

## Usage

### Web UI (recommended)

```bash
streamlit run app.py
```

Enter a target IP, hit **Scan**, and expand each port's results to see its banner and any known CVEs.

![App screenshot placeholder](docs/screenshot-app.png)

![Scan results placeholder](docs/screenshot-results.png)

### CLI

```bash
python main.py
```

Prompts for an IP, then prints a per-port summary (banner + CVE count) to the terminal.

### Individual modules

Each module can also be run and tested standalone:

```bash
python scanner.py   # scans TEST_IP, prints open ports
python banner.py     # grabs banners for all open ports on TEST_IP
python vuln.py        # looks up CVEs for a sample CPE
```

## How It Works

1. `scan_host(ip)` runs an nmap scan (`-Pn -sT -sV --top-ports 100`) and returns a list of open ports, each with a service name and CPE string (if detected).
2. For each open port, two things happen concurrently (via `ThreadPoolExecutor`):
   - `get_banner(ip, port)` opens a raw socket to the port and reads whatever the service sends back.
   - `vulns_from_cpe(cpe)` converts the CPE to 2.3 format, queries the NVD API for an exact match, and falls back to a keyword search if nothing is found.
3. Results are combined into a single structure per port: `{"port", "name", "banner", "cves"}`, where each CVE is `{"id", "description", "score"}`.

## Known Limitations

- Only the top 100 most common ports are scanned by default (configurable in `scanner.py` if you want full coverage — expect it to take significantly longer).
- CVE matching quality depends on nmap's version detection accuracy and NVD's CPE dictionary coverage; obscure or very new services may return no CVEs even when vulnerabilities exist.
- If nmap detects a service but can't determine its version, the tool deliberately reports 0 CVEs for that port rather than guessing — a keyword search on vendor/product alone (e.g. "mysql mysql") would otherwise match thousands of unrelated CVEs and produce misleading results.
- The NVD API without an API key is heavily rate-limited; scans may be slow or partially fail without one.

## Roadmap / Stretch Goals

- [ ] Dockerize the app
- [ ] Deploy the Streamlit app (cloud or local server)
- [ ] Basic authentication
- [ ] Unit tests

## Disclaimer

This tool is for educational and authorized security testing purposes only. Scanning systems without permission may be illegal in your jurisdiction.
