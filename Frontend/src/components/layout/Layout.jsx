import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { Shield, Link2, Mail, Clock, LayoutDashboard, Activity } from 'lucide-react'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/scan/url', label: 'URL Scanner', icon: Link2 },
  { to: '/scan/email', label: 'Email Scanner', icon: Mail },
  { to: '/history', label: 'Scan History', icon: Clock },
]

export default function Layout() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <TopBar />
        <div style={{ flex: 1, overflowY: 'auto', padding: '32px' }}>
          <Outlet />
        </div>
      </main>
    </div>
  )
}

function Sidebar() {
  return (
    <aside style={{
      width: '240px',
      flexShrink: 0,
      background: 'var(--bg-deep)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 0',
    }}>
      {/* Logo */}
      <div style={{ padding: '0 20px 32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 8,
            background: 'var(--accent-cyan-dim)',
            border: '1px solid var(--border-active)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 16px rgba(0,229,255,0.2)',
          }}>
            <Shield size={18} color="var(--accent-cyan)" />
          </div>
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 16, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              PhishGuard
            </div>
            <div style={{ fontSize: 10, color: 'var(--accent-cyan)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
              AI System
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '0 12px', display: 'flex', flexDirection: 'column', gap: 4 }}>
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} style={({ isActive }) => ({
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '10px 12px', borderRadius: 8,
            color: isActive ? 'var(--accent-cyan)' : 'var(--text-secondary)',
            background: isActive ? 'var(--accent-cyan-dim)' : 'transparent',
            border: isActive ? '1px solid var(--border-active)' : '1px solid transparent',
            fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 13,
            transition: 'all 0.15s ease',
            textDecoration: 'none',
          })}>
            <Icon size={15} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border)' }}>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', lineHeight: 1.8 }}>
          <div style={{ color: 'var(--text-secondary)', marginBottom: 2, fontFamily: 'var(--font-display)', fontWeight: 600 }}>Final Year Project</div>
          <div>AI/ML-Based Phishing Detection System</div>
        </div>
      </div>
    </aside>
  )
}

function TopBar() {
  const location = useLocation()
  const titles = {
    '/dashboard': 'System Dashboard',
    '/scan/url': 'URL Scanner',
    '/scan/email': 'Email Scanner',
    '/history': 'Scan History',
  }
  const title = titles[location.pathname] || 'PhishGuard'

  return (
    <header style={{
      height: 56,
      background: 'var(--bg-deep)',
      borderBottom: '1px solid var(--border)',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 32px', flexShrink: 0,
    }}>
      <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 15, color: 'var(--text-primary)' }}>
        {title}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--accent-green)', boxShadow: '0 0 8px var(--accent-green)', animation: 'pulse-ring 2s infinite' }} />
        <span style={{ fontSize: 11, color: 'var(--text-secondary)', letterSpacing: '0.06em' }}>
          <Activity size={11} style={{ display: 'inline', marginRight: 4 }} />
          
        </span>
      </div>
    </header>
  )
}
