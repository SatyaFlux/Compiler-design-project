const API_BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data.error || (data.errors && data.errors[0]?.message) || `Request failed (${res.status})`;
    const err = new Error(msg);
    err.data = data;
    throw err;
  }
  return data;
}

export const api = {
  health: () => request('/health'),

  // Dashboard & Experiments
  getDashboardStats: () => request('/dashboard/stats'),
  markProgress: (module_key, completed = true) =>
    request('/progress', { method: 'POST', body: JSON.stringify({ module_key, completed }) }),
  listExperiments: () => request('/experiments'),
  saveExperiment: (payload) =>
    request('/experiments', { method: 'POST', body: JSON.stringify(payload) }),
  deleteExperiment: (id) =>
    request(`/experiments/${id}`, { method: 'DELETE' }),

  // Grammar & LL(1)
  getGrammarPresets: () => request('/grammar/presets'),
  validateGrammar: (grammar_text) =>
    request('/grammar/validate', { method: 'POST', body: JSON.stringify({ grammar_text }) }),
  getFirstFollow: (grammar_text) =>
    request('/grammar/first-follow', { method: 'POST', body: JSON.stringify({ grammar_text }) }),
  getLL1Table: (grammar_text) =>
    request('/grammar/ll1-table', { method: 'POST', body: JSON.stringify({ grammar_text }) }),
  simulateLL1: (grammar_text, input_string) =>
    request('/grammar/ll1-parse', { method: 'POST', body: JSON.stringify({ grammar_text, input_string }) }),

  // Compiler Pipeline
  tokenize: (source_code) =>
    request('/lexer/tokenize', { method: 'POST', body: JSON.stringify({ source_code }) }),
  parseCode: (source_code) =>
    request('/compiler/parse', { method: 'POST', body: JSON.stringify({ source_code }) }),
  semanticCheck: (source_code, strict_declarations = false) =>
    request('/compiler/semantic', { method: 'POST', body: JSON.stringify({ source_code, strict_declarations }) }),
  generateTAC: (source_code) =>
    request('/compiler/tac', { method: 'POST', body: JSON.stringify({ source_code }) }),
  optimizeTAC: (source_code) =>
    request('/compiler/optimize', { method: 'POST', body: JSON.stringify({ source_code }) }),
  executeCode: (source_code) =>
    request('/compiler/execute', { method: 'POST', body: JSON.stringify({ source_code }) }),
  runAll: (source_code, strict_declarations = false) =>
    request('/compiler/run-all', { method: 'POST', body: JSON.stringify({ source_code, strict_declarations }) }),

  // Error Simulator & Quiz
  getErrorPresets: () => request('/errors/presets'),
  getQuizQuestions: (topic = 'All') =>
    request(`/quiz/questions?topic=${encodeURIComponent(topic)}`),
  submitQuiz: (topic, answers) =>
    request('/quiz/submit', { method: 'POST', body: JSON.stringify({ topic, answers }) }),
  getQuizHistory: () => request('/quiz/history'),
};
