import React from 'react';
import './Sidebar.css';

const NAV = [
  { id: 'dashboard', label: 'Dashboard', icon: '⊞' },
  { id: 'upload',    label: 'Unggah CV', icon: '⇪' },
  { id: 'ranking',   label: 'History',  icon: '≡' },
];

export default function Sidebar({ activePage, onNavigate, user, onLogout, isOpen = true, onToggle }) {
  return (
    <aside className={`sidebar${isOpen ? '' : ' collapsed'}`}>
      <div className="sidebar-top">
        <div className="sidebar-brand">
          <span className="sidebar-menu-label">Recruitly</span>
        </div>
        <button
          className="sidebar-hamburger"
          onClick={onToggle}
          aria-label="Buka tutup sidebar"
          title="Buka/tutup sidebar"
        >
          ☰
        </button>
      </div>
      <nav className="sidebar-nav">
        {NAV.map(n => (
          <button key={n.id}
            className={`nav-item${activePage === n.id ? ' active' : ''}`}
            onClick={() => onNavigate(n.id)}>
            <span className="nav-icon">{n.icon}</span>
            <span>{n.label}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        {user && (
          <button className="sidebar-user profile-shortcut" type="button" onClick={() => onNavigate('profile')} title="Buka profil">
            <div className="sidebar-profile-avatar">{user.profilePhoto ? <img src={user.profilePhoto} alt="Foto profil" /> : (user.name || user.full_name || 'User').slice(0, 1).toUpperCase()}</div>
            <div className="sidebar-profile-text">
              <strong>{user.name || user.full_name || 'User'}</strong>
              <span>{user.email}</span>
            </div>
          </button>
        )}
        <button className="sidebar-logout" onClick={onLogout}>Logout</button>
      </div>
    </aside>
  );
}
