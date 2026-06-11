"""Category logic driven by two CSV files (both editable, no code changes):

  Chart_of_Accounts.csv  - the accounting Chart of Accounts. The expense-type
                           account names become the valid categories / the
                           dropdown options in the app.
  category_map.csv       - keyword -> account-name rules. First match wins,
                           so list more specific keywords first.

Unknown merchants fall back to "Uncategorized" and are flagged for review.
"""
import csv
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
_COA_FILE = os.path.join(_DIR, "Chart_of_Accounts.csv")
_MAP_FILE = os.path.join(_DIR, "category_map.csv")

# Account types that make sense as expense categories for a card statement.
_EXPENSE_TYPES = {"Expense", "Other Expense", "Cost Of Goods Sold"}
DEFAULT_CATEGORY = "Uncategorized"


def load_categories(coa_path=_COA_FILE):
    """Return the sorted list of valid category names from the COA."""
    cats = []
    with open(coa_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            status = (row.get("Account Status") or "Active").strip()
            if status == "Active" and row.get("Account Type") in _EXPENSE_TYPES:
                cats.append(row["Account Name"].strip())
    if DEFAULT_CATEGORY not in cats:
        cats.append(DEFAULT_CATEGORY)
    return sorted(set(cats))


def load_rules(map_source=_MAP_FILE):
    """Load keyword rules. map_source may be a path or a file-like object."""
    rules = []
    if hasattr(map_source, "read"):
        text = map_source.read()
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        reader = csv.DictReader(text.splitlines())
    else:
        f = open(map_source, newline="", encoding="utf-8")
        reader = csv.DictReader(f)
    for row in reader:
        kw = (row.get("keyword") or "").strip()
        cat = (row.get("category") or "").strip()
        if kw and cat:
            rules.append((kw.upper(), cat))
    return rules


# Default rules loaded once at import; the app can override per-session.
RULES = load_rules()


def categorize(description, rules=None):
    """Return (category, is_uncertain) for a transaction description."""
    up = (description or "").upper()
    for kw, cat in (rules or RULES):
        if kw in up:
            return cat, False
    return DEFAULT_CATEGORY, True
