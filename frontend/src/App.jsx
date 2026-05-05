import React, { useState, useRef, useEffect } from 'react';
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
} from 'lucide-react';
import './index.css';

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
  if (compact) return null;
  return (
    <nav className="portal-nav" aria-label="التنقل الرئيسي">
      <div className="portal-nav-inner">
        <a href="#accueil" className="portal-nav-home" title="الاستقبال" aria-label="الانتقال إلى الاستقبال">
          <Home size={20} aria-hidden />
        </a>
        <a href="#accueil">استقبال المنصة</a>
        <a href={LINK_MAHAKIM} target="_blank" rel="noopener noreferrer">
          تتبع الملفات <ExternalLink size={11} style={{ opacity: 0.85 }} aria-hidden />
        </a>
        <a href={LINK_JUSTICE_MIN} target="_blank" rel="noopener noreferrer">
          السجل العدلي والخدمات <ExternalLink size={11} style={{ opacity: 0.85 }} aria-hidden />
        </a>
        <a href="#guide">دليل المستعمل</a>
        <a href={LINK_JUSTICE_MIN} target="_blank" rel="noopener noreferrer">
          الاتصال بوزارة العدل <ExternalLink size={11} style={{ opacity: 0.85 }} aria-hidden />
        </a>
      </div>
    </nav>
  );
}

function PortalHeader({ compact }) {
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
                <div className="pt-main-title">المملكة المغربية · وزارة العدل</div>
                <div className="pt-sub-title">مساعد إرشادي — مدونة الشغل المغربية</div>
              </div>
            </div>

            {!compact && (
              <div className="pt-slogan">
                <span>محاكم المملكة في خدمة المواطنة</span>
                <small>خدمات رقمية بروح الإدارة المواطَنة</small>
              </div>
            )}

            <div className="pt-portal-name">
              <span>{compact ? 'استشارات مدونة الشغل' : 'مساعد مدونة الشغل الإلكتروني'}</span>
            </div>
          </div>
        </div>
      </div>
      <PortalNavWithHome compact={compact} />
    </>
  );
}

