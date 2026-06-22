import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Download, Trash2, ThumbsUp, ThumbsDown } from 'lucide-react';
import PageWrapper from '../components/PageWrapper.jsx';
import Markdown from '../components/Markdown.jsx';
import { getBlueprint, deleteBlueprint } from '../api/client.js';

const SECTIONS = [
  { key: 'executive_summary',    label: '📋 Summary'     },
  { key: 'user_personas',        label: '👥 Personas'    },
  { key: 'core_features',        label: '⚡ Features'    },
  { key: 'architecture',         label: '🏗️ Architecture'},
  { key: 'tech_stack',           label: '🔧 Tech Stack'  },
  { key: 'roadmap',              label: '🗓️ Roadmap'     },
  { key: 'business_model',       label: '💰 Business'    },
  { key: 'risk_analysis',        label: '⚠️ Risks'       },
  { key: 'competitor_landscape', label: '🏁 Competitors' },
  { key: 'success_metrics',      label: '📊 Metrics'     },
];

export default function Blueprint() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [bp, setBp]         = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [deleting, setDeleting]   = useState(false);

  useEffect(() => {
    getBlueprint(id)
      .then(r => { setBp(r.data); setLoading(false); })
      .catch(() => { navigate('/gallery'); });
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm('Delete this blueprint?')) return;
    setDeleting(true);
    await deleteBlueprint(id);
    navigate('/gallery');
  };

  const handleExport = () => {
    if (!bp) return;
    const text = SECTIONS.map(s => `# ${s.label}\n\n${bp.sections?.[s.key] || 'Not generated'}`).join('\n\n---\n\n');
    const blob = new Blob([`# ${bp.idea}\n\n${text}`], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `dream-machine-${id.slice(0,8)}.md`;
    a.click();
  };

  if (loading) return (
    <PageWrapper>
      <div className="gen-container" style={{ paddingTop: 60 }}>
        <div className="spinner" style={{ width: 48, height: 48 }} />
        <p style={{ color: 'var(--c-text-2)', marginTop: 16 }}>Loading blueprint…</p>
      </div>
    </PageWrapper>
  );

  const section = SECTIONS[activeTab];
  const content = bp?.sections?.[section.key] || '*Not generated yet.*';

  return (
    <PageWrapper className="page--wide">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <button className="btn btn--ghost btn--sm" onClick={() => navigate('/gallery')} id="btn-bp-back">
          <ArrowLeft size={14} /> Gallery
        </button>
        <div className="flex gap-2">
          <button className="btn btn--ghost btn--sm" onClick={handleExport} id="btn-bp-export" title="Export">
            <Download size={14} />
          </button>
          <button className="btn btn--danger btn--sm" onClick={handleDelete} disabled={deleting} id="btn-bp-delete" title="Delete">
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {/* Idea title */}
      <div className="glass-card glass-card--gradient mb-4">
        <div className="flex items-center gap-2 mb-2">
          <span style={{ fontSize: '1.4rem' }}>{sessionStorage.getItem('dm_icon') || '💡'}</span>
          <span className="badge badge--primary">{bp?.idea_type || 'Idea'}</span>
        </div>
        <h1 className="page-heading" style={{ fontSize: '1.2rem', margin: 0 }}>{bp?.idea}</h1>
        <div className="text-xs text-muted mt-2">{bp?.created_at ? new Date(bp.created_at).toLocaleDateString() : ''}</div>
      </div>

      {/* Section Tabs */}
      <div className="tabs">
        {SECTIONS.map((s, i) => (
          <button
            key={s.key}
            className={`tab ${activeTab === i ? 'active' : ''}`}
            onClick={() => setActiveTab(i)}
            id={`tab-${s.key}`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* Section Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
          className="section-card"
        >
          <div className="section-card__header">
            <div className="section-card__title">{section.label}</div>
            <div className={`section-card__status ${content && content !== '*Not generated yet.*' ? 'done' : ''}`} />
          </div>
          <Markdown content={content} />
        </motion.div>
      </AnimatePresence>
    </PageWrapper>
  );
}
