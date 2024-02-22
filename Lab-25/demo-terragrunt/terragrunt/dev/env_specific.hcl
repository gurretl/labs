# All variables related to the current environment
locals {
  environment = basename(get_terragrunt_dir())
}

