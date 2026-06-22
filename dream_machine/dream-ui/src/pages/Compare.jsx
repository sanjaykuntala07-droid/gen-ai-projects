import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GitCompare, Loader, ChevronDown } from 'lucide-react';
import PageWrapper from '../components/PageWrapper.jsx';
import Markdown from '../components/Markdown.jsx';
import { getBlueprints, compareBlueprints } from '../api/client.js';

export default function Compare() {
  const [blueprints, setBlueprints] = useState([]);
  const [idA, setIdA]         = useState('');
  const [idB, setIdB]         = useState('');
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  useEffect(() => {
    getBlueprints(50).then(r => setBlueprints(r.data.blueprints || [])).catch(() => {});
  }, []);

  const handleCompare = async () => {
    if (!idA || !idB || idA === idB) { setError('Select two different blueprints.'); return; }
    setError('');
    setLoading(true);
    setResult(null);
    try {
      const r = await compareBlueprints(idA, idB);
      setResult(r.data);
    } catch (e) {
      setError('Comparison failed. Please try again.');
    }
    setLoading(false);
  };

  const findBp = (id) => blueprints.find(b => b.id === id);

  return (
    <PageWrapper>
      <h1 className="page-heading">Compare</h1>
      <p className="page-sub">Select two blueprints to get an AI strategic analysis.</p>

      {blueprints.length < 2 ? (
        <div className="empty-state">
          <div className="empty-state__icon">🔭</div>
          <div className="empty-state__title">Need at least 2 blueprints</div>
          <div className="empty-state__sub">Create more blueprints from the Home screen to compare them.</div>
        </div>
      ) : (
        <>
          {/* Blueprint selectors */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 16 }}>
            {[{ id: idA, set: setIdA, label: 'Blueprint A' }, { id: idB, set: setIdB, label: 'Blueprint B' }].map(({ id, set, label }) => (
              <div key={label}>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-text-2)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6, display: 'block' }}>
                  {label}
                </label>
                <div style={{ position: 'relative' }}>
                  <select
                    className="input"
                    value={id}
                    onChange={e => set(e.target.value)}
                    style={{ appearance: 'none', paddingRight: 32 }}
                  >
                    <option value="">Select…</option>
                    {blueprints.map(b => (
                      <option key={b.id} value={b.id}>
                        {b.idea?.slice(0, 40) + (b.idea?.length > 40 ? '…' : '')}
                      </option>
                    ))}
                  </select>
                  <ChevronDown size={14} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--c-muted)', pointerEvents: 'none' }} />
                </div>
              </div>
            ))}
          </div>

          {error && <p style={{ color: 'var(--c-danger)', fontSize: '0.8rem', marginBottom: 12 }}>{error}</p>}

          <button
            className="btn btn--primary btn--full"
            onClick={handleCompare}
            disabled={loading || !idA || !idB}
            id="btn-compare"
          >
            {loading ? <><div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Analyzing…</> : <><GitCompare size={15} /> Compare Blueprints</>}
          </button>

          {/* Side-by-side previews */}
          {idA && idB && !result && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 16 }}>
              {[findBp(idA), findBp(idB)].map((bp, i) => bp && (
                <div key={i} className="glass-card" style={{ padding: 14 }}>
                  <div style={{ fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: i === 0 ? 'var(--c-primary)' : 'var(--c-accent)', marginBottom: 6 }}>
                    {i === 0 ? 'Blueprint A' : 'Blueprint B'}
                  </div>
                  <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--c-text)', lineHeight: 1.4 }}>
                    {bp.idea?.slice(0, 60)}{bp.idea?.length > 60 ? '…' : ''}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--c-muted)', marginTop: 6 }}>{bp.idea_type}</div>
                </div>
              ))}
            </div>
          )}

          {/* Result */}
          <AnimatePresence>
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="glass-card glass-card--gradient mt-4"
              >
                <div style={{ fontFamily: 'var(--f-display)', fontSize: '0.9rem', fontWeight: 700, marginBottom: 12, color: 'var(--c-text)' }}>
                  🤖 AI Strategic Analysis
                </div>
                <Markdown content={result.analysis} />
              </motion.div>
            )}
          </AnimatePresence>
        </>
      )}
    </PageWrapper>
  );
}
