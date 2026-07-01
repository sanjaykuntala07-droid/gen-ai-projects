import { useState, useRef, useCallback } from 'react';
import { Download, Upload, X, FileText, Check, Loader2 } from 'lucide-react';
import { useStore } from '../../store';
import { useToast } from '../ui/Toast';

interface ExportImportProps {
  noteId?: string;
  noteTitle?: string;
  onClose: () => void;
  mode: 'export' | 'import';
}

export function ExportImport({ noteId, noteTitle, onClose, mode }: ExportImportProps) {
  const { createNote, setCurrentNote, fetchNotes } = useStore();
  const { addToast } = useToast();
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [imported, setImported] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleExport = useCallback(async () => {
    if (!noteId) return;
    setIsProcessing(true);
    try {
      const res = await fetch(`/api/notes/${noteId}/export`);
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${(noteTitle || 'note').replace(/[^a-zA-Z0-9]/g, '_')}.md`;
        a.click();
        URL.revokeObjectURL(url);
        addToast('success', 'Note exported successfully!');
        onClose();
      } else {
        // Fallback: do client-side export
        const noteRes = await fetch(`/api/notes/${noteId}`);
        if (noteRes.ok) {
          const note = await noteRes.json();
          const content = htmlToMarkdown(note.content || '');
          const md = `# ${note.title}\n\n${content}`;
          const blob = new Blob([md], { type: 'text/markdown' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${(note.title || 'note').replace(/[^a-zA-Z0-9]/g, '_')}.md`;
          a.click();
          URL.revokeObjectURL(url);
          addToast('success', 'Note exported successfully!');
          onClose();
        }
      }
    } catch {
      addToast('error', 'Failed to export note');
    } finally {
      setIsProcessing(false);
    }
  }, [noteId, noteTitle, addToast, onClose]);

  const handleImport = useCallback(async () => {
    if (files.length === 0) return;
    setIsProcessing(true);
    let count = 0;

    for (const file of files) {
      try {
        const text = await file.text();
        // Extract title from first heading or filename
        let title = file.name.replace(/\.md$/i, '');
        const headingMatch = text.match(/^#\s+(.+)$/m);
        if (headingMatch) {
          title = headingMatch[1];
        }
        // Convert markdown to basic HTML for the editor
        const content = markdownToHtml(headingMatch ? text.replace(/^#\s+.+\n*/, '') : text);
        const note = await createNote(title, content);
        count++;
      } catch (err) {
        console.error('Failed to import file:', file.name, err);
      }
    }

    setImported(count);
    await fetchNotes();
    addToast('success', `Imported ${count} note${count > 1 ? 's' : ''} successfully!`);
    setIsProcessing(false);
  }, [files, createNote, fetchNotes, addToast]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      (f) => f.name.endsWith('.md') || f.name.endsWith('.txt'),
    );
    setFiles((prev) => [...prev, ...droppedFiles]);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles((prev) => [...prev, ...Array.from(e.target.files!)]);
    }
  }, []);

  if (mode === 'export') {
    return (
      <>
        <div className="modal-backdrop" onClick={onClose} />
        <div className="modal" id="export-modal" style={{ minWidth: 360 }}>
          <div className="modal-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Download size={18} style={{ color: 'var(--color-accent)' }} />
              <h3>Export Note</h3>
            </div>
            <button className="btn-icon" onClick={onClose}><X size={18} /></button>
          </div>
          <div className="modal-body">
            <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)', marginBottom: 'var(--space-4)' }}>
              Export "{noteTitle}" as a Markdown file.
            </p>
            <button
              className="btn btn-primary"
              style={{ width: '100%' }}
              onClick={handleExport}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
              ) : (
                <><Download size={16} /> Download as .md</>
              )}
            </button>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <div className="modal-backdrop" onClick={onClose} />
      <div className="modal" id="import-modal" style={{ minWidth: 420 }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Upload size={18} style={{ color: 'var(--color-accent)' }} />
            <h3>Import Notes</h3>
          </div>
          <button className="btn-icon" onClick={onClose}><X size={18} /></button>
        </div>
        <div className="modal-body">
          {imported > 0 ? (
            <div className="import-success">
              <Check size={40} style={{ color: 'var(--color-success)' }} />
              <h4>Imported {imported} note{imported > 1 ? 's' : ''}!</h4>
              <button className="btn btn-primary" onClick={onClose}>Done</button>
            </div>
          ) : (
            <>
              <div
                className={`import-dropzone ${isDragging ? 'dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload size={32} style={{ color: 'var(--color-accent)', opacity: 0.6 }} />
                <p>Drag & drop .md or .txt files here</p>
                <span>or click to browse</span>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".md,.txt,.markdown"
                  multiple
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
              </div>

              {files.length > 0 && (
                <div className="import-file-list">
                  {files.map((file, i) => (
                    <div key={i} className="import-file-item">
                      <FileText size={14} />
                      <span>{file.name}</span>
                      <button
                        className="btn-icon"
                        onClick={() => setFiles((prev) => prev.filter((_, j) => j !== i))}
                        style={{ width: 24, height: 24, marginLeft: 'auto' }}
                      >
                        <X size={12} />
                      </button>
                    </div>
                  ))}
                  <button
                    className="btn btn-primary"
                    style={{ width: '100%', marginTop: 'var(--space-3)' }}
                    onClick={handleImport}
                    disabled={isProcessing}
                  >
                    {isProcessing ? (
                      <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
                    ) : (
                      <><Upload size={16} /> Import {files.length} file{files.length > 1 ? 's' : ''}</>
                    )}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
}

// Simple HTML to Markdown conversion
function htmlToMarkdown(html: string): string {
  return html
    .replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n')
    .replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n')
    .replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n')
    .replace(/<strong[^>]*>(.*?)<\/strong>/gi, '**$1**')
    .replace(/<b[^>]*>(.*?)<\/b>/gi, '**$1**')
    .replace(/<em[^>]*>(.*?)<\/em>/gi, '*$1*')
    .replace(/<i[^>]*>(.*?)<\/i>/gi, '*$1*')
    .replace(/<s[^>]*>(.*?)<\/s>/gi, '~~$1~~')
    .replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`')
    .replace(/<blockquote[^>]*>(.*?)<\/blockquote>/gi, '> $1\n')
    .replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1\n')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&nbsp;/g, ' ')
    .trim();
}

// Simple Markdown to HTML conversion
function markdownToHtml(md: string): string {
  return md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/~~(.+?)~~/g, '<s>$1</s>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^> (.+)$/gm, '<blockquote><p>$1</p></blockquote>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`)
    .replace(/^(?!<[hubloi])((?!$).+)$/gm, '<p>$1</p>')
    .replace(/\n{2,}/g, '')
    .trim();
}
