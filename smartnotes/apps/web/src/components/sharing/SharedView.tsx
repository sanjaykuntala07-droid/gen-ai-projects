import { useState, useEffect, useCallback, useRef } from 'react';
import { Sparkles, Eye, Edit3, Loader2, Check, AlertCircle, Clock } from 'lucide-react';
import { BlockEditor } from '../editor/BlockEditor';
import { useToast } from '../ui/Toast';
import { formatDistanceToNow } from 'date-fns';

interface SharedViewProps {
  shareToken: string;
}

interface SharedNoteData {
  permission: 'VIEW' | 'EDIT';
  note: {
    id: string;
    title: string;
    content: string;
    updatedAt: string;
    tags: Array<{ tag: { id: string; name: string; color: string } }>;
  };
}

export function SharedView({ shareToken }: SharedViewProps) {
  const { addToast } = useToast();
  const [data, setData] = useState<SharedNoteData | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    async function fetchSharedNote() {
      try {
        const res = await fetch(`/api/shared/${shareToken}`);
        if (!res.ok) {
          const err = await res.json().catch(() => ({ message: 'Failed to load shared note' }));
          throw new Error(err.message || 'Failed to load shared note');
        }
        const noteData: SharedNoteData = await res.json();
        setData(noteData);
        setTitle(noteData.note.title);
        setContent(noteData.note.content);
      } catch (err: any) {
        setError(err.message || 'Shared note is invalid, expired, or does not exist.');
      } finally {
        setIsLoading(false);
      }
    }
    fetchSharedNote();
  }, [shareToken]);

  const saveSharedNote = useCallback(async (newTitle: string, newContent: string) => {
    setSaveStatus('saving');
    try {
      const res = await fetch(`/api/shared/${shareToken}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle, content: newContent }),
      });
      if (!res.ok) throw new Error('Save failed');
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch {
      setSaveStatus('error');
      addToast('error', 'Failed to save changes');
    }
  }, [shareToken, addToast]);

  const handleTitleChange = useCallback((newTitle: string) => {
    setTitle(newTitle);
    if (data?.permission !== 'EDIT') return;

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      saveSharedNote(newTitle, content);
    }, 800);
  }, [content, data, saveSharedNote]);

  const handleContentChange = useCallback((newContent: string) => {
    setContent(newContent);
    if (data?.permission !== 'EDIT') return;

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      saveSharedNote(title, newContent);
    }, 800);
  }, [title, data, saveSharedNote]);

  if (isLoading) {
    return (
      <div className="shared-layout loading-layout">
        <Loader2 size={32} className="ai-spinner" />
        <p>Loading shared note...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="shared-layout error-layout">
        <div className="error-card">
          <AlertCircle size={48} className="error-icon" />
          <h2>Unable to Access Note</h2>
          <p>{error || 'This link may have expired or been revoked.'}</p>
          <a href="/" className="btn btn-primary" style={{ marginTop: 'var(--space-4)' }}>
            Go to SmartNotes
          </a>
        </div>
      </div>
    );
  }

  const isEditable = data.permission === 'EDIT';

  return (
    <div className="shared-layout">
      <header className="shared-header">
        <div className="shared-logo">
          <Sparkles size={20} className="shared-logo-icon" />
          <span>SmartNotes Shared Note</span>
        </div>
        <div className="shared-header-actions">
          {saveStatus !== 'idle' && (
            <span className={`save-indicator ${saveStatus}`} style={{ marginRight: 'var(--space-2)' }}>
              {saveStatus === 'saving' && <Loader2 size={12} className="ai-spinner" />}
              {saveStatus === 'saved' && <Check size={12} />}
              {saveStatus === 'error' && <AlertCircle size={12} />}
              {saveStatus === 'saving' ? 'Saving...' : saveStatus === 'saved' ? 'Saved' : 'Error'}
            </span>
          )}
          <span className="permission-badge">
            {isEditable ? (
              <><Edit3 size={12} /> Collaborative Editor</>
            ) : (
              <><Eye size={12} /> View Only</>
            )}
          </span>
        </div>
      </header>

      <main className="shared-content-container">
        <div className="note-editor">
          {/* Note Meta */}
          <div className="note-editor-meta" style={{ borderBottom: '1px solid var(--color-border-light)', paddingBottom: 'var(--space-3)' }}>
            {data.note.tags?.map((nt: any) => (
              <span
                key={nt.tag.id}
                className="tag-badge"
                style={{
                  background: `${nt.tag.color}20`,
                  color: nt.tag.color,
                }}
              >
                <span className="tag-dot" style={{ background: nt.tag.color }} />
                {nt.tag.name}
              </span>
            ))}
            <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)', marginLeft: 'auto' }}>
              <Clock size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
              Last updated {formatDistanceToNow(new Date(data.note.updatedAt), { addSuffix: true })}
            </span>
          </div>

          {/* Title */}
          <input
            className="note-editor-title"
            value={title}
            onChange={(e) => handleTitleChange(e.target.value)}
            readOnly={!isEditable}
            placeholder="Untitled Note"
            style={{ border: 'none', background: 'transparent', outline: 'none' }}
          />

          {/* Editor */}
          <div className="tiptap-editor" style={{ marginTop: 'var(--space-4)' }}>
            <BlockEditor
              content={content}
              onUpdate={handleContentChange}
              editable={isEditable}
            />
          </div>
        </div>
      </main>

      <footer className="shared-footer">
        <p>Powered by <a href="/">SmartNotes</a> — Take notes, organize with tags, set reminders, work together.</p>
      </footer>
    </div>
  );
}
