import {
  FileText,
  Archive,
  Bell,
  Tag,
  Settings,
  ChevronLeft,
  Zap,
  LayoutDashboard,
} from 'lucide-react';
import { useStore } from '../../store';
import { useAuth } from '../auth/AuthProvider';

export function Sidebar() {
  const {
    tags,
    upcomingReminders,
    sidebarCollapsed,
    showArchived,
    activeTagFilter,
    notes,
    view,
    toggleSidebar,
    setShowArchived,
    setTagFilter,
    setCurrentNote,
    setView,
  } = useStore();
  const { user } = useAuth();

  return (
    <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
      {/* Logo */}
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Zap size={22} />
          {!sidebarCollapsed && <span>SmartNotes</span>}
        </div>
        <button
          className="btn-icon"
          onClick={toggleSidebar}
          title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          style={{ marginLeft: 'auto' }}
        >
          <ChevronLeft
            size={18}
            style={{
              transform: sidebarCollapsed ? 'rotate(180deg)' : 'none',
              transition: 'transform 0.25s ease',
            }}
          />
        </button>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {/* Dashboard */}
        <div className="sidebar-section">
          {!sidebarCollapsed && (
            <div className="sidebar-section-title">Overview</div>
          )}
          <button
            className={`sidebar-item ${view === 'dashboard' && !showArchived ? 'active' : ''}`}
            onClick={() => {
              setCurrentNote(null);
              setView('dashboard');
              setShowArchived(false);
              setTagFilter(null);
            }}
          >
            <LayoutDashboard size={18} />
            {!sidebarCollapsed && <span>Dashboard</span>}
          </button>
        </div>

        {/* Notes */}
        <div className="sidebar-section">
          {!sidebarCollapsed && (
            <div className="sidebar-section-title">Notes</div>
          )}
          <button
            className={`sidebar-item ${view === 'notes' && !showArchived && !activeTagFilter ? 'active' : ''}`}
            onClick={() => {
              setShowArchived(false);
              setTagFilter(null);
              setCurrentNote(null);
              setView('notes');
            }}
          >
            <FileText size={18} />
            {!sidebarCollapsed && (
              <>
                <span>All Notes</span>
                <span className="count">{notes.length}</span>
              </>
            )}
          </button>
          <button
            className={`sidebar-item ${showArchived ? 'active' : ''}`}
            onClick={() => {
              setShowArchived(true);
              setCurrentNote(null);
              setView('notes');
            }}
          >
            <Archive size={18} />
            {!sidebarCollapsed && <span>Archive</span>}
          </button>
        </div>

        {/* Reminders */}
        <div className="sidebar-section">
          {!sidebarCollapsed && (
            <div className="sidebar-section-title">Reminders</div>
          )}
          <button className="sidebar-item">
            <Bell size={18} />
            {!sidebarCollapsed && (
              <>
                <span>Upcoming</span>
                {upcomingReminders.length > 0 && (
                  <span className="count">{upcomingReminders.length}</span>
                )}
              </>
            )}
          </button>
        </div>

        {/* Tags */}
        {!sidebarCollapsed && tags.length > 0 && (
          <div className="sidebar-section">
            <div className="sidebar-section-title">Tags</div>
            <div className="tag-filter">
              {tags.map((tag: any) => (
                <button
                  key={tag.id}
                  className={`tag-filter-item ${activeTagFilter === tag.id ? 'active' : ''}`}
                  onClick={() => {
                    setTagFilter(activeTagFilter === tag.id ? null : tag.id);
                    setCurrentNote(null);
                    setView('notes');
                  }}
                >
                  <span
                    className="tag-dot"
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: tag.color,
                      flexShrink: 0,
                    }}
                  />
                  <span>{tag.name}</span>
                  {tag._count?.notes > 0 && (
                    <span className="count">{tag._count.notes}</span>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* Footer — User Info */}
      {!sidebarCollapsed && (
        <div className="sidebar-footer">
          {user && (
            <div className="sidebar-user">
              <div className="sidebar-user-avatar">
                {user.name.split(' ').map((w) => w[0]).join('').toUpperCase().slice(0, 2)}
              </div>
              <div className="sidebar-user-info">
                <span className="sidebar-user-name">{user.name}</span>
                <span className="sidebar-user-email">{user.email}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </aside>
  );
}
