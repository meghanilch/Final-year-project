import { AlertTriangle, CheckCircle, XCircle, ChevronDown, ChevronUp, Shield } from 'lucide-react'
import { useState } from 'react'
import { Badge, RiskMeter, Card } from './index'

const riskConfig = {
  danger: {
    icon: XCircle, color: 'var(--accent-red)',
    bg: 'var(--accent-red-dim)', border: 'rgba(255,59,92,0.25)',
    label: 'PHISHING DETECTED', shadow: 'var(--shadow-danger)',
  },
  warning: {
    icon: AlertTriangle, color: 'var(--accent-amber)',
    bg: 'var(--accent-amber-dim)', border: 'rgba(255,171,0,0.25)',
    label: 'SUSPICIOUS', shadow: '0 0 30px rgba(255,171,0,0.15)',
  },
  safe: {
    icon: CheckCircle, color: 'var(--accent-green)',
    bg: 'var(--accent-green-dim)', border: 'rgba(0,230,118,0.25)',
    label: 'SAFE', shadow: 'var(--shadow-safe)',
  },
}

export function ScanResultCard({ result, type }) {
  const [showDetails, setShowDetails] = useState(false)
  if (!result) return null

  const risk = riskConfig[result.risk_level] || riskConfig.safe
  const Icon = risk.icon
  const score = type === 'url' ? result.phishing_probability : result.phishing_score

  return (
    <div className="animate-slide-up" style={{ marginTop: 24 }}>
      {/* Main verdict */}
      <div style={{
        background: risk.bg,
        border: `1px solid ${risk.border}`,
        borderRadius: 'var(--radius-lg)',
        padding: 24,
        boxShadow: risk.shadow,
        marginBottom: 16,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
          <div style={{
            width: 52, height: 52, borderRadius: '50%',
            background: `${risk.color}20`,
            border: `2px solid ${risk.color}50`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
          }}>
            <Icon size={24} color={risk.color} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 18, color: risk.color, letterSpacing: '-0.01em' }}>
              {risk.label}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
              {type === 'url'
                ? `Prediction: ${result.prediction} — Confidence: ${result.confidence}%`
                : `Prediction: ${result.prediction} — Score: ${result.phishing_score}/100`}
            </div>
          </div>
          <Badge
            label={result.risk_level.toUpperCase()}
            variant={result.risk_level === 'safe' ? 'safe' : result.risk_level === 'danger' ? 'danger' : 'warning'}
          />
        </div>

        <RiskMeter value={score ?? 0} />
      </div>

      {/* Indicators */}
      {result.indicators?.length > 0 && (
        <Card style={{ marginBottom: 16, overflow: 'hidden' }}>
          <div
            style={{
              padding: '14px 20px',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              cursor: 'pointer', userSelect: 'none',
            }}
            onClick={() => setShowDetails(v => !v)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Shield size={14} color="var(--accent-amber)" />
              <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 13 }}>
                {result.indicators.length} Threat Indicator{result.indicators.length !== 1 ? 's' : ''} Found
              </span>
            </div>
            {showDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </div>
          {showDetails && (
            <div style={{ borderTop: '1px solid var(--border)', padding: '12px 20px', display: 'flex', flexDirection: 'column', gap: 8 }}>
              {result.indicators.map((ind, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                  <span style={{ color: 'var(--accent-amber)', marginTop: 2, flexShrink: 0 }}>▸</span>
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{ind}</span>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Phishing URLs in email */}
      {type === 'email' && result.phishing_urls?.length > 0 && (
        <Card style={{ padding: 20, marginBottom: 16 }}>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 13, marginBottom: 12, color: 'var(--accent-red)' }}>
            ⚠ Phishing URLs Found in Body
          </div>
          {result.phishing_urls.map((u, i) => (
            <div key={i} style={{
              background: 'var(--accent-red-dim)',
              border: '1px solid rgba(255,59,92,0.2)',
              borderRadius: 6, padding: '8px 12px', marginBottom: 8,
              fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent-red)',
              wordBreak: 'break-all',
            }}>
              {u.url}
            </div>
          ))}
        </Card>
      )}

      {/* VirusTotal */}
      {result.virustotal && (
        <Card style={{ padding: 20 }}>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 13, marginBottom: 12 }}>
            VirusTotal Results
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 8 }}>
            {Object.entries(result.virustotal).map(([k, v]) => (
              <div key={k} style={{
                background: 'var(--bg-surface)', borderRadius: 6, padding: '8px 10px', textAlign: 'center',
                border: '1px solid var(--border)',
              }}>
                <div style={{ fontSize: 18, fontWeight: 800, fontFamily: 'var(--font-display)', color: k === 'malicious' ? 'var(--accent-red)' : k === 'suspicious' ? 'var(--accent-amber)' : 'var(--text-secondary)' }}>{v}</div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{k}</div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
