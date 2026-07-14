import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  // Authentication States
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState("");
  const [usernameInput, setUsernameInput] = useState("");
  const [passwordInput, setPasswordInput] = useState("");
  const [authMode, setAuthMode] = useState("LOGIN"); // LOGIN or REGISTER
  const [authMessage, setAuthMessage] = useState({ text: "", isError: false });

  // Chat States
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [currentMetrics, setCurrentMetrics] = useState({ sentiment: "N/A", lastTicket: "None" });

  // Fetch Chat History upon successful login
  useEffect(() => {
    if (isLoggedIn && currentUser) {
      axios.get(`http://127.0.0.1:8000/api/chat/history/${currentUser}`)
        .then(res => setMessages(res.data))
        .catch(err => console.error("History fetch error:", err));
    }
  }, [isLoggedIn, currentUser]);

  // Auth Handler for Login & Registration
  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthMessage({ text: "", isError: false });

    if (!usernameInput.trim() || !passwordInput.trim()) {
      setAuthMessage({ text: "Please fill all fields!", isError: true });
      return;
    }

    const endpoint = authMode === "LOGIN" ? "login" : "register";
    try {
      const res = await axios.post(`http://127.0.0.1:8000/api/auth/${endpoint}`, {
        username: usernameInput,
        password: passwordInput
      });

      if (authMode === "LOGIN") {
        setCurrentUser(res.data.username);
        setIsLoggedIn(true);
      } else {
        setAuthMessage({ text: "Registration successful! Now please login.", isError: false });
        setAuthMode("LOGIN");
        setPasswordInput("");
      }
    } catch (err) {
      const errMsg = err.response?.data?.detail || "Connection to backend failed!";
      setAuthMessage({ text: errMsg, isError: true });
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setIsTyping(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/api/chat", { 
        username: currentUser,
        message: currentInput 
      });
      
      const botMessage = { 
        text: res.data.response, 
        sender: 'bot', 
        intents: res.data.intents,
        sentiment: res.data.sentiment
      };
      setMessages((prev) => [...prev, botMessage]);
      setCurrentMetrics({
        sentiment: res.data.sentiment,
        lastTicket: res.data.ticket_id || currentMetrics.lastTicket
      });

    } catch (err) {
      setMessages((prev) => [...prev, { text: "Failed to connect to backend engine.", sender: 'bot' }]);
    } finally {
      setIsTyping(false);
    }
  };

  // 🔒 SCREEN 1: LOGIN / PASSWORD INTERFACE
  if (!isLoggedIn) {
    return (
      <div style={{ maxWidth: '400px', margin: '100px auto', padding: '30px', border: '1px solid #ddd', borderRadius: '12px', boxShadow: '0 4px 15px rgba(0,0,0,0.1)', fontFamily: 'Segoe UI, sans-serif' }}>
        <h2 style={{ textAlign: 'center', color: '#2c3e50', marginBottom: '5px' }}>🛒 TechMart Portal</h2>
        <p style={{ textAlign: 'center', color: '#7f8c8d', fontSize: '14px', marginTop: 0 }}>
          {authMode === "LOGIN" ? "Sign in to access AI Support Agents" : "Create a new customer account"}
        </p>
        
        {authMessage.text && (
          <div style={{ color: authMessage.isError ? '#721c24' : '#155724', backgroundColor: authMessage.isError ? '#f8d7da' : '#d4edda', padding: '10px', borderRadius: '6px', marginBottom: '15px', textAlign: 'center', fontSize: '14px', fontWeight: 'bold' }}>
            {authMessage.text}
          </div>
        )}

        <form onSubmit={handleAuthSubmit}>
          <input type="text" placeholder="Username" value={usernameInput} onChange={(e) => setUsernameInput(e.target.value)} style={{ width: '93%', padding: '12px', marginBottom: '15px', borderRadius: '6px', border: '1px solid #ccc', fontSize: '14px' }} />
          <input type="password" placeholder="Password" value={passwordInput} onChange={(e) => setPasswordInput(e.target.value)} style={{ width: '93%', padding: '12px', marginBottom: '20px', borderRadius: '6px', border: '1px solid #ccc', fontSize: '14px' }} />
          <button type="submit" style={{ width: '100%', padding: '12px', backgroundColor: '#2c3e50', color: 'white', border: 'none', borderRadius: '6px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer' }}>
            {authMode === "LOGIN" ? "Sign In" : "Register Account"}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '20px', color: '#3498db', cursor: 'pointer', fontSize: '14px' }} onClick={() => { setAuthMode(authMode === "LOGIN" ? "REGISTER" : "LOGIN"); setAuthMessage({text:"", isError:false}); }}>
          {authMode === "LOGIN" ? "New user? Create an account here" : "Already have an account? Login here"}
        </p>
      </div>
    );
  }

  // 💬 SCREEN 2: MAIN MULTI-AGENT CHAT INTERFACE
  return (
    <div style={{ display: 'flex', maxWidth: '1100px', margin: '40px auto', gap: '20px', fontFamily: 'Segoe UI, sans-serif' }}>
      {/* Analytics Sidebar */}
      <div style={{ width: '30%', border: '1px solid #ddd', borderRadius: '12px', padding: '20px', backgroundColor: '#f8f9fa', height: 'fit-content' }}>
        <h3 style={{ marginTop: 0, color: '#2c3e50' }}>👤 Customer: {currentUser}</h3>
        <button onClick={() => { setIsLoggedIn(false); setCurrentUser(""); setUsernameInput(""); setPasswordInput(""); }} style={{ padding: '6px 12px', backgroundColor: '#e74c3c', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' }}>Logout</button>
        <hr style={{ margin: '15px 0', border: '0.5px solid #eee' }}/>
        <div style={{ margin: '15px 0' }}><strong>Sentiment Status:</strong> <span style={{ marginLeft: '5px', padding: '3px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold', background: currentMetrics.sentiment === 'ANGRY' ? '#f8d7da' : '#d4edda', color: currentMetrics.sentiment === 'ANGRY' ? '#721c24' : '#155724' }}>{currentMetrics.sentiment}</span></div>
        <div style={{ margin: '15px 0' }}><strong>Escalation Ticket:</strong> <br/><span style={{ fontFamily: 'monospace', color: '#e74c3c', fontWeight: 'bold', fontSize: '14px' }}>{currentMetrics.lastTicket}</span></div>
      </div>

      {/* Chat Windows */}
      <div style={{ width: '70%' }}>
        <div style={{ border: '1px solid #ddd', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 15px rgba(0,0,0,0.05)' }}>
          <div style={{ background: '#2c3e50', color: '#fff', padding: '15px', textAlign: 'center' }}>
            <h2 style={{ margin: 0, fontSize: '20px' }}>🛒 TechMart Enterprise Multi-Agent Center</h2>
          </div>

          <div style={{ height: '450px', overflowY: 'auto', padding: '20px', backgroundColor: '#fff' }}>
            {messages.map((msg, i) => (
              <div key={i} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left', margin: '15px 0' }}>
                <div style={{ 
                  background: msg.sender === 'user' ? '#3498db' : '#f1f2f6', color: msg.sender === 'user' ? '#fff' : '#2c3e50', 
                  padding: '12px 18px', borderRadius: msg.sender === 'user' ? '15px 15px 0 15px' : '15px 15px 15px 0',
                  display: 'inline-block', maxWidth: '80%', textAlign: 'left'
                }}>
                  <span style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</span>
                  {msg.intents && <div style={{ fontSize: '10px', color: msg.sender === 'user' ? '#e0f2fe' : '#7f8c8d', marginTop: '5px' }}>🤖 Routed to: {msg.intents.join(', ')}</div>}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div style={{ textAlign: 'left', margin: '15px 0' }}>
                <div style={{ background: '#f1f2f6', color: '#7f8c8d', padding: '10px 15px', borderRadius: '15px', display: 'inline-block', fontStyle: 'italic' }}>
                  ⚙️ TechMart Agents are reviewing context...
                </div>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', padding: '15px', background: '#f8f9fa', borderTop: '1px solid #ddd', gap: '10px' }}>
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && sendMessage()} style={{ flexGrow: 1, padding: '12px', borderRadius: '8px', border: '1px solid #ccc' }} placeholder="Type your support request here..." />
            <button onClick={sendMessage} style={{ padding: '12px 25px', backgroundColor: '#2c3e50', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>Send</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;