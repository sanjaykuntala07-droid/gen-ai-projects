import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart2, Zap, FileText, Users, TrendingUp } from 'lucide-react';
import PageWrapper from '../components/PageWrapper.jsx';
import { getStats, getBlueprints } from '../api/client.js';

function StatCard({ icon: Icon, value, label, color = 'var(--c-primary)' }) {
  return (
    <div className="glass-card" style={{ padding: '18px', textAlign: 'center' }}>
      <div style={{ width: 40, height: 40, borderRadius: 12, background: `rgba(${color},0.12)`, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 10px', border: `1px solid rgba(${color},0.25)` }}>
        <Icon size={18} style={{ color }} />
      </div>
      <div className="stat-block__value">{value ?? '—'}</div>
      <div className="stat-block__label">{label}</div>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats]     = useState(null);
  const [recent, setRecent]   = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getStats(), getBlueprints(5)]).then(([s, b]) => {
      setStats(s.data);
      setRecent(b.data.blueprints || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return (
    <PageWrapper>
      <div className="gen-container" style={{ paddingTop: 60 }}>
        <div className="spinner" />
      </div>
    </PageWrapper>
  );

  const typeCount = {};
  recent.forEach(b => { typeCount[b.idea_type] = (typeCount[b.idea_type] || 0) + 1; });

  return (
    <PageWrapper>
      <h1 className="page-heading">Dashboard</h1>
      <p className="page-sub">Your innovation at a glance.</p>

      {/* Stats Grid */}
      <div className="stats-row" style={{ gridTemplateColumns: 'repeat(2,1fr)', marginBottom: 24 }}>
        <StatCard icon={FileText} value={stats?.total_blueprints} label="Blueprints" color="108,99,255" />
        <StatCard icon={Users}    value={stats?.total_users}      label="Users"      color="0,245,212" />
        <StatCard icon={Zap}      value={stats?.total_sections}   label="Sections"   color="255,184,0" />
        <StatCard icon={TrendingUp} value={recent.length}         label="Recent"     color="108,99,255" />
      </div>

      {/* Recent blueprints */}
      <div style={{ marginBottom: 12 }}>
        <h2 style={{ fontFamily: 'var(--f-display)', fontSize: '0.95rem', fontWeight: 700, marginBottom: 12, color: 'var(--c-text)' }}>
          Recent Blueprints
        </h2>
        {recent.length === 0 ? (
          <div className="empty-state" style={{ padding: 24 }}>
            <div className="empty-state__icon">🌙</div>
            <div className="empty-state__sub">No blueprints yet. Create your first!</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {recent.map((bp, i) => (
              <motion.div
                key={bp.id}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="glass-card"
                style={{ padding: '14px 16px' }}
              >
                <div className="flex items-center gap-3">
                  <div style={{ fontSize: '1.4rem' }}>💡</div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--c-text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {bp.idea}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--c-muted)', marginTop: 2 }}>
                      {bp.idea_type} · {bp.created_at ? new Date(bp.created_at).toLocaleDateString() : ''}
                    </div>
                  </div>
                  <span className="badge badge--primary" style={{ flexShrink: 0 }}>View</span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Idea Type breakdown */}
      {Object.keys(typeCount).length > 0 && (
        <div>
          <h2 style={{ fontFamily: 'var(--f-display)', fontSize: '0.95rem', fontWeight: 700, marginBottom: 12, color: 'var(--c-text)' }}>
            Idea Types
          </h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {Object.entries(typeCount).map(([type, count]) => (
              <div key={type} className="chip">
                {type} <span style={{ background: 'var(--c-primary)', color: '#fff', borderRadius: 99, padding: '1px 7px', fontSize: '0.7rem', marginLeft: 4 }}>{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </PageWrapper>
  );
}
