# app/metrics.py
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import math
import re
from statistics import mean

# ---------------------------
# Data model
# ---------------------------

@dataclass
class EffortMetrics:
    chars_typed: int
    time_spent_ms: int
    backspaces: int
    attempt_count: int
    hint_count: int
    final_request_count: int

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def _sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))

# ---------------------------
# Structure scoring
# ---------------------------

def structure_points(text: str) -> float:
    """
    Rewards attempts that show reasoning, steps, or multi-sentence structure.
    """
    if not text:
        return 0.0

    pts = 0.0

    # multiple sentences
    if len(re.split(r"[.!?]+", text)) >= 3:
        pts += 3

    # reasoning connectors
    if re.search(r"\b(because|so|therefore|thus|however|if|then|since)\b", text, re.I):
        pts += 3

    # steps/bullets/equations
    if re.search(r"(\n-|\n\d+\.|\bstep\b|=|->)", text, re.I):
        pts += 4

    return clamp(pts, 0, 10)

# ---------------------------
# Effort scoring
# ---------------------------

def compute_effort_score(user_text: str, m: EffortMetrics) -> Tuple[int, str, bool, List[str]]:
    reasons: List[str] = []

    # 1) Length (0–40): saturates after ~600 chars
    length_points = 40 * (1 - math.exp(-m.chars_typed / 250))
    if m.chars_typed >= 120:
        reasons.append("Good attempt length")

    # 2) Time (0–25): saturates after ~90s
    time_sec = m.time_spent_ms / 1000
    time_points = 25 * (1 - math.exp(-time_sec / 45))
    if time_sec >= 25:
        reasons.append("Time invested")

    # 3) Iteration (0–15): rewards repeated attempts, saturates
    iteration_points = 15 * (1 - math.exp(-(max(m.attempt_count, 1) - 1) / 2))
    if m.attempt_count >= 2:
        reasons.append("Iterated on attempt")

    # 4) Editing (0–10): healthy editing earns points
    bs = m.backspaces
    edit_points = 10 * _sigmoid((bs - 8) / 10)  # rises after ~8 backspaces
    edit_points = clamp(edit_points, 0, 10)
    if bs >= 8:
        reasons.append("Active editing")

    # 5) Structure (0–10)
    sp = structure_points(user_text)
    if sp >= 6:
        reasons.append("Reasoning structure detected")

    base = length_points + time_points + iteration_points + edit_points + sp

    # Penalties
    hint_penalty = min(20, 6 * m.hint_count)  # each hint ~6, cap 20
    if m.hint_count > 0:
        reasons.append("Hint penalty applied")

    final_early_penalty = 0
    if m.final_request_count > 0:
        low_effort_signal = (m.chars_typed < 80) or (time_sec < 15)
        final_early_penalty = 18 + (12 if low_effort_signal else 0) + min(5, 2 * m.final_request_count)
        reasons.append("Early FINAL request penalty")

    score = base - hint_penalty - final_early_penalty
    score = int(round(clamp(score, 0, 100)))

    # Anti-cheese cap: asked FINAL with almost no effort
    if (
        m.final_request_count > 0
        and (m.chars_typed < 120 and time_sec < 25 and m.attempt_count <= 1)
    ):
        score = min(score, 39)
        reasons.append("Anti-cheese cap applied")

    # State thresholds
    if score <= 29:
        state = "RAW"
    elif score <= 69:
        state = "SIZZLING"
    else:
        state = "COOKED"

    # Unlock rule: must be COOKED and not abusing hints/final
    unlocked = (score >= 70) and (m.final_request_count <= 1) and (m.hint_count <= 3)

    return score, state, unlocked, reasons

# ---------------------------
# Reliance index (0–1)
# ---------------------------

def reliance_index(m: EffortMetrics) -> float:
    hint = clamp(m.hint_count / 5, 0, 1)
    final = clamp(m.final_request_count / 3, 0, 1)
    attempts = clamp(1 - (min(m.attempt_count, 4) / 4), 0, 1)
    return round(0.45 * final + 0.35 * hint + 0.20 * attempts, 2)

# ---------------------------
# Skill tagging
# ---------------------------

TAG_RULES = {
    "Recall": [
        r"\bdefine\b", r"\bdefinition\b", r"\bwhat is\b", r"\bmeaning\b", r"\blist\b", r"\bremember\b"
    ],
    "Application": [
        r"\bsolve\b", r"\bcalculate\b", r"\bcompute\b", r"\buse (the )?formula\b", r"\bplug in\b",
        r"\bexample\b", r"\bimplement\b", r"\bcode\b"
    ],
    "Analysis": [
        r"\bbecause\b", r"\btherefore\b", r"\bwhy\b", r"\bcompare\b", r"\bdifference\b",
        r"\bif\b.*\bthen\b", r"\bbreak down\b"
    ],
    "Synthesis": [
        r"\bdesign\b", r"\bbuild\b", r"\bplan\b", r"\bpropose\b", r"\bcombine\b", r"\bcreate\b",
        r"\barchitecture\b", r"\broadmap\b"
    ],
    "Evaluation": [
        r"\bpros\b", r"\bcons\b", r"\btrade-?off\b", r"\bbest\b", r"\bjustify\b", r"\bargue\b",
        r"\bcritique\b", r"\bevaluate\b"
    ],
}

def skill_tags(user_text: str) -> List[str]:
    text = (user_text or "").lower()
    scores: Dict[str, int] = {k: 0 for k in TAG_RULES}

    for tag, patterns in TAG_RULES.items():
        for p in patterns:
            if re.search(p, text):
                scores[tag] += 1

    # heuristics
    if len(text) > 200 and scores["Analysis"] == 0:
        scores["Analysis"] += 1
    if re.search(r"=|\d", text) and scores["Application"] == 0:
        scores["Application"] += 1

    picked = [t for t, s in sorted(scores.items(), key=lambda x: x[1], reverse=True) if s > 0]
    return picked[:2] if picked else ["Recall"]

# ---------------------------
# Summary generator
# ---------------------------

def generate_summary(turns: List[dict]) -> dict:
    scores = [t["score"] for t in turns if "score" in t]
    hint_uses = sum(1 for t in turns if t.get("mode") == "HINT")
    finals = sum(1 for t in turns if t.get("mode") == "FINAL")
    unlock_turn = next((i + 1 for i, t in enumerate(turns) if t.get("unlocked")), None)

    tag_counts: Dict[str, int] = {}
    for t in turns:
        for tag in t.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    top_tags = [k for k, _ in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)][:3]

    out = {
        "turns_total": len(turns),
        "turns_to_unlock": unlock_turn,
        "hints_used": hint_uses,
        "final_requests": finals,
        "effort_avg": round(mean(scores), 1) if scores else 0,
        "effort_min": min(scores) if scores else 0,
        "effort_max": max(scores) if scores else 0,
        "top_skill_tags": top_tags or ["Recall"],
    }

    feedback: List[str] = []
    if hint_uses >= 4:
        feedback.append("Lots of hints used — try writing a short attempt before requesting hints.")
    if unlock_turn and unlock_turn <= 2:
        feedback.append("Fast unlock — next time, explain your reasoning to earn COOKED faster.")
    if out["effort_avg"] >= 70:
        feedback.append("Strong independence — your attempts show real thinking.")
    if not feedback:
        feedback.append("Solid progress — keep doing short attempts, then refine.")
    out["coach_feedback"] = feedback[:3]
    return out