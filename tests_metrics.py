# app/tests_metrics.py
from .metrics import EffortMetrics, compute_effort_score, skill_tags, reliance_index, generate_summary

def simulate():
    cases = {
        "lazy_final_now": [
            ("give final answer", EffortMetrics(20, 4000, 0, 1, 0, 1)),
            ("pls", EffortMetrics(10, 2000, 0, 1, 0, 2)),
        ],
        "normal_student": [
            ("I think the answer is X because ...", EffortMetrics(180, 25000, 12, 1, 0, 0)),
            ("Wait maybe Y. Step 1... Step 2...", EffortMetrics(320, 55000, 25, 2, 1, 0)),
            ("Ok final? I feel confident now.", EffortMetrics(220, 30000, 10, 3, 1, 1)),
        ],
        "hint_spammer": [
            ("idk", EffortMetrics(30, 5000, 2, 1, 1, 0)),
            ("hint again", EffortMetrics(40, 6000, 3, 1, 2, 0)),
            ("final", EffortMetrics(50, 8000, 1, 1, 3, 1)),
            ("fine I try: because ...", EffortMetrics(220, 35000, 15, 2, 3, 1)),
        ]
    }

    for name, seq in cases.items():
        print("\n===", name, "===")
        turns = []
        for i, (text, met) in enumerate(seq, 1):
            score, state, unlocked, reasons = compute_effort_score(text, met)
            tags = skill_tags(text)
            ri = reliance_index(met)
            turns.append({"score": score, "state": state, "unlocked": unlocked, "mode": "SOCRATIC", "tags": tags})
            print(f"Turn {i}: score={score} state={state} unlocked={unlocked} tags={tags} RI={ri} reasons={reasons}")

        print("SUMMARY:", generate_summary(turns))

if __name__ == "__main__":
    simulate()