// Shared UI primitives

export function Card({ children, style = {}, glow }) {
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      boxShadow: glow ? 'var(--shadow-glow)' : 'var(--shadow-card)',
      ...style,
    }}>
      {children}
    </div>
  )
}

export function Badge({ label, variant = 'default' }) {
  const map = {
    danger: { bg: 'var(--accent-red-dim)', color: 'var(--accent-red)', border: 'rgba(255,59,92,0.3)' },
    warning: { bg: 'var(--accent-amber-dim)', color: 'var(--accent-amber)', border: 'rgba(255,171,0,0.3)' },
    safe: { bg: 'var(--accent-green-dim)', color: 'var(--accent-green)', border: 'rgba(0,230,118,0.3)' },
    default: { bg: 'var(--bg-raised)', color: 'var(--text-secondary)', border: 'var(--border)' },
    cyan: { bg: 'var(--accent-cyan-dim)', color: 'var(--accent-cyan)', border: 'var(--border-active)' },
  }
  const s = map[variant] || map.default
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center',
      padding: '2px 10px', borderRadius: 20,
      background: s.bg, color: s.color,
      border: `1px solid ${s.border}`,
      fontSize: 11, fontWeight: 700, letterSpacing: '0.08em',
      textTransform: 'uppercase',
    }}>
      {label}
    </span>
  )
}

export function RiskMeter({ value, max = 100 }) {
  const pct = Math.min(100, Math.round((value / max) * 100))
  const color = pct >= 70 ? 'var(--accent-red)' : pct >= 40 ? 'var(--accent-amber)' : 'var(--accent-green)'
  return (
    <div style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 11, color: 'var(--text-secondary)', letterSpacing: '0.06em' }}>RISK SCORE</span>
        <span style={{ fontSize: 13, fontWeight: 700, color }}>{value}%</span>
      </div>
      <div style={{ height: 6, background: 'var(--bg-raised)', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{
          height: '100%', borderRadius: 3,
          width: `${pct}%`,
          background: `linear-gradient(90deg, ${color}88, ${color})`,
          boxShadow: `0 0 10px ${color}`,
          transition: 'width 0.8s cubic-bezier(0.4,0,0.2,1)',
        }} />
      </div>
    </div>
  )
}

export function Button({ children, onClick, variant = 'primary', disabled, style = {}, size = 'md' }) {
  const variants = {
    primary: {
      background: 'var(--accent-cyan)', color: 'var(--bg-void)',
      border: 'none', boxShadow: '0 0 20px rgba(0,229,255,0.25)',
    },
    ghost: {
      background: 'transparent', color: 'var(--text-secondary)',
      border: '1px solid var(--border)',
    },
    danger: {
      background: 'var(--accent-red-dim)', color: 'var(--accent-red)',
      border: '1px solid rgba(255,59,92,0.3)',
    },
  }
  const sizes = {
    sm: { padding: '6px 14px', fontSize: 12 },
    md: { padding: '10px 22px', fontSize: 13 },
    lg: { padding: '14px 32px', fontSize: 14 },
  }
  const s = variants[variant]
  const sz = sizes[size]
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        ...s, ...sz,
        borderRadius: 8,
        fontFamily: 'var(--font-display)',
        fontWeight: 700,
        letterSpacing: '0.04em',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        transition: 'all 0.15s ease',
        ...style,
      }}
    >
      {children}
    </button>
  )
}

export function Input({ value, onChange, placeholder, label, type = 'text', style = {} }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {label && (
        <label style={{ fontSize: 11, color: 'var(--text-secondary)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
          {label}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border)',
          borderRadius: 8,
          padding: '12px 16px',
          color: 'var(--text-primary)',
          fontSize: 13,
          outline: 'none',
          transition: 'border 0.15s',
          width: '100%',
          ...style,
        }}
        onFocus={e => e.target.style.borderColor = 'var(--border-active)'}
        onBlur={e => e.target.style.borderColor = 'var(--border)'}
      />
    </div>
  )
}

export function Textarea({ value, onChange, placeholder, label, rows = 6, style = {} }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {label && (
        <label style={{ fontSize: 11, color: 'var(--text-secondary)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
          {label}
        </label>
      )}
      <textarea
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        rows={rows}
        style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border)',
          borderRadius: 8,
          padding: '12px 16px',
          color: 'var(--text-primary)',
          fontSize: 13,
          outline: 'none',
          resize: 'vertical',
          transition: 'border 0.15s',
          width: '100%',
          ...style,
        }}
        onFocus={e => e.target.style.borderColor = 'var(--border-active)'}
        onBlur={e => e.target.style.borderColor = 'var(--border)'}
      />
    </div>
  )
}

export function Spinner() {
  return (
    <div style={{
      width: 20, height: 20,
      border: '2px solid var(--border)',
      borderTopColor: 'var(--accent-cyan)',
      borderRadius: '50%',
      animation: 'spin 0.7s linear infinite',
      display: 'inline-block',
    }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

export function StatCard({ label, value, icon: Icon, color = 'var(--accent-cyan)', sub }) {
  return (
    <Card style={{ padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 8 }}>
            {label}
          </div>
          <div style={{ fontSize: 30, fontWeight: 800, fontFamily: 'var(--font-display)', color }}>
            {value ?? '—'}
          </div>
          {sub && <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>{sub}</div>}
        </div>
        {Icon && (
          <div style={{
            width: 40, height: 40, borderRadius: 10,
            background: `${color}18`,
            border: `1px solid ${color}30`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Icon size={18} color={color} />
          </div>
        )}
      </div>
    </Card>
  )
}
