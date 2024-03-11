locals {
  prefix   = "${var.environment}${var.region}"
  rg_name  = "${local.prefix}-rg"
  app_name = "${local.prefix}-${var.app_name}"
}
