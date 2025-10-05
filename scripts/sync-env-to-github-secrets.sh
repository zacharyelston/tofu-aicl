#!/bin/bash

# sync-env-to-github-secrets.sh
# Script to sync .env file variables to GitHub repository secrets
# Requires: GitHub CLI (gh) installed and authenticated

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENV_FILE=".env"
DRY_RUN=false
FORCE=false
REPO=""

# Help function
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Sync environment variables from .env file to GitHub repository secrets.

OPTIONS:
    -f, --file FILE     Path to .env file (default: .env)
    -r, --repo REPO     GitHub repository (owner/repo format)
    -d, --dry-run       Show what would be done without making changes
    --force             Overwrite existing secrets without confirmation
    -h, --help          Show this help message

EXAMPLES:
    # Sync .env to current repository
    $0

    # Sync custom file to specific repository
    $0 --file .env.prod --repo myorg/myrepo

    # Preview changes without applying
    $0 --dry-run

REQUIREMENTS:
    - GitHub CLI (gh) must be installed and authenticated
    - Repository must exist and you must have admin access
    - .env file must exist and be readable

SECURITY NOTES:
    - This script will upload sensitive data to GitHub
    - Ensure your .env file doesn't contain local-only secrets
    - GitHub secrets are encrypted and only accessible to repository collaborators
    - Consider using different .env files for different environments
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            ENV_FILE="$2"
            shift 2
            ;;
        -r|--repo)
            REPO="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}" >&2
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Function to log messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed"
        log_info "Install it from: https://cli.github.com/"
        exit 1
    fi
    
    # Check if gh is authenticated
    if ! gh auth status &> /dev/null; then
        log_error "GitHub CLI is not authenticated"
        log_info "Run: gh auth login"
        exit 1
    fi
    
    # Check if .env file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Environment file '$ENV_FILE' not found"
        exit 1
    fi
    
    # Check if .env file is readable
    if [[ ! -r "$ENV_FILE" ]]; then
        log_error "Environment file '$ENV_FILE' is not readable"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Get repository information
get_repo_info() {
    if [[ -n "$REPO" ]]; then
        log_info "Using specified repository: $REPO"
        return
    fi
    
    # Try to get repo from current directory
    if git rev-parse --is-inside-work-tree &> /dev/null; then
        local remote_url
        remote_url=$(git config --get remote.origin.url 2>/dev/null || echo "")
        
        if [[ -n "$remote_url" ]]; then
            # Extract owner/repo from various GitHub URL formats
            if [[ "$remote_url" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
                REPO="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
                log_info "Detected repository: $REPO"
            fi
        fi
    fi
    
    if [[ -z "$REPO" ]]; then
        log_error "Could not determine repository. Use --repo option."
        exit 1
    fi
}

# Parse .env file and extract variables
parse_env_file() {
    local env_vars=()
    local line_num=0
    
    log_info "Parsing environment file: $ENV_FILE"
    
    while IFS= read -r line || [[ -n "$line" ]]; do
        ((line_num++))
        
        # Skip empty lines and comments
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        
        # Check for valid variable format
        if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*=[[:space:]]*(.*)[[:space:]]*$ ]]; then
            local var_name="${BASH_REMATCH[1]}"
            local var_value="${BASH_REMATCH[2]}"
            
            # Remove surrounding quotes if present
            if [[ "$var_value" =~ ^[\"\'](.*)[\"\']$ ]]; then
                var_value="${BASH_REMATCH[1]}"
            fi
            
            env_vars+=("$var_name:$var_value")
            log_info "Found variable: $var_name"
        else
            log_warning "Skipping invalid line $line_num: $line"
        fi
    done < "$ENV_FILE"
    
    if [[ ${#env_vars[@]} -eq 0 ]]; then
        log_warning "No valid environment variables found in $ENV_FILE"
        exit 0
    fi
    
    log_success "Found ${#env_vars[@]} environment variables"
    printf '%s\n' "${env_vars[@]}"
}

# Check existing secrets
check_existing_secrets() {
    local var_name="$1"
    
    if gh secret list --repo "$REPO" | grep -q "^$var_name[[:space:]]"; then
        return 0  # Secret exists
    else
        return 1  # Secret doesn't exist
    fi
}

# Set GitHub secret
set_github_secret() {
    local var_name="$1"
    local var_value="$2"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would set secret: $var_name"
        return 0
    fi
    
    # Check if secret already exists
    if check_existing_secrets "$var_name"; then
        if [[ "$FORCE" != "true" ]]; then
            log_warning "Secret '$var_name' already exists"
            read -p "Overwrite? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Skipping $var_name"
                return 0
            fi
        fi
        log_info "Updating existing secret: $var_name"
    else
        log_info "Creating new secret: $var_name"
    fi
    
    # Set the secret
    if echo "$var_value" | gh secret set "$var_name" --repo "$REPO"; then
        log_success "Successfully set secret: $var_name"
    else
        log_error "Failed to set secret: $var_name"
        return 1
    fi
}

# Main function
main() {
    log_info "Starting GitHub secrets sync..."
    log_info "Repository: $REPO"
    log_info "Environment file: $ENV_FILE"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi
    
    # Parse environment variables
    local env_vars
    mapfile -t env_vars < <(parse_env_file)
    
    if [[ ${#env_vars[@]} -eq 0 ]]; then
        log_info "No variables to sync"
        exit 0
    fi
    
    # Confirm before proceeding (unless dry run or force)
    if [[ "$DRY_RUN" != "true" && "$FORCE" != "true" ]]; then
        echo
        log_warning "This will upload ${#env_vars[@]} environment variables to GitHub repository '$REPO'"
        log_warning "These secrets will be accessible to repository collaborators and GitHub Actions"
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Operation cancelled"
            exit 0
        fi
    fi
    
    # Process each variable
    local success_count=0
    local error_count=0
    
    for env_var in "${env_vars[@]}"; do
        local var_name="${env_var%%:*}"
        local var_value="${env_var#*:}"
        
        if set_github_secret "$var_name" "$var_value"; then
            ((success_count++))
        else
            ((error_count++))
        fi
    done
    
    # Summary
    echo
    log_success "Sync completed!"
    log_info "Successfully processed: $success_count"
    if [[ $error_count -gt 0 ]]; then
        log_warning "Errors encountered: $error_count"
        exit 1
    fi
    
    if [[ "$DRY_RUN" != "true" ]]; then
        log_info "View secrets at: https://github.com/$REPO/settings/secrets/actions"
    fi
}

# Run the script
check_prerequisites
get_repo_info
main
