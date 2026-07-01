import { useState, useCallback, useRef, useEffect } from 'react';
import {
  ArrowLeft,
  Archive,
  ArchiveRestore,
  Trash2,
  Bell,
  Tag,
  Clock,
  Check,
  Loader2,
  AlertCircle,
  Sparkles,
  Share2,
  Download,
  FileText,
  BookOpen,
} from 'lucide-react';
import { useStore } from '../../store';
import { BlockEditor } from '../editor/BlockEditor';
import { TagPicker } from '../tags/TagPicker';
import { ReminderPicker } from '../reminders/ReminderPicker';
import { AiPanel } from '../ai/AiPanel';
import { ShareModal } from '../sharing/ShareModal';
import { ExportImport } from './ExportImport';
import { ConfirmDialog } from '../ui/ConfirmDialog';
import { useToast } from '../ui/Toast';
import { formatDistanceToNow, format } from 'date-fns';

export function NoteEditor() {
  const {
    currentNote,
    saveStatus,
    updateNote,
    deleteNote,
    setCurrentNote,
    fetchNotes,
    setView,
  } = useStore();
  const { addToast } = useToast();

  const [title, setTitle] = useState(currentNote?.title || '');
  const [showTagPicker, setShowTagPicker] = useState(false);
  const [showReminderPicker, setShowReminderPicker] = useState(false);
  const [showAiPanel, setShowAiPanel] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  // Word count & reading time
  const wordCount = currentNote?.content
    ? stripHtml(currentNote.content).split(/\s+/).filter(Boolean).length
    : 0;
  const readingTime = Math.max(1, Math.ceil(wordCount / 200));

  // Update title state when note changes
  useEffect(() => {
    if (currentNote) {
      setTitle(currentNote.title);
    }
  }, [currentNote?.id]);

  const handleTitleChange = useCallback(
    (newTitle: string) => {
      setTitle(newTitle);
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        if (currentNote) {
          updateNote(currentNote.id, { title: newTitle });
        }
      }, 800);
    },
    [currentNote, updateNote],
  );

  const handleContentChange = useCallback(
    (content: string) => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        if (currentNote) {
          updateNote(currentNote.id, { content });
        }
      }, 800);
    },
    [currentNote, updateNote],
  );

  const handleBack = useCallback(() => {
    setCurrentNote(null);
    setView('notes');
    fetchNotes();
  }, [setCurrentNote, setView, fetchNotes]);

  const handleArchive = useCallback(async () => {
    if (currentNote) {
      await updateNote(currentNote.id, { archived: !currentNote.archived });
      addToast('success', currentNote.archived ? 'Note unarchived' : 'Note archived');
    }
  }, [currentNote, updateNote, addToast]);

  const handleDelete = useCallback(async () => {
    if (currentNote) {
      await deleteNote(currentNote.id);
      addToast('success', 'Note deleted');
      setView('notes');
      fetchNotes();
    }
    setShowDeleteConfirm(false);
  }, [currentNote, deleteNote, fetchNotes, setView, addToast]);

  if (!currentNote) return null;

  return (
    <div className="note-editor">
      {/* Header Bar */}
      <div className="note-editor-header">
        <button className="btn btn-ghost" onClick={handleBack} id="back-button">
          <ArrowLeft size={18} />
          Back
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          {/* Save Status */}
          <SaveIndicator status={saveStatus} />

          {/* AI Panel toggle */}
          <button
            className={`btn-icon ${showAiPanel ? 'active-accent' : ''}`}
            onClick={() => setShowAiPanel(!showAiPanel)}
            title="AI Assistant"
            id="ai-panel-toggle"
          >
            <Sparkles size={18} />
          </button>

          {/* Tag button */}
          <div style={{ position: 'relative' }}>
            <button
              className="btn-icon"
              onClick={() => setShowTagPicker(!showTagPicker)}
              title="Manage tags"
              id="tag-picker-toggle"
            >
              <Tag size={18} />
            </button>
            {showTagPicker && (
              <div style={{ position: 'absolute', right: 0, top: '100%', marginTop: 4, zIndex: 400 }}>
                <TagPicker
                  noteId={currentNote.id}
                  noteTags={currentNote.tags || []}
                  onClose={() => setShowTagPicker(false)}
                />
              </div>
            )}
          </div>

          {/* Reminder button */}
          <div style={{ position: 'relative' }}>
            <button
              className="btn-icon"
              onClick={() => setShowReminderPicker(!showReminderPicker)}
              title="Set reminder"
              id="reminder-picker-toggle"
            >
              <Bell size={18} />
            </button>
            {showReminderPicker && (
              <div style={{ position: 'absolute', right: 0, top: '100%', marginTop: 4, zIndex: 400 }}>
                <ReminderPicker
                  noteId={currentNote.id}
                  onClose={() => setShowReminderPicker(false)}
                />
              </div>
            )}
          </div>

          {/* Share */}
          <button
            className="btn-icon"
            onClick={() => setShowShareModal(true)}
            title="Share note"
            id="share-toggle"
          >
            <Share2 size={18} />
          </button>

          {/* Export */}
          <button
            className="btn-icon"
            onClick={() => setShowExport(true)}
            title="Export as Markdown"
            id="export-toggle"
          >
            <Download size={18} />
          </button>

          {/* Archive */}
          <button
            className="btn-icon"
            onClick={handleArchive}
            title={currentNote.archived ? 'Unarchive' : 'Archive'}
            id="archive-toggle"
          >
            {currentNote.archived ? <ArchiveRestore size={18} /> : <Archive size={18} />}
          </button>

          {/* Delete */}
          <button
            className="btn-icon"
            onClick={() => setShowDeleteConfirm(true)}
            title="Delete note"
            id="delete-note"
            style={{ color: 'var(--color-danger)' }}
          >
            <Trash2 size={18} />
          </button>
        </div>
      </div>

      {/* Meta info */}
      <div className="note-editor-meta">
        {currentNote.tags?.map((nt: any) => (
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
        {currentNote.reminders?.filter((r: any) => r.status === 'PENDING').map((r: any) => (
          <span key={r.id} className="note-card-reminder">
            <Bell size={12} />
            {format(new Date(r.remindAt), 'MMM d, h:mm a')}
          </span>
        ))}
        <span className="note-editor-stats">
          <BookOpen size={12} /> {wordCount} words · {readingTime} min read
        </span>
        <span style={{
          fontSize: 'var(--font-size-xs)',
          color: 'var(--color-text-tertiary)',
          marginLeft: 'auto',
        }}>
          <Clock size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
          Edited {formatDistanceToNow(new Date(currentNote.updatedAt), { addSuffix: true })}
        </span>
      </div>

      <div className="note-editor-body">
        {/* Main editor area */}
        <div className="note-editor-main">
          {/* Title */}
          <input
            className="note-editor-title"
            value={title}
            onChange={(e) => handleTitleChange(e.target.value)}
            placeholder="Untitled"
            id="note-title"
          />

          {/* Block Editor */}
          <div className="tiptap-editor" style={{ marginTop: 'var(--space-4)' }}>
            <BlockEditor
              content={currentNote.content}
              onUpdate={handleContentChange}
            />
          </div>
        </div>

        {/* AI Panel (side panel) */}
        {showAiPanel && (
          <AiPanel
            noteId={currentNote.id}
            noteContent={currentNote.content}
            onClose={() => setShowAiPanel(false)}
          />
        )}
      </div>

      {/* Modals */}
      {showShareModal && (
        <ShareModal
          noteId={currentNote.id}
          noteTitle={currentNote.title}
          onClose={() => setShowShareModal(false)}
        />
      )}

      {showExport && (
        <ExportImport
          noteId={currentNote.id}
          noteTitle={currentNote.title}
          onClose={() => setShowExport(false)}
          mode="export"
        />
      )}

      <ConfirmDialog
        open={showDeleteConfirm}
        title="Delete Note"
        message="Are you sure you want to delete this note? This action cannot be undone."
        confirmLabel="Delete"
        variant="danger"
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteConfirm(false)}
      />
    </div>
  );
}

function SaveIndicator({ status }: { status: string }) {
  if (status === 'idle') return null;

  return (
    <span className={`save-indicator ${status}`}>
      {status === 'saving' && (
        <>
          <Loader2 size={12} style={{ animation: 'spin 1s linear infinite' }} />
          Saving...
        </>
      )}
      {status === 'saved' && (
        <>
          <Check size={12} />
          Saved
        </>
      )}
      {status === 'error' && (
        <>
          <AlertCircle size={12} />
          Error
        </>
      )}
    </span>
  );
}

function stripHtml(html: string): string {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
}
