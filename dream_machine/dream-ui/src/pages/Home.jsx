import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ArrowRight, Zap, Users, FileText, Activity, Cpu, ShieldCheck } from 'lucide-react';
import PageWrapper from '../components/PageWrapper.jsx';
import { detectType, getStats, getBlueprints } from '../api/client.js';

const POPULAR_TYPES = [
  { name: 'SaaS Platform', icon: '🖥️' },
  { name: 'Mobile App', icon: '📱' },
  { name: 'AI Tool', icon: '🤖' },
  { name: 'Workflow Automation', icon: '⚙️' },
  { name: 'Game', icon: '🎮' },
  { name: 'Marketplace', icon: '🛒' },
  { name: 'Business Concept', icon: '💼' },
  { name: 'Hardware Device', icon: '🔌' }
];

export default function Home() {
  const [idea, setIdea] = useState('');
  const [selectedType, setSelectedType] = useState(null);
  const [userName, setUserName] = useState(sessionStorage.getItem('dm_name') || '');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [recentBps, setRecentBps] = useState([]);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const textRef = useRef(null);

  // Load stats and recent blueprints, and clear session
  useEffect(() => {
    getStats().then(r => setStats(r.data)).catch(() => {});
    getBlueprints(4).then(r => setRecentBps(r.data.blueprints || [])).catch(() => {});
    
    // Clear leftover session data to start fresh
    sessionStorage.removeItem('dm_idea');
    sessionStorage.removeItem('dm_type');
    sessionStorage.removeItem('dm_icon');
    sessionStorage.removeItem('dm_answers');
  }, []);

  const handleSubmit = async () => {
    if (!idea.trim() || idea.trim().length < 10) {
      setError('Please describe your idea in at least 10 characters.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      let ideaType = selectedType;
      let typeIcon = '💡';

      if (!ideaType) {
        // Auto-detect type if not explicitly selected
        const { data } = await detectType(idea.trim());
        ideaType = data.idea_type;
        typeIcon = data.icon;
      } else {
        const matchingType = POPULAR_TYPES.find(t => t.name === ideaType);
        if (matchingType) typeIcon = matchingType.icon;
      }

      // Save user details to sessionStorage
      sessionStorage.setItem('dm_idea', idea.trim());
      sessionStorage.setItem('dm_type', ideaType);
      sessionStorage.setItem('dm_icon', typeIcon);
      sessionStorage.setItem('dm_name', userName.trim() || 'Guest Builder');

      navigate('/questions');
    } catch (e) {
      setError('Could not connect to the engineering engine. Is the backend running?');
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit();
  };

  return (
    <PageWrapper className="page--wide">
      {/* Hero Banner */}
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
        >
          <div className="hero__eyebrow" style={{ marginBottom: 12 }}>
            <Sparkles size={11} style={{ marginRight: 4 }} />
            ✦ Dream Machine Engine v2
          </div>
        </motion.div>

        <motion.h1
          className="hero__title"
          style={{ fontSize: 'clamp(1.8rem, 6vw, 2.8rem)', marginBottom: 6 }}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
        >
          Innovate your idea <span className="hero__gradient-text">in 60 seconds.</span>
        </motion.h1>
        <p style={{ color: 'var(--c-text-2)', fontSize: '0.86rem', maxWidth: 440, margin: '0 auto 12px' }}>
          Your idea. Fully engineered. Describe any concept, choose a framework, and build a strategic architecture instantly.
        </p>
      </div>

      {/* Main Grid: Split Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
        
        {/* Left Column: Command Console (Inputs) */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          style={{ display: 'flex', flexDirection: 'column', gap: 16 }}
        >
          {/* Card 1: Describe the Idea */}
          <div className="idea-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, borderBottom: '1px solid var(--b-subtle)', paddingBottom: 8 }}>
              <Cpu size={14} style={{ color: 'var(--c-primary)' }} />
              <span style={{ fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--c-text)' }}>
                1. Product Concept
              </span>
            </div>
            <textarea
              ref={textRef}
              className="idea-textarea"
              placeholder="Describe what you want to build (e.g. 'A mobile marketplace for buying and selling fresh local organic honey'...)"
              value={idea}
              onChange={e => { setIdea(e.target.value); setError(''); }}
              onKeyDown={handleKey}
              rows={4}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--c-muted)' }}>
                {idea.length > 0 ? `${idea.length} chars` : '⌘ + Enter to submit'}
              </span>
              <input
                type="text"
                placeholder="Developer name (optional)"
                className="input"
                style={{ width: 140, padding: '6px 10px', borderRadius: 'var(--r-sm)', fontSize: '0.75rem' }}
                value={userName}
                onChange={e => setUserName(e.target.value)}
              />
            </div>
          </div>

          {/* Card 2: Select Category (Graphical Selector) */}
          <div className="glass-card" style={{ padding: 18 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, borderBottom: '1px solid var(--b-subtle)', paddingBottom: 8 }}>
              <Zap size={14} style={{ color: 'var(--c-accent)' }} />
              <span style={{ fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--c-text)' }}>
                2. Select Framework Type (Optional)
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
              {POPULAR_TYPES.map(t => {
                const isSelected = selectedType === t.name;
                return (
                  <button
                    key={t.name}
                    className={`type-card ${isSelected ? 'selected' : ''}`}
                    onClick={() => setSelectedType(isSelected ? null : t.name)}
                    style={{ background: isSelected ? 'var(--c-primary-dim)' : 'rgba(255,255,255,0.015)', border: isSelected ? '1px solid var(--c-primary)' : '1px solid var(--b-subtle)', padding: '10px 12px', outline: 'none', textAlign: 'left' }}
                  >
                    <span className="type-card__icon">{t.icon}</span>
                    <span className="type-card__name" style={{ fontSize: '0.76rem' }}>{t.name}</span>
                  </button>
                );
              })}
            </div>
            {!selectedType && (
              <div style={{ fontSize: '0.7rem', color: 'var(--c-muted)', marginTop: 8, textAlign: 'center' }}>
                💡 Leave unselected for AI auto-detection
              </div>
            )}
          </div>

          {/* Submit Trigger */}
          <div>
            <button
              className="btn btn--primary btn--full btn--lg"
              onClick={handleSubmit}
              disabled={loading}
              id="btn-submit-idea"
              style={{ padding: '16px' }}
            >
              {loading ? (
                <>
                  <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                  Running AI Synthesis…
                </>
              ) : (
                <>
                  Build Digital Blueprint <ArrowRight size={16} />
                </>
              )}
            </button>
            <AnimatePresence>
              {error && (
                <motion.p
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  style={{ color: 'var(--c-danger)', fontSize: '0.78rem', marginTop: 8, textAlign: 'center' }}
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Right Column: Engine Dashboard (Metrics & Live Activity) */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          style={{ display: 'flex', flexDirection: 'column', gap: 16 }}
        >
          {/* Card 1: System Telemetry */}
          <div className="glass-card" style={{ padding: 18 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, borderBottom: '1px solid var(--b-subtle)', paddingBottom: 8 }}>
              <Activity size={14} style={{ color: 'var(--c-primary)' }} />
              <span style={{ fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--c-text)' }}>
                System Metrics
              </span>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, textAlign: 'center' }}>
              {[
                { label: 'Blueprints', value: stats?.total_blueprints ?? '—', icon: FileText },
                { label: 'Builders', value: stats?.total_users ?? '—', icon: Users },
                { label: 'Nodes Compiled', value: stats?.total_sections ?? '—', icon: Zap }
              ].map(({ label, value, icon: Icon }) => (
                <div key={label} style={{ background: 'rgba(255,255,255,0.015)', borderRadius: 'var(--r-md)', padding: '12px 8px', border: '1px solid var(--b-subtle)' }}>
                  <Icon size={13} style={{ color: 'var(--c-primary)', marginBottom: 4 }} />
                  <div style={{ fontSize: '1.2rem', fontFamily: 'var(--f-display)', fontWeight: 800, color: 'var(--c-text)' }}>
                    {value}
                  </div>
                  <div style={{ fontSize: '0.62rem', color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    {label}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 12, background: 'rgba(0,245,212,0.04)', border: '1px solid rgba(0,245,212,0.15)', borderRadius: 'var(--r-sm)', padding: '8px 10px' }}>
              <ShieldCheck size={12} style={{ color: 'var(--c-accent)' }} />
              <span style={{ fontSize: '0.68rem', color: 'var(--c-accent)' }}>
                Gemini 2.5 Engine: Online · Latency normal
              </span>
            </div>
          </div>

          {/* Card 2: Recent Architectures (Feed) */}
          <div className="glass-card" style={{ padding: 18, flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, borderBottom: '1px solid var(--b-subtle)', paddingBottom: 8 }}>
              <FileText size={14} style={{ color: 'var(--c-accent)' }} />
              <span style={{ fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--c-text)' }}>
                Recent Blueprints
              </span>
            </div>

            {recentBps.length === 0 ? (
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.78rem', color: 'var(--c-muted)', padding: '30px 0' }}>
                No architectures in feed
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, flex: 1 }}>
                {recentBps.map(bp => (
                  <div
                    key={bp.id}
                    onClick={() => navigate(`/blueprint/${bp.id}`)}
                    style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', background: 'rgba(255,255,255,0.015)', border: '1px solid var(--b-subtle)', borderRadius: 'var(--r-md)', cursor: 'pointer', transition: 'all 0.2s' }}
                    className="gallery-item-feed"
                  >
                    <div style={{ minWidth: 0, marginRight: 10 }}>
                      <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--c-text)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {bp.idea}
                      </div>
                      <div style={{ fontSize: '0.64rem', color: 'var(--c-muted)' }}>
                        {bp.idea_type || 'Custom blueprint'}
                      </div>
                    </div>
                    <div style={{ fontSize: '0.62rem', color: 'var(--c-primary)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.02em', background: 'var(--c-primary-dim)', padding: '2px 8px', borderRadius: '99px', flexShrink: 0 }}>
                      Inspect
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </PageWrapper>
  );
}
