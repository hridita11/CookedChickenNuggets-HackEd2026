export default function ModeBanner({ mode }) {
  return (
    <h2 style={{ textAlign: "center" }}>
      {mode === "RAW" && "brain AFK detected 🥶"}
      {mode === "SIZZLING" && "thinking.exe loading… 🔥"}
      {mode === "COOKED" && "FULLY COOKED — answer unlocked ✨"}
    </h2>
  );
}