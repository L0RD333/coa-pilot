"""Parses a credit-card statement PDF into structured data.

Returns a dict with:
  holder        - card-holder name (e.g. "MS NEETIKA PUNEET GARG")
  first_name    - first name only, title-cased (e.g. "Neetika")
  statement_end - statement period end date (datetime.date)
  month_label   - lowercase month of the statement (e.g. "may")
  purchases     - the "Purchases / Charges" figure from the summary (float)
  transactions  - list of dicts: date, serno, details, reward_points,
                  intl_amount, amount (CR -> negative)

Settlement / payment entries (autodebit payments, returns, fee reversals)
are excluded, because they are not spend. What remains sums (gross debits)
to the statement's "Purchases / Charges" figure, which is the reconciliation
check.
"""
import re
from datetime import datetime

import pdfplumber

_TXN = re.compile(
    r'(?P<date>\d{2}/\d{2}/\d{4})\s+(?P<serno>\d{8,})\s+(?P<details>.*?)\s+'
    r'(?P<rp>-?\d+)(?:\s+(?P<intl>[\d.]+\s*USD))?\s+'
    r'(?P<amt>[\d,]+\.\d{2})(?P<cr>\s+CR)?\s*$'
)
# Settlement / payment rows that are NOT spend and must be excluded.
_EXCLUDE = re.compile(
    r'autodebit payment|auto dr\.retn|rev fee|igst-rev|payment recd', re.I
)
_SUMMARY = re.compile(
    r'Previous Balance.*?Payments / Credits\s*\n'
    r'[`\s]*([\d,]+\.\d{2})[`\s]+([\d,]+\.\d{2})', re.S
)
_NAME = re.compile(r'^(MR|MRS|MS)\s+([A-Z][A-Z .]+?)\s*$', re.M)
_PERIOD = re.compile(
    r'Statement period\s*:\s*[A-Za-z]+ \d+, \d{4}\s+to\s+'
    r'([A-Za-z]+ \d+, \d{4})'
)


def _to_float(s):
    return float(s.replace(',', ''))


def parse_statement(file_like):
    """file_like: a path or a file-like object (e.g. Streamlit UploadedFile)."""
    with pdfplumber.open(file_like) as pdf:
        full = "\n".join((pg.extract_text() or "") for pg in pdf.pages)

    m = _SUMMARY.search(full)
    purchases = _to_float(m.group(2)) if m else None

    nm = _NAME.search(full)
    holder = nm.group(0).strip() if nm else "Unknown"
    name_part = nm.group(2).strip() if nm else "Unknown"
    first_name = name_part.split()[0].title() if name_part else "Unknown"

    pm = _PERIOD.search(full)
    statement_end = None
    month_label = ""
    if pm:
        statement_end = datetime.strptime(pm.group(1), "%B %d, %Y").date()
        month_label = statement_end.strftime("%B").lower()

    txns = []
    for line in full.split("\n"):
        mt = _TXN.search(line.strip())
        if not mt:
            continue
        d = mt.groupdict()
        if _EXCLUDE.search(d['details']):
            continue
        amount = _to_float(d['amt']) * (-1 if d['cr'] else 1)
        txns.append({
            "date": datetime.strptime(d['date'], "%d/%m/%Y").date(),
            "serno": d['serno'],
            "details": re.sub(r'\s+', ' ', d['details']).strip(),
            "reward_points": int(d['rp']),
            "intl_amount": (d['intl'] or "").strip(),
            "amount": round(amount, 2),
        })

    return {
        "holder": holder,
        "first_name": first_name,
        "statement_end": statement_end,
        "month_label": month_label,
        "purchases": purchases,
        "transactions": txns,
    }
