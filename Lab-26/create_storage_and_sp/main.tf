# Sources
# https://github.com/ned1313/terraform-tuesdays/blob/main/2024-01-23-AzureStorageABAC/create_storage/main.tf

# Set storage access to use Entra ID instead of storage key SAS
provider "azurerm" {
  features {}
  storage_use_azuread = true
}

provider "azuread" {
}

########
# IAM
########

# Service principal
## 1 SP "project1" to create resources in our project RG and generate User Delegated SAS Tokens
data "azuread_client_config" "current" {}

resource "azuread_application" "main" {
  display_name = "devops-dev-account@project1"
  owners       = [data.azuread_client_config.current.object_id]
}

resource "azuread_service_principal" "main" {
  client_id                    = azuread_application.main.client_id
  app_role_assignment_required = false
  owners                       = [data.azuread_client_config.current.object_id]
}

# Add time rotating for client secret
resource "time_rotating" "one_day" {
  rotation_hours = 23
}

resource "azuread_service_principal_password" "main" {
  service_principal_id = azuread_service_principal.main.id
  rotate_when_changed = {
    rotation = time_rotating.one_day.id
  }
}

# Roles
data "azurerm_subscription" "main" {}

# Custom Role to generate User Delegated SAS Token
resource "azurerm_role_definition" "storage_account" {
  name        = "custom-write-access"
  scope       = data.azurerm_subscription.main.id
  description = "Custom role definition allowing generate SAS Tokens to the storage account ${azurerm_storage_account.main.name}."

  permissions {
    actions = [
      "Microsoft.Storage/storageAccounts/blobServices/containers/read",
      "Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action"
    ]
  }

  assignable_scopes = [
    data.azurerm_subscription.main.id
  ]
}

###########################
# We assign Roles to our SP
###########################
resource "azurerm_role_assignment" "storage_account" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = azurerm_role_definition.storage_account.name
  principal_id         = azuread_service_principal.main.object_id

  skip_service_principal_aad_check = true

  depends_on = [azurerm_role_definition.storage_account]
}

######################################
# Built In Role assignement for the Project1 Demo RG
resource "azurerm_role_assignment" "resource_group" {
  scope                            = azurerm_resource_group.demo.id
  role_definition_name             = "Owner"
  principal_id                     = azuread_service_principal.main.object_id
  skip_service_principal_aad_check = true
}

####################
# RG Demo Project1
####################
# We create a RG for our test Project
resource "azurerm_resource_group" "demo" {
  name     = "project1"
  location = "eastus"
}

####################
# RG Storage Account
####################

# We create a RG for our Storage accounts
resource "azurerm_resource_group" "main" {
  name     = "tfstates"
  location = "eastus"
}

# We create a DEV Storage account without Shared access token and HNS Activated
resource "azurerm_storage_account" "main" {
  name                = "lionelgurrettestsa"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  account_tier              = "Standard"
  account_kind              = "StorageV2"
  account_replication_type  = "GRS"
  enable_https_traffic_only = true
  min_tls_version           = "TLS1_2"

  # security :) !!!!!!!!!!!!!!!!!!!!!!!!!!!
  shared_access_key_enabled         = false
  default_to_oauth_authentication   = true
  infrastructure_encryption_enabled = false
  is_hns_enabled                    = true

#  blob_properties {
#    change_feed_enabled           = true
#    change_feed_retention_in_days = 90
#    last_access_time_enabled      = true
#
#    delete_retention_policy {
#      days = 30
#    }
#
#    container_delete_retention_policy {
#      days = 30
#    }
#
#  }

  sas_policy {
    expiration_period = "00.01:00:00"
    expiration_action = "Log"
  }

}

#######
# ACLs
#######

# We configure an ACL to let our SP project1, access project1 folder
resource "azurerm_storage_data_lake_gen2_filesystem" "main" {
  name               = "tfstate"
  storage_account_id = azurerm_storage_account.main.id
}

resource "azurerm_storage_data_lake_gen2_path" "main" {
  storage_account_id = azurerm_storage_account.main.id
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.main.name
  path               = "project1"
  resource           = "directory"

  ace {
    id          = azuread_service_principal.main.object_id
    type        = "user"
    permissions = "rwx"
  }
}

# Second folder without ACL
resource "azurerm_storage_data_lake_gen2_path" "project2" {
  storage_account_id = azurerm_storage_account.main.id
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.main.name
  path               = "project2"
  resource           = "directory"
}

#########
# Outputs
#########

# SP name
output "service_principal_clientid" {
  value = azuread_service_principal.main.client_id
}

# SP Password
output "service_principal_password" {
  value = nonsensitive(azuread_service_principal_password.main.value)
}

# Storage Account Name
output "storage_account_name" {
  value = azurerm_storage_account.main.name
}

# Storage Account Key for Project1
output "key" {
  value = "project1/dev.terraform.tfstate"
}
