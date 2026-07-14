import html
import os
from datetime import datetime, timezone

import dotenv
import streamlit as st

from main import main

dotenv.load_dotenv()

APP_PASSWORD = os.getenv("APP_PASSWORD")

st.set_page_config(
    page_title="Port Scanner & Vulnerability Checker", page_icon="🔍", layout="wide"
)

GREEN = "#33ff66"
GREEN_DIM = "#4a7a56"
GREEN_SOFT = "#7fe0a0"
GREEN_PALE = "#8fb89c"
GREEN_BRIGHT_TEXT = "#c8ffd4"
RED = "#ff3b3b"
ORANGE = "#ff9f1c"
YELLOW = "#ffd23f"
BORDER = "#1c3a1c"
ROW_BORDER = "#14261a"
PANEL_BG = "#0a120a"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, [class^="st"], [class*=" st"], .stApp, .stApp * {{
    font-family: 'JetBrains Mono', monospace !important;
}}

[data-testid="stIconMaterial"] {{
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    color: {GREEN} !important;
}}

/* True-black terminal backdrop with CRT scanlines */
.stApp {{
    background: #000000 !important;
}}
[data-testid="stAppViewContainer"] {{
    background: #000000;
    background-image: repeating-linear-gradient(
        0deg,
        rgba(51, 255, 102, 0.025) 0px,
        rgba(51, 255, 102, 0.025) 1px,
        transparent 1px,
        transparent 3px
    );
}}
[data-testid="stHeader"] {{
    background: transparent !important;
}}

[data-testid="stAppViewContainer"] .block-container {{
    max-width: 1300px;
    margin: 0 auto;
    padding: 2.5rem 2rem 4rem;
}}

/* Header panel */
.app-hero {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    padding: 1.75rem 2rem;
    margin-bottom: 1.5rem;
    border: 1px solid {BORDER};
    background: rgba(10, 18, 10, 0.4);
    flex-wrap: wrap;
}}
.app-hero h1 {{
    margin: 0;
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: {GREEN};
}}
.app-hero h1 .cursor {{
    display: inline-block;
    width: 9px;
    height: 16px;
    background: {GREEN};
    margin-left: 6px;
    vertical-align: middle;
    animation: blink 1.1s steps(1) infinite;
}}
@keyframes blink {{
    0%, 49% {{ opacity: 1; }}
    50%, 100% {{ opacity: 0; }}
}}
.app-hero p {{
    margin: 0.35rem 0 0;
    color: {GREEN_DIM};
    font-size: 0.82rem;
}}
.app-status {{
    text-align: right;
}}
.app-status .dot-row {{
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 7px;
    color: {GREEN};
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    font-weight: 600;
}}
.app-status .dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: {GREEN};
    box-shadow: 0 0 6px {GREEN};
    animation: pulse 1.6s ease-in-out infinite;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.35; }}
}}
.app-status .sub {{
    margin-top: 4px;
    color: {GREEN_DIM};
    font-size: 0.75rem;
}}

/* Inputs */
.stTextInput input {{
    border-radius: 0 !important;
    background: {PANEL_BG} !important;
    border: none !important;
    color: {GREEN_BRIGHT_TEXT} !important;
    caret-color: {GREEN} !important;
    box-shadow: none !important;
}}
[data-testid="stTextInputRootElement"] {{
    border-radius: 0 !important;
    background: {PANEL_BG} !important;
    border: 1px solid {BORDER} !important;
    box-shadow: none !important;
}}
[data-testid="stTextInputRootElement"]:focus-within {{
    border-color: {GREEN} !important;
    box-shadow: 0 0 0 1px {GREEN} !important;
}}
[data-baseweb="base-input"] {{
    background: {PANEL_BG} !important;
}}
[data-testid="stTextInput"] label p {{
    color: {GREEN_DIM} !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}}

/* Terminal "> " prompt prefix on the scan target field (not the password field) */
[data-testid="stTextInputRootElement"]:not(:has(input[type="password"])) {{
    position: relative;
    padding-left: 22px;
}}
[data-testid="stTextInputRootElement"]:not(:has(input[type="password"]))::before {{
    content: ">";
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: {GREEN};
    font-weight: 700;
    pointer-events: none;
    z-index: 1;
}}

/* Defeat the browser's autofill highlight so it doesn't blow out the theme */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {{
    -webkit-text-fill-color: {GREEN_BRIGHT_TEXT} !important;
    -webkit-box-shadow: 0 0 0 1000px {PANEL_BG} inset !important;
    caret-color: {GREEN} !important;
}}

/* Only show the "Press Enter to submit form" hint on hover/focus, and never
   on password fields (it overlaps the show/hide-password icon there) */
