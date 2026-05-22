import React, { useState, useRef, useEffect, createContext, useContext } from 'react';
import {
  Scale,
  ArrowRight,
  Send,
  BookOpen,
  Landmark,
  FileSearch,
  Home,
  User,
  ChevronLeft,
  ExternalLink,
  Globe,
} from 'lucide-react';
import './index.css';
import { T } from './translations';

const LangContext = createContext();

const SITE_LOGO = '/Group-1511-1.svg';

/** روابط رسمية معروفة — تفتح في تبويب جديد */
const LINK_MAHAKIM = 'https://www.mahakim.ma/';
const LINK_JUSTICE_MIN = 'https://www.justice.gov.ma/';

function scrollToId(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function isMostlyArabic(text) {
  if (!text || !text.trim()) return false;
  const ar = (text.match(/[\u0600-\u06FF]/g) || []).length;
  const lat = (text.match(/[A-Za-zÀ-ÿ]/g) || []).length;
  return ar >= 3 && ar >= lat;
}

function renderBoldInline(text) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

function isListBlock(text) {
  const lines = text.split('\n').filter((l) => l.trim());
  return lines.length > 0 && lines.every((l) => /^\s*-\s/.test(l));
}

function renderListBlock(text) {
  const lines = text.split('\n').filter((l) => l.trim());
  return (
    <ul className="msg-list">
      {lines.map((l, li) => (
        <li key={li}>{renderBoldInline(l.replace(/^\s*-\s*/, ''))}</li>
      ))}
    </ul>
  );
}

function renderArabicParagraph(bodyText) {
  const lines = bodyText.split('\n');
  return lines.map((line, i) => (
    <React.Fragment key={i}>
      {i > 0 && <br />}
      {renderBoldInline(line)}
    </React.Fragment>
  ));
}

function renderArabicBlock(block, index) {
  const trimmed = block.trim();
  if (!trimmed) return null;
  if (isListBlock(trimmed)) {
    return (
      <div key={index} className="msg-block">
        {renderListBlock(trimmed)}
      </div>
    );
  }
  const lines = trimmed.split('\n');
  const first = lines[0];
  const sectionMatch = first.match(/^(\s*\*\*[^*]+\*\*)(.*)$/);
  if (sectionMatch) {
    const rawTitle = sectionMatch[1].slice(2, -2);
    const tail = sectionMatch[2].trim();
    const bodyText = [tail, ...lines.slice(1)].join('\n').trim();
    return (
      <div key={index} className="msg-block">
        <span className="msg-section-title">{rawTitle}</span>
        {bodyText &&
          (isListBlock(bodyText) ? (
            renderListBlock(bodyText)
          ) : (
            <div className="msg-section-body">{renderArabicParagraph(bodyText)}</div>
          ))}
      </div>
    );
  }
  return (
    <div key={index} className="msg-block">
      {renderArabicParagraph(trimmed)}
    </div>
  );
}

function MessageBody({ content }) {
  const arabic = isMostlyArabic(content);
  if (!arabic) {
    return (
      <>
        {content.split(/(\*\*.*?\*\*)/g).map((part, index) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={index}>{part.slice(2, -2)}</strong>;
          }
          return part;
        })}
      </>
    );
  }
  const blocks = content.trim().split(/\n\n+/);
  return (
    <div className="msg-formatted" lang="ar">
      {blocks.map((b, i) => renderArabicBlock(b, i))}
    </div>
  );
}

function PortalNavWithHome({ compact }) {
  const { t } = useContext(LangContext);
  if (compact) return null;
  return (
    <nav className="portal-nav" aria-label="التنقل الرئيسي">
      <div className="portal-nav-inner">
        <a href="#accueil" className="portal-nav-home" title={t.home} aria-label={t.home}>
          <Home size={20} aria-hidden />
        </a>
        <a href="#accueil">{t.home}</a>
        <a href={LINK_MAHAKIM} target="_blank" rel="noopener noreferrer">
          {t.track} <ExternalLink size={11} style={{ opacity: 0.85 }} aria-hidden />
        </a>
        <a href={LINK_JUSTICE_MIN} target="_blank" rel="noopener noreferrer">
          {t.criminal} <ExternalLink size={11} style={{ opacity: 0.85 }} aria-hidden />
        </a>
        <a href="#guide">{t.guide}</a>
        <a href={LINK_JUSTICE_MIN} target="_blank" rel="noopener noreferrer">
          {t.contact} <ExternalLink size={11} style={{ opacity: 0.85 }} aria-hidden />
        </a>
      </div>
    </nav>
  );
}

