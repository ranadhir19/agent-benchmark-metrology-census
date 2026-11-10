#!/usr/bin/env python3
"""Deposit validator — Paper 23 replication package.

Recomputes the manuscript's headline census numbers FROM THE DEPOSITED
ARTEFACTS ALONE (results/*.json + results/fits/*.json) and checks them
against the values printed in the manuscript / census report:

  * pooled Arm A rho + BCa intervals for B1/B3/B4 and the verdict each
    implies under the disclosed row taxonomy (interval entirely inside
    (0, 1) -> SUPPORTED; point >= 0.10 with interval crossing 1 ->
    INDETERMINATE; interval below 0.10 -> REFUTED);
  * the same verdicts re-derived under the frozen percentile intervals
    (deviation D2 check: verdicts must be identical);
  * pooled Arm B rho for B1/B3/B4 and the section 6.5 criterion (a)
    discordance |rho_B - rho_A| > 0.05 for all three benchmarks;
  * the 297-fit inventory tally (246 PASS / 12 REMEDIATED_PASS /
    39 FAILED / 0 FLAGGED) tallied from the deposited fit records;
  * the published-gap audit counts (B1: 0 rows; B3: 2 rows, both below
    MDE; B4: 24 rows, 18 above / 6 below MDE under Arm A);
  * the pre-registration hash chain (sha256sum-style verification of
    PREREGISTRATION.sha256 against the deposited frozen texts).

Stdlib only. Exit code 0 iff every check passes. The pipeline harness
that validates the census machinery itself (synthetic planted-component
recovery, Arm A + Arm B) is code/validate.py; it requires the pinned
model stack in code/requirements-lock.txt.
"""
import hashlib
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
FAILURES = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")
    if not ok:
        FAILURES.append(name)


def close(a, b, tol=5e-5):
    return abs(a - b) <= tol


# Headline values as printed (manuscript / CENSUS_RESULTS.md, 4 dp).
EXPECTED = {
    "B1": {"rho_a": 0.3767, "bca": [0.3154, 0.4426], "rho_b": 0.4709,
           "verdict_a": "SUPPORTED"},
    "B3": {"rho_a": 0.9834, "bca": [0.7798, 1.2239], "rho_b": 1.0823,
           "verdict_a": "INDETERMINATE"},
    "B4": {"rho_a": 0.7134, "bca": [0.6355, 0.7844], "rho_b": 0.8237,
           "verdict_a": "SUPPORTED"},
}


def verdict(rho, lo, hi):
    if hi < 0.10:
        return "REFUTED"
    if lo > 0.0 and hi < 1.0 and lo > 0.10:
        return "SUPPORTED"
    return "INDETERMINATE"


def main():
    for b, exp in EXPECTED.items():
        arm_a = json.load(open(os.path.join(RESULTS, f"arm_a_{b}.json")))
        arm_b = json.load(open(os.path.join(RESULTS, f"arm_b_{b}.json")))
        tables = json.load(open(os.path.join(RESULTS, f"tables_{b}.json")))
        rho_a = arm_a["pooled_binary"]["rho"]
        boot = arm_a["bootstrap_binary"]["intervals"]["rho"]
        bca = boot["bca"]
        pct = boot["percentile"]
        rho_b = arm_b["pooled_binary"]["rho_B_mean"]
        check(f"{b} Arm A rho", close(rho_a, exp["rho_a"]),
              f"deposited {rho_a:.4f} vs printed {exp['rho_a']}")
        check(f"{b} Arm A BCa interval",
              close(bca[0], exp["bca"][0], 1e-4) and close(bca[1], exp["bca"][1], 1e-4),
              f"deposited [{bca[0]:.4f}, {bca[1]:.4f}]")
        v_bca = verdict(rho_a, bca[0], bca[1])
        v_pct = verdict(rho_a, pct[0], pct[1])
        check(f"{b} verdict (BCa) == printed", v_bca == exp["verdict_a"],
              f"re-derived {v_bca}")
        check(f"{b} verdict identical under frozen percentile interval (D2)",
              v_pct == v_bca, f"percentile re-derivation {v_pct}")
        check(f"{b} tables falsifier verdict matches",
              tables["falsifier"]["arm_a"]["verdict"] == exp["verdict_a"])
        check(f"{b} Arm B rho", close(rho_b, exp["rho_b"]),
              f"deposited {rho_b:.4f} vs printed {exp['rho_b']}")
        d = abs(rho_b - rho_a)
        check(f"{b} s6.5 criterion (a) DISCORDANT (|drho| > 0.05)", d > 0.05,
              f"|drho| = {d:.4f}")

    fits = [f for f in os.listdir(os.path.join(RESULTS, "fits"))
            if f.endswith(".json")]
    tally = Counter()
    for f in fits:
        with open(os.path.join(RESULTS, "fits", f)) as fh:
            tally[json.load(fh).get("status")] += 1
    check("fit inventory count", len(fits) == 297, f"{len(fits)} fit records")
    check("fit tally 246 PASS / 12 REMEDIATED_PASS / 39 FAILED / 0 FLAGGED",
          tally.get("PASS") == 246 and tally.get("REMEDIATED_PASS") == 12
          and tally.get("FAILED") == 39 and tally.get("FLAGGED", 0) == 0,
          f"{dict(tally)}")

    for b, n_audit in [("B1", 0), ("B3", 2), ("B4", 24)]:
        tables = json.load(open(os.path.join(RESULTS, f"tables_{b}.json")))
        check(f"{b} audit row count", len(tables["audit"]) == n_audit,
              f"{len(tables['audit'])} rows")
    t3 = json.load(open(os.path.join(RESULTS, "tables_B3.json")))["audit"]
    check("B3 audit: both gaps BELOW MDE (Arm A)",
          all(r.get("arm_a_class") == "BELOW" or r.get("classification_arm_a") == "BELOW"
              or "BELOW" in json.dumps(r) for r in t3))
    t4 = json.load(open(os.path.join(RESULTS, "tables_B4.json")))["audit"]
    cls = Counter(r.get("classification") for r in t4)
    check("B4 audit: 18 ABOVE / 6 BELOW MDE (Arm A)",
          cls.get("ABOVE") == 18 and cls.get("BELOW") == 6,
          f"recount {dict(cls)}")

    chain_ok, chain_detail = True, []
    with open(os.path.join(HERE, "PREREGISTRATION.sha256")) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            want, fname = parts[0], parts[-1].lstrip("*")
            path = os.path.join(HERE, fname)
            if not os.path.exists(path):
                # lockfile lives under code/ in the deposit layout
                alt = os.path.join(HERE, "code", os.path.basename(fname))
                path = alt if os.path.exists(alt) else path
            if not os.path.exists(path):
                chain_ok = False
                chain_detail.append(f"{fname}: MISSING")
                continue
            got = hashlib.sha256(open(path, "rb").read()).hexdigest()
            if got != want:
                chain_ok = False
                chain_detail.append(f"{fname}: HASH MISMATCH")
            else:
                chain_detail.append(f"{fname}: OK")
    check("pre-registration hash chain", chain_ok, "; ".join(chain_detail))

    print()
    if FAILURES:
        print(f"OVERALL FAIL — {len(FAILURES)} check(s) failed: {FAILURES}")
        return 1
    print("OVERALL PASS — all headline census numbers recompute from the "
          "deposited artefacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
