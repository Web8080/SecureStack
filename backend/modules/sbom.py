import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import hashlib
import logging

logger = logging.getLogger(__name__)


class SBOMGenerator:
    def __init__(self):
        self.supported_formats = ["cyclonedx", "spdx"]
    
    async def generate_sbom(
        self,
        project_name: str,
        version: str,
        format_type: str = "cyclonedx",
        dependencies: List[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None,
        include_attestation: bool = True
    ) -> Dict[str, Any]:
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}. Supported: {self.supported_formats}")
        
        if format_type == "cyclonedx":
            sbom_content = self._generate_cyclonedx(
                project_name, version, dependencies or [], metadata or {}
            )
        else:
            sbom_content = self._generate_spdx(
                project_name, version, dependencies or [], metadata or {}
            )
        
        attestation = None
        if include_attestation:
            attestation = self._generate_attestation(sbom_content, project_name, version)
        
        return {
            "content": json.dumps(sbom_content, indent=2),
            "attestation": attestation,
            "format": format_type,
            "project_name": project_name,
            "version": version
        }
    
    def _generate_cyclonedx(
        self,
        project_name: str,
        version: str,
        dependencies: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        components = []
        
        for dep in dependencies:
            component = {
                "type": "library",
                "name": dep.get("name", ""),
                "version": dep.get("version", ""),
                "purl": dep.get("purl", f"pkg:npm/{dep.get('name', '')}@{dep.get('version', '')}")
            }
            
            if "license" in dep:
                component["licenses"] = [{"license": {"id": dep["license"]}}]
            
            if "vulnerabilities" in dep:
                component["vulnerabilities"] = dep["vulnerabilities"]
            
            components.append(component)
        
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{self._generate_uuid()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "tools": [
                    {
                        "vendor": "SecureStack",
                        "name": "SBOM Generator",
                        "version": "1.0.0"
                    }
                ],
                "component": {
                    "type": "application",
                    "name": project_name,
                    "version": version
                }
            },
            "components": components
        }
        
        if metadata:
            sbom["metadata"].update(metadata)
        
        return sbom
    
    def _generate_spdx(
        self,
        project_name: str,
        version: str,
        dependencies: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        packages = []
        
        for dep in dependencies:
            package = {
                "SPDXID": f"SPDXRef-Package-{dep.get('name', '').replace('/', '-')}",
                "name": dep.get("name", ""),
                "versionInfo": dep.get("version", ""),
                "downloadLocation": dep.get("downloadLocation", "NOASSERTION"),
                "filesAnalyzed": False,
                "licenseConcluded": dep.get("license", "NOASSERTION"),
                "licenseDeclared": dep.get("license", "NOASSERTION"),
                "copyrightText": "NOASSERTION",
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": dep.get("purl", f"pkg:npm/{dep.get('name', '')}@{dep.get('version', '')}")
                    }
                ]
            }
            packages.append(package)
        
        spdx = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": f"{project_name}-{version}",
            "documentNamespace": f"https://securestack.dev/spdx/{project_name}-{version}",
            "creationInfo": {
                "created": datetime.utcnow().isoformat() + "Z",
                "creators": [
                    "Tool: SecureStack-SBOM-Generator-1.0.0"
                ],
                "licenseListVersion": "3.23"
            },
            "packages": packages,
            "relationships": [
                {
                    "spdxElementId": "SPDXRef-DOCUMENT",
                    "relationshipType": "DESCRIBES",
                    "relatedSpdxElement": f"SPDXRef-{project_name}"
                }
            ]
        }
        
        return spdx
    
    def _generate_attestation(
        self,
        sbom_content: Dict[str, Any],
        project_name: str,
        version: str
    ) -> str:
        content_str = json.dumps(sbom_content, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        attestation = {
            "type": "https://securestack.dev/attestation/v1",
            "predicateType": "https://securestack.dev/sbom/v1",
            "subject": [
                {
                    "name": f"{project_name}:{version}",
                    "digest": {
                        "sha256": content_hash
                    }
                }
            ],
            "predicate": {
                "sbom": {
                    "format": "cyclonedx" if "bomFormat" in sbom_content else "spdx",
                    "version": sbom_content.get("specVersion") or sbom_content.get("spdxVersion", ""),
                    "generatedAt": datetime.utcnow().isoformat() + "Z",
                    "generator": "SecureStack SBOM Generator 1.0.0"
                }
            }
        }
        
        return json.dumps(attestation, indent=2)
    
    def _generate_uuid(self) -> str:
        import uuid
        return str(uuid.uuid4())


