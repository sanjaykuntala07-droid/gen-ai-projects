import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Trash2, BookOpen, Edit3 } from 'lucide-react';
import PageWrapper from '../components/PageWrapper.jsx';

const STORAGE_KEY = 'dm_notebook';

function loadNotes() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
  catch { return []; }
}

function saveNotes(notes) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
}

export default function Notebook() {
  const [notes, setNotes]     = useState(loadNotes);
  const [editing, setEditing] = useState(null); // null | index | 'new'
  const [text, setText]       = useState('');
  const [title, setTitle]     = useState('');

  const persist = (updated) => { setNotes(updated); saveNotes(updated); };

  const openNew = () => { setTitle(''); setText(''); setEditing('new'); };
  const openEdit = (i) => { setTitle(notes[i].title); setText(notes[i].text); setEditing(i); };

  const handleSave = () => {
    if (!text.trim()) return;
    const note = { id: Date.now(), title: title.trim() || 'Untitled', text: text.trim(), date: new Date().toISOString() };
    if (editing === 'new') {
      persist([note, ...notes]);
    } else {
      const updated = [...notes];
      updated[editing] = { ...updated[editing], ...note };
      persist(updated);
    }
    setEditing(null);
  };

  const handleDelete = (i) => {
    if (!window.confirm('Delete note?')) return;
    const updated = notes.filter((_, idx) => idx !== i);
    persist(updated);
  };

  return (
    <PageWrapper>
      <div className="flex items-center justify-between mb-4">
        <h1 className="page-heading" style={{ fontSize: '1.4rem', margin: 0 }}>Notebook</h1>
        <button className="btn btn--primary btn--sm" onClick={openNew} id="btn-new-note">
          <Plus size={14} /> Note
        </button>
      </div>

      {/* Editor */}
      <AnimatePresence>
        {editing !== null && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="glass-card glass-card--gradient mb-4"
          >
            <input
              className="input"
              placeholder="Note title…"
              value={title}
              onChange={e => setTitle(e.target.value)}
              style={{ marginBottom: 10 }}
            />
            <textarea
              className="input"
              placeholder="Write your idea, insight, or strategy here…"
              value={text}
              onChange={e => setText(e.target.value)}
              rows={5}
              style={{ marginBottom: 10 }}
            />
            <div className="flex gap-2">
              <button className="btn btn--primary btn--sm" onClick={handleSave} id="btn-save-note">Save</button>
              <button className="btn btn--ghost btn--sm" onClick={() => setEditing(null)} id="btn-cancel-note">Cancel</button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Notes list */}
      {notes.length === 0 ? (
        <div className="empty-state">
          <BookOpen size={36} style={{ opacity: 0.3 }} />
          <div className="empty-state__title">Your notebook is empty</div>
          <div className="empty-state__sub">Jot down ideas, strategies, or observations as you build.</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {notes.map((note, i) => (
            <motion.div
              key={note.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
              className="glass-card"
              style={{ padding: 16 }}
            >
              <div className="flex items-center justify-between mb-2">
                <div style={{ fontFamily: 'var(--f-display)', fontSize: '0.9rem', fontWeight: 700, color: 'var(--c-text)' }}>{note.title}</div>
                <div className="flex gap-2">
                  <button className="btn btn--ghost btn--sm" style={{ padding: 6 }} onClick={() => openEdit(i)} id={`btn-edit-note-${i}`}><Edit3 size={12} /></button>
                  <button className="btn btn--ghost btn--sm" style={{ padding: 6 }} onClick={() => handleDelete(i)} id={`btn-del-note-${i}`}><Trash2 size={12} /></button>
                </div>
              </div>
              <p style={{ fontSize: '0.84rem', color: 'var(--c-text-2)', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                {note.text.length > 200 ? note.text.slice(0, 200) + '…' : note.text}
              </p>
              <div style={{ fontSize: '0.7rem', color: 'var(--c-muted)', marginTop: 8 }}>
                {new Date(note.date).toLocaleDateString()}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </PageWrapper>
  );
}
