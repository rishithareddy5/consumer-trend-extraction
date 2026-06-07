#!/usr/bin/env python3
"""Replace the analytics top/count chart with a colorful VERTICAL bar chart.
Each bar colored by its trend family; count labels on top; clean exec styling.
Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

# Match the current (already-patched) horizontal-bar block. Try the styled one first.
candidates = []
candidates.append('''                _n = len(counts)
                # gradient: darkest blue for the top bar, lighter going down
                _palette = ["#1E3A8A", "#1D4ED8", "#2563EB", "#3B82F6", "#60A5FA"]
                _bar_colors = [_palette[min(i * len(_palette) // max(_n, 1), len(_palette) - 1)]
                               for i in range(_n)]
                _labels_pretty = [c.replace("_", " ").title() for c in counts[chart_col]]
                fig = px.bar(counts, x="count", y=chart_col, orientation="h",
                             text="count")''')
# also the very original unstyled block as a fallback
candidates.append('''                fig = px.bar(counts, x="count", y=chart_col, orientation="h",
                             title=chart_col.replace("_", " ").title() + " distribution")
                fig.update_traces(marker_color="#2563EB")
                fig.update_layout(height=380, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
                result["chart"] = fig''')

# Find which candidate exists and where its enclosing block ends.
# Simplest robust approach: replace from the 'fig = px.bar(' for count chart up to
# the 'result["chart"] = fig' that follows it, within the else branch.
import re
anchor_start = '                chart_col = gb if gb else tgt'
if anchor_start not in src:
    print("ERROR: cannot find the count-chart section anchor. No changes.")
    sys.exit(1)

# Locate the section: from chart_col line to the next 'result["chart"] = fig'
sidx = src.index(anchor_start)
ridx = src.index('result["chart"] = fig', sidx)
rend = ridx + len('result["chart"] = fig')
section = src[sidx:rend]

new_section = '''                chart_col = gb if gb else tgt
                counts = filtered[chart_col].value_counts().head(12).reset_index()
                counts.columns = [chart_col, "count"]
                # color each bar by its trend family (fallback palette otherwise)
                _fam_color = {}
                for _cat, _labs in LABEL_CATEGORIES.items():
                    for _l in _labs:
                        _fam_color[_l] = CAT_COLORS.get(_cat, "#2563EB")
                _palette_cycle = ["#2563EB", "#10B981", "#8B5CF6", "#EC4899",
                                  "#F59E0B", "#0EA5E9", "#EF4444", "#14B8A6"]
                _bar_colors = []
                for _i, _v in enumerate(counts[chart_col]):
                    _bar_colors.append(_fam_color.get(_v, _palette_cycle[_i % len(_palette_cycle)]))
                _pretty = [str(_v).replace("_", " ").title() for _v in counts[chart_col]]
                import plotly.graph_objects as _go
                fig = _go.Figure(_go.Bar(
                    x=_pretty, y=counts["count"],
                    marker=dict(color=_bar_colors, line=dict(color="white", width=1.5)),
                    text=counts["count"], textposition="outside",
                    textfont=dict(size=18, color="#1E3A8A", family="JetBrains Mono"),
                    cliponaxis=False,
                    hovertemplate="<b>%{x}</b><br>%{y} records<extra></extra>",
                ))
                fig.update_layout(
                    title=dict(text="<b>" + chart_col.replace("_", " ").title() + " Distribution</b>",
                               font=dict(size=19, color="#1E3A8A", family="Inter")),
                    height=460, showlegend=False,
                    margin=dict(l=20, r=20, t=60, b=120),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(239,246,255,0.5)",
                    font=dict(family="Inter", color="#374151", size=13),
                    bargap=0.35,
                    xaxis=dict(tickangle=-35, tickfont=dict(size=12, color="#1E3A8A", family="Inter"),
                               title=None),
                    yaxis=dict(showgrid=True, gridcolor="rgba(37,99,235,0.12)", zeroline=False,
                               title=dict(text="Number of records", font=dict(size=12, color="#9CA3AF")),
                               range=[0, max(counts["count"]) * 1.18]),
                )
                result["chart"] = fig'''

patched = src.replace(section, new_section)
if patched == src:
    print("ERROR: replacement made no change. No changes written.")
    sys.exit(1)
try:
    ast.parse(patched)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".prechart2")
with open(UI, "w") as f:
    f.write(patched)
print("SUCCESS: vertical colorful bar chart applied. Backup: view/ui.py.prechart2")
