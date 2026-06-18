import { useApp } from '../../hooks/useAppContext'
import { StatCard, Card, CardHeader, Badge, ScoreBar, Btn, Avatar } from '../ui'
import { getScoreColor } from '../../data/candidates'
import { TrendingUp, Users, CheckCircle, AlertCircle, ChevronRight } from 'lucide-react'

export default function Dashboard({ setPage, setDetailId }) {
  const { candidates, activeJob } = useApp()

  const avg = Math.round(candidates.reduce((s, c) => s + c.score, 0) / candidates.length)
  const great = candidates.filter(c => c.score >= 85).length
  const review = candidates.filter(c => c.score < 65).length
  const top5 = [...candidates].sort((a, b) => b.score - a.score).slice(0, 5)

  function openDetail(id) {
    setDetailId(id)
    setPage('detail')
  }

  return (
    <div className="page-enter" style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10 }}>
        <StatCard label="Total kandidat" value={candidates.length} sub={`Posisi: ${activeJob}`} icon={Users} />
        <StatCard label="Skor rata-rata" value={`${avg}%`} sub="Dari semua CV yang diproses" icon={TrendingUp} />
        <StatCard label="Sangat cocok" value={great} sub="Skor ≥ 85%" icon={CheckCircle} />
        <StatCard label="Perlu review" value={review} sub="Skor < 65%" icon={AlertCircle} />
      </div>

      {/* JD aktif */}
      <Card>
        <CardHeader title="Job description aktif" right={
          <span style={{
            fontSize: 11, background: 'var(--accent-soft)',
            color: 'var(--accent)', padding: '2px 8px', borderRadius: 4, fontWeight: 500,
          }}>
            {activeJob}
          </span>
        } />
        <div style={{ padding: '12px 16px', fontSize: 13, color: 'var(--text-2)', lineHeight: 1.7 }}>
          Kami mencari <strong style={{ color: 'var(--text)' }}>Frontend Engineer</strong> berpengalaman
          min. 3 tahun. Wajib menguasai <strong style={{ color: 'var(--text)' }}>React.js, TypeScript,
          dan Tailwind CSS</strong>. Pengalaman REST API, Git, dan Agile diutamakan. Pendidikan min. S1
          Teknik Informatika. Nilai plus: Next.js, Jest/Cypress, desain sistem.
        </div>
      </Card>

      {/* Top 5 */}
      <Card>
        <CardHeader
          title="Top 5 kandidat"
          right={
            <Btn size="sm" onClick={() => setPage('ranking')}>
              Lihat semua <ChevronRight size={13} />
            </Btn>
          }
        />
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr>
              {['#', 'Nama', 'Skor', 'Status', 'Skill', ''].map((h, i) => (
                <th key={i} style={{
                  padding: '8px 14px', textAlign: 'left',
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
            {top5.map((c, i) => (
              <tr key={c.id} style={{ cursor: 'pointer' }} onClick={() => openDetail(c.id)}>
                <td style={tdStyle}><span style={{ color: 'var(--text-3)', fontSize: 12 }}>{i + 1}</span></td>
                <td style={tdStyle}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Avatar name={c.name} color={c.color} />
                    <div>
                      <div style={{ fontSize: 13, color: 'var(--text)' }}>{c.name}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-3)' }}>{c.email}</div>
                    </div>
                  </div>
                </td>
                <td style={{ ...tdStyle, width: 120 }}>
                  <ScoreBar score={c.score} />
                </td>
                <td style={tdStyle}><Badge status={c.status} /></td>
                <td style={tdStyle}>
                  <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                    {c.skills.slice(0, 3).map(s => (
                      <span key={s} style={{
                        background: 'var(--bg-4)', border: '1px solid var(--border)',
                        borderRadius: 20, padding: '1px 7px', fontSize: 11, color: 'var(--text-2)',
                      }}>{s}</span>
                    ))}
                  </div>
                </td>
                <td style={tdStyle}>
                  <button
                    style={{ fontSize: 12, color: 'var(--accent)', background: 'none', border: 'none', cursor: 'pointer' }}
                    onClick={e => { e.stopPropagation(); openDetail(c.id) }}
                  >
                    Detail →
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  )
}

const tdStyle = {
  padding: '10px 14px',
  borderBottom: '1px solid var(--border)',
  color: 'var(--text)',
  whiteSpace: 'nowrap',
}
