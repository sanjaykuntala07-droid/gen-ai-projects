import { useState, useRef, useCallback, useEffect } from 'react';
import { Search, Sun, Moon, Upload, User, LogOut, ChevronDown } from 'lucide-react';
import { useStore } from '../../store';
import { useAuth } from '../auth/AuthProvider';
import { ExportImport } from '../notes/ExportImport';

export function Header() {
  const { theme, toggleTheme, searchNotes, clearSearch, searchResults, setCurrentNote } = useStore();
  const { user, logout } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const handleSearch = useCallback(
    (value: string) => {
      setSearchQuery(value);
      if (debounceRef.current) clearTimeout(debounceRef.current);

      if (!value.trim()) {
        clearSearch();
        setShowResults(false);
        return;
      }

      debounceRef.current = setTimeout(() => {
        searchNotes(value);
        setShowResults(true);
      }, 300);
    },
    [searchNotes, clearSearch],
  );

  // Close search on click outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowResults(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setShowUserMenu(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Keyboard shortcut: Ctrl/Cmd + K
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        const input = searchRef.current?.querySelector('input');
        input?.focus();
      }
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const initials = user?.name
    ? user.name.split(' ').map((w) => w[0]).join('').toUpperCase().slice(0, 2)
    : '?';

  return (
    <header className="header">
      <div className="header-search" ref={searchRef}>
        <Search className="search-icon" size={16} />
        <input
          type="text"
          placeholder="Search notes..."
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          onFocus={() => searchQuery.trim() && setShowResults(true)}
          id="search-bar"
        />
        <span className="shortcut-hint">⌘K</span>

        {showResults && searchResults.length > 0 && (
          <div className="search-results">
            {searchResults.map((result: any) => (
              <div
                key={result.id}
                className="search-result-item"
                onClick={() => {
                  setCurrentNote(result);
                  setShowResults(false);
                  setSearchQuery('');
                  clearSearch();
                }}
              >
                <div className="search-result-title">{result.title}</div>
                {result.snippet && (
                  <div
                    className="search-result-snippet"
                    dangerouslySetInnerHTML={{ __html: result.snippet }}
                  />
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="header-actions">
        {/* Import */}
        <button
          className="btn-icon"
          onClick={() => setShowImport(true)}
          title="Import notes"
          id="import-toggle"
        >
          <Upload size={18} />
        </button>

        {/* Theme toggle */}
        <button
          className="theme-toggle"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          id="theme-toggle"
        >
          <div className="theme-toggle-icon">
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </div>
        </button>

        {/* User menu */}
        <div className="user-menu-container" ref={userMenuRef}>
          <button
            className="user-avatar-btn"
            onClick={() => setShowUserMenu(!showUserMenu)}
            id="user-menu-toggle"
          >
            <div className="user-avatar">{initials}</div>
            <ChevronDown size={14} />
          </button>
          {showUserMenu && (
            <div className="user-menu">
              <div className="user-menu-header">
                <div className="user-avatar" style={{ width: 36, height: 36, fontSize: 'var(--font-size-sm)' }}>
                  {initials}
                </div>
                <div>
                  <div className="user-menu-name">{user?.name}</div>
                  <div className="user-menu-email">{user?.email}</div>
                </div>
              </div>
              <div className="user-menu-divider" />
              <button className="user-menu-item" onClick={logout}>
                <LogOut size={14} />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Import modal */}
      {showImport && (
        <ExportImport onClose={() => setShowImport(false)} mode="import" />
      )}
    </header>
  );
}
