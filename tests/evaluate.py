"""Run the labeled evaluation set and print accuracy numbers.

Usage (from the project root):  python -m tests.evaluate
"""
from backend.ingestion.normalizer import normalize_report
from backend.intelligence.fusion import process_event, reset_state
from tests.eval_reports import EVAL_REPORTS

TIERS = ["Info", "Low", "Moderate", "High", "Critical"]


def tier_of(p: int) -> str:
    if p >= 80:
        return "Critical"
    if p >= 60:
        return "High"
    if p >= 40:
        return "Moderate"
    if p >= 20:
        return "Low"
    return "Info"


def run(reports=EVAL_REPORTS, verbose: bool = True):
    rows = []
    for i, (src, text, exp_type, exp_tier, exp_inj) in enumerate(reports):
        reset_state()
        inc = process_event(normalize_report({
            "source_id": f"eval_{i}", "source_type": src, "raw_text": text,
            "lat": 33.5, "lng": -101.8,
        }))
        pf = inc.events[0].parsed_fields
        rows.append(dict(
            i=i, text=text, exp_type=exp_type, got_type=inc.incident_type,
            exp_tier=exp_tier, got_tier=tier_of(inc.priority), priority=inc.priority,
            exp_inj=exp_inj, got_inj=pf.injuries,
        ))

    n = len(rows)
    dist = lambda r: TIERS.index(r["got_tier"]) - TIERS.index(r["exp_tier"])
    type_ok = sum(r["exp_type"] == r["got_type"] for r in rows)
    in_scope = [r for r in rows if r["exp_type"] is not None]
    in_scope_ok = sum(r["exp_type"] == r["got_type"] for r in in_scope)
    tier_exact = sum(dist(r) == 0 for r in rows)
    tier_within1 = sum(abs(dist(r)) <= 1 for r in rows)
    under = sum(dist(r) <= -2 for r in rows)
    over = sum(dist(r) >= 2 for r in rows)
    inj = [r for r in rows if r["exp_inj"] is not None]
    inj_ok = sum(r["exp_inj"] == r["got_inj"] for r in inj)

    print(f"Reports evaluated: {n}")
    print(f"Incident type accuracy (all):       {type_ok}/{n} = {type_ok / n:.0%}")
    print(f"Incident type accuracy (in-scope):  {in_scope_ok}/{len(in_scope)} = {in_scope_ok / len(in_scope):.0%}")
    print(f"Priority tier exact match:          {tier_exact}/{n} = {tier_exact / n:.0%}")
    print(f"Priority tier within one tier:      {tier_within1}/{n} = {tier_within1 / n:.0%}")
    print(f"Under-prioritized by 2+ tiers:      {under}/{n}")
    print(f"Over-prioritized by 2+ tiers:       {over}/{n}")
    print(f"Injury count accuracy (labeled):    {inj_ok}/{len(inj)} = {inj_ok / len(inj):.0%}")

    if verbose:
        print("\nMisses:")
        for r in rows:
            bad = []
            if r["exp_type"] != r["got_type"]:
                bad.append(f"type {r['got_type']} (want {r['exp_type']})")
            if abs(dist(r)) > 1:
                bad.append(f"tier {r['got_tier']}/{r['priority']} (want {r['exp_tier']})")
            if r["exp_inj"] is not None and r["exp_inj"] != r["got_inj"]:
                bad.append(f"injuries {r['got_inj']} (want {r['exp_inj']})")
            if bad:
                print(f" #{r['i']}: {'; '.join(bad)} :: {r['text'][:70]}")
    return rows


if __name__ == "__main__":
    import sys

    if "--heldout" in sys.argv:
        from tests.eval_heldout import HELDOUT_REPORTS

        run(HELDOUT_REPORTS)
    else:
        run()
