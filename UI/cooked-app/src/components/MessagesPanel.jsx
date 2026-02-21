export default function MessagesPanel({ messages }) {
  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: "15px",
        minHeight: "200px",
        marginTop: "20px",
        background: "#fafafa"
      }}
    >
      {messages.length === 0 && <p>No attempts yet.</p>}

      {messages.map((msg, index) => (
        <div
          key={index}
          style={{
            marginBottom: "10px",
            padding: "8px",
            borderRadius: "6px",
            background:
              msg.role === "user" ? "#dbeafe" : "#fcd34d"
          }}
        >
          <strong>{msg.role}:</strong> {msg.content}
        </div>
      ))}
    </div>
  );
}