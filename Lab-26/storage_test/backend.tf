terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "3.94.0"
    }
  }
}


terraform {
  backend "azurerm" {
    storage_account_name = "lionelgurrettestsa"
    container_name       = "tfstate"
    key                  = "project1/dev.terraform.tfstate"
    sas_token            = "XXX"
  }
}

provider "azurerm" {
  features {}
}
