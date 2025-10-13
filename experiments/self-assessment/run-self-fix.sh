#!/bin/bash
# Run AICL Self-Assessment Experiment
# Uses AICL to fix itself using RAG + LLM judging

set -e

echo "=================================="
echo "AICL Self-Assessment Experiment"
echo "Use AICL to fix AICL"
echo "=================================="
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Phase 1: Index codebase
echo -e "${YELLOW}Phase 0: Test Judge System${NC}"
echo "Verifying judge works..."
echo
./aicl_modular run experiments/self-assessment/simple-judge-test.aicl

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Judge system working${NC}"
else
    echo -e "${RED}✗ Judge test failed${NC}"
    exit 1
fi

echo
echo "=================================="
echo

echo -e "${YELLOW}Phase 1: Index Codebase (Optional)${NC}"
echo "Skip indexing for now, use existing code patterns..."
echo "(Run index-codebase.aicl separately if you want full RAG)"
echo
# ./aicl_modular run experiments/self-assessment/index-codebase.aicl

echo "=================================="
echo

# Phase 2: Fix failing test
echo -e "${YELLOW}Phase 2: Self-Fix Failing Test${NC}"
echo "Using RAG + LLM to fix test_parse_config..."
echo
./aicl_modular run experiments/self-assessment/fix-test.aicl

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Fix generated and judged${NC}"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Review the proposed fix in the output above"
    echo "  2. Check the judge's score and reasoning"
    echo "  3. If score >= 80:"
    echo "     - Manually apply fix to tests/integration/test_engine.py"
    echo "     - Run: pytest tests/integration/test_engine.py -v"
    echo "     - Commit if tests pass"
    echo "  4. If score < 80:"
    echo "     - Review judge feedback"
    echo "     - Refine the experiment"
    echo "     - Run again"
else
    echo -e "${RED}✗ Self-fix experiment failed${NC}"
    echo "Check the output above for errors"
    exit 1
fi

echo
echo "=================================="
echo -e "${GREEN}Self-Assessment Complete!${NC}"
echo "=================================="
echo
echo "The tool tested itself. Review results and apply manually."
