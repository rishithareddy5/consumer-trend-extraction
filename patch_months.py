#!/usr/bin/env python3
"""Make month-name and quarter queries work.
1. Convert month names (december->12) into the 'month' filter.
2. Handle quarters (q4, quarter 4 -> 'Q4') into the 'quarter' filter.
3. RESCUE: if a month name or quarter wrongly landed in 'season', move it.
Inserted right after the trend-synonym product_category block, before the
'remap aliased filter keys' line. Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

anchor = '''            # remap aliased filter keys to real column names
            _f = spec.get("filters") or {}
            _fixed = {}'''

inject = '''            # MONTH NAMES -> month number; QUARTERS -> Q1..Q4; rescue from wrong fields
            _month_map = {
                "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
                "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
                "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
                "october": 10, "oct": 10, "november": 11, "nov": 11,
                "december": 12, "dec": 12,
            }
            _quarter_map = {
                "q1": "Q1", "q2": "Q2", "q3": "Q3", "q4": "Q4",
                "quarter 1": "Q1", "quarter 2": "Q2", "quarter 3": "Q3", "quarter 4": "Q4",
                "first quarter": "Q1", "second quarter": "Q2",
                "third quarter": "Q3", "fourth quarter": "Q4",
            }
            _valid_seasons = {"summer", "monsoon", "winter"}
            _flt = spec.get("filters") or {}
            # If a month name / quarter wrongly landed in 'season', move it out.
            if "season" in _flt:
                _sv = str(_flt["season"]).lower().strip()
                if _sv in _month_map:
                    _flt["month"] = _month_map[_sv]; del _flt["season"]
                elif _sv in _quarter_map:
                    _flt["quarter"] = _quarter_map[_sv]; del _flt["season"]
                elif _sv not in _valid_seasons:
                    # not a real season at all - drop it so it doesn't zero out results
                    del _flt["season"]
            # Normalise an explicit 'month' value that is a name.
            if "month" in _flt:
                _mv = str(_flt["month"]).lower().strip()
                if _mv in _month_map:
                    _flt["month"] = _month_map[_mv]
            # Normalise an explicit 'quarter' value.
            if "quarter" in _flt:
                _qv = str(_flt["quarter"]).lower().strip()
                if _qv in _quarter_map:
                    _flt["quarter"] = _quarter_map[_qv]
            spec["filters"] = _flt
            # remap aliased filter keys to real column names
            _f = spec.get("filters") or {}
            _fixed = {}'''

if anchor not in src:
    print("ERROR: anchor not found. No changes.")
    sys.exit(1)
src = src.replace(anchor, inject)

try:
    ast.parse(src)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".premonths")
with open(UI, "w") as f:
    f.write(src)
print("SUCCESS: month-name + quarter handling added, season-misroute rescued. Backup: view/ui.py.premonths")
