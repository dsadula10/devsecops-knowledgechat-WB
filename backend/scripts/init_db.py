#!/usr/bin/env python3
"""Initialize the SQLite database with sample tickets"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import init_db, SessionLocal, TicketDB
from datetime import datetime, timedelta


def create_sample_tickets():
    """Create sample tickets in the database"""
    
    db = SessionLocal()
    
    sample_tickets = [
        {
            "id": "TICKET-001",
            "title": "Fix SQL Injection in Login Form",
            "description": "Critical SQL injection vulnerability found in the user login endpoint. This allows unauthorized database access and potential data breach. Immediate action required.",
            "priority": "critical",
            "status": "open",
            "project_id": "web-app-1",
            "vulnerability_id": "VULN-2024-001",
            "created_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "id": "TICKET-002",
            "title": "Update OpenSSL to Latest Version",
            "description": "Currently using OpenSSL 1.0.1 which has multiple known CVEs. Need to upgrade to OpenSSL 3.0 or later to address security vulnerabilities.",
            "priority": "critical",
            "status": "in_progress",
            "project_id": "web-app-1",
            "vulnerability_id": "VULN-2024-003",
            "assigned_to": "security-team",
            "created_at": datetime.utcnow() - timedelta(days=5)
        },
        {
            "id": "TICKET-003",
            "title": "Implement JWT Token Expiration",
            "description": "JWT tokens are being issued without expiration times, allowing indefinite access. Implement proper token expiration (15-60 minutes) and refresh token mechanism.",
            "priority": "critical",
            "status": "open",
            "project_id": "api-service",
            "vulnerability_id": "VULN-2024-006",
            "created_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "id": "TICKET-004",
            "title": "Add Rate Limiting to API Endpoints",
            "description": "API endpoints lack rate limiting, making them vulnerable to brute force attacks. Implement rate limiting using Redis or similar solution.",
            "priority": "high",
            "status": "open",
            "project_id": "api-service",
            "vulnerability_id": "VULN-2024-007",
            "created_at": datetime.utcnow() - timedelta(hours=12)
        },
        {
            "id": "TICKET-005",
            "title": "Implement Certificate Pinning in Mobile App",
            "description": "Mobile app HTTPS connections don't use certificate pinning, vulnerable to MITM attacks. Implement SSL certificate pinning for all API communications.",
            "priority": "high",
            "status": "open",
            "project_id": "mobile-app",
            "vulnerability_id": "VULN-2024-011",
            "created_at": datetime.utcnow() - timedelta(hours=6)
        }
    ]
    
    try:
        # Clear existing tickets
        db.query(TicketDB).delete()
        
        # Add sample tickets
        for ticket_data in sample_tickets:
            ticket = TicketDB(**ticket_data)
            db.add(ticket)
        
        db.commit()
        print(f"✅ Created {len(sample_tickets)} sample tickets")
        
        # Verify
        count = db.query(TicketDB).count()
        print(f"✅ Total tickets in database: {count}")
        
    except Exception as e:
        print(f"❌ Error creating sample tickets: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    print("🔧 Initializing database...")
    
    # Create database tables
    init_db()
    print("✅ Database tables created")
    
    # Create sample tickets
    create_sample_tickets()
    
    print("✅ Database initialization complete!")


if __name__ == "__main__":
    main()
