import { useState, useRef, useEffect } from 'react';
import { X, Plus, Check } from 'lucide-react';
import { useStore } from '../../store';

const TAG_COLORS = [
  '#ef4444', '#f97316', '#eab308', '#22c55e',
  '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#6b7280',
];

interface TagPickerProps {
  noteId: string;
  noteTags: { tag: { id: string; name: string; color: string } }[];
  onClose: () => void;
}

export function TagPicker({ noteId, noteTags, onClose }: TagPickerProps) {
  const { tags, createTag, attachTag, detachTag } = useStore();
  const [search, setSearch] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [newColor, setNewColor] = useState(TAG_COLORS[0]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const noteTagIds = new Set(noteTags.map((nt: any) => nt.tag.id));
  const filteredTags = tags.filter((t: any) =>
    t.name.toLowerCase().includes(search.toLowerCase()),
  );
  const canCreate = search.trim() && !tags.some(
    (t: any) => t.name.toLowerCase() === search.toLowerCase(),
  );

  const handleToggleTag = async (tagId: string) => {
    if (noteTagIds.has(tagId)) {
      await detachTag(noteId, tagId);
    } else {
      await attachTag(noteId, tagId);
    }
  };

  const handleCreate = async () => {
    if (!search.trim()) return;
    await createTag(search.trim(), newColor);
    // Find newly created tag and attach
    const newTags = useStore.getState().tags;
    const newTag = newTags.find(
      (t: any) => t.name.toLowerCase() === search.toLowerCase(),
    );
    if (newTag) {
      await attachTag(noteId, newTag.id);
    }
    setSearch('');
    setIsCreating(false);
  };

  return (
    <div className="reminder-picker" style={{ minWidth: 240 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <span className="reminder-picker-title" style={{ margin: 0 }}>Tags</span>
        <button className="btn-icon" onClick={onClose} style={{ width: 24, height: 24 }}>
          <X size={14} />
        </button>
      </div>

      <input
        ref={inputRef}
        className="input"
        placeholder="Search or create tag..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && canCreate) handleCreate();
        }}
        style={{ marginBottom: 8 }}
      />

      <div style={{ maxHeight: 200, overflowY: 'auto' }}>
        {filteredTags.map((tag: any) => (
          <button
            key={tag.id}
            className="reminder-quick-option"
            onClick={() => handleToggleTag(tag.id)}
          >
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: tag.color,
                flexShrink: 0,
              }}
            />
            <span style={{ flex: 1, textAlign: 'left' }}>{tag.name}</span>
            {noteTagIds.has(tag.id) && (
              <Check size={14} style={{ color: 'var(--color-success)' }} />
            )}
          </button>
        ))}

        {canCreate && (
          <button
            className="reminder-quick-option"
            onClick={handleCreate}
            style={{ color: 'var(--color-accent)' }}
          >
            <Plus size={14} />
            <span>Create "{search.trim()}"</span>
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: newColor,
                cursor: 'pointer',
                marginLeft: 'auto',
              }}
              onClick={(e) => {
                e.stopPropagation();
                const idx = TAG_COLORS.indexOf(newColor);
                setNewColor(TAG_COLORS[(idx + 1) % TAG_COLORS.length]);
              }}
            />
          </button>
        )}
      </div>

      {filteredTags.length === 0 && !canCreate && (
        <div style={{
          padding: '12px',
          textAlign: 'center',
          fontSize: 'var(--font-size-sm)',
          color: 'var(--color-text-tertiary)',
        }}>
          No tags found
        </div>
      )}
    </div>
  );
}
