import { useState } from "react";
import Header from "./components/Header";
import Meter from "./components/Meter";


function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  //const modeHelp = "RAW";
  const [mode,setMode]=useState("");


  const sendMessage = () => {
    if (!input.trim()) return;

    setMessages([...messages, { role: "user", content: input }]);
    setInput("");
    changeMode();
  };

  const changeMode=()=>{
    if(input=="cooked"){
      setMode("COOKED");    
    }else if(input=="sizzling"){
      setMode("SIZZLING");
    }else setMode("RAW");
  }

  return (
    <div style={{ padding: "20px" }}>
      <Header/>

      <div style={{ minHeight: "300px", border: "1px solid #ccc", padding: "10px" }}>
        {messages.map((msg, index) => (
          <p key={index}>
            <strong>{msg.role}:</strong> {msg.content}
          </p>
        ))}
      </div>

      <Meter mode={mode}></Meter>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default App;