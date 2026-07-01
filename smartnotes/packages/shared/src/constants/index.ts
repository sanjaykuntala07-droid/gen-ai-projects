export const APP_NAME = 'SmartNotes';

export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

export const AUTOSAVE_DEBOUNCE_MS = 800;
export const SEARCH_DEBOUNCE_MS = 300;

export const REMINDER_QUICK_OPTIONS = [
  { label: 'In 1 hour', hours: 1 },
  { label: 'Tomorrow morning', hours: 0, preset: 'tomorrow_9am' },
  { label: 'Next week', hours: 0, preset: 'next_monday_9am' },
] as const;

export const TAG_COLORS = [
  '#ef4444', // red
  '#f97316', // orange
  '#eab308', // yellow
  '#22c55e', // green
  '#06b6d4', // cyan
  '#3b82f6', // blue
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#6b7280', // gray
] as const;
