import { useState, useCallback } from 'react';
import { Share2, Copy, Link, Check, X, Trash2, Eye, Edit3, Loader2 } from 'lucide-react';
import { useToast } from '../ui/Toast';

const API_BASE = '/api';

interface ShareModalProps {
  noteId: string;
  noteTitle: string;
  onClose: () => void;
}

interface ShareLink {
  id: string;
  shareToken: string;
  permission: 'VIEW' | 'EDIT';
  expiresAt: string | null;
  createdAt: string;
}

export function ShareModal({ noteId, noteTitle, onClose }: ShareModalProps) {
  const { addToast } = useToast();
  const [shares, setShares] = useState<ShareLink[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [permission, setPermission] = useState<'VIEW' | 'EDIT'>('VIEW');
  const [copied, setCopied] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  // Load existing shares
  const loadShares = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/notes/${noteId}/shares`);
      if (res.ok) {
        const data = await res.json();
        setShares(data);
      }
    } catch {
      // Shares endpoint may not exist yet — that's ok
    }
    setLoaded(true);
  }, [noteId]);

  useState(() => {
    loadShares();
  });

  const handleCreateShare = useCallback(async () => {
    setIsCreating(true);
    try {
      const res = await fetch(`${API_BASE}/notes/${noteId}/share`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ permission }),
      });
      if (res.ok) {
        const share = await res.json();
        setShares((prev) => [...prev, share]);
        addToast('success', 'Share link created!');
      } else {
        addToast('error', 'Failed to create share link');
      }
    } catch {
      addToast('error', 'Failed to create share link');
    } finally {
      setIsCreating(false);
    }
  }, [noteId, permission, addToast]);

  const handleRevokeShare = useCallback(async (shareId: string) => {
    try {
      await fetch(`${API_BASE}/notes/${noteId}/share/${shareId}`, { method: 'DELETE' });
      setShares((prev) => prev.filter((s) => s.id !== shareId));
      addToast('success', 'Share link revoked');
    } catch {
      addToast('error', 'Failed to revoke share link');
    }
  }, [noteId, addToast]);

  const handleCopyLink = useCallback((token: string) => {
    const url = `${window.location.origin}/shared/${token}`;
    navigator.clipboard.writeText(url);
    setCopied(token);
    addToast('success', 'Link copied to clipboard!');
    setTimeout(() => setCopied(null), 2000);
  }, [addToast]);

  return (
    <>
      <div className="modal-backdrop" onClick={onClose} />
      <div className="modal share-modal" id="share-modal">
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Share2 size={18} style={{ color: 'var(--color-accent)' }} />
            <h3>Share "{noteTitle}"</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {/* Create new share */}
          <div className="share-create">
            <div className="share-create-row">
              <div className="share-permission-toggle">
                <button
                  className={`share-perm-btn ${permission === 'VIEW' ? 'active' : ''}`}
                  onClick={() => setPermission('VIEW')}
                >
                  <Eye size={14} /> View only
                </button>
                <button
                  className={`share-perm-btn ${permission === 'EDIT' ? 'active' : ''}`}
                  onClick={() => setPermission('EDIT')}
                >
                  <Edit3 size={14} /> Can edit
                </button>
              </div>
              <button
                className="btn btn-primary"
                onClick={handleCreateShare}
                disabled={isCreating}
              >
                {isCreating ? (
                  <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
                ) : (
                  <>
                    <Link size={14} /> Create Link
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Existing shares */}
          {shares.length > 0 && (
            <div className="share-list">
              <div className="share-list-title">Active Links</div>
              {shares.map((share) => (
                <div key={share.id} className="share-item">
                  <div className="share-item-info">
                    <span className="share-item-perm">
                      {share.permission === 'VIEW' ? (
                        <><Eye size={12} /> View</>
                      ) : (
                        <><Edit3 size={12} /> Edit</>
                      )}
                    </span>
                    <span className="share-item-url">
                      {window.location.origin}/shared/{share.shareToken.slice(0, 8)}...
                    </span>
                  </div>
                  <div className="share-item-actions">
                    <button
                      className="btn-icon"
                      onClick={() => handleCopyLink(share.shareToken)}
                      title="Copy link"
                    >
                      {copied === share.shareToken ? <Check size={14} /> : <Copy size={14} />}
                    </button>
                    <button
                      className="btn-icon"
                      onClick={() => handleRevokeShare(share.id)}
                      title="Revoke"
                      style={{ color: 'var(--color-danger)' }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {shares.length === 0 && loaded && (
            <div className="share-empty">
              <Link size={24} />
              <p>No active share links. Create one to share this note.</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
