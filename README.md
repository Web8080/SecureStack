# SecureStack

**SecureStack** is a unified DevSecOps platform that integrates security directly into your development workflow. Built for engineering teams who want to ship secure code without slowing down, SecureStack provides API security testing, compliance automation, dependency risk management, and SBOM generation in a single, easy-to-integrate service.

## What is SecureStack?

SecureStack is a production-ready security platform that combines four essential DevSecOps capabilities:

- **API Security Testing**: Automated contract validation, fuzzing, and rate limiting checks
- **Compliance-as-Code**: Continuous policy enforcement and auditing for SOC 2, PCI-DSS, GDPR
- **Dependency Management**: Intelligent risk scoring and vulnerability assessment
- **SBOM Generation**: Automated Software Bill of Materials with cryptographic attestation

Connect SecureStack to your CI/CD pipeline or use it as a standalone service. Built with modern APIs and client libraries for seamless integration into any tech stack.

## Features

- **API Security Testing**: Contract testing, fuzzing, rate limiting validation
- **Compliance-as-Code**: Policy engine with continuous auditing (SOC 2, PCI-DSS, GDPR)
- **Dependency Management**: Risk scoring and vulnerability assessment
- **SBOM Generation**: Software Bill of Materials with attestation support

## Quick Start

### Using Docker Compose

```bash
docker-compose up -d
```

Access the platform at `http://localhost:3000`

### Manual Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start
```

## Integration

### REST API

Base URL: `http://localhost:8000/api/v1`

Full API documentation available at `http://localhost:8000/docs` when the server is running.

### Python Client

```python
from securestack_client import SecureStackClient

client = SecureStackClient(api_url="http://localhost:8000")
result = client.test_api_security(
    endpoint="https://api.example.com/users",
    method="GET",
    test_types=["contract", "fuzzing", "rate_limit"]
)
print(f"Test status: {result['status']}")
```

Install: `pip install -e clients/python`

### JavaScript/TypeScript Client

```javascript
import { SecureStackClient } from '@securestack/client';

const client = new SecureStackClient({ 
  apiUrl: 'http://localhost:8000' 
});

const result = await client.testApiSecurity({ 
  endpoint: 'https://api.example.com/users',
  method: 'GET'
});
console.log(`Test status: ${result.status}`);
```

Install: `npm install -C clients/javascript`

## Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript
- **Database**: PostgreSQL
- **Policy Engine**: Open Policy Agent (OPA)
- **SBOM**: CycloneDX format

## License

MIT

