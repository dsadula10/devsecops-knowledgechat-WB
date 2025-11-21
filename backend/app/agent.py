import httpx
import json
import re
from typing import AsyncGenerator, Dict, Any, List, Optional
from app.tools.rag import RAGTool
from app.tools.scanner import ScannerTool
from app.tools.tickets import TicketTool
from app.models import ChatMessage, MessageRole, StreamEvent
import os

class DevSecOpsAgent:
    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")
        
        self.rag_tool = RAGTool()
        self.scanner_tool = ScannerTool()
        self.ticket_tool = TicketTool()
        
        self.tools = {
            "search_policies": self.rag_tool,
            "get_latest_scan": self.scanner_tool,
            "create_ticket": self.ticket_tool
        }
        
        # Simple in-memory history for the demo
        self.conversations: Dict[str, List[ChatMessage]] = {}
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            RAGTool.get_tool_definition(),
            ScannerTool.get_tool_definition(),
            TicketTool.get_tool_definition()
        ]
    
    def _build_system_prompt(self) -> str:
        tools_desc = json.dumps(self.get_tool_definitions(), indent=2)
        
        # streamlined prompt for tool calling reliability
        return f"""You are a DevSecOps assistant. You have access to the following tools:

{tools_desc}

PROTOCOL:
1. To use a tool, output ONLY the JSON object: {{"tool": "name", "args": {{...}}}}
2. Do not add text before or after the JSON.
3. After receiving a Tool Result, provide a natural language summary.

Use 'search_policies' for compliance/guidelines.
Use 'get_latest_scan' for vulnerability data.
Use 'create_ticket' for tracking issues.
"""
    
    async def chat_stream(self, message: str, conversation_id: str) -> AsyncGenerator[StreamEvent, None]:
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        conversation = self.conversations[conversation_id]
        conversation.append(ChatMessage(role=MessageRole.USER, content=message))
        
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        for msg in conversation:
            messages.append({"role": msg.role.value, "content": msg.content})
        
        # Cap iterations to prevent loops
        for _ in range(5):
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={"model": self.model, "messages": messages, "stream": False}
                )
                
                if response.status_code != 200:
                    yield StreamEvent(type="error", content=f"LLM Provider Error: {response.text}")
                    return
                
                result = response.json()
                content = result.get("message", {}).get("content", "").strip()
            
            tool_call = self._parse_tool_call(content)
            
            if tool_call:
                yield StreamEvent(type="tool_call", tool=tool_call["tool"], args=tool_call["args"])
                
                try:
                    # Execute and feed back to LLM
                    tool_result = await self._execute_tool(tool_call["tool"], tool_call["args"])
                    yield StreamEvent(type="tool_result", tool=tool_call["tool"], result=tool_result)
                    
                    messages.append({"role": "assistant", "content": content})
                    messages.append({
                        "role": "user", 
                        "content": f"Tool Result: {json.dumps(tool_result, default=str)}"
                    })
                except Exception as e:
                    yield StreamEvent(type="error", content=f"Tool Error: {str(e)}")
                    return
            else:
                # Final answer
                for token in content.split(" "):
                    yield StreamEvent(type="token", content=token + " ")
                
                conversation.append(ChatMessage(role=MessageRole.ASSISTANT, content=content))
                yield StreamEvent(type="done")
                return
    
    def _parse_tool_call(self, message: str) -> Optional[Dict[str, Any]]:
        try:
            if message.startswith('{') and message.endswith('}'):
                return json.loads(message)
            # Fallback regex for chatty models
            match = re.search(r'\{[^{}]*"tool"[^{}]*"args"[^{}]*\}', message, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return None
    
    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        if tool_name == "search_policies":
            results = self.rag_tool.search(args.get("query", ""), args.get("top_k", 3))
            return [{"content": r.content, "source": r.source} for r in results]
        
        elif tool_name == "get_latest_scan":
            scan = self.scanner_tool.get_latest_scan(args.get("project_id", ""))
            if scan:
                return scan.dict(exclude={'scan_date'}) | {"scan_date": scan.scan_date.isoformat()}
            return {"error": "Project not found"}
        
        elif tool_name == "create_ticket":
            ticket = self.ticket_tool.create_ticket(
                title=args.get("title", ""),
                description=args.get("description", ""),
                priority=args.get("priority", "medium"),
                project_id=args.get("project_id"),
                vulnerability_id=args.get("vulnerability_id")
            )
            return {"ticket_id": ticket.id, "status": "created"}
        
        raise ValueError(f"Unknown tool: {tool_name}")
