#!/usr/bin/env python3
"""Make 'list' queries show a prominent table of notes.
1) _run_spec: store full list in result['list_table'] (not just samples).
2) render block: if list_table present, show it as st.dataframe.
Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

# ---- Part 1: change the list branch in _run_spec ----
old_list = '''            if op == "list":
                cols = [c for c in ["record_id", "city", "consumer_demographic",
                                    "product_category", "retailer_feedback"] if c in filtered.columns]
                result["samples"] = filtered[cols].head(15).to_dict("records")
                result["insight"] = "Listing " + str(min(15, n)) + " of " + str(n) + " matching records."
                return result'''

new_list = '''            if op == "list":
                cols = [c for c in ["record_id", "city", "consumer_demographic",
                                    "product_category", "retailer_feedback"] if c in filtered.columns]
                _tbl = filtered[cols].head(50).copy()
                _tbl.columns = [c.replace("_", " ").title() for c in _tbl.columns]
                result["list_table"] = _tbl
                result["insight"] = ("Showing <b>" + str(min(50, n)) + "</b> of <b>"
                                     + str(n) + "</b> matching retailer notes below.")
                return result'''

if old_list not in src:
    print("ERROR: list branch not found in _run_spec. No changes.")
    sys.exit(1)
src = src.replace(old_list, new_list)

# ---- Part 2: render the list_table in the analytics render block ----
# Anchor: right after the analytics header markdown, before the chart check.
render_anchor = '''                st.markdown(f'<div style="background:#F0FDF4;border-left:4px solid #10B981;padding:0.8rem 1rem;border-radius:8px;margin:0.5rem 0;"><b>📊 Analytics:</b> {r["text"]}</div>', unsafe_allow_html=True)
                if r.get("chart") is not None:'''

render_new = '''                st.markdown(f'<div style="background:#F0FDF4;border-left:4px solid #10B981;padding:0.8rem 1rem;border-radius:8px;margin:0.5rem 0;"><b>📊 Analytics:</b> {r["text"]}</div>', unsafe_allow_html=True)
                if r.get("list_table") is not None:
                    st.dataframe(r["list_table"], use_container_width=True, hide_index=True)
                if r.get("chart") is not None:'''

if render_anchor not in src:
    print("ERROR: analytics render anchor not found. No changes.")
    sys.exit(1)
src = src.replace(render_anchor, render_new)

try:
    ast.parse(src)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".prelist")
with open(UI, "w") as f:
    f.write(src)
print("SUCCESS: list queries now show a prominent table. Backup: view/ui.py.prelist")
