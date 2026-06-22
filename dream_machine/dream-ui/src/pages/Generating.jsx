import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, Circle, Loader } from 'lucide-react';
import PageWrapper from '../components/PageWrapper.jsx';
import { generateStream } from '../api/client.js';

const SECTIONS = [
  { key: 'executive_summary',     label: '📋 Executive Summary'   },
  { key: 'user_personas',         label: '👥 User Personas'        },
  { key: 'core_features',         label: '⚡ Core Features'        },
  { key: 'architecture',          label: '🏗️ Architecture'         },
  { key: 'tech_stack',            label: '🔧 Tech Stack'           },
  { key: 'roadmap',               label: '🗓️ Roadmap'              },
  { key: 'business_model',        label: '💰 Business Model'       },
  { key: 'risk_analysis',         label: '⚠️ Risk Analysis'        },
  { key: 'competitor_landscape',  label: '🏁 Competitor Landscape' },
  { key: 'success_metrics',       label: '📊 Success Metrics'      },
];

export default function Generating() {
  const navigate = useNavigate();
  const idea      = sessionStorage.getItem('dm_idea') || '';
  const idea_type = sessionStorage.getItem('dm_type') || '';
  const icon      = sessionStorage.getItem('dm_icon') || '💡';
  const answers   = JSON.parse(sessionStorage.getItem('dm_answers') || '{}');
  const user_name = sessionStorage.getItem('dm_name') || 'User';

  const [status, setStatus] = useState({}); // key -> 'pending' | 'streaming' | 'done'
  const [current, setCurrent] = useState(null);
  const [pct, setPct] = useState(0);
  const [blueprintId, setBlueprintId] = useState(null);
  const started = useRef(false);

  useEffect(() => {
    if (!idea) { navigate('/'); return; }
    if (started.current) return;
    started.current = true;

    const init = {};
    SECTIONS.forEach(s => { init[s.key] = 'pending'; });
    setStatus(init);

    generateStream(idea, idea_type, answers, user_name, (msg) => {
      if (msg.type === 'init') {
        setBlueprintId(msg.blueprint_id);
      } else if (msg.type === 'section_start') {
        setCurrent(msg.key);
        setStatus(prev => ({ ...prev, [msg.key]: 'streaming' }));
      } else if (msg.type === 'section_done') {
        setStatus(prev => ({ ...prev, [msg.key]: 'done' }));
        const done = Object.values({ ...status, [msg.key]: 'done' }).filter(v => v === 'done').length;
        setPct(Math.round((done / SECTIONS.length) * 100));
      } else if (msg.type === 'complete') {
        setPct(100);
        setTimeout(() => navigate(`/blueprint/${msg.blueprint_id}`), 800);
      }
    }).catch(e => {
      console.error(e);
      navigate('/');
    });
  }, []);

  // Progress ring
  const r = 50, stroke = 6, circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;

  return (
    <PageWrapper>
      <div className="gen-container">
        <div className="gen-ring-wrapper" style={{ width: 120, height: 120 }}>
          <svg width={120} height={120} className="progress-ring">
            <defs>
              <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="var(--c-primary)" />
                <stop offset="100%" stopColor="var(--c-accent)" />
              </linearGradient>
            </defs>
            <circle className="progress-ring__bg" cx={60} cy={60} r={r} strokeWidth={stroke} />
            <circle
              className="progress-ring__fg"
              cx={60} cy={60} r={r}
              strokeWidth={stroke}
              strokeDasharray={circ}
              strokeDashoffset={offset}
            />
          </svg>
          <div className="gen-ring-emoji">{icon}</div>
          <div style={{ position: 'absolute', bottom: -24, left: 0, right: 0, textAlign: 'center', fontSize: '0.9rem', fontWeight: 700, color: 'var(--c-primary)' }}>
            {pct}%
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: 40, marginBottom: 24 }}>
          <h2 style={{ fontFamily: 'var(--f-display)', fontSize: '1.2rem', fontWeight: 800, marginBottom: 6 }}>
            Building Your Blueprint
          </h2>
          <p style={{ color: 'var(--c-text-2)', fontSize: '0.85rem', maxWidth: 280, margin: '0 auto' }}>
            {idea.length > 60 ? idea.slice(0, 60) + '…' : idea}
          </p>
        </div>

        {/* Section list */}
        <div className="gen-sections">
          {SECTIONS.map(({ key, label }) => {
            const state = status[key] || 'pending';
            return (
              <motion.div
                key={key}
                className={`gen-section-item ${state === 'streaming' ? 'active' : ''} ${state === 'done' ? 'done' : ''}`}
                animate={state === 'streaming' ? { x: [0, 2, 0] } : {}}
                transition={{ repeat: Infinity, duration: 1 }}
              >
                {state === 'done'      ? <CheckCircle size={14} /> :
                 state === 'streaming' ? <Loader size={14} style={{ animation: 'spin 1s linear infinite' }} /> :
                 <Circle size={14} />}
                {label}
              </motion.div>
            );
          })}
        </div>
      </div>
    </PageWrapper>
  );
}
