resource "azurerm_service_plan" "example" {
  name                = "example"
  resource_group_name = "project1"
  location            = "eastus"
  os_type             = "Linux"
  sku_name            = "P1v2"
}