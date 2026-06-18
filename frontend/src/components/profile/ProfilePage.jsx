import React, { useState } from 'react';
import { saveSession, isMockApi } from '../../services/apiClient';
import './ProfilePage.css';

const MOCK_USER_KEY = 'recruitly_mock_user';
const MOCK_REGISTERED_USER_KEY = 'recruitly_mock_registered_user';

export default function ProfilePage({ user, onUserUpdate }) {
  const [form, setForm] = useState({
    name: user?.name || user?.full_name || '',
    company_name: user?.company_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    role: user?.role || 'HR Recruiter',
  });
  const [saved, setSaved] = useState(false);
  const [passwordForm, setPasswordForm] = useState({ oldPassword:'', newPassword:'', confirmPassword:'' });
  const [passwordMessage, setPasswordMessage] = useState('');

  function handleChange(event) {
    const { name, value } = event.target;
    setSaved(false);
    setForm(prev => ({ ...prev, [name]: value }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    const updatedUser = { ...user, ...form, name: form.name, full_name: form.name, company_name: form.company_name };
    saveSession({ user: updatedUser });
    if (isMockApi()) {
      sessionStorage.setItem(MOCK_USER_KEY, JSON.stringify(updatedUser));
      localStorage.setItem(MOCK_REGISTERED_USER_KEY, JSON.stringify(updatedUser));
    }
    onUserUpdate(updatedUser);
    setSaved(true);
  }

  return (<div className="profile-page">
      <div className="profile-card profile-hero">
        <div>
          <p className="profile-kicker">Profil pengguna</p>
          <h1>{form.name || 'User'}</h1>
          <p>{form.email || '-'}</p>
        </div>
      </div>
      <form className="profile-card profile-form" onSubmit={handleSubmit}>
        <div className="profile-section-title">Update data profil</div>
        <label><span>Nama lengkap</span><input name="name" value={form.name} onChange={handleChange} placeholder="Nama lengkap" /></label>
        <label><span>Email</span><input name="email" type="email" value={form.email} onChange={handleChange} placeholder="email@domain.com" /></label>
        <label><span>Nama company</span><input name="company_name" value={form.company_name} onChange={handleChange} placeholder="Nama perusahaan" /></label>
        <label><span>Nomor telepon</span><input name="phone" value={form.phone} onChange={handleChange} placeholder="Nomor telepon" /></label>
        <label><span>Role</span><input name="role" value={form.role} onChange={handleChange} placeholder="Role pengguna" /></label>
        {saved && <div className="profile-success">Profil berhasil diperbarui.</div>}
        <button className="profile-save" type="submit">Simpan Perubahan</button>
      </form>
      <div className="profile-card profile-form" style={{marginTop:'20px'}}>
      <div className="profile-section-title">Ubah Password</div>
      <label><input type="password" placeholder="Password Lama" value={passwordForm.oldPassword} onChange={(e)=>setPasswordForm({...passwordForm, oldPassword:e.target.value})} /></label>
      <label><input type="password" placeholder="Password Baru" value={passwordForm.newPassword} onChange={(e)=>setPasswordForm({...passwordForm, newPassword:e.target.value})} /></label>
      <label><input type="password" placeholder="Konfirmasi Password Baru" value={passwordForm.confirmPassword} onChange={(e)=>setPasswordForm({...passwordForm, confirmPassword:e.target.value})} /></label>
      <button type="button" className="profile-save" onClick={() => { if(passwordForm.newPassword.length < 8){setPasswordMessage('Password baru minimal 8 karakter');return;} if(passwordForm.newPassword !== passwordForm.confirmPassword){setPasswordMessage('Konfirmasi password tidak sesuai');return;} setPasswordMessage('Password berhasil diperbarui'); }}>Ubah Password</button>
      {passwordMessage && <div className="profile-success">{passwordMessage}</div>}
      </div></div>);
}
