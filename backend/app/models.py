from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class ToolType(str, Enum):
    SEARCH_POLICIES = "search_policies"
    GET_LATEST_SCAN = "get_latest_scan"
    CREATE_TICKET = "create_ticket"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class StreamEvent(BaseModel):
    type: Literal["token", "tool_call", "tool_result", "reasoning", "done", "error"]
    content: Optional[str] = None
    tool: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None


class PolicySearchRequest(BaseModel):
    query: str
    top_k: int = 3


class PolicySearchResult(BaseModel):
    content: str
    source: str
    page: Optional[int] = None
    score: float


class ScanResult(BaseModel):
    project_id: str
    scan_date: datetime
    total_vulnerabilities: int
    critical: int
    high: int
    medium: int
    low: int
    findings: List[Dict[str, Any]]


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CreateTicketRequest(BaseModel):
    title: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM
    project_id: Optional[str] = None
    vulnerability_id: Optional[str] = None


class Ticket(BaseModel):
    id: str
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    project_id: Optional[str] = None
    vulnerability_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str] = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
