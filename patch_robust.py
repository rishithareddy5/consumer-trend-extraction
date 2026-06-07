#!/usr/bin/env python3
"""Two fixes for multi-filter analytics:
1. _validate_spec: if model puts column keys at TOP LEVEL (not in 'filters'),
   pull them into filters. Also map trend synonyms (spicy->rising_spicy...).
2. _spec_prompt: add a two-filter 'spicy + teenagers' example so the model
   wraps correctly and maps 'spicy' to trend_label.
Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

# ---------- FIX 1: make _validate_spec robust ----------
# Insert top-level-key rescue + trend synonym mapping right after the _aliases dict.
anchor = '''            # remap aliased filter keys to real column names
            _f = spec.get("filters") or {}'''

inject = '''            # RESCUE: if the model put column keys at top level instead of in "filters",
            # pull recognised columns into filters.
            _real_cols = {"season","city","store_type","consumer_demographic",
                          "product_category","month","quarter","trend_label",
                          "retailer_id","salesperson_name","week_number","visit_date"}
            _topf = spec.get("filters") or {}
            if not isinstance(_topf, dict):
                _topf = {}
            for _tk in list(spec.keys()):
                if _tk in _real_cols and _tk not in _topf:
                    _topf[_tk] = spec[_tk]
                if _tk in _aliases and _aliases[_tk] in _real_cols and _aliases[_tk] not in _topf:
                    _topf[_aliases[_tk]] = spec[_tk]
            spec["filters"] = _topf
            # TREND SYNONYMS: map loose words to real trend_label values
            _trend_syn = {
                "spicy": "rising_spicy_flavor_preference",
                "spicy notes": "rising_spicy_flavor_preference",
                "spice": "rising_spicy_flavor_preference",
                "sugar free": "sugar_free_demand", "sugarfree": "sugar_free_demand",
                "sugar-free": "sugar_free_demand", "diabetic": "sugar_free_demand",
                "protein": "protein_snack_trend", "gym": "protein_snack_trend",
                "tangy": "tangy_sour_flavor_rise", "sour": "tangy_sour_flavor_rise",
                "fusion": "fusion_flavor_adoption", "regional": "regional_flavor_revival",
                "western": "western_snack_influence", "premium": "premium_packaging_demand",
                "gifting": "festive_gifting_trend", "festive": "festive_gifting_trend",
                "vegan": "plant_based_adoption", "plant based": "plant_based_adoption",
                "health": "health_conscious_snacking", "healthy": "health_conscious_snacking",
                "youth": "youth_driven_consumption", "online": "online_impulse_buying",
                "convenience": "convenience_format_preference",
                "small pack": "small_pack_affordability_preference",
                "affordability": "small_pack_affordability_preference",
            }
            if "trend_label" in spec["filters"]:
                _tv = str(spec["filters"]["trend_label"]).lower().strip()
                if _tv in _trend_syn:
                    spec["filters"]["trend_label"] = _trend_syn[_tv]
            # if 'spicy notes' etc landed in product_category, move to trend_label
            if "product_category" in spec["filters"]:
                _pv = str(spec["filters"]["product_category"]).lower().strip()
                if _pv in _trend_syn:
                    spec["filters"]["trend_label"] = _trend_syn[_pv]
                    del spec["filters"]["product_category"]
            # remap aliased filter keys to real column names
            _f = spec.get("filters") or {}'''

if anchor not in src:
    print("ERROR: validator anchor not found. No changes.")
    sys.exit(1)
src = src.replace(anchor, inject)

# ---------- FIX 2: add a two-filter spicy+teenagers example to the prompt ----------
prompt_anchor = '''                "Q: list spicy notes in Hyderabad\\n"
                'A: {"filters": {"trend_label": "rising_spicy_flavor_preference", "city": "Hyderabad"}, "group_by": null, "operation": "list", "target": "retailer_feedback"}\\n'
'''
prompt_add = prompt_anchor + '''                "Q: list spicy notes among teenagers\\n"
                'A: {"filters": {"trend_label": "rising_spicy_flavor_preference", "consumer_demographic": "teenagers"}, "group_by": null, "operation": "list", "target": "retailer_feedback"}\\n'
'''
if prompt_anchor not in src:
    print("ERROR: prompt example anchor not found. (Validator fix still applied if reached here?) No changes.")
    sys.exit(1)
src = src.replace(prompt_anchor, prompt_add)

try:
    ast.parse(src)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".prerobust")
with open(UI, "w") as f:
    f.write(src)
print("SUCCESS: validator made robust + prompt example added. Backup: view/ui.py.prerobust")
