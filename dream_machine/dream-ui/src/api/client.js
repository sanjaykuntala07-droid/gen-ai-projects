// Dream Machine — API Client
import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL || 
  (window.location.origin.startsWith('capacitor://') || (window.location.hostname === 'localhost' && !window.location.port)
    ? 'http://192.168.1.126:8000'
    : 'http://localhost:8000');

const api = axios.create({ baseURL: BASE, timeout: 60000 });

export const detectType = (idea) => api.post('/api/detect-type', { idea });
export const getQuestions = (idea, idea_type) => api.post('/api/questions', { idea, idea_type });
export const getBlueprints = (limit = 20) => api.get('/api/blueprints', { params: { limit } });
export const getBlueprint = (id) => api.get(`/api/blueprints/${id}`);
export const deleteBlueprint = (id) => api.delete(`/api/blueprints/${id}`);
export const getStats = () => api.get('/api/stats');
export const getIdeaTypes = () => api.get('/api/idea-types');
export const compareBlueprints = (a, b) => api.post('/api/compare', { blueprint_id_a: a, blueprint_id_b: b });

// Streaming generation — returns a ReadableStream
export async function generateStream(idea, idea_type, answers, user_name, onChunk) {
  const resp = await fetch(`${BASE}/api/generate/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ idea, idea_type, answers, user_name }),
  });

  if (!resp.ok) throw new Error(`API error ${resp.status}`);

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // keep incomplete line
    for (const line of lines) {
      if (line.trim()) {
        try {
          const msg = JSON.parse(line);
          onChunk(msg);
        } catch (e) { /* skip malformed */ }
      }
    }
  }
}

export default api;
