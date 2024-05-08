# About
Date : 08th May 2024  
Author: Lionel Gurret  
Description : Remove a commit from AZDO

# Commands
```
git clone git@ssh.dev.azure.com:v3/org_name/project_name/repo-name
cd azdo_projects_management/
git branch
checkout feature/test-remove-commit
git rebase --rebase-merges --onto XXXXXXXXXXXXX  # commit number you wish to go back - so n-1 the bad one
git push origin +feature/test-remove-commit
```

# YouTube Video
[](Link)
