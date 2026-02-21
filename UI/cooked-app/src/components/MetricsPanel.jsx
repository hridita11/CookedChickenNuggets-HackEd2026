export default function MetricsPanel({
  charsTyped,
  backspaces,
  timeSpent,
  attemptCount,
  hintCount
}) {
  return (
    <div style={{ marginTop: "20px" }}>
      <p>Chars: {charsTyped}</p>
      <p>Backspaces: {backspaces}</p>
      <p>Time Spent: {timeSpent} ms</p>
      <p>Attempts: {attemptCount}</p>
      <p>Hints: {hintCount}</p>
    </div>
  );
}