#!/usr/bin/env python3
"""Replace _spec_prompt with a leaner, sharper version tuned for small 2B model.
Adds a product_category example and trims noise. Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

# find the whole existing _spec_prompt function (from its def to the line before def _parse_spec)
start_marker = "        def _spec_prompt(question, valid_trends):\n"
end_marker = "        def _parse_spec(raw):"

i = src.find(start_marker)
j = src.find(end_marker)
if i == -1 or j == -1 or j < i:
    print("ERROR: could not locate _spec_prompt boundaries. No changes.")
    sys.exit(1)

new_fn = '''        def _spec_prompt(question, valid_trends):
            return (
                "You output ONLY one line of JSON. No prose, no markdown.\\n"
                "Map the question to filters using these column names exactly: "
                "season, city, store_type, consumer_demographic, product_category, month, quarter, trend_label.\\n"
                "operation is one of: count, list, top, compare.\\n\\n"
                "Q: what trends show up for makhana\\n"
                'A: {"filters": {"product_category": "makhana"}, "group_by": null, "operation": "top", "target": "trend_label"}\\n'
                "Q: trends among senior citizens\\n"
                'A: {"filters": {"consumer_demographic": "senior citizens"}, "group_by": null, "operation": "top", "target": "trend_label"}\\n'
                "Q: what sells during Diwali\\n"
                'A: {"filters": {"month": "diwali"}, "group_by": null, "operation": "top", "target": "trend_label"}\\n'
                "Q: top trends in kirana stores\\n"
                'A: {"filters": {"store_type": "Kirana Store"}, "group_by": null, "operation": "top", "target": "trend_label"}\\n'
                "Q: list spicy notes in Hyderabad\\n"
                'A: {"filters": {"trend_label": "rising_spicy_flavor_preference", "city": "Hyderabad"}, "group_by": null, "operation": "list", "target": "retailer_feedback"}\\n'
                "Q: sugar free demand in winter\\n"
                'A: {"filters": {"trend_label": "sugar_free_demand", "season": "Winter"}, "group_by": "city", "operation": "count", "target": "trend_label"}\\n'
                "Q: " + question + "\\n"
                "A:"
            )

'''

patched = src[:i] + new_fn + src[j:]
try:
    ast.parse(patched)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".preprompt")
with open(UI, "w") as f:
    f.write(patched)
print("SUCCESS: _spec_prompt replaced with leaner version. Backup: view/ui.py.preprompt")
