# SecureStack JavaScript/TypeScript Client

JavaScript and TypeScript client library for the SecureStack DevSecOps Platform.

## Installation

```bash
npm install @securestack/client
```

Or install from source:

```bash
cd clients/javascript
npm install
npm run build
```

## Usage

### JavaScript

```javascript
import { SecureStackClient } from '@securestack/client';

const client = new SecureStackClient({
  apiUrl: 'http://localhost:8000'
});

// Test API security
const result = await client.testApiSecurity({
  endpoint: 'https://api.example.com/users',
  method: 'GET',
  testTypes: ['contract', 'fuzzing', 'rate_limit']
});
console.log(`Test status: ${result.status}`);

// Check compliance
const compliance = await client.checkCompliance({
  framework: 'SOC 2',
  resourceType: 'application',
  resourceData: {
    access_control_enabled: true,
    encryption_at_rest: true,
    encryption_in_transit: true
  }
});
console.log(`Compliance status: ${compliance.status}`);

// Scan dependency
const scan = await client.scanDependency({
  packageName: 'express',
  version: '4.18.2',
  ecosystem: 'npm'
});
console.log(`Risk score: ${scan.risk_score}`);

// Generate SBOM
const sbom = await client.generateSBOM({
  projectName: 'my-app',
  version: '1.0.0',
  dependencies: [
    { name: 'express', version: '4.18.2' },
    { name: 'axios', version: '1.6.2' }
  ]
});
console.log(`SBOM generated: ${sbom.sbom_id}`);
```

### TypeScript

```typescript
import { SecureStackClient } from '@securestack/client';

const client = new SecureStackClient({
  apiUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

const result = await client.testApiSecurity({
  endpoint: 'https://api.example.com/users',
  method: 'GET'
});
```

## API Reference

See the main SecureStack documentation for full API reference.


