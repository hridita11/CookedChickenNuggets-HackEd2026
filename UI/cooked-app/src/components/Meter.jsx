export default function Meter({ score = 0, mode }) {
  const pct = Math.max(0, Math.min(100, score));

  return (
    <div style={{ textAlign: "center" }}>
      <p>The Effort Meter</p>

      <div
        style={{
          height: "20px",
          width: "100%",
          background: "#ddd",
          marginTop: "10px",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${pct}%`,
            background:
              mode === "RAW" ? "red" : mode === "SIZZLING" ? "orange" : "green",
            transition: "0.3s",
          }}
        />
      </div>

      <p style={{ marginTop: 8 }}>
        {mode} — {pct}/100
      </p>
    </div>
  );
}