# Create a secret in AWS Secrets manager for the database

# Create the secret
resource "aws_secretsmanager_secret" "lottery_secret" {
  name = "lottery_secret_${var.environment}"
  description = "Secrets for Lotería Santa Lucía ${var.environment}"
}

# Upload the secrets to AWS
resource "aws_secretsmanager_secret_version" "lottery_secret_value" {
  secret_id           = aws_secretsmanager_secret.lottery_secret.id
  secret_string       = jsonencode({
    db_arn            = var.arn_db_dev
    db_host           = var.endpoint_db_dev
    db_port           = var.db_port
    db_username       = var.db_username_dev
    db_password       = var.db_password_dev
    db_av_zone        = var.db_availability_zone_dev
    database          = var.database
    s3_bucket_raw     = var.s3_bucket_prod_raw_and_processed_arn
  })
}