import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'

export default function APISecurity() {
  const [endpoint, setEndpoint] = useState('')
  const [method, setMethod] = useState('GET')
  const queryClient = useQueryClient()

  const { data: tests } = useQuery({
    queryKey: ['api-tests'],
    queryFn: async () => {
      const res = await api.get('/api-security/tests')
      return res.data
    }
  })

  const testMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post('/api-security/test', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-tests'] })
    }
  })

  const handleTest = () => {
    if (!endpoint) return
    testMutation.mutate({
      endpoint,
      method,
      test_types: ['contract', 'fuzzing', 'rate_limit']
    })
  }

  return (
    <div>
      <h1 style={{ fontSize: '32px', marginBottom: '30px' }}>API Security Testing</h1>
      
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        marginBottom: '30px'
      }}>
        <h2 style={{ marginBottom: '15px' }}>Run Security Test</h2>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value)}
            style={{
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #e2e8f0'
            }}
          >
            <option>GET</option>
            <option>POST</option>
            <option>PUT</option>
            <option>DELETE</option>
          </select>
          <input
            type="text"
            value={endpoint}
            onChange={(e) => setEndpoint(e.target.value)}
            placeholder="https://api.example.com/users"
            style={{
              flex: 1,
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #e2e8f0'
            }}
          />
          <button
            onClick={handleTest}
            disabled={testMutation.isPending}
            style={{
              padding: '8px 20px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {testMutation.isPending ? 'Testing...' : 'Run Test'}
          </button>
        </div>
      </div>

      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ marginBottom: '15px' }}>Test History</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {tests?.tests?.map((test: any) => (
            <div
              key={test.id}
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
                <div style={{ fontWeight: 'bold' }}>{test.method} {test.endpoint}</div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  {new Date(test.created_at).toLocaleString()}
                </div>
              </div>
              <div style={{
                padding: '4px 12px',
                borderRadius: '4px',
                backgroundColor: test.status === 'passed' ? '#10b98120' : '#ef444420',
                color: test.status === 'passed' ? '#10b981' : '#ef4444',
                fontSize: '12px',
                fontWeight: 'bold'
              }}>
                {test.status.toUpperCase()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}


