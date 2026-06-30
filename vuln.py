import os

import dotenv
import requests

dotenv.load_dotenv()
NVD_API_KEY = os.getenv("NVD_API_KEY")

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
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error: {e}")
        return {"vulnerabilities": []}


def vulns_from_cpe(cpe):
    vulns = []
    result = get_cves(cpe)

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
    print(vulns_from_cpe("cpe:2.3:a:python:python:3.11:*:*:*:*:*:*:*"))
