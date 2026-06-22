import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plus, Search, Trash2 } from 'lucide-react';
import PageWrapper from '../components/PageWrapper.jsx';
import { getBlueprints, deleteBlueprint } from '../api/client.js';

export default function Gallery() {
  const [items, setItems]       = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [query, setQuery]       = useState('');
  const [loading, setLoading]   = useState(true);
  const navigate = useNavigate();

  const load = () => {
    setLoading(true);
    getBlueprints(50).then(r => {
      setItems(r.data.blueprints || []);
      setFiltered(r.data.blueprints || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleSearch = (e) => {
    const q = e.target.value;
    setQuery(q);
    setFiltered(items.filter(b =>
      b.idea?.toLowerCase().includes(q.toLowerCase()) ||
      b.idea_type?.toLowerCase().includes(q.toLowerCase())
    ));
  };

  const handleDelete = async (e, id) => {
    e.preventDefault(); e.stopPropagation();
    if (!window.confirm('Delete?')) return;
    await deleteBlueprint(id);
    load();
  };

  const typeIcon = {
    'SaaS Platform':'🖥️','Mobile App':'📱','Physical Product':'📦',
    'Workflow Automation':'⚙️','Business Concept':'💼','Social Cause':'🌍',
    'AI Tool':'🤖','Game':'🎮','Marketplace':'🛒','Other':'💡',
  };

  return (
    <PageWrapper>
      <div className="flex items-center justify-between mb-4">
        <h1 className="page-heading" style={{ fontSize: '1.4rem', margin: 0 }}>My Blueprints</h1>
        <button className="btn btn--primary btn--sm" onClick={() => navigate('/')} id="btn-new-blueprint">
          <Plus size={14} /> New
        </button>
      </div>

      {/* Search */}
      <div className="input-group">
        <div style={{ position: 'relative' }}>
          <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--c-muted)' }} />
          <input
            className="input"
            style={{ paddingLeft: 34 }}
            placeholder="Search ideas…"
            value={query}
            onChange={handleSearch}
          />
        </div>
      </div>

      {loading ? (
        <div className="gen-container" style={{ paddingTop: 40 }}>
          <div className="spinner" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state__icon">🌙</div>
          <div className="empty-state__title">No blueprints yet</div>
          <div className="empty-state__sub">Start by describing your idea on the Home screen.</div>
          <button className="btn btn--primary mt-4" onClick={() => navigate('/')}>
            <Plus size={14} /> Create Blueprint
          </button>
        </div>
      ) : (
        <div className="gallery-grid">
          {filtered.map((bp, i) => (
            <motion.div
              key={bp.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
            >
              <Link to={`/blueprint/${bp.id}`} className="gallery-item" id={`gallery-item-${bp.id}`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div className="gallery-item__icon">{typeIcon[bp.idea_type] || '💡'}</div>
                    <div className="gallery-item__title">{bp.idea}</div>
                    <div className="gallery-item__meta">
                      <span className="badge badge--primary">{bp.idea_type || 'Idea'}</span>
                      <span>{bp.created_at ? new Date(bp.created_at).toLocaleDateString() : ''}</span>
                    </div>
                  </div>
                  <button
                    className="btn btn--ghost btn--sm"
                    style={{ padding: 8, marginLeft: 8, flexShrink: 0 }}
                    onClick={(e) => handleDelete(e, bp.id)}
                    id={`btn-delete-${bp.id}`}
                    title="Delete"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </PageWrapper>
  );
}
