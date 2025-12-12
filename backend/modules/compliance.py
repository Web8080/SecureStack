import re
import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ComplianceEngine:
    def __init__(self):
        self.policies = self._load_default_policies()
    
    def _load_default_policies(self) -> Dict[str, Dict[str, Any]]:
        return {
            "soc2": {
                "access_control": {
                    "rule": "resource_data.get('access_control_enabled') == True",
                    "description": "Access control must be enabled"
                },
                "encryption": {
                    "rule": "resource_data.get('encryption_at_rest') == True and resource_data.get('encryption_in_transit') == True",
                    "description": "Encryption at rest and in transit required"
                },
                "monitoring": {
                    "rule": "resource_data.get('logging_enabled') == True and resource_data.get('monitoring_enabled') == True",
                    "description": "Logging and monitoring must be enabled"
                },
                "incident_response": {
                    "rule": "resource_data.get('incident_response_plan') == True",
                    "description": "Incident response plan must be documented"
                }
            },
            "pci-dss": {
                "data_encryption": {
                    "rule": "resource_data.get('encryption_at_rest') == True and resource_data.get('encryption_in_transit') == True",
                    "description": "Cardholder data must be encrypted"
                },
                "access_control": {
                    "rule": "resource_data.get('access_control_enabled') == True and resource_data.get('mfa_enabled') == True",
                    "description": "Access control and MFA required"
                },
                "network_security": {
                    "rule": "resource_data.get('firewall_enabled') == True and resource_data.get('network_segmentation') == True",
                    "description": "Network security controls required"
                },
                "vulnerability_management": {
                    "rule": "resource_data.get('vulnerability_scanning') == True and resource_data.get('patch_management') == True",
                    "description": "Vulnerability management program required"
                }
            },
            "gdpr": {
                "data_encryption": {
                    "rule": "resource_data.get('encryption_at_rest') == True and resource_data.get('encryption_in_transit') == True",
                    "description": "Personal data must be encrypted"
                },
                "access_control": {
                    "rule": "resource_data.get('access_control_enabled') == True and resource_data.get('audit_logging') == True",
                    "description": "Access control and audit logging required"
                },
                "data_retention": {
                    "rule": "resource_data.get('data_retention_policy') == True and resource_data.get('data_deletion_capability') == True",
                    "description": "Data retention and deletion policies required"
                },
                "privacy_by_design": {
                    "rule": "resource_data.get('privacy_by_design') == True and resource_data.get('data_minimization') == True",
                    "description": "Privacy by design principles required"
                }
            }
        }
    
    async def check_compliance(
        self,
        framework: str,
        policy_name: Optional[str],
        resource_type: str,
        resource_data: Dict[str, Any],
        custom_policy: Optional[str] = None
    ) -> Dict[str, Any]:
        framework_lower = framework.lower().replace("-", "").replace("_", "")
        
        if custom_policy:
            return self._evaluate_custom_policy(custom_policy, resource_data)
        
        if framework_lower not in self.policies:
            return {
                "status": "error",
                "message": f"Framework '{framework}' not supported",
                "supported_frameworks": list(self.policies.keys())
            }
        
        framework_policies = self.policies[framework_lower]
        
        if policy_name:
            if policy_name not in framework_policies:
                return {
                    "status": "error",
                    "message": f"Policy '{policy_name}' not found in framework '{framework}'"
                }
            policies_to_check = {policy_name: framework_policies[policy_name]}
        else:
            policies_to_check = framework_policies
        
        results = {}
        all_passed = True
        
        for policy, policy_def in policies_to_check.items():
            try:
                passed = self._evaluate_rule(policy_def["rule"], resource_data)
                results[policy] = {
                    "passed": passed,
                    "description": policy_def["description"],
                    "rule": policy_def["rule"]
                }
                if not passed:
                    all_passed = False
            except Exception as e:
                logger.error(f"Error evaluating policy {policy}: {e}")
                results[policy] = {
                    "passed": False,
                    "error": str(e)
                }
                all_passed = False
        
        return {
            "status": "passed" if all_passed else "failed",
            "framework": framework,
            "policy_name": policy_name or "all",
            "resource_type": resource_type,
            "policies": results,
            "evidence": {
                "resource_data": resource_data,
                "checked_at": str(datetime.utcnow())
            }
        }
    
    def _evaluate_rule(self, rule: str, resource_data: Dict[str, Any]) -> bool:
        try:
            safe_dict = {"resource_data": resource_data}
            return eval(rule, {"__builtins__": {}}, safe_dict)
        except Exception as e:
            logger.error(f"Rule evaluation error: {e}")
            return False
    
    def _evaluate_custom_policy(self, policy: str, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            policy_dict = json.loads(policy) if isinstance(policy, str) else policy
            results = {}
            all_passed = True
            
            for rule_name, rule_def in policy_dict.items():
                rule = rule_def.get("rule", "")
                passed = self._evaluate_rule(rule, resource_data)
                results[rule_name] = {
                    "passed": passed,
                    "description": rule_def.get("description", ""),
                    "rule": rule
                }
                if not passed:
                    all_passed = False
            
            return {
                "status": "passed" if all_passed else "failed",
                "framework": "custom",
                "policy_name": "custom_policy",
                "policies": results,
                "evidence": {
                    "resource_data": resource_data,
                    "checked_at": str(datetime.utcnow())
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Custom policy evaluation failed: {str(e)}"
            }

