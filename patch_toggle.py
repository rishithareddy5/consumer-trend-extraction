#!/usr/bin/env python3
"""Add a Classify/Analytics radio toggle to Smart Chat and use it instead of
the auto-router. Eliminates misrouting. Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

# 1. Add the radio toggle right before the text input.
#    Anchor on the markdown label line that precedes the chat input.
anchor_label = "    st.markdown('<div style=\"color:#1F2937;font-size:0.95rem;font-weight:700;margin-bottom:0.4rem;\">💬 Type your question or paste a retailer note below:</div>', unsafe_allow_html=True)"

if anchor_label not in src:
    print("ERROR: could not find the input label anchor. No changes.")
    sys.exit(1)

radio_block = '''    _mode = st.radio(
        "Mode",
        ["🔍 Classify a retailer note", "📊 Ask an analytics question"],
        horizontal=True, label_visibility="collapsed", key="cte_mode",
    )
''' + anchor_label

src = src.replace(anchor_label, radio_block)

# 2. Replace the router call with the radio-driven intent.
old_route = '''    if send and chat_input and chat_input.strip():
        intent = _detect_intent(chat_input)
        if intent == "analytics":'''
new_route = '''    if send and chat_input and chat_input.strip():
        intent = "analytics" if st.session_state.get("cte_mode", "").startswith("📊") else "classification"
        if intent == "analytics":'''

if old_route not in src:
    print("ERROR: could not find the routing block. No changes.")
    sys.exit(1)
src = src.replace(old_route, new_route)

try:
    ast.parse(src)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)

shutil.copy(UI, UI + ".pretoggle")
with open(UI, "w") as f:
    f.write(src)
print("SUCCESS: Classify/Analytics toggle added; router replaced. Backup: view/ui.py.pretoggle")
