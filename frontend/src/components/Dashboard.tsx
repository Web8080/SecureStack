import { useQuery } from '@tanstack/react-query'
import { Shield, AlertTriangle, CheckCircle, Package } from 'lucide-react'
import api from '../services/api'

export default function Dashboard() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => api.get('/health')
  })

  return (
    <div>
      <h1 style={{ fontSize: '32px', marginBottom: '30px' }}>Dashboard</h1>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '20px',
        marginBottom: '30px'
      }}>
        <Card
          title="API Security"
          value="Active"
          icon={Shield}
          color="#3b82f6"
        />
        <Card
          title="Compliance"
          value="Monitoring"
          icon={CheckCircle}
          color="#10b981"
        />
        <Card
          title="Dependencies"
          value="Scanned"
          icon={Package}
          color="#f59e0b"
        />
        <Card
          title="SBOM"
          value="Generated"
          icon={Shield}
          color="#8b5cf6"
        />
      </div>

      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ marginBottom: '15px' }}>System Status</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: health ? '#10b981' : '#ef4444'
          }} />
          <span>{health ? 'All systems operational' : 'Checking status...'}</span>
        </div>
      </div>
    </div>
  )
}

function Card({ title, value, icon: Icon, color }: any) {
  return (
    <div style={{
      backgroundColor: 'white',
      padding: '20px',
      borderRadius: '8px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      display: 'flex',
      alignItems: 'center',
      gap: '15px'
    }}>
      <div style={{
        width: '50px',
        height: '50px',
        borderRadius: '8px',
        backgroundColor: `${color}20`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Icon size={24} color={color} />
      </div>
      <div>
        <div style={{ fontSize: '14px', color: '#64748b' }}>{title}</div>
        <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#1e293b' }}>
          {value}
        </div>
      </div>
    </div>
  )
}


