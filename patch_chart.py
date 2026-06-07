#!/usr/bin/env python3
"""Make analytics charts visually impressive for the CEO demo:
big count labels on bars, gradient-style blues, bold readable text,
clean background. Targets the top/count chart in the new _run_spec.
Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

old = '''                fig = px.bar(counts, x="count", y=chart_col, orientation="h",
                             title=chart_col.replace("_", " ").title() + " distribution")
                fig.update_traces(marker_color="#2563EB")
                fig.update_layout(height=380, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
                result["chart"] = fig'''

new = '''                _n = len(counts)
                # gradient: darkest blue for the top bar, lighter going down
                _palette = ["#1E3A8A", "#1D4ED8", "#2563EB", "#3B82F6", "#60A5FA"]
                _bar_colors = [_palette[min(i * len(_palette) // max(_n, 1), len(_palette) - 1)]
                               for i in range(_n)]
                _labels_pretty = [c.replace("_", " ").title() for c in counts[chart_col]]
                fig = px.bar(counts, x="count", y=chart_col, orientation="h",
                             text="count")
                fig.update_traces(
                    marker=dict(color=_bar_colors,
                                line=dict(color="rgba(255,255,255,0.6)", width=1)),
                    textposition="outside",
                    textfont=dict(size=17, color="#1E3A8A", family="JetBrains Mono"),
                    cliponaxis=False,
                    hovertemplate="<b>%{y}</b><br>%{x} records<extra></extra>",
                )
                fig.update_layout(
                    title=dict(text="<b>" + chart_col.replace("_", " ").title() + " Distribution</b>",
                               font=dict(size=18, color="#1E3A8A", family="Inter")),
                    height=max(380, 40 * _n + 120), showlegend=False,
                    margin=dict(l=10, r=70, t=55, b=35),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(239,246,255,0.6)",
                    font=dict(family="Inter", color="#374151", size=14),
                    bargap=0.35,
                    yaxis=dict(autorange="reversed",
                               tickfont=dict(size=14, color="#1E3A8A", family="Inter"),
                               title=None),
                    xaxis=dict(showgrid=True, gridcolor="rgba(37,99,235,0.12)",
                               zeroline=False, title=dict(text="Number of records",
                               font=dict(size=12, color="#9CA3AF")),
                               range=[0, max(counts["count"]) * 1.2]),
                )
                result["chart"] = fig'''

if old not in src:
    # maybe an earlier chart patch already ran; try the labeled variant
    alt = '''                fig = px.bar(counts, x="count", y=chart_col, orientation="h",
                             title=chart_col.replace("_", " ").title() + " distribution",
                             text="count")'''
    if alt in src:
        print("NOTE: an earlier chart patch is present. Please tell me — I'll adjust.")
        sys.exit(1)
    print("ERROR: could not find the count-chart block. No changes.")
    sys.exit(1)

patched = src.replace(old, new)
try:
    ast.parse(patched)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".prechart")
with open(UI, "w") as f:
    f.write(patched)
print("SUCCESS: charts upgraded (gradient bars + big count labels). Backup: view/ui.py.prechart")
