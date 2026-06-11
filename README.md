# COA Pilot

A Streamlit app that turns **credit-card statement PDFs** into a
formatted Excel workbook with three sheets — **J.V.**, **Reconciliation**, and
**Workings** — matching the in-house accounting template. It can produce one
file per statement, or combine several months into a single workbook.

## Features

- **Light / dark theme** — toggle with the ☀️/🌙 button (top-right).
- **Add PDFs or a local folder** — drag in files, or (when run locally) point
  to a folder and every PDF inside is processed.
- **Auto-categorise** against your Chart of Accounts; edit any row inline.
- **Reconciliation** — each statement's gross debits are checked against its
  "Purchases / Charges"; the combined sheet shows **Gross** and **Net (after
  CR)** side by side, per statement and as a grand total.
- **Export** one workbook per statement or all months **combined**.
- **Download all as ZIP** — when several statements are processed, grab every
  workbook in one click (handy on Streamlit Cloud, where the browser controls
  the download location).

## What it does

1. **Reads the PDF** and extracts every spend transaction. Credit (CR) entries
   become negative. Autodebit payments, returns and fee reversals are excluded
   (they are settlements, not spend).
2. **Categorises** each transaction against your **Chart of Accounts**. The
   valid categories are read from `Chart_of_Accounts.csv`; the keyword→account
   rules live in `category_map.csv`. Anything unmatched becomes *Uncategorized*
   and is flagged for review (highlighted yellow in Workings).
3. **Reconciles** the total of all debits against the statement's
   "Purchases / Charges" figure — a green **MATCH** means nothing was missed.
4. **Exports** either:
   - one workbook per statement, named `<FirstName> <month>.xlsx`
     (e.g. `Neetika may.xlsx`), or
   - a single **combined** workbook (`Combined statements.xlsx`) with all months
     in one Workings sheet, a combined J.V., and a Reconciliation sheet that
     verifies each statement separately plus a grand total.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the printed URL (usually http://localhost:8501), upload PDF(s), review the
categories, and download.

## Deploy on Streamlit Community Cloud (free)

1. Push these files to a new GitHub repo:
   ```bash
   git init
   git add .
   git commit -m "COA Pilot"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo>.git
   git push -u origin main
   ```
2. Go to **https://share.streamlit.io**, sign in with GitHub, **New app**,
   pick the repo/branch, set the main file to `app.py`, and **Deploy**.

## Managing categories (no code changes)

- **Add / change categories:** replace `Chart_of_Accounts.csv` with your latest
  export. Every active *Expense / Other Expense / Cost of Goods Sold* account
  becomes a selectable category in the app.
- **Teach it new merchants:** edit `category_map.csv` — each row is
  `keyword,category`. Rules are checked top-to-bottom (first match wins), so put
  specific keywords (hotel brands, telecoms) above generic ones. The category
  must exactly match an account name in the Chart of Accounts.
- **Try a mapping without committing:** in the app sidebar you can upload a
  replacement `category_map.csv` for the current session, or download the
  current one as a starting point.

## Project layout

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI: upload, review/edit, reconcile, per-file or combined download |
| `statement_parser.py` | Extracts transactions + summary figures from the PDF |
| `categorizer.py` | Loads the COA + mapping CSVs and assigns categories |
| `excel_builder.py` | Builds the formatted single and combined workbooks |
| `Chart_of_Accounts.csv` | Your Chart of Accounts (source of valid categories) |
| `category_map.csv` | Editable keyword → account mapping rules |
| `requirements.txt` | Python dependencies |

## Notes & limits

- Built for a specific Corporate/Business Gold credit-card statement layout. A very
  different layout may need tweaks to the regexes in `statement_parser.py`.
- The reconciliation **MATCH** is the safety net: if it isn't green, the parse
  missed or misread something — don't rely on the output until it reconciles.
- Run locally and no data leaves your machine. On Streamlit Cloud, PDFs are
  processed in memory on Streamlit's servers.

---

_Made by **Rahul Mehta**._
