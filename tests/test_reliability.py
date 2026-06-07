"""
tests/test_reliability.py
Consumer Trend Extraction - reliability test.

Protocol from the brief:
  1. Pick 10 retailer feedback questions.
  2. Ask each question, record the answer.
  3. Ask the same questions again in a randomized order - answers MUST match.
  4. Inject 2 out-of-distribution probes between repeats.

Run against a running FastAPI server:
    python tests/test_reliability.py --api http://localhost:8000

Exit code 0 = reliability passed.
"""

from __future__ import annotations

import argparse
import random
import sys
import time

import requests

BASELINE = [
    "College boys near hostel asking for the highest spice level available. Regular not enough.",
    "Kids increasingly asking for cheesy dip flavours. Retailer says he could sell 5 packs a day.",
    "Rs.5 and Rs.10 packs are flying off the shelves. Anything above Rs.20 sits for weeks.",
    "Diabetic customers walking in asking specifically for sugar-free biscuits this week.",
    "Two customers asked for protein bars at the counter today. New thing for this area.",
    "Diwali approaching, retailer asking for premium gift packs in fancy boxes.",
    "Youngsters keep ordering chips online - owner says he loses sale to quick-commerce.",
    "Customers asking for ragi and millet-based snacks. Health awareness has gone up.",
    "Mango pickle flavour chips - three customers asked today. Tangy stuff is moving fast.",
    "Plant-based curd snacks getting weekly queries from gym-going customers.",
]

PROBES = [
    "Weather is good today, retailer was happy.",
    "New shop opened across the street, lots of activity.",
]


def call(api, text):
    r = requests.post(
        f"{api}/predict",
        json={"retailer_feedback": text},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def primary(resp):
    return resp["primary_trend"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://localhost:8000")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)  # NOSONAR - non-crypto random is fine for test question shuffling

    print("=" * 72)
    print("PASS 1 - baseline (10 questions in order)")
    print("=" * 72)
    pass1 = {}
    for i, q in enumerate(BASELINE):
        t0 = time.time()
        resp = call(args.api, q)
        dt = (time.time() - t0) * 1000
        pass1[i] = resp
        print("  Q%-2d [%6.0f ms]  ->  %s  (%.3f)" % (i+1, dt, primary(resp), resp["primary_confidence"]))

    print()
    print("Injecting 2 out-of-distribution probes...")
    for p in PROBES:
        resp = call(args.api, p)
        print("  probe -> %s  (%.3f)" % (primary(resp), resp["primary_confidence"]))

    print()
    print("=" * 72)
    print("PASS 2 - same 10 questions, shuffled order")
    print("=" * 72)
    order = list(range(len(BASELINE)))
    rng.shuffle(order)
    pass2 = {}
    for idx in order:
        resp = call(args.api, BASELINE[idx])
        pass2[idx] = resp
        print("  Q%-2d            ->  %s  (%.3f)" % (idx+1, primary(resp), resp["primary_confidence"]))

    print()
    print("=" * 72)
    print("RELIABILITY REPORT")
    print("=" * 72)
    mismatches = []
    for i in range(len(BASELINE)):
        a = primary(pass1[i])
        b = primary(pass2[i])
        ca = pass1[i]["primary_confidence"]
        cb = pass2[i]["primary_confidence"]
        match = "PASS" if a == b else "FAIL"
        print("  [%s] Q%-2d  pass1=%s (%.3f)  pass2=%s (%.3f)" % (match, i+1, a, ca, b, cb))
        if a != b:
            mismatches.append((i + 1, a, b))

    print()
    if not mismatches:
        print("RELIABILITY PASSED - all %d/%d responses identical." % (len(BASELINE), len(BASELINE)))
        sys.exit(0)
    else:
        print("RELIABILITY FAILED - %d/%d differed:" % (len(mismatches), len(BASELINE)))
        for q, a, b in mismatches:
            print("     Q%d:  %s  !=  %s" % (q, a, b))
        sys.exit(1)


if __name__ == "__main__":
    main()
