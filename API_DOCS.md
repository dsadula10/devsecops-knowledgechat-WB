# 📚 API Documentation & Testing Guide

## Base URL
```
http://localhost:8000
```

## API Endpoints

### 1. Health Check
**GET** `/`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "DevSecOps Knowledge Chat",
  "version": "1.0.0"
}
```

**Test:**
```bash
curl http://localhost:8000/
```

---

### 2. List Available Tools
**GET** `/tools`

Get all available tools with their definitions.

**Response:**
```json
{
  "tools": [
    {
      "name": "search_policies",
      "description": "Search security policies and guidelines...",
      "parameters": { ... }
    },
    {
      "name": "get_latest_scan",
      "description": "Retrieve vulnerability scan results...",
      "parameters": { ... }
    },
    {
      "name": "create_ticket",
      "description": "Create a security ticket...",
      "parameters": { ... }
    }
  ]
}
```

**Test:**
```bash
curl http://localhost:8000/tools | jq
```

---

### 3. Chat (Streaming)
**POST** `/chat`

Send a message and receive a streaming response.

**Request Body:**
```json
{
  "message": "What does our password policy say?",
  "conversation_id": "optional-uuid-here"
}
```

**Response:** Server-Sent Events (SSE) stream

**Event Types:**

1. **Token Event** (streaming response text)
```json
{
  "type": "token",
  "content": "According to ",
  "conversation_id": "uuid"
}
```

2. **Tool Call Event** (tool being invoked)
```json
{
  "type": "tool_call",
  "tool": "search_policies",
  "args": {
    "query": "password policy",
    "top_k": 3
  },
  "conversation_id": "uuid"
}
```

3. **Tool Result Event** (tool execution result)
```json
{
  "type": "tool_result",
  "tool": "search_policies",
  "result": [
    {
      "content": "Password requirements...",
      "source": "password_guidelines.pdf",
      "page": 1,
      "score": 0.89
    }
  ],
  "conversation_id": "uuid"
}
```

4. **Error Event**
```json
{
  "type": "error",
  "content": "Error message here",
  "conversation_id": "uuid"
}
```

5. **Done Event**
```json
{
  "type": "done",
  "conversation_id": "uuid"
}
```

**Test with curl:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does our password policy say?",
    "conversation_id": "test-123"
  }'
```

**Test with Python:**
```python
import requests
import json

response = requests.post(
    'http://localhost:8000/chat',
    json={
        'message': 'Show me scan results for web-app-1',
        'conversation_id': 'test-456'
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data = json.loads(line_str[6:])
            print(data)
```

---

### 4. Get Conversation
**GET** `/conversations/{conversation_id}`

Retrieve conversation history.

**Response:**
```json
{
  "conversation_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "What is our password policy?",
      "timestamp": "2024-11-21T10:30:00"
    },
    {
      "role": "assistant",
      "content": "According to our password policy...",
      "timestamp": "2024-11-21T10:30:05"
    }
  ]
}
```

**Test:**
```bash
curl http://localhost:8000/conversations/test-123 | jq
```

---

### 5. List Projects
**GET** `/projects`

Get all available projects for vulnerability scanning.

**Response:**
```json
{
  "projects": [
    "web-app-1",
    "api-service",
    "mobile-app"
  ]
}
```

**Test:**
```bash
curl http://localhost:8000/projects | jq
```

---

### 6. List Tickets
**GET** `/tickets`

Get all tickets with optional filters.

**Query Parameters:**
- `project_id` (optional): Filter by project
- `status` (optional): Filter by status (open, in_progress, resolved, closed)

**Response:**
```json
{
  "tickets": [
    {
      "id": "TICKET-001",
      "title": "Fix SQL Injection in Login Form",
      "description": "Critical SQL injection...",
      "priority": "critical",
      "status": "open",
      "project_id": "web-app-1",
      "created_at": "2024-11-19T10:00:00"
    }
  ]
}
```

**Test:**
```bash
# All tickets
curl http://localhost:8000/tickets | jq

# Filter by project
curl http://localhost:8000/tickets?project_id=web-app-1 | jq

# Filter by status
curl http://localhost:8000/tickets?status=open | jq

# Combined filters
curl "http://localhost:8000/tickets?project_id=web-app-1&status=open" | jq
```

---

## Sample Test Scenarios

### Scenario 1: Policy Search
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does OWASP say about SQL injection?",
    "conversation_id": "policy-test-1"
  }'
