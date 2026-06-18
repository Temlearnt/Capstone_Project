import {
  apiRequest,
  clearSession,
  getSavedUser,
  getToken,
  isMockApi,
  normalizeAuthPayload,
  saveSession,
} from './apiClient';

const MOCK_USER_KEY = 'recruitly_mock_user';
const MOCK_REGISTERED_USER_KEY = 'recruitly_mock_registered_user';

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function createMockUser({ fullName, companyName, email }) {
  return {
    id: email,
    name: fullName || email.split('@')[0],
    full_name: fullName || email.split('@')[0],
    company_name: companyName || 'Demo Company',
    email,
  };
}

export async function getCurrentUser() {
  if (isMockApi()) {
    try {
      const saved = sessionStorage.getItem(MOCK_USER_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  }

  const savedUser = getSavedUser();
  if (!savedUser) return null;

  try {
    const token = getToken();
    const payload = await apiRequest(token ? `/auth/me?token=${encodeURIComponent(token)}` : '/auth/me');
    const { user } = normalizeAuthPayload(payload);
    return user || savedUser;
  } catch {
    return savedUser;
  }
}

export async function registerUser({ fullName, companyName, email, password }) {
  const cleanFullName = fullName.trim();
  const cleanCompanyName = companyName.trim();
  const cleanEmail = email.trim().toLowerCase();
  const cleanPassword = password.trim();

  if (!cleanFullName || !cleanCompanyName || !cleanEmail || !cleanPassword) {
    throw new Error('Nama lengkap, nama company, email, dan password wajib diisi.');
  }

  if (!validateEmail(cleanEmail)) {
    throw new Error('Format email tidak valid.');
  }

  if (cleanPassword.length < 6) {
    throw new Error('Password minimal 6 karakter.');
  }

  if (isMockApi()) {
    const user = createMockUser({ fullName: cleanFullName, companyName: cleanCompanyName, email: cleanEmail });
    localStorage.setItem(MOCK_REGISTERED_USER_KEY, JSON.stringify(user));
    return { user, requiresLogin: true };
  }

  const payload = await apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      email: cleanEmail,
      password: cleanPassword,
      full_name: cleanFullName,
      company_name: cleanCompanyName,
    }),
  });

  const { user } = normalizeAuthPayload(payload);
  return user || payload;
}

export async function loginUser({ email, password }) {
  const cleanEmail = email.trim().toLowerCase();
  const cleanPassword = password.trim();

  if (!cleanEmail || !cleanPassword) {
    throw new Error('Email dan password wajib diisi.');
  }

  if (isMockApi()) {
    let user = null;
    try {
      const registeredUser = localStorage.getItem(MOCK_REGISTERED_USER_KEY);
      user = registeredUser ? JSON.parse(registeredUser) : null;
    } catch {
      user = null;
    }

    if (!user || user.email !== cleanEmail) {
      user = createMockUser({ email: cleanEmail });
    }

    sessionStorage.setItem(MOCK_USER_KEY, JSON.stringify(user));
    return user;
  }

  // Swagger backend menunjukkan /auth/login menerima application/json:
  // { "email": "...", "password": "..." }
  const payload = await apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({
      email: cleanEmail,
      password: cleanPassword,
    }),
  });

  const { token, user } = normalizeAuthPayload(payload);
  if (token || user) saveSession({ token, user });
  return user || payload;
}

export async function logoutUser() {
  if (!isMockApi()) {
    try {
      await apiRequest('/auth/logout', { method: 'POST' });
    } catch {
      // Tetap hapus sesi frontend meski backend logout gagal.
    }
  }

  expireLocalSession();
}

export function expireLocalSession({ notify = false } = {}) {
  clearSession({ notify });
  sessionStorage.removeItem(MOCK_USER_KEY);
}

export function onAuthStateChange() {
  return { data: { authListener: null, subscription: { unsubscribe() {} } } };
}
