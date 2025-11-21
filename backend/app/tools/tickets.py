from typing import Optional, List
from datetime import datetime
import uuid
from app.models import Ticket, CreateTicketRequest, TicketPriority, TicketStatus
from app.database import SessionLocal, TicketDB
from sqlalchemy.orm import Session


class TicketTool:
    """Tool for creating and managing security tickets"""
    
    def __init__(self):
        pass
    
    def create_ticket(
        self,
        title: str,
        description: str,
        priority: str = "medium",
        project_id: Optional[str] = None,
        vulnerability_id: Optional[str] = None
    ) -> Ticket:
        """Create a new security ticket"""
        
        db = SessionLocal()
        try:
            # Generate ticket ID
            ticket_id = f"TICKET-{str(uuid.uuid4())[:8].upper()}"
            
            # Create ticket in database
            db_ticket = TicketDB(
                id=ticket_id,
                title=title,
                description=description,
                priority=priority,
                status="open",
                project_id=project_id,
                vulnerability_id=vulnerability_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(db_ticket)
            db.commit()
            db.refresh(db_ticket)
            
            # Convert to Pydantic model
            ticket = Ticket(
                id=db_ticket.id,
                title=db_ticket.title,
                description=db_ticket.description,
                priority=TicketPriority(db_ticket.priority),
                status=TicketStatus(db_ticket.status),
                project_id=db_ticket.project_id,
                vulnerability_id=db_ticket.vulnerability_id,
                created_at=db_ticket.created_at,
                updated_at=db_ticket.updated_at,
                assigned_to=db_ticket.assigned_to
            )
            
            return ticket
            
        finally:
            db.close()
    
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get a ticket by ID"""
        
        db = SessionLocal()
        try:
            db_ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()
            if not db_ticket:
                return None
            
            return Ticket(
                id=db_ticket.id,
                title=db_ticket.title,
                description=db_ticket.description,
                priority=TicketPriority(db_ticket.priority),
                status=TicketStatus(db_ticket.status),
                project_id=db_ticket.project_id,
                vulnerability_id=db_ticket.vulnerability_id,
                created_at=db_ticket.created_at,
                updated_at=db_ticket.updated_at,
                assigned_to=db_ticket.assigned_to
            )
        finally:
            db.close()
    
    def list_tickets(self, project_id: Optional[str] = None, status: Optional[str] = None) -> List[Ticket]:
        """List tickets with optional filters"""
        
        db = SessionLocal()
        try:
            query = db.query(TicketDB)
            
            if project_id:
                query = query.filter(TicketDB.project_id == project_id)
            if status:
                query = query.filter(TicketDB.status == status)
            
            db_tickets = query.order_by(TicketDB.created_at.desc()).all()
            
            return [
                Ticket(
                    id=t.id,
                    title=t.title,
                    description=t.description,
                    priority=TicketPriority(t.priority),
                    status=TicketStatus(t.status),
                    project_id=t.project_id,
                    vulnerability_id=t.vulnerability_id,
                    created_at=t.created_at,
                    updated_at=t.updated_at,
                    assigned_to=t.assigned_to
                )
                for t in db_tickets
            ]
        finally:
            db.close()
    
    @staticmethod
    def get_tool_definition():
        """Return tool definition for the agent"""
        return {
            "name": "create_ticket",
            "description": "Create a security ticket in the issue tracking system. Use this to file tickets for vulnerabilities, security issues, policy violations, or remediation tasks. The ticket will be saved to the database and assigned a unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Brief title describing the security issue"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue, impact, and recommended actions"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Priority level based on severity and impact",
                        "default": "medium"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project identifier (optional)"
                    },
                    "vulnerability_id": {
                        "type": "string",
                        "description": "Vulnerability ID if ticket is related to a scan finding (optional)"
                    }
                },
                "required": ["title", "description"]
            }
        }
