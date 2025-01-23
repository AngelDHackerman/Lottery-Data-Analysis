provider "aws" {
  region     = var.aws_region

  access_key = var.environment == "prod" ? var.prod_aws_access_key : var.dev_aws_access_key
  secret_key = var.environment == "prod" ? var.prod_aws_secret_key : var.dev_aws_secret_key
}
