import os
import time

import dotenv
import requests

dotenv.load_dotenv()
NVD_API_KEY = os.getenv("NVD_API_KEY")
TEST_IP = os.getenv("TEST_IP")

NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def get_cves(cpe):
    try:
        headers = {
            "apiKey": NVD_API_KEY,
        }
        # response = requests.get(NVD_URL, params={"cpeName": cpe}, headers=headers)
        response = requests.get(
            NVD_URL,
            params={
                "cpeName": cpe,
            },
            headers={"apiKey": NVD_API_KEY},
        )
        jresponse = response.json()
        return jresponse
    except (
        requests.exceptions.JSONDecodeError,
        requests.exceptions.RequestException,
    ) as e:
        print(f"Error: {e}")
        return {"vulnerabilities": []}


def get_cves_from_keyword(keyword):
    try:
        headers = {
            "apiKey": NVD_API_KEY,
        }
        # response = requests.get(NVD_URL, params={"cpeName": cpe}, headers=headers)
        response = requests.get(
            NVD_URL,
            params={
                "keywordSearch": keyword,
            },
            headers={"apiKey": NVD_API_KEY},
        )
        jresponse = response.json()
        return jresponse
    except (
        requests.exceptions.JSONDecodeError,
        requests.exceptions.RequestException,
    ) as e:
        print(f"Error: {e}")
        return {"vulnerabilities": []}


def keyword_search(cpe):
    parts = cpe.split(":")
    keywords = parts[3:5]
    return " ".join(keywords)


def convert_cpe(cpe):
    new_cpe = cpe.replace("cpe:/", "cpe:2.3:")
    new_cpe += ":*:*:*:*:*:*:*"
    return new_cpe


def vulns_from_cpe(cpe):
    vulns = []
    cpe = convert_cpe(cpe)
    keyword = keyword_search(cpe)
    result = get_cves(cpe)
    if result["vulnerabilities"] == []:
        result = get_cves_from_keyword(keyword)
    for vuln in result["vulnerabilities"]:
        metrics = vuln["cve"]["metrics"]
        if metrics.get("cvssMetricV31"):
            score = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
        elif metrics.get("cvssMetricV30"):
            score = metrics["cvssMetricV30"][0]["cvssData"]["baseScore"]
        elif metrics.get("cvssMetricV2"):
            score = metrics["cvssMetricV2"][0]["cvssData"]["baseScore"]
        else:
            score = "N/A"

        vuln_info = {
            "id": vuln["cve"]["id"],
            "description": vuln["cve"]["descriptions"][0]["value"],
            "score": score,
        }
        vulns.append(vuln_info)
    return vulns


if __name__ == "__main__":
    from scanner import scan_host

    open_ports = scan_host(TEST_IP)
    for port in open_ports:
        if port["cpe"]:
            print(f"\n=== Port {port['port']} ({port['name']}) — {port['cpe']} ===")
            vulns = vulns_from_cpe(port["cpe"])
            print(f"Found {len(vulns)} CVEs")
            for v in vulns[:3]:
                print(f"  {v['id']} (score: {v['score']})")
            time.sleep(1)
