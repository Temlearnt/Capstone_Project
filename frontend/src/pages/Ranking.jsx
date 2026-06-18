import { useState } from 'react'
import { useApp } from '../../hooks/useAppContext'
import { Card, CardHeader, Badge, ScoreBar, Avatar, SkillTag } from '../ui'
import { ChevronDown, Mail, Phone, MapPin, GraduationCap, Briefcase } from 'lucide-react'
import { getScoreColor } from '../../data/candidates'

export default function Ranking({ setPage, setDetailId }) {
  const { candidates } = useApp()
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [sortBy, setSortBy] = useState('score')
  const [openId, setOpenId] = useState(null)

  const filtered = candidates
    .filter(c => {
      const q = search.toLowerCase()
      const matchQ = !q || c.name.toLowerCase().includes(q) || c.skills.some(s => s.toLowerCase().includes(q)) || c.email.toLowerCase().includes(q)
      const matchS = !filterStatus || c.status === filterStatus
      return matchQ && matchS
    })
    .sort((a, b) => {
      if (sortBy === 'name') return a.name.localeCompare(b.name)
      if (sortBy === 'exp') return b.experience.years - a.experience.years
      return b.score - a.score
    })

  function toggle(id) {
    setOpenId(prev => prev === id ? null : id)
  }

  function openDetail(id) {
    setDetailId(id)
    setPage('detail')
  }

  return (
    <div className="page-enter" style={{ padding: 20 }}>
      <Card>
        <CardHeader
          title={
            <span>
              Peringkat kandidat{' '}
              <span style={{ fontSize: 11, fontWeight: 400, color: 'var(--text-3)' }}>
                ({filtered.length} dari {candidates.length})
              </span>
            </span>
          }
          right={
            <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Cari nama / skill..."
                style={{
                  fontSize: 12, padding: '5px 10px',
                  border: '1px solid var(--border-2)', borderRadius: 7,
                  background: 'var(--bg-3)', color: 'var(--text)', width: 150,
                }}
              />
              <select
                value={filterStatus}
                onChange={e => setFilterStatus(e.target.value)}
                style={selStyle}
              >
                <option value="">Semua status</option>
                <option value="Sangat Cocok">Sangat Cocok</option>
                <option value="Cocok">Cocok</option>
                <option value="Perlu Review">Perlu Review</option>
              </select>
              <select value={sortBy} onChange={e => setSortBy(e.target.value)} style={selStyle}>
                <option value="score">Skor tertinggi</option>
                <option value="name">Nama A–Z</option>
                <option value="exp">Pengalaman</option>
              </select>
            </div>
          }
        />

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr>
              {['', '#', 'Kandidat', 'Skor', 'Status', 'Exp.', 'Edu.', 'Skill utama', 'Aksi'].map((h, i) => (
                <th key={i} style={{
                  padding: '8px 12px', textAlign: 'left',
                  fontSize: 11, fontWeight: 500, color: 'var(--text-3)',
                  background: 'var(--bg-3)', borderBottom: '1px solid var(--border)',
                  whiteSpace: 'nowrap',
                }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((c, i) => {
              const isOpen = openId === c.id
              return [
                /* Data row */
                <tr key={c.id} style={{ background: isOpen ? 'var(--bg-3)' : 'transparent' }}>
                  {/* Toggle */}
                  <td style={{ ...td, width: 36, textAlign: 'center' }}>
                    <button
                      onClick={() => toggle(c.id)}
                      style={{
                        background: 'none', border: 'none', cursor: 'pointer',
                        color: isOpen ? 'var(--accent)' : 'var(--text-3)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        transition: 'var(--transition)',
                      }}
                    >
                      <ChevronDown
                        size={16}
                        style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform .2s' }}
                      />
                    </button>
                  </td>
                  {/* Rank */}
                  <td style={{ ...td, width: 32, color: 'var(--text-3)', textAlign: 'center', fontSize: 12 }}>{i + 1}</td>
                  {/* Kandidat */}
                  <td style={{ ...td, minWidth: 170 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Avatar name={c.name} color={c.color} />
                      <div>
                        <div style={{ fontSize: 13, color: 'var(--text)', fontWeight: 500 }}>{c.name}</div>
                        <div style={{ fontSize: 11, color: 'var(--text-3)' }}>{c.position}</div>
                      </div>
                    </div>
                  </td>
                  {/* Skor */}
                  <td style={{ ...td, width: 120 }}><ScoreBar score={c.score} /></td>
                  {/* Status */}
                  <td style={td}><Badge status={c.status} /></td>
                  {/* Exp */}
                  <td style={{ ...td, color: 'var(--text-2)', fontSize: 12 }}>{c.experience.label}</td>
                  {/* Edu */}
                  <td style={{ ...td, color: 'var(--text-2)', fontSize: 12 }}>{c.education.level}</td>
                  {/* Skill */}
                  <td style={td}>
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {c.skills.slice(0, 3).map(s => <SkillTag key={s} label={s} />)}
                      {c.skills.length > 3 && <SkillTag label={`+${c.skills.length - 3}`} />}
                    </div>
                  </td>
                  {/* Aksi */}
                  <td style={td}>
                    <button
                      onClick={() => openDetail(c.id)}
                      style={{ fontSize: 12, color: 'var(--accent)', background: 'none', border: 'none', cursor: 'pointer' }}
                    >
                      Detail →
                    </button>
                  </td>
                </tr>,

                /* Expanded row */
                isOpen && (
                  <tr key={`exp-${c.id}`}>
                    <td colSpan={9} style={{ padding: 0, borderBottom: '1px solid var(--border)' }}>
                      <ExpandedDetail c={c} onOpenDetail={() => openDetail(c.id)} />
                    </td>
                  </tr>
                ),
              ]
            })}
          </tbody>
        </table>

        {filtered.length === 0 && (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-3)', fontSize: 13 }}>
            Tidak ada kandidat yang sesuai filter.
          </div>
        )}
      </Card>
    </div>
  )
}

function ExpandedDetail({ c, onOpenDetail }) {
  const cats = [
    { key: 'skill', label: 'Kecocokan skill' },
    { key: 'experience', label: 'Pengalaman' },
    { key: 'education', label: 'Pendidikan' },
    { key: 'relevance', label: 'Relevansi JD' },
  ]

  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
      gap: 16, padding: '16px 14px',
      background: 'var(--bg-3)', borderTop: '1px solid var(--border)',
      animation: 'fadeSlide .15s ease',
    }}>
      {/* Kolom 1: Profil */}
      <div>
        <SectionTitle>Profil kandidat</SectionTitle>
        <InfoLine label={<><Mail size={11} /> Email</>} value={<span style={{ color: 'var(--accent)' }}>{c.email}</span>} />
        <InfoLine label={<><Phone size={11} /> Telepon</>} value={c.phone} />
        <InfoLine label={<><MapPin size={11} /> Lokasi</>} value={c.location} />
        <InfoLine label={<><GraduationCap size={11} /> Universitas</>} value={c.education.university} />
        <InfoLine label="Jurusan" value={c.education.major} />
        <InfoLine label="Jenjang" value={c.education.level} />
        <InfoLine label="IPK" value={c.education.gpa} />
        <InfoLine label="Lulus" value={c.education.year} />
        <InfoLine label={<><Briefcase size={11} /> Pengalaman</>} value={c.experience.label} />

        <div style={{ marginTop: 12 }}>
          <SectionTitle>Skill terdeteksi</SectionTitle>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
            {c.skills.map(s => <SkillTag key={s} label={s} />)}
          </div>
        </div>
      </div>

      {/* Kolom 2: Skor + Pengalaman kerja */}
      <div>
        <SectionTitle>Breakdown skor AI</SectionTitle>
        {cats.map(({ key, label }) => (
          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, fontSize: 12 }}>
            <span style={{ width: 120, color: 'var(--text-3)', flexShrink: 0 }}>{label}</span>
            <div style={{ flex: 1, height: 4, background: 'var(--bg-4)', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{
                height: '100%', borderRadius: 3,
                background: getScoreColor(c.scoreBreakdown[key]),
                width: `${c.scoreBreakdown[key]}%`,
              }} />
            </div>
            <span style={{ fontSize: 11, fontWeight: 500, color: getScoreColor(c.scoreBreakdown[key]), minWidth: 28, textAlign: 'right' }}>
              {c.scoreBreakdown[key]}%
            </span>
          </div>
        ))}

        <div style={{
          marginTop: 12, padding: '10px 12px',
          background: 'var(--bg-4)', borderRadius: 8,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <span style={{ fontSize: 12, color: 'var(--text-3)' }}>Skor keseluruhan</span>
          <span style={{ fontSize: 20, fontWeight: 600, color: getScoreColor(c.score) }}>{c.score}%</span>
        </div>

        {c.experience.jobs.length > 0 && (
          <div style={{ marginTop: 14 }}>
            <SectionTitle>Riwayat kerja</SectionTitle>
            {c.experience.jobs.map((j, i) => (
              <div key={i} style={{ marginBottom: 10 }}>
                <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text)' }}>{j.title}</div>
                <div style={{ fontSize: 11, color: 'var(--accent)', marginBottom: 3 }}>{j.company} · {j.period}</div>
                <div style={{ fontSize: 11, color: 'var(--text-3)', lineHeight: 1.6 }}>{j.desc}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Kolom 3: CV snippet */}
      <div>
        <SectionTitle>Ringkasan CV</SectionTitle>
        <div style={{
          fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--text-2)',
          background: 'var(--bg-4)', borderRadius: 8, padding: '10px 12px',
          maxHeight: 240, overflowY: 'auto', whiteSpace: 'pre-wrap', lineHeight: 1.7,
        }}>
          {c.cvText}
        </div>
        <button
          onClick={onOpenDetail}
          style={{
            marginTop: 10, fontSize: 12, color: 'var(--accent)',
            background: 'none', border: 'none', cursor: 'pointer',
          }}
        >
          Lihat halaman detail lengkap →
        </button>
      </div>
    </div>
  )
}

function SectionTitle({ children }) {
  return (
    <div style={{
      fontSize: 10, fontWeight: 600, color: 'var(--text-3)',
      textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 8,
    }}>
      {children}
    </div>
  )
}

function InfoLine({ label, value }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between',
      fontSize: 12, padding: '4px 0',
      borderBottom: '1px solid var(--border)',
    }}>
      <span style={{ color: 'var(--text-3)', display: 'flex', alignItems: 'center', gap: 4 }}>{label}</span>
      <span style={{ color: 'var(--text-2)' }}>{value}</span>
    </div>
  )
}

const td = { padding: '10px 12px', borderBottom: '1px solid var(--border)', verticalAlign: 'middle' }
const selStyle = {
  fontSize: 12, padding: '5px 9px',
  border: '1px solid var(--border-2)', borderRadius: 7,
  background: 'var(--bg-3)', color: 'var(--text)',
}
