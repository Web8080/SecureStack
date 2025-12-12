# SecureStack Quick Start Guide

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

## Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd DevSecOps_project
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the platform:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Manual Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://devsecops:devsecops_password@localhost:5432/devsecops"
export SECRET_KEY="your-secret-key"

# Run migrations (if using Alembic)
# alembic upgrade head

# Start server
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Using the Client Libraries

### Python

```bash
cd clients/python
pip install -e .
```

```python
from securestack_client import SecureStackClient

client = SecureStackClient(api_url="http://localhost:8000")

# Test API security
result = client.test_api_security(
    endpoint="https://api.example.com/users",
    method="GET"
)
print(result)
```

### JavaScript/TypeScript

```bash
cd clients/javascript
npm install
npm run build
```

```javascript
import { SecureStackClient } from '@securestack/client';

const client = new SecureStackClient({
  apiUrl: 'http://localhost:8000'
});

const result = await client.testApiSecurity({
  endpoint: 'https://api.example.com/users'
});
```

## Example Use Cases

### 1. Test API Security in CI/CD

```python
from securestack_client import SecureStackClient

client = SecureStackClient(api_url="https://securestack.example.com")

result = client.test_api_security(
    endpoint="https://api.myapp.com/users",
    method="GET",
    test_types=["contract", "fuzzing"]
)

if result["status"] != "passed":
    raise Exception("API security tests failed")
```

### 2. Check Compliance Before Deployment

```python
compliance = client.check_compliance(
    framework="SOC 2",
    resource_type="application",
    resource_data={
        "access_control_enabled": True,
        "encryption_at_rest": True,
        "encryption_in_transit": True,
        "logging_enabled": True,
        "monitoring_enabled": True
    }
)

if compliance["status"] != "passed":
    print("Compliance check failed")
    exit(1)
```

### 3. Scan Dependencies

```python
scan = client.scan_dependency(
    package_name="express",
    version="4.18.2",
    ecosystem="npm"
)

if scan["risk_score"] > 7.0:
    print(f"High risk dependency: {scan['risk_score']}")
```

### 4. Generate SBOM

```python
sbom = client.generate_sbom(
    project_name="my-app",
    version="1.0.0",
    dependencies=[
        {"name": "express", "version": "4.18.2"},
        {"name": "axios", "version": "1.6.2"}
    ],
    format_type="cyclonedx"
)

print(f"SBOM generated: {sbom['sbom_id']}")
```

## Troubleshooting

### Database Connection Issues

Ensure PostgreSQL is running and accessible:
```bash
docker-compose up postgres -d
```

### Frontend Not Connecting to Backend

Check that `REACT_APP_API_URL` in frontend environment matches your backend URL.

### API Rate Limiting

The platform uses free public APIs (NVD, OSV) for vulnerability data. These may have rate limits. Consider caching results for production use.

## Next Steps

- Review the API documentation at `/docs` endpoint
- Explore the web dashboard at http://localhost:3000
- Integrate SecureStack into your CI/CD pipeline
- Customize compliance policies for your organization


