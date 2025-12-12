import httpx
import asyncio
from typing import Dict, Any, List, Optional
from packaging import version as pkg_version
import logging

from config import settings
from modules.vulnerability_cache import VulnerabilityCache

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    def __init__(self):
        self.nvd_api_url = settings.NVD_API_URL
        self.osv_api_url = settings.OSV_API_URL
        self.timeout = 30.0
        self.cache = VulnerabilityCache()
    
    async def analyze_package(
        self,
        package_name: str,
        version: str,
        ecosystem: str = "npm"
    ) -> Dict[str, Any]:
        cached = self.cache.get(package_name, version, ecosystem)
        if cached:
            return {**cached, "cached": True}
        
        vulnerabilities = []
        
        osv_vulns = await self._check_osv(package_name, version, ecosystem)
        vulnerabilities.extend(osv_vulns)
        
        nvd_vulns = await self._check_nvd(package_name, version)
        vulnerabilities.extend(nvd_vulns)
        
        risk_score = self._calculate_risk_score(vulnerabilities)
        
        result = {
            "package_name": package_name,
            "version": version,
            "ecosystem": ecosystem,
            "vulnerabilities": vulnerabilities,
            "vulnerability_count": len(vulnerabilities),
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "cached": False
        }
        
        self.cache.set(package_name, version, result, ecosystem)
        
        return result
    
    async def _check_osv(
        self,
        package_name: str,
        version: str,
        ecosystem: str
    ) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "package": {
                        "name": package_name,
                        "ecosystem": ecosystem
                    },
                    "version": version
                }
                
                response = await client.post(
                    f"{self.osv_api_url}",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    vulns = []
                    
                    for vuln in data.get("vulns", []):
                        severity_score = 0.0
                        if "database_specific" in vuln and "severity" in vuln["database_specific"]:
                            severity = vuln["database_specific"]["severity"]
                            if isinstance(severity, list) and len(severity) > 0:
                                if "score" in severity[0]:
                                    severity_score = float(severity[0]["score"])
                        
                        vulns.append({
                            "id": vuln.get("id", ""),
                            "summary": vuln.get("summary", ""),
                            "severity": severity_score,
                            "source": "OSV",
                            "published": vuln.get("published", ""),
                            "modified": vuln.get("modified", "")
                        })
                    
                    return vulns
        except Exception as e:
            logger.error(f"OSV check failed for {package_name}: {e}")
        
        return []
    
    async def _check_nvd(
        self,
        package_name: str,
        version: str
    ) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                query = f"{package_name} {version}"
                params = {
                    "keywordSearch": query,
                    "resultsPerPage": 20
                }
                
                response = await client.get(
                    self.nvd_api_url,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    vulns = []
                    
                    for item in data.get("vulnerabilities", []):
                        cve = item.get("cve", {})
                        metrics = cve.get("metrics", {})
                        
                        cvss_score = 0.0
                        if "cvssMetricV31" in metrics:
                            cvss_data = metrics["cvssMetricV31"][0]
                            cvss_score = float(cvss_data.get("cvssData", {}).get("baseScore", 0.0))
                        elif "cvssMetricV2" in metrics:
                            cvss_data = metrics["cvssMetricV2"][0]
                            cvss_score = float(cvss_data.get("cvssData", {}).get("baseScore", 0.0))
                        
                        vulns.append({
                            "id": cve.get("id", ""),
                            "summary": cve.get("descriptions", [{}])[0].get("value", ""),
                            "severity": cvss_score,
                            "source": "NVD",
                            "published": cve.get("published", ""),
                            "modified": cve.get("lastModified", "")
                        })
                    
                    return vulns
        except Exception as e:
            logger.error(f"NVD check failed for {package_name}: {e}")
        
        return []
    
    def _calculate_risk_score(self, vulnerabilities: List[Dict[str, Any]]) -> float:
        if not vulnerabilities:
            return 0.0
        
        total_score = 0.0
        count = 0
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", 0.0)
            if severity > 0:
                total_score += severity
                count += 1
        
        if count == 0:
            return 0.0
        
        avg_severity = total_score / count
        
        critical_count = sum(1 for v in vulnerabilities if v.get("severity", 0) >= 9.0)
        high_count = sum(1 for v in vulnerabilities if 7.0 <= v.get("severity", 0) < 9.0)
        
        risk_score = avg_severity
        
        if critical_count > 0:
            risk_score += (critical_count * 2.0)
        if high_count > 0:
            risk_score += (high_count * 1.0)
        
        return min(risk_score, 10.0)
    
    def _get_risk_level(self, risk_score: float) -> str:
        if risk_score >= 9.0:
            return "critical"
        elif risk_score >= 7.0:
            return "high"
        elif risk_score >= 4.0:
            return "medium"
        elif risk_score > 0:
            return "low"
        else:
            return "none"


