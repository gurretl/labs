terraform {
  backend "azurerm" {
    resource_group_name  = "tfstatedeveastus-rg"
    storage_account_name = "tfstatedeveastussa"
    container_name       = "tfstate"
    key                  = "dev.eastus.tfstate"
  }
}
