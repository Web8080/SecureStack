import requests
from typing import Dict, Any, List, Optional
import json


class SecureStackClient:
    def __init__(self, api_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.api_url = api_url.rstrip('/')
        self.base_url = f"{self.api_url}/api/v1"
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_api_security(
        self,
        endpoint: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        test_types: Optional[List[str]] = None,
        contract_schema: Optional[Dict[str, Any]] = None,
        rate_limit_threshold: Optional[int] = 100
    ) -> Dict[str, Any]:
        if test_types is None:
            test_types = ["contract", "fuzzing", "rate_limit"]
        
        payload = {
            "endpoint": endpoint,
            "method": method,
            "test_types": test_types
        }
        
        if headers:
            payload["headers"] = headers
        if body:
            payload["body"] = body
        if contract_schema:
            payload["contract_schema"] = contract_schema
        if rate_limit_threshold:
            payload["rate_limit_threshold"] = rate_limit_threshold
        
        response = self.session.post(f"{self.base_url}/api-security/test", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_api_tests(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/api-security/tests",
            params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()
    
    def check_compliance(
        self,
        framework: str,
        resource_type: str,
        resource_data: Dict[str, Any],
        policy_name: Optional[str] = None,
        custom_policy: Optional[str] = None
    ) -> Dict[str, Any]:
        payload = {
            "framework": framework,
            "resource_type": resource_type,
            "resource_data": resource_data
        }
        
        if policy_name:
            payload["policy_name"] = policy_name
        if custom_policy:
            payload["custom_policy"] = custom_policy
        
        response = self.session.post(f"{self.base_url}/compliance/check", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_compliance_checks(
        self,
        framework: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        if framework:
            params["framework"] = framework
        if status:
            params["status"] = status
        
        response = self.session.get(f"{self.base_url}/compliance/checks", params=params)
        response.raise_for_status()
        return response.json()
    
    def scan_dependency(
        self,
        package_name: str,
        version: str = "latest",
        ecosystem: str = "npm"
    ) -> Dict[str, Any]:
        payload = {
            "package_name": package_name,
            "version": version,
            "ecosystem": ecosystem
        }
        
        response = self.session.post(f"{self.base_url}/dependencies/scan", json=payload)
        response.raise_for_status()
        return response.json()
    
    def scan_dependencies_batch(
        self,
        packages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/dependencies/scan-batch",
            json=packages
        )
        response.raise_for_status()
        return response.json()
    
    def get_dependency_scans(
        self,
        package_name: Optional[str] = None,
        min_risk_score: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        if package_name:
            params["package_name"] = package_name
        if min_risk_score is not None:
            params["min_risk_score"] = min_risk_score
        
        response = self.session.get(f"{self.base_url}/dependencies/scans", params=params)
        response.raise_for_status()
        return response.json()
    
    def generate_sbom(
        self,
        project_name: str,
        version: str,
        dependencies: List[Dict[str, Any]],
        format_type: str = "cyclonedx",
        metadata: Optional[Dict[str, Any]] = None,
        include_attestation: bool = True
    ) -> Dict[str, Any]:
        payload = {
            "project_name": project_name,
            "version": version,
            "format": format_type,
            "dependencies": dependencies,
            "include_attestation": include_attestation
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        response = self.session.post(f"{self.base_url}/sbom/generate", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_sbom_documents(
        self,
        project_name: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        if project_name:
            params["project_name"] = project_name
        
        response = self.session.get(f"{self.base_url}/sbom/documents", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_sbom(self, sbom_id: int) -> Dict[str, Any]:
        response = self.session.get(f"{self.base_url}/sbom/documents/{sbom_id}")
        response.raise_for_status()
        return response.json()
    
    def download_sbom(self, sbom_id: int) -> bytes:
        response = self.session.get(f"{self.base_url}/sbom/documents/{sbom_id}/download")
        response.raise_for_status()
        return response.content
    
    def health_check(self) -> Dict[str, Any]:
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


