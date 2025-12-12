import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'

export default function SBOM() {
  const [projectName, setProjectName] = useState('')
  const [version, setVersion] = useState('1.0.0')
  const queryClient = useQueryClient()

  const { data: sboms } = useQuery({
    queryKey: ['sbom-documents'],
    queryFn: async () => {
      const res = await api.get('/sbom/documents')
      return res.data
    }
  })

  const generateMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post('/sbom/generate', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sbom-documents'] })
    }
  })

  const handleGenerate = () => {
    if (!projectName) return
    generateMutation.mutate({
      project_name: projectName,
      version,
      format: 'cyclonedx',
      dependencies: [
        { name: 'express', version: '4.18.2' },
        { name: 'axios', version: '1.6.2' }
      ]
    })
  }

  return (
    <div>
      <h1 style={{ fontSize: '32px', marginBottom: '30px' }}>SBOM Generation</h1>
      
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        marginBottom: '30px'
      }}>
        <h2 style={{ marginBottom: '15px' }}>Generate SBOM</h2>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <input
            type="text"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="Project name"
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
            onClick={handleGenerate}
            disabled={generateMutation.isPending}
            style={{
              padding: '8px 20px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {generateMutation.isPending ? 'Generating...' : 'Generate'}
          </button>
        </div>
      </div>

      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ marginBottom: '15px' }}>SBOM Documents</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {sboms?.sboms?.map((sbom: any) => (
            <div
              key={sbom.id}
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
                <div style={{ fontWeight: 'bold' }}>{sbom.project_name} v{sbom.version}</div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  Format: {sbom.format.toUpperCase()} • {new Date(sbom.created_at).toLocaleString()}
                </div>
              </div>
              <div style={{
                padding: '4px 12px',
                borderRadius: '4px',
                backgroundColor: sbom.has_attestation ? '#10b98120' : '#f59e0b20',
                color: sbom.has_attestation ? '#10b981' : '#f59e0b',
                fontSize: '12px',
                fontWeight: 'bold'
              }}>
                {sbom.has_attestation ? 'Attested' : 'No Attestation'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}


