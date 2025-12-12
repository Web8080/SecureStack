import httpx
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)


class APISecurityTester:
    def __init__(self):
        self.timeout = 30.0
        self.max_retries = 3
    
    async def run_tests(
        self,
        endpoint: str,
        method: str = "GET",
        headers: Dict[str, str] = None,
        body: Optional[Dict[str, Any]] = None,
        test_types: List[str] = None,
        contract_schema: Optional[Dict[str, Any]] = None,
        rate_limit_threshold: Optional[int] = 100
    ) -> Dict[str, Any]:
        if test_types is None:
            test_types = ["contract", "fuzzing", "rate_limit"]
        
        results = {}
        
        if "contract" in test_types:
            results["contract"] = await self.test_contract(
                endpoint, method, headers, body, contract_schema
            )
        
        if "fuzzing" in test_types:
            results["fuzzing"] = await self.test_fuzzing(
                endpoint, method, headers, body
            )
        
        if "rate_limit" in test_types:
            results["rate_limit"] = await self.test_rate_limiting(
                endpoint, method, headers, body, rate_limit_threshold
            )
        
        return results
    
    async def test_contract(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[Dict[str, Any]],
        schema: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=endpoint,
                    headers=headers or {},
                    json=body
                )
                
                result = {
                    "passed": True,
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "issues": []
                }
                
                if schema:
                    try:
                        response_data = response.json()
                        validate(instance=response_data, schema=schema)
                        result["contract_validation"] = "passed"
                    except ValidationError as e:
                        result["passed"] = False
                        result["contract_validation"] = "failed"
                        result["issues"].append({
                            "type": "contract_violation",
                            "message": str(e.message),
                            "path": ".".join(str(p) for p in e.path)
                        })
                    except json.JSONDecodeError:
                        result["passed"] = False
                        result["issues"].append({
                            "type": "invalid_json",
                            "message": "Response is not valid JSON"
                        })
                
                if response.status_code >= 400:
                    result["passed"] = False
                    result["issues"].append({
                        "type": "http_error",
                        "message": f"HTTP {response.status_code} error"
                    })
                
                return result
        except httpx.TimeoutException:
            return {
                "passed": False,
                "issues": [{"type": "timeout", "message": "Request timed out"}]
            }
        except Exception as e:
            logger.error(f"Contract test failed: {e}")
            return {
                "passed": False,
                "issues": [{"type": "error", "message": str(e)}]
            }
    
    async def test_fuzzing(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        fuzz_payloads = [
            None,
            "",
            "null",
            "undefined",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "'; DROP TABLE users; --",
            "\x00\x01\x02",
            "A" * 10000,
            {"nested": {"deep": {"value": "test"}}}
        ]
        
        issues = []
        passed = True
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for payload in fuzz_payloads:
                try:
                    if method.upper() in ["GET", "DELETE"]:
                        response = await client.request(
                            method=method,
                            url=endpoint,
                            headers=headers or {}
                        )
                    else:
                        response = await client.request(
                            method=method,
                            url=endpoint,
                            headers=headers or {},
                            json=payload if payload is not None else body
                        )
                    
                    if response.status_code == 500:
                        issues.append({
                            "type": "server_error",
                            "payload": str(payload)[:100],
                            "status_code": 500
                        })
                        passed = False
                    elif response.status_code == 400 and payload is None:
                        pass
                except Exception as e:
                    issues.append({
                        "type": "exception",
                        "payload": str(payload)[:100],
                        "message": str(e)
                    })
        
        return {
            "passed": passed,
            "payloads_tested": len(fuzz_payloads),
            "issues_found": len(issues),
            "issues": issues[:10]
        }
    
    async def test_rate_limiting(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[Dict[str, Any]],
        threshold: int = 100
    ) -> Dict[str, Any]:
        requests_sent = 0
        rate_limited = False
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = []
            for i in range(min(threshold + 10, 150)):
                if method.upper() in ["GET", "DELETE"]:
                    task = client.request(method=method, url=endpoint, headers=headers or {})
                else:
                    task = client.request(
                        method=method,
                        url=endpoint,
                        headers=headers or {},
                        json=body
                    )
                tasks.append(task)
                requests_sent += 1
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for response in responses:
                if isinstance(response, httpx.Response):
                    if response.status_code == 429:
                        rate_limited = True
                        break
        
        elapsed = time.time() - start_time
        requests_per_second = requests_sent / elapsed if elapsed > 0 else 0
        
        return {
            "passed": rate_limited,
            "requests_sent": requests_sent,
            "requests_per_second": round(requests_per_second, 2),
            "rate_limited": rate_limited,
            "threshold": threshold,
            "elapsed_seconds": round(elapsed, 2)
        }


