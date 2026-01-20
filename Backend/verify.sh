#!/bin/bash
# Verification script for Daystar Research Collaboration Graph
# Ensures all systems are properly configured

echo "=========================================="
echo "Daystar System Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

checks_passed=0
checks_failed=0

# Function to check if command exists
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        ((checks_passed++))
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        ((checks_failed++))
    fi
}

# Function to check Python module
check_python_module() {
    python3 -c "import $1" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Python module '$1' is installed"
        ((checks_passed++))
    else
        echo -e "${RED}✗${NC} Python module '$1' is NOT installed"
        ((checks_failed++))
    fi
}

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} File exists: $1"
        ((checks_passed++))
    else
        echo -e "${RED}✗${NC} File missing: $1"
        ((checks_failed++))
    fi
}

echo "1. SYSTEM DEPENDENCIES"
echo "====================="
check_command python3
check_command pip3
check_command docker
check_command docker-compose

echo ""
echo "2. PYTHON ENVIRONMENT"
echo "====================="
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${YELLOW}→${NC} Python version: $python_version"

check_python_module django
check_python_module rest_framework
check_python_module pgvector
check_python_module celery
check_python_module redis
check_python_module psycopg2

echo ""
echo "3. PROJECT STRUCTURE"
echo "====================="
check_file "COMPLETE_ARCHITECTURE.md"
check_file "requirements.txt"
check_file "Dockerfile"
check_file "docker-compose.yml"
check_file "daystar_project/settings.py"
check_file "daystar_project/celery.py"
check_file "research_graph/models.py"
check_file "research_graph/tasks.py"
check_file "research_graph/views.py"
check_file "research_graph/services.py"
check_file "research_graph/analytics.py"
check_file "research_graph/utils.py"

echo ""
echo "4. DATABASE CONFIGURATION"
echo "========================="
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    ((checks_passed++))
else
    echo -e "${YELLOW}!${NC} .env file not found (copy from .env.example)"
fi

echo ""
echo "5. PYTHON SYNTAX CHECK"
echo "======================"
python3 -m py_compile daystar_project/celery.py 2>/dev/null && \
python3 -m py_compile research_graph/tasks.py 2>/dev/null && \
python3 -m py_compile research_graph/views.py 2>/dev/null && \
python3 -m py_compile research_graph/models.py 2>/dev/null && \
echo -e "${GREEN}✓${NC} All Python files have valid syntax" && \
((checks_passed++)) || \
(echo -e "${RED}✗${NC} Python syntax errors found" && ((checks_failed++)))

echo ""
echo "=========================================="
echo "VERIFICATION SUMMARY"
echo "=========================================="
echo -e "Checks Passed: ${GREEN}$checks_passed${NC}"
echo -e "Checks Failed: ${RED}$checks_failed${NC}"

if [ $checks_failed -eq 0 ]; then
    echo -e "${GREEN}✓ All systems ready!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Copy .env.example to .env and configure"
    echo "2. Run: docker-compose up -d"
    echo "3. Run: docker-compose exec web python manage.py migrate"
    echo "4. Visit: http://localhost:8000/admin"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review above.${NC}"
    exit 1
fi
