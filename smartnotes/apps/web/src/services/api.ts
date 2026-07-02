const isCapacitor = (window as any).Capacitor !== undefined || window.location.protocol.startsWith('capacitor') || window.location.origin.includes('localhost') && !window.location.port;

// In production, we want to use the absolute URL provided by Render
// We check window.location to see if we're on Render
const isRender = window.location.hostname.includes('onrender.com');
const RENDER_API_URL = 'https://smartnotes-api.onrender.com/api'; // We will use this as a fallback

const API_BASE = isRender ? RENDER_API_URL : (isCapacitor ? 'http://192.168.1.126:3000/api' : '/api');

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(error.message || `Request failed: ${res.status}`);
  }

  // Handle 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json();
}

// Notes API
export const notesApi = {
  list: (params?: { page?: number; limit?: number; tagId?: string; archived?: boolean }) => {
    const query = new URLSearchParams();
    if (params?.page) query.set('page', String(params.page));
    if (params?.limit) query.set('limit', String(params.limit));
    if (params?.tagId) query.set('tagId', params.tagId);
    if (params?.archived !== undefined) query.set('archived', String(params.archived));
    const qs = query.toString();
    return request<any>(`/notes${qs ? `?${qs}` : ''}`);
  },
  get: (id: string) => request<any>(`/notes/${id}`),
  create: (data: { title: string; content?: string }) =>
    request<any>('/notes', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: { title?: string; content?: string; archived?: boolean }) =>
    request<any>(`/notes/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<void>(`/notes/${id}`, { method: 'DELETE' }),
  search: (q: string, limit = 20) =>
    request<any[]>(`/notes/search?q=${encodeURIComponent(q)}&limit=${limit}`),
};

// Tags API
export const tagsApi = {
  list: () => request<any[]>('/tags'),
  create: (data: { name: string; color: string }) =>
    request<any>('/tags', { method: 'POST', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<void>(`/tags/${id}`, { method: 'DELETE' }),
  attachToNote: (noteId: string, tagId: string) =>
    request<any>(`/tags/${noteId}/tags/${tagId}`, { method: 'POST' }),
  detachFromNote: (noteId: string, tagId: string) =>
    request<void>(`/tags/${noteId}/tags/${tagId}`, { method: 'DELETE' }),
};

// Reminders API
export const remindersApi = {
  create: (noteId: string, data: { remindAt: string; deliveryChannel?: string }) =>
    request<any>(`/notes/${noteId}/reminders`, { method: 'POST', body: JSON.stringify(data) }),
  upcoming: (limit = 5) =>
    request<any[]>(`/reminders/upcoming?limit=${limit}`),
  delete: (id: string) =>
    request<void>(`/reminders/${id}`, { method: 'DELETE' }),
};
