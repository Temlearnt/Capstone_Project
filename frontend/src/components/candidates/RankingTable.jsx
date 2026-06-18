import React, { useState } from 'react';
import { getScoreColor, getStatusClass } from '../../utils/helpers';
import CandidateDetail from './CandidateDetail';
import './RankingTable.css';

export default function RankingTable({ candidates, onViewDetail }) {
  const [search, setSearch] = useState('');
  const [filterBatch, setFilterBatch] = useState('');
  const [sortBy, setSortBy] = useState('score');
  const [expandedId, setExpandedId] = useState(null);

  const filtered = candidates
    .filter(c => {
      const q = search.toLowerCase();
      const matchQ = !q || c.name.toLowerCase().includes(q) || c.skills.some(s => s.toLowerCase().includes(q));
      const matchBatch = !filterBatch || (c.batchId || c.batchLabel || 'batch-terbaru') === filterBatch;
      return matchQ && matchBatch;
    })
    .sort((a, b) => {
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      if (sortBy === 'exp') return b.experience.years - a.experience.years;
      return b.score - a.score;
    });

  const batchOptions = Array.from(new Map(candidates.map(c => [c.batchId || c.batchLabel || 'batch-terbaru', c.batchLabel || 'Batch terbaru'])).entries());

  const toggle = (id) => setExpandedId(prev => prev === id ? null : id);

  return (
    <div className="ranking-wrap">
      <div className="ranking-card">
        <div className="ranking-hdr">
          <span className="card-title">
            History Kandidat
            <span className="count-badge">{filtered.length}</span>
          </span>
          <div className="filter-row">
            <input
              className="filter-input"
              placeholder="Cari nama / skill..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <select className="filter-select" value={filterBatch} onChange={e => setFilterBatch(e.target.value)}>
              <option value="">Semua batch upload CV</option>
              {batchOptions.map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
            <select className="filter-select" value={sortBy} onChange={e => setSortBy(e.target.value)}>
              <option value="score">Skor tertinggi</option>
              <option value="name">Nama A–Z</option>
              <option value="exp">Pengalaman</option>
            </select>
          </div>
        </div>

        <table className="rank-table">
          <thead>
            <tr>
              <th style={{width:36}}></th>
              <th style={{width:34}}>#</th>
              <th style={{width:180}}>Nama</th>
              <th style={{width:120}}>Skor</th>
              <th style={{width:115}}>Status</th>
              <th style={{width:80}}>Exp.</th>
              <th style={{width:56}}>Edu.</th>
              <th>Skill</th>
              <th style={{width:170}}>Email</th>
              <th style={{width:80}}>Aksi</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((c, i) => (
              <React.Fragment key={c.id}>
                <tr className={`data-row${expandedId === c.id ? ' expanded' : ''}`}>
                  <td className="toggle-cell">
                    <button
                      className={`toggle-btn${expandedId === c.id ? ' open' : ''}`}
                      onClick={() => toggle(c.id)}
                      aria-label={`Detail ${c.name}`}
                    >▾</button>
                  </td>
                  <td className="rank-num">{i + 1}</td>
                  <td>
                    <div className="name-cell">
                      <div className="avatar" style={{ background: c.colorBg, color: c.colorAccent }}>{c.initials}</div>
                      <div>
                        <div className="cand-name">{c.name}</div>
                        <div className="cand-pos">{c.position}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div className="score-bar">
                      <div className="bar-track">
                        <div className="bar-fill" style={{ width: c.score + '%', background: getScoreColor(c.score) }} />
                      </div>
                      <span className="score-num" style={{ color: getScoreColor(c.score) }}>{c.score}%</span>
                    </div>
                  </td>
                  <td><span className={`badge ${getStatusClass(c.status)}`}>{c.status}</span></td>
                  <td className="muted">{c.experience.label}</td>
                  <td className="muted">{c.education.level}</td>
                  <td>
                    <div className="tags-row">
                      {c.skills.slice(0, 3).map(s => <span key={s} className="tag">{s}</span>)}
                      {c.skills.length > 3 && <span className="tag">+{c.skills.length - 3}</span>}
                    </div>
                  </td>
                  <td className="email-cell">{c.email}</td>
                  <td><button className="detail-btn" onClick={() => onViewDetail(c)}>Detail</button></td>
                </tr>

                {expandedId === c.id && (
                  <tr className="detail-row">
                    <td colSpan={10} className="detail-cell">
                      <CandidateDetail candidate={c} />
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}

            {filtered.length === 0 && (
              <tr><td colSpan={10} className="empty-state">Tidak ada kandidat yang cocok dengan filter.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
