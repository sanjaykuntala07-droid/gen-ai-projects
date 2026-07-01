import { useState, useCallback } from 'react';
import { Plus } from 'lucide-react';
import { useStore } from '../../store';

export function QuickAdd() {
  const [title, setTitle] = useState('');
  const { createNote, setCurrentNote } = useStore();

  const handleSubmit = useCallback(
    async (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter' && title.trim()) {
        e.preventDefault();
        try {
          const note = await createNote(title.trim());
          setTitle('');
          // Open the newly created note for editing
          setCurrentNote(note);
        } catch (error) {
          console.error('Failed to create note:', error);
        }
      }
    },
    [title, createNote, setCurrentNote],
  );

  return (
    <div className="quick-add">
      <div className="quick-add-input">
        <Plus size={20} />
        <input
          type="text"
          placeholder="Quick add a new note..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={handleSubmit}
          id="quick-add-input"
        />
        <span className="hint">Press Enter</span>
      </div>
    </div>
  );
}
