import { getScoreColor, getStatusColor } from '../../data/candidates'

export function Badge({ status }) {
  const c = getStatusColor(status)
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center',
      padding: '2px 8px', borderRadius: 20,
      fontSize: 11, fontWeight: 500, whiteSpace: 'nowrap',
      background: c.bg, color: c.text,
    }}>
      {status}
    </span>
  )
}

export function ScoreBar({ score, height = 4 }) {
  const color = getScoreColor(score)
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{
        flex: 1, height, background: 'var(--bg-4)',
        borderRadius: 3, overflow: 'hidden',
      }}>
        <div style={{
          width: `${score}%`, height: '100%',
          background: color, borderRadius: 3,
          transition: 'width .4s ease',
        }} />
      </div>
      <span style={{
        fontSize: 12, fontWeight: 500, minWidth: 30,
        color, fontVariantNumeric: 'tabular-nums',
      }}>
        {score}%
      </span>
    </div>
  )
}

export function Avatar({ name, initials, color }) {
  return (
    <div style={{
      width: 30, height: 30, borderRadius: '50%',
      background: color?.bg || 'var(--bg-4)',
      color: color?.text || 'var(--text)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 11, fontWeight: 600, flexShrink: 0,
    }}>
      {initials || name?.slice(0, 2).toUpperCase()}
    </div>
  )
}

export function SkillTag({ label }) {
  return (
    <span style={{
      background: 'var(--bg-4)', border: '1px solid var(--border)',
      borderRadius: 20, padding: '2px 8px',
      fontSize: 11, color: 'var(--text-2)',
      display: 'inline-block',
    }}>
      {label}
    </span>
  )
}

export function Card({ children, style = {} }) {
  return (
    <div style={{
      background: 'var(--bg-2)', border: '1px solid var(--border)',
      borderRadius: 'var(--border-radius-lg, 12px)',
      overflow: 'hidden', ...style,
    }}>
      {children}
    </div>
  )
}

export function CardHeader({ title, right, style = {} }) {
  return (
    <div style={{
      padding: '10px 16px',
      borderBottom: '1px solid var(--border)',
      display: 'flex', alignItems: 'center',
      justifyContent: 'space-between', gap: 8, ...style,
    }}>
      <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text)' }}>
        {title}
      </span>
      {right}
    </div>
  )
}

export function Btn({ children, onClick, variant = 'default', size = 'md', style = {}, disabled }) {
  const base = {
    display: 'inline-flex', alignItems: 'center', gap: 6,
    border: '1px solid var(--border-2)',
    borderRadius: 8, cursor: disabled ? 'not-allowed' : 'pointer',
    fontFamily: 'var(--font)', fontWeight: 500,
    transition: 'var(--transition)', opacity: disabled ? .5 : 1,
  }
  const sizes = {
    sm: { padding: '4px 10px', fontSize: 12 },
    md: { padding: '6px 14px', fontSize: 13 },
    lg: { padding: '9px 18px', fontSize: 14 },
  }
  const variants = {
    default: { background: 'var(--bg-3)', color: 'var(--text-2)' },
    primary: { background: 'var(--accent)', color: '#fff', border: 'none' },
    ghost: { background: 'transparent', color: 'var(--text-2)', border: '1px solid transparent' },
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{ ...base, ...sizes[size], ...variants[variant], ...style }}
    >
      {children}
    </button>
  )
}

export function StatCard({ label, value, sub, icon }) {
  return (
    <div style={{
      background: 'var(--bg-2)', border: '1px solid var(--border)',
      borderRadius: 12, padding: '14px 16px',
    }}>
      <div style={{ fontSize: 11, color: 'var(--text-3)', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 600, color: 'var(--text)' }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 3 }}>{sub}</div>}
    </div>
  )
}
