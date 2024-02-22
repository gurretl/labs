resource "azurerm_resource_group" "example" {
  name     = var.rg_name
  location = var.rg_location
}

resource "azurerm_service_plan" "example" {
  name                = "appservice_sp"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  os_type             = "Linux"
  sku_name            = "P1v2"
}

resource "azurerm_linux_web_app" "example" {
  name                = "${var.app_name}"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  service_plan_id     = azurerm_service_plan.example.id

  site_config {}
  tags = var.tags
}