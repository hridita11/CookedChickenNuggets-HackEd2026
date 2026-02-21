export default function Meter({ charsTyped, mode }) {
  return (
    <div style={{textAlign:"center"}}>
    <p>The Effort Meter</p>
    <div style={{
      height: "20px",
      width: "100%",
      background: "#ddd",
      marginTop: "10px"
    }}>
      <div style={{
        height: "100%",
        width: `${Math.min(charsTyped, 100)}%`,
        background:
          mode === "RAW"
            ? "red"
            : mode === "SIZZLING"
            ? "orange"
            : "green",
        transition: "0.3s"
      }} />
    </div>
    </div>
  );
}