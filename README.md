# SecureStack

**SecureStack** is a unified DevSecOps platform that integrates security directly into your development workflow. Built for engineering teams who want to ship secure code without slowing down, SecureStack provides API security testing, compliance automation, dependency risk management, and SBOM generation in a single, easy-to-integrate service.

## What is SecureStack?

SecureStack is an enterprise-grade DevSecOps platform that combines comprehensive security testing, compliance automation, and risk management in a single unified service.

### Core Security Modules
- **API Security Testing**: OWASP Top 10 testing, contract validation, fuzzing, and rate limiting
- **Compliance-as-Code**: Continuous policy enforcement for SOC 2, PCI-DSS, GDPR with custom policies
- **Dependency Management**: Intelligent risk scoring with NVD/OSV integration and caching
- **SBOM Generation**: CycloneDX/SPDX with cryptographic attestation and comparison

### Enterprise Features
- **Authentication & Authorization**: JWT-based auth with RBAC and API keys
- **Team & Project Management**: Multi-user collaboration with project organization
- **Container Security**: Image scanning with Trivy integration
- **Infrastructure Scanning**: Terraform, Kubernetes, CloudFormation, Docker Compose
- **Automation**: Scheduled scans, webhooks, and background job processing
- **Reporting & Analytics**: Dashboard metrics, CSV/JSON exports, trend analysis
- **Audit Logging**: Complete action audit trail
- **Policy Templates**: Reusable compliance policy library

Connect SecureStack to your CI/CD pipeline or use it as a standalone service. Built with modern APIs and client libraries for seamless integration into any tech stack.

## Complete Feature List

### Core Security Modules

#### API Security Testing
- **Contract Testing**: JSON schema validation and API contract verification
- **Fuzzing**: Automated payload injection and edge case testing
- **Rate Limiting**: Load testing and rate limit validation
- **OWASP Top 10**: Comprehensive security testing including:
  - Injection attacks (SQL, NoSQL, Command)
  - Broken authentication detection
  - Sensitive data exposure scanning
  - XML External Entities (XXE) testing
  - Broken access control validation
  - Security misconfiguration detection
  - Cross-site scripting (XSS) detection
  - Insecure deserialization checks
  - Known vulnerabilities scanning
  - Insufficient logging detection

#### Compliance-as-Code
- **Framework Support**: SOC 2, PCI-DSS, GDPR compliance
- **Policy Engine**: Rule-based compliance checking
- **Custom Policies**: Define your own compliance rules
- **Evidence Collection**: Automated evidence gathering
- **Policy Templates**: Reusable compliance policy library
- **Continuous Auditing**: Automated compliance monitoring

#### Dependency Management
- **Vulnerability Scanning**: NVD and OSV API integration
- **Risk Scoring**: Intelligent risk calculation algorithm
- **Batch Scanning**: Scan multiple dependencies simultaneously
- **Caching**: Redis-based vulnerability cache for performance
- **Multi-Ecosystem**: Support for npm, PyPI, Maven, and more
- **Real-time Updates**: Latest vulnerability data

#### SBOM Generation
- **Formats**: CycloneDX and SPDX support
- **Attestation**: Cryptographic signing and verification
- **Comparison**: Diff between SBOM versions
- **Export**: Download in multiple formats
- **Component Tracking**: Detailed dependency tracking

### Enterprise Features

#### Authentication & Authorization
- JWT-based authentication with secure token management
- User registration and login
- Role-based access control (RBAC)
- API key management for programmatic access
- Session tracking and management

#### Team & Project Management
- Multi-user support with user profiles
- Team creation and collaboration
- Project organization and grouping
- Resource sharing across team members
- Access control at project level

#### Container Security
- Container image scanning with Trivy integration
- CVE detection and vulnerability assessment
- Risk scoring for container images
- Image digest tracking for integrity verification
- Multi-registry support

#### Infrastructure Scanning
- **Terraform**: Security scanning for Terraform files
- **Kubernetes**: Manifest security analysis
- **CloudFormation**: AWS template scanning
- **Docker Compose**: Compose file security checks
- **Misconfiguration Detection**: Find security issues in IaC

#### Automation & Scheduling
- Scheduled scans with cron-based automation
- Background job processing with Celery
- Webhook system for event-driven integrations
- Automated compliance checks
- Recurring scan management

#### Reporting & Analytics
- Comprehensive dashboard with security metrics
- CSV and JSON export capabilities
- Risk trend analysis and historical data
- Compliance reporting and pass rates
- Custom report generation

