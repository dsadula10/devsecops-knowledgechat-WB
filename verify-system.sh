#!/bin/bash

# DevSecOps Knowledge Chat - System Verification Script
# This script tests all components to ensure everything is working correctly

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  DevSecOps Knowledge Chat - System Verification${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Track test results
PASSED=0
FAILED=0

# Helper function for tests
run_test() {
    local test_name=$1
    local command=$2
    
    echo -n "Testing: $test_name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

# 1. System Prerequisites
echo -e "${YELLOW}[1/7] Checking System Prerequisites${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Python 3.11+ installed" "command -v python3"
run_test "Node.js installed" "command -v node"
run_test "npm installed" "command -v npm"
run_test "Ollama installed" "command -v ollama"
run_test "curl installed" "command -v curl"

echo ""

# 2. Ollama Service
echo -e "${YELLOW}[2/7] Checking Ollama Service${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Ollama server running" "curl -s http://localhost:11434/api/tags"
run_test "qwen2.5:14b model available" "ollama list | grep -q 'qwen2.5:14b'"

echo ""

# 3. Backend Service
echo -e "${YELLOW}[3/7] Checking Backend Service${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Backend health endpoint" "curl -s $BACKEND_URL/ | grep -q 'healthy'"
run_test "Backend API docs" "curl -s $BACKEND_URL/docs | grep -q 'FastAPI'"
run_test "Tools endpoint" "curl -s $BACKEND_URL/tools | grep -q 'search_policies'"
run_test "Projects endpoint" "curl -s $BACKEND_URL/projects | grep -q 'web-app-1'"
run_test "Tickets endpoint" "curl -s $BACKEND_URL/tickets | grep -q 'TICKET'"

echo ""

# 4. Database & Data
echo -e "${YELLOW}[4/7] Checking Database & Data${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "SQLite database exists" "test -f backend/data/tickets.db"
run_test "ChromaDB directory exists" "test -d backend/data/chroma_db"
run_test "Sample tickets in database" "curl -s $BACKEND_URL/tickets | grep -q 'TICKET-001'"

echo ""

# 5. Frontend Service
echo -e "${YELLOW}[5/7] Checking Frontend Service${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Frontend accessible" "curl -s $FRONTEND_URL | grep -q 'DevSecOps'"
run_test "Frontend loads React" "curl -s $FRONTEND_URL | grep -q 'root'"

echo ""

# 6. Tool Functionality
echo -e "${YELLOW}[6/7] Testing Tool Functionality${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test RAG tool
echo -n "Testing: RAG tool (search_policies)... "
RESPONSE=$(curl -s -X POST $BACKEND_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "password", "conversation_id": "test-rag"}')
if echo "$RESPONSE" | grep -q "search_policies"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test Scanner tool
echo -n "Testing: Scanner tool (get_latest_scan)... "
RESPONSE=$(curl -s -X POST $BACKEND_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "scan web-app-1", "conversation_id": "test-scan"}')
if echo "$RESPONSE" | grep -q "get_latest_scan"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test Ticket tool
echo -n "Testing: Ticket tool (create_ticket)... "
RESPONSE=$(curl -s -X POST $BACKEND_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "create a test ticket", "conversation_id": "test-ticket"}')
if echo "$RESPONSE" | grep -q "create_ticket"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo ""

# 7. File Structure
echo -e "${YELLOW}[7/7] Checking File Structure${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Backend main.py exists" "test -f backend/app/main.py"
run_test "Backend agent.py exists" "test -f backend/app/agent.py"
run_test "RAG tool exists" "test -f backend/app/tools/rag.py"
run_test "Scanner tool exists" "test -f backend/app/tools/scanner.py"
run_test "Ticket tool exists" "test -f backend/app/tools/tickets.py"
run_test "Frontend App.tsx exists" "test -f frontend/src/App.tsx"
run_test "Frontend Chat.tsx exists" "test -f frontend/src/components/Chat.tsx"
run_test "README exists" "test -f README.md"
run_test "Docker Compose exists" "test -f docker-compose.yml"

echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${GREEN}Passed: $PASSED${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed! System is ready for demo.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Open http://localhost:3000 in your browser"
    echo "  2. Try the example queries"
    echo "  3. Review the DEMO_CHECKLIST.md for interview tips"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please check the errors above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Ensure services are running: ./start-dev.sh"
    echo "  - Check Ollama is running: ollama serve"
    echo "  - Verify model is pulled: ollama pull qwen2.5:14b"
    echo ""
    exit 1
fi
