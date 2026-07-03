import streamlit as st

from main import main

st.set_page_config(page_title="Port Scanner & Vulnerability Checker", layout="centered")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, [class^="st"], [class*=" st"], .stApp, .stApp * {
    font-family: 'JetBrains Mono', monospace !important;
}

[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def severity_color(score):
    if not isinstance(score, (int, float)):
        return "#6c757d"  # gray for N/A
    if score >= 7.0:
        return "#dc3545"  # red
    if score >= 4.0:
        return "#fd7e14"  # orange
    return "#28a745"  # green


def severity_label(score):
    if not isinstance(score, (int, float)):
        return "N/A"
    return f"{score:.1f}"


st.title("Port Scanner & Vulnerability Checker")
st.caption(
    "Scan a host for open ports, grab service banners, and cross-reference known CVEs."
)

with st.form("scan_form"):
    col1, col2 = st.columns([4, 1])
    with col1:
        ip = st.text_input(
            "Target IP address",
            placeholder="e.g. 192.168.1.1",
            label_visibility="collapsed",
        )
    with col2:
        scan_clicked = st.form_submit_button(
            "Scan", type="primary", use_container_width=True
        )

if scan_clicked:
    if not ip or not ip.strip():
        st.error("Please enter an IP address before scanning.")
    else:
        with st.spinner(f"Scanning {ip.strip()}... this can take 30-90 seconds"):
            results = main(ip.strip())
        st.session_state["results"] = results
        st.session_state["scanned_ip"] = ip.strip()

results = st.session_state.get("results")
scanned_ip = st.session_state.get("scanned_ip")

if results is not None:
    total_ports = len(results)
    total_cves = sum(len(port["cves"]) for port in results)

    st.divider()
    st.subheader(f"Results for {scanned_ip}")

    summary_col1, summary_col2 = st.columns(2)
    summary_col1.metric("Open Ports Found", total_ports)
    summary_col2.metric("Total CVEs Found", total_cves)

    if total_ports == 0:
        st.info("No open ports found on this host.")
    else:
        st.divider()
        for port in results:
            cve_count = len(port["cves"])
            header = f"Port {port['port']} — {port['name']} ({cve_count} CVE{'s' if cve_count != 1 else ''})"
            with st.expander(header):
                st.markdown("**Banner**")
                st.code(port["banner"] or "No banner retrieved", language="text")

                st.markdown("**Known Vulnerabilities**")
                if not port["cves"]:
                    st.success("No known vulnerabilities found.")
                else:
                    for cve in port["cves"]:
                        color = severity_color(cve["score"])
                        label = severity_label(cve["score"])
                        st.markdown(
                            f"""
<div style="border-left: 4px solid {color}; padding: 0.5rem 0.75rem; margin-bottom: 0.5rem; background-color: rgba(128,128,128,0.08); border-radius: 4px;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 600;">{cve["id"]}</span>
        <span style="background-color: {color}; color: white; padding: 0.1rem 0.5rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">{label}</span>
    </div>
    <div style="margin-top: 0.25rem; font-size: 0.9rem;">{cve["description"]}</div>
</div>
""",
                            unsafe_allow_html=True,
                        )
