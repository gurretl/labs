#!/bin/bash

# Script to restore a deleted Azure DevOps repository
# Uses Azure DevOps REST API to list and restore deleted repositories

# Colors for display
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check that jq and curl are installed
if ! command -v jq &> /dev/null; then
    log_error "jq is not installed. Please install it with: sudo apt-get install jq"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    log_error "curl is not installed. Please install it with: sudo apt-get install curl"
    exit 1
fi

# Banner
echo "=========================================="
echo "  Azure DevOps Repository Restore Tool"
echo "=========================================="
echo

# Ask for necessary information
read -p "Enter Azure DevOps project URL (ex: https://dev.azure.com/myorg/myproject): " PROJECT_URL

# Validate URL format
if [[ ! "$PROJECT_URL" =~ ^https://dev\.azure\.com/[^/]+/[^/]+/?$ ]]; then
    log_error "Invalid URL format. Expected: https://dev.azure.com/{ORGANIZATION}/{PROJECT}"
    exit 1
fi

# Extract organization and project
PROJECT_URL="${PROJECT_URL%/}"  # Remove trailing slash
ORGANIZATION=$(echo "$PROJECT_URL" | sed 's|https://dev.azure.com/\([^/]*\)/.*|\1|')
PROJECT=$(echo "$PROJECT_URL" | sed 's|https://dev.azure.com/[^/]*/\([^/]*\)|\1|')

echo
read -s -p "Enter your Personal Access Token (PAT): " PAT
echo
echo

if [ -z "$PAT" ]; then
    log_error "PAT cannot be empty"
    exit 1
fi

log_info "Organization: $ORGANIZATION"
log_info "Project: $PROJECT"
echo

# Get deleted repositories
log_info "Retrieving deleted repositories..."

PROJECT_ENCODED=$(echo "$PROJECT" | sed 's/ /%20/g')
URL="https://dev.azure.com/${ORGANIZATION}/${PROJECT_ENCODED}/_apis/git/deletedrepositories?api-version=5.1-preview.1"

log_info "Calling URL: $URL"

RESPONSE=$(curl -s -u ":${PAT}" "$URL")

if [ $? -ne 0 ]; then
    log_error "Error during API call"
    exit 1
fi

# Check if response is valid JSON
if ! echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    log_error "Invalid response received:"
    log_error "$RESPONSE"
    exit 1
fi

# Check for API errors
if echo "$RESPONSE" | jq -e '.message' > /dev/null 2>&1; then
    log_error "API Error: $(echo "$RESPONSE" | jq -r '.message')"
    exit 1
fi

# Get count
COUNT=$(echo "$RESPONSE" | jq -r '.count // 0')

if [ "$COUNT" -eq 0 ]; then
    log_warning "No deleted repositories found."
    exit 0
fi

# Display repositories
echo
log_info "Deleted repositories found ($COUNT):"
echo "=================================================="
printf "%-3s | %-30s | %-36s | %s\n" "No" "Repository Name" "ID" "Deletion Date"
echo "=================================================="

# Create a temporary file to store the repositories for selection
TEMP_FILE=$(mktemp)
echo "$RESPONSE" | jq -r '.value[] | "\(.name)|\(.id)|\(.deletedDate)"' > "$TEMP_FILE"

INDEX=1
while IFS='|' read -r name id date; do
    formatted_date=$(echo "$date" | cut -d'T' -f1)
    printf "%-3d | %-30s | %-36s | %s\n" "$INDEX" "${name:0:30}" "$id" "$formatted_date"
    ((INDEX++))
done < "$TEMP_FILE"

# Ask for selection
echo
echo "=================================================="
read -p "Enter the number of the repository to restore: " REPO_SELECTION

if [ -z "$REPO_SELECTION" ]; then
    log_error "Repository number cannot be empty"
    rm "$TEMP_FILE"
    exit 1
fi

# Validate selection
if ! [[ "$REPO_SELECTION" =~ ^[0-9]+$ ]]; then
    log_error "Please enter a valid number"
    rm "$TEMP_FILE"
    exit 1
fi

if [ "$REPO_SELECTION" -lt 1 ] || [ "$REPO_SELECTION" -gt "$COUNT" ]; then
    log_error "Invalid number. Please choose between 1 and $COUNT"
    rm "$TEMP_FILE"
    exit 1
fi

# Get selected repository info
SELECTED_LINE=$(sed -n "${REPO_SELECTION}p" "$TEMP_FILE")
REPO_NAME=$(echo "$SELECTED_LINE" | cut -d'|' -f1)
REPO_ID=$(echo "$SELECTED_LINE" | cut -d'|' -f2)

rm "$TEMP_FILE"

# Ask for confirmation
echo
log_warning "You are about to restore the repository: $REPO_NAME"
log_warning "ID: $REPO_ID"
read -p "Are you sure? (y/N): " CONFIRM

if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    log_info "Restoration cancelled."
    exit 0
fi

# Restore repository
echo
log_info "Restoring repository with ID: $REPO_ID"

RESTORE_URL="https://dev.azure.com/${ORGANIZATION}/${PROJECT_ENCODED}/_apis/git/recycleBin/repositories/${REPO_ID}?api-version=7.1"
log_info "Restore URL: $RESTORE_URL"

RESTORE_RESPONSE=$(curl -s -X PATCH -u ":${PAT}" \
    -H "Content-Type: application/json" \
    -d '{"deleted": false}' \
    "$RESTORE_URL")

if [ $? -ne 0 ]; then
    log_error "Error during restoration API call"
    exit 1
fi

# Check if restoration was successful
if echo "$RESTORE_RESPONSE" | jq -e '.message' > /dev/null 2>&1; then
    log_error "Error during restoration: $(echo "$RESTORE_RESPONSE" | jq -r '.message')"
    exit 1
fi

log_success "Repository restored successfully!"
echo "Details:"
if echo "$RESTORE_RESPONSE" | jq . > /dev/null 2>&1; then
    echo "$RESTORE_RESPONSE" | jq -r '"  Name: \(.name // "N/A")\n  ID: \(.id // "N/A")\n  URL: \(.webUrl // "N/A")"'
else
    echo "  Repository ID: $REPO_ID"
    echo "  Repository Name: $REPO_NAME"
fi

echo
log_success "Operation completed successfully!"
