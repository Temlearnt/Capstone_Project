import React, { useEffect, useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import AuthPage from './components/auth/AuthPage';
import LandingPage from './components/LandingPage';
import Dashboard from './components/dashboard/Dashboard';
import RankingTable from './components/candidates/RankingTable';
import UploadPage from './components/upload/UploadPage';
import CandidateDetail from './components/candidates/CandidateDetail';
import ProfilePage from './components/profile/ProfilePage';
import { JOB_DESCRIPTION, JOB_DESCRIPTIONS } from './data/candidates';
import { getCandidates, getJobDescriptions, mergeCandidateHistory } from './services/candidateService';
import { getCurrentUser, logoutUser, onAuthStateChange, expireLocalSession } from './services/authService';
import { AUTH_SESSION_ENDED_EVENT } from './services/apiClient';
import recruitlyLogo from './assets/recruitly-logo.png';
import recruitlyLoadingLogo from './assets/recruitly-loading-logo.png';
import './App.css';

export default function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [page, setPage] = useState('dashboard');
  const [showLanding, setShowLanding] = useState(true);
  const [authMode, setAuthMode] = useState('login');
  const [selectedRole, setSelectedRole] = useState('Frontend Developer');
  const [jd, setJd] = useState(JOB_DESCRIPTION);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [detailCandidate, setDetailCandidate] = useState(null);
  const [screeningLoading, setScreeningLoading] = useState(false);
  const [candidates, setCandidates] = useState([]);
  const [jobDescriptions, setJobDescriptions] = useState(JOB_DESCRIPTIONS);
  const [dataError, setDataError] = useState('');

  const sorted = [...candidates].sort((a, b) => b.score - a.score);
  const HISTORY_STORAGE_KEY = 'recruitly_candidate_history';

  useEffect(() => {
    let mounted = true;

    getCurrentUser()
      .then(currentUser => {
        if (mounted) {
          setUser(currentUser);
        }
      })
      .finally(() => {
        if (mounted) {
          setAuthLoading(false);
        }
      });

    const { data: authListener } = onAuthStateChange(currentUser => {
      setUser(currentUser);
      setAuthLoading(false);
    });

    const endSession = () => {
      expireLocalSession();
    };

    const handleForcedLogout = () => {
      setUser(null);
      setPage('dashboard');
      setShowLanding(false);
      setAuthMode('login');
      setAuthLoading(false);
    };

    window.addEventListener('pagehide', endSession);
    window.addEventListener(AUTH_SESSION_ENDED_EVENT, handleForcedLogout);

    return () => {
      mounted = false;
      authListener?.subscription?.unsubscribe();
      window.removeEventListener('pagehide', endSession);
      window.removeEventListener(AUTH_SESSION_ENDED_EVENT, handleForcedLogout);
    };
  }, []);



  useEffect(() => {
    let mounted = true;

    if (!user) return undefined;

    Promise.all([getCandidates(), getJobDescriptions()])
      .then(([candidateData, jdData]) => {
        if (!mounted) return;
        const savedHistory = JSON.parse(localStorage.getItem(HISTORY_STORAGE_KEY) || '[]');
        setCandidates(mergeCandidateHistory(savedHistory, candidateData || []));
        const nextJobDescriptions = jdData || JOB_DESCRIPTIONS;
        setJobDescriptions(nextJobDescriptions);
        const roleNames = Object.keys(nextJobDescriptions);
        if (roleNames.length && !nextJobDescriptions[selectedRole]) {
          setSelectedRole(roleNames[0]);
          setJd(nextJobDescriptions[roleNames[0]] || '');
        }
        setDataError('');
      })
      .catch(err => {
        if (!mounted) return;
        setDataError(err.message || 'Gagal mengambil data dari backend.');
        const savedHistory = JSON.parse(localStorage.getItem(HISTORY_STORAGE_KEY) || '[]');
        setCandidates(savedHistory);
        if (!savedHistory.length) setDataError(err.message || 'Gagal mengambil data dari backend.');
      });

    return () => {
      mounted = false;
    };
  }, [user]);


  useEffect(() => {
    if (!user) return;
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(candidates));
  }, [candidates, user]);

  function handleCandidatesUpdate(updater) {
    setCandidates(prev => {
      const next = typeof updater === 'function' ? updater(prev) : updater;
      return mergeCandidateHistory(prev, next || []);
    });
  }

  async function handleLogout() {
    await logoutUser();
    setUser(null);
    setPage('dashboard');
    setAuthMode('login');
    setShowLanding(false);
  }

  function handleAuthSuccess(currentUser) {
    setUser(currentUser);
    setShowLanding(false);
    setPage('dashboard');
    setScreeningLoading(true);

    window.setTimeout(() => {
      setScreeningLoading(false);
    }, 2300);
  }

  function handleRoleChange(role) {
    setSelectedRole(role);
    setJd(jobDescriptions[role] || JOB_DESCRIPTIONS[role] || '');
  }

  function openAuth(nextMode = 'login') {
    setAuthMode(nextMode);
    setShowLanding(false);
  }

  function openDashboard() {
    setShowLanding(false);
    setPage('dashboard');
  }


  if (authLoading) {
    return (
      <div className="auth-page">
        <div className="auth-card auth-loading-card">
          <div className="auth-brand">
            <img src={recruitlyLoadingLogo} alt="Recruitly" className="auth-logo-img" />
            <div>
              <h1>Recruitly</h1>
              <p>Memeriksa sesi login...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (showLanding) {
    return (
      <LandingPage
        user={user}
        onLogin={() => openAuth('login')}
        onRegister={() => openAuth('register')}
        onDashboard={openDashboard}
      />
    );
  }

  if (!user) {
    return (
      <AuthPage
        initialMode={authMode}
        onAuthSuccess={handleAuthSuccess}
        onBackToLanding={() => setShowLanding(true)}
      />
    );
  }

  if (screeningLoading) {
    return <ScreeningLoader />;
  }

  return (
    <div className={`app-shell${sidebarOpen ? '' : ' sidebar-closed'}`}>
      <Sidebar
        activePage={page}
        onNavigate={setPage}
        user={user}
        onLogout={handleLogout}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(prev => !prev)}
      />
      <div className="app-main">
        <header className="app-topbar">
          <div className="topbar-left">
            <span className="topbar-title">
              {page === 'dashboard' && 'Dashboard'}
              {page === 'upload' && 'Unggah CV'}
              {page === 'ranking' && 'History Kandidat'}
              {page === 'profile' && 'Profil'}
            </span>
          </div>
          <div className="topbar-actions topbar-actions-empty" aria-hidden="true" />
        </header>

        <main className="app-content">
          {dataError && <div className="backend-warning">{dataError}</div>}
          {page === 'dashboard' && (
            <Dashboard
              candidates={sorted}
              jobDescription={jd}
              selectedRole={selectedRole}
              onRoleChange={handleRoleChange}
              onNavigate={setPage}
              onViewDetail={setDetailCandidate}
            />
          )}
          {page === 'upload' && (
            <UploadPage
              jobDescription={jd}
              selectedRole={selectedRole}
              onRoleChange={handleRoleChange}
              onJDChange={setJd}
              jobDescriptions={jobDescriptions}
              onGoRanking={() => setPage('ranking')}
              onCandidatesUpdate={handleCandidatesUpdate}
            />
          )}
          {page === 'ranking' && (
            <RankingTable candidates={sorted} onViewDetail={setDetailCandidate} />
          )}
          {page === 'profile' && (
            <ProfilePage user={user} onUserUpdate={setUser} />
          )}
        </main>
      </div>

      {detailCandidate && (
        <div className="detail-modal-backdrop" onClick={() => setDetailCandidate(null)}>
          <div className="detail-modal" onClick={e => e.stopPropagation()}>
            <button className="detail-close" onClick={() => setDetailCandidate(null)}>×</button>
            <CandidateDetail candidate={detailCandidate} />
          </div>
        </div>
      )}
    </div>
  );
}


function ScreeningLoader() {
  return (
    <div className="screening-page">
      <div className="screening-orb-wrap">
        <div className="screening-orb" />
        <div className="screening-ring ring-one" />
        <div className="screening-ring ring-two" />
        <div className="screening-chip chip-a">Skill Match</div>
        <div className="screening-chip chip-b">CV Parsing</div>
        <div className="screening-chip chip-c">AI Ranking</div>
      </div>
      <div className="screening-card">
        <img src={recruitlyLoadingLogo} alt="Recruitly" className="screening-logo" />
        <div className="screening-kicker">Recruitly Screening</div>
        <h1>Menganalisis CV kandidat...</h1>
        <p>AI sedang membaca profil, mencocokkan skill, dan menyusun peringkat terbaik untuk job description aktif.</p>
        <div className="screening-progress">
          <span />
        </div>
        <div className="screening-steps">
          <span>Ekstrak CV</span>
          <span>Cocokkan JD</span>
          <span>Ranking</span>
        </div>
      </div>
    </div>
  );
}