[data-testid="InputInstructions"] {{
    opacity: 0;
    color: {GREEN_DIM} !important;
    transition: opacity 0.15s ease-in-out;
}}
[data-testid="stTextInput"]:hover [data-testid="InputInstructions"],
[data-testid="stTextInput"]:focus-within [data-testid="InputInstructions"] {{
    opacity: 1;
}}
[data-testid="stTextInput"]:has(input[type="password"]) [data-testid="InputInstructions"] {{
    opacity: 0 !important;
}}

/* Buttons: solid green, black text, sharp corners */
div[data-testid="stFormSubmitButton"] button,
.stButton button {{
    border-radius: 0 !important;
    background: {GREEN} !important;
    color: #000000 !important;
    border: 1px solid {GREEN} !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    transition: transform 0.05s ease-in-out, box-shadow 0.15s ease-in-out;
}}
div[data-testid="stFormSubmitButton"] button:hover,
.stButton button:hover {{
    box-shadow: 0 0 14px rgba(51, 255, 102, 0.55);
    color: #000000 !important;
}}
div[data-testid="stFormSubmitButton"] button:active,
.stButton button:active {{
    transform: scale(0.98);
}}
div[data-testid="stFormSubmitButton"] button p,
.stButton button p {{
    color: #000000 !important;
}}

/* Alerts: dark panel with colored left border instead of filled color */
[data-testid="stAlert"] {{
    border-radius: 0 !important;
    background: {PANEL_BG} !important;
    border: 1px solid {BORDER} !important;
}}

/* Section labels */
.section-label {{
    color: {GREEN_DIM};
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0.9rem 0 0.5rem;
}}

/* Vulnerability findings table */
.vuln-table {{
    width: 100%;
    border-collapse: collapse;
}}
.vuln-table th {{
    text-align: left;
    padding: 8px 10px;
    color: {GREEN_DIM};
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-bottom: 1px solid {BORDER};
}}
.vuln-table td {{
    padding: 11px 10px;
    font-size: 0.82rem;
    border-bottom: 1px solid {ROW_BORDER};
    vertical-align: top;
}}
.vuln-table tr:last-child td {{
    border-bottom: none;
}}
.vuln-banner {{
    color: {GREEN_DIM};
    font-size: 0.72rem;
    margin-top: 2px;
}}
.cve-badge {{
    display: inline-block;
    padding: 2px 8px;
    border: 1px solid var(--badge-color);
    color: var(--badge-color);
    font-size: 0.68rem;
    letter-spacing: 0.06em;
    white-space: nowrap;
}}

