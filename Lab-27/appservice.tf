module "appservice" {
  source      = "./modules/appservice"
  app_name    = local.app_name
  rg_name     = local.rg_name
  rg_location = var.region
}