function PortalHeader({ compact }) {
  const { t, lang, setLang } = useContext(LangContext);
  return (
    <>
      <div className="portal-top">
        <div className="portal-top-stripes" aria-hidden>
          <span /><span />
        </div>
        <div className={`ministry-header${compact ? ' ministry-header--compact' : ''}`}>
          <div className="portal-top-inner">
            <div className="pt-ministry">
              <div className="pt-emblem">
                <img
                  className="pt-emblem-img"
                  src={SITE_LOGO}
                  alt="شعار المملكة المغربية — وزارة العدل"
                  width={132}
                  height={67}
                  decoding="async"
                />
              </div>
              <div className="pt-names">
                <div className="pt-main-title">{t.ministry}</div>
                <div className="pt-sub-title">{t.subMinistry}</div>
              </div>
            </div>

            {!compact && (
              <div className="pt-slogan">
                <span>{t.slogan1}</span>
                <small>{t.slogan2}</small>
              </div>
            )}

            <div className="pt-portal-name">
              <span>{compact ? t.portalCompact : t.portalFull}</span>
            </div>

            <button 
              className="lang-switcher"
              onClick={() => setLang(lang === 'ar' ? 'fr' : 'ar')}
              style={{
                marginLeft: lang === 'ar' ? '0' : 'auto',
                marginRight: lang === 'ar' ? 'auto' : '0',
                display: 'flex', alignItems: 'center', gap: '0.4rem',
                background: 'transparent', border: '1px solid var(--border-soft)',
                padding: '0.4rem 0.8rem', borderRadius: '6px', cursor: 'pointer',
                color: 'var(--nav-navy)', fontWeight: '600', fontSize: '0.85rem'
              }}
            >
              <Globe size={16} /> {t.langButton}
            </button>
          </div>
        </div>
      </div>
      <PortalNavWithHome compact={compact} />
    </>
  );
}

const LandingPage = ({ onStart }) => {
  const { t } = useContext(LangContext);
  return (
    <div className="landing-root fade-in" id="accueil">
      <PortalHeader compact={false} />

      <div className="landing-main">
        <section className="hero">
          <p className="hero-kicker">{t.heroKicker}</p>
          <h1 className="hero-title-main">{t.heroTitle}</h1>
          <p className="hero-lead">
            {t.heroLead}
          </p>

          <div className="landing-cards" id="services">
            <div className="svc-card">
              <div className="svc-icon-wrap">
                <BookOpen size={26} aria-hidden />
              </div>
              <h3>{t.svc1Title}</h3>
              <p>{t.svc1Desc}</p>
              <button type="button" className="svc-btn" onClick={() => scrollToId('guide')}>
                {t.svc1Btn} <ChevronLeft size={14} aria-hidden />
              </button>
            </div>

            <div className="svc-card">
              <div className="svc-icon-wrap">
                <Landmark size={26} aria-hidden />
              </div>
              <h3>{t.svc2Title}</h3>
              <p>{t.svc2Desc}</p>
              <button
                type="button"
                className="svc-btn"
                onClick={() => {
                  window.open(LINK_MAHAKIM, '_blank', 'noopener,noreferrer');
                }}
              >
                {t.svc2Btn} <ChevronLeft size={14} aria-hidden />
              </button>
            </div>

            <div className="svc-card">
              <div className="svc-icon-wrap">
                <FileSearch size={26} aria-hidden />
              </div>
              <h3>{t.svc3Title}</h3>
              <p>{t.svc3Desc}</p>
              <button type="button" className="svc-btn" onClick={() => scrollToId('avis-juridique')}>
                {t.svc3Btn} <ChevronLeft size={14} aria-hidden />
              </button>
            </div>
          </div>

          <button type="button" className="hero-cta" onClick={onStart}>
            {t.enterChat}
          </button>

          <section className="guide-section" id="guide" aria-labelledby="guide-heading">
            <h2 id="guide-heading">{t.guideTitle}</h2>
            <ol>
              <li>{t.guide1}</li>
              <li>{t.guide2}</li>
              <li>{t.guide3}</li>
              <li>{t.guide4}</li>
              <li>{t.guide5}</li>
            </ol>
            <button type="button" className="hero-cta" style={{ marginTop: '1.25rem' }} onClick={onStart}>
              {t.openChat}
            </button>
          </section>
        </section>

        <footer className="landing-footer" id="avis-juridique">
          <div className="landing-footer__inner">
            <h4>{t.disclaimerTitle}</h4>
            <p>{t.disclaimer1}</p>
            <p>{t.disclaimer2}</p>
          </div>
        </footer>
      </div>
    </div>
  );
};

