import React, { useState } from 'react';
import { ArrowLeft, LogIn, UserPlus } from 'lucide-react';
import { loginUser, registerUser } from '../../services/authService';
import recruitlyLogo from '../../assets/recruitly-logo.png';
import './AuthPage.css';

export default function AuthPage({ onAuthSuccess, initialMode = 'login', onBackToLanding }) {
  const [mode, setMode] = useState(initialMode);
  const [form, setForm] = useState({ fullName: '', companyName: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const isLogin = mode === 'login';

  function handleChange(event) {
    setForm(prev => ({ ...prev, [event.target.name]: event.target.value }));
  }

  function switchMode(nextMode) {
    setMode(nextMode);
    setError('');
    setSuccess('');
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (isLogin) {
        const user = await loginUser(form);
        onAuthSuccess(user);
        return;
      }

      await registerUser(form);
      setMode('login');
      setSuccess('Registrasi berhasil. Silakan cek email jika verifikasi aktif, lalu login memakai akun yang baru dibuat.');
      setForm(prev => ({ ...prev, password: '' }));
    } catch (err) {
      setError(err.message || 'Terjadi kesalahan. Coba lagi.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        {onBackToLanding && (
          <button type="button" className="auth-back" onClick={onBackToLanding}>
            <ArrowLeft size={16} /> Kembali ke landing page
          </button>
        )}
        <div className="auth-brand">
          <img src={recruitlyLogo} alt="Recruitly" className="auth-logo-img" />
          <h1>Recruitly</h1>
          <p>Masuk untuk mengelola ranking kandidat.</p>
        </div>

        <div className="auth-tabs" role="tablist" aria-label="Auth tabs">
          <button
            type="button"
            className={isLogin ? 'active' : ''}
            onClick={() => switchMode('login')}
          >
            Login
          </button>
          <button
            type="button"
            className={!isLogin ? 'active' : ''}
            onClick={() => switchMode('register')}
          >
            Register
          </button>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {!isLogin && (
            <>
            <label>
              Nama Lengkap
              <input
                type="text"
                name="fullName"
                placeholder="Masukkan nama lengkap"
                value={form.fullName}
                onChange={handleChange}
                autoComplete="name"
              />
            </label>

            <label>
              Nama Company
              <input
                type="text"
                name="companyName"
                placeholder="Contoh: PT Recruitly Indonesia"
                value={form.companyName}
                onChange={handleChange}
                autoComplete="organization"
              />
            </label>
            </>
          )}

          <label>
            Email
            <input
              type="email"
              name="email"
              placeholder="nama@email.com"
              value={form.email}
              onChange={handleChange}
              autoComplete="email"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              name="password"
              placeholder="Minimal 6 karakter"
              value={form.password}
              onChange={handleChange}
              autoComplete={isLogin ? 'current-password' : 'new-password'}
            />
          </label>

          {success && <div className="auth-success">{success}</div>}
          {error && <div className="auth-error">{error}</div>}

          <button className="auth-submit" type="submit" disabled={loading}>
            {isLogin ? <LogIn size={16} /> : <UserPlus size={16} />}
            {loading ? 'Memproses...' : isLogin ? 'Login' : 'Register'}
          </button>
        </form>

        <p className="auth-note">
          Setelah register, akun tidak langsung masuk dashboard. Silakan login setelah registrasi berhasil atau setelah verifikasi email selesai.
        </p>
      </div>
    </div>
  );
}
