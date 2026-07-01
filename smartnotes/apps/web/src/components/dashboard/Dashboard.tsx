import { useEffect, useState } from 'react';
import {
  FileText,
  Tag,
  Bell,
  Archive,
  TrendingUp,
  Clock,
  Plus,
  Upload,
  Sparkles,
  Zap,
} from 'lucide-react';
import { useStore } from '../../store';
import { formatDistanceToNow } from 'date-fns';

interface Stats {
  totalNotes: number;
  totalTags: number;
  totalReminders: number;
  archivedNotes: number;
}

export function Dashboard() {
  const {
    notes,
    tags,
    upcomingReminders,
    setCurrentNote,
    createNote,
    setShowArchived,
  } = useStore();
  const [stats, setStats] = useState<Stats>({
    totalNotes: 0,
    totalTags: 0,
    totalReminders: 0,
    archivedNotes: 0,
  });

  useEffect(() => {
    // Compute stats from existing store data
    setStats({
      totalNotes: notes.length,
      totalTags: tags.length,
      totalReminders: upcomingReminders.length,
      archivedNotes: 0, // Will be fetched separately if needed
    });
  }, [notes, tags, upcomingReminders]);

  const recentNotes = notes.slice(0, 5);
  const tagDistribution = tags
    .map((t: any) => ({
      name: t.name,
      color: t.color,
      count: t._count?.notes || 0,
    }))
    .sort((a: any, b: any) => b.count - a.count)
    .slice(0, 8);

  const maxCount = Math.max(...tagDistribution.map((t: any) => t.count), 1);

  const handleQuickNote = async () => {
    try {
      const note = await createNote('Untitled Note');
      setCurrentNote(note);
    } catch (err) {
      console.error('Failed to create note:', err);
    }
  };

  return (
    <div className="dashboard">
      {/* Welcome Section */}
      <div className="dashboard-welcome">
        <div className="dashboard-welcome-text">
          <h1>
            <Zap size={28} className="dashboard-welcome-icon" />
            Welcome to SmartNotes
          </h1>
          <p>Your intelligent note-taking companion. Here's your workspace overview.</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="dashboard-stats">
        <div className="stat-card" id="stat-notes">
          <div className="stat-card-icon" style={{ background: 'var(--color-accent-soft)', color: 'var(--color-accent)' }}>
            <FileText size={20} />
          </div>
          <div className="stat-card-info">
            <span className="stat-card-value">{stats.totalNotes}</span>
            <span className="stat-card-label">Total Notes</span>
          </div>
        </div>
        <div className="stat-card" id="stat-tags">
          <div className="stat-card-icon" style={{ background: 'var(--color-success-soft)', color: 'var(--color-success)' }}>
            <Tag size={20} />
          </div>
          <div className="stat-card-info">
            <span className="stat-card-value">{stats.totalTags}</span>
            <span className="stat-card-label">Tags</span>
          </div>
        </div>
        <div className="stat-card" id="stat-reminders">
          <div className="stat-card-icon" style={{ background: 'var(--color-warning-soft)', color: 'var(--color-warning)' }}>
            <Bell size={20} />
          </div>
          <div className="stat-card-info">
            <span className="stat-card-value">{stats.totalReminders}</span>
            <span className="stat-card-label">Reminders</span>
          </div>
        </div>
        <div className="stat-card" id="stat-streak">
          <div className="stat-card-icon" style={{ background: 'hsla(280, 70%, 60%, 0.15)', color: 'hsl(280, 70%, 60%)' }}>
            <TrendingUp size={20} />
          </div>
          <div className="stat-card-info">
            <span className="stat-card-value">{notes.length > 0 ? '🔥' : '—'}</span>
            <span className="stat-card-label">Active</span>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Recent Activity */}
        <div className="dashboard-panel" id="recent-activity">
          <div className="dashboard-panel-header">
            <h3><Clock size={16} /> Recent Notes</h3>
          </div>
          <div className="dashboard-panel-body">
            {recentNotes.length === 0 ? (
              <div className="dashboard-empty">
                <FileText size={32} />
                <p>No notes yet. Create your first note!</p>
              </div>
            ) : (
              recentNotes.map((note: any) => (
                <div
                  key={note.id}
                  className="activity-item"
                  onClick={() => setCurrentNote(note)}
                >
                  <div className="activity-item-icon">
                    <FileText size={14} />
                  </div>
                  <div className="activity-item-content">
                    <span className="activity-item-title">{note.title || 'Untitled'}</span>
                    <span className="activity-item-time">
                      {formatDistanceToNow(new Date(note.updatedAt), { addSuffix: true })}
                    </span>
                  </div>
                  {note.tags?.length > 0 && (
                    <div className="activity-item-tags">
                      {note.tags.slice(0, 2).map((nt: any) => (
                        <span
                          key={nt.tag.id}
                          className="tag-dot-mini"
                          style={{ background: nt.tag.color }}
                          title={nt.tag.name}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Tag Distribution */}
        <div className="dashboard-panel" id="tag-distribution">
          <div className="dashboard-panel-header">
            <h3><Tag size={16} /> Tags Overview</h3>
          </div>
          <div className="dashboard-panel-body">
            {tagDistribution.length === 0 ? (
              <div className="dashboard-empty">
                <Tag size={32} />
                <p>No tags created yet.</p>
              </div>
            ) : (
              <div className="tag-chart">
                {tagDistribution.map((tag: any) => (
                  <div key={tag.name} className="tag-chart-row">
                    <span className="tag-chart-label">
                      <span className="tag-dot" style={{ background: tag.color, width: 8, height: 8, borderRadius: '50%', display: 'inline-block' }} />
                      {tag.name}
                    </span>
                    <div className="tag-chart-bar-container">
                      <div
                        className="tag-chart-bar"
                        style={{
                          width: `${(tag.count / maxCount) * 100}%`,
                          background: tag.color,
                        }}
                      />
                    </div>
                    <span className="tag-chart-count">{tag.count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="dashboard-actions">
        <button className="dashboard-action-btn" onClick={handleQuickNote} id="quick-new-note">
          <Plus size={18} />
          <span>New Note</span>
        </button>
        <button
          className="dashboard-action-btn"
          onClick={() => setShowArchived(true)}
          id="view-archived"
        >
          <Archive size={18} />
          <span>View Archive</span>
        </button>
        <button className="dashboard-action-btn" id="quick-ai">
          <Sparkles size={18} />
          <span>AI Assist</span>
        </button>
      </div>

      {/* Upcoming Reminders */}
      {upcomingReminders.length > 0 && (
        <div className="dashboard-panel dashboard-reminders" id="upcoming-reminders-panel">
          <div className="dashboard-panel-header">
            <h3><Bell size={16} /> Upcoming Reminders</h3>
          </div>
          <div className="dashboard-panel-body">
            {upcomingReminders.map((r: any) => (
              <div
                key={r.id}
                className="activity-item"
                onClick={() => r.note && setCurrentNote(r.note)}
              >
                <div className="activity-item-icon" style={{ color: 'var(--color-warning)' }}>
                  <Bell size={14} />
                </div>
                <div className="activity-item-content">
                  <span className="activity-item-title">{r.note?.title || 'Note'}</span>
                  <span className="activity-item-time">
                    {formatDistanceToNow(new Date(r.remindAt), { addSuffix: true })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
