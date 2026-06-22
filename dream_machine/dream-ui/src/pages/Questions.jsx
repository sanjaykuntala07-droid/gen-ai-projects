import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft, CheckCircle } from 'lucide-react';
import PageWrapper from '../components/PageWrapper.jsx';
import { getQuestions } from '../api/client.js';

// Progress ring component
function ProgressRing({ pct, size = 100, stroke = 6 }) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;
  return (
    <svg width={size} height={size} className="progress-ring">
      <defs>
        <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%"   stopColor="var(--c-primary)" />
          <stop offset="100%" stopColor="var(--c-accent)" />
        </linearGradient>
      </defs>
      <circle className="progress-ring__bg" cx={size/2} cy={size/2} r={r} strokeWidth={stroke} />
      <circle
        className="progress-ring__fg"
        cx={size/2} cy={size/2} r={r}
        strokeWidth={stroke}
        strokeDasharray={circ}
        strokeDashoffset={offset}
      />
    </svg>
  );
}

export default function Questions() {
  const navigate = useNavigate();
  const idea      = sessionStorage.getItem('dm_idea') || '';
  const idea_type = sessionStorage.getItem('dm_type') || '';
  const icon      = sessionStorage.getItem('dm_icon') || '💡';

  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers]     = useState({});
  const [step, setStep]           = useState(0);
  const [loading, setLoading]     = useState(true);
  const [customText, setCustomText] = useState('');

  useEffect(() => {
    if (!idea) { navigate('/'); return; }
    getQuestions(idea, idea_type)
      .then(r => { setQuestions(r.data.questions); setLoading(false); })
      .catch(() => { navigate('/'); });
  }, []);

  const q     = questions[step];
  const total = questions.length;
  const pct   = total ? Math.round(((step) / total) * 100) : 0;

  const selectOption = (opt) => {
    setAnswers(prev => ({ ...prev, [step]: opt }));
    setCustomText('');
  };

  const handleNext = () => {
    const answer = customText.trim() || answers[step];
    if (!answer) return;
    const updated = { ...answers, [step]: answer };
    setAnswers(updated);

    if (step < total - 1) {
      setStep(s => s + 1);
      setCustomText('');
    } else {
      // Done — build final answers map keyed by question text
      const finalAnswers = {};
      questions.forEach((q, i) => {
        finalAnswers[q.question] = updated[i] || '';
      });
      sessionStorage.setItem('dm_answers', JSON.stringify(finalAnswers));
      navigate('/generating');
    }
  };

  if (loading) return (
    <PageWrapper>
      <div className="gen-container" style={{ paddingTop: 60 }}>
        <div className="spinner" style={{ width: 48, height: 48 }} />
        <p style={{ color: 'var(--c-text-2)', marginTop: 16 }}>Crafting your discovery questions…</p>
      </div>
    </PageWrapper>
  );

  return (
    <PageWrapper>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <button className="btn btn--ghost btn--sm" onClick={() => step > 0 ? setStep(s => s-1) : navigate('/')} id="btn-back">
          <ArrowLeft size={14} />
        </button>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className="qa-step">Question {step + 1} of {total}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--c-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {icon} {idea_type}
          </div>
        </div>
        <div style={{ position: 'relative' }}>
          <ProgressRing pct={pct} size={52} stroke={4} />
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', fontWeight: 700, color: 'var(--c-primary)' }}>
            {pct}%
          </div>
        </div>
      </div>

      {/* Question */}
      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.28 }}
        >
          <div className="glass-card glass-card--gradient mb-4">
            <h2 style={{ fontFamily: 'var(--f-display)', fontSize: '1.1rem', fontWeight: 700, marginBottom: 16, lineHeight: 1.4 }}>
              {q?.question}
            </h2>

            {/* Option chips */}
            <div className="qa-options">
              {q?.options?.map(opt => (
                <button
                  key={opt}
                  className={`chip ${answers[step] === opt && !customText ? 'active' : ''}`}
                  onClick={() => selectOption(opt)}
                  id={`btn-option-${opt.replace(/\s+/g,'-')}`}
                >
                  {answers[step] === opt && !customText && <CheckCircle size={11} />}
                  {opt}
                </button>
              ))}
            </div>

            {/* Custom input */}
            <textarea
              className="input"
              placeholder={q?.placeholder || 'Or type your own answer…'}
              value={customText}
              onChange={e => { setCustomText(e.target.value); if (e.target.value) setAnswers(a => ({...a, [step]: ''})); }}
              rows={2}
              style={{ marginTop: 8 }}
            />
          </div>

          <button
            className="btn btn--primary btn--full btn--lg"
            onClick={handleNext}
            disabled={!answers[step] && !customText.trim()}
            id="btn-next-question"
          >
            {step === total - 1 ? 'Generate Blueprint' : 'Next Question'} <ArrowRight size={16} />
          </button>
        </motion.div>
      </AnimatePresence>
    </PageWrapper>
  );
}
