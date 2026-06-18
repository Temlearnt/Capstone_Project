const rawApiUrl =
  process.env.REACT_APP_API_URL ||
  '';

function normalizeApiUrl(url) {
  return (url || '').replace(/\/docs\/?$/, '').replace(/\/$/, '');
}

// In local development, empty API URL means same-origin.
// react-scripts will proxy /auth, /screen, /dashboard, etc. to Railway via package.json "proxy".
// This avoids browser CORS while developing on localhost:3000.
const API_URL = normalizeApiUrl(rawApiUrl);
const USE_MOCK_API = process.env.REACT_APP_USE_MOCK_API === 'true';
const TOKEN_KEY = 'recruitly_auth_token';
const USER_KEY = 'recruitly_auth_user';
export const AUTH_SESSION_ENDED_EVENT = 'recruitly:session-ended';

function notifySessionEnded() {
  window.dispatchEvent(new CustomEvent(AUTH_SESSION_ENDED_EVENT));
}

export function isMockApi() {
  return USE_MOCK_API;
}

export function getApiUrl() {
  return API_URL || 'same-origin proxy';
}

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function saveSession({ token, user }) {
  if (token) sessionStorage.setItem(TOKEN_KEY, token);
  if (user) sessionStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getSavedUser() {
  try {
    const user = sessionStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  } catch {
    return null;
  }
}

export function clearSession({ notify = false } = {}) {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
  if (notify) notifySessionEnded();
}

export async function apiRequest(path, options = {}) {
  if (USE_MOCK_API) {
    throw new Error('Mock API aktif. Set REACT_APP_USE_MOCK_API=false untuk memakai FastAPI.');
  }

  const token = getToken();
  const headers = new Headers(options.headers || {});

  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const url = `${API_URL}${path}`;
  const response = await fetch(url, {
    ...options,
    headers,
  });

  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      clearSession({ notify: true });
    }

    const message = payload?.message || payload?.error || payload?.detail || (typeof payload === 'string' && payload) || `Request ke backend gagal (${response.status}).`;
    const error = new Error(message);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }

  return payload;
}

export function normalizeUser(payload) {
  const user = payload?.user || payload;
  if (!user) return null;

  return {
    id: user.id || user.user_id || user.uid || user.email,
    name: user.name || user.full_name || user.user_metadata?.name || user.email?.split('@')[0] || 'User',
    full_name: user.full_name || user.name || user.user_metadata?.name || '',
    company_name: user.company_name || user.company || user.user_metadata?.company_name || '',
    email: user.email || '',
    role: user.role || '',
    phone: user.phone || user.phone_number || '',
    profilePhoto: user.profilePhoto || user.profile_photo || user.avatar_url || '',
  };
}

export function normalizeAuthPayload(payload) {
  const token = payload?.token || payload?.access_token || payload?.session?.access_token || payload?.data?.access_token;
  const user = normalizeUser(payload?.user || payload?.data?.user || payload?.session?.user || payload);
  return { token, user };
}
