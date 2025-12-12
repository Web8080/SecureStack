import yaml
import json
import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class InfrastructureScanner:
    def __init__(self):
        self.supported_types = ["terraform", "cloudformation", "kubernetes", "docker_compose"]
    
    async def scan(
        self,
        scan_type: str,
        target: str,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        if scan_type not in self.supported_types:
            return {
                "status": "error",
                "message": f"Unsupported scan type: {scan_type}",
                "supported_types": self.supported_types
            }
        
        scanner_func = getattr(self, f"_scan_{scan_type}", None)
        if not scanner_func:
            return {"status": "error", "message": f"Scanner for {scan_type} not implemented"}
        
        try:
            return await scanner_func(target, config or {})
        except Exception as e:
            logger.error(f"Infrastructure scan failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "findings": [],
                "risk_score": 0.0
            }
    
    async def _scan_terraform(
        self,
        target: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        findings = []
        
        try:
            with open(target, 'r') as f:
                content = f.read()
            
            findings.extend(self._check_terraform_security(content))
        except Exception as e:
            findings.append({
                "severity": "HIGH",
                "type": "file_error",
                "message": f"Failed to read Terraform file: {str(e)}"
            })
        
        risk_score = self._calculate_risk_from_findings(findings)
        
        return {
            "status": "completed",
            "scan_type": "terraform",
            "target": target,
            "findings": findings,
            "risk_score": risk_score
        }
    
    def _check_terraform_security(self, content: str) -> List[Dict[str, Any]]:
        findings = []
        
        security_patterns = [
            {
                "pattern": r'password\s*=\s*["\']([^"\']+)["\']',
                "severity": "HIGH",
                "message": "Hardcoded password found"
            },
            {
                "pattern": r'secret\s*=\s*["\']([^"\']+)["\']',
                "severity": "HIGH",
                "message": "Hardcoded secret found"
            },
            {
                "pattern": r'aws_access_key\s*=\s*["\']([^"\']+)["\']',
                "severity": "CRITICAL",
                "message": "Hardcoded AWS access key found"
            },
            {
                "pattern": r'encryption\s*=\s*false',
                "severity": "MEDIUM",
                "message": "Encryption disabled"
            },
            {
                "pattern": r'publicly_accessible\s*=\s*true',
                "severity": "MEDIUM",
                "message": "Resource is publicly accessible"
            }
        ]
        
        for pattern_info in security_patterns:
            matches = re.finditer(pattern_info["pattern"], content, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "severity": pattern_info["severity"],
                    "type": "security_misconfiguration",
                    "message": pattern_info["message"],
                    "line": content[:match.start()].count('\n') + 1
                })
        
        return findings
    
    async def _scan_kubernetes(
        self,
        target: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        findings = []
        
        try:
            with open(target, 'r') as f:
                content = f.read()
            
            findings.extend(self._check_kubernetes_security(content))
        except Exception as e:
            findings.append({
                "severity": "HIGH",
                "type": "file_error",
                "message": f"Failed to read Kubernetes manifest: {str(e)}"
            })
        
        risk_score = self._calculate_risk_from_findings(findings)
        
        return {
            "status": "completed",
            "scan_type": "kubernetes",
            "target": target,
            "findings": findings,
            "risk_score": risk_score
        }
    
    def _check_kubernetes_security(self, content: str) -> List[Dict[str, Any]]:
        findings = []
        
        try:
            docs = yaml.safe_load_all(content)
            for doc in docs:
                if not doc:
                    continue
                
                if doc.get("kind") == "Pod":
                    spec = doc.get("spec", {})
                    containers = spec.get("containers", [])
                    
                    for container in containers:
                        security_context = container.get("securityContext", {})
                        
                        if not security_context.get("runAsNonRoot"):
                            findings.append({
                                "severity": "MEDIUM",
                                "type": "security_context",
                                "message": "Container should run as non-root user"
                            })
                        
                        if security_context.get("privileged") == True:
                            findings.append({
                                "severity": "HIGH",
                                "type": "security_context",
                                "message": "Container running in privileged mode"
                            })
        except Exception as e:
            findings.append({
                "severity": "MEDIUM",
                "type": "parse_error",
                "message": f"Failed to parse YAML: {str(e)}"
            })
        
        return findings
    
    async def _scan_cloudformation(
        self,
        target: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        findings = []
        
        try:
            with open(target, 'r') as f:
                content = f.read()
            
            findings.extend(self._check_cloudformation_security(content))
        except Exception as e:
            findings.append({
                "severity": "HIGH",
                "type": "file_error",
                "message": f"Failed to read CloudFormation template: {str(e)}"
            })
        
        risk_score = self._calculate_risk_from_findings(findings)
        
        return {
            "status": "completed",
            "scan_type": "cloudformation",
            "target": target,
            "findings": findings,
            "risk_score": risk_score
        }
    
    def _check_cloudformation_security(self, content: str) -> List[Dict[str, Any]]:
        findings = []
        
        try:
            template = json.loads(content) if content.strip().startswith('{') else yaml.safe_load(content)
            
            resources = template.get("Resources", {})
            for resource_name, resource in resources.items():
                resource_type = resource.get("Type", "")
                properties = resource.get("Properties", {})
                
                if "PublicAccessBlockConfiguration" not in str(properties):
                    if "S3" in resource_type or "Bucket" in resource_type:
                        findings.append({
                            "severity": "MEDIUM",
                            "type": "public_access",
                            "message": f"Resource {resource_name} may have public access"
                        })
        except Exception as e:
            findings.append({
                "severity": "MEDIUM",
                "type": "parse_error",
                "message": f"Failed to parse template: {str(e)}"
            })
        
        return findings
    
    async def _scan_docker_compose(
        self,
        target: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        findings = []
        
        try:
            with open(target, 'r') as f:
                content = f.read()
            
            findings.extend(self._check_docker_compose_security(content))
        except Exception as e:
            findings.append({
                "severity": "HIGH",
                "type": "file_error",
                "message": f"Failed to read docker-compose file: {str(e)}"
            })
        
        risk_score = self._calculate_risk_from_findings(findings)
        
        return {
            "status": "completed",
            "scan_type": "docker_compose",
            "target": target,
            "findings": findings,
            "risk_score": risk_score
        }
    
    def _check_docker_compose_security(self, content: str) -> List[Dict[str, Any]]:
        findings = []
        
        try:
            compose = yaml.safe_load(content)
            services = compose.get("services", {})
            
            for service_name, service in services.items():
                if service.get("privileged") == True:
                    findings.append({
                        "severity": "HIGH",
                        "type": "privileged_mode",
                        "message": f"Service {service_name} running in privileged mode"
                    })
                
                if not service.get("security_opt"):
                    findings.append({
                        "severity": "LOW",
                        "type": "security_options",
                        "message": f"Service {service_name} missing security options"
                    })
        except Exception as e:
            findings.append({
                "severity": "MEDIUM",
                "type": "parse_error",
                "message": f"Failed to parse docker-compose: {str(e)}"
            })
        
        return findings
    
    def _calculate_risk_from_findings(self, findings: List[Dict[str, Any]]) -> float:
        if not findings:
            return 0.0
        
        severity_scores = {
            "CRITICAL": 10.0,
            "HIGH": 7.0,
            "MEDIUM": 4.0,
            "LOW": 1.0
        }
        
        total_score = 0.0
        for finding in findings:
            severity = finding.get("severity", "LOW")
            total_score += severity_scores.get(severity, 1.0)
        
        return min(total_score / len(findings), 10.0)

