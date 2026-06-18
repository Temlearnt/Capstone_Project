import { useApp } from '../../hooks/useAppContext'
import { Badge, ScoreBar, Avatar, SkillTag, Card, CardHeader } from '../ui'
import { getScoreColor } from '../../data/candidates'
import { ArrowLeft, Mail, Phone, MapPin, GraduationCap, Briefcase, FileText, Calendar } from 'lucide-react'

export default function Detail({ candidateId, setPage }) {
  const { candidates } = useApp()
  const c = candidates.find(x => x.id === candidateId)

  if (!c) return (
    <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-3)' }}>
      Kandidat tidak ditemukan.
    </div>
  )

  const cats = [
    { key: 'skill', label: 'Kecocokan skill', pct: 40 },
    { key: 'experience', label: 'Pengalaman kerja', pct: 30 },
    { key: 'education', label: 'Pendidikan', pct: 15 },
    { key: 'relevance', label: 'Relevansi JD', pct: 15 },
  ]

  return (
    <div className="page-enter" style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>
      {/* Back */}
      <button
        onClick={() => setPage('ranking')}
        style={{
          display: 'inline-flex', alignItems: 'center', gap: 6,
          fontSize: 13, color: 'var(--text-2)', background: 'none',
          border: 'none', cursor: 'pointer',
        }}
      >
        <ArrowLeft size={15} /> Kembali ke peringkat
      </button>

      {/* Hero */}
      <Card>
        <div style={{
          padding: '16px 20px', display: 'flex', alignItems: 'center', gap: 16,
          borderBottom: '1px solid var(--border)',
        }}>
          <Avatar name={c.name} color={c.color} />
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--text)' }}>{c.name}</div>
            <div style={{ fontSize: 13, color: 'var(--text-3)' }}>{c.position}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 30, fontWeight: 700, color: getScoreColor(c.score) }}>{c.score}%</div>
            <Badge status={c.status} />
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', borderBottom: '1px solid var(--border)' }}>
          {[
            { icon: Mail, label: 'Email', value: c.email },
            { icon: Phone, label: 'Telepon', value: c.phone },
            { icon: MapPin, label: 'Lokasi', value: c.location },
            { icon: Calendar, label: 'Diunggah', value: c.uploadedAt },
          ].map(({ icon: Icon, label, value }) => (
            <div key={label} style={{ padding: '12px 16px', borderRight: '1px solid var(--border)' }}>
              <div style={{ fontSize: 11, color: 'var(--text-3)', marginBottom: 3, display: 'flex', alignItems: 'center', gap: 4 }}>
                <Icon size={11} /> {label}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-2)' }}>{value}</div>
            </div>
          ))}
        </div>
      </Card>

      {/* Main grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        {/* Breakdown skor */}
        <Card>
          <CardHeader title="Breakdown skor AI" right={
            <span style={{ fontSize: 11, color: 'var(--text-3)' }}>4 dimensi penilaian</span>
          } />
          <div style={{ padding: '14px 16px' }}>
            {cats.map(({ key, label, pct }) => (
              <div key={key} style={{ marginBottom: 14 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5, fontSize: 12 }}>
                  <span style={{ color: 'var(--text-2)' }}>{label}</span>
                  <span style={{ color: 'var(--text-3)', fontSize: 11 }}>bobot {pct}%</span>
                </div>
                <ScoreBar score={c.scoreBreakdown[key]} height={6} />
              </div>
            ))}
            <div style={{
              marginTop: 16, padding: '12px 14px',
              background: 'var(--bg-3)', borderRadius: 8,
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
              <span style={{ fontSize: 13, color: 'var(--text-2)' }}>Total skor keseluruhan</span>
              <span style={{ fontSize: 26, fontWeight: 700, color: getScoreColor(c.score) }}>{c.score}%</span>
            </div>
          </div>
        </Card>

        {/* Pendidikan + Skill */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Card>
            <CardHeader title="Pendidikan" right={<GraduationCap size={15} color="var(--text-3)" />} />
            <div style={{ padding: '4px 16px' }}>
              {[
                ['Jenjang', c.education.level],
                ['Jurusan', c.education.major],
                ['Universitas', c.education.university],
                ['IPK', c.education.gpa],
                ['Tahun', c.education.year],
              ].map(([l, v]) => (
                <div key={l} style={{
                  display: 'flex', justifyContent: 'space-between',
                  fontSize: 12, padding: '7px 0',
                  borderBottom: '1px solid var(--border)',
                }}>
                  <span style={{ color: 'var(--text-3)' }}>{l}</span>
                  <span style={{ color: 'var(--text-2)' }}>{v}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <CardHeader title="Skill terdeteksi" />
            <div style={{ padding: '10px 14px', display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {c.skills.map(s => <SkillTag key={s} label={s} />)}
            </div>
          </Card>
        </div>
      </div>

      {/* Pengalaman kerja */}
      {c.experience.jobs.length > 0 && (
        <Card>
          <CardHeader title="Riwayat pengalaman kerja" right={<Briefcase size={15} color="var(--text-3)" />} />
          <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 16 }}>
            {c.experience.jobs.map((j, i) => (
              <div key={i} style={{ display: 'flex', gap: 14 }}>
                <div style={{
                  width: 8, minWidth: 8, marginTop: 4,
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
                }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--accent)' }} />
                  {i < c.experience.jobs.length - 1 && (
                    <div style={{ flex: 1, width: 1, background: 'var(--border-2)' }} />
                  )}
                </div>
                <div style={{ flex: 1, paddingBottom: 8 }}>
                  <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text)' }}>{j.title}</div>
                  <div style={{ fontSize: 12, color: 'var(--accent)', marginBottom: 4 }}>{j.company} · {j.period}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-3)', lineHeight: 1.7 }}>{j.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* CV asli */}
      <Card>
        <CardHeader title="Isi CV" right={
          <span style={{ fontSize: 11, color: 'var(--text-3)', display: 'flex', alignItems: 'center', gap: 4 }}>
            <FileText size={12} /> Teks terekstrak dari PDF
          </span>
        } />
        <div style={{
          margin: 14, padding: '14px 16px',
          background: 'var(--bg-3)', borderRadius: 8,
          fontFamily: 'var(--mono)', fontSize: 12,
          color: 'var(--text-2)', lineHeight: 1.8,
          whiteSpace: 'pre-wrap', maxHeight: 320, overflowY: 'auto',
        }}>
          {c.cvText}
        </div>
      </Card>
    </div>
  )
}
