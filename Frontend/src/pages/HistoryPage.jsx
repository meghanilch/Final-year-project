import { useState, useEffect } from 'react'
import { getHistory, deleteHistoryItem, clearHistory } from '../services/api'
import { Card, Badge, Button } from '../components/ui'
import { Clock, Trash2, Link2, Mail, RefreshCw } from 'lucide-react'

export default function HistoryPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  const load = () => {
    setLoading(true)
    const params = filter !== 'all' ? { scan_type: filter } : {}
    getHistory({ limit: 50, ...params })
      .then(setItems)
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [filter])

  const handleDelete = async (id) => {
    await deleteHistoryItem(id)
    setItems(prev => prev.filter(i => i.id !== id))
  }

  const handleClear = async () => {
    if (!window.confirm('Clear all history?')) return
    await clearHistory()
    setItems([])
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <Clock size={20} color="var(--accent-cyan)" />
            <h1 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 22, letterSpacing: '-0.02em' }}>
              Scan History
            </h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>All previous URL and email scans</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Button onClick={load} variant="ghost" size="sm">
            <RefreshCw size={12} style={{ display: 'inline', marginRight: 6 }} />Refresh
          </Button>
          <Button onClick={handleClear} variant="danger" size="sm">
            <Trash2 size={12} style={{ display: 'inline', marginRight: 6 }} />Clear All
          </Button>
        </div>
      </div>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: 6 }}>
        {['all', 'url', 'email'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '6px 16px', borderRadius: 6,
              background: filter === f ? 'var(--accent-cyan-dim)' : 'var(--bg-surface)',
              border: filter === f ? '1px solid var(--border-active)' : '1px solid var(--border)',
              color: filter === f ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              fontSize: 12, fontFamily: 'var(--font-display)', fontWeight: 600,
              cursor: 'pointer', textTransform: 'capitalize',
              transition: 'all 0.15s',
            }}
          >
            {f === 'all' ? 'All' : f === 'url' ? '🔗 URLs' : '📧 Emails'}
          </button>
        ))}
      </div>

      {loading && (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
          <div style={{ width: 32, height: 32, border: '2px solid var(--border)', borderTopColor: 'var(--accent-cyan)', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      )}

      {!loading && items.length === 0 && (
        <Card style={{ padding: 40, textAlign: 'center' }}>
          <Clock size={32} color="var(--text-muted)" style={{ marginBottom: 12 }} />
          <p style={{ fontFamily: 'var(--font-display)', fontWeight: 700, marginBottom: 4 }}>No scans yet</p>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Run a URL or email scan to see history here</p>
        </Card>
      )}

      {!loading && items.map(item => (
        <HistoryItem key={item.id} item={item} onDelete={handleDelete} />
      ))}
    </div>
  )
}

function HistoryItem({ item, onDelete }) {
  const isUrl = item.scan_type === 'url'
  const score = isUrl ? item.phishing_probability : item.phishing_score
  const riskVariant = item.risk_level === 'safe' ? 'safe' : item.risk_level === 'danger' ? 'danger' : 'warning'

  return (
    <Card style={{ padding: 18 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, flex: 1, minWidth: 0 }}>
          <div style={{
            width: 34, height: 34, borderRadius: 8, flexShrink: 0, marginTop: 2,
            background: isUrl ? 'var(--accent-cyan-dim)' : 'rgba(191,128,255,0.12)',
            border: `1px solid ${isUrl ? 'var(--border-active)' : 'rgba(191,128,255,0.25)'}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {isUrl ? <Link2 size={14} color="var(--accent-cyan)" /> : <Mail size={14} color="#bf80ff" />}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-code)', wordBreak: 'break-all', marginBottom: 4 }}>
              {isUrl ? item.url : item.subject || '(no subject)'}
            </div>
            {!isUrl && item.sender && (
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>
                From: {item.sender}
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <Badge label={item.prediction} variant={item.prediction === 'phishing' ? 'danger' : 'safe'} />
              <Badge label={item.risk_level} variant={riskVariant} />
              {score != null && (
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  Score: {score}%
                </span>
              )}
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8, flexShrink: 0 }}>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
            {item.created_at ? new Date(item.created_at).toLocaleString() : ''}
          </span>
          <button
            onClick={() => onDelete(item.id)}
            style={{ color: 'var(--text-muted)', cursor: 'pointer', background: 'none', border: 'none', padding: 4, borderRadius: 4, transition: 'color 0.1s' }}
            onMouseEnter={e => e.currentTarget.style.color = 'var(--accent-red)'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
          >
            <Trash2 size={13} />
          </button>
        </div>
      </div>
    </Card>
  )
}
