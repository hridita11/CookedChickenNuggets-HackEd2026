from fastapi import FastAPI
from pydantic import BaseModel, Field
from llm_client import ask_gemini
from prompts import socratic_prompt, hint_prompt, final_prompt, reflection_prompt
from typing import Literal, Optional, Dict, Any, List

from session_store import store, Session, Message
from task_detect import detect_task_type

from metrics import (
    EffortMetrics,
    compute_effort_score,
    skill_tags,
    generate_summary,
)

Mode = Literal["SOCRATIC", "HINT", "FINAL", "REFLECTION", "SUMMARY"]

app = FastAPI()

@app.get("/")
def home():
    return {"message": "COOKED backend running 🍗🧠"}

class MetricsIn(BaseModel):
    chars_typed: int = 0
    time_spent_ms: int = 0
    backspaces: int = 0
    attempt_count: int = 0
    hint_count: int = 0
    final_request_count: int = 0

class ChatRequest(BaseModel):
    session_id: str
    mode: Mode = "SOCRATIC"
    user_text: str
    metrics: MetricsIn = Field(default_factory=MetricsIn)

class ChatResponse(BaseModel):
    assistant_text: str
    score: int
    state: Literal["RAW","SIZZLING","COOKED"]
    unlocked: bool
    reasons: List[str]
    tags: List[str]
    task_type: Literal["math","writing","explain"]
    banner: str
    summary: Optional[Dict[str, Any]] = None

def banner_from_state(state: str, unlocked: bool) -> str:
    if unlocked:
        return "FULLY COOKED — answer unlocked ✨"
    if state == "RAW":
        return "brain AFK detected 🥶"
    return "thinking.exe loading… 🔥"

def socratic_fallback(task_type: str) -> str:
    if task_type == "math":
        return "Let’s start with Step 1: what method seems right (substitution, parts, simplification)? Write your first move."
    if task_type == "writing":
        return "Before I write anything: what’s your thesis in ONE sentence? Then give one example you’ll use."
    return "Which part is confusing: definition, steps, or example? Try explaining it in your own words first."

def hint_fallback(task_type: str) -> str:
    if task_type == "math":
        return "Hint: look for a pattern where something’s derivative is nearby. Try a substitution or integration by parts if you see x·e^x-style products."
    if task_type == "writing":
        return "Hint: structure it as Hook → Context → Thesis. Start with a thesis draft and I’ll help refine it."
    return "Hint: split into 2 key ideas and give 1 real example for each."

def final_locked_msg() -> str:
    return "Final is locked 🔒 — show any attempt (even messy). Once you try Step 1, I can unlock the full answer."

def reflection_fallback() -> str:
    return "Reflection: (1) What was the key step? (2) What would you try first next time? (3) What mistake will you avoid?"

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    s: Session = store.get(req.session_id)

    # set task type once per session
    if s.task_type is None:
        s.task_type = detect_task_type(req.user_text)
    task_type = s.task_type

    # update question history
    s.question_history.append(req.user_text)

    # convert request metrics -> EffortMetrics (dataclass from your metrics.py)
    m = EffortMetrics(
        chars_typed=req.metrics.chars_typed,
        time_spent_ms=req.metrics.time_spent_ms,
        backspaces=req.metrics.backspaces,
        attempt_count=req.metrics.attempt_count,
        hint_count=req.metrics.hint_count,
        final_request_count=req.metrics.final_request_count,
    )

    # compute effort score using your function
    score, state, unlocked_now, reasons = compute_effort_score(req.user_text, m)

    # update session unlock state
    if unlocked_now:
        s.final_unlocked = True

    # compute tags
    tags = skill_tags(req.user_text)

    # append chat history
    s.history.append(Message(role="user", content=req.user_text))

    # enforce FINAL lock
    effective_mode: Mode = req.mode
    locked = False
    if req.mode == "FINAL" and not s.final_unlocked:
        effective_mode = "SOCRATIC"
        locked = True

    # LLM assistant response
    assistant_text = None

    if effective_mode == "SOCRATIC":
        assistant_text = ask_gemini(socratic_prompt(task_type), req.user_text)
        if assistant_text is None:
            assistant_text = final_locked_msg() if locked else socratic_fallback(task_type)

    elif effective_mode == "HINT":
        assistant_text = ask_gemini(hint_prompt(task_type), req.user_text)
        if assistant_text is None:
            assistant_text = hint_fallback(task_type)

    elif effective_mode == "FINAL":
        assistant_text = ask_gemini(final_prompt(task_type), req.user_text)
        if assistant_text is None:
            assistant_text = "Final answer unlocked, but AI unavailable. (Fallback active)"

    elif effective_mode == "REFLECTION":
        assistant_text = ask_gemini(reflection_prompt(task_type), req.user_text)
        if assistant_text is None:
            assistant_text = reflection_fallback()

    else:  # SUMMARY
        assistant_text = "Here’s your Summary, you may not be cooked after all."


    # log this turn (for summary generator)
    s.turns.append({
        "mode": req.mode,
        "score": score,
        "unlocked": s.final_unlocked,
        "tags": tags,
    })

    summary_payload = generate_summary(s.turns) if req.mode == "SUMMARY" else None

    return ChatResponse(
        assistant_text=assistant_text,
        score=score,
        state=state,   # RAW/SIZZLING/COOKED
        unlocked=s.final_unlocked,
        reasons=reasons,
        tags=tags,
        task_type=task_type,  # math/writing/explain
        banner=banner_from_state(state, s.final_unlocked),
        summary=summary_payload
    )
