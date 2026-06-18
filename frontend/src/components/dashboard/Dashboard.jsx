import React, { useMemo, useState } from 'react';
import { getScoreColor, getStatusClass } from '../../utils/helpers';
import { JOB_ROLES } from '../../data/candidates';
import './Dashboard.css';

export default function Dashboard({ candidates, jobDescription, selectedRole, onRoleChange, onNavigate, onViewDetail }) {
  const [rankingSearch, setRankingSearch] = useState('');
  const avg = candidates.length ? Math.round(candidates.reduce((s, c) => s + c.score, 0) / candidates.length) : 0;
  const sangat = candidates.filter(c => c.status === 'Sangat Cocok').length;
  const perlu = candidates.filter(c => c.status === 'Perlu Review').length;

  const topCandidates = useMemo(() => {
    const q = rankingSearch.trim().toLowerCase();

    return candidates
      .filter(candidate => {
        if (!q) return true;

        const searchableText = [
          candidate.name,
          candidate.email,
          candidate.position,
          candidate.status,
          ...(candidate.skills || []),
        ].join(' ').toLowerCase();

        return searchableText.includes(q);
      })
      .slice(0, 5);
  }, [candidates, rankingSearch]);

  return (
    <div className="dashboard">
      <div className="stat-grid">
        <StatCard label="Total Kandidat" value={candidates.length} sub="Batch aktif" />
        <StatCard label="Skor Rata-rata" value={avg + '%'} sub="Dari semua kandidat" />
        <StatCard label="Sangat Cocok" value={sangat} sub="Skor ≥ 85%" accent="green" />
        <StatCard label="Perlu Review" value={perlu} sub="Skor < 65%" accent="red" />
      </div>

      <div className="dashboard-main-grid">
        <div className="db-card">
          <div className="card-hdr jd-card-hdr">
            <span className="card-title">Job Description</span>
            <div className="role-inline">
              <span>Role</span>
              <select className="role-select" value={selectedRole} onChange={e => onRoleChange(e.target.value)}>
                {JOB_ROLES.map(role => <option key={role} value={role}>{role}</option>)}
              </select>
            </div>
          </div>
          <pre className="jd-preview">{jobDescription}</pre>
        </div>

        <div className="db-card top-card">
          <div className="card-hdr top-ranking-hdr">
            <span className="card-title">5 Kandidat Teratas</span>
            <div className="top-ranking-actions">
              <label className="dashboard-search">
                <span className="sr-only">Cari kandidat</span>
                <input
                  type="search"
                  placeholder="Cari nama, role, skill..."
                  value={rankingSearch}
                  onChange={e => setRankingSearch(e.target.value)}
                />
              </label>
              <button className="see-all-btn" onClick={() => onNavigate('ranking')}>Lihat History</button>
            </div>
          </div>
          {candidates.length === 0 ? (
            <div className="dashboard-empty-state">
              <div className="empty-icon">□</div>
              <h3>Belum ada data screening</h3>
              <p>Data kandidat akan muncul setelah kamu upload CV dan FastAPI mengembalikan hasil screening.</p>
              <button className="see-all-btn" onClick={() => onNavigate('upload')}>Upload CV</button>
            </div>
          ) : (
          <table className="mini-table">
            <thead><tr>
              <th style={{width:32}}>#</th><th>Nama</th><th style={{width:110}}>Skor</th>
              <th style={{width:110}}>Status</th><th>Skill</th><th style={{width:70}}>Aksi</th>
            </tr></thead>
            <tbody>
              {topCandidates.map((c,i) => (
                <tr key={c.id}>
                  <td className="tc">{i+1}</td>
                  <td><div className="name-cell">
                    <div className="avatar" style={{background:c.colorBg,color:c.colorAccent}}>{c.initials}</div>
                    <span>{c.name}</span>
                  </div></td>
                  <td><div className="score-bar">
                    <div className="bar-track"><div className="bar-fill" style={{width:c.score+'%',background:getScoreColor(c.score)}}/></div>
                    <span className="score-num">{c.score}%</span>
                  </div></td>
                  <td><span className={`badge ${getStatusClass(c.status)}`}>{c.status}</span></td>
                  <td><div className="tags-row">{c.skills.slice(0,3).map(s=><span key={s} className="tag">{s}</span>)}</div></td>
                  <td><button className="link-btn" onClick={()=>onViewDetail(c)}>Detail</button></td>
                </tr>
              ))}
              {topCandidates.length === 0 && (
                <tr>
                  <td colSpan={6} className="dashboard-empty">Kandidat tidak ditemukan.</td>
                </tr>
              )}
            </tbody>
          </table>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({label,value,sub,accent}) {
  const colors = {green:'var(--green)',red:'var(--red)'};
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={accent?{color:colors[accent]}:{}}>{value}</div>
      <div className="stat-sub">{sub}</div>
    </div>
  );
}
