import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'

export default function Dependencies() {
  const [packageName, setPackageName] = useState('')
  const [version, setVersion] = useState('latest')
  const queryClient = useQueryClient()

  const { data: scans } = useQuery({
    queryKey: ['dependency-scans'],
    queryFn: async () => {
      const res = await api.get('/dependencies/scans')
      return res.data
    }
  })

  const scanMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post('/dependencies/scan', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dependency-scans'] })
    }
  })

  const handleScan = () => {
    if (!packageName) return
    scanMutation.mutate({
      package_name: packageName,
      version,
      ecosystem: 'npm'
    })
  }

  return (
    <div>
      <h1 style={{ fontSize: '32px', marginBottom: '30px' }}>Dependency Management</h1>
      
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        marginBottom: '30px'
      }}>
        <h2 style={{ marginBottom: '15px' }}>Scan Dependency</h2>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <input
            type="text"
            value={packageName}
            onChange={(e) => setPackageName(e.target.value)}
            placeholder="Package name (e.g., express)"
            style={{
              flex: 1,
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #e2e8f0'
            }}
          />
          <input
            type="text"
            value={version}
            onChange={(e) => setVersion(e.target.value)}
            placeholder="Version"
            style={{
              width: '150px',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #e2e8f0'
            }}
          />
          <button
            onClick={handleScan}
            disabled={scanMutation.isPending}
            style={{
              padding: '8px 20px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {scanMutation.isPending ? 'Scanning...' : 'Scan'}
          </button>
        </div>
      </div>

      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ marginBottom: '15px' }}>Scan History</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {scans?.scans?.map((scan: any) => (
            <div
              key={scan.id}
              style={{
                padding: '15px',
                border: '1px solid #e2e8f0',
                borderRadius: '4px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div>
                <div style={{ fontWeight: 'bold' }}>{scan.package_name}@{scan.version}</div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  {scan.vulnerability_count} vulnerabilities found
                </div>
              </div>
              <div style={{
                padding: '4px 12px',
                borderRadius: '4px',
                backgroundColor: scan.risk_score >= 7 ? '#ef444420' : '#10b98120',
                color: scan.risk_score >= 7 ? '#ef4444' : '#10b981',
                fontSize: '12px',
                fontWeight: 'bold'
              }}>
                Risk: {scan.risk_score.toFixed(1)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}


