#!/usr/bin/env python3
"""Fix ugly one-bar-per-note charts. When no group_by is set, never chart by
a free-text/unique column (retailer_feedback, record_id) or by a column that
is uniform (single value). Fall back to a meaningful breakdown: city, else
consumer_demographic, else trend_label. Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

old = '''            else:
                chart_col = gb if gb else tgt
                counts = filtered[chart_col].value_counts().head(12).reset_index()
                counts.columns = [chart_col, "count"]'''

new = '''            else:
                # Choose a sensible column to chart.
                _bad_cols = {"retailer_feedback", "record_id", "visit_date",
                             "salesperson_name", "retailer_id"}
                chart_col = gb if gb else tgt
                # Never chart free-text/unique columns - they make one bar per row.
                if chart_col in _bad_cols:
                    chart_col = None
                # If the chosen column has only one unique value (uniform result),
                # a single bar is useless - break down by city instead.
                if chart_col is not None and filtered[chart_col].nunique() <= 1:
                    chart_col = None
                if chart_col is None:
                    for _cand in ["city", "consumer_demographic", "store_type",
                                  "season", "trend_label"]:
                        if _cand in filtered.columns and filtered[_cand].nunique() > 1:
                            chart_col = _cand
                            break
                    if chart_col is None:
                        chart_col = "trend_label"
                counts = filtered[chart_col].value_counts().head(12).reset_index()
                counts.columns = [chart_col, "count"]'''

if old not in src:
    print("ERROR: chart_col block not found. No changes.")
    sys.exit(1)
src = src.replace(old, new)

try:
    ast.parse(src)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".prechartcol")
with open(UI, "w") as f:
    f.write(src)
print("SUCCESS: count charts now use a meaningful column (city/demographic) instead of one-bar-per-note. Backup: view/ui.py.prechartcol")
