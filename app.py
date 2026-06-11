"""COA Pilot — Credit-Card Statement → Excel.

Extracts transactions from credit-card statement PDFs, categorises
them against your Chart of Accounts, reconciles each total against the
statement's 'Purchases / Charges', and exports formatted Excel — one file per
statement or all months combined. Includes a light/dark theme toggle, PDF and
local-folder inputs, per-file downloads and a one-click "download all as ZIP".
"""
import glob
import io
import os
import zipfile

import pandas as pd
import streamlit as st

from statement_parser import parse_statement
from categorizer import load_categories, load_rules, categorize, RULES
from excel_builder import build_workbook, build_combined_workbook
from theme import css

st.set_page_config(page_title="COA Pilot", page_icon="💳",
                   layout="wide", initial_sidebar_state="expanded")

XLSX_MIME = ("application/vnd.openxmlformats-officedocument"
             ".spreadsheetml.sheet")
_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- Theme ----------
if "dark" not in st.session_state:
    st.session_state.dark = True
st.markdown(css("dark" if st.session_state.dark else "light"),
            unsafe_allow_html=True)

# ---------- Hero ----------
st.markdown(
    """
    <div class="hero">
      <span class="status-pill"><span class="live"></span> LIVE · Streamlit</span>
      <h1>💳 <span class="grad">COA Pilot</span></h1>
      <p class="sub">Finance, built smarter — upload credit-card statements,
         auto-categorise against your Chart of Accounts, reconcile to the rupee,
         and export J.V. / Reconciliation / Workings.</p>
      <div class="badges">
        <span class="badge">Auto-categorise</span>
        <span class="badge">Reconciliation check</span>
        <span class="badge">Combine months</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ---------- Sidebar: theme toggle + categories ----------
if st.sidebar.button("☀️ Switch to light" if st.session_state.dark
                     else "🌙 Switch to dark", use_container_width=True):
    st.session_state.dark = not st.session_state.dark
    st.rerun()
st.sidebar.divider()

st.sidebar.header("⚙️ Categories")
st.sidebar.caption("Categories come from **Chart_of_Accounts.csv**. Keyword "
                   "rules live in **category_map.csv** (first match wins).")
rules = RULES
map_upload = st.sidebar.file_uploader("Override mapping (CSV)", type="csv",
                                      key="map")
if map_upload is not None:
    try:
        rules = load_rules(map_upload)
        st.sidebar.success(f"Using uploaded mapping ({len(rules)} rules).")
    except Exception as e:  # noqa: BLE001
        st.sidebar.error(f"Couldn't read mapping: {e}")
CATEGORIES = load_categories()

# ---------- Inputs: PDFs and/or local folder ----------
sources = []   # list of (display_name, path-or-uploaded-file)
tab_pdf, tab_folder = st.tabs(["📄 Add PDFs", "📁 Add folder (local)"])
with tab_pdf:
    ups = st.file_uploader("Drag in one or more statement PDFs", type="pdf",
                           accept_multiple_files=True)
    for u in ups or []:
        sources.append((u.name, u))
with tab_folder:
    st.caption("When running locally, point to a folder and every PDF inside "
               "is processed. (On Streamlit Cloud this path is the server, not "
               "your computer.)")
    folder = st.text_input("Folder path", placeholder="/Users/me/statements")
    if folder:
        if os.path.isdir(folder):
            found = sorted(glob.glob(os.path.join(folder, "*.pdf")))
            st.success(f"Found {len(found)} PDF(s).")
            for p in found:
                sources.append((os.path.basename(p), p))
        else:
            st.error("That folder doesn't exist on this machine.")

if not sources:
    st.info("⬆️ Add statement PDFs (or a local folder) to begin.")
    st.stop()

combine = False
if len(sources) > 1:
    combine = st.toggle("📚 Combine all months into one workbook", value=True)

# ---------- Process ----------
statements = []
generated = []   # (filename, BytesIO) for save-to-folder
for name, src in sources:
    st.divider()
    try:
        parsed = parse_statement(src)
    except Exception as e:  # noqa: BLE001
        st.error(f"Could not read **{name}**: {e}")
        continue
    if not parsed["transactions"]:
        st.warning(f"**{name}** — no spend transactions found.")
        continue

    label = f"{parsed['first_name']} {parsed['month_label']}".strip()
    df = pd.DataFrame([{
        "Date": t["date"], "SerNo.": t["serno"], "Particulars": t["details"],
        "Reward Points": t["reward_points"], "Intl. amount": t["intl_amount"],
        "Amount": t["amount"],
        "As per books": categorize(t["details"], rules)[0],
        "Review?": categorize(t["details"], rules)[1],
    } for t in parsed["transactions"]])

    with st.container(border=True):
        st.subheader(f"{parsed['holder']}  ·  {parsed['month_label'].title()}")
        n_review = int(df["Review?"].sum())
        if n_review:
            st.warning(f"⚠️ {n_review} transaction(s) are **Uncategorized** — "
                       "pick a category in **As per books**.")
        edited = st.data_editor(
            df, key=f"ed_{name}", use_container_width=True, hide_index=True,
            column_config={
                "As per books": st.column_config.SelectboxColumn(
                    "As per books", options=CATEGORIES, required=True),
                "Amount": st.column_config.NumberColumn("Amount", format="%.2f"),
                "Review?": st.column_config.CheckboxColumn("Review?",
                                                           disabled=True),
            },
            disabled=["Date", "SerNo.", "Particulars", "Reward Points",
                      "Intl. amount", "Amount", "Review?"])

        gross = round(edited.loc[edited["Amount"] > 0, "Amount"].sum(), 2)
        net = round(edited["Amount"].sum(), 2)
        purchases = parsed["purchases"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Gross debits", f"₹{gross:,.2f}")
        m2.metric("Net (after CR)", f"₹{net:,.2f}")
        m3.metric("PDF Purchases", f"₹{purchases:,.2f}"
                  if purchases is not None else "—")
        if purchases is not None and abs(gross - purchases) < 0.01:
            m4.metric("Status", "MATCH ✅")
        else:
            diff = (gross - purchases) if purchases is not None else 0
            m4.metric("Status", "CHECK ❌", delta=f"{diff:,.2f}")
            st.error("Doesn't match the statement — review the parsed rows.")

    out_txns = [{
        "date": r["Date"], "serno": r["SerNo."], "details": r["Particulars"],
        "reward_points": r["Reward Points"], "intl_amount": r["Intl. amount"],
        "amount": r["Amount"], "category": r["As per books"],
        "uncertain": bool(r["Review?"]) and r["As per books"] == "Uncategorized",
    } for _, r in edited.iterrows()]
    statements.append({"label": label, "transactions": out_txns,
                       "purchases": purchases})

    if not combine:
        buf = build_workbook(out_txns, purchases)
        fname = f"{label}.xlsx"
        generated.append((fname, buf))
        st.download_button(f"⬇️ Download  {fname}", buf.getvalue(), fname,
                           XLSX_MIME, key=f"dl_{name}")

# ---------- Combined export ----------
if combine and statements:
    st.divider()
    with st.container(border=True):
        st.subheader("📚 Combined workbook")
        tg = sum(round(sum(t["amount"] for t in s["transactions"]
                           if t["amount"] > 0), 2) for s in statements)
        tn = sum(round(sum(t["amount"] for t in s["transactions"]), 2)
                 for s in statements)
        tp = sum(s["purchases"] or 0 for s in statements)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Statements", str(len(statements)))
        c2.metric("Total gross", f"₹{tg:,.2f}")
        c3.metric("Total net", f"₹{tn:,.2f}")
        c4.metric("Status", "MATCH ✅" if abs(tg - tp) < 0.01 else "CHECK ❌")
        buf = build_combined_workbook(statements)
        generated.append(("Combined statements.xlsx", buf))
        st.download_button("⬇️ Download  Combined statements.xlsx",
                           buf.getvalue(), "Combined statements.xlsx",
                           XLSX_MIME, key="dl_combined")

# ---------- Download everything as a ZIP ----------
if len(generated) > 1:
    st.divider()
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, b in generated:
            zf.writestr(fname, b.getvalue())
    zip_buf.seek(0)
    st.download_button(
        f"⬇️ Download all ({len(generated)}) as ZIP",
        zip_buf.getvalue(), "COA Pilot statements.zip", "application/zip",
        key="dl_zip", use_container_width=True)

# ---------- Footer ----------
st.divider()
st.markdown(
    "<div style='text-align:center; color:var(--muted); font-size:.85rem; "
    "padding:8px 0;'>Made by <strong>Rahul Mehta</strong></div>",
    unsafe_allow_html=True)