const LandingPage = ({ onStart }) => {
  return (
    <div className="landing-root fade-in" id="accueil">
      <PortalHeader compact={false} />

      <div className="landing-main">
        <section className="hero">
          <p className="hero-kicker">خدمات رقمية</p>
          <h1 className="hero-title-main">مساندة استشارية لمدونة الشغل المغربية</h1>
          <p className="hero-lead">
            تستند الإجابات إلى مقتطفات من المواد المتعلقة بطلبكم، وفق آلية بحث دلالي في الوثائق الممركزة؛
            المعاينة تجري فقط وفق المراجع الواردة، مع إقراركم بمراجعتكم للجهة المعنية والنشر الرسمي.
          </p>

          <div className="landing-cards" id="services">
            <div className="svc-card">
              <div className="svc-icon-wrap">
                <BookOpen size={26} aria-hidden />
              </div>
              <h3>المرجعية النصّية</h3>
              <p>تلخيص مهيكل يعتمد المواد المعروضة أثناء الاسترجاع من قاعدة النصوص المرجعية للمساعد.</p>
              <button type="button" className="svc-btn" onClick={() => scrollToId('guide')}>
                تعرّف على آلية العمل <ChevronLeft size={14} aria-hidden />
              </button>
            </div>

            <div className="svc-card">
              <div className="svc-icon-wrap">
                <Landmark size={26} aria-hidden />
              </div>
              <h3>البورتالات الوطنية</h3>
              <p>الربط المباشر ببوابة محاكم وموقع وزارة العدل للخدمات القضائية والإدارية الرسمية.</p>
              <button
                type="button"
                className="svc-btn"
                onClick={() => {
                  window.open(LINK_MAHAKIM, '_blank', 'noopener,noreferrer');
                }}
              >
                فتح بوابة محاكم <ChevronLeft size={14} aria-hidden />
              </button>
            </div>

            <div className="svc-card">
              <div className="svc-icon-wrap">
                <FileSearch size={26} aria-hidden />
              </div>
              <h3>التحقّق والمسؤولية</h3>
              <p>المواءمة مع مدونة الشغل المنشورة في الجريدة الرسمية قبل أي قرار مهني أو تنفيذي.</p>
              <button type="button" className="svc-btn" onClick={() => scrollToId('avis-juridique')}>
                قراءة الإشعار القانوني <ChevronLeft size={14} aria-hidden />
              </button>
            </div>
          </div>

          <button type="button" className="hero-cta" onClick={onStart}>
            الدخول إلى منصّة الاستشارة
          </button>

          <section className="guide-section" id="guide" aria-labelledby="guide-heading">
            <h2 id="guide-heading">دليل المستعمل — مساعد مدونة الشغل</h2>
            <ol>
              <li>
                اضغطوا «الدخول إلى منصّة الاستشارة» أو زِر زر «فتح المحادثة» أسفل هذه الخطوات بعد تنصيب الخادم المحلي.
              </li>
              <li>
                صاغوا سؤالكم بوضوح (يمكن بالعربية أو الفرنسية أو الإنجليزية؛ ستكون الإجابة بالعربية الفصحى وفق إعدادات النظام).
              </li>
              <li>
                انتظروا ظهور الأقسام الثلاثة: الإجابة، التوضيح، الأساس القانوني مع أرقام المواد المقتبسة من القاعدة.
              </li>
              <li>
                راجعوا دائماً النصوص على الجريدة الرسمية أو مع مختص قانوني قبل اتخاذ أي إجراء.
              </li>
              <li>
                للتتبع القضائي والخدمات الحكومية استعملوا روابط «بوابة محاكم» و«وزارة العدل» في الشريط العلوي.
              </li>
            </ol>
            <button type="button" className="hero-cta" style={{ marginTop: '1.25rem' }} onClick={onStart}>
              فتح المحادثة الآن
            </button>
          </section>
        </section>

        <footer className="landing-footer" id="avis-juridique">
          <div className="landing-footer__inner">
            <h4>إشعار قانوني وإخلاء مسؤولية</h4>
            <p>
              هذه الواجهة أداة إرشادية تعتمد التوليف الآلي؛ لا تغني عن استشارة محام أو مستشار قانوني مؤهل، ولا عن
              إجراء أو مرسوم صادر عن جهة مختصّة بالوزارة أو القضاء أو الإدارات ذات الصلة بالشغل.
            </p>
            <p>
              الأجوبة المركّبة آلياً تجب مطابقتها مع النشر الرسمي في الجريدة الرسمية؛ أي قرار دون ذلك يبقى على مسؤولية المستخدم.
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
};

const ChatbotUI = ({ onBack }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content:
        '**الإجابة :** مرحبا، يعمل المُساند على استجلاء المواد المتعلقة بمدونة الشغل وفق الأسئلة الموجهة له.\n\n' +
        '**التوضيح :** يمكنكم صياغة الاستفسار باللسان الذي تريدونه؛ ستُنسَج الإجابة بالعربية الفصحى المهنية مع الحفاظ على أرقام المواد المرجعة.\n\n' +
        '**الأساس القانوني :** تأتي المواد المعروضة من قاعدة النصوص المدمجة في النظام قبل التوليف.',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

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
          content:
            '**الإجابة :** تعذّر الوصول إلى خادّم المعالجة.\n\n**التوضيح :** تأكّدوا من تشغيل واجهة FastAPI على العنوان 127.0.0.1:8000 وفحص شبكتكم.\n\n**الأساس القانوني :** لا ينطبق.',
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
            <p className="chat-sidebar-title">معلومات خدمية</p>
            <p className="chat-sidebar-sub">قطاع العدالة الرقمية · مدونة الشغل · استرجاع دلالي وتوليف نصي</p>
          </div>
          <div className="chat-sidebar-content">
            <div className="sidebar-links">
              <a className="sidebar-link-out" href={LINK_MAHAKIM} target="_blank" rel="noopener noreferrer">
                بوابة محاكم <ExternalLink size={13} aria-hidden />
              </a>
              <a className="sidebar-link-out" href={LINK_JUSTICE_MIN} target="_blank" rel="noopener noreferrer">
                موقع وزارة العدل <ExternalLink size={13} aria-hidden />
              </a>
            </div>
            <button type="button" className="btn-link-back" onClick={onBack}>
              <ArrowRight size={17} aria-hidden /> العودة لاستقبال المنصّة
            </button>
            <div className="sidebar-notice">
              <strong>تنبيه</strong>
              <br />
              تُنشَأ المقاطع باستخدام نموذج لغوي؛ التثبُّت إلزامي أمام المراجع المعتمدة والجريدة الرسمية قبل أي قرار مهني.
            </div>
          </div>
        </aside>

        <main className="chat-main">
          <header className="chat-header">
            <div>
              <p className="chat-header-title">جلسة استشارية فورية — مدونة الشغل</p>
              <p className="chat-header-detail">
                عرض المواد المستخلصة وفق استفساركم؛ السجل الحالي يُحفظ في المتصفح لهذه الجولة فقط وليس أرشيفاً إدارياً.
              </p>
            </div>
          </header>

          <div className="chat-messages">
            <button type="button" className="btn-link-back hide-on-desktop" onClick={onBack}>
              <ArrowRight size={17} aria-hidden /> عودة
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
                <div className="message-bubble assistant-reply loading-bubble">جاري التحليل والمراجعة الموضوعية…</div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-container">
            <p className="chat-disclaimer-inline">
              أداة إرشادية لا تمثل موقفاً إدارياً ولا حكماً قضائياً؛ التحقق من النشر الرسمي في الجريدة الرسمية واجب قبل أي قرار.
            </p>
            <div className="chat-input-shell">
              <label className="chat-input-label" htmlFor="chat-query">
                صياغة الاستفسار
              </label>
              <p className="chat-input-hint">اكتبوا سؤالكم بوضوح؛ يمكن استخدام العربية أو الفرنسية أو الإنجليزية. المفتاح Enter يرسل، Shift+Enter سطر جديد.</p>
              <div className="chat-input-wrapper">
                <textarea
                  id="chat-query"
                  className="chat-input"
                  placeholder="مثال: ما مدة إشعار فسخ عقد العمل؟ أو ما حقوقي إذا تعرضتُ لمضايقة في العمل؟"
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
                  aria-label="إرسال السؤال"
                >
                  <span>إرسال</span>
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
  return view === 'landing' ? (
    <LandingPage onStart={() => setView('chat')} />
  ) : (
    <ChatbotUI onBack={() => setView('landing')} />
  );
}
