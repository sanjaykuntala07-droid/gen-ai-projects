import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './components/auth/AuthProvider';
import { LoginPage } from './components/auth/LoginPage';
import { SignupPage } from './components/auth/SignupPage';
import { ToastProvider } from './components/ui/Toast';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { QuickAdd } from './components/notes/QuickAdd';
import { NotesList } from './components/notes/NotesList';
import { NoteEditor } from './components/notes/NoteEditor';
import { Dashboard } from './components/dashboard/Dashboard';
import { Onboarding } from './components/onboarding/Onboarding';
import { SharedView } from './components/sharing/SharedView';
import { useToast } from './components/ui/Toast';
import { useStore } from './store';

function AppContent() {
  const {
    currentNote,
    theme,
    view,
    fetchNotes,
    fetchTags,
    fetchUpcoming,
    createNote,
    setCurrentNote,
    setView,
  } = useStore();
  const { addToast } = useToast();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    fetchNotes();
    fetchTags();
    fetchUpcoming();
  }, []);

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleGlobalKeyDown = async (e: KeyboardEvent) => {
      // Create new note: Ctrl + Alt + N
      if ((e.ctrlKey || e.metaKey) && e.altKey && e.key.toLowerCase() === 'n') {
        e.preventDefault();
        try {
          const note = await createNote('Untitled Note');
          setCurrentNote(note);
          setView('editor');
          addToast('success', 'Created a new note');
        } catch (err) {
          console.error(err);
        }
      }

      // Save note: Ctrl + S
      if ((e.ctrlKey || e.metaKey) && !e.altKey && e.key.toLowerCase() === 's') {
        e.preventDefault();
        if (currentNote) {
          addToast('success', 'Note saved');
        }
      }
    };

    document.addEventListener('keydown', handleGlobalKeyDown);
    return () => document.removeEventListener('keydown', handleGlobalKeyDown);
  }, [currentNote, createNote, setCurrentNote, setView, addToast]);

  const showEditor = currentNote !== null;

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <Header />
        {showEditor ? (
          <NoteEditor />
        ) : view === 'dashboard' ? (
          <Dashboard />
        ) : (
          <>
            <QuickAdd />
            <NotesList />
          </>
        )}
      </div>
      <Onboarding />
    </div>
  );
}

function AuthGate() {
  const { isAuthenticated, isLoading } = useAuth();
  const [authView, setAuthView] = useState<'login' | 'signup'>('login');

  if (isLoading) {
    return (
      <div className="auth-loading">
        <div className="auth-loading-spinner" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return authView === 'login' ? (
      <LoginPage onSwitchToSignup={() => setAuthView('signup')} />
    ) : (
      <SignupPage onSwitchToLogin={() => setAuthView('login')} />
    );
  }

  return <AppContent />;
}

export function App() {
  const path = window.location.pathname;
  const sharedMatch = path.match(/^\/shared\/([^/]+)$/);

  if (sharedMatch) {
    const token = sharedMatch[1];
    return (
      <ToastProvider>
        <SharedView shareToken={token} />
      </ToastProvider>
    );
  }

  return (
    <AuthProvider>
      <ToastProvider>
        <AuthGate />
      </ToastProvider>
    </AuthProvider>
  );
}
