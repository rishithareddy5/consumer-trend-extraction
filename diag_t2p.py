import json, requests

API_URL = "http://localhost:8000"

def spec_prompt(question):
    return (
        "You output ONLY one line of JSON. No prose, no markdown.\n"
        "Map the question to filters using these column names exactly: "
        "season, city, store_type, consumer_demographic, product_category, month, quarter, trend_label.\n"
        "operation is one of: count, list, top, compare.\n\n"
        "Q: what trends show up for makhana\n"
        'A: {"filters": {"product_category": "makhana"}, "group_by": null, "operation": "top", "target": "trend_label"}\n'
        "Q: trends among senior citizens\n"
        'A: {"filters": {"consumer_demographic": "senior citizens"}, "group_by": null, "operation": "top", "target": "trend_label"}\n'
        "Q: top trends in kirana stores\n"
        'A: {"filters": {"store_type": "Kirana Store"}, "group_by": null, "operation": "top", "target": "trend_label"}\n'
        "Q: " + question + "\nA:"
    )

queries = [
    "trends for makhana", "what do teenagers buy", "top trends in kirana stores",
    "trends among senior citizens", "sugar free demand in winter",
    "spicy snacks in Hyderabad", "what sells during Diwali", "popcorn trends",
    "premium shoppers preferences", "trends in supermarkets",
]

for q in queries:
    print("="*70)
    print("Q:", q)
    try:
        r = requests.post(API_URL + "/generate",
                          json={"prompt": spec_prompt(q), "max_new_tokens": 160}, timeout=60)
        print("RAW:", r.json().get("text", "")[:300])
    except Exception as e:
        print("ERROR:", e)
