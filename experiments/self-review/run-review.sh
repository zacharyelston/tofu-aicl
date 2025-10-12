#!/bin/bash
# Run AICL Self-Review in Docker

set -e

cd "$(dirname "$0")"

echo "=================================="
echo "AICL Self-Review (Dockerized)"
echo "=================================="
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if specific review requested
REVIEW_TYPE="${1:-all}"

case "$REVIEW_TYPE" in
  code)
    echo -e "${BLUE}Running Code Quality Review...${NC}"
    docker-compose -f docker-compose.review.yml build
    docker-compose -f docker-compose.review.yml --profile code up review-code
    ;;
  
  tests)
    echo -e "${BLUE}Running Test Coverage Review...${NC}"
    docker-compose -f docker-compose.review.yml build
    docker-compose -f docker-compose.review.yml --profile tests up review-tests
    ;;
  
  arch)
    echo -e "${BLUE}Running Architecture Review...${NC}"
    docker-compose -f docker-compose.review.yml build
    docker-compose -f docker-compose.review.yml --profile arch up review-architecture
    ;;
  
  shell)
    echo -e "${BLUE}Starting Interactive Shell...${NC}"
    docker-compose -f docker-compose.review.yml build
    docker-compose -f docker-compose.review.yml --profile shell run review-shell
    ;;
  
  all)
    echo -e "${BLUE}Running All Reviews...${NC}"
    echo
    
    # Build once
    echo -e "${YELLOW}Building review image...${NC}"
    docker-compose -f docker-compose.review.yml build
    
    # Run code quality
    echo
    echo -e "${YELLOW}1/3: Code Quality Review${NC}"
    docker-compose -f docker-compose.review.yml --profile code up review-code
    
    # Run test coverage
    echo
    echo -e "${YELLOW}2/3: Test Coverage Review${NC}"
    docker-compose -f docker-compose.review.yml --profile tests up review-tests
    
    # Run architecture
    echo
    echo -e "${YELLOW}3/3: Architecture Review${NC}"
    docker-compose -f docker-compose.review.yml --profile arch up review-architecture
    
    echo
    echo -e "${GREEN}✓ All reviews complete!${NC}"
    echo "Check results/ directory for reports"
    ;;
  
  *)
    echo "Usage: $0 {code|tests|arch|shell|all}"
    echo
    echo "Reviews:"
    echo "  code   - Code quality analysis"
    echo "  tests  - Test coverage analysis"
    echo "  arch   - Architecture review"
    echo "  shell  - Interactive shell"
    echo "  all    - Run all reviews (default)"
    exit 1
    ;;
esac

echo
echo "=================================="
echo -e "${GREEN}Review Complete!${NC}"
echo "=================================="
