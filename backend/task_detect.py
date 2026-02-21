MATH = ["integral","derivative","solve","simplify","limit","proof","equation","matrix","vector","probability","statistics"]
WRITING = ["essay","thesis","introduction","conclusion","paragraph","outline","citation","argument","rewrite","rephrase"]
EXPLAIN = ["explain","define","summarize","difference","how","why","what is"]

def detect_task_type(text: str) -> str:
    t = (text or "").lower()
    mh = sum(k in t for k in MATH)
    wh = sum(k in t for k in WRITING)
    eh = sum(k in t for k in EXPLAIN)

    if mh >= wh and mh >= eh and mh > 0:
        return "math"
    if wh >= mh and wh >= eh and wh > 0:
        return "writing"
    return "explain"
