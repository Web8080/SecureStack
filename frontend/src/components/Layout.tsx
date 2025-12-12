import { Link, useLocation } from 'react-router-dom'
import { Shield, TestTube, FileCheck, Package, FileText } from 'lucide-react'
import { ReactNode } from 'react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: Shield },
    { path: '/api-security', label: 'API Security', icon: TestTube },
    { path: '/compliance', label: 'Compliance', icon: FileCheck },
    { path: '/dependencies', label: 'Dependencies', icon: Package },
    { path: '/sbom', label: 'SBOM', icon: FileText },
  ]

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside style={{
        width: '250px',
        backgroundColor: '#1e293b',
        color: 'white',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <div style={{ marginBottom: '30px' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>SecureStack</h1>
          <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '5px' }}>
            DevSecOps Platform
          </p>
        </div>
        
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '12px',
                  borderRadius: '6px',
                  textDecoration: 'none',
                  color: isActive ? '#fff' : '#cbd5e1',
                  backgroundColor: isActive ? '#334155' : 'transparent',
                  transition: 'all 0.2s'
                }}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>
      </aside>
      
      <main style={{ flex: 1, padding: '30px', overflow: 'auto' }}>
        {children}
      </main>
    </div>
  )
}


