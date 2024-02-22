locals {
  # Get Current Environment
  env_vars    = read_terragrunt_config(find_in_parent_folders("env_specific.hcl"))
  environment = local.env_vars.locals.environment

  # Get Current Region
  region_vars = read_terragrunt_config(find_in_parent_folders("region_specific.hcl"))
  region      = local.region_vars.locals.region

  # Create prefix for resources and backend
  prefix  = "${local.environment}${local.region}"
  rg_name = "${local.prefix}-rg"
}

# Values for module(s) for all projects
inputs = {
  app_name    = "${local.prefix}-myapp"
  rg_name     = local.rg_name
  rg_location = local.region
}

# Generate a backend (one per project)
generate "backend" {
  path      = "backend.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  backend "azurerm" {
    resource_group_name = "tfstate-${local.prefix}-rg"
    storage_account_name = "tfstate${local.prefix}sa"
    container_name       = "tfstate"
    key                  = "${local.environment}.${local.region}.tfstate"
  }
}
EOF
}

# Providers used by projects
generate "providers" {
  path      = "providers.tf"
  if_exists = "overwrite"
  contents  = <<EOF
    terraform {
      required_providers {
        azurerm = {
          source  = "hashicorp/azurerm"
          version = "3.92.0"
        }
      }
    }
    provider "azurerm" {
      features {}
    }
EOF
}
