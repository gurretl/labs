# Azure DevOps Repository Restore Tool - PowerShell Version
# Script to restore a deleted Azure DevOps repository
# Uses Azure DevOps REST API to list and restore deleted repositories

# Colors for console output
$Colors = @{
    Red = 'Red'
    Green = 'Green'
    Yellow = 'Yellow'
    Blue = 'Blue'
    White = 'White'
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Colors.Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Colors.Yellow
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Colors.Red
}

# Check if required commands are available
try {
    Get-Command curl -ErrorAction Stop | Out-Null
} catch {
    Write-ErrorMsg "curl is not available. Please install curl or use Windows 10/11 with built-in curl."
    exit 1
}

# Banner
Write-Host "==========================================" -ForegroundColor $Colors.White
Write-Host "  Azure DevOps Repository Restore Tool" -ForegroundColor $Colors.White
Write-Host "==========================================" -ForegroundColor $Colors.White
Write-Host ""

# Ask for necessary information
$ProjectURL = Read-Host "Enter Azure DevOps project URL (ex: https://dev.azure.com/myorg/myproject)"

# Validate URL format
if ($ProjectURL -notmatch '^https://dev\.azure\.com/[^/]+/[^/]+/?$') {
    Write-ErrorMsg "Invalid URL format. Expected: https://dev.azure.com/{ORGANIZATION}/{PROJECT}"
    exit 1
}

# Extract organization and project
$ProjectURL = $ProjectURL.TrimEnd('/')  # Remove trailing slash
$Organization = ($ProjectURL -replace 'https://dev\.azure\.com/([^/]*)/.*', '$1')
$Project = ($ProjectURL -replace 'https://dev\.azure\.com/[^/]*/([^/]*)', '$1')

Write-Host ""
$PAT = Read-Host "Enter your Personal Access Token (PAT)" -AsSecureString
$PAT = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($PAT))
Write-Host ""

if ([string]::IsNullOrWhiteSpace($PAT)) {
    Write-ErrorMsg "PAT cannot be empty"
    exit 1
}

Write-Info "Organization: $Organization"
Write-Info "Project: $Project"
Write-Host ""

# Get deleted repositories
Write-Info "Retrieving deleted repositories..."

# URL encode the project name (simple replacement for spaces)
$ProjectEncoded = $Project -replace ' ', '%20'
$URL = "https://dev.azure.com/$Organization/$ProjectEncoded/_apis/git/deletedrepositories?api-version=5.1-preview.1"

Write-Info "Calling URL: $URL"

# Prepare authentication header
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$PAT"))
$headers = @{
    Authorization = "Basic $base64AuthInfo"
    'Content-Type' = 'application/json'
}

try {
    $response = Invoke-RestMethod -Uri $URL -Method Get -Headers $headers
    
    # Check if response has the expected structure
    if (-not $response -or -not $response.PSObject.Properties['value']) {
        Write-Warning "No deleted repositories found."
        exit 0
    }
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Warning "No deleted repositories found or project not accessible."
        exit 0
    }
    Write-ErrorMsg "Error during API call: $($_.Exception.Message)"
    exit 1
}

# Filter repositories for the current project only
$filteredRepos = $response.value | Where-Object { $_.project.name -eq $project }
$count = $filteredRepos.Count

if ($count -eq 0) {
    Write-Warning "No deleted repositories found for project '$project'."
    exit 0
}

# Display repositories
Write-Host ""
Write-Info "Deleted repositories found for project '$project' ($count):"
Write-Host "==================================================" -ForegroundColor $Colors.White
Write-Host ("{0,-3} | {1,-30} | {2,-36} | {3}" -f "No", "Repository Name", "ID", "Deletion Date") -ForegroundColor $Colors.White
Write-Host "==================================================" -ForegroundColor $Colors.White

$repositories = @()
$index = 1
foreach ($repo in $filteredRepos) {
    $formattedDate = ($repo.deletedDate -split 'T')[0]
    $repoName = if ($repo.name.Length -gt 30) { $repo.name.Substring(0, 30) } else { $repo.name }
    Write-Host ("{0,-3} | {1,-30} | {2,-36} | {3}" -f $index, $repoName, $repo.id, $formattedDate)
    
    $repositories += @{
        Index = $index
        Name = $repo.name
        Id = $repo.id
        DeletedDate = $repo.deletedDate
    }
    $index++
}

# Ask for selection
Write-Host ""
Write-Host "==================================================" -ForegroundColor $Colors.White
$selection = Read-Host "Enter the number of the repository to restore"

if ([string]::IsNullOrWhiteSpace($selection)) {
    Write-ErrorMsg "Repository number cannot be empty"
    exit 1
}

# Validate selection
$selectionNumber = 0
if (-not [int]::TryParse($selection, [ref]$selectionNumber)) {
    Write-ErrorMsg "Please enter a valid number"
    exit 1
}

if ($selectionNumber -lt 1 -or $selectionNumber -gt $count) {
    Write-ErrorMsg "Invalid number. Please choose between 1 and $count"
    exit 1
}

# Get selected repository info
$selectedRepo = $repositories[$selectionNumber - 1]
$repoName = $selectedRepo.Name
$repoId = $selectedRepo.Id

# Ask for confirmation
Write-Host ""
Write-Warning "You are about to restore the repository: $repoName"
Write-Warning "ID: $repoId"
$confirm = Read-Host "Are you sure? (y/N)"

if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Info "Restoration cancelled."
    exit 0
}

# Restore repository
Write-Host ""
Write-Info "Restoring repository with ID: $repoId"

$restoreURL = "https://dev.azure.com/$Organization/$ProjectEncoded/_apis/git/recycleBin/repositories/$repoId?api-version=7.1"
Write-Info "Restore URL: $restoreURL"

$restoreBody = @{
    deleted = $false
} | ConvertTo-Json

try {
    $restoreResponse = Invoke-RestMethod -Uri $restoreURL -Method Patch -Headers $headers -Body $restoreBody
} catch {
    Write-ErrorMsg "Error during restoration API call: $($_.Exception.Message)"
    exit 1
}

Write-Success "Repository restored successfully!"
Write-Host "Details:"
if ($restoreResponse.name) {
    Write-Host "  Name: $($restoreResponse.name)"
    Write-Host "  ID: $($restoreResponse.id)"
    Write-Host "  URL: $($restoreResponse.webUrl)"
} else {
    Write-Host "  Repository ID: $repoId"
    Write-Host "  Repository Name: $repoName"
}

Write-Host ""
Write-Success "Operation completed successfully!"
