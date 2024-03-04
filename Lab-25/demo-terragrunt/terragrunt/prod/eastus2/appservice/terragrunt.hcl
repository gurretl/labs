# Include root terragrunt.hcl
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "../../../../terraform//appservice"
}

# Values
inputs = {
  tags = {
    createdby = "Terragrunt"
    version   = "1.0"
  }
}