/* Stat cards */
.stat-card {{
    background: {PANEL_BG};
    border: 1px solid {BORDER};
    padding: 18px 20px;
    transition: border-color 0.15s ease-in-out;
}}
.stat-card:hover {{
    border-color: {GREEN};
}}
.stat-card .stat-label {{
    color: {GREEN_DIM};
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
.stat-card .stat-value {{
    font-size: 2rem;
    font-weight: 700;
    margin-top: 6px;
}}

.subheader-green {{
    color: {GREEN};
    font-weight: 700;
}}

hr {{
    border-color: {ROW_BORDER} !important;
    opacity: 1;
}}
</style>
""",
    unsafe_allow_html=True,
)


def render_hero(subtitle, show_status=False, container=None):
    target = container if container is not None else st
    if show_status:
        last_scan = st.session_state.get("last_scan_at")
        if last_scan:
            elapsed = int((datetime.now(timezone.utc) - last_scan).total_seconds())
            h, rem = divmod(elapsed, 3600)
            m, s = divmod(rem, 60)
            scan_line = f"last scan: {h:02d}:{m:02d}:{s:02d} ago"
        else:
            scan_line = "no scans run yet"
        status_html = f"""
<div class="app-status">
    <div class="dot-row"><span class="dot"></span>SYSTEM ONLINE</div>
    <div class="sub">{scan_line}</div>
</div>
"""
    else:
        status_html = ""

    target.markdown(
        f"""
<div class="app-hero">
    <div>
        <h1>NETSCAN<span class="cursor"></span></h1>
        <p>{subtitle}</p>
    </div>
    {status_html}
</div>
""",
        unsafe_allow_html=True,
    )


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown(
            f'<p style="color:{GREEN_DIM};font-size:0.82rem;margin:0 0 0.75rem;">'
            "root@netscan:~# authentication required</p>",
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            entered_pw = st.text_input("Enter access password", type="password")
            login_clicked = st.form_submit_button(
                "Login ▸", type="primary", use_container_width=True
            )

        if login_clicked:
            if entered_pw == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
    st.stop()


def severity_tier(score):
    if not isinstance(score, (int, float)):
        return "N/A", GREEN_DIM
    if score >= 9.0:
        return "CRITICAL", RED
    if score >= 7.0:
        return "HIGH", ORANGE
    if score >= 4.0:
        return "MEDIUM", YELLOW
    return "LOW", GREEN


hero_placeholder = st.empty()

with st.form("scan_form"):
    col1, col2 = st.columns([5, 1])
    with col1:
        ip = st.text_input(
            "Target IP address",
            placeholder="e.g. 192.168.1.1",
            label_visibility="collapsed",
        )
    with col2:
        scan_clicked = st.form_submit_button(
            "Run Scan ▸", type="primary", use_container_width=True
        )

if scan_clicked:
    if not ip or not ip.strip():
        st.error("Please enter an IP address before scanning.")
    else:
        with st.spinner(f"> scanning {ip.strip()} ... this can take 30-90 seconds"):
            results = main(ip.strip())
        st.session_state["results"] = results
        st.session_state["scanned_ip"] = ip.strip()
        st.session_state["last_scan_at"] = datetime.now(timezone.utc)

render_hero(
    "root@netscan:~# port scanner &amp; vulnerability audit",
    show_status=True,
    container=hero_placeholder.container(),
)

results = st.session_state.get("results")
scanned_ip = st.session_state.get("scanned_ip")


def render_stat_card(label, value, color):
    return f"""
<div class="stat-card">
    <div class="stat-label">{label}</div>
    <div class="stat-value" style="color: {color};">{value}</div>
</div>
"""


if results is not None:
    total_ports = len(results)
    all_cves = [cve for port in results for cve in port["cves"]]
    total_cves = len(all_cves)
    critical_cves = sum(
        1 for cve in all_cves if isinstance(cve["score"], (int, float)) and cve["score"] >= 9.0
    )

    st.divider()
    st.markdown(
        f'<div class="subheader-green">RESULTS FOR {html.escape(scanned_ip)}</div>',
        unsafe_allow_html=True,
    )

    summary_col1, summary_col2, summary_col3 = st.columns(3, gap="medium")
    summary_col1.markdown(
        render_stat_card("Open Ports", total_ports, GREEN), unsafe_allow_html=True
    )
    summary_col2.markdown(
        render_stat_card("Vulnerabilities", total_cves, RED), unsafe_allow_html=True
    )
    summary_col3.markdown(
        render_stat_card("Critical CVEs (≥9.0)", critical_cves, RED),
        unsafe_allow_html=True,
    )

    if total_ports == 0:
        st.info("No open ports found on this host.")
    else:
        st.markdown(
            '<div class="section-label">Vulnerability Findings</div>',
            unsafe_allow_html=True,
        )

        rows_html = []
        for port in results:
            service_cell = (
                f"{html.escape(port['name'])}"
                f'<div class="vuln-banner">{html.escape(port["banner"]) or "no banner retrieved"}</div>'
            )
            if not port["cves"]:
                rows_html.append(
                    "<tr>"
                    f'<td style="color: {GREEN};white-space: nowrap;">{port["port"]}</td>'
                    f'<td style="color: {GREEN_BRIGHT_TEXT};white-space: nowrap;">{service_cell}</td>'
                    f'<td style="color: {GREEN_DIM};">&mdash;</td>'
                    f'<td style="color: {GREEN_DIM};">no known vulnerabilities</td>'
                    f'<td><span class="cve-badge" style="--badge-color: {GREEN};">CLEAN</span></td>'
                    f'<td style="color: {GREEN_DIM};text-align: right;">&mdash;</td>'
                    "</tr>"
                )
            else:
                for cve in port["cves"]:
                    label, color = severity_tier(cve["score"])
                    score_text = (
                        f"{cve['score']:.1f}"
                        if isinstance(cve["score"], (int, float))
                        else "N/A"
                    )
                    rows_html.append(
                        "<tr>"
                        f'<td style="color: {GREEN};white-space: nowrap;">{port["port"]}</td>'
                        f'<td style="color: {GREEN_BRIGHT_TEXT};white-space: nowrap;">{service_cell}</td>'
                        f'<td style="color: {GREEN_SOFT};white-space: nowrap;">{html.escape(cve["id"])}</td>'
                        f'<td style="color: {GREEN_PALE};">{html.escape(cve["description"])}</td>'
                        f'<td><span class="cve-badge" style="--badge-color: {color};">{label}</span></td>'
                        f'<td style="color: {color};text-align: right;">{score_text}</td>'
                        "</tr>"
                    )

        table_header = (
            "<tr><th>Port</th><th>Service</th><th>CVE ID</th><th>Description</th>"
            '<th>Severity</th><th style="text-align: right;">CVSS</th></tr>'
        )
        st.markdown(
            f'<table class="vuln-table"><thead>{table_header}</thead>'
            f'<tbody>{"".join(rows_html)}</tbody></table>',
            unsafe_allow_html=True,
        )
