import React from 'react';
import { getScoreColor, getStatusClass } from '../../utils/helpers';
import './CandidateDetail.css';

const BREAKDOWN_LABELS = {
  skill: 'Kecocokan Skill',
  experience: 'Pengalaman',
  education: 'Pendidikan',
  relevance: 'Relevansi JD',
};

export default function CandidateDetail({ candidate: c }) {
  return (
    <div className="cdet">
      {/* Hero */}
      <div className="cdet-hero">
        <div className="cdet-avatar" style={{ background: c.colorBg, color: c.colorAccent }}>
          {c.initials}
        </div>
        <div className="cdet-hero-info">
          <div className="cdet-name">{c.name}</div>
          <div className="cdet-sub">{c.email} · {c.phone} · {c.location}</div>
          <div className="cdet-pos">{c.position}</div>
        </div>
        <div className="cdet-score-box">
          <div className="cdet-score-num" style={{ color: getScoreColor(c.score) }}>{c.score}%</div>
          <span className={`badge ${getStatusClass(c.status)}`}>{c.status}</span>
        </div>
      </div>

      {/* 3-col grid */}
      <div className="cdet-grid">

        {/* Profil */}
        <div className="cdet-section">
          <div className="cdet-section-title">Profil Kandidat</div>
          <div className="info-list">
            <InfoRow label="Universitas" value={c.education.university} />
            <InfoRow label="Jurusan" value={c.education.major} />
            <InfoRow label="Jenjang" value={c.education.level} />
            <InfoRow label="IPK" value={c.education.gpa} />
            <InfoRow label="Angkatan" value={c.education.year} />
            <InfoRow label="Pengalaman" value={c.experience.label} />
          </div>
          <div className="cdet-section-title" style={{ marginTop: 12 }}>Skill Terdeteksi</div>
          <div className="tags-wrap">
            {c.skills.map(s => <span key={s} className="skill-chip">{s}</span>)}
          </div>
        </div>

        {/* Breakdown skor */}
        <div className="cdet-section">
          <div className="cdet-section-title">Breakdown Skor AI</div>
          <div className="breakdown-list">
            {Object.entries(c.scoreBreakdown).map(([k, v]) => (
              <div key={k} className="bd-row">
                <span className="bd-label">{BREAKDOWN_LABELS[k]}</span>
                <div className="bd-bar-track">
                  <div className="bd-bar-fill" style={{ width: v + '%', background: getScoreColor(v) }} />
                </div>
                <span className="bd-score" style={{ color: getScoreColor(v) }}>{v}%</span>
              </div>
            ))}
          </div>
          <div className="overall-box">
            <div className="overall-label">Skor Keseluruhan</div>
            <div className="overall-num" style={{ color: getScoreColor(c.score) }}>{c.score}%</div>
            <span className={`badge ${getStatusClass(c.status)}`}>{c.status}</span>
          </div>
        </div>

        {/* CV text */}
        <div className="cdet-section">
          <div className="cdet-section-title">
            Ringkasan CV
            <span className="section-note">teks terekstrak</span>
          </div>
          <pre className="cv-text">{c.cvText}</pre>

          {c.workHistory.length > 0 && (
            <>
              <div className="cdet-section-title" style={{ marginTop: 12 }}>Riwayat Kerja</div>
              <div className="work-list">
                {c.workHistory.map((w, i) => (
                  <div key={i} className="work-item">
                    <div className="work-header">
                      <span className="work-company">{w.company}</span>
                      <span className="work-period">{w.period}</span>
                    </div>
                    <div className="work-role">{w.role}</div>
                    <div className="work-desc">{w.desc}</div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

      </div>
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="info-row">
      <span className="info-label">{label}</span>
      <span className="info-value">{value}</span>
    </div>
  );
}
