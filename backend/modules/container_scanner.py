import subprocess
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ContainerScanner:
    def __init__(self):
        self.scan_tool = "trivy"
    
    async def scan_image(
        self,
        image_name: str,
        image_tag: str = "latest"
    ) -> Dict[str, Any]:
        full_image = f"{image_name}:{image_tag}"
        
        try:
            result = subprocess.run(
                ["trivy", "image", "--format", "json", full_image],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                vulnerabilities = self._parse_trivy_output(data)
                risk_score = self._calculate_risk_score(vulnerabilities)
                
                return {
                    "image_name": image_name,
                    "image_tag": image_tag,
                    "digest": data.get("ArtifactName", ""),
                    "vulnerabilities": vulnerabilities,
                    "risk_score": risk_score,
                    "status": "completed"
                }
            else:
                return {
                    "image_name": image_name,
                    "image_tag": image_tag,
                    "vulnerabilities": [],
                    "risk_score": 0.0,
                    "status": "error",
                    "error": result.stderr
                }
        except FileNotFoundError:
            logger.warning("Trivy not found, using fallback scanning")
            return await self._fallback_scan(image_name, image_tag)
        except Exception as e:
            logger.error(f"Container scan failed: {e}")
            return {
                "image_name": image_name,
                "image_tag": image_tag,
                "vulnerabilities": [],
                "risk_score": 0.0,
                "status": "error",
                "error": str(e)
            }
    
    def _parse_trivy_output(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        vulnerabilities = []
        
        for result in data.get("Results", []):
            for vuln in result.get("Vulnerabilities", []):
                vulnerabilities.append({
                    "id": vuln.get("VulnerabilityID", ""),
                    "package": vuln.get("PkgName", ""),
                    "severity": vuln.get("Severity", ""),
                    "title": vuln.get("Title", ""),
                    "description": vuln.get("Description", ""),
                    "cvss_score": vuln.get("CVSS", {}).get("nvd", {}).get("V3Score", 0.0)
                })
        
        return vulnerabilities
    
    def _calculate_risk_score(self, vulnerabilities: List[Dict[str, Any]]) -> float:
        if not vulnerabilities:
            return 0.0
        
        severity_scores = {"CRITICAL": 10.0, "HIGH": 7.0, "MEDIUM": 4.0, "LOW": 1.0}
        total_score = 0.0
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "LOW")
            score = vuln.get("cvss_score", severity_scores.get(severity, 1.0))
            total_score += score
        
        return min(total_score / len(vulnerabilities), 10.0)
    
    async def _fallback_scan(
        self,
        image_name: str,
        image_tag: str
    ) -> Dict[str, Any]:
        return {
            "image_name": image_name,
            "image_tag": image_tag,
            "vulnerabilities": [],
            "risk_score": 0.0,
            "status": "not_available",
            "note": "Trivy scanner not installed. Install Trivy for container scanning."
        }

