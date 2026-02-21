from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

Role = Literal["user", "assistant"]

@dataclass
class Message:
    role: Role
    content: str

@dataclass
class Session:
    session_id: str
    history: List[Message] = field(default_factory=list)
    turns: List[dict] = field(default_factory=list)   # for generate_summary()
    question_history: List[str] = field(default_factory=list)
    final_unlocked: bool = False
    task_type: Optional[str] = None

class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def get(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            self.sessions[session_id] = Session(session_id=session_id)
        return self.sessions[session_id]

store = SessionStore()
