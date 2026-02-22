import { useEffect, useMemo, useRef, useState } from "react";
import Header from "./components/Header";
import Meter from "./components/Meter";

const API_BASE = "http://127.0.0.1:8000";

function getSessionId() {
  let id = localStorage.getItem("cooked_session_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("cooked_session_id", id);
  }
  return id;
}

function App() {
  const sessionId = useMemo(() => getSessionId(), []);

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // mode = RAW / SIZZLING / COOKED (driven by backend)
  const [mode, setMode] = useState("RAW");

  // store latest backend response so you can display score/tags/etc.
  const [lastResult, setLastResult] = useState(null);

  // ---- basic metrics tracking (minimal MVP) ----
  const typingStartRef = useRef(null);
  const backspacesRef = useRef(0);
  const attemptCountRef = useRef(0);
  const hintCountRef = useRef(0);
  const finalCountRef = useRef(0);

  const onChangeInput = (e) => {
    const next = e.target.value;

    if (typingStartRef.current === null) typingStartRef.current = performance.now();
    if (next.length < input.length) backspacesRef.current += 1;

    setInput(next);
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text) return;

    // count this as an attempt
    attemptCountRef.current += 1;

    const now = performance.now();
    const timeSpentMs =
      typingStartRef.current === null ? 0 : Math.max(0, Math.round(now - typingStartRef.current));

    const payload = {
      session_id: sessionId,
      mode: "SOCRATIC", // keep simple for now; you can add a dropdown later
      user_text: text,
      metrics: {
        chars_typed: text.length,
        time_spent_ms: timeSpentMs,
        backspaces: backspacesRef.current,
        attempt_count: attemptCountRef.current,
        hint_count: hintCountRef.current,
        final_request_count: finalCountRef.current,
      },
    };

    // show the user message immediately
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      // this is where your Vidhi work shows up
      setLastResult(data);
      setMode(data.state); // RAW / SIZZLING / COOKED

      // append assistant reply
      setMessages((prev) => [...prev, { role: "assistant", content: data.assistant_text }]);

      // optional: store history for analytics later
      const prevHistory = JSON.parse(localStorage.getItem("cooked_history") || "[]");
      prevHistory.push({
        text,
        timestamp: Date.now(),
        effort: data.score,
        state: data.state,
        tags: data.tags,
      });
      localStorage.setItem("cooked_history", JSON.stringify(prevHistory));

      // reset per-turn typing metrics
      typingStartRef.current = null;
      backspacesRef.current = 0;
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Could not reach backend. Is FastAPI running on :8000? (Check console/CORS)" },
      ]);
    }
  };


  return (
    <div style={{ padding: "20px" }}>
      <Header />

      {/* ✅ YOUR WORK VISIBLE HERE */}
      <div style={{ margin: "12px 0", padding: "10px", border: "3px solid #ffffff55" }}>
        <div><strong>Banner:</strong> {lastResult?.banner ?? "—"}</div>
        <div><strong>Score:</strong> {lastResult?.score ?? 0} / 100</div>
        <div>
          <strong>State:</strong> {lastResult?.state ?? "—"} {lastResult?.unlocked ? "✅ unlocked" : "🔒 locked"}
        </div>
        <div><strong>Tags:</strong> {lastResult?.tags ? lastResult.tags.join(", ") : "—"}</div>
        <div><strong>Reasons:</strong> {lastResult?.reasons ? lastResult.reasons.join(" • ") : "—"}</div>
      </div>

      <div class="chat-container" style={{ minHeight: "300px", border: "5px solid #e4d3bb", padding: "10px" }}>
        {messages.map((msg, index) => (
          <p key={index}>
            <strong>{msg.role}:</strong> {msg.content}
          </p>
        ))}
      </div>

      {/* Meter now uses backend-driven mode */}
      <Meter mode={mode} score={lastResult?.score ?? 0} />

      <input style={{color:"#96541e", background:"white"}}value={input} onChange={onChangeInput} />
      <button onClick={sendMessage}>Send</button>

    </div>
  );
}

export default App;