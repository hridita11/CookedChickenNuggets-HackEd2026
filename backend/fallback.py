# backend/fallback.py
def socratic_fallback(task_type: str) -> str:
    if task_type == "math":
        return "Let’s start with Step 1: what method fits (substitution, parts, simplification)? Write your first move."
    if task_type == "writing":
        return "Before I write anything: what’s your thesis in ONE sentence? Then give one example you’ll use."
    return "Which part is confusing: definition, steps, or example? Try explaining it in your own words first."

def hint_fallback(task_type: str) -> str:
    if task_type == "math":
        return "Hint: look for a pattern where a derivative is ‘nearby’. If it’s a product like x·e^x, think integration by parts."
    if task_type == "writing":
        return "Hint: structure: Hook → Context → Thesis. Draft a thesis first; we’ll polish it."
    return "Hint: split into 2 key ideas and give 1 example for each."

def final_locked_msg() -> str:
    return "Final is locked — show any attempt (even messy). Once you try Step 1, I can unlock the full answer."

def reflection_fallback() -> str:
    return "Reflection: (1) What was the key step? (2) What will you try first next time? (3) What mistake will you avoid?"
