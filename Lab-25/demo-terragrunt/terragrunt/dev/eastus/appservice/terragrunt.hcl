# Include root terragrunt.hcl
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "../../../../terraform//appservice"
}

# Values for current module - Specific to this project
inputs = {
  tags = {
    createdby = "Terragrunt"
    version   = "1.1"
  }
}