const ChatbotUI = ({ onBack }) => {
  const { t } = useContext(LangContext);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messages.length === 0 && t) {
      setMessages([{
        id: 1,
        role: 'assistant',
        content: t.initialChat
      }]);
    }
  }, [t]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const query = inputValue;
    setMessages((prev) => [...prev, { id: Date.now(), role: 'user', content: query }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { id: Date.now(), role: 'assistant', content: data.response }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: 'assistant',
          content: t.errorChat,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-page fade-in">
      <PortalHeader compact />

      <div className="chat-container">
        <aside className="chat-sidebar">
          <div className="chat-sidebar-header">
            <p className="chat-sidebar-title">{t.chatInfo}</p>
            <p className="chat-sidebar-sub">{t.chatInfoSub}</p>
          </div>
          <div className="chat-sidebar-content">
            <div className="sidebar-links">
              <a className="sidebar-link-out" href={LINK_MAHAKIM} target="_blank" rel="noopener noreferrer">
                {t.track} <ExternalLink size={13} aria-hidden />
              </a>
              <a className="sidebar-link-out" href={LINK_JUSTICE_MIN} target="_blank" rel="noopener noreferrer">
                {t.contact} <ExternalLink size={13} aria-hidden />
              </a>
            </div>
            <button type="button" className="btn-link-back" onClick={onBack}>
              <ArrowRight size={17} aria-hidden /> {t.backHome}
            </button>
            <div className="sidebar-notice">
              <strong>{t.noticeTitle}</strong>
              <br />
              {t.noticeBody}
            </div>
          </div>
        </aside>

        <main className="chat-main">
          <header className="chat-header">
            <div>
              <p className="chat-header-title">{t.chatHeader}</p>
              <p className="chat-header-detail">{t.chatHeaderSub}</p>
            </div>
          </header>

          <div className="chat-messages">
            <button type="button" className="btn-link-back hide-on-desktop" onClick={onBack}>
              <ArrowRight size={17} aria-hidden /> {t.backHomeMobile}
            </button>
            {messages.map((msg) => {
              const rtl = isMostlyArabic(msg.content);
              const bubbleClass =
                msg.role === 'assistant'
                  ? `message-bubble assistant-reply${rtl ? ' is-arabic' : ''}`
                  : `message-bubble user-reply${rtl ? ' is-arabic' : ''}`;

              return (
                <div key={msg.id} className={`message-wrapper ${msg.role}`}>
                  <div className="message-avatar" aria-hidden="true">
                    {msg.role === 'assistant' ? <Scale size={18} strokeWidth={2} /> : <User size={18} />}
                  </div>
                  <div
                    className={bubbleClass}
                    dir={rtl ? 'rtl' : 'auto'}
                    lang={rtl ? 'ar' : undefined}
                    style={
                      rtl
                        ? undefined
                        : {
                            whiteSpace: 'pre-line',
                            lineHeight: '1.82',
                            color: 'var(--text-body)',
                          }
                    }
                  >
                    <MessageBody content={msg.content} />
                  </div>
                </div>
              );
            })}
            {isLoading && (
              <div className="message-wrapper assistant">
                <div className="message-avatar" aria-hidden="true">
                  <Scale size={18} strokeWidth={2} />
                </div>
                <div className="message-bubble assistant-reply loading-bubble">{t.loading}</div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-container">
            <p className="chat-disclaimer-inline">{t.chatDisclaimer}</p>
            <div className="chat-input-shell">
              <label className="chat-input-label" htmlFor="chat-query">
                {t.chatLabel}
              </label>
              <p className="chat-input-hint">{t.chatHint}</p>
              <div className="chat-input-wrapper">
                <textarea
                  id="chat-query"
                  className="chat-input"
                  placeholder={t.chatPlaceholder}
                  rows={3}
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
                  type="button"
                  className="chat-send-btn"
                  onClick={handleSend}
                  disabled={isLoading || !inputValue.trim()}
                  aria-label={t.send}
                >
                  <span>{t.send}</span>
                  <Send size={18} aria-hidden />
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default function App() {
  const [view, setView] = useState('landing');
  const [lang, setLang] = useState('ar');

  useEffect(() => {
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
  }, [lang]);

  const t = T[lang];

  return (
    <LangContext.Provider value={{ lang, setLang, t }}>
      {view === 'landing' ? (
        <LandingPage onStart={() => setView('chat')} />
      ) : (
        <ChatbotUI onBack={() => setView('landing')} />
      )}
    </LangContext.Provider>
  );
}
