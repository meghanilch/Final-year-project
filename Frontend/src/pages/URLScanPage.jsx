import { useState } from 'react'
import { scanURL } from '../services/api'
import { Card, Button, Input, Spinner } from '../components/ui'
import { ScanResultCard } from '../components/ui/ScanResultCard'
import { Link2, Zap, Info } from 'lucide-react'

const EXAMPLES = [
  'https://www.google.com',
  'http://paypal-secure-login.xyz/verify?id=12345',
  'http://192.168.1.1/admin/login.php',
  'https://github.com/user/repo',
  'http://amazon-prize-winner.click/claim',
]

export default function URLScanPage() {
  const [url, setUrl] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleScan = async () => {
    if (!url.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await scanURL(url.trim())
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Scan failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 700, display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <Link2 size={20} color="var(--accent-cyan)" />
          <h1 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 22, letterSpacing: '-0.02em' }}>
            URL Scanner
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
          Analyse any URL for phishing indicators using our ML model with 25+ extracted features.
        </p>
      </div>

      {/* Input card */}
      <Card style={{ padding: 24 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Input
            label="Target URL"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="https://example.com/path?query=value"
            onKeyDown={e => e.key === 'Enter' && handleScan()}
          />

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Button onClick={handleScan} disabled={loading || !url.trim()} size="md">
              {loading ? <><Spinner />&nbsp; Scanning…</> : <><Zap size={13} style={{ display: 'inline', marginRight: 6 }} />Scan URL</>}
            </Button>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              Press Enter to scan
            </span>
          </div>

          {error && (
            <div style={{
              background: 'var(--accent-red-dim)', border: '1px solid rgba(255,59,92,0.2)',
              borderRadius: 6, padding: '10px 14px', fontSize: 12, color: 'var(--accent-red)',
            }}>
              {error}
            </div>
          )}
        </div>
      </Card>

      {/* Examples */}
      <Card style={{ padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Info size={13} color="var(--text-secondary)" />
          <span style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Example URLs to try
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {EXAMPLES.map(ex => (
            <div
              key={ex}
              onClick={() => setUrl(ex)}
              style={{
                padding: '7px 12px',
                borderRadius: 6,
                background: 'var(--bg-surface)',
                border: '1px solid var(--border)',
                fontSize: 12,
                color: 'var(--text-code)',
                cursor: 'pointer',
                fontFamily: 'var(--font-mono)',
                wordBreak: 'break-all',
                transition: 'border-color 0.1s',
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border-active)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
            >
              {ex}
            </div>
          ))}
        </div>
      </Card>

      {/* Result */}
      <ScanResultCard result={result} type="url" />
    </div>
  )
}
