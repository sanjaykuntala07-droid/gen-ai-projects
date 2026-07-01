import { create } from 'zustand';
import { notesApi, tagsApi, remindersApi } from '../services/api';

interface Note {
  id: string;
  title: string;
  content: string;
  archived: boolean;
  createdAt: string;
  updatedAt: string;
  tags: { tag: { id: string; name: string; color: string } }[];
  reminders: any[];
}

interface Tag {
  id: string;
  name: string;
  color: string;
  _count?: { notes: number };
}

interface NotesState {
  notes: Note[];
  total: number;
  page: number;
  totalPages: number;
  currentNote: Note | null;
  tags: Tag[];
  upcomingReminders: any[];
  searchResults: any[];
  isLoading: boolean;
  isSaving: boolean;
  saveStatus: 'idle' | 'saving' | 'saved' | 'error';
  activeTagFilter: string | null;
  showArchived: boolean;
  theme: 'dark' | 'light';
  sidebarCollapsed: boolean;

  // Actions
  fetchNotes: () => Promise<void>;
  fetchNote: (id: string) => Promise<void>;
  view: 'dashboard' | 'notes' | 'editor';
  setView: (view: 'dashboard' | 'notes' | 'editor') => void;

  createNote: (title: string, content?: string) => Promise<Note>;
  updateNote: (id: string, data: Partial<Note>) => Promise<void>;
  deleteNote: (id: string) => Promise<void>;
  setCurrentNote: (note: Note | null) => void;

  fetchTags: () => Promise<void>;
  createTag: (name: string, color: string) => Promise<void>;
  deleteTag: (id: string) => Promise<void>;
  attachTag: (noteId: string, tagId: string) => Promise<void>;
  detachTag: (noteId: string, tagId: string) => Promise<void>;

  fetchUpcoming: () => Promise<void>;
  createReminder: (noteId: string, remindAt: string) => Promise<void>;
  deleteReminder: (id: string) => Promise<void>;

  searchNotes: (query: string) => Promise<void>;
  clearSearch: () => void;

  setTagFilter: (tagId: string | null) => void;
  setShowArchived: (show: boolean) => void;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setSaveStatus: (status: 'idle' | 'saving' | 'saved' | 'error') => void;
}

export const useStore = create<NotesState>((set, get) => ({
  notes: [],
  total: 0,
  page: 1,
  totalPages: 0,
  currentNote: null,
  tags: [],
  upcomingReminders: [],
  searchResults: [],
  isLoading: false,
  isSaving: false,
  saveStatus: 'idle',
  activeTagFilter: null,
  showArchived: false,
  theme: (localStorage.getItem('theme') as 'dark' | 'light') || 'dark',
  sidebarCollapsed: false,
  view: 'dashboard',

  setView: (view) => set({ view }),

  fetchNotes: async () => {
    set({ isLoading: true });
    try {
      const { activeTagFilter, showArchived } = get();
      const result = await notesApi.list({
        tagId: activeTagFilter || undefined,
        archived: showArchived,
      });
      set({
        notes: result.data,
        total: result.total,
        page: result.page,
        totalPages: result.totalPages,
      });
    } catch (error) {
      console.error('Failed to fetch notes:', error);
    } finally {
      set({ isLoading: false });
    }
  },

  fetchNote: async (id: string) => {
    try {
      const note = await notesApi.get(id);
      set({ currentNote: note });
    } catch (error) {
      console.error('Failed to fetch note:', error);
    }
  },

  createNote: async (title: string, content = '') => {
    const note = await notesApi.create({ title, content });
    set((state) => ({ notes: [note, ...state.notes], view: 'editor' }));
    return note;
  },

  updateNote: async (id: string, data: Partial<Note>) => {
    set({ saveStatus: 'saving' });
    try {
      const updated = await notesApi.update(id, data);
      set((state) => ({
        notes: state.notes.map((n) => (n.id === id ? updated : n)),
        currentNote: state.currentNote?.id === id ? updated : state.currentNote,
        saveStatus: 'saved',
      }));
      setTimeout(() => {
        if (get().saveStatus === 'saved') set({ saveStatus: 'idle' });
      }, 2000);
    } catch (error) {
      set({ saveStatus: 'error' });
      console.error('Failed to update note:', error);
    }
  },

  deleteNote: async (id: string) => {
    await notesApi.delete(id);
    set((state) => ({
      notes: state.notes.filter((n) => n.id !== id),
      currentNote: state.currentNote?.id === id ? null : state.currentNote,
    }));
  },

  setCurrentNote: (note) => set({ currentNote: note }),

  fetchTags: async () => {
    try {
      const tags = await tagsApi.list();
      set({ tags });
    } catch (error) {
      console.error('Failed to fetch tags:', error);
    }
  },

  createTag: async (name: string, color: string) => {
    const tag = await tagsApi.create({ name, color });
    set((state) => ({ tags: [...state.tags, tag] }));
  },

  deleteTag: async (id: string) => {
    await tagsApi.delete(id);
    set((state) => ({
      tags: state.tags.filter((t) => t.id !== id),
      activeTagFilter: state.activeTagFilter === id ? null : state.activeTagFilter,
    }));
  },

  attachTag: async (noteId: string, tagId: string) => {
    await tagsApi.attachToNote(noteId, tagId);
    await get().fetchNote(noteId);
  },

  detachTag: async (noteId: string, tagId: string) => {
    await tagsApi.detachFromNote(noteId, tagId);
    await get().fetchNote(noteId);
  },

  fetchUpcoming: async () => {
    try {
      const reminders = await remindersApi.upcoming();
      set({ upcomingReminders: reminders });
    } catch (error) {
      console.error('Failed to fetch reminders:', error);
    }
  },

  createReminder: async (noteId: string, remindAt: string) => {
    await remindersApi.create(noteId, { remindAt });
    await get().fetchUpcoming();
    if (get().currentNote?.id === noteId) {
      await get().fetchNote(noteId);
    }
  },

  deleteReminder: async (id: string) => {
    await remindersApi.delete(id);
    await get().fetchUpcoming();
  },

  searchNotes: async (query: string) => {
    if (!query.trim()) {
      set({ searchResults: [] });
      return;
    }
    try {
      const results = await notesApi.search(query);
      set({ searchResults: results });
    } catch (error) {
      console.error('Search failed:', error);
    }
  },

  clearSearch: () => set({ searchResults: [] }),

  setTagFilter: (tagId) => {
    set({ activeTagFilter: tagId });
    get().fetchNotes();
  },

  setShowArchived: (show) => {
    set({ showArchived: show });
    get().fetchNotes();
  },

  toggleTheme: () => {
    const newTheme = get().theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    set({ theme: newTheme });
  },

  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  setSaveStatus: (status) => set({ saveStatus: status }),
}));
