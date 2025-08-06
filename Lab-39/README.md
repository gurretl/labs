# Azure DevOps Repository Restore Tools

This repository contains two scripts to restore deleted repositories from Azure DevOps using the Azure DevOps REST API.

## 📋 Overview

When repositories are deleted in Azure DevOps, they are moved to the recycle bin and can be restored within a certain timeframe. These scripts automate the process of:

1. **Listing** all deleted repositories in a project
2. **Selecting** a repository to restore via an interactive menu
3. **Restoring** the selected repository back to active state

## 🚀 Available Scripts

### Bash Script (`restore-azure-repo.sh`)

- **Platform**: Linux, macOS, Windows (with WSL/Git Bash)
- **Requirements**: `bash`, `curl`, `jq`
- **Features**: Colored output, input validation, interactive selection

### PowerShell Script (`restore-azure-repo.ps1`)

- **Platform**: Windows, Linux (with PowerShell Core), macOS (with PowerShell Core)
- **Requirements**: PowerShell 5.1+, built-in cmdlets
- **Features**: Colored output, input validation, interactive selection, robust error handling

## 📦 Prerequisites

### For Bash Script

```bash
# Ubuntu/Debian
sudo apt-get install curl jq

# macOS (with Homebrew)
brew install curl jq

# CentOS/RHEL
sudo yum install curl jq
```

### For PowerShell Script

- PowerShell 5.1 or later
- Built-in cmdlets (no external dependencies required)

## 🔑 Azure DevOps Setup

1. **Personal Access Token (PAT)**: Create a PAT in Azure DevOps with the following permissions:
   - **Code (read & write)**: Required to list and restore repositories
   - **Project and team (read)**: Required to access project information

2. **Project URL**: You'll need the full project URL in the format:

   ```text
   https://dev.azure.com/{ORGANIZATION}/{PROJECT}
   ```

## 🛠️ Usage

### Bash Script

```bash
# Make script executable
chmod +x restore-azure-repo.sh

# Run the script
./restore-azure-repo.sh
```

### PowerShell Script

```powershell
# Run the script (PowerShell execution policy may need to be adjusted)
.\restore-azure-repo.ps1

# If you encounter execution policy issues:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\restore-azure-repo.ps1
```

## 📝 Step-by-Step Process

1. **Enter Project URL**: Provide your Azure DevOps project URL

   ```text
   Example: https://dev.azure.com/myorganization/myproject
   ```

2. **Enter PAT**: Provide your Personal Access Token (input will be hidden for security)

3. **View Deleted Repositories**: The script will display a numbered list of all deleted repositories:

   ```text
   ==================================================
   No  | Repository Name                | ID                                   | Deletion Date
   ==================================================
   1   | old-project                    | a1b2c3d4-e5f6-7890-abcd-ef1234567890 | 2024-01-15
   2   | deprecated-api                 | b2c3d4e5-f6g7-8901-bcde-f23456789012 | 2024-01-10
   ```

4. **Select Repository**: Enter the number corresponding to the repository you want to restore

5. **Confirm Restoration**: Confirm your choice when prompted

6. **Restoration Complete**: The script will restore the repository and display the results

## ⚠️ Important Notes

- **Time Limit**: Deleted repositories can only be restored within a limited timeframe (typically 30 days)
- **Permissions**: Ensure your PAT has sufficient permissions for the target project
- **Backup**: Consider this as a recovery tool, not a replacement for proper backup strategies
- **Rate Limits**: The scripts respect Azure DevOps API rate limits

## 🔧 API Endpoints Used

- **List Deleted Repositories**:

  ```http
  GET https://dev.azure.com/{organization}/{project}/_apis/git/deletedrepositories?api-version=5.1-preview.1
  ```

- **Restore Repository**:

  ```http
  PATCH https://dev.azure.com/{organization}/{project}/_apis/git/recycleBin/repositories/{repositoryId}?api-version=7.1
  ```

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid URL format"**
   - Ensure the URL follows the exact format: `https://dev.azure.com/{org}/{project}`
   - Remove any trailing slashes or additional paths

2. **"API Error: Access Denied"**
   - Check that your PAT has the correct permissions
   - Verify that the PAT hasn't expired
   - Ensure you have access to the specified project

3. **"No deleted repositories found"**
   - All repositories may have already been restored or permanently deleted
   - Check that you're looking in the correct project

4. **"jq command not found" (Bash only)**
   - Install jq using your system's package manager
   - On Ubuntu/Debian: `sudo apt-get install jq`

5. **PowerShell execution policy errors**
   - Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
   - Or run with: `powershell -ExecutionPolicy Bypass -File restore-azure-repo.ps1`

## 📄 License

These scripts are provided as-is for educational and utility purposes. Use at your own risk and always test in a non-production environment first.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve these scripts.

## 📞 Support

For Azure DevOps API documentation, visit: [Azure DevOps REST API Reference](https://docs.microsoft.com/en-us/rest/api/azure/devops/)
