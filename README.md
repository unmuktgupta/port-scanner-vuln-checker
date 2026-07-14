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
├── tests/          # pytest unit tests
├── Dockerfile
├── .dockerignore
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
APP_PASSWORD=choose_a_password
```

`TEST_IP` is only used by each module's built-in `if __name__ == "__main__":` test block — the Streamlit app takes the target IP directly from the UI. `APP_PASSWORD` gates access to the Streamlit app itself (see Authentication below).

> ⚠️ **Only scan hosts you own or have explicit permission to scan.** This tool is intended for use against your own lab environment (e.g. a local [Metasploitable 2](https://sourceforge.net/projects/metasploitable/) VM), not third-party systems.

## Usage

### Web UI (recommended)

```bash
streamlit run app.py
```

Enter a target IP, hit **Scan**, and expand each port's results to see its banner and any known CVEs.

### Authentication

The app is gated behind a single shared password (set as `APP_PASSWORD` in `.env`). This is intentionally basic — not a multi-user account system — since the tool is meant for personal/lab use, not public deployment. Enter the password once per session; it's remembered via Streamlit's session state for the rest of that browser session.

### Running with Docker

Build the image (installs Python, the `nmap` binary, and all dependencies inside a self-contained container):

```bash
docker build -t port-scanner .
```

Run it, passing your `.env` file so `NVD_API_KEY` and `APP_PASSWORD` are available inside the container:

```bash
docker run -p 8501:8501 --env-file .env port-scanner
```

Then open `http://localhost:8501`. If nmap can't complete scans properly from inside the container (some scan types need extra network privileges Docker restricts by default), add these capability flags:

```bash
docker run -p 8501:8501 --env-file .env --cap-add=NET_RAW --cap-add=NET_ADMIN port-scanner
```

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

### CPE → CVE lookup, in detail

**1. Where the CPE comes from.** The `-sV` flag tells nmap to actively fingerprint each open port's service and version, not just whether it's open. When it succeeds, it assigns a [CPE](https://nvd.nist.gov/products/cpe) (Common Platform Enumeration) string — a standardized name for a specific piece of software — e.g. `cpe:/a:vsftpd:vsftpd:2.3.4` (`a` = application, then vendor, product, version). `scan_host()` pulls this straight from nmap's result dict.

**2. Converting the format.** NVD's API only accepts CPE **2.3** format — a fixed 11-field structure padded with wildcards, e.g. `cpe:2.3:a:vsftpd:vsftpd:2.3.4:*:*:*:*:*:*:*`. `convert_cpe()` swaps the `cpe:/` prefix for `cpe:2.3:` and pads the remaining fields (update, edition, language, sw_edition, target_sw, target_hw, other — none of which nmap provides) with `:*`.

**3. Exact match lookup.** The converted CPE is sent to NVD as `?cpeName=...`. NVD maintains a mapping of every known CPE to the CVEs documented as affecting it, so this asks: "give me every CVE where this exact CPE appears in its affected-software list."

**4. Keyword fallback.** Exact CPE matching frequently returns nothing — nmap's version string doesn't always match NVD's stored CPE exactly (e.g. vendor `vsftpd` vs. NVD's `vsftpd_project`), and NVD's CPE-to-CVE mapping isn't exhaustive for every version. When the exact match comes back empty, `keyword_search()` extracts just the vendor + product (deliberately dropping the version) and queries NVD's `keywordSearch` parameter instead — a fuzzy text match across CVE descriptions rather than exact CPE matching. This fallback only runs if nmap actually detected a real version in the first place (see Known Limitations below for why).

**5. Extracting the result.** Once real CVE data comes back, `vulns_from_cpe()` pulls out each CVE's `id`, English `description`, and severity score — checking CVSS v3.1 first, then v3.0, then v2.0, since not every CVE has all three populated, falling back to `"N/A"` if none exist.

## Known Limitations

- Only the top 100 most common ports are scanned by default (configurable in `scanner.py` if you want full coverage — expect it to take significantly longer).
- CVE matching quality depends on nmap's version detection accuracy and NVD's CPE dictionary coverage; obscure or very new services may return no CVEs even when vulnerabilities exist.
- If nmap detects a service but can't determine its version, the tool deliberately reports 0 CVEs for that port rather than guessing — a keyword search on vendor/product alone (e.g. "mysql mysql") would otherwise match thousands of unrelated CVEs and produce misleading results.
- The NVD API without an API key is heavily rate-limited; scans may be slow or partially fail without one.


## Disclaimer

This tool is for educational and authorized security testing purposes only. Scanning systems without permission may be illegal in your jurisdiction.