```

**Expected:**
- Tool call: `search_policies`
- Result contains OWASP Top 10 information
- Natural language response explaining prevention

### Scenario 2: Vulnerability Scan
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me critical vulnerabilities in web-app-1",
    "conversation_id": "scan-test-1"
  }'
```

**Expected:**
- Tool call: `get_latest_scan` with project_id
- Result shows scan data
- Response lists critical vulnerabilities

### Scenario 3: Ticket Creation
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a critical ticket for SQL injection in login form",
    "conversation_id": "ticket-test-1"
  }'
```

**Expected:**
- Tool call: `create_ticket`
- Ticket ID returned
- Confirmation message

### Scenario 4: Multi-Tool Workflow
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Check web-app-1 scan and create tickets for critical issues",
    "conversation_id": "multi-test-1"
  }'
```

**Expected:**
- First tool call: `get_latest_scan`
- Multiple tool calls: `create_ticket` (one per critical issue)
- Summary response

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

**Swagger UI:**
```
http://localhost:8000/docs
```

**ReDoc:**
```
http://localhost:8000/redoc
```

You can test all endpoints directly from the Swagger UI!

---

## Testing with Postman

### Import Collection

Create a Postman collection with these requests:

1. **Health Check**
   - Method: GET
   - URL: `http://localhost:8000/`

2. **List Tools**
   - Method: GET
   - URL: `http://localhost:8000/tools`

3. **Chat - Policy Search**
   - Method: POST
   - URL: `http://localhost:8000/chat`
   - Body (JSON):
     ```json
     {
       "message": "What is our password policy?",
       "conversation_id": "{{$guid}}"
     }
     ```

4. **Chat - Scan Results**
   - Method: POST
   - URL: `http://localhost:8000/chat`
   - Body (JSON):
     ```json
     {
       "message": "Show scan for web-app-1",
       "conversation_id": "{{$guid}}"
     }
     ```

5. **List Tickets**
   - Method: GET
   - URL: `http://localhost:8000/tickets`

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200 OK** - Successful request
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Invalid request body
- **500 Internal Server Error** - Server error

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

---

## Rate Limiting (Future)

For production, implement rate limiting:

```python
# Example with slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_req: ChatRequest):
    # ...
```

---

## WebSocket Alternative (Future Enhancement)

For true bidirectional communication:

```python
from fastapi import WebSocket

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        # Process and stream back
        await websocket.send_text(response)
```

---

## Monitoring & Logging

### Current Logging
All tool calls and agent actions are logged to stdout.

### Production Recommendations

1. **Structured Logging**
   ```python
   import structlog
   
   logger = structlog.get_logger()
   logger.info("tool_called", tool="search_policies", args=args)
   ```

2. **Request Tracking**
   ```python
   from fastapi import Request
   import uuid
   
   @app.middleware("http")
   async def add_request_id(request: Request, call_next):
       request_id = str(uuid.uuid4())
       request.state.request_id = request_id
       response = await call_next(request)
       response.headers["X-Request-ID"] = request_id
       return response
   ```

3. **Metrics**
   ```python
   from prometheus_client import Counter, Histogram
   
   tool_calls = Counter('tool_calls_total', 'Total tool calls', ['tool_name'])
   response_time = Histogram('response_time_seconds', 'Response time')
   ```

---

## Testing Checklist

- [ ] All endpoints return 200 OK
- [ ] Tools endpoint returns 3 tools
- [ ] Projects endpoint returns 3 projects
- [ ] Tickets endpoint returns sample tickets
- [ ] Chat endpoint streams SSE events
- [ ] RAG tool returns relevant results
- [ ] Scanner tool returns mock vulnerabilities
- [ ] Ticket creation saves to database
- [ ] Conversation history is retrievable
- [ ] Error handling works (try invalid JSON)

---

## Performance Benchmarks

### Expected Response Times (Local Development)

- Health check: < 10ms
- List tools/projects/tickets: < 50ms
- RAG search: 200-500ms (depends on collection size)
- Scanner tool: < 10ms (mock data)
- Ticket creation: < 100ms
- Full chat response: 2-10s (depends on LLM and response length)

### Load Testing

```bash
# Install Apache Bench
brew install httpd

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/

# Test chat endpoint (requires wrk or similar)
wrk -t2 -c10 -d30s --latency \
  -s chat.lua \
  http://localhost:8000/chat
```

---

## Security Headers (Production)

Add these headers for production:

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# HTTPS redirect
app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

---

**Happy Testing! 🚀**
