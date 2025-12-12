import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'

export default function Compliance() {
  const [framework, setFramework] = useState('SOC 2')
  const queryClient = useQueryClient()

  const { data: checks } = useQuery({
    queryKey: ['compliance-checks'],
    queryFn: async () => {
      const res = await api.get('/compliance/checks')
      return res.data
    }
  })

  const checkMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post('/compliance/check', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compliance-checks'] })
    }
  })

  const handleCheck = () => {
    checkMutation.mutate({
      framework,
      resource_type: 'application',
      resource_data: {
        access_control_enabled: true,
        encryption_at_rest: true,
        encryption_in_transit: true,
        logging_enabled: true,
        monitoring_enabled: true
      }
    })
  }

  return (
    <div>
      <h1 style={{ fontSize: '32px', marginBottom: '30px' }}>Compliance-as-Code</h1>
      
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        marginBottom: '30px'
      }}>
        <h2 style={{ marginBottom: '15px' }}>Run Compliance Check</h2>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <select
            value={framework}
            onChange={(e) => setFramework(e.target.value)}
            style={{
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #e2e8f0',
              flex: 1
            }}
          >
            <option>SOC 2</option>
            <option>PCI-DSS</option>
            <option>GDPR</option>
          </select>
          <button
            onClick={handleCheck}
            disabled={checkMutation.isPending}
            style={{
              padding: '8px 20px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {checkMutation.isPending ? 'Checking...' : 'Run Check'}
          </button>
        </div>
      </div>

      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ marginBottom: '15px' }}>Compliance History</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {checks?.checks?.map((check: any) => (
            <div
              key={check.id}
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
                <div style={{ fontWeight: 'bold' }}>{check.framework} - {check.policy_name}</div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  {new Date(check.created_at).toLocaleString()}
                </div>
              </div>
              <div style={{
                padding: '4px 12px',
                borderRadius: '4px',
                backgroundColor: check.status === 'passed' ? '#10b98120' : '#ef444420',
                color: check.status === 'passed' ? '#10b981' : '#ef4444',
                fontSize: '12px',
                fontWeight: 'bold'
              }}>
                {check.status.toUpperCase()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}


