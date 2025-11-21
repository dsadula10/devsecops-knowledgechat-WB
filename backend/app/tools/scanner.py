from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import random
from app.models import ScanResult


class ScannerTool:
    """Mock security scanner tool that returns fake vulnerability scan results"""
    
    # Mock vulnerability database
    MOCK_VULNERABILITIES = {
        "web-app-1": [
            {
                "id": "VULN-2024-001",
                "title": "SQL Injection in Login Form",
                "severity": "critical",
                "cve": "CVE-2024-1234",
                "description": "SQL injection vulnerability found in user login endpoint. Allows unauthorized database access.",
                "affected_component": "auth/login.py",
                "recommendation": "Use parameterized queries and input validation"
            },
            {
                "id": "VULN-2024-002",
                "title": "Cross-Site Scripting (XSS) in Comments",
                "severity": "high",
                "cve": "CVE-2024-1235",
                "description": "Stored XSS vulnerability in user comment system. Could lead to session hijacking.",
                "affected_component": "comments/views.py",
                "recommendation": "Implement proper output encoding and Content Security Policy"
            },
            {
                "id": "VULN-2024-003",
                "title": "Outdated OpenSSL Version",
                "severity": "critical",
                "cve": "CVE-2023-5678",
                "description": "Using OpenSSL 1.0.1 which has known vulnerabilities",
                "affected_component": "requirements.txt",
                "recommendation": "Update to OpenSSL 3.0 or later"
            },
            {
                "id": "VULN-2024-004",
                "title": "Missing CSRF Protection",
                "severity": "high",
                "description": "CSRF tokens not implemented on state-changing operations",
                "affected_component": "middleware/security.py",
                "recommendation": "Implement CSRF token validation"
            },
            {
                "id": "VULN-2024-005",
                "title": "Weak Password Policy",
                "severity": "medium",
                "description": "Password requirements allow weak passwords (minimum 6 characters)",
                "affected_component": "auth/validators.py",
                "recommendation": "Enforce minimum 12 characters with complexity requirements"
            }
        ],
        "api-service": [
            {
                "id": "VULN-2024-006",
                "title": "JWT Token Without Expiration",
                "severity": "critical",
                "cve": None,
                "description": "JWT tokens issued without expiration time, allowing indefinite access",
                "affected_component": "auth/jwt.py",
                "recommendation": "Set appropriate token expiration (15-60 minutes)"
            },
            {
                "id": "VULN-2024-007",
                "title": "Missing Rate Limiting",
                "severity": "high",
                "description": "API endpoints lack rate limiting, vulnerable to brute force attacks",
                "affected_component": "api/middleware.py",
                "recommendation": "Implement rate limiting with Redis or similar"
            },
            {
                "id": "VULN-2024-008",
                "title": "Sensitive Data in Logs",
                "severity": "high",
                "description": "API keys and passwords logged in plain text",
                "affected_component": "utils/logging.py",
                "recommendation": "Implement log sanitization for sensitive data"
            },
            {
                "id": "VULN-2024-009",
                "title": "Outdated Django Version",
                "severity": "medium",
                "cve": "CVE-2023-9876",
                "description": "Using Django 3.2.0 with known security patches",
                "affected_component": "requirements.txt",
                "recommendation": "Update to Django 4.2 LTS"
            }
        ],
        "mobile-app": [
            {
                "id": "VULN-2024-010",
                "title": "Insecure Data Storage",
                "severity": "high",
                "description": "Sensitive user data stored without encryption in SQLite",
                "affected_component": "storage/database.dart",
                "recommendation": "Use encrypted storage (SQLCipher) for sensitive data"
            },
            {
                "id": "VULN-2024-011",
                "title": "Missing Certificate Pinning",
                "severity": "high",
                "description": "HTTPS connections don't use certificate pinning",
                "affected_component": "network/client.dart",
                "recommendation": "Implement SSL certificate pinning"
            },
            {
                "id": "VULN-2024-012",
                "title": "Hardcoded API Keys",
                "severity": "medium",
                "description": "API keys found in source code",
                "affected_component": "config/constants.dart",
                "recommendation": "Use environment variables and secure key storage"
            },
            {
                "id": "VULN-2024-013",
                "title": "Weak Biometric Authentication",
                "severity": "medium",
                "description": "Biometric auth fallback allows unlimited PIN attempts",
                "affected_component": "auth/biometric.dart",
                "recommendation": "Implement attempt limiting and account lockout"
            }
        ]
    }
    
    def get_latest_scan(self, project_id: str) -> Optional[ScanResult]:
        """Get the latest security scan results for a project"""
        
        if project_id not in self.MOCK_VULNERABILITIES:
            return None
        
        findings = self.MOCK_VULNERABILITIES[project_id]
        
        # Count by severity
        critical = sum(1 for f in findings if f['severity'] == 'critical')
        high = sum(1 for f in findings if f['severity'] == 'high')
        medium = sum(1 for f in findings if f['severity'] == 'medium')
        low = sum(1 for f in findings if f['severity'] == 'low')
        
        # Create scan result
        scan_result = ScanResult(
            project_id=project_id,
            scan_date=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            total_vulnerabilities=len(findings),
            critical=critical,
            high=high,
            medium=medium,
            low=low,
            findings=findings
        )
        
        return scan_result
    
    def list_projects(self) -> list[str]:
        """List all available projects"""
        return list(self.MOCK_VULNERABILITIES.keys())
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        """Return tool definition for the agent"""
        return {
            "name": "get_latest_scan",
            "description": "Retrieve the latest security vulnerability scan results for a specific project. Returns detailed findings including severity levels, CVE IDs, affected components, and remediation recommendations. Use this to check for security issues, analyze vulnerabilities, or get scan summaries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "The project identifier (e.g., 'web-app-1', 'api-service', 'mobile-app')"
                    }
                },
                "required": ["project_id"]
            }
        }