#### Advanced Features
- **Audit Logging**: Complete action audit trail
- **Vulnerability Caching**: Performance optimization with Redis
- **SBOM Comparison**: Version diff analysis
- **Policy Templates**: Reusable compliance policies
- **Notification System**: In-app and webhook notifications
- **Webhook Support**: Event-driven integrations

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

### Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache & Queue**: Redis for caching and task queue
- **Background Jobs**: Celery for asynchronous processing
- **Authentication**: JWT tokens with bcrypt password hashing
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### Frontend Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and builds
- **State Management**: React Query for server state
- **UI Components**: Custom components with modern design
- **Routing**: React Router for navigation

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Worker**: Celery with Redis broker
- **Web Server**: Uvicorn (ASGI)

### Security Tools Integration
- **Container Scanning**: Trivy integration
- **Vulnerability Databases**: NVD API, OSV API
- **SBOM Formats**: CycloneDX, SPDX
- **Policy Engine**: Custom rule-based engine

## API Endpoints

SecureStack provides **50+ API endpoints** organized into the following categories:

### Authentication (3 endpoints)
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Users & Teams (6 endpoints)
- User management and team collaboration

### Projects (3 endpoints)
- Project creation and management

### API Security (3 endpoints)
- Security testing, test history, and results

### Compliance (4 endpoints)
- Compliance checks, frameworks, and history

### Dependencies (4 endpoints)
- Dependency scanning, batch scanning, and results

### SBOM (5 endpoints)
- SBOM generation, listing, comparison, and download

### Containers (2 endpoints)
- Container image scanning and results

### Infrastructure (2 endpoints)
- Infrastructure scanning and results

### Scheduled Scans (3 endpoints)
- Create, list, and manage scheduled scans

### Reports (3 endpoints)
- Dashboard statistics and data exports

### Webhooks (2 endpoints)
- Webhook creation and management

### Notifications (3 endpoints)
- Notification management and marking as read

### Policy Templates (3 endpoints)
- Template creation and library access

### Audit Logs (2 endpoints)
- Audit log viewing and filtering

**Full API Documentation**: Visit `http://localhost:8000/docs` when the server is running.

## Project Statistics

- **Backend Modules**: 30+ Python files
- **API Routes**: 15+ router modules
- **Database Tables**: 15+ tables with relationships
- **API Endpoints**: 50+ REST endpoints
- **Frontend Components**: 6+ React components
- **Client SDKs**: Python & JavaScript/TypeScript
- **Documentation**: 7+ comprehensive guides

## Use Cases

1. **API Security Testing** - Comprehensive API security validation in CI/CD
2. **Compliance Automation** - SOC 2, PCI-DSS, GDPR compliance monitoring
3. **Dependency Management** - Automated vulnerability scanning and risk assessment
4. **SBOM Management** - Generate, compare, and track Software Bill of Materials
5. **Container Security** - Image scanning and vulnerability detection
6. **Infrastructure Security** - Infrastructure as Code security scanning
7. **Automated Scanning** - Scheduled and automated security checks
8. **Team Collaboration** - Multi-user team workflows and project organization
9. **Security Reporting** - Comprehensive security reports and analytics
10. **CI/CD Integration** - Seamless integration with GitHub Actions, GitLab CI, Jenkins

## Deployment

### Prerequisites
- Docker and Docker Compose
- PostgreSQL (included in Docker Compose)
- Redis (included in Docker Compose)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/Web8080/SecureStack.git
cd SecureStack

# Start all services
docker-compose up -d

# Access the platform
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://devsecops:devsecops_password@postgres:5432/devsecops
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Production Deployment

1. Set up environment variables
2. Configure SSL/TLS certificates
3. Set up database backups
4. Configure monitoring and alerting
5. Set up webhook endpoints
6. Review security settings

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[INTEGRATION.md](INTEGRATION.md)** - CI/CD integration examples
- **[FEATURES.md](FEATURES.md)** - Complete feature documentation
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[SCALING_SUMMARY.md](SCALING_SUMMARY.md)** - Scaling details
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Project status and statistics

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt encryption for passwords
- **API Key Management**: Secure programmatic access
- **Role-Based Access Control**: Fine-grained permissions
- **Audit Logging**: Complete action audit trail
- **Webhook Security**: HMAC signature verification
- **Rate Limiting**: API abuse prevention
- **Input Validation**: Comprehensive input sanitization

## Performance Features

- **Redis Caching**: Vulnerability data caching for faster responses
- **Background Processing**: Celery for long-running tasks
- **Database Optimization**: Efficient queries and indexing
- **Async Processing**: Asynchronous API endpoints
- **Connection Pooling**: Optimized database connections

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built with:
- FastAPI
- React
- PostgreSQL
- Redis
- Celery
- And many other open-source projects

