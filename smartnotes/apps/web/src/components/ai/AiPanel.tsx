import { useState, useCallback } from 'react';
import { Sparkles, FileText, Tag, Lightbulb, Wand2, X, Loader2, Check, Copy } from 'lucide-react';
import { useStore } from '../../store';
import { useToast } from '../ui/Toast';

const AI_BASE = '/api/ai';

async function aiRequest(endpoint: string, body: any) {
  const res = await fetch(`${AI_BASE}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: 'AI request failed' }));
    throw new Error(err.message || 'AI request failed');
  }
  return res.json();
}

interface AiPanelProps {
  noteId: string;
  noteContent: string;
  onInsertText?: (text: string) => void;
  onClose: () => void;
}

type AiAction = 'summarize' | 'suggest-tags' | 'suggestions' | 'improve';

export function AiPanel({ noteId, noteContent, onInsertText, onClose }: AiPanelProps) {
  const { attachTag, createTag, tags, fetchNote } = useStore();
  const { addToast } = useToast();
  const [activeAction, setActiveAction] = useState<AiAction | null>(null);
  const [result, setResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [displayedText, setDisplayedText] = useState('');

  const typewriterEffect = useCallback((text: string) => {
    setDisplayedText('');
    let i = 0;
    const interval = setInterval(() => {
      setDisplayedText(text.slice(0, i + 1));
      i++;
      if (i >= text.length) clearInterval(interval);
    }, 15);
    return () => clearInterval(interval);
  }, []);

  const handleAction = useCallback(async (action: AiAction) => {
    setActiveAction(action);
    setIsLoading(true);
    setResult(null);
    setDisplayedText('');

    try {
      const data = await aiRequest(`/${action}`, { noteId });
      setResult(data);

      if (action === 'summarize' && data.summary) {
        typewriterEffect(data.summary);
      } else if (action === 'improve' && data.improved) {
        typewriterEffect(data.improved);
      } else if (action === 'suggestions' && data.suggestions) {
        setDisplayedText(data.suggestions.join('\n'));
      }
    } catch (err: any) {
      addToast('error', err.message || 'AI request failed');
      setActiveAction(null);
    } finally {
      setIsLoading(false);
    }
  }, [noteId, typewriterEffect, addToast]);

  const handleAcceptTags = useCallback(async (suggestedTags: string[]) => {
    for (const tagName of suggestedTags) {
      const existing = tags.find((t: any) => t.name.toLowerCase() === tagName.toLowerCase());
      if (existing) {
        await attachTag(noteId, existing.id);
      } else {
        const colors = ['#3b82f6', '#8b5cf6', '#06b6d4', '#22c55e', '#f97316', '#ec4899'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        await createTag(tagName, color);
        const newTags = useStore.getState().tags;
        const newTag = newTags.find((t: any) => t.name.toLowerCase() === tagName.toLowerCase());
        if (newTag) {
          await attachTag(noteId, newTag.id);
        }
      }
    }
    await fetchNote(noteId);
    addToast('success', `Applied ${suggestedTags.length} tags`);
  }, [noteId, tags, attachTag, createTag, fetchNote, addToast]);

  const handleCopy = useCallback((text: string) => {
    navigator.clipboard.writeText(text);
    addToast('success', 'Copied to clipboard');
  }, [addToast]);

  const actions: { key: AiAction; icon: React.ReactNode; label: string; desc: string }[] = [
    { key: 'summarize', icon: <FileText size={16} />, label: 'Summarize', desc: 'Get a brief summary' },
    { key: 'suggest-tags', icon: <Tag size={16} />, label: 'Auto-Tag', desc: 'Suggest relevant tags' },
    { key: 'suggestions', icon: <Lightbulb size={16} />, label: 'Suggestions', desc: 'Smart ideas & actions' },
    { key: 'improve', icon: <Wand2 size={16} />, label: 'Improve', desc: 'Polish your writing' },
  ];

  return (
    <div className="ai-panel" id="ai-panel">
      <div className="ai-panel-header">
        <div className="ai-panel-title">
          <Sparkles size={16} className="ai-sparkle" />
          <span>AI Assistant</span>
        </div>
        <button className="btn-icon" onClick={onClose} style={{ width: 28, height: 28 }}>
          <X size={14} />
        </button>
      </div>

      {/* Action buttons */}
      {!activeAction && (
        <div className="ai-actions">
          {actions.map((action) => (
            <button
              key={action.key}
              className="ai-action-btn"
              onClick={() => handleAction(action.key)}
              disabled={!noteContent?.trim()}
            >
              <span className="ai-action-icon">{action.icon}</span>
              <span className="ai-action-text">
                <span>{action.label}</span>
                <span className="ai-action-desc">{action.desc}</span>
              </span>
            </button>
          ))}
          {!noteContent?.trim() && (
            <p className="ai-hint">Write some content in your note first to use AI features.</p>
          )}
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="ai-loading">
          <Loader2 size={20} className="ai-spinner" />
          <span>Thinking...</span>
        </div>
      )}

      {/* Results */}
      {activeAction && !isLoading && result && (
        <div className="ai-result">
          <div className="ai-result-header">
            <span>
              {activeAction === 'summarize' && '📝 Summary'}
              {activeAction === 'suggest-tags' && '🏷️ Suggested Tags'}
              {activeAction === 'suggestions' && '💡 Suggestions'}
              {activeAction === 'improve' && '✨ Improved Text'}
            </span>
            <button
              className="btn-icon"
              onClick={() => { setActiveAction(null); setResult(null); }}
              style={{ width: 24, height: 24 }}
              title="Back"
            >
              <X size={12} />
            </button>
          </div>

          {(activeAction === 'summarize' || activeAction === 'improve') && (
            <div className="ai-result-text">
              <p>{displayedText}<span className="ai-cursor" /></p>
              <div className="ai-result-actions">
                <button className="btn btn-ghost" onClick={() => handleCopy(displayedText)}>
                  <Copy size={14} /> Copy
                </button>
                {activeAction === 'improve' && onInsertText && (
                  <button className="btn btn-primary" onClick={() => { onInsertText(result.improved); onClose(); }}>
                    <Check size={14} /> Apply
                  </button>
                )}
              </div>
            </div>
          )}

          {activeAction === 'suggest-tags' && result.tags && (
            <div className="ai-result-tags">
              <div className="ai-tag-list">
                {result.tags.map((tag: string, i: number) => (
                  <span key={i} className="ai-tag-chip">{tag}</span>
                ))}
              </div>
              <button
                className="btn btn-primary"
                style={{ width: '100%', marginTop: 'var(--space-3)' }}
                onClick={() => { handleAcceptTags(result.tags); setActiveAction(null); }}
              >
                <Check size={14} /> Apply All Tags
              </button>
            </div>
          )}

          {activeAction === 'suggestions' && result.suggestions && (
            <div className="ai-result-suggestions">
              {result.suggestions.map((s: string, i: number) => (
                <div key={i} className="ai-suggestion-item">
                  <Lightbulb size={14} />
                  <span>{s}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
