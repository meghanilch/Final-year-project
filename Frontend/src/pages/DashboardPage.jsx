import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import { getStats } from '../services/api'
import { StatCard, Card } from '../components/ui'
import { Shield, AlertTriangle, CheckCircle, Link2, Mail, TrendingUp } from 'lucide-react'

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingState />
  if (!stats) return <EmptyState />

  const pieData = [
    { name: 'Phishing', value: stats.phishing_detected, color: '#ff3b5c' },
    { name: 'Legitimate', value: stats.legitimate_detected, color: '#00e676' },
  ]
  const riskData = [
    { name: 'Danger', value: stats.risk_breakdown.danger, color: '#ff3b5c' },
    { name: 'Warning', value: stats.risk_breakdown.warning, color: '#ffab00' },
    { name: 'Safe', value: stats.risk_breakdown.safe, color: '#00e676' },
  ]
  const typeData = [
    { name: 'URL Scans', value: stats.url_scans, color: '#00e5ff' },
    { name: 'Email Scans', value: stats.email_scans, color: '#bf80ff' },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header */}
      <div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 24, letterSpacing: '-0.02em', marginBottom: 4 }}>
          System Overview
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
          Real-time statistics from the phishing detection engine
        </p>
      </div>

      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
        <StatCard label="Total Scans" value={stats.total_scans} icon={Shield} color="var(--accent-cyan)" />
        <StatCard label="Phishing Found" value={stats.phishing_detected} icon={AlertTriangle} color="var(--accent-red)" />
        <StatCard label="Legitimate" value={stats.legitimate_detected} icon={CheckCircle} color="var(--accent-green)" />
        <StatCard label="URL Scans" value={stats.url_scans} icon={Link2} color="var(--accent-cyan)" />
        <StatCard label="Email Scans" value={stats.email_scans} icon={Mail} color="#bf80ff" />
        <StatCard label="Detection Rate" value={`${stats.detection_rate}%`} icon={TrendingUp} color="var(--accent-amber)" sub="of all scans flagged" />
      </div>

      {/* Charts row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
        <ChartCard title="Prediction Split" subtitle="Phishing vs Legitimate">
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" strokeWidth={0}>
                {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <Legend data={pieData} />
        </ChartCard>

        <ChartCard title="Risk Breakdown" subtitle="Severity distribution">
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={riskData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} />
              <YAxis tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} />
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="value" radius={[4,4,0,0]}>
                {riskData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Scan Types" subtitle="URL vs Email distribution">
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={typeData} cx="50%" cy="50%" outerRadius={80} dataKey="value" strokeWidth={0}>
                {typeData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <Legend data={typeData} />
        </ChartCard>
      </div>
    </div>
  )
}

function ChartCard({ title, subtitle, children }) {
  return (
    <Card style={{ padding: 20 }}>
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 14 }}>{title}</div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{subtitle}</div>
      </div>
      {children}
    </Card>
  )
}

function Legend({ data }) {
  return (
    <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginTop: 12 }}>
      {data.map(d => (
        <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: d.color }} />
          <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{d.name}</span>
        </div>
      ))}
    </div>
  )
}

function LoadingState() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 400, gap: 16 }}>
      <div style={{ width: 40, height: 40, border: '3px solid var(--border)', borderTopColor: 'var(--accent-cyan)', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
      <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Loading statistics...</p>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

function EmptyState() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 400, gap: 12, color: 'var(--text-secondary)' }}>
      <Shield size={40} color="var(--text-muted)" />
      <p style={{ fontFamily: 'var(--font-display)', fontWeight: 700 }}>No data yet</p>
      <p style={{ fontSize: 13 }}>Run some scans to see statistics here</p>
    </div>
  )
}
