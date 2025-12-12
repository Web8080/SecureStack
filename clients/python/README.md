# SecureStack Python Client

Python client library for the SecureStack DevSecOps Platform.

## Installation

```bash
pip install securestack-client
```

Or install from source:

```bash
cd clients/python
pip install .
```

## Usage

```python
from securestack_client import SecureStackClient

# Initialize client
client = SecureStackClient(api_url="http://localhost:8000")

# Test API security
result = client.test_api_security(
    endpoint="https://api.example.com/users",
    method="GET",
    test_types=["contract", "fuzzing", "rate_limit"]
)
print(f"Test status: {result['status']}")

# Check compliance
compliance = client.check_compliance(
    framework="SOC 2",
    resource_type="application",
    resource_data={
        "access_control_enabled": True,
        "encryption_at_rest": True,
        "encryption_in_transit": True
    }
)
print(f"Compliance status: {compliance['status']}")

# Scan dependency
scan = client.scan_dependency(
    package_name="express",
    version="4.18.2",
    ecosystem="npm"
)
print(f"Risk score: {scan['risk_score']}")

# Generate SBOM
sbom = client.generate_sbom(
    project_name="my-app",
    version="1.0.0",
    dependencies=[
        {"name": "express", "version": "4.18.2"},
        {"name": "axios", "version": "1.6.2"}
    ]
)
print(f"SBOM generated: {sbom['sbom_id']}")
```

## API Reference

See the main SecureStack documentation for full API reference.


