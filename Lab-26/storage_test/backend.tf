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
    sas_token = "st=2024-03-12T10%3A49Z&se=2024-03-12T11%3A19Z&sp=rcwdl&sip=80.218.69.39&spr=https&sv=2021-08-06&sr=d&sdd=1&skoid=6aae7428-4ec8-44f4-99e3-20112a39fbd5&sktid=7121c231-fb17-4318-a5a6-eb9283f60660&skt=2024-03-12T10%3A49%3A00Z&ske=2024-03-12T11%3A19%3A00Z&sks=b&skv=2021-08-06&sig=VCdaSnBKnFsjPd6lVx1sb9HefPelLs9szOvksXFrG4g%3D"
  }
}

provider "azurerm" {
  features {}
}
