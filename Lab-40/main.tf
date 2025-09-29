# Terraform Configuration for Azure Deployment
# YouTube Video - Terraform with GitHub Actions

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm" # Official Azure Provider
      version = "4.46.0"            # Fixed version for reproducibility
    }
  }
}

# === AZURE RESOURCES ===

# Resource Group - Logical container for our resources
resource "azurerm_resource_group" "test" {
  name     = "test-tf-actions" # Unique name within subscription
  location = "East US"         # Azure region
}

# Azure Virtual Network (similar to AWS VPC)
resource "azurerm_virtual_network" "test" {
  name                = "test-vnet"
  address_space       = ["10.0.0.0/16"] # Private IP address range
  location            = azurerm_resource_group.test.location
  resource_group_name = azurerm_resource_group.test.name
}

# Subnet within the VNet
resource "azurerm_subnet" "test" {
  name                 = "test-subnet"
  resource_group_name  = azurerm_resource_group.test.name
  virtual_network_name = azurerm_virtual_network.test.name
  address_prefixes     = ["10.0.1.0/24"] # Subset of the VNet
}

resource "azurerm_subnet" "subnet2" {
  name                 = "test-subnet-2"
  resource_group_name  = azurerm_resource_group.test.name
  virtual_network_name = azurerm_virtual_network.test.name
  address_prefixes     = ["10.0.2.0/24"] # Subset of the VNet
}

resource "azurerm_linux_virtual_machine" "test" {
  name                = "test-vm"
  resource_group_name = azurerm_resource_group.test.name
  location            = azurerm_resource_group.test.location
  size                = "Standard_B1s" # Cost-effective size
  admin_username      = "azureuser"

  network_interface_ids = [
    azurerm_network_interface.example.id
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }
}

resource "azurerm_network_interface" "example" {
  name                = "example"
  location            = azurerm_resource_group.test.location
  resource_group_name = azurerm_resource_group.test.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.test.id
    private_ip_address_allocation = "Dynamic"
  }
  tags = {
    demo_flag = "v2"
  }
}

resource "terraform_data" "example" {
  #   input = azurerm_network_interface.example.private_ip_address
  input = azurerm_network_interface.example.tags.demo_flag

  lifecycle {
    action_trigger {
      events  = [after_update]
      actions = [action.azurerm_virtual_machine_power.example]
    }
  }
}

# Action resource to restart the VM
action "azurerm_virtual_machine_power" "example" {
  config {
    virtual_machine_id = azurerm_linux_virtual_machine.test.id
    power_action       = "restart"
  }
}