#!/usr/bin/env python3
"""Ingest security policies into ChromaDB"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.tools.rag import RAGTool
from pypdf import PdfReader
import glob


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """Extract text from PDF with page numbers"""
    
    try:
        reader = PdfReader(pdf_path)
        documents = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                # Split into chunks (simple paragraph-based chunking)
                paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                
                for para in paragraphs:
                    if len(para) > 50:  # Only keep substantial paragraphs
                        documents.append({
                            'content': para,
                            'source': os.path.basename(pdf_path),
                            'page': page_num
                        })
        
        return documents
    
    except Exception as e:
        print(f"❌ Error reading {pdf_path}: {e}")
        return []


def ingest_policies():
    """Ingest all policy PDFs into ChromaDB"""
    
    print("📚 Ingesting security policies...")
    
    # Initialize RAG tool
    rag_tool = RAGTool()
    
    # Find all PDFs in policies directory
    policies_dir = os.path.join(os.path.dirname(__file__), '..', 'policies')
    pdf_files = glob.glob(os.path.join(policies_dir, '*.pdf'))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in {policies_dir}")
        print("⚠️  Creating sample policy documents as text instead...")
        create_sample_text_policies(rag_tool)
        return
    
    total_chunks = 0
    
    for pdf_path in pdf_files:
        print(f"📄 Processing {os.path.basename(pdf_path)}...")
        
        documents = extract_text_from_pdf(pdf_path)
        
        if documents:
            # Prepare for ChromaDB
            contents = [doc['content'] for doc in documents]
            metadatas = [{'source': doc['source'], 'page': doc['page']} for doc in documents]
            
            # Add to vector store
            rag_tool.add_documents(contents, metadatas)
            
            total_chunks += len(documents)
            print(f"  ✅ Added {len(documents)} chunks from {os.path.basename(pdf_path)}")
    
    print(f"\n✅ Ingestion complete! Total chunks: {total_chunks}")


def create_sample_text_policies(rag_tool: RAGTool):
    """
    Fallback method: Ingests hardcoded OWASP and internal policy samples.
    Used for portable demos where PDF parsing dependencies or files might be missing.
    """
    
    sample_policies = [
        {
            "content": "OWASP Top 10 - A01: Broken Access Control. Access control enforces policy such that users cannot act outside of their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction of all data or performing a business function outside the user's limits.",
            "source": "owasp_top10.pdf",
            "page": 1
        },
        {
            "content": "OWASP Top 10 - A02: Cryptographic Failures. The first thing is to determine the protection needs of data in transit and at rest. For example, passwords, credit card numbers, health records, personal information, and business secrets require extra protection, mainly if that data falls under privacy laws, e.g., EU's General Data Protection Regulation (GDPR), or regulations, e.g., financial data protection such as PCI Data Security Standard (PCI DSS).",
            "source": "owasp_top10.pdf",
            "page": 2
        },
        {
            "content": "OWASP Top 10 - A03: Injection. Injection flaws, such as SQL, NoSQL, OS, and LDAP injection, occur when untrusted data is sent to an interpreter as part of a command or query. The attacker's hostile data can trick the interpreter into executing unintended commands or accessing data without proper authorization. Use parameterized queries, ORMs, or stored procedures to prevent injection attacks.",
            "source": "owasp_top10.pdf",
            "page": 3
        },
        {
            "content": "OWASP Top 10 - A04: Insecure Design. Insecure design is a broad category representing different weaknesses, expressed as 'missing or ineffective control design.' Insecure design is not the source for all other Top 10 risk categories. There is a difference between insecure design and insecure implementation. We differentiate between design flaws and implementation defects for a reason; they have different root causes and remediation.",
            "source": "owasp_top10.pdf",
            "page": 4
        },
        {
            "content": "OWASP Top 10 - A05: Security Misconfiguration. Security misconfiguration vulnerabilities occur when security settings are defined, implemented, maintained incorrectly. This includes: Missing appropriate security hardening across any part of the application stack, Unnecessary features enabled or installed, Default accounts and their passwords still enabled and unchanged, Error handling reveals stack traces or other overly informative error messages to users.",
            "source": "owasp_top10.pdf",
            "page": 5
        },
        {
            "content": "OWASP Top 10 - A06: Vulnerable and Outdated Components. You are likely vulnerable if you do not know the versions of all components you use (both client-side and server-side). This includes components you directly use as well as nested dependencies. If the software is vulnerable, unsupported, or out of date includes the OS, web/application server, DBMS, applications, APIs, and all components, runtime environments, and libraries.",
            "source": "owasp_top10.pdf",
            "page": 6
        },
        {
            "content": "OWASP Top 10 - A07: Identification and Authentication Failures. Confirmation of the user's identity, authentication, and session management is critical to protect against authentication-related attacks. There may be authentication weaknesses if the application: Permits automated attacks such as credential stuffing, where the attacker has a list of valid usernames and passwords. Permits brute force or other automated attacks. Permits default, weak, or well-known passwords.",
            "source": "owasp_top10.pdf",
            "page": 7
        },
        {
            "content": "Company Password Policy: All user passwords must meet the following requirements: Minimum length of 12 characters, Must include at least one uppercase letter, one lowercase letter, one number, and one special character, Cannot contain the user's name or email address, Must be changed every 90 days, Cannot reuse any of the last 5 passwords, Multi-factor authentication (MFA) is required for all administrative accounts and recommended for all users.",
            "source": "password_guidelines.pdf",
            "page": 1
        },
        {
            "content": "Company Password Policy - Account Lockout: To prevent brute force attacks, user accounts will be temporarily locked after 5 consecutive failed login attempts. The lockout duration is 15 minutes. After 10 failed attempts within 24 hours, the account will be locked pending manual review by the security team. Administrative accounts are locked after 3 failed attempts.",
            "source": "password_guidelines.pdf",
            "page": 2
        },
        {
            "content": "Company Security Policy - Data Encryption: All sensitive data must be encrypted both in transit and at rest. In transit: Use TLS 1.2 or higher for all network communications. SSL and TLS 1.0/1.1 are prohibited. At rest: Use AES-256 encryption for data storage. Database encryption must be enabled for all production databases. Encryption keys must be managed through a dedicated key management system (KMS) and rotated every 6 months.",
            "source": "company_security_policy.pdf",
            "page": 1
        },
        {
            "content": "Company Security Policy - Access Control: All systems must implement the principle of least privilege. Users should only have access to resources necessary for their job function. Role-Based Access Control (RBAC) must be implemented for all applications. Access reviews must be conducted quarterly. Terminated employees must have all access revoked within 1 hour of termination. Privileged access must be logged and monitored.",
            "source": "company_security_policy.pdf",
            "page": 2
        },
        {
            "content": "Company Security Policy - Vulnerability Management: All production systems must undergo vulnerability scanning at least monthly. Critical vulnerabilities (CVSS score 9.0+) must be patched within 7 days. High severity vulnerabilities (CVSS 7.0-8.9) must be patched within 30 days. Medium severity vulnerabilities must be patched within 90 days. All patch deployments must follow the change management process. Penetration testing must be conducted annually.",
            "source": "company_security_policy.pdf",
            "page": 3
        },
        {
            "content": "Company Security Policy - Secure Development: All code must undergo security review before production deployment. Use SAST (Static Application Security Testing) tools in the CI/CD pipeline. Dependencies must be scanned for known vulnerabilities using SCA (Software Composition Analysis) tools. Secrets (API keys, passwords, tokens) must never be hardcoded in source code. Use environment variables and secure secret management systems. All inputs must be validated and sanitized. Use parameterized queries to prevent injection attacks.",
            "source": "company_security_policy.pdf",
            "page": 4
        },
        {
            "content": "Company Security Policy - Incident Response: All security incidents must be reported within 1 hour of detection. The incident response team must be notified via the security hotline or email. Incident severity levels: Critical - Active breach with data exfiltration, High - Attempted breach or significant vulnerability, Medium - Policy violation or suspicious activity, Low - Minor security event. Critical incidents require executive notification within 2 hours.",
            "source": "company_security_policy.pdf",
            "page": 5
        },
        {
            "content": "API Security Best Practices: All API endpoints must require authentication. Use OAuth 2.0 or JWT tokens for API authentication. Implement rate limiting to prevent abuse (recommended: 100 requests per minute per user). Use HTTPS for all API communications. Validate all input parameters and sanitize output. Implement proper error handling without exposing sensitive information. Use API versioning to maintain backwards compatibility. Document all API endpoints with security requirements.",
            "source": "company_security_policy.pdf",
            "page": 6
        }
    ]
    
    # Add to vector store
    contents = [p["content"] for p in sample_policies]
    metadatas = [{"source": p["source"], "page": p["page"]} for p in sample_policies]
    
    rag_tool.add_documents(contents, metadatas)
    
    print(f"✅ Added {len(sample_policies)} sample policy chunks to vector store")


def main():
    ingest_policies()
    print("✅ Policy ingestion complete!")


if __name__ == "__main__":
    main()
