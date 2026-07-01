export interface Note {
  id: string;
  userId: string;
  title: string;
  content: string;
  archived: boolean;
  createdAt: string;
  updatedAt: string;
  tags?: Tag[];
  reminders?: Reminder[];
}

export interface CreateNoteDto {
  title: string;
  content?: string;
}

export interface UpdateNoteDto {
  title?: string;
  content?: string;
  archived?: boolean;
}

export interface NoteListQuery {
  page?: number;
  limit?: number;
  tagId?: string;
  archived?: boolean;
  search?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Re-export for convenience
import type { Tag } from './tag';
import type { Reminder } from './reminder';
