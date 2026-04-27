import React, { useState, useRef, useEffect } from 'react';
import { 
  SquareAsterisk, Layers, ShieldCheck, FileText, CheckSquare, 
  LayoutGrid, BarChart3, LockKeyhole, ArrowRight, ArrowLeft, Send
} from 'lucide-react';
import './index.css';

// --- Components ---
const Navbar = () => (
  <nav className="navbar fade-in">
    <div className="brand-brand">
      <SquareAsterisk size={28} />
      LegalAssistant
    </div>
    <div className="nav-links">
      <a href="#">Home</a>
      <a href="#">How it Works</a>
      <a href="#">Pricing</a>
      <a href="#">Law Firm</a>
    </div>
    <button className="btn-outline">Sign In</button>
  </nav>
);

const LandingPage = ({ onStart }) => {
  return (
    <div className="fade-in">
      <Navbar />

      {/* Hero */}
      <section className="hero">
        <h1 className="hero-title">
          The Best Legal Service for <span style={{color: 'var(--accent-color)'}}>Moroccan Labor Law 🇲🇦</span>
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem', marginBottom: '3rem', maxWidth: '600px', lineHeight: 1.6 }}>
          Navigate the complexity of the Moroccan Labor Code instantly with AI-driven synthesis designed exclusively for Moroccan professionals.
        </p>
        <button className="btn-primary" onClick={onStart}>
          Chat with our Assistant
        </button>

        {/* 3D Graphic Area */}
        <div className="hero-graphic" style={{ background: 'transparent', border: 'none', boxShadow: 'none', justifyContent: 'center' }}>
           <img src="/heyLAwyer.png" alt="3D Lawyer Avatar Talking" style={{ maxWidth: '100%', height: 'auto', maxHeight: '550px', filter: 'drop-shadow(0 20px 40px rgba(136,201,161,0.4))', animation: 'floating 4s ease-in-out infinite' }} />
        </div>
      </section>
    </div>
  );
};


// --- Chatbot Component ---
const ChatbotUI = ({ onBack }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: "Hello. I am the LegalAssistant for the Moroccan Labor Code. How can I assist you with your inquiry?"
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const query = inputValue;
    const newUserMsg = { id: Date.now(), role: 'user', content: query };
    setMessages((prev) => [...prev, newUserMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      
      let finalContent = data.response;

      setMessages((prev) => [
        ...prev,
        { id: Date.now(), role: 'assistant', content: finalContent }
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), role: 'assistant', content: "Erreur de connexion au serveur IA backend." }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container fade-in">
      <aside className="chat-sidebar">
        <div className="chat-sidebar-header">
          <div className="brand-brand" style={{ fontSize: '1rem' }}>
            <SquareAsterisk size={20} />
            LegalAssistant
          </div>
        </div>
        <div className="chat-sidebar-content">
          <div style={{ marginBottom: '2rem' }}>
            <button 
              onClick={onBack}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}
            >
              <ArrowLeft size={16} /> Return to Site
            </button>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
            This specialized RAG engine analyzes legal documentation to generate precise synthesis. Ensure validations are performed by certified legal practitioners.
          </p>
        </div>
      </aside>

      <main className="chat-main">
        <header className="chat-header">
           <div style={{ fontWeight: 500 }}>Active Session</div>
        </header>

        <div className="chat-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-wrapper ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'assistant' ? <SquareAsterisk size={18} /> : 'U'}
              </div>
              <div className="message-bubble" style={{ whiteSpace: 'pre-line', lineHeight: '1.6' }}>
                {msg.content.split(/(\*\*.*?\*\*)/g).map((part, index) => {
                  if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={index} style={{ color: 'var(--text-color)' }}>{part.slice(2, -2)}</strong>;
                  }
                  return part;
                })}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message-wrapper assistant">
              <div className="message-avatar">
                 <SquareAsterisk size={18} />
              </div>
              <div className="message-bubble" style={{ color: 'var(--text-muted)' }}>
                 Analyzing provisions...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <textarea
              className="chat-input"
              placeholder="Describe your legal inquiry..."
              rows={1}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <button 
              className="chat-send-btn" 
              onClick={handleSend}
              disabled={isLoading || !inputValue.trim()}
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  const [view, setView] = useState('landing');
  return view === 'landing' ? <LandingPage onStart={() => setView('chat')} /> : <ChatbotUI onBack={() => setView('landing')} />;
}
