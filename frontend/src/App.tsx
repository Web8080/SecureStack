import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import APISecurity from './components/APISecurity'
import Compliance from './components/Compliance'
import Dependencies from './components/Dependencies'
import SBOM from './components/SBOM'
import Layout from './components/Layout'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/api-security" element={<APISecurity />} />
          <Route path="/compliance" element={<Compliance />} />
          <Route path="/dependencies" element={<Dependencies />} />
          <Route path="/sbom" element={<SBOM />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App


