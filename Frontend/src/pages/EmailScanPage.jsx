import { useState } from 'react'
import { scanEmail } from '../services/api'
import { Card, Button, Input, Textarea, Spinner } from '../components/ui'
import { ScanResultCard } from '../components/ui/ScanResultCard'
import { Mail, Zap, Info } from 'lucide-react'

const EXAMPLES = [
  {
    label: 'Phishing — PayPal Alert',
    subject: 'URGENT: Your PayPal account has been suspended',
    sender: 'support-alert@paypal-verify.ml',
    body: `Dear Customer,

We have detected unusual activity on your account. Your account has been suspended.

Please verify your credentials IMMEDIATELY by clicking the link below:
http://paypal-secure-login.xyz/verify?id=12345

If you do not confirm your password within 24 hours, your account will be permanently deleted.

Provide your bank account details and social security number to restore access.

PayPal Security Team`,
  },
  {
    label: 'Legitimate — GitHub Notification',
    subject: 'Your pull request was merged',
    sender: 'notifications@github.com',
    body: `Hi there,

Your pull request #42 "Fix login bug" was successfully merged into main by reviewer.

You can view the changes at https://github.com/user/repo/pull/42

Thanks for contributing!
The GitHub Team`,
  },
]

export default function EmailScanPage() {
  const [subject, setSubject] = useState('')
  const [sender, setSender] = useState('')
  const [body, setBody] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleScan = async () => {
    if (!subject.trim() && !body.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await scanEmail(subject.trim(), body.trim(), sender.trim())
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Scan failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const loadExample = (ex) => {
    setSubject(ex.subject)
    setSender(ex.sender)
    setBody(ex.body)
    setResult(null)
  }

  return (
    <div style={{ maxWidth: 700, display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <Mail size={20} color="var(--accent-cyan)" />
          <h1 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 22, letterSpacing: '-0.02em' }}>
            Email Scanner
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
          Paste email content below to detect phishing attempts via NLP pattern matching and embedded URL analysis.
        </p>
      </div>

      {/* Examples */}
      <Card style={{ padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Info size={13} color="var(--text-secondary)" />
          <span style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Load an example
          </span>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {EXAMPLES.map(ex => (
            <button
              key={ex.label}
              onClick={() => loadExample(ex)}
              style={{
                padding: '7px 14px', borderRadius: 6,
                background: 'var(--bg-surface)', border: '1px solid var(--border)',
                color: 'var(--text-secondary)', fontSize: 12,
                cursor: 'pointer', fontFamily: 'var(--font-mono)',
                transition: 'all 0.1s',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--border-active)'; e.currentTarget.style.color = 'var(--accent-cyan)' }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-secondary)' }}
            >
              {ex.label}
            </button>
          ))}
        </div>
      </Card>

      {/* Form */}
      <Card style={{ padding: 24 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Input label="Sender (optional)" value={sender} onChange={e => setSender(e.target.value)} placeholder="noreply@example.com" />
          <Input label="Subject" value={subject} onChange={e => setSubject(e.target.value)} placeholder="Email subject line..." />
          <Textarea label="Email Body" value={body} onChange={e => setBody(e.target.value)} placeholder="Paste the email body content here..." rows={8} />

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Button onClick={handleScan} disabled={loading || (!subject.trim() && !body.trim())} size="md">
              {loading ? <><Spinner />&nbsp; Analysing…</> : <><Zap size={13} style={{ display: 'inline', marginRight: 6 }} />Analyse Email</>}
            </Button>
            <button
              onClick={() => { setSubject(''); setSender(''); setBody(''); setResult(null) }}
              style={{ fontSize: 12, color: 'var(--text-muted)', cursor: 'pointer', background: 'none', border: 'none' }}
            >
              Clear all
            </button>
          </div>

          {error && (
            <div style={{ background: 'var(--accent-red-dim)', border: '1px solid rgba(255,59,92,0.2)', borderRadius: 6, padding: '10px 14px', fontSize: 12, color: 'var(--accent-red)' }}>
              {error}
            </div>
          )}
        </div>
      </Card>

      <ScanResultCard result={result} type="email" />
    </div>
  )
}
