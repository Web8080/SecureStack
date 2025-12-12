# SecureStack Integration Guide

## CI/CD Integration Examples

### GitHub Actions

```yaml
name: Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Test API Security
        run: |
          pip install securestack-client
          python -c "
          from securestack_client import SecureStackClient
          client = SecureStackClient(api_url='${{ secrets.SECURESTACK_API_URL }}')
          result = client.test_api_security(
              endpoint='https://api.example.com/users',
              method='GET'
          )
          if result['status'] != 'passed':
              exit(1)
          "
      
      - name: Check Compliance
        run: |
          python -c "
          from securestack_client import SecureStackClient
          client = SecureStackClient(api_url='${{ secrets.SECURESTACK_API_URL }}')
          result = client.check_compliance(
              framework='SOC 2',
              resource_type='application',
              resource_data={'encryption_at_rest': True}
          )
          if result['status'] != 'passed':
              exit(1)
          "
```

### GitLab CI

```yaml
security_checks:
  stage: test
  image: python:3.11
  script:
    - pip install securestack-client
    - python -c "
      from securestack_client import SecureStackClient
      client = SecureStackClient(api_url='$SECURESTACK_API_URL')
      result = client.test_api_security(
          endpoint='$API_ENDPOINT',
          method='GET'
      )
      assert result['status'] == 'passed'
      "
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Security Tests') {
            steps {
                sh '''
                    pip install securestack-client
                    python -c "
                    from securestack_client import SecureStackClient
                    client = SecureStackClient(api_url='${SECURESTACK_API_URL}')
                    result = client.test_api_security(
                        endpoint='${API_ENDPOINT}',
                        method='GET'
                    )
                    if result['status'] != 'passed':
                        exit(1)
                    "
                '''
            }
        }
    }
}
```

## Web Application Integration

### Express.js Middleware

```javascript
const { SecureStackClient } = require('@securestack/client');

const client = new SecureStackClient({
  apiUrl: process.env.SECURESTACK_API_URL
});

async function securityMiddleware(req, res, next) {
  try {
    const result = await client.testApiSecurity({
      endpoint: req.originalUrl,
      method: req.method
    });
    
    if (result.status !== 'passed') {
      return res.status(403).json({ error: 'Security check failed' });
    }
    
    next();
  } catch (error) {
    next(error);
  }
}

app.use(securityMiddleware);
```

### Django Middleware

```python
from securestack_client import SecureStackClient

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.client = SecureStackClient(
            api_url=settings.SECURESTACK_API_URL
        )
    
    def __call__(self, request):
        result = self.client.test_api_security(
            endpoint=request.path,
            method=request.method
        )
        
        if result['status'] != 'passed':
            return HttpResponse('Security check failed', status=403)
        
        return self.get_response(request)
```

## API Endpoints Reference

### API Security Testing

- `POST /api/v1/api-security/test` - Run security tests
- `GET /api/v1/api-security/tests` - List test results
- `GET /api/v1/api-security/tests/{id}` - Get test details

### Compliance

- `POST /api/v1/compliance/check` - Run compliance check
- `GET /api/v1/compliance/checks` - List compliance checks
- `GET /api/v1/compliance/frameworks` - List supported frameworks

### Dependencies

- `POST /api/v1/dependencies/scan` - Scan single dependency
- `POST /api/v1/dependencies/scan-batch` - Scan multiple dependencies
- `GET /api/v1/dependencies/scans` - List scan results

### SBOM

- `POST /api/v1/sbom/generate` - Generate SBOM
- `GET /api/v1/sbom/documents` - List SBOM documents
- `GET /api/v1/sbom/documents/{id}` - Get SBOM details
- `GET /api/v1/sbom/documents/{id}/download` - Download SBOM

## Authentication

For production deployments, configure API key authentication:

```python
client = SecureStackClient(
    api_url="https://securestack.example.com",
    api_key=os.getenv("SECURESTACK_API_KEY")
)
```

```javascript
const client = new SecureStackClient({
  apiUrl: 'https://securestack.example.com',
  apiKey: process.env.SECURESTACK_API_KEY
});
```

## Best Practices

1. **Cache Results**: Don't re-scan the same dependencies repeatedly
2. **Async Processing**: Use background jobs for long-running scans
3. **Error Handling**: Always handle API errors gracefully
4. **Rate Limiting**: Respect API rate limits in your integrations
5. **Logging**: Log all security check results for audit purposes


