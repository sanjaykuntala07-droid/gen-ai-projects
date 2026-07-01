import { useState } from 'react';
import { FileText, Clock, Bell, Grid3X3, List, ArrowUpDown } from 'lucide-react';
import { useStore } from '../../store';
import { formatDistanceToNow } from 'date-fns';

type SortOption = 'updated' | 'created' | 'title';
type ViewMode = 'grid' | 'list';

export function NotesList() {
  const { notes, isLoading, showArchived, fetchNote, setCurrentNote } = useStore();
  const [sortBy, setSortBy] = useState<SortOption>('updated');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

  const sortedNotes = [...notes].sort((a: any, b: any) => {
    switch (sortBy) {
      case 'title':
        return (a.title || '').localeCompare(b.title || '');
      case 'created':
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
      case 'updated':
      default:
        return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
    }
  });

  if (isLoading) {
    return (
      <div className="notes-container">
        <div className="notes-header">
          <h2>{showArchived ? 'Archived Notes' : 'All Notes'}</h2>
        </div>
        <div className="notes-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton skeleton-card" />
          ))}
        </div>
      </div>
    );
  }

  if (notes.length === 0) {
    return (
      <div className="notes-container">
        <div className="empty-state">
          <FileText size={64} />
          <h3>
            {showArchived ? 'No archived notes' : 'No notes yet'}
          </h3>
          <p>
            {showArchived
              ? 'Archive notes you want to keep but hide from your main view.'
              : 'Start by typing in the quick-add bar above to create your first note.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="notes-container">
      <div className="notes-header">
        <h2>{showArchived ? 'Archived Notes' : 'All Notes'}</h2>
        <div className="notes-header-actions">
          <div className="sort-dropdown">
            <button className="btn btn-ghost sort-btn" id="sort-toggle">
              <ArrowUpDown size={14} />
              {sortBy === 'updated' ? 'Last edited' : sortBy === 'created' ? 'Created' : 'Title'}
            </button>
            <div className="sort-menu">
              <button
                className={`sort-option ${sortBy === 'updated' ? 'active' : ''}`}
                onClick={() => setSortBy('updated')}
              >
                Last edited
              </button>
              <button
                className={`sort-option ${sortBy === 'created' ? 'active' : ''}`}
                onClick={() => setSortBy('created')}
              >
                Created
              </button>
              <button
                className={`sort-option ${sortBy === 'title' ? 'active' : ''}`}
                onClick={() => setSortBy('title')}
              >
                Title
              </button>
            </div>
          </div>
          <div className="view-toggle">
            <button
              className={`btn-icon ${viewMode === 'grid' ? 'active-accent' : ''}`}
              onClick={() => setViewMode('grid')}
              title="Grid view"
            >
              <Grid3X3 size={16} />
            </button>
            <button
              className={`btn-icon ${viewMode === 'list' ? 'active-accent' : ''}`}
              onClick={() => setViewMode('list')}
              title="List view"
            >
              <List size={16} />
            </button>
          </div>
          <span className="notes-count">{notes.length} notes</span>
        </div>
      </div>
      <div className={`notes-grid ${viewMode === 'list' ? 'notes-list-view' : ''}`}>
        {sortedNotes.map((note: any, index: number) => (
          <div
            key={note.id}
            className="note-card note-card-animated"
            style={{ animationDelay: `${index * 50}ms` }}
            onClick={async () => {
              await fetchNote(note.id);
            }}
            id={`note-${note.id}`}
          >
            <div className="note-card-title">{note.title || 'Untitled'}</div>
            {note.content && viewMode === 'grid' && (
              <div className="note-card-content">
                {stripHtml(note.content)}
              </div>
            )}
            <div className="note-card-footer">
              {note.tags?.map((nt: any) => (
                <span
                  key={nt.tag.id}
                  className="tag-badge"
                  style={{
                    background: `${nt.tag.color}20`,
                    color: nt.tag.color,
                  }}
                >
                  <span
                    className="tag-dot"
                    style={{ background: nt.tag.color }}
                  />
                  {nt.tag.name}
                </span>
              ))}
              {note.reminders?.length > 0 && (
                <span className="note-card-reminder">
                  <Bell size={12} />
                  {formatDistanceToNow(new Date(note.reminders[0].remindAt), {
                    addSuffix: true,
                  })}
                </span>
              )}
              <span className="note-card-date">
                <Clock size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                {formatDistanceToNow(new Date(note.updatedAt), { addSuffix: true })}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function stripHtml(html: string): string {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
}
