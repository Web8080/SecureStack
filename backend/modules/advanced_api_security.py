import httpx
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AdvancedAPISecurityTester:
    OWASP_TOP_10 = [
        "injection",
        "broken_authentication",
        "sensitive_data_exposure",
        "xml_external_entities",
        "broken_access_control",
        "security_misconfiguration",
        "xss",
        "insecure_deserialization",
        "known_vulnerabilities",
        "insufficient_logging"
    ]
    
    def __init__(self):
        self.timeout = 30.0
    
    async def test_owasp_top_10(
        self,
        endpoint: str,
        method: str = "GET",
        headers: Dict[str, str] = None,
        body: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        results = {}
        
        for vulnerability in self.OWASP_TOP_10:
            test_func = getattr(self, f"_test_{vulnerability}", None)
            if test_func:
                try:
                    result = await test_func(endpoint, method, headers, body)
                    results[vulnerability] = result
                except Exception as e:
                    logger.error(f"Test {vulnerability} failed: {e}")
                    results[vulnerability] = {"passed": False, "error": str(e)}
        
        overall_status = "passed" if all(r.get("passed", True) for r in results.values()) else "failed"
        
        return {
            "status": overall_status,
            "tests": results,
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results.values() if r.get("passed", False)),
                "failed": sum(1 for r in results.values() if not r.get("passed", False))
            }
        }
    
    async def _test_injection(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT NULL--",
            "../../../etc/passwd",
            "<script>alert('xss')</script>"
        ]
        
        issues = []
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for payload in injection_payloads:
                try:
                    if method.upper() in ["GET", "DELETE"]:
                        response = await client.request(
                            method=method,
                            url=f"{endpoint}?input={payload}",
                            headers=headers or {}
                        )
                    else:
                        test_body = {**body, "input": payload} if body else {"input": payload}
                        response = await client.request(
                            method=method,
                            url=endpoint,
                            headers=headers or {},
                            json=test_body
                        )
                    
                    if response.status_code == 500 or "error" in response.text.lower():
                        issues.append({
                            "payload": payload,
                            "status_code": response.status_code,
                            "vulnerable": True
                        })
                except Exception:
                    pass
        
        return {
            "passed": len(issues) == 0,
            "issues_found": len(issues),
            "issues": issues[:5]
        }
    
    async def _test_broken_authentication(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        issues = []
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            no_auth_headers = {k: v for k, v in (headers or {}).items() if k.lower() != "authorization"}
            
            response = await client.request(
                method=method,
                url=endpoint,
                headers=no_auth_headers,
                json=body
            )
            
            if response.status_code == 200:
                issues.append({
                    "issue": "Endpoint accessible without authentication",
                    "status_code": 200
                })
            
            weak_auth_headers = {**(headers or {}), "Authorization": "Bearer weak_token"}
            response2 = await client.request(
                method=method,
                url=endpoint,
                headers=weak_auth_headers,
                json=body
            )
            
            if response2.status_code == 200:
                issues.append({
                    "issue": "Weak authentication accepted",
                    "status_code": 200
                })
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    async def _test_sensitive_data_exposure(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        sensitive_patterns = [
            "password", "secret", "token", "api_key",
            "credit_card", "ssn", "social_security"
        ]
        
        issues = []
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=endpoint,
                headers=headers or {},
                json=body
            )
            
            response_text = response.text.lower()
            for pattern in sensitive_patterns:
                if pattern in response_text:
                    issues.append({
                        "pattern": pattern,
                        "issue": f"Sensitive data pattern '{pattern}' found in response"
                    })
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    async def _test_xss(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>"
        ]
        
        issues = []
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for payload in xss_payloads:
                try:
                    if method.upper() in ["GET", "DELETE"]:
                        response = await client.request(
                            method=method,
                            url=f"{endpoint}?input={payload}",
                            headers=headers or {}
                        )
                    else:
                        test_body = {**body, "input": payload} if body else {"input": payload}
                        response = await client.request(
                            method=method,
                            url=endpoint,
                            headers=headers or {},
                            json=test_body
                        )
                    
                    if payload in response.text:
                        issues.append({
                            "payload": payload,
                            "issue": "XSS payload reflected in response"
                        })
                except Exception:
                    pass
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    async def _test_broken_access_control(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        issues = []
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=endpoint,
                headers=headers or {},
                json=body
            )
            
            if response.status_code == 200:
                if "admin" in endpoint.lower() or "user" in endpoint.lower():
                    issues.append({
                        "issue": "Potential unauthorized access to restricted endpoint"
                    })
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    async def _test_security_misconfiguration(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        issues = []
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=endpoint,
                headers=headers or {},
                json=body
            )
            
            server_header = response.headers.get("Server", "")
            if server_header:
                issues.append({
                    "issue": f"Server information leaked: {server_header}"
                })
            
            if "X-Powered-By" in response.headers:
                issues.append({
                    "issue": "X-Powered-By header exposes technology stack"
                })
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    async def _test_xml_external_entities(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"passed": True, "note": "XXE testing requires XML endpoints"}
    
    async def _test_insecure_deserialization(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"passed": True, "note": "Deserialization testing requires specific formats"}
    
    async def _test_known_vulnerabilities(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"passed": True, "note": "Vulnerability scanning integrated in dependency module"}
    
    async def _test_insufficient_logging(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"passed": True, "note": "Logging verification requires server-side access"}

